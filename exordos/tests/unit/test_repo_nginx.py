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
"""Unit tests for the parallel artifact upload of the nginx repo driver."""

import pathlib
import threading

from exordos.builder import base as builder_base
from exordos.repo import nginx


def _element() -> builder_base.ElementInventory:
    return builder_base.ElementInventory(
        name="elem",
        version="1.0.0",
        images=[pathlib.Path("/tmp/foo.raw"), pathlib.Path("/tmp/bar.raw")],
        manifests=[pathlib.Path("/tmp/elem.yaml")],
    )


class TestUploadArtifacts:
    """Tests for NginxRepoDriver._upload_artifacts."""

    def test_upload_artifacts_uploads_every_artifact(self) -> None:
        driver = nginx.NginxRepoDriver(url="http://repo.example.com")
        uploaded: list[tuple[str, str]] = []
        driver._upload_file = lambda local, remote: uploaded.append(
            (str(local), remote)
        )

        driver._upload_artifacts(_element(), "http://repo/elem/1.0.0", "elem/1.0.0", 1)

        assert uploaded == [
            ("/tmp/foo.raw", "http://repo/elem/1.0.0/images/foo.raw"),
            ("/tmp/bar.raw", "http://repo/elem/1.0.0/images/bar.raw"),
            ("/tmp/elem.yaml", "http://repo/elem/1.0.0/manifests/elem.yaml"),
        ]

    def test_upload_artifacts_parallel_uploads_every_artifact(self) -> None:
        driver = nginx.NginxRepoDriver(url="http://repo.example.com")
        lock = threading.Lock()
        threads: set[int] = set()
        uploaded: list[str] = []

        def upload_file(local: str, remote: str) -> None:
            barrier.wait(timeout=5)
            with lock:
                threads.add(threading.get_ident())
                uploaded.append(remote)

        # All three uploads must be in flight at once, otherwise the barrier
        # times out and the test fails.
        barrier = threading.Barrier(3)
        driver._upload_file = upload_file

        driver._upload_artifacts(_element(), "http://repo/elem/1.0.0", "elem/1.0.0", 3)

        assert sorted(uploaded) == [
            "http://repo/elem/1.0.0/images/bar.raw",
            "http://repo/elem/1.0.0/images/foo.raw",
            "http://repo/elem/1.0.0/manifests/elem.yaml",
        ]
        assert len(threads) == 3
