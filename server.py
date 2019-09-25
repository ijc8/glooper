#!/usr/bin/env python

import ssl
import pathlib
import asyncio
import websockets
import json
import logging
import array
import time
import os
from http import HTTPStatus
import mimetypes

mimetypes.init()
logging.basicConfig()


# https://gist.github.com/artizirk/04eb23d957d7916c01ca632bb27d5436
class WebSocketServerProtocolWithHTTP(websockets.WebSocketServerProtocol):
    """Implements a simple static file server for WebSocketServer"""

    async def process_request(self, path, request_headers):
        """Serves a file when doing a GET request with a valid path"""

        if "Upgrade" in request_headers:
            return  # Probably a WebSocket connection

        if path == '/':
            path = '/index.html'

        response_headers = [
            ('Server', 'asyncio'),
            ('Connection', 'close'),
        ]
        server_root = os.path.join(os.getcwd(), 'static')
        full_path = os.path.realpath(os.path.join(server_root, path[1:]))

        print("GET", path, end=' ')

        # Validate the path
        if os.path.commonpath((server_root, full_path)) != server_root or \
                not os.path.exists(full_path) or not os.path.isfile(full_path):
            print("404 NOT FOUND")
            return HTTPStatus.NOT_FOUND, [], b'404 NOT FOUND'

        print("200 OK")
        body = open(full_path, 'rb').read()
        mime_type = mimetypes.guess_type(path)[0]
        response_headers.append(('Content-Type', mime_type))
        response_headers.append(('Content-Length', str(len(body))))
        response_headers.append(('Feature-Policy', "microphone 'self'"))
        return HTTPStatus.OK, response_headers, body

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

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
localhost_pem = pathlib.Path(__file__).with_name("server.pem")
ssl_context.load_cert_chain(localhost_pem)

start_server = websockets.serve(chat, "", 8765, ssl=ssl_context, max_size=None, create_protocol=WebSocketServerProtocolWithHTTP)

#start_server = websockets.serve(chat, "", 8765, max_size=None, create_protocol=WebSocketServerProtocolWithHTTP)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
