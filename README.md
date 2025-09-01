> Under Construction

# Game Eavesdropper

*This readme will be updated and is not finalized.*

## Summary

This is a script that uses [VOSK](https://alphacephei.com/vosk/)
and [PiperTTS](https://github.com/OHF-Voice/piper1-gpl) to
listen to the user's speech and determine if something they
said is from a list of user-selected words that should be
avoided.

## Use Cases

This is meant for fun or goofy events, primarily
those such as for streamers or YouTubers. Some examples
are listed below.

- Streaming challenges
 - Breath of the Wild but if I say "fly" I restart
 - Super Mario Odyssey but saying "dog" spawns 10 dogs

As an alternative use, this could help train or coax
oneself into avoiding saying common words such as swear
words or "like."

## Setup

For the server side, we recommend using `uv` to install
dependencies but `pip` would suffice.

The packages you will need to install are:

- `sounddevice`
- `vosk`
- `piper-tts`

And they would be installed by running the following in your virtual
environment: `pip install sounddevice vosk piper-tts` OR
`uv add sounddevice vosk piper-tts`.

### For Linux Users

You may find that `sounddevice` doesn't work. If this is true,
install [PortAudio](https://www.portaudio.com/) and try again.
