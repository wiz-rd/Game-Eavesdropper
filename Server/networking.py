#!/usr/bin/env python3
"""
Handles communicating with the client mod
by sending data when and what "bad words"
were sent.
"""

# TODO:
# support multiple clients

# confirm with client on connection

# map in-game entity names to verbose names (for SMO specifically)

# find a networking library that is NOT http

# add this networking portion


def send_term(phrase: str) -> bool:
    """
    Send what the user said to all clients.

    Args:
        phrase (str): The phrase to send.

    Returns:
        bool: If all clients recieved the words.
    """
    ...
    return NotImplemented

def confirm_connection(ip: str, message: str = "Connected!") -> bool:
    """
    Sends a confirmation message to the specified client.

    Args:
        ip (str): The IP address of the client.
        message (str): The connection message.

    Returns:
        bool: If the client received the message.
    """
    ...
    return NotImplemented

