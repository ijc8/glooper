#!/usr/bin/env python

import asyncio
import websockets
import json
import logging
import array
import time

logging.basicConfig()

USERS = set()

async def register(websocket):
    USERS.add(websocket)

async def unregister(websocket):
    USERS.remove(websocket)

async def chat(websocket, path):
    print("connect")
    await register(websocket)
    try:
        async for data in websocket:
            print('got something, broadcasting')
            if len(USERS) > 1:
                await asyncio.wait([user.send(data) for user in USERS if user is not websocket])
    finally:
        print("disconnect")
        await unregister(websocket)

start_server = websockets.serve(chat, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
