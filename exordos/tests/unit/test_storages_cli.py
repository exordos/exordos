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
from unittest.mock import MagicMock
from unittest.mock import patch

import click
from click.testing import CliRunner
import pytest

from exordos.cmd.compute.hypervisors import commands as hv_commands
from exordos.cmd.storages import commands as storages_commands
from exordos.common.cmd_context import ContextObject


def _obj(auth_data: dict | None = None) -> ContextObject:
    return ContextObject(
        auth_data=auth_data or {"endpoint": "http://10.20.0.2/api/core"},
        cfg_path=None,
        developer_key_path=None,
        cfg={},
        need_update=None,
    )


_FAKE_AGENT_TARGET = hv_commands.AgentInstallTarget(
    venv_path="/opt/universal_agent/.venv",
    exec_path="/usr/bin/exordos-universal-agent",
    config_path="/etc/exordos_universal_agent/exordos_universal_agent.conf",
    meta_file="/var/lib/exordos/universal_agent/pool_meta.json",
    default_private_key_path="/var/lib/exordos/universal_agent/private_key",
    unit_path="/etc/systemd/system/exordos-universal-agent.service",
    unit_name="exordos-universal-agent.service",
)


class TestProvisionRawstorCluster:
    def test_returns_driver_spec_and_default_pool(self) -> None:
        with (
            patch.object(hv_commands, "install_rawstor_packages") as install_mock,
            patch.object(storages_commands, "write_root_owned_file") as write_mock,
            patch.object(storages_commands, "run_command") as run_mock,
            patch.object(
                storages_commands,
                "_detect_local_endpoint",
                return_value="ost://10.0.0.5:7777",
            ),
            patch.object(
                storages_commands, "_backing_store_capacity_gb", return_value=100
            ),
        ):
            driver_spec, storage_pools = storages_commands.provision_rawstor_cluster(
                log=hv_commands.ClickLogger(),
                add_sudo=True,
                location=None,
                speed="HOT",
                ephemeral=False,
                endpoint=None,
                core_endpoint="http://10.20.0.2/api/core",
            )

        install_mock.assert_called_once_with(["librawstor", "rawstor-ost"], True)
        write_mock.assert_called_once_with(
            "BIND_ADDR=10.0.0.5:7777\n",
            storages_commands.RAWSTOR_OST_CONF_PATH,
            mode="644",
        )
        run_mock.assert_called_once_with(
            ["systemctl", "restart", "rawstor-ost"], sudo=True
        )
        assert driver_spec == {
            "kind": "rawstor",
            "location": storages_commands.RAWSTOR_DEFAULT_BACKING_STORE,
            "endpoint": "ost://10.0.0.5:7777",
            "speed": "HOT",
            "ephemeral": False,
        }
        assert storage_pools == [
            {
                "kind": "thin_storage_pool",
                "pool_type": "rawstor",
                "name": "default",
                "speed": "HOT",
                "ephemeral": False,
                "capacity_usable": 100,
            }
        ]

    def test_explicit_location_reconfigures_and_restarts_rawstor_ost(self) -> None:
        with (
            patch.object(hv_commands, "install_rawstor_packages"),
            patch.object(storages_commands, "write_root_owned_file") as write_mock,
            patch.object(storages_commands, "run_command") as run_mock,
            patch.object(
                storages_commands,
                "_detect_local_endpoint",
                return_value="ost://10.0.0.5:7777",
            ),
            patch.object(
                storages_commands, "_backing_store_capacity_gb", return_value=50
            ),
        ):
            driver_spec, _ = storages_commands.provision_rawstor_cluster(
                log=hv_commands.ClickLogger(),
                add_sudo=False,
                location="file:///data/rawstor",
                speed="COLD",
                ephemeral=True,
                endpoint="ost://1.2.3.4:7777",
                core_endpoint="http://10.20.0.2/api/core",
            )

        write_mock.assert_called_once_with(
            "BIND_ADDR=1.2.3.4:7777\nLOCATION=file:///data/rawstor\n",
            storages_commands.RAWSTOR_OST_CONF_PATH,
            mode="644",
        )
        run_mock.assert_called_once_with(
            ["systemctl", "restart", "rawstor-ost"], sudo=False
        )
        assert driver_spec["location"] == "file:///data/rawstor"
        assert driver_spec["endpoint"] == "ost://1.2.3.4:7777"


class TestDetectLocalEndpoint:
    def test_uses_the_interface_that_reaches_the_core(self) -> None:
        with patch("socket.gethostbyname", return_value="10.20.0.2"):
            with patch("socket.socket") as socket_cls:
                sock = socket_cls.return_value.__enter__.return_value
                sock.getsockname.return_value = ("10.20.0.5", 12345)

                endpoint = storages_commands._detect_local_endpoint(
                    "http://10.20.0.2/api/core"
                )

        assert endpoint == "ost://10.20.0.5:7777"

    def test_raises_a_clean_error_when_unreachable(self) -> None:
        with patch("socket.gethostbyname", side_effect=OSError("no route")):
            with pytest.raises(click.ClickException, match="Unable to auto-detect"):
                storages_commands._detect_local_endpoint("http://10.20.0.2/api/core")


