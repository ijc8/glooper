Glooper
---

Instrument built for sharing small _loops_ in a _group_.

Anyone with the instrument can record snippets of audio, which are immediately shared with the rest of the group.

Code of interest is in `server.py` (server) and `static/index.html` (client).

Requires the Python [websockets library](https://websockets.readthedocs.io/en/stable/) and expects `certificate.pem` and `key.pem` in the same directory as `server.py`. These can be generated with the command:

    $ openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

To use it, run `python3 server.py` and go to `http://localhost/`. The former may require privileges to use port 80 (running with `sudo` is the quick fix), and the latter may give you a scary-looking warning which can be ignored. To have other players join, make sure you're on the same network and give them your IP address.

Happy glooping!

