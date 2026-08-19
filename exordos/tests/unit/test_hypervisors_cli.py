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
import base64
import configparser
import getpass
from unittest.mock import MagicMock
from unittest.mock import call as mock_call
from unittest.mock import patch

import click
import pytest

from exordos.cmd.compute.hypervisors import commands as hv_commands
from exordos.common import crypto


class TestLocalAgentNodeUuid:
    """Tests for local_agent_node_uuid: node-id file, DMI product_uuid
    fallback, and the case where neither exists.
    """

    def test_reads_node_id_file_when_present(self, tmp_path) -> None:
        node_id_path = tmp_path / "node-id"
        node_id_path.write_text("some-node-uuid\n")

        result = hv_commands.local_agent_node_uuid(
            node_id_path=str(node_id_path),
            product_uuid_path=str(tmp_path / "product_uuid"),
        )

        assert result == "some-node-uuid"

    def test_falls_back_to_product_uuid_when_node_id_missing(self, tmp_path) -> None:
        product_uuid_path = tmp_path / "product_uuid"
        product_uuid_path.write_text("some-product-uuid\n")

        result = hv_commands.local_agent_node_uuid(
            node_id_path=str(tmp_path / "node-id"),
            product_uuid_path=str(product_uuid_path),
        )

        assert result == "some-product-uuid"

    def test_raises_a_clean_error_when_neither_path_exists(self, tmp_path) -> None:
        with pytest.raises(click.ClickException, match="Unable to determine"):
            hv_commands.local_agent_node_uuid(
                node_id_path=str(tmp_path / "node-id"),
                product_uuid_path=str(tmp_path / "product_uuid"),
            )


class TestAgentConfigContent:
    """Tests for the pure content-building helpers:
    _agent_config_content, _agent_systemd_unit_content.
    """

    def test_agent_config_content(self) -> None:
        content = hv_commands._agent_config_content(
            "http://10.20.0.2:11011",
            "http://10.20.0.2:11012",
            "/opt/exordos-hyper-agent/pool_meta.json",
            "/etc/exordos_universal_agent/node_private_key",
        )
        assert "orch_secure_communication = True" in content
        assert "orch_endpoint = http://10.20.0.2:11011" in content
        assert "status_endpoint = http://10.20.0.2:11012" in content
        assert (
            "private_key_path = /etc/exordos_universal_agent/node_private_key"
            in content
        )
        assert "caps_drivers = LocalPoolAgentDriver" in content
        assert "verify_node_on_register = False" in content
        assert "meta_file = /opt/exordos-hyper-agent/pool_meta.json" in content

    def test_agent_systemd_unit_content(self) -> None:
        content = hv_commands._agent_systemd_unit_content(
            "/opt/universal_agent/.venv/bin/exordos-universal-agent",
            "/etc/exordos_universal_agent/exordos_universal_agent.conf",
        )
        assert (
            "ExecStart=/opt/universal_agent/.venv/bin/exordos-universal-agent "
            "--config-file /etc/exordos_universal_agent/exordos_universal_agent.conf"
            in content
        )


