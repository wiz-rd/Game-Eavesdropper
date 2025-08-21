#!/usr/bin/env python3
"""
A very simple client meant to vaguely imitate
what the mod should look like at completion.
"""

from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

# https://docs.twisted.org/en/stable/core/examples/index.html
# was immensely helpful in this

class SampleClient(LineReceiver):
    # end of line
    end = b"\x00"
    # end of connection
    terminate = b"\x04"

    def connectionMade(self):
        print("connection made")
        self.sendLine(b"Hi, can I have phrases please?")
        self.sendLine(self.end)

    def lineReceived(self, line):
        print("received:", line)
        if line == self.terminate:
            self.transport.loseConnection()


class SampleClientFactory(ClientFactory):
    protocol = SampleClient

    def __init__(self):
        self.done = Deferred()

    def clientConnectionFailed(self, connector, reason):
        print("connection failed:", reason.getErrorMessage())
        self.done.errback(reason)

    def clientConnectionLost(self, connector, reason):
        print("connection lost:", reason.getErrorMessage())
        self.done.callback(None)


def main(reactor):
    factory = SampleClientFactory()
    reactor.connectTCP("localhost", 8000, factory)
    return factory.done


if __name__ == "__main__":
    task.react(main)

