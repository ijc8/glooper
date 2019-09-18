#!/usr/bin/env python

# WS server example

import asyncio
import websockets
import json
import logging
import array
import time

logging.basicConfig()

available_names = ["zebra", "ocelot", "pants", "foobar", "jimbo", "burgundy"]

USERS = {}

AUDIO = 0
MESSAGE = 1
OBJECT = 2

AUDIO_TAG = AUDIO.to_bytes(4, byteorder='little')
MESSAGE_TAG = MESSAGE.to_bytes(4, byteorder='little')
OBJECT_TAG = OBJECT.to_bytes(4, byteorder='little')

async def broadcast_data(data):
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([user.send(data) for user in USERS])

def broadcast_audio(audio):
    return broadcast_data(AUDIO_TAG + audio)

def broadcast_object(obj):
    return broadcast_data(OBJECT_TAG + json.dumps(obj).encode('utf8'))

async def register(websocket):
    name = available_names.pop()
    USERS[websocket] = name
    await broadcast_object({'type': 'join', 'user': name})
    return name

async def unregister(websocket):
    name = USERS[websocket]
    available_names.append(name)
    del USERS[websocket]
    await broadcast_object({'type': 'leave', 'user': name})

async def chat(websocket, path):
    name = await register(websocket)
    print(f"got a new connection, assigned name {name}")
    try:
        async for packet in websocket:
            if packet.startswith(AUDIO_TAG):
                await broadcast_audio(packet[len(AUDIO_TAG):])
            elif packet.startswith(MESSAGE_TAG):
                message = packet[len(MESSAGE_TAG):].decode('utf8')
                await broadcast_object({'type': 'message', 'user': name, 'message': message})
    finally:
        await unregister(websocket)

start_server = websockets.serve(chat, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
