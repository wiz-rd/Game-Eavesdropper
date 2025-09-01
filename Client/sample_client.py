#!/usr/bin/env python3
"""
A very simple client meant to vaguely imitate
what the mod should look like at completion.
"""

from websockets.sync.client import connect


def hello():
    with connect("ws://localhost:8765") as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        print(f"Received: {message}")


hello()
