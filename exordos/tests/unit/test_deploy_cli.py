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
import ipaddress
import json
import pathlib
from unittest.mock import MagicMock
from unittest.mock import patch
import uuid as sys_uuid

import click
from click.testing import CliRunner
import pytest

from exordos.cmd.deploy import commands as deploy_commands
from exordos.common.cmd_context import ContextObject
from exordos.repo import utils as repo_utils


def _make_build_output(tmp_path: pathlib.Path) -> pathlib.Path:
    elements_dir = tmp_path / "output" / "exordos-elements"
    elements_dir.mkdir(parents=True)
    inventory = {
        "elements": {
            "foo": {
                "1.0.0": {
                    "name": "foo",
                    "version": "1.0.0",
                    "images": [],
                    "manifests": [],
                    "configs": [],
                    "templates": [],
                    "artifacts": [],
                }
            }
        }
    }
    (elements_dir / "inventory.json").write_text(json.dumps(inventory))
    return tmp_path / "output"


def _obj() -> ContextObject:
    return ContextObject(
        auth_data={"endpoint": "http://10.20.0.2:11010"},
        cfg_path=None,
        developer_key_path=None,
        cfg={},
        need_update=None,
    )


class TestLoadBuildInventory:
    def test_missing_build_raises(self, tmp_path: pathlib.Path) -> None:
        with pytest.raises(click.ClickException, match="Run `exordos build` first"):
            deploy_commands._load_build_inventory(tmp_path / "output")

    def test_loads_inventory(self, tmp_path: pathlib.Path) -> None:
        output_dir = _make_build_output(tmp_path)
        result = deploy_commands._load_build_inventory(output_dir)
        assert list(result.keys()) == ["foo"]
        assert list(result["foo"].keys()) == ["1.0.0"]


class TestIsLocalRealm:
    def test_no_current_realm_returns_false(self) -> None:
        assert deploy_commands._is_local_realm({}) is False

    def test_no_realm_config_returns_false(self) -> None:
        assert deploy_commands._is_local_realm({"current-realm": "foo"}) is False

    def test_not_local_returns_false(self) -> None:
        config = {"current-realm": "foo", "realms": {"foo": {"local": False}}}
        assert deploy_commands._is_local_realm(config) is False

    def test_local_without_cidr_returns_true(self) -> None:
        config = {"current-realm": "foo", "realms": {"foo": {"local": True}}}
        assert deploy_commands._is_local_realm(config) is True

    def test_local_with_cidr_and_matching_ip_returns_true(self) -> None:
        config = {
            "current-realm": "foo",
            "realms": {"foo": {"local": True, "meta": {"cidr": "10.20.0.0/22"}}},
        }
        with patch.object(
            deploy_commands,
            "_find_local_ip_in_network",
            return_value=ipaddress.IPv4Address("10.20.0.5"),
        ):
            assert deploy_commands._is_local_realm(config) is True

    def test_local_with_cidr_but_no_matching_ip_returns_false(self) -> None:
        config = {
            "current-realm": "foo",
            "realms": {"foo": {"local": True, "meta": {"cidr": "10.20.0.0/22"}}},
        }
        with patch.object(
            deploy_commands, "_find_local_ip_in_network", return_value=None
        ):
            assert deploy_commands._is_local_realm(config) is False


class TestGetLocalHostBind:
    def test_no_realm_raises(self) -> None:
        with pytest.raises(click.ClickException, match="Unable to determine"):
            deploy_commands._get_local_host_bind({})

    def test_realm_with_cidr_and_matching_ip_returns_ip(self) -> None:
        config = {
            "current-realm": "foo",
            "realms": {"foo": {"meta": {"cidr": "10.20.0.0/22"}}},
        }
        with patch.object(
            deploy_commands,
            "_find_local_ip_in_network",
            return_value=ipaddress.IPv4Address("10.20.0.5"),
        ):
            assert deploy_commands._get_local_host_bind(config) == "10.20.0.5"

    def test_realm_with_cidr_but_no_matching_ip_raises(self) -> None:
        config = {
            "current-realm": "foo",
            "realms": {"foo": {"meta": {"cidr": "10.20.0.0/22"}}},
        }
        with patch.object(
            deploy_commands, "_find_local_ip_in_network", return_value=None
        ):
            with pytest.raises(click.ClickException, match="Unable to determine"):
                deploy_commands._get_local_host_bind(config)


