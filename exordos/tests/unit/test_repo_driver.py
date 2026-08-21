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
"""Unit tests for exordos.repo drivers."""

import json
import pathlib

from exordos.builder import base as builder_base
from exordos.repo import fs as repo_fs


def _push(tmp_path: pathlib.Path, project: str | None) -> dict:
    driver = repo_fs.FSRepoDriver(str(tmp_path))
    driver.init_repo()
    element = builder_base.ElementInventory(name="elem", version="1.0.0")
    driver.push(element, project=project)
    with open(driver.elements_inventory_path(element)) as f:
        return json.load(f)


class TestFSRepoDriverPush:
    """Tests for exordos.repo.fs.FSRepoDriver.push."""

    def test_push_with_project(self, tmp_path: pathlib.Path) -> None:
        spec = _push(tmp_path, "my-project")
        assert spec["project"] == "my-project"

    def test_push_without_project(self, tmp_path: pathlib.Path) -> None:
        spec = _push(tmp_path, None)
        assert "project" not in spec