class TestBackingStoreCapacityGb:
    def test_reports_total_capacity_in_gib(self, tmp_path) -> None:
        with patch(
            "shutil.disk_usage",
            return_value=type(
                "Usage", (), {"total": 100 << 30, "free": 0, "used": 0}
            )(),
        ):
            assert (
                storages_commands._backing_store_capacity_gb(f"file://{tmp_path}")
                == 100
            )

    def test_returns_zero_when_the_path_is_unreachable(self) -> None:
        with patch("shutil.disk_usage", side_effect=OSError):
            assert storages_commands._backing_store_capacity_gb("file:///nope") == 0


@pytest.fixture
def _patch_common_init_deps():
    with (
        patch.object(hv_commands, "_check_debian_like", return_value=True),
        patch("subprocess.call", return_value=0),
        patch.object(
            hv_commands,
            "resolve_agent_install_target",
            return_value=_FAKE_AGENT_TARGET,
        ),
        patch.object(hv_commands, "install_agent_venv") as venv_mock,
    ):
        yield venv_mock


class TestInitCmdRegistration:
    """Tests for exordos.cmd.storages.commands.init_cmd: the always-on
    provisioning, and the --add-gated registration step.
    """

    def test_requires_type_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(storages_commands.init_cmd, [], obj=_obj())

        assert result.exit_code != 0
        assert "--type" in result.output

    def test_installs_gcl_sdk_without_the_libvirt_extra(
        self, _patch_common_init_deps
    ) -> None:
        runner = CliRunner()
        fake_provisioner = MagicMock(return_value=({"kind": "rawstor"}, []))
        with patch.dict(
            storages_commands.STORAGE_TYPE_PROVISIONERS, {"rawstor": fake_provisioner}
        ):
            result = runner.invoke(
                storages_commands.init_cmd, ["--type", "rawstor"], obj=_obj()
            )

        assert result.exit_code == 0, result.output
        _patch_common_init_deps.assert_called_once_with(
            _FAKE_AGENT_TARGET.venv_path,
            packages=["gcl_sdk", hv_commands.RAWSTOR_WHEEL_URL],
        )

    def test_without_add_skips_registration(self, _patch_common_init_deps) -> None:
        runner = CliRunner()
        fake_provisioner = MagicMock(return_value=({"kind": "rawstor"}, []))
        with (
            patch.dict(
                storages_commands.STORAGE_TYPE_PROVISIONERS,
                {"rawstor": fake_provisioner},
            ),
            patch.object(storages_commands, "add_cmd") as add_cmd_mock,
        ):
            result = runner.invoke(
                storages_commands.init_cmd, ["--type", "rawstor"], obj=_obj()
            )

        assert result.exit_code == 0, result.output
        add_cmd_mock.assert_not_called()

    def test_add_invokes_add_cmd_with_the_provisioned_spec(
        self, _patch_common_init_deps
    ) -> None:
        runner = CliRunner()
        driver_spec = {
            "kind": "rawstor",
            "location": "file:///var/lib/rawstor",
            "endpoint": "ost://10.0.0.5:7777",
            "speed": "HOT",
            "ephemeral": False,
        }
        storage_pools = [
            {
                "name": "default",
                "speed": "HOT",
                "ephemeral": False,
                "capacity_usable": 100,
            }
        ]
        fake_provisioner = MagicMock(return_value=(driver_spec, storage_pools))
        with (
            patch.dict(
                storages_commands.STORAGE_TYPE_PROVISIONERS,
                {"rawstor": fake_provisioner},
            ),
            patch.object(
                hv_commands, "_default_hypervisor_uuid", return_value="uuid-1"
            ),
            patch.object(
                hv_commands, "_default_hypervisor_name", return_value="storage-1"
            ),
            patch.object(storages_commands, "add_cmd") as add_cmd_mock,
            patch.object(storages_commands.base_client, "get_user_api_client"),
            patch.object(hv_commands, "local_agent_node_uuid", return_value="node-1"),
            patch.object(hv_commands, "reset_agent_meta_file"),
            patch.object(hv_commands, "write_agent_config") as write_config_mock,
            patch.object(
                storages_commands.base_client, "register_agent_and_write_key"
            ) as register_mock,
            patch.object(hv_commands, "install_agent_systemd_unit"),
        ):
            result = runner.invoke(
                storages_commands.init_cmd, ["--type", "rawstor", "--add"], obj=_obj()
            )

        assert result.exit_code == 0, result.output
        add_cmd_mock.assert_called_once()
        kwargs = add_cmd_mock.call_args.kwargs
        assert "kind=rawstor" in kwargs["driver_spec"]
        assert "endpoint=ost://10.0.0.5:7777" in kwargs["driver_spec"]
        assert kwargs["storage_pools"] == json.dumps(storage_pools)

        write_config_mock.assert_called_once()
        assert write_config_mock.call_args.kwargs["driver_name"] == (
            "StorageClusterAgentDriver"
        )
        register_mock.assert_called_once()
        assert register_mock.call_args.kwargs["capabilities"] == (
            storages_commands.STORAGE_CLUSTER_AGENT_CAPABILITIES
        )
