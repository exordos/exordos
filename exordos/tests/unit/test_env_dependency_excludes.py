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

import pytest

from exordos.builder import dependency


@pytest.mark.parametrize("kind", ("env", "local"))
def test_dependency_excludes_root_virtualenv_and_keeps_nested_files(
    tmp_path, monkeypatch, kind
):
    source = tmp_path / "checkout"
    for name in (".venv/large-wheel", "nested/.venv/fixture", "app.py"):
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("content")
    output = tmp_path / "output"
    output.mkdir()
    if kind == "env":
        monkeypatch.setenv("EXORDOS_TEST_CHECKOUT", str(source))
        dep = dependency.LocalEnvPathDependency.from_config(
            {
                "path": {"env": "EXORDOS_TEST_CHECKOUT"},
                "dst": "/opt/app",
                "exclude": ["/.venv"],
            },
            tmp_path,
        )
    else:
        dep = dependency.LocalPathDependency(
            str(source), "/opt/app", exclude=["/.venv"]
        )
    dep.fetch(str(output))
    copied = output / "checkout"
    assert not (copied / ".venv").exists()
    assert (copied / "nested/.venv/fixture").read_text() == "content"
    assert (copied / "app.py").read_text() == "content"


def test_env_dependency_without_excludes_copies_all_files(tmp_path, monkeypatch):
    source = tmp_path / "checkout"
    source.mkdir()
    (source / "keep.txt").write_text("keep")
    output = tmp_path / "output"
    output.mkdir()
    monkeypatch.setenv("EXORDOS_TEST_CHECKOUT", str(source))
    dep = dependency.LocalEnvPathDependency.from_config(
        {"path": {"env": "EXORDOS_TEST_CHECKOUT"}, "dst": "/opt/app"}, tmp_path
    )
    dep.fetch(str(output))
    assert (output / "checkout/keep.txt").read_text() == "keep"