class TestFindOrUpdateRepository:
    def test_creates_when_missing_and_project_id_given(self) -> None:
        client = MagicMock()
        client.filter.return_value = []
        project_id = sys_uuid.uuid4()

        with patch.object(
            deploy_commands.base_client,
            "add_entity",
            return_value={"uuid": "new"},
        ) as add_entity:
            result = repo_utils.ensure_repository(
                client,
                "exordos-dev-repo",
                {"kind": "nginx", "url": "http://host:1/exordos-elements/"},
                project_id,
                4096,
                sync_mode="copy",
            )

        assert result == {"uuid": "new"}
        _, _, data = add_entity.call_args[0]
        assert data["project_id"] == str(project_id)
        assert data["driver_spec"] == {
            "kind": "nginx",
            "url": "http://host:1/exordos-elements/",
        }
        assert data["sync_mode"] == "copy"

    def test_creates_when_missing_with_default_project_id(self) -> None:
        client = MagicMock()
        client.filter.return_value = []
        project_id = sys_uuid.UUID(int=0)

        with patch.object(
            deploy_commands.base_client,
            "add_entity",
            return_value={"uuid": "new"},
        ) as add_entity:
            result = repo_utils.ensure_repository(
                client,
                "exordos-dev-repo",
                {"kind": "nginx", "url": "http://host/"},
                project_id,
                4096,
                sync_mode="copy",
            )

        assert result == {"uuid": "new"}
        _, _, data = add_entity.call_args[0]
        assert data["project_id"] == str(project_id)

    def test_updates_existing(self) -> None:
        client = MagicMock()
        client.filter.return_value = [{"uuid": "existing"}]

        with patch.object(
            deploy_commands.base_client,
            "update_entity",
            return_value={"uuid": "existing"},
        ) as update_entity:
            result = repo_utils.ensure_repository(
                client,
                "exordos-dev-repo",
                {"kind": "nginx", "url": "http://host/"},
                None,
                100,
                sync_mode="lazy",
            )

        assert result == {"uuid": "existing"}
        args, _ = update_entity.call_args
        assert args[2] == "existing"
        assert args[3]["priority"] == 100
        assert args[3]["sync_mode"] == "lazy"

    def test_multiple_matches_raises(self) -> None:
        client = MagicMock()
        client.filter.return_value = [{"uuid": "a"}, {"uuid": "b"}]
        with pytest.raises(click.ClickException, match="Multiple repositories"):
            repo_utils.ensure_repository(
                client,
                "exordos-dev-repo",
                {"kind": "nginx", "url": "http://host/"},
                None,
                100,
                sync_mode="lazy",
            )


class TestWaitForRepoElement:
    def test_returns_matching_element(self) -> None:
        repo_uuid = str(sys_uuid.uuid4())
        client = MagicMock()
        client.filter.return_value = [
            {
                "name": "foo",
                "version": "1.0.0",
                "uuid": "e1",
                "status": "AVAILABLE",
                "repository": f"/v1/repo/repositories/{repo_uuid}",
            }
        ]
        result = repo_utils.wait_for_repo_element(
            client, repo_uuid, "foo", "1.0.0", "AVAILABLE", timeout=5
        )
        assert result["uuid"] == "e1"

    def test_times_out_when_not_found(self) -> None:
        client = MagicMock()
        client.filter.return_value = []
        with pytest.raises(click.ClickException, match="Timed out"):
            repo_utils.wait_for_repo_element(
                client, "repo-uuid", "foo", "1.0.0", "AVAILABLE", timeout=-1
            )


class TestWaitForElementActive:
    def test_returns_when_active(self) -> None:
        client = MagicMock()
        client.filter.return_value = [{"name": "foo", "status": "ACTIVE"}]
        repo_utils.wait_for_element_active(client, "foo", "1.0.0", timeout=5)

    def test_raises_on_error_status(self) -> None:
        client = MagicMock()
        client.filter.return_value = [{"name": "foo", "status": "ERROR"}]
        with pytest.raises(click.ClickException, match="failed to install"):
            repo_utils.wait_for_element_active(client, "foo", "1.0.0", timeout=5)

    def test_times_out(self) -> None:
        client = MagicMock()
        client.filter.return_value = [{"name": "foo", "status": "IN_PROGRESS"}]
        with pytest.raises(click.ClickException, match="Timed out"):
            repo_utils.wait_for_element_active(client, "foo", "1.0.0", timeout=-1)

    def test_stable_checks_returns_after_consecutive_active(self) -> None:
        client = MagicMock()
        client.filter.return_value = [{"name": "foo", "status": "ACTIVE"}]
        with patch("exordos.repo.utils.time.sleep"):
            repo_utils.wait_for_element_active(
                client, "foo", "1.0.0", timeout=30, stable_checks=3
            )
        assert client.filter.call_count == 3

    def test_stable_checks_resets_on_non_active(self) -> None:
        statuses = [
            {"name": "foo", "status": "ACTIVE"},
            {"name": "foo", "status": "ACTIVE"},
            {"name": "foo", "status": "IN_PROGRESS"},
            {"name": "foo", "status": "ACTIVE"},
            {"name": "foo", "status": "ACTIVE"},
            {"name": "foo", "status": "ACTIVE"},
        ]
        client = MagicMock()
        client.filter.side_effect = [
            [{"name": "foo", "status": s["status"]}] for s in statuses
        ]
        with patch("exordos.repo.utils.time.sleep"):
            repo_utils.wait_for_element_active(
                client, "foo", "1.0.0", timeout=30, stable_checks=3
            )
        assert client.filter.call_count == 6