class TestAgentSetup:
    """Tests for the local universal agent setup helpers:
    install_agent_venv, write_agent_config, install_agent_systemd_unit.

    All privileged filesystem/systemctl operations must go through sudo:
    `exordos bootstrap` runs as a regular, sudo-capable user, not root.
    """

    def test_generate_node_private_key_base64_produces_32_byte_key(self) -> None:
        key_base64 = hv_commands.generate_node_private_key_base64()

        assert len(base64.b64decode(key_base64)) == 32

    def test_reset_agent_meta_file_removes_it_via_sudo(self) -> None:
        with patch.object(hv_commands, "run_command") as run_mock:
            hv_commands.reset_agent_meta_file("/opt/exordos-hyper-agent/pool_meta.json")

        run_mock.assert_called_once_with(
            ["sudo", "rm", "-f", "/opt/exordos-hyper-agent/pool_meta.json"]
        )

    def test_install_agent_venv_creates_venv_and_symlinks_when_standard(
        self, tmp_path
    ) -> None:
        """No venv at the standard path yet: create one fresh, owned by
        the current user, plus the /usr/bin symlink."""
        venv_path = str(tmp_path / "agent-home" / "venv")
        with (
            patch.object(hv_commands, "run_command") as run_mock,
            patch.object(hv_commands, "STANDARD_AGENT_VENV_PATH", venv_path),
            patch.object(hv_commands, "STANDARD_AGENT_BIN_SYMLINK", "/usr/bin/fake"),
        ):
            hv_commands.install_agent_venv(venv_path)

        assert run_mock.call_args_list == [
            mock_call(["sudo", "mkdir", "-p", str(tmp_path / "agent-home")]),
            mock_call(
                ["sudo", "chown", getpass.getuser(), str(tmp_path / "agent-home")]
            ),
            mock_call(["python3", "-m", "venv", venv_path]),
            mock_call([f"{venv_path}/bin/pip", "install", "gcl_sdk[libvirt]"]),
            mock_call(
                [
                    "sudo",
                    "ln",
                    "-sf",
                    f"{venv_path}/bin/exordos-universal-agent",
                    "/usr/bin/fake",
                ]
            ),
        ]

    def test_install_agent_venv_creates_venv_without_symlink_when_custom(
        self, tmp_path
    ) -> None:
        """A custom-named agent's fresh venv must not hijack the
        standard agent's /usr/bin symlink - it may belong to an agent
        this code isn't managing."""
        venv_path = str(tmp_path / "agent-home" / "venv")
        with (
            patch.object(hv_commands, "run_command") as run_mock,
            patch.object(hv_commands, "STANDARD_AGENT_VENV_PATH", "/opt/other/.venv"),
        ):
            hv_commands.install_agent_venv(venv_path)

        assert run_mock.call_args_list == [
            mock_call(["sudo", "mkdir", "-p", str(tmp_path / "agent-home")]),
            mock_call(
                ["sudo", "chown", getpass.getuser(), str(tmp_path / "agent-home")]
            ),
            mock_call(["python3", "-m", "venv", venv_path]),
            mock_call([f"{venv_path}/bin/pip", "install", "gcl_sdk[libvirt]"]),
        ]

    def test_install_agent_venv_extends_existing_venv_via_sudo_pip(
        self, tmp_path
    ) -> None:
        """A venv already exists at this path (this host already runs the
        standard universal agent): just add libvirt-python to it via
        sudo, don't touch ownership or recreate anything."""
        venv_path = tmp_path / "agent-home" / "venv"
        venv_path.mkdir(parents=True)

        with patch.object(hv_commands, "run_command") as run_mock:
            hv_commands.install_agent_venv(str(venv_path))

        run_mock.assert_called_once_with(
            ["sudo", f"{venv_path}/bin/pip", "install", "gcl_sdk[libvirt]"]
        )

    def test_install_agent_systemd_unit_writes_enables_and_restarts(
        self, tmp_path
    ) -> None:
        unit_path = str(tmp_path / "systemd" / "agent.service")
        with (
            patch.object(hv_commands, "write_root_owned_file") as write_mock,
            patch.object(hv_commands, "run_command") as run_mock,
        ):
            hv_commands.install_agent_systemd_unit(
                config_path="/etc/exordos_universal_agent/exordos_universal_agent.conf",
                unit_path=unit_path,
                unit_name="exordos-universal-agent.service",
            )

        write_call = write_mock.call_args[0]
        assert write_call[1] == unit_path
        assert write_mock.call_args.kwargs == {"mode": "644"}
        assert run_mock.call_args_list == [
            mock_call(["sudo", "systemctl", "daemon-reload"]),
            mock_call(
                ["sudo", "systemctl", "enable", "exordos-universal-agent.service"]
            ),
            mock_call(
                ["sudo", "systemctl", "restart", "exordos-universal-agent.service"]
            ),
        ]

    def test_install_agent_systemd_unit_overwrites_a_stale_existing_unit(
        self, tmp_path
    ) -> None:
        """A unit already exists at this path - from either a genuinely
        pre-existing standard agent or a stale earlier run of this same
        code - either way it gets rewritten with the current template
        rather than left untouched."""
        unit_path = tmp_path / "systemd" / "agent.service"
        unit_path.parent.mkdir(parents=True)
        unit_path.write_text("[Unit]\nold stale content\n")

        with (
            patch.object(hv_commands, "write_root_owned_file") as write_mock,
            patch.object(hv_commands, "run_command") as run_mock,
        ):
            hv_commands.install_agent_systemd_unit(
                config_path="/etc/exordos_universal_agent/exordos_universal_agent.conf",
                unit_path=str(unit_path),
                unit_name="exordos-universal-agent.service",
            )

        write_call = write_mock.call_args[0]
        assert write_call[1] == str(unit_path)
        assert write_mock.call_args.kwargs == {"mode": "644"}
        assert run_mock.call_args_list == [
            mock_call(["sudo", "systemctl", "daemon-reload"]),
            mock_call(
                ["sudo", "systemctl", "enable", "exordos-universal-agent.service"]
            ),
            mock_call(
                ["sudo", "systemctl", "restart", "exordos-universal-agent.service"]
            ),
        ]


