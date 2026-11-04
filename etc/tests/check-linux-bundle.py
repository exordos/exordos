#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

import http.server
import json
import os
from pathlib import Path
import re
import ssl
import statistics
import subprocess
import sys
import tempfile
import threading
import time


def check_abi(bundle):
    for path in bundle.rglob("*"):
        if not path.is_file():
            continue
        with path.open("rb") as stream:
            if stream.read(4) != b"\x7fELF":
                continue
        result = subprocess.run(
            ["readelf", "--version-info", "--wide", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
        versions = re.findall(r"GLIBC_(\d+)\.(\d+)", result.stdout)
        if any(tuple(map(int, version)) > (2, 28) for version in versions):
            raise SystemExit(f"{path} requires glibc newer than 2.28")


def check_runtime(binary):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        config = root / "config.yaml"
        config.write_text("{}\n")
        environment = os.environ | {
            "HOME": str(root),
            "TMPDIR": str(root),
            "NO_PROXY": "127.0.0.1",
        }
        command = [
            str(binary),
            "--config",
            str(config),
            "--silent",
            "--no-check-updates",
        ]

        def run(*arguments):
            return subprocess.run(
                [*command, *arguments],
                check=True,
                capture_output=True,
                text=True,
                env=environment,
                timeout=15,
            )

        run("--help")
        version = run("version").stdout.strip()
        durations = []
        for _ in range(7):
            started = time.perf_counter()
            run("version")
            durations.append(time.perf_counter() - started)
        print(f"version={version} startup median={statistics.median(durations):.3f}s")
        if statistics.median(durations) >= 2.0:
            raise SystemExit("Linux startup performance regression")

        certificate = root / "certificate.pem"
        private_key = root / "key.pem"
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-keyout",
                str(private_key),
                "-out",
                str(certificate),
                "-days",
                "1",
                "-subj",
                "/CN=127.0.0.1",
                "-addext",
                "subjectAltName=IP:127.0.0.1",
            ],
            check=True,
            capture_output=True,
        )
        requests = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append((self.path, self.headers.get("Authorization")))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"[]")

            def log_message(self, *args):
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certificate, private_key)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        environment["REQUESTS_CA_BUNDLE"] = str(certificate)
        try:
            response = run(
                "--endpoint",
                f"https://127.0.0.1:{server.server_port}",
                "--access-token",
                "bundle-test",
                "iam",
                "projects",
                "list",
                "--output",
                "json",
            )
            if json.loads(response.stdout) != [] or requests != [
                ("/v1/iam/projects/", "Bearer bundle-test")
            ]:
                raise SystemExit("Bundled HTTPS API request failed")
        finally:
            server.shutdown()
            worker.join()
            server.server_close()
        print("Bundled HTTPS API request passed")


if __name__ == "__main__":
    binary = Path(sys.argv[1]).resolve()
    if "--abi" in sys.argv[2:]:
        check_abi(binary.parent)
    check_runtime(binary)
