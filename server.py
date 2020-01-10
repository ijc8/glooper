#!/usr/bin/env python3

import ssl
import pathlib
import asyncio
import json
import logging
import array
import time
import os
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
import threading
import websockets

mimetypes.init()
logging.basicConfig()


# Static file server (compatible with websocket library).
# See https://gist.github.com/artizirk/04eb23d957d7916c01ca632bb27d5436
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


# === WebSocket server code ===
# Essentially a broadcast server; anything sent by one user is broadcast to all others.

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

# Configure SSL.
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
pem = pathlib.Path(__file__).with_name("certificate.pem")
key = pathlib.Path(__file__).with_name("key.pem")
ssl_context.load_cert_chain(pem, keyfile=key)

start_server = websockets.serve(chat, "", 8765, ssl=ssl_context, max_size=None, create_protocol=WebSocketServerProtocolWithHTTP)

# Convenience server on port 80; just redirects users to https:// with the correct port.
import threading

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        addr = self.headers.get('Host').split(':')[0]
        self.send_response(307)
        self.send_header('Location', f'https://{addr}:8765')
        self.end_headers()

def run():
    server_address = ('', 80)
    httpd = HTTPServer(server_address, RedirectHandler)
    httpd.serve_forever()

t = threading.Thread(target=run)
t.start()

# Start the real server.
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
