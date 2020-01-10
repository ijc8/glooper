Glooper
---

Instrument built for sharing small _loops_ in a _group_.

Anyone with the instrument can record snippets of audio, which are immediately shared with the rest of the group.

Requires the Python [websockets library](https://websockets.readthedocs.io/en/stable/) and expects `certificate.pem` and `key.pem` in the same directory as `server.py`. These can be generated with the command:

    $ openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

