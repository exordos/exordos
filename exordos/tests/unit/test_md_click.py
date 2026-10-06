#    Copyright 2026 Genesis Corporation.
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

import rich_click as click
from rich_click import rich_click as rich_config

from exordos.common import md_click


def test_dump_helper_is_independent_of_terminal_settings(tmp_path, monkeypatch):
    @click.group(help="Manage resources")
    def resources():
        pass

    @resources.command(help="Create a resource with tags")
    @click.option("--tag", multiple=True, help="A long tag description " * 12)
    def create(tag):
        pass

    monkeypatch.setattr(md_click.utils, "PROJECT_PATH", str(tmp_path))
    outputs = []
    for width, color in [(40, "1"), (180, "0")]:
        monkeypatch.setenv("COLUMNS", str(width))
        monkeypatch.setenv("FORCE_COLOR", color)
        monkeypatch.setattr(rich_config, "WIDTH", width)
        monkeypatch.setattr(rich_config, "MAX_WIDTH", width)
        monkeypatch.setattr(rich_config, "FORCE_TERMINAL", color == "1")
        md_click.dump_helper(resources)
        outputs.append(
            {p.name: p.read_bytes() for p in (tmp_path / "docs/cli").glob("*.md")}
        )

    assert outputs[0] == outputs[1]
    assert set(outputs[0]) == {"resources.md", "resources_create.md"}
    assert all(b"\x1b" not in content for content in outputs[0].values())
    assert b"A long tag description" in outputs[0]["resources_create.md"]
    assert rich_config.WIDTH == 180
