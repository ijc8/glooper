#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import json
import logging

logging.basicConfig()

available_names = ["zebra", "ocelot", "pants", "foobar", "jimbo", "burgundy"]

USERS = {}

async def broadcast_event(event_type, *data):
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([user.send(json.dumps((event_type, *data))) for user in USERS])

async def register(websocket):
    name = available_names.pop()
    USERS[websocket] = name
    await broadcast_event('join', name)
    return name

async def unregister(websocket):
    name = USERS[websocket]
    available_names.append(name)
    del USERS[websocket]
    await broadcast_event('leave', name)

async def chat(websocket, path):
    name = await register(websocket)
    print(f"got a new connection, assigned name {name}")
    try:
        async for e in websocket:
            event = json.loads(e)
            if event[0] == 'msg':
                print(name, event[1])
                await broadcast_event('msg', name, event[1])
            elif event[0] == 'audio':
                await broadcast_event('audio', event[1])
    finally:
        await unregister(websocket)

start_server = websockets.serve(chat, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