class TestReadExistingConfig:
    """Tests for _read_existing_config: missing vs present vs root-only
    readable (falls back to sudo cat, matching local_agent_node_uuid's
    established pattern for a root-only-readable path).
    """

    def test_returns_none_when_missing(self, tmp_path) -> None:
        assert hv_commands._read_existing_config(str(tmp_path / "missing")) is None

    def test_reads_content_directly_when_readable(self, tmp_path) -> None:
        config_path = tmp_path / "exordos_universal_agent.conf"
        config_path.write_text("[universal_agent]\n")

        assert (
            hv_commands._read_existing_config(str(config_path)) == "[universal_agent]\n"
        )

    def test_falls_back_to_sudo_cat_on_permission_error(self, tmp_path) -> None:
        config_path = tmp_path / "exordos_universal_agent.conf"
        config_path.write_text("[universal_agent]\n")

        fake_result = MagicMock(stdout="[universal_agent]\nfrom sudo cat\n")
        with (
            patch.object(hv_commands, "open", side_effect=PermissionError, create=True),
            patch.object(
                hv_commands, "run_command", return_value=fake_result
            ) as run_mock,
        ):
            content = hv_commands._read_existing_config(str(config_path))

        assert content == "[universal_agent]\nfrom sudo cat\n"
        run_mock.assert_called_once_with(["sudo", "cat", str(config_path)])


class TestWriteAgentConfig:
    """Tests for write_agent_config: fresh-install vs merge-into-existing."""

    def test_writes_fresh_config_when_none_exists(self, tmp_path) -> None:
        config_path = str(tmp_path / "exordos_universal_agent.conf")
        written = {}

        def fake_run(cmd):
            if cmd[:2] == ["sudo", "install"]:
                written["content"] = open(cmd[4]).read()

        with patch.object(crypto, "run_command", side_effect=fake_run):
            private_key_path = hv_commands.write_agent_config(
                orch_endpoint="http://10.20.0.2:11011",
                status_endpoint="http://10.20.0.2:11012",
                config_path=config_path,
                meta_file="/var/lib/exordos/universal_agent/pool_meta.json",
            )

        assert private_key_path == hv_commands.AGENT_PRIVATE_KEY_PATH
        assert "caps_drivers = LocalPoolAgentDriver" in written["content"]
        assert "orch_endpoint = http://10.20.0.2:11011" in written["content"]

    def test_merges_local_pool_driver_into_existing_config(self, tmp_path) -> None:
        """This host already runs the standard agent for other
        capabilities (it's also a registered compute node): add
        LocalPoolAgentDriver to its caps_drivers, leave orch_endpoint
        and its own private_key_path untouched."""
        config_path = tmp_path / "exordos_universal_agent.conf"
        config_path.write_text(
            "[universal_agent]\n"
            "orch_endpoint = http://core.local.genesis-core.tech:11011\n"
            "status_endpoint = http://core.local.genesis-core.tech:11012\n"
            "private_key_path = /var/lib/exordos/universal_agent/private_key\n"
            "caps_drivers = \n"
            "    SSHKeyCapabilityDriver,\n"
            "    GuestMachineCapabilityDriver\n"
        )
        written = {}

        def fake_run(cmd):
            if cmd[:2] == ["sudo", "install"]:
                written["content"] = open(cmd[4]).read()

        with patch.object(crypto, "run_command", side_effect=fake_run):
            private_key_path = hv_commands.write_agent_config(
                orch_endpoint="http://10.20.0.2:11011",
                status_endpoint="http://10.20.0.2:11012",
                config_path=str(config_path),
                meta_file="/var/lib/exordos/universal_agent/pool_meta.json",
            )

        assert private_key_path == "/var/lib/exordos/universal_agent/private_key"
        content = written["content"]
        assert "SSHKeyCapabilityDriver" in content
        assert "GuestMachineCapabilityDriver" in content
        assert "LocalPoolAgentDriver" in content
        assert "core.local.genesis-core.tech" in content
        assert "[LocalPoolAgentDriver]" in content
        assert "meta_file = /var/lib/exordos/universal_agent/pool_meta.json" in content

    def test_merge_is_idempotent_if_local_pool_driver_already_present(
        self, tmp_path
    ) -> None:
        config_path = tmp_path / "exordos_universal_agent.conf"
        config_path.write_text(
            "[universal_agent]\n"
            "caps_drivers = SSHKeyCapabilityDriver, LocalPoolAgentDriver\n"
        )
        written = {}

        def fake_run(cmd):
            if cmd[:2] == ["sudo", "install"]:
                written["content"] = open(cmd[4]).read()

        with patch.object(crypto, "run_command", side_effect=fake_run):
            hv_commands.write_agent_config(
                orch_endpoint="http://10.20.0.2:11011",
                status_endpoint="http://10.20.0.2:11012",
                config_path=str(config_path),
                meta_file="/var/lib/exordos/universal_agent/pool_meta.json",
            )

        parser = configparser.ConfigParser()
        parser.read_string(written["content"])
        drivers = [
            d.strip()
            for d in parser.get("universal_agent", "caps_drivers").split(",")
            if d.strip()
        ]
        assert drivers.count("LocalPoolAgentDriver") == 1


