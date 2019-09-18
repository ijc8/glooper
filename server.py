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

# For now, if the first byte is null, the rest of the packet is raw audio data.
# Otherwise, the entire packet is JSON.
AUDIO_TAG = bytes([AUDIO])

async def broadcast_data(data):
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([user.send(data) for user in USERS])

def broadcast_audio(audio):
    return broadcast_data(AUDIO_TAG + audio)

def broadcast_event(event_type, *data):
    return broadcast_data(json.dumps((event_type, *data)))

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
        async for packet in websocket:
            if packet.startswith(AUDIO_TAG):
                arr = array.array('f')
                arr.frombytes(packet[1:])
                await broadcast_event('audio', list(arr))
            elif packet[0] == MESSAGE:
                print(name, packet[1:])
                await broadcast_event('msg', name, packet[1:])
    finally:
        await unregister(websocket)

start_server = websockets.serve(chat, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
