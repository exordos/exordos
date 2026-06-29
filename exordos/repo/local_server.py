#    Copyright 2026 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import annotations

import contextlib
import functools
import http.server
import pathlib
import threading
import typing as tp


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    """A SimpleHTTPRequestHandler that doesn't spam stderr per request."""

    def log_message(self, format: str, *args: tp.Any) -> None:
        pass


@contextlib.contextmanager
def serve_directory(
    path: pathlib.Path | str, host: str, port: int = 0
) -> tp.Iterator[str]:
    """Serve `path` read-only over plain HTTP in a background thread.

    This is enough for the platform's repository driver, which only issues
    deterministic GETs (inventory.json, manifests, artifacts) -- no WebDAV
    or directory-listing support is required for reading.

    Yields the base URL (e.g. ``http://10.20.0.1:41231/``) once the server
    is accepting connections. The server is stopped when the context exits.
    """
    handler = functools.partial(_QuietHandler, directory=str(path))
    server = http.server.ThreadingHTTPServer((host, port), handler)
    bound_port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://{host}:{bound_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