class TestDeployCmdPushMode:
    def test_rejects_non_http_driver(self, tmp_path: pathlib.Path) -> None:
        output_dir = _make_build_output(tmp_path)
        fake_driver = MagicMock()
        fake_driver.elements_path = str(tmp_path / "some" / "local" / "path")

        runner = CliRunner()
        with (
            patch.object(
                deploy_commands.base_client,
                "get_user_api_client",
                return_value=MagicMock(),
            ),
            patch.object(
                deploy_commands.repo_utils,
                "load_repo_driver_from_settings",
                return_value=fake_driver,
            ),
            patch.object(deploy_commands.repo_utils, "do_push") as do_push_mock,
        ):
            result = runner.invoke(
                deploy_commands.deploy_cmd,
                ["-e", str(output_dir), "-t", "my-target"],
                obj=_obj(),
            )

        assert result.exit_code != 0
        assert "network-reachable" in result.output
        do_push_mock.assert_called_once()

    def test_pushes_then_deploys_when_http(self, tmp_path: pathlib.Path) -> None:
        output_dir = _make_build_output(tmp_path)
        fake_driver = MagicMock()
        fake_driver.elements_path = "http://repo.example.com/exordos-elements"

        runner = CliRunner()
        with (
            patch.object(
                deploy_commands.base_client,
                "get_user_api_client",
                return_value=MagicMock(),
            ),
            patch.object(
                deploy_commands.repo_utils,
                "load_repo_driver_from_settings",
                return_value=fake_driver,
            ),
            patch.object(deploy_commands.repo_utils, "do_push") as do_push_mock,
            patch.object(
                deploy_commands.repo_utils,
                "ensure_repository",
                return_value={"uuid": "repo-uuid"},
            ) as find_repo_mock,
            patch.object(deploy_commands, "_deploy_element") as deploy_elements_mock,
        ):
            result = runner.invoke(
                deploy_commands.deploy_cmd,
                ["-e", str(output_dir), "-t", "my-target"],
                obj=_obj(),
            )

        assert result.exit_code == 0, result.output
        do_push_mock.assert_called_once()
        find_repo_mock.assert_called_once()
        assert find_repo_mock.call_args[0][2] == {
            "kind": "nginx",
            "url": "http://repo.example.com/exordos-elements/",
        }
        assert find_repo_mock.call_args[1]["sync_mode"] == "lazy"
        deploy_elements_mock.assert_called_once()


class TestDeployCmdLocalMode:
    def test_errors_without_local_realm(self, tmp_path: pathlib.Path) -> None:
        output_dir = _make_build_output(tmp_path)

        runner = CliRunner()
        with patch.object(
            deploy_commands.base_client,
            "get_user_api_client",
            return_value=MagicMock(),
        ):
            result = runner.invoke(
                deploy_commands.deploy_cmd, ["-e", str(output_dir)], obj=_obj()
            )

        assert result.exit_code != 0
        assert "not a local realm" in result.output

    def test_local_mode_deploys(self, tmp_path: pathlib.Path) -> None:
        output_dir = _make_build_output(tmp_path)

        @contextlib.contextmanager
        def fake_serve_directory(path, host, port=0):
            yield f"http://{host}:9999/"

        runner = CliRunner()
        with (
            patch.object(
                deploy_commands.base_client,
                "get_user_api_client",
                return_value=MagicMock(),
            ),
            patch.object(deploy_commands, "_is_local_realm", return_value=True),
            patch.object(
                deploy_commands, "_get_local_host_bind", return_value="192.168.1.5"
            ),
            patch.object(
                deploy_commands.local_server,
                "serve_directory",
                side_effect=fake_serve_directory,
            ),
            patch.object(
                deploy_commands.repo_utils,
                "ensure_repository",
                return_value={"uuid": "repo-uuid"},
            ) as find_repo_mock,
            patch.object(deploy_commands, "_deploy_element") as deploy_elements_mock,
        ):
            result = runner.invoke(
                deploy_commands.deploy_cmd,
                ["-e", str(output_dir)],
                obj=_obj(),
            )

        assert result.exit_code == 0, result.output
        find_repo_mock.assert_called_once()
        assert find_repo_mock.call_args[0][2] == {
            "kind": "nginx",
            "url": "http://192.168.1.5:9999/exordos-elements/",
        }
        assert find_repo_mock.call_args[1]["sync_mode"] == "copy"
        deploy_elements_mock.assert_called_once()
