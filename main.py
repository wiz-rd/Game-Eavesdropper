#!/usr/bin/env python3
"""
This script takes input from the microphone and
(deliberately poorly) transcribes it. It's meant
to mimic challenges originating from the streamer DougDoug.

Resources this uses:
- Vosk
- Piper (Piper-TTS)

Author: @Wiz-rd
"""

import argparse
import json
import pathlib
from queue import Queue
import sys
from urllib.error import HTTPError

import sounddevice as sd
from piper import PiperVoice, SynthesisConfig
from piper.download_voices import download_voice
from vosk import Model, KaldiRecognizer, SetLogLevel


# https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py
# and https://github.com/alphacep/vosk-api/blob/master/python/example/test_ep.py
# were referenced when writing this

PUNISHMENT_STRING = "You silly goose, you said "
MODELS_FOLDER = pathlib.Path(pathlib.Path(__file__).parent, "models")


MODELS_FOLDER.mkdir(exist_ok=True)


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


list_argument: bool = "-l" in sys.argv or "--list" in sys.argv

# setting up the argument parsing
parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument(
    "-l",
    "--list",
    help="List input audio devices and exit. Use in conjunction with '--device' to list ALL audio devices.",
    action="store_true",
)
parser.add_argument(
    "--model",
    help="The speech-to-text language model; en-us, fr, nl, etc.",
    type=str,
    default="en-us",
)
parser.add_argument(
    "-s",
    "--speech-model",
    type=str,
    help="The TTS model for use with Piper. Default: en_US-john-medium. More "
    "available at: https://huggingface.co/rhasspy/piper-voices/tree/main",
    default="en_US-john-medium",
)
parser.add_argument(
    "-a",
    "--any-word",
    help="Separate the bad-words file by spaces AND new lines.",
    action="store_true",
    default=False,
)

# prepare the device argument
if list_argument:
    parser.add_argument(
        "--device",
        help="The audio device to use. Specify by index or name.",
        action="store_true",
    )
else:
    parser.add_argument(
        "--device",
        help="The audio device to use. Specify by index or name.",
        default="default"
    )

parser.add_argument("-r", "--samplerate", type=int, help="The sampling rate.")

# require this one only if "--list" is not passed
parser.add_argument(
    "-w",
    "--words-file",
    type=str,
    help='The "bad words" file.',
    required=not list_argument,
    default="problem_words.txt",
)

args = parser.parse_args()

# if "list" and "device" are passed, show all sound devices
if args.list and args.device:
    print(sd.query_devices())
    parser.exit(0)


# if list is passed alone
if args.list:
    devices = sd.query_devices()
    print("\nAvailable devices\n---------------")
    if isinstance(devices, dict):
        print(f"Index: {devices['index']}\t\t{devices['name']}")
    else:
        for dev in devices:
            if str(dev["max_input_channels"]) != "0":
                print(f"Index: {dev['index']}\t\t{dev['name']}")

    print("")
    parser.exit(0)

#
# get the bad words file setup
#

bad_words_file = pathlib.Path(args.words_file)
if not bad_words_file.is_file():
    raise FileNotFoundError(f"Bad words file '{bad_words_file}' does not exist.")
else:
    with open(bad_words_file, "r", encoding="utf-8") as f:
        # each bad word or phrase should be on it's own line
        BAD_WORDS = [line.lower().strip() for line in f.readlines()]


#
# get the TTS model setup
#

if not args.speech_model.endswith(".onnx"):
    voice_model = (MODELS_FOLDER / (args.speech_model + ".onnx"))
else:
    voice_model = (MODELS_FOLDER / args.speech_model)

# attempt to download a model if it doesn't exist already
if not voice_model.exists():
    try:
        download_voice(args.speech_model, download_dir=MODELS_FOLDER)
    except HTTPError as e:
        raise ValueError(
            f"There is no voice with the name '{args.speech_model}' available on your system or for download on HuggingFace."
        ) from e


# remove Vosk debug logs
SetLogLevel(-1)

# setup a queue for printing voice output
q = Queue()


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


model = Model(lang=args.model)
syn_config = SynthesisConfig(
    volume=1.5,  # half louder
    noise_scale=1.2,  # more audio variation
    noise_w_scale=1.2,  # more speaking variation
    normalize_audio=False,  # use raw audio from voice
)
voice = PiperVoice.load(voice_model)

# TODO: DELETE DEBUGGING
print(BAD_WORDS)

######################
# PROCESS THE SPEECH #
######################

try:
    if args.samplerate is None:
        # try converting the device to an int first
        try:
            device = int(args.device)
            device_info = sd.query_devices(device, "input")
        except ValueError:
            device = args.device
            device_info = sd.query_devices(device, "input")

        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])

    # use the voice recognizer to take input
    with sd.RawInputStream(
        samplerate=args.samplerate,
        blocksize=8000,
        device=device,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)

        ############################################
        # PROCESS THE SPEECH (SPEAK ALOUD PORTION) #
        ############################################
        with sd.OutputStream(
            samplerate=voice.config.sample_rate, channels=1, dtype="int16"
        ) as output_stream:
            while True:
                data = q.get()
                transcription_results = {}
                current_quote = ""
                caught_words = []
                caught_string = ""
                # if there is a phrase heard
                if rec.AcceptWaveform(data):
                    # load the data into a JSON dictionary
                    transcription_results = json.loads(rec.Result())
                    print(f"{transcription_results['text']}")

                    current_quote: str = transcription_results["text"].lower().strip()

                    # skip if silence
                    if not current_quote or current_quote == "":
                        continue

                    if args.any_word:
                        # for each word in our input
                        for word in current_quote.split():
                            # and for each line in our phrases to catch
                            for bad_line in BAD_WORDS:
                                # and for each "bad word" in each bad phrase...
                                # if a spoken word is in there: bad human
                                if word in bad_line.split():
                                    caught_words.append(word)
                    else:
                        for phrase in BAD_WORDS:
                            if phrase in current_quote:
                                caught_words.append(phrase)

                    # turning our caught words into coherent phrases
                    # so the computer can tell us what we did wrong

                    if any(caught_words):
                        # comma separate all values except the last one
                        # if there are multiple values at all
                        if len(caught_words) > 2:
                            caught_string = ", ".join(caught_words[:-1])
                            caught_string += f", and {caught_words[-1]}"
                        elif len(caught_words) == 2:
                            caught_string = " and ".join(caught_words)
                        else:
                            caught_string = caught_words[0]

                        # print this so we can see the string
                        print(PUNISHMENT_STRING + f"'{caught_string}'.")

                        # say the punishment phrase aloud
                        for chunk in voice.synthesize(
                            PUNISHMENT_STRING + f"'{caught_string}'.",
                            syn_config=syn_config,
                        ):
                            # crazy how this just works
                            output_stream.write(chunk.audio_int16_array)

                # uncomment this below to get or use partials or
                # text before it's "solidified" by the model

                # else:
                #     print(rec.PartialResult())

# exiting the script
except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(f"{type(e).__name__}: {str(e)} at line {e.__traceback__.tb_lineno}")
