#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

import os
import stat
from unittest import mock

from exordos.clients import base_client
from exordos.cmd.compute import common as compute_common


def test_get_agent_private_key_bare_string():
    client = mock.MagicMock()
    client.do_action.return_value = "BASE64KEY=="
    key = base_client.get_agent_private_key(client, "/v1/compute/nodes/", "uuid-1")
    assert key == "BASE64KEY=="
    # get_private_key is a GET action (invoke=False).
    client.do_action.assert_called_once_with(
        "/v1/compute/nodes/", uuid="uuid-1", name="get_private_key", invoke=False
    )


def test_an_answer_that_is_not_a_key_does_not_become_one():
    """What comes back is written to the file the agent reads as its
    identity. An answer of another shape unwrapped into it is an agent that
    fails every registration with nothing anywhere saying why."""
    import pytest
    import rich_click as click

    for answer in ({"private_key": "WRAPPED=="}, "", None, {}):
        client = mock.MagicMock()
        client.do_action.return_value = answer
        with pytest.raises(click.ClickException):
            base_client.get_agent_private_key(client, "/v1/compute/nodes/", "u")


def test_write_agent_key_creates_file_mode_0600(tmp_path):
    path = tmp_path / "sub" / "private_key"
    compute_common.write_agent_key(str(path), "SECRET==")
    assert path.read_text() == "SECRET=="
    mode = stat.S_IMODE(os.stat(path).st_mode)
    assert mode == 0o600


def test_register_agent_pool_sets_hypervisor_node(tmp_path):
    """--pool must point the pool's hypervisor_node at the new agent node
    so the core schedules the pool's guest SDN wiring to this agent."""
    from click import testing

    from exordos.cmd.compute.hypervisors import commands

    key_path = tmp_path / "private_key"
    with (
        mock.patch.object(commands.base_client, "get_user_api_client") as get_client,
        mock.patch.object(commands.base_client, "add_entity") as add_entity,
        mock.patch.object(
            commands.base_client, "get_agent_private_key", return_value="K=="
        ),
        mock.patch.object(
            commands.base_client,
            "get_entity",
            return_value={"driver_spec": {"kind": "libvirt"}},
        ),
        mock.patch.object(commands.base_client, "update_entity") as update_entity,
        # The ROM is a fact of the host, so the assertion below must not
        # depend on whether the machine running the tests happens to have it.
        mock.patch.object(commands.os.path, "exists", return_value=False),
    ):
        obj = mock.MagicMock()
        result = testing.CliRunner().invoke(
            commands.register_agent_cmd,
            [
                "--name",
                "sdn-agent",
                "-p",
                "11111111-1111-1111-1111-111111111111",
                "-u",
                "22222222-2222-2222-2222-222222222222",
                "--key-path",
                str(key_path),
                "--pool",
                "33333333-3333-3333-3333-333333333333",
            ],
            obj=obj,
        )

    assert result.exit_code == 0, result.output
    add_entity.assert_called_once()
    # The pool is also switched to OVS: the agent can only find guests that
    # libvirt plugged into the integration bridge.
    update_entity.assert_called_once_with(
        get_client.return_value,
        commands.ENTITY_COLLECTION,
        "33333333-3333-3333-3333-333333333333",
        {
            "hypervisor_node": "22222222-2222-2222-2222-222222222222",
            "driver_spec": {"kind": "libvirt", "ovs": True},
        },
    )
    assert key_path.read_text() == "K=="


def test_register_agent_cmd_leaves_the_host_agents_key_alone(tmp_path):
    """`hypervisors init` registers the host agent under another node uuid;
    its key is not ours to overwrite, with or without --write-config."""
    from click import testing

    from exordos.cmd.compute.hypervisors import commands

    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "add_entity"),
        mock.patch.object(
            commands.base_client, "get_agent_private_key", return_value="K=="
        ),
        mock.patch.object(commands.compute_common, "write_agent_key") as write_key,
    ):
        result = testing.CliRunner().invoke(
            commands.register_agent_cmd,
            [
                "--name",
                "sdn-agent",
                "-p",
                "11111111-1111-1111-1111-111111111111",
                "-u",
                "22222222-2222-2222-2222-222222222222",
            ],
            obj=mock.MagicMock(),
        )

    assert result.exit_code == 0, result.output
    write_key.assert_called_once_with(compute_common.SDN_AGENT_KEY_PATH, "K==")


def test_register_agent_is_idempotent_when_the_node_already_exists(tmp_path):
    """A re-run after a partial failure must not abort on the node's
    'already exists': it should still fetch the key and wire the pool."""
    from bazooka import exceptions as bazooka_exc
    from click import testing

    from exordos.cmd.compute.hypervisors import commands

    key_path = tmp_path / "private_key"
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(
            commands.base_client,
            "add_entity",
            side_effect=bazooka_exc.ConflictError(mock.MagicMock()),
        ),
        mock.patch.object(
            commands.base_client, "get_agent_private_key", return_value="K=="
        ) as get_key,
        mock.patch.object(
            commands.base_client,
            "get_entity",
            side_effect=lambda _c, collection, _u: (
                {"name": "sdn-agent", "node_type": "HW"}
                if collection == commands.c.NODE_COLLECTION
                else {"driver_spec": {"kind": "libvirt"}}
            ),
        ),
        mock.patch.object(commands.base_client, "update_entity") as update_entity,
    ):
        result = testing.CliRunner().invoke(
            commands.register_agent_cmd,
            [
                "--name",
                "sdn-agent",
                "-p",
                "11111111-1111-1111-1111-111111111111",
                "-u",
                "22222222-2222-2222-2222-222222222222",
                "--key-path",
                str(key_path),
                "--pool",
                "33333333-3333-3333-3333-333333333333",
            ],
            obj=mock.MagicMock(),
        )

    assert result.exit_code == 0, result.output
    get_key.assert_called_once()  # carried on past the conflict
    update_entity.assert_called_once()  # …and wired the pool
    assert key_path.read_text() == "K=="