class TestAgentNamingHelpers:
    """Tests for the per-agent-name path builders."""

    def test_standard_name_maps_to_the_exordos_base_conventions(self) -> None:
        assert (
            hv_commands._agent_venv_path(hv_commands.DEFAULT_AGENT_NAME)
            == "/opt/universal_agent/.venv"
        )
        assert (
            hv_commands._agent_config_path(hv_commands.DEFAULT_AGENT_NAME)
            == "/etc/exordos_universal_agent/exordos_universal_agent.conf"
        )
        assert (
            hv_commands._agent_unit_name(hv_commands.DEFAULT_AGENT_NAME)
            == "exordos-universal-agent.service"
        )
        assert (
            hv_commands._agent_exec_path(hv_commands.DEFAULT_AGENT_NAME, "/x/.venv")
            == hv_commands.STANDARD_AGENT_BIN_SYMLINK
        )

    def test_custom_name_gets_parallel_paths_and_no_symlink(self) -> None:
        assert hv_commands._agent_venv_path("hyper1_pool") == "/opt/hyper1_pool/.venv"
        assert (
            hv_commands._agent_config_path("hyper1_pool")
            == "/etc/exordos_universal_agent/exordos_hyper1_pool.conf"
        )
        assert (
            hv_commands._agent_unit_name("hyper1_pool") == "exordos-hyper1-pool.service"
        )
        assert (
            hv_commands._agent_exec_path("hyper1_pool", "/opt/hyper1_pool/.venv")
            == "/opt/hyper1_pool/.venv/bin/exordos-universal-agent"
        )


class TestEndpointIdentity:
    """Tests for _endpoint_identity: resolving a URL's host to an IP so
    a DNS name and the literal IP it resolves to compare equal.
    """

    def test_resolves_hostname_to_ip(self) -> None:
        with patch.object(
            hv_commands.socket, "gethostbyname", return_value="10.100.0.2"
        ):
            assert hv_commands._endpoint_identity(
                "http://core.local.genesis-core.tech:11011"
            ) == ("10.100.0.2", 11011)

    def test_falls_back_to_raw_hostname_when_resolution_fails(self) -> None:
        with patch.object(hv_commands.socket, "gethostbyname", side_effect=OSError):
            assert hv_commands._endpoint_identity("http://unresolvable:11011") == (
                "unresolvable",
                11011,
            )

    def test_empty_host_is_not_resolved(self) -> None:
        # socket.gethostbyname("") resolves to "0.0.0.0" instead of
        # raising - resolving it would make two differently-broken
        # (hostless) endpoints compare equal, defeating the "erring
        # towards different core" default.
        with patch.object(hv_commands.socket, "gethostbyname") as gethostbyname_mock:
            identity = hv_commands._endpoint_identity("http:///no-host-here")

        gethostbyname_mock.assert_not_called()
        assert identity == ("", None)


