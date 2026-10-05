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
from unittest.mock import patch

from click.testing import CliRunner
import pytest

from exordos.cmd.storages import commands as storage

CLUSTER_UUID = "11111111-1111-1111-1111-111111111111"
NODE_UUID = "22222222-2222-2222-2222-222222222222"


def invoke(args, **kwargs):
    return CliRunner().invoke(
        storage.storages_group,
        args,
        obj=SimpleNamespace(auth_data={"endpoint": "http://10.100.0.2/api/core"}),
        **kwargs,
    )


@pytest.fixture
def api():
    with (
        patch.object(
            storage.base_client, "get_user_api_client", return_value=MagicMock()
        ),
        patch.object(storage.base_client, "list_entities", return_value=[]) as listing,
        patch.object(
            storage.base_client, "get_entity", return_value={"uuid": CLUSTER_UUID}
        ) as get,
        patch.object(storage.base_client, "add_entity", return_value={}) as add,
        patch.object(storage.base_client, "update_entity", return_value={}) as update,
        patch.object(storage, "show_data"),
    ):
        yield SimpleNamespace(list=listing, get=get, add=add, update=update)


def test_first_cluster_creates_mds_without_local_installation(api):
    with patch.object(storage, "run_command") as run:
        result = invoke(["clusters", "add", "--type", "rawstor", "--name", "storage1"])
    assert result.exit_code == 0, result.output
    spec = api.add.call_args.args[2]["driver_spec"]
    assert spec == {"kind": "rawstor", "endpoint": "mds://10.100.0.2:7776/"}
    run.assert_not_called()


def test_second_cluster_prompts_for_port(api):
    api.list.return_value = [
        {"name": "storage1", "driver_spec": {"endpoint": "mds://core:7776/"}}
    ]
    result = invoke(
        ["clusters", "add", "--type", "rawstor", "--name", "storage2"], input="7778\n"
    )
    assert result.exit_code == 0, result.output
    assert api.add.call_args.args[2]["driver_spec"]["endpoint"].endswith(":7778/")


def test_cluster_rejects_duplicate_port(api):
    api.list.return_value = [
        {"name": "storage1", "driver_spec": {"endpoint": "mds://core:7776/"}}
    ]
    result = invoke(
        [
            "clusters",
            "add",
            "--type",
            "rawstor",
            "--name",
            "storage2",
            "--mds-port",
            "7776",
        ]
    )
    assert result.exit_code != 0
    api.add.assert_not_called()


def test_cluster_ipv6_advertised_host(api):
    result = invoke(
        [
            "clusters",
            "add",
            "--type",
            "rawstor",
            "--name",
            "storage1",
            "--mds-host",
            "2001:db8::1",
        ]
    )
    assert result.exit_code == 0, result.output
    assert (
        api.add.call_args.args[2]["driver_spec"]["endpoint"]
        == "mds://[2001:db8::1]:7776/"
    )


def test_nodes_init_installs_ost_and_keeps_advertised_address_separate(api, tmp_path):
    with (
        patch.object(storage, "_require_local_privileges"),
        patch.object(storage, "LOCAL_CONFIG_DIR", tmp_path),
        patch.object(storage.hyper_commands, "is_root", return_value=True),
        patch.object(storage.hyper_commands, "install_rawstor_packages") as packages,
        patch.object(storage, "run_command") as run,
        patch.object(storage, "write_root_owned_file") as write,
    ):
        result = invoke(
            [
                "nodes",
                "init",
                "--type",
                "rawstor",
                "--name",
                "ost1",
                "--uuid",
                NODE_UUID,
                "--endpoint",
                "ost://10.100.0.1:7777",
                "--location",
                "file:///data/ost1",
            ]
        )
    assert result.exit_code == 0, result.output
    packages.assert_called_once_with(["librawstor", "rawstor-ost"], False, version=None)
    unit = write.call_args_list[0].args[0]
    assert "--bind=0.0.0.0:7777 file:///data/ost1" in unit
    assert (
        json.loads(write.call_args_list[1].args[0])["endpoint"]
        == "ost://10.100.0.1:7777"
    )
    assert ["systemctl", "enable", "--now", f"rawstor-ost@{NODE_UUID}.service"] in [
        c.args[0] for c in run.call_args_list
    ]
    api.add.assert_not_called()


def test_nodes_add_reads_stable_local_ost_identity(api):
    with patch.object(
        storage,
        "_read_instance",
        return_value={"uuid": NODE_UUID, "endpoint": "ost://host:7777"},
    ):
        result = invoke(
            [
                "nodes",
                "add",
                "--cluster",
                "storage1",
                "--name",
                "ost1",
                "--failure-domain-path",
                "dc1/row1/rack1/host1",
            ]
        )
    assert result.exit_code == 0, result.output
    data = api.add.call_args.args[2]
    assert data["cluster"] == CLUSTER_UUID
    assert data["uuid"] == NODE_UUID
    assert data["failure_domain_path"] == "dc1/row1/rack1/host1"


def test_remote_node_registration_requires_identity(api):
    result = invoke(
        [
            "nodes",
            "add",
            "--cluster",
            "storage1",
            "--endpoint",
            "ost://host:7777",
            "--failure-domain-path",
            "host1",
        ]
    )
    assert result.exit_code != 0
    api.add.assert_not_called()


def test_pool_add_accepts_replication_and_chunk_policy(api):
    result = invoke(
        [
            "pools",
            "add",
            "--cluster",
            "storage1",
            "--name",
            "replicated",
            "--mirrors",
            "2",
            "--chunk-size",
            "256MiB",
            "--failure-domain",
            "rack",
            "--speed",
            "warm",
            "--no-ephemeral",
        ]
    )
    assert result.exit_code == 0, result.output
    data = api.add.call_args.args[2]
    assert data["mirrors"] == 2
    assert data["chunk_size"] == 256 << 20
    assert data["failure_domain"] == "rack"
    assert data["speed"] == "WARM"
    assert data["ephemeral"] is False


def test_pool_update_does_not_reset_unspecified_policy(api):
    result = invoke(["pools", "update", "persistent", "--mirrors", "3"])
    assert result.exit_code == 0, result.output
    assert api.update.call_args.args[3] == {"mirrors": 3}


@pytest.mark.parametrize("chunk", ["0", "3GiB", "2GiB", "bogus"])
def test_pool_rejects_invalid_chunk_size(api, chunk):
    result = invoke(
        ["pools", "add", "--cluster", "storage1", "--name", "p", "--chunk-size", chunk]
    )
    assert result.exit_code != 0
    api.add.assert_not_called()


@pytest.mark.parametrize("group", ["clusters", "nodes", "pools"])
def test_storage_groups_have_full_crud(group):
    result = invoke([group, "--help"])
    assert result.exit_code == 0
    for command in ("add", "delete", "list", "show", "update"):
        assert command in result.output
