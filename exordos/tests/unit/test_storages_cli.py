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
    api.get.side_effect = [
        {"uuid": expected, "capabilities": {"capabilities": ["hypervisor"]}},
        {
            "uuid": expected,
            "capabilities": {"capabilities": ["hypervisor", "storage_node"]},
        },
    ]
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
        patch.object(storage.time, "sleep"),
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
            ["nodes", "init", "--type", "rawstor", "--pool-agent-name", agent_name]
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
    api.update.assert_not_called()
    assert api.get.call_count == 2
    agent_unit.assert_called_once()
    commands = [call.args[0] for call in run.call_args_list]
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


def test_nodes_add_declares_ost_via_api(api):
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
    assert data["bind_address"] == "host:7777"
    assert data["failure_domain_path"] == "dc1/row1/rack1/host1"
    assert data["weight"] == 100


def test_nodes_add_allocates_the_next_port_on_the_same_host(api):
    _agent(api)
    api.list.side_effect = lambda client, collection: (
        [{"uuid": CLUSTER_UUID, "node": NODE_UUID}]
        if collection == storage.c.AGENT_COLLECTION
        else [{"agent": CLUSTER_UUID, "bind_address": "0.0.0.0:7777"}]
    )
    with (
        patch.object(
            storage.hyper_commands,
            "_read_existing_config",
            return_value="[universal_agent]\nuuid=" + NODE_UUID,
        ),
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
    assert data["bind_address"] == "host:7778"


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


def test_nodes_init_passes_version_to_package_and_agent_setup(api):
    with (
        patch.object(storage, "_require_local_privileges"),
        patch.object(storage.hyper_commands, "is_root", return_value=True),
        patch.object(storage.hyper_commands, "install_rawstor_packages") as packages,
        patch.object(
            storage, "_prepare_local_storage_agent", return_value=(NODE_UUID, NODE_UUID)
        ) as prepare,
        patch.object(storage, "run_command") as run,
    ):
        result = invoke(["nodes", "init", "--type", "rawstor", "--version", "1.2.3"])
    assert result.exit_code == 0, result.output
    packages.assert_called_once_with(
        ["librawstor", "rawstor-ost"], False, version="1.2.3"
    )
    assert prepare.call_args.args[1:] == ("universal_agent", "1.2.3")
    command = run.call_args.args[0]
    assert command[:5] == [
        "env",
        "DEBIAN_FRONTEND=noninteractive",
        "apt-get",
        "install",
        "-y",
    ]
    assert "zfsutils-linux" in command
    assert "zfs-dkms" in command
    assert any(arg.startswith("linux-headers-") for arg in command)
    run.assert_called_once()


def test_nodes_add_discovers_local_agent_and_endpoint(api):
    api.list.side_effect = lambda client, collection: (
        [
            {
                "uuid": NODE_UUID,
                "node": NODE_UUID,
                "capabilities": {"capabilities": ["storage_node"]},
            }
        ]
        if collection == storage.c.AGENT_COLLECTION
        else []
    )
    with (
        patch.object(
            storage.hyper_commands, "local_agent_node_uuid", return_value=NODE_UUID
        ),
        patch.object(
            storage, "_detect_local_endpoint", return_value="ost://10.0.0.1:7777"
        ) as detect,
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
                "node",
            ]
        )
    assert result.exit_code == 0, result.output
    detect.assert_called_once_with("http://10.100.0.2/api/core", 7777)
    assert api.add.call_args.args[2]["agent"] == NODE_UUID
    assert api.add.call_args.args[2]["endpoint"] == "ost://10.0.0.1:7777"


def test_nodes_add_selects_agent_by_name_without_local_setup(api):
    _agent(api)
    with (
        patch.object(storage.hyper_commands, "_read_existing_config") as config,
        patch.object(storage, "_prepare_local_storage_agent") as prepare,
        patch.object(storage, "run_command") as run,
    ):
        result = invoke(
            [
                "nodes",
                "add",
                "--cluster",
                "storage1",
                "--agent",
                "registered_storage_agent",
                "--name",
                "ost1",
                "--endpoint",
                "ost://host:7777",
                "--failure-domain-path",
                "node",
            ]
        )
    assert result.exit_code == 0, result.output
    config.assert_not_called()
    prepare.assert_not_called()
    run.assert_not_called()
    assert api.get.call_args_list[0].args[2] == "registered_storage_agent"
    assert api.add.call_args.args[2]["agent"] == NODE_UUID


def test_nodes_add_requires_endpoint_for_remote_agent(api):
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
                "node",
            ]
        )
    assert result.exit_code != 0
    assert "Specify --endpoint" in result.output
    api.add.assert_not_called()


@pytest.mark.parametrize("count", [0, 1, 2])
def test_nodes_add_discovers_storage_agents_on_local_host(api, count):
    _agent(api)
    candidates = [
        {
            "uuid": str(sys_uuid.uuid4()),
            "node": NODE_UUID,
            "name": f"storage-agent-{index}",
            "capabilities": {"capabilities": ["storage_node"]},
        }
        for index in range(count)
    ]
    api.list.return_value = [
        *candidates,
        {"uuid": CLUSTER_UUID, "node": NODE_UUID, "capabilities": {}},
        {
            "uuid": CLUSTER_UUID,
            "node": CLUSTER_UUID,
            "capabilities": {"capabilities": ["storage_node"]},
        },
    ]
    with (
        patch.object(
            storage.hyper_commands, "local_agent_node_uuid", return_value=NODE_UUID
        ),
        patch("questionary.select") as select,
    ):
        select.return_value.ask.return_value = candidates[-1] if count else None
        result = invoke(
            [
                "nodes",
                "add",
                "--cluster",
                "storage1",
                "--name",
                "ost1",
                "--endpoint",
                "ost://10.0.0.1:7777",
                "--failure-domain-path",
                "node",
            ]
        )
    if not count:
        assert result.exit_code != 0
        assert "No storage agent" in result.output
        api.add.assert_not_called()
    else:
        assert result.exit_code == 0, result.output
        assert api.add.call_args.args[2]["agent"] == candidates[-1]["uuid"]
    if count == 2:
        assert [
            choice.value for choice in select.call_args.kwargs["choices"]
        ] == candidates
    else:
        select.assert_not_called()


def test_local_storage_agent_selection_can_be_cancelled(api):
    api.list.return_value = [
        {
            "uuid": str(sys_uuid.uuid4()),
            "node": NODE_UUID,
            "capabilities": {"capabilities": ["storage_node"]},
        }
        for _ in range(2)
    ]
    with (
        patch.object(
            storage.hyper_commands, "local_agent_node_uuid", return_value=NODE_UUID
        ),
        patch("questionary.select") as select,
    ):
        select.return_value.ask.return_value = None
        result = invoke(
            [
                "nodes",
                "add",
                "--cluster",
                "storage1",
                "--name",
                "ost1",
                "--endpoint",
                "ost://10.0.0.1:7777",
                "--failure-domain-path",
                "node",
            ]
        )
    assert result.exit_code != 0
    api.add.assert_not_called()