class TestResolveAgentInstallTarget:
    """Tests for resolve_agent_install_target: fresh/matching vs a
    foreign agent already configured for a different core.
    """

    def test_no_existing_config_resolves_the_named_paths(self, tmp_path) -> None:
        config_path = str(tmp_path / "exordos_universal_agent.conf")
        with patch.object(hv_commands, "AGENT_CONFIG_DIR", str(tmp_path)):
            target = hv_commands.resolve_agent_install_target(
                agent_name=hv_commands.DEFAULT_AGENT_NAME,
                orch_endpoint="http://10.20.0.2:11011",
                status_endpoint="http://10.20.0.2:11012",
            )

        assert target.config_path == config_path
        assert target.venv_path == "/opt/universal_agent/.venv"
        assert target.exec_path == hv_commands.STANDARD_AGENT_BIN_SYMLINK

    def test_existing_config_for_the_same_core_is_accepted(self, tmp_path) -> None:
        config_path = tmp_path / "exordos_universal_agent.conf"
        config_path.write_text(
            "[universal_agent]\n"
            "orch_endpoint = http://10.20.0.2:11011\n"
            "status_endpoint = http://10.20.0.2:11012\n"
        )
        with patch.object(hv_commands, "AGENT_CONFIG_DIR", str(tmp_path)):
            target = hv_commands.resolve_agent_install_target(
                agent_name=hv_commands.DEFAULT_AGENT_NAME,
                orch_endpoint="http://10.20.0.2:11011",
                status_endpoint="http://10.20.0.2:11012",
            )

        assert target.config_path == str(config_path)

    def test_dns_name_and_literal_ip_for_the_same_core_are_accepted(
        self, tmp_path
    ) -> None:
        """The exordos-base image's own agent config points at a DNS
        name (e.g. core.local.genesis-core.tech); this code computes a
        literal IP from --endpoint. Both must be recognized as the same
        core when the name resolves to that IP, not rejected as a
        string mismatch."""
        config_path = tmp_path / "exordos_universal_agent.conf"
        config_path.write_text(
            "[universal_agent]\n"
            "orch_endpoint = http://core.local.genesis-core.tech:11011\n"
            "status_endpoint = http://core.local.genesis-core.tech:11012\n"
        )
        with (
            patch.object(hv_commands, "AGENT_CONFIG_DIR", str(tmp_path)),
            patch.object(
                hv_commands.socket, "gethostbyname", return_value="10.100.0.2"
            ),
        ):
            target = hv_commands.resolve_agent_install_target(
                agent_name=hv_commands.DEFAULT_AGENT_NAME,
                orch_endpoint="http://10.100.0.2:11011",
                status_endpoint="http://10.100.0.2:11012",
            )

        assert target.config_path == str(config_path)

    def test_existing_config_for_a_different_core_raises(self, tmp_path) -> None:
        """A machine that's also a compute node of some other, unrelated
        exordos deployment must not have its agent silently
        reconfigured to point at our core instead."""
        config_path = tmp_path / "exordos_universal_agent.conf"
        config_path.write_text(
            "[universal_agent]\n"
            "orch_endpoint = http://core.local.genesis-core.tech:11011\n"
            "status_endpoint = http://core.local.genesis-core.tech:11012\n"
        )
        with (
            patch.object(hv_commands, "AGENT_CONFIG_DIR", str(tmp_path)),
            patch.object(hv_commands.socket, "gethostbyname", side_effect=OSError),
            pytest.raises(click.ClickException, match="different core"),
        ):
            hv_commands.resolve_agent_install_target(
                agent_name=hv_commands.DEFAULT_AGENT_NAME,
                orch_endpoint="http://10.20.0.2:11011",
                status_endpoint="http://10.20.0.2:11012",
            )
