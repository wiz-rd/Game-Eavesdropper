#!/usr/bin/env python3
"""
A very simple client meant to vaguely imitate
what the mod should look like at completion.
"""

from websockets.sync.client import connect
from websockets import ConnectionClosed


def listen_indefinitely():
    with connect("ws://localhost:8765") as websocket:
        while True:
            try:
                message = websocket.recv(timeout=None)
                print(f"Received: {message}")
            except ConnectionClosed:
                print("Server closed connection.")
                break


listen_indefinitely()
