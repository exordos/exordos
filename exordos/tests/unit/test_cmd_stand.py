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

import ipaddress
import multiprocessing
import os
import pathlib
import stat
from unittest import mock

import click
import pytest
import rich.console
import yaml

from exordos.cmd.compute.hypervisors import commands as hv_commands
from exordos.cmd.stand import commands


def test_save_admin_password_file_uses_owner_only_permissions(
    tmp_path: pathlib.Path,
) -> None:
    password_path = tmp_path / "secrets" / "admin-password"
    previous_umask = os.umask(0o002)
    try:
        commands._save_admin_password_file(
            str(password_path), "test-password", mock.Mock()
        )
    finally:
        os.umask(previous_umask)

    assert password_path.read_text(encoding="utf-8") == "test-password"
    assert stat.S_IMODE(password_path.stat().st_mode) == 0o600


def test_print_bootstrap_summary_includes_core_version_in_realm() -> None:
    console = rich.console.Console(record=True)
    with mock.patch("rich.console.Console", return_value=console):
        commands._print_bootstrap_summary(
            installation_name="test-realm",
            core_version="1.2.3",
            admin_password="test-password",
            core_ip=None,
            ssh_public_key_path="~/.ssh/test.pub",
            ssh_private_key_path=None,
        )

    assert "1.2.3" in console.export_text()


class TestResolveHypervisorPlacement:
    _CIDR = ipaddress.IPv4Network("10.20.0.0/22")

    def test_core_without_explicit_uri_defaults_to_network_first_address(self):
        uri, kind = commands._resolve_hypervisor_placement("core", "", self._CIDR)

        assert uri == "qemu+tcp://10.20.0.1/system"
        assert kind == "libvirt"

    def test_core_with_explicit_uri_uses_it_unchanged(self):
        uri, kind = commands._resolve_hypervisor_placement(
            "core", "qemu+ssh://user@10.0.0.5/system", self._CIDR
        )

        assert uri == "qemu+ssh://user@10.0.0.5/system"
        assert kind == "libvirt"

    def test_local_without_explicit_uri_uses_the_local_socket(self):
        uri, kind = commands._resolve_hypervisor_placement("local", "", self._CIDR)

        assert uri == hv_commands.DEFAULT_LOCAL_CONNECTION_URI
        assert kind == "exordos_local_hyper"

    def test_local_with_explicit_uri_is_rejected(self):
        with pytest.raises(click.UsageError, match="--pool-agent-placement=local"):
            commands._resolve_hypervisor_placement(
                "local", "qemu+tcp://10.0.0.5/system", self._CIDR
            )


def _write_realm(args: tuple) -> None:
    cfg_path, name = args
    from exordos.cmd.stand import commands as stand_commands

    stand_commands._update_realm_config(
        name,
        ipaddress.IPv4Address("10.40.0.2"),
        ipaddress.IPv4Network("10.40.0.0/22"),
        "admin",
        cfg_path,
    )


def test_update_realm_config_keeps_parallel_writes(tmp_path) -> None:
    cfg_path = str(tmp_path / "exordosctl.yaml")
    names = [f"test{i}" for i in range(8)]

    with multiprocessing.Pool(len(names)) as pool:
        pool.map(_write_realm, [(cfg_path, name) for name in names])

    with open(cfg_path) as f:
        config = yaml.safe_load(f)

    assert sorted(config["realms"]) == sorted(names)
