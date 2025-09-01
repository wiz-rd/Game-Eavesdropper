#!/usr/bin/env python3
"""
Handles communicating with the client mod
by sending when and what "bad words"
were detected.
"""

import json
import queue

from websockets.sync.server import serve
from websockets import ServerConnection, ConnectionClosed


# TODO: replace this with a file based around SMO that
# contains a dictionary or JSON information of SMO
# actors and their "common English" names
PLACEHOLDER_DICTIONARY = {"goomba": "kuribo"}


class ConnectionHandler:
    """
    This class handles all ongoing
    connections and broadcasts a
    message to all of them upon request.
    """
    def __init__(self, ip: str = "localhost", port: int | str = 8765):
        self.ip = ip
        self.port = port
        self.connected_clients = []
        self.queue = queue.Queue()
        self.server = None

    def broadcast(self, message: str):
        """Broadcast `message` to all connected hosts.

        Args:
            message (str): The message itself. Needs to be string.
        """
        self.queue.put(message)

    def _producer_handler(self, websocket: ServerConnection):
        """
        This handles all connections and messages outwards.
        It's meant for usage internally and should not be called itself.
        """
        # if they are just connecting, send them the information
        # about what enemies we have coded for.
        # this is highly nonperformant BUT since we should only
        # recieve a few requests a minute (if that), this
        # should be more than fine.
        if websocket.remote_address not in self.connected_clients:
            self.connected_clients.append(websocket.remote_address)
            websocket.send(json.dumps(PLACEHOLDER_DICTIONARY))

        while True:
            try:
                message = self.queue.get()
                websocket.send(message)
            except ConnectionClosed:
                break

    def run(self):
        """Start the server. Should only be called once."""
        with serve(self._producer_handler, self.ip, self.port) as server:
            self.server = server
            server.serve_forever()

    def shutdown(self):
        """Shuts down the server."""
        self.broadcast("Disconnected")
        self.server.shutdown()


if __name__ == "__main__":
    connection = ConnectionHandler()
    try:
        connection.run()
    except KeyboardInterrupt:
        print("\nExiting.")
