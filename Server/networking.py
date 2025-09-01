#!/usr/bin/env python3
"""
Handles communicating with the client mod
by sending when and what "bad words"
were detected.
"""

import asyncio

from websockets.asyncio.server import serve


# TODO: replace this with a file based around SMO that
# contains a dictionary or JSON information of SMO
# actors and their "common English" names
PLACEHOLDER_DICTIONARY = {"goomba": "kuribo"}


async def echo(websocket):
    await websocket.send(PLACEHOLDER_DICTIONARY)


async def main():
    async with serve(echo, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
