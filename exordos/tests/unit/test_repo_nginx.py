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

import json
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


class _FakeResponse:
    def __init__(self, status_code: int, body: dict | None = None) -> None:
        self.status_code = status_code
        self._body = body

    def json(self) -> dict:
        return self._body

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError(f"HTTP {self.status_code}")


class _FakeSession:
    """Serves one in-memory repo-level index over GET and PUT."""

    def __init__(self, index: dict | None = None) -> None:
        self.index = index

    def get(self, url: str) -> _FakeResponse:
        if self.index is None:
            return _FakeResponse(404)
        return _FakeResponse(200, self.index)

    def put(self, url: str, data: bytes) -> _FakeResponse:
        self.index = json.loads(data)
        return _FakeResponse(201)


class TestIndex:
    """The realm reads the repo-level inventory.json before anything else."""

    def test_token_is_sent_as_bearer(self) -> None:
        driver = nginx.NginxRepoDriver(url="http://repo", token="tkn")

        assert driver._session.headers["Authorization"] == "Bearer tkn"

    def test_first_push_creates_the_index(self) -> None:
        driver = nginx.NginxRepoDriver(url="http://repo", update_index=True)
        driver._session = _FakeSession()

        driver._set_index_entry(_element(), {"name": "elem"})

        assert driver._session.index == {
            "elements": {"elem": {"1.0.0": {"name": "elem"}}}
        }

    def test_push_keeps_other_elements_and_versions(self) -> None:
        driver = nginx.NginxRepoDriver(url="http://repo", update_index=True)
        driver._session = _FakeSession(
            {"elements": {"elem": {"0.9.0": {}}, "other": {"2.0.0": {}}}}
        )

        driver._set_index_entry(_element(), {"name": "elem"})

        assert driver._session.index == {
            "elements": {
                "elem": {"0.9.0": {}, "1.0.0": {"name": "elem"}},
                "other": {"2.0.0": {}},
            }
        }

    def test_remove_drops_the_version_and_an_emptied_element(self) -> None:
        driver = nginx.NginxRepoDriver(url="http://repo", update_index=True)
        driver._session = _FakeSession(
            {"elements": {"elem": {"1.0.0": {}}, "other": {"2.0.0": {}}}}
        )

        driver._set_index_entry(_element(), None)

        assert driver._session.index == {"elements": {"other": {"2.0.0": {}}}}

    def test_index_lives_next_to_the_elements(self) -> None:
        driver = nginx.NginxRepoDriver(url="http://realm/repo/p1")

        assert (
            driver.index_path == "http://realm/repo/p1/exordos-elements/inventory.json"
        )