def test_register_agent_hw_defaults_to_system_uuid_and_auto_pool(tmp_path):
    """Without --uuid an HW registration must use the host system uuid
    (the agent's encryptor identity), and --pool auto must resolve the
    installation's only pool; --write-config wires the SDN agent service."""
    from click import testing

    from exordos.cmd.compute import common as compute_common
    from exordos.cmd.compute.hypervisors import commands

    sys_uuid = "44444444-4444-4444-4444-444444444444"
    pool = {"uuid": "55555555-5555-5555-5555-555555555555"}
    key_path = tmp_path / "key"
    with (
        mock.patch.object(commands.base_client, "get_user_api_client") as gc,
        mock.patch.object(commands.base_client, "add_entity") as add_entity,
        mock.patch.object(
            commands.base_client, "get_agent_private_key", return_value="K=="
        ),
        mock.patch.object(commands.base_client, "list_entities", return_value=[pool]),
        mock.patch.object(commands.base_client, "update_entity") as update_entity,
        mock.patch.object(
            compute_common,
            "read_system_uuid",
        ) as read_uuid,
        mock.patch.object(compute_common, "write_sdn_agent_service") as write_svc,
        # The ROM is a fact of the host; the assertion must not depend on
        # whether the machine running the tests happens to have one.
        mock.patch.object(commands.os.path, "exists", return_value=False),
    ):
        import uuid as uuid_mod

        read_uuid.return_value = uuid_mod.UUID(sys_uuid)
        obj = mock.MagicMock()
        obj.auth_data = {"endpoint": "http://192.168.100.2/api/core"}
        result = testing.CliRunner().invoke(
            commands.register_agent_cmd,
            [
                "--name",
                "sdn-agent",
                "-p",
                "11111111-1111-1111-1111-111111111111",
                "--machine-type",
                "HW",
                "--pool",
                "auto",
                "--key-path",
                str(key_path),
                "--write-config",
            ],
            obj=obj,
        )

    assert result.exit_code == 0, result.output
    assert add_entity.call_args.args[2]["uuid"] == sys_uuid
    update_entity.assert_called_once_with(
        gc.return_value,
        commands.ENTITY_COLLECTION,
        pool["uuid"],
        {"hypervisor_node": sys_uuid, "driver_spec": {"ovs": True}},
    )
    write_svc.assert_called_once_with(
        node_uuid=uuid_mod.UUID(sys_uuid),
        endpoint="http://192.168.100.2/api/core",
        key_path=str(key_path),
    )


def test_register_agent_cmd_leaves_the_pools_rom_alone(tmp_path):
    """The iPXE ROM an overlay guest netboots from is chosen per port by the
    agent; the pool's own ROM stays what its flat guests boot from."""
    from click import testing

    from exordos.cmd.compute.hypervisors import commands

    def _register():
        with (
            mock.patch.object(commands.base_client, "get_user_api_client"),
            mock.patch.object(commands.base_client, "add_entity"),
            mock.patch.object(
                commands.base_client, "get_agent_private_key", return_value="K=="
            ),
            mock.patch.object(
                commands.base_client,
                "get_entity",
                return_value={"driver_spec": {"kind": "libvirt"}},
            ),
            mock.patch.object(commands.base_client, "update_entity") as update_entity,
        ):
            result = testing.CliRunner().invoke(
                commands.register_agent_cmd,
                [
                    "--name",
                    "sdn-agent",
                    "-p",
                    "11111111-1111-1111-1111-111111111111",
                    "-u",
                    "22222222-2222-2222-2222-222222222222",
                    "--key-path",
                    str(tmp_path / "key"),
                    "--pool",
                    "33333333-3333-3333-3333-333333333333",
                ],
                obj=mock.MagicMock(),
            )
        assert result.exit_code == 0, result.output
        return update_entity.call_args[0][3]["driver_spec"]

    assert _register() == {"kind": "libvirt", "ovs": True}


def test_register_agent_refuses_to_take_over_another_nodes_identity(tmp_path):
    """With the system uuid, the node that already exists may be the host's
    own agent; fetching its key would give two agents one identity."""
    from bazooka import exceptions as bazooka_exc
    from click import testing

    from exordos.cmd.compute.hypervisors import commands

    key_path = tmp_path / "private_key"
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(
            commands.base_client,
            "add_entity",
            side_effect=bazooka_exc.ConflictError(mock.MagicMock()),
        ),
        mock.patch.object(
            commands.base_client,
            "get_entity",
            return_value={"name": "hv-01", "node_type": "HW"},
        ),
        mock.patch.object(commands.base_client, "get_agent_private_key") as get_key,
        mock.patch.object(commands.base_client, "update_entity") as update_entity,
    ):
        result = testing.CliRunner().invoke(
            commands.register_agent_cmd,
            [
                "--name",
                "sdn-hv-01",
                "-p",
                "11111111-1111-1111-1111-111111111111",
                "-u",
                "22222222-2222-2222-2222-222222222222",
                "--key-path",
                str(key_path),
                "--pool",
                "33333333-3333-3333-3333-333333333333",
            ],
            obj=mock.MagicMock(),
        )

    assert result.exit_code != 0
    assert "hv-01" in result.output
    get_key.assert_not_called()
    update_entity.assert_not_called()
    assert not key_path.exists()
