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
import pathlib
from unittest import mock

from click.testing import CliRunner
import pytest
import rich_click as click

from exordos import constants as c
from exordos.cmd.stand import commands
from exordos.cmd.stand.commands import _load_realm_spec


def _valid_spec() -> dict:
    # Contract pinned in exordos_ecosystem docs/realm-manager.md
    return {
        "version": 1,
        "realm_uuid": "c0ffee00-0000-4000-8000-000000000000",
        "realm_name": "customer-realm",
        "realm_domain": "c0ffee.exordos.io",
        "realm_secret": "b" * 128,
        "ecosystem_endpoint": "https://ecosystem.exordos.io",
        "admin_password": "super-secret-password",
        "realm_tokens": {
            "access_token": "at",
            "refresh_token": "rt",
        },
        "disable_telemetry": False,
    }


class TestLoadRealmSpec:
    def test_valid_spec(self, tmp_path) -> None:
        path = tmp_path / "realm_spec.json"
        path.write_text(json.dumps(_valid_spec()))

        spec = _load_realm_spec(str(path))

        assert spec["realm_uuid"] == "c0ffee00-0000-4000-8000-000000000000"
        assert spec["realm_secret"] == "b" * 128
        assert spec["realm_tokens"]["access_token"] == "at"
        assert spec["ecosystem_endpoint"] == "https://ecosystem.exordos.io"
        assert spec["admin_password"] == "super-secret-password"

    @pytest.mark.parametrize(
        "missing_key",
        [
            "realm_uuid",
            "realm_secret",
            "realm_tokens",
            "ecosystem_endpoint",
            "admin_password",
        ],
    )
    def test_missing_required_key(self, tmp_path, missing_key) -> None:
        spec = _valid_spec()
        del spec[missing_key]
        path = tmp_path / "realm_spec.json"
        path.write_text(json.dumps(spec))

        with pytest.raises(click.UsageError, match=missing_key):
            _load_realm_spec(str(path))

    def test_unsupported_version(self, tmp_path) -> None:
        spec = _valid_spec()
        spec["version"] = 2
        path = tmp_path / "realm_spec.json"
        path.write_text(json.dumps(spec))

        with pytest.raises(click.UsageError, match="version"):
            _load_realm_spec(str(path))

    def test_empty_realm_tokens_allowed(self, tmp_path) -> None:
        # An empty realm_tokens object is valid (only presence is required).
        spec = _valid_spec()
        spec["realm_tokens"] = {}
        path = tmp_path / "realm_spec.json"
        path.write_text(json.dumps(spec))

        assert _load_realm_spec(str(path))["realm_tokens"] == {}

    def test_empty_string_key_rejected(self, tmp_path) -> None:
        spec = _valid_spec()
        spec["admin_password"] = ""
        path = tmp_path / "realm_spec.json"
        path.write_text(json.dumps(spec))

        with pytest.raises(click.UsageError, match="admin_password"):
            _load_realm_spec(str(path))

    def test_not_a_json_object(self, tmp_path) -> None:
        path = tmp_path / "realm_spec.json"
        path.write_text(json.dumps(["not", "an", "object"]))

        with pytest.raises(click.UsageError, match="must be a JSON object"):
            _load_realm_spec(str(path))

    def test_invalid_json(self, tmp_path) -> None:
        path = tmp_path / "realm_spec.json"
        path.write_text("{not valid json")

        with pytest.raises(click.UsageError, match="not a valid JSON"):
            _load_realm_spec(str(path))

    def test_unreadable_file(self, tmp_path) -> None:
        path = tmp_path / "does_not_exist.json"

        with pytest.raises(click.ClickException, match="Failed to read"):
            _load_realm_spec(str(path))


@pytest.mark.parametrize("elements", [None, "app", [1], [""], ["  "]])
def test_load_realm_spec_rejects_invalid_elements(
    tmp_path: pathlib.Path, elements: object
) -> None:
    spec = _valid_spec() | {"elements": elements}
    path = tmp_path / "realm_spec.json"
    path.write_text(json.dumps(spec))
    with pytest.raises(click.UsageError, match="elements"):
        _load_realm_spec(str(path))


@pytest.mark.parametrize(
    ("repo_url", "repositories", "expected_repositories"),
    [
        (None, (), (f"{c.ELEMENT_REPO_URL}/",)),
        ("", (), (f"{c.ELEMENT_REPO_URL}/",)),
        (
            "https://repo.example.com",
            (),
            (f"{c.ELEMENT_REPO_URL}/", "https://repo.example.com"),
        ),
        (
            "https://repo.example.com",
            ("https://other.example.com",),
            ("https://other.example.com", "https://repo.example.com"),
        ),
        (
            "https://repo.example.com",
            ("https://repo.example.com",),
            ("https://repo.example.com",),
        ),
    ],
)
@pytest.mark.parametrize(
    ("spec_elements", "cli_elements", "expected"),
    [
        (["exordos_s3", "exordos_db"], [], ["exordos_s3", "exordos_db"]),
        (["exordos_s3"], ["exordos_db"], ["exordos_db"]),
        ([], [], None),
    ],
)
def test_bootstrap_uses_realm_spec_elements_unless_cli_overrides(
    tmp_path: pathlib.Path,
    spec_elements: list[str],
    cli_elements: list[str],
    expected: list[str] | None,
    repo_url: str | None,
    repositories: tuple[str, ...],
    expected_repositories: tuple[str, ...],
) -> None:
    spec = _valid_spec() | {
        "elements": spec_elements,
        "ssh_public_key": "ssh-ed25519 AAAA test",
        "repo_url": repo_url,
    }
    path = tmp_path / "realm_spec.json"
    path.write_text(json.dumps(spec))
    inventory = mock.Mock(images=["core.raw"], manifests=["core.yaml"], version="1.0.0")
    args = [
        "--inventory",
        "1.0.0",
        "--launch-mode",
        "core",
        "--realm-spec",
        str(path),
        "--no-update-realm",
        "--no-start",
    ]
    for name in cli_elements:
        args.extend(["--elements", name])
    for url in repositories:
        args.extend(["--repository", url])
    with (
        mock.patch.object(
            commands, "get_element_inventory_from_url", return_value=inventory
        ),
        mock.patch.object(
            commands, "_get_core_image_uri_from_manifest", return_value=None
        ),
        mock.patch.object(commands.subprocess, "call", return_value=0),
        mock.patch.object(commands, "_bootstrap_core", return_value=None) as bootstrap,
        mock.patch.object(commands, "_print_bootstrap_summary"),
    ):
        result = CliRunner().invoke(commands.bootstrap_cmd, args)
    assert result.exit_code == 0, result.output
    assert bootstrap.call_args.kwargs["elements"] == expected
    assert bootstrap.call_args.kwargs["repository"] == expected_repositories
    assert bootstrap.call_args.kwargs["repo_url"] == repo_url
