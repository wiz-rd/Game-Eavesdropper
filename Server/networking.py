#!/usr/bin/env python3
"""
Handles communicating with the client mod
by sending when and what "bad words"
were detected.
"""

import json

from twisted.internet import protocol, reactor, endpoints

# TODO:
# support multiple clients?

# confirm with client on connection

# map in-game entity names to verbose names (for SMO specifically)

# find a networking library that is NOT http

# add this networking portion


# TODO: replace this with a file based around SMO that
# contains a dictionary or JSON information of SMO
# actors and their "common English" names
PLACEHOLDER_DICTIONARY = {
    "goomba": "kuribo"
}


# setting up a protocol
class Words(protocol.Protocol):
    """
    A simple protocol that sends JSON data to clients.
    """
    # end of line
    end = b"\x00"
    # end of connection
    terminate = b"\x04"

    # def __init__(self, factory):
    #     self.factory = factory

    def connectionMade(self):
        peer = self.transport.getPeer()
        # TODO: make some sort of logging handler?
        print(f"Connection from {peer.host}:{peer.port}")
        self.transport.write(b"Connected!")
        self.transport.write(json.dumps(PLACEHOLDER_DICTIONARY).encode() + self.end)

    def dataReceived(self, data):
        # exit if the terminate sequence is sent
        if self.terminate in data:
            self.transport.loseConnection()

        self.transport.write(b"I'm not doing anything with data sent right now.")

    def sendTerm(self, phrase: str) -> bool:
        """
        Send what the user said to all clients.

        Args:
            phrase (str): The phrase to send.

        Returns:
            bool: If all clients recieved the words.
        """
        phrase_dict = {
            "phrase": phrase,
        }

        self.transport.write(json.dumps(phrase_dict).encode() + self.end)

        ...
        return NotImplemented

    def close(self):
        """
        Closes the connection.
        TODO: make sure this doesn't disconnect from all clients.
        """
        self.transport.loseConnection()


class WordsFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Words(self)


def main():
    PORT = 8000
    # # TODO implement logging mentioned above?
    # print("Starting server...")
    # endpoint = endpoints.TCP4ServerEndpoint(reactor, PORT)
    # endpoint.listen(WordsFactory())
    # reactor.run()
    f = protocol.Factory()
    f.protocol = Words
    reactor.listenTCP(PORT, f)
    reactor.run()


if __name__ == "__main__":
    main()
