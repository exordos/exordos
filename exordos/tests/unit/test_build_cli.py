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
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

from click.testing import CliRunner
import yaml

from exordos.cmd.builds import commands


def test_build_cmd_element_builds_only_requested_element(monkeypatch, tmp_path) -> None:
    project_dir = tmp_path / "project"
    output_dir = tmp_path / "output"
    project_dir.mkdir()
    (project_dir / "app1.yaml").write_text("name: app1\n")
    (project_dir / "app2.yaml").write_text("name: app2\n")
    (project_dir / "exordos.yaml").write_text(
        yaml.safe_dump(
            {
                "build": {
                    "elements": [
                        {"manifest": "app1.yaml"},
                        {"manifest": "app2.yaml"},
                    ]
                }
            }
        )
    )
    monkeypatch.setattr(commands.utils, "load_spec", lambda: {})
    monkeypatch.setattr(commands.schema, "validate_yaml", MagicMock())
    monkeypatch.setattr(commands, "get_project_version", lambda _: "1.0.0")
    monkeypatch.setattr(commands.utils, "get_keys_by_path_or_env", lambda *_: "")

    result = CliRunner().invoke(
        commands.build_cmd,
        [
            "-e",
            "app2",
            "--no-validate",
            "--output-dir",
            str(output_dir),
            str(project_dir),
        ],
        obj=SimpleNamespace(developer_key_path=None),
    )

    assert result.exit_code == 0, result.output
    inventory = json.loads(
        (output_dir / "exordos-elements" / "inventory.json").read_text()
    )
    assert inventory["elements"].keys() == {"app2"}
    assert not (output_dir / "exordos-elements" / "app1").exists()


def test_build_cmd_unknown_element_exits_before_build(monkeypatch, tmp_path) -> None:
    builder = MagicMock()
    builder.select_element.return_value = False
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    marker = output_dir / "existing-artifact"
    marker.write_text("keep")
    monkeypatch.setattr(
        commands.utils,
        "get_exordos_config",
        lambda *_: ({"build": {"elements": [{}]}}, tmp_path / "exordos.yaml"),
    )
    monkeypatch.setattr(commands.utils, "load_spec", lambda: {})
    monkeypatch.setattr(commands.schema, "validate_yaml", MagicMock())
    monkeypatch.setattr(commands, "get_project_version", lambda _: "1.0.0")
    monkeypatch.setattr(commands, "PackerBuilder", MagicMock())
    monkeypatch.setattr(
        commands.simple_builder.SimpleBuilder,
        "from_config",
        MagicMock(return_value=builder),
    )
    monkeypatch.setattr(commands.utils, "get_keys_by_path_or_env", lambda *_: "")

    result = CliRunner().invoke(
        commands.build_cmd,
        [
            "--element",
            "missing",
            "--force",
            "--output-dir",
            str(output_dir),
            ".",
        ],
        obj=SimpleNamespace(developer_key_path=None),
    )

    assert result.exit_code == 1
    assert "Element 'missing' not found in the configuration" in result.output
    assert marker.read_text() == "keep"
    builder.fetch_dependency.assert_not_called()
    builder.build.assert_not_called()


def test_clear_build_cache_cmd_removes_default_dir(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("PACKER_CACHE_DIR", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    cache_dir = tmp_path / ".cache" / "packer"
    cache_dir.mkdir(parents=True)
    (cache_dir / "image.iso").write_text("data")

    result = CliRunner().invoke(commands.clear_build_cache_cmd)

    assert result.exit_code == 0, result.output
    assert not cache_dir.exists()


def test_clear_build_cache_cmd_uses_xdg_cache_home(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("PACKER_CACHE_DIR", raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    cache_dir = tmp_path / "packer"
    cache_dir.mkdir()

    result = CliRunner().invoke(commands.clear_build_cache_cmd)

    assert result.exit_code == 0, result.output
    assert not cache_dir.exists()


def test_clear_build_cache_cmd_uses_packer_cache_dir(monkeypatch, tmp_path) -> None:
    cache_dir = tmp_path / "custom_cache"
    cache_dir.mkdir()
    monkeypatch.setenv("PACKER_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))

    result = CliRunner().invoke(commands.clear_build_cache_cmd)

    assert result.exit_code == 0, result.output
    assert not cache_dir.exists()


def test_clear_build_cache_cmd_missing_dir(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PACKER_CACHE_DIR", str(tmp_path / "missing"))

    result = CliRunner().invoke(commands.clear_build_cache_cmd)

    assert result.exit_code == 0, result.output
    assert "does not exist" in result.output


def test_build_cmd_jobs_passed_to_builder(monkeypatch, tmp_path) -> None:
    from_config = MagicMock()
    monkeypatch.setattr(
        commands.utils,
        "get_exordos_config",
        lambda *_: ({"build": {"elements": [{}]}}, tmp_path / "exordos.yaml"),
    )
    monkeypatch.setattr(commands.utils, "load_spec", lambda: {})
    monkeypatch.setattr(commands.schema, "validate_yaml", MagicMock())
    monkeypatch.setattr(commands, "get_project_version", lambda _: "1.0.0")
    monkeypatch.setattr(commands, "PackerBuilder", MagicMock())
    monkeypatch.setattr(
        commands.simple_builder.SimpleBuilder, "from_config", from_config
    )
    monkeypatch.setattr(commands.utils, "get_keys_by_path_or_env", lambda *_: "")

    result = CliRunner().invoke(
        commands.build_cmd,
        ["-j", "2", "--output-dir", str(tmp_path / "out"), "."],
        obj=SimpleNamespace(developer_key_path=None),
    )

    assert result.exit_code == 0, result.output
    assert from_config.call_args.args[-1] == 2
    from_config.return_value.build.assert_called_once()


def test_build_cmd_jobs_rejects_zero(tmp_path) -> None:
    result = CliRunner().invoke(
        commands.build_cmd,
        ["--jobs", "0", str(tmp_path)],
        obj=SimpleNamespace(developer_key_path=None),
    )

    assert result.exit_code == 2
