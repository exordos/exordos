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
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch
import uuid as sys_uuid

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
            "--port",
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
            "--host",
            "2001:db8::1",
        ]
    )
    assert result.exit_code == 0, result.output
    assert (
        api.add.call_args.args[2]["driver_spec"]["endpoint"]
        == "mds://[2001:db8::1]:7776/"
    )


@pytest.mark.parametrize(
    "agent_name,existing,expected",
    [
        ("universal_agent", None, NODE_UUID),
        (
            "storage_agent",
            None,
            str(sys_uuid.uuid5(sys_uuid.UUID(NODE_UUID), "storage_agent")),
        ),
        ("storage_agent", "[universal_agent]\nuuid=" + CLUSTER_UUID, CLUSTER_UUID),
        (
            "storage_agent",
            "[universal_agent]\ncaps_drivers=LocalPoolAgentDriver",
            NODE_UUID,
        ),
    ],
)
def test_nodes_init_prepares_agent_without_starting_an_ost(
    api, monkeypatch, agent_name, existing, expected
):
    monkeypatch.setenv("LOCAL_GENESIS_SDK_PATH", "/source/gcl_sdk")
    target = SimpleNamespace(
        venv_path="/venv",
        exec_path="/venv/bin/agent",
        config_path="/agent.conf",
        meta_file="/work/pool_meta.json",
        default_private_key_path="/work/key",
        unit_path="/etc/systemd/system/agent.service",
        unit_name="agent.service",
    )
    with (
        patch.object(storage, "_require_local_privileges"),
        patch.object(storage.hyper_commands, "is_root", return_value=True),
        patch.object(
            storage.hyper_commands, "local_agent_node_uuid", return_value=NODE_UUID
        ),
        patch.object(
            storage.hyper_commands, "resolve_agent_install_target", return_value=target
        ),
        patch.object(
            storage.hyper_commands, "_read_existing_config", return_value=existing
        ),
        patch.object(storage.hyper_commands, "install_rawstor_packages") as packages,
        patch.object(storage.hyper_commands, "install_agent_venv") as venv,
        patch.object(
            storage.hyper_commands, "write_agent_config", return_value="/work/key"
        ) as config,
        patch.object(
            storage.hyper_commands, "install_agent_systemd_unit"
        ) as agent_unit,
        patch.object(storage.base_client, "register_agent_and_write_key") as register,
        patch.object(storage, "run_command") as run,
    ):
        result = invoke(
            ["nodes", "init", "--type", "rawstor", "--agent-name", agent_name]
        )
    assert result.exit_code == 0, result.output
    packages.assert_called_once_with(["librawstor", "rawstor-ost"], False, version=None)
    assert venv.call_args.kwargs["packages"] == [
        "/source/gcl_sdk",
        storage.hyper_commands.RAWSTOR_WHEEL_URL,
    ]
    assert config.call_args.kwargs["driver_name"] == "StorageNodeAgentDriver"
    assert config.call_args.kwargs["meta_file"] == "/work/storage_node_meta.json"
    assert register.call_args.kwargs["agent_uuid"] == expected
    assert config.call_args.kwargs["agent_uuid"] == expected
    assert register.call_args.kwargs["capabilities"] == ["storage_node"]
    agent_unit.assert_called_once()
    commands = [call.args[0] for call in run.call_args_list]
    assert any(
        command[:3] == ["apt-get", "install", "-y"]
        and "zfsutils-linux" in command
        and "zfs-dkms" in command
        and any(arg.startswith("linux-headers-") for arg in command)
        for command in commands
    )
    assert ["modprobe", "zfs"] in commands
    assert all(
        not any("rawstor-ost@" in arg for arg in call.args[0])
        for call in run.call_args_list
    )
    api.add.assert_not_called()


def _agent(api):
    api.get.side_effect = lambda client, collection, identifier: (
        {
            "uuid": NODE_UUID,
            "node": NODE_UUID,
            "capabilities": {"capabilities": ["storage_node"]},
        }
        if collection == storage.c.AGENT_COLLECTION
        else {"uuid": CLUSTER_UUID}
    )


def test_nodes_add_declares_remote_ost_without_local_files(api):
    _agent(api)
    result = invoke(
        [
            "nodes",
            "add",
            "--cluster",
            "storage1",
            "--agent",
            NODE_UUID,
            "--name",
            "ost1",
            "--endpoint",
            "ost://host:7777",
            "--location",
            "file:///data/ost1",
            "--failure-domain-path",
            "dc1/row1/rack1/host1",
        ]
    )
    assert result.exit_code == 0, result.output
    data = api.add.call_args.args[2]
    assert data["cluster"] == CLUSTER_UUID
    assert data["agent"] == NODE_UUID
    assert "uuid" not in data  # Core generates the resource identity.
    assert data["location"] == "file:///data/ost1"
    assert data["bind_address"] == "0.0.0.0:7777"
    assert data["failure_domain_path"] == "dc1/row1/rack1/host1"


def test_remote_node_without_endpoint_is_rejected(api):
    _agent(api)
    with patch.object(
        storage.hyper_commands, "local_agent_node_uuid", return_value=CLUSTER_UUID
    ):
        result = invoke(
            [
                "nodes",
                "add",
                "--cluster",
                "storage1",
                "--agent",
                NODE_UUID,
                "--name",
                "ost1",
                "--failure-domain-path",
                "host1",
            ]
        )
    assert result.exit_code != 0
    assert "Specify --endpoint" in result.output
    api.add.assert_not_called()


def test_nodes_add_allocates_the_next_port_on_the_same_host(api):
    _agent(api)
    api.list.side_effect = lambda client, collection: (
        [{"uuid": CLUSTER_UUID, "node": NODE_UUID}]
        if collection == storage.c.AGENT_COLLECTION
        else [{"agent": CLUSTER_UUID, "bind_address": "0.0.0.0:7777"}]
    )
    with (
        patch.object(
            storage.hyper_commands, "local_agent_node_uuid", return_value=NODE_UUID
        ),
        patch.object(
            storage,
            "_detect_local_endpoint",
            side_effect=lambda core, port: f"ost://host:{port}",
        ),
    ):
        result = invoke(
            [
                "nodes",
                "add",
                "--cluster",
                "storage1",
                "--agent",
                NODE_UUID,
                "--name",
                "ost2",
                "--failure-domain-path",
                "host1",
            ]
        )
    assert result.exit_code == 0, result.output
    data = api.add.call_args.args[2]
    assert data["endpoint"] == "ost://host:7778"
    assert data["bind_address"] == "0.0.0.0:7778"


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
