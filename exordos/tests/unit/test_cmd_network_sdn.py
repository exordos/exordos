#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

from unittest import mock

from click import testing
import pytest
import rich_click as click

from exordos.cmd.network import common as net_common
from exordos.cmd.network.addresses import commands as addresses_commands
from exordos.cmd.network.networks import commands as networks_commands
from exordos.cmd.network.nfs import commands as nfs_commands
from exordos.cmd.network.ports import commands as ports_commands
from exordos.cmd.network.security_groups import commands as security_commands
from exordos.cmd.network.subnets import commands as subnets_commands

PROJECT = "11111111-1111-1111-1111-111111111111"
SUBNET = "22222222-2222-2222-2222-222222222222"
NODE = "33333333-3333-3333-3333-333333333333"
SG = "44444444-4444-4444-4444-444444444444"


def test_parse_filter_rule_forms():
    assert net_common.parse_filter_rule("egress:any") == {
        "direction": "egress",
        "protocol": "any",
    }
    assert net_common.parse_filter_rule("ingress:tcp:22") == {
        "direction": "ingress",
        "protocol": "tcp",
        "port": 22,
    }
    assert net_common.parse_filter_rule("ingress:udp:53@10.0.0.0/8") == {
        "direction": "ingress",
        "protocol": "udp",
        "port": 53,
        "remote_ip": "10.0.0.0/8",
    }


@pytest.mark.parametrize(
    "spec", ["tcp:22", "sideways:tcp:22", "ingress:sctp:22", "ingress:tcp:ssh"]
)
def test_parse_filter_rule_rejects_junk(spec):
    with pytest.raises(click.ClickException):
        net_common.parse_filter_rule(spec)


def test_format_rule_round_trips():
    spec = "ingress:tcp:443@10.0.0.0/8"
    assert net_common.format_rule(net_common.parse_filter_rule(spec)) == spec


def _run(command, args, entity=None):
    """Invoke a command with the API client mocked out; return the payload."""
    with (
        mock.patch.object(networks_commands.base_client, "get_user_api_client"),
        mock.patch.object(
            networks_commands.base_client, "add_entity", return_value={}
        ) as add_entity,
        mock.patch.object(
            networks_commands.base_client, "update_entity", return_value={}
        ) as update_entity,
        mock.patch.object(
            networks_commands.base_client,
            "get_entity",
            side_effect=lambda _c, _coll, ref: (
                entity if entity is not None else {"uuid": SG}
            ),
        ),
    ):
        result = testing.CliRunner().invoke(command, args, obj=mock.MagicMock())
        assert result.exit_code == 0, result.output
        return add_entity, update_entity


def test_network_add_builds_driver_spec():
    add_entity, _ = _run(
        networks_commands.network_add_cmd,
        ["-n", "private", "-p", PROJECT, "--mtu", "1450"],
    )
    data = add_entity.call_args[0][2]
    assert data["driver_spec"] == {"driver": "ovs_evpn", "mtu": 1450}
    assert data["access"] == "private"


def test_subnet_add_resolves_network_and_parses_routes():
    add_entity, _ = _run(
        subnets_commands.subnet_add_cmd,
        [
            "-n",
            "private",
            "-p",
            PROJECT,
            "-N",
            "private",
            "-c",
            "10.100.0.0/24",
            "-r",
            "0.0.0.0/0=10.100.0.1",
            "-s",
            "10.100.0.1",
        ],
        entity={"uuid": SUBNET},
    )
    data = add_entity.call_args[0][2]
    assert data["network"] == SUBNET  # resolved by name through get_entity
    assert data["routers"] == [{"to": "0.0.0.0/0", "via": "10.100.0.1"}]
    assert data["dns_servers"] == ["10.100.0.1"]
    assert data["dhcp"] is True


def test_port_add_uses_native_fields():
    add_entity, _ = _run(
        ports_commands.port_add_cmd,
        [
            "-p",
            PROJECT,
            "-s",
            SUBNET,
            "-N",
            NODE,
            "--no-dhcp",
            "--mac",
            "02:00:00:00:00:01",
            "--ipv4",
            "10.100.0.4",
        ],
    )
    data = add_entity.call_args[0][2]
    assert data["subnet"] == SUBNET
    assert data["node"] == NODE
    assert "config" not in data
    assert data["dhcp"] is False
    assert data["target_mac"] == "02:00:00:00:00:01"
    assert data["target_ipv4"] == "10.100.0.4"
    assert data["port_security"] is True


def test_port_update_sends_only_native_setting():
    _, update_entity = _run(
        ports_commands.port_update_cmd,
        ["some-port", "--dns"],
        entity={
            "uuid": "55555555-5555-5555-5555-555555555555",
            "security_groups": [SG],
            "dhcp": False,
        },
    )
    data = update_entity.call_args[0][3]
    assert data == {"dns": True}


def test_nf_set_keeps_the_rest_of_the_config():
    """A function is edited, never made, and an edit names one setting: the
    others are what the function already answers with."""
    _, update_entity = _run(
        nfs_commands.nf_set_cmd,
        ["some-nf", "--forwarder", "9.9.9.9"],
        entity={
            "uuid": SG,
            "kind": "dns",
            "config": {"forwarders": ["1.1.1.1"], "zone_suffix": "internal"},
        },
    )
    data = update_entity.call_args[0][3]
    assert data == {"config": {"forwarders": ["9.9.9.9"], "zone_suffix": "internal"}}


def test_nf_set_resolves_a_named_group_like_a_security_group_does():
    """`@<group>` names a security group; the API takes its uuid under the
    key security-group rules use, not the CLI's own unresolved reference."""
    group = "77777777-7777-7777-7777-777777777777"

    def _get(_c, collection, ref):
        if collection == nfs_commands.c.SECURITY_GROUP_COLLECTION:
            assert ref == "db"
            return {"uuid": group}
        return {"uuid": SG, "kind": "splitter", "config": {"rules": []}}

    with (
        mock.patch.object(nfs_commands.base_client, "get_user_api_client"),
        mock.patch.object(nfs_commands.base_client, "get_entity", side_effect=_get),
        mock.patch.object(
            nfs_commands.base_client, "update_entity", return_value={}
        ) as update_entity,
    ):
        result = testing.CliRunner().invoke(
            nfs_commands.nf_set_cmd,
            ["some-nf", "-r", "ingress:tcp:5432@db"],
            obj=mock.MagicMock(),
        )
    assert result.exit_code == 0, result.output
    assert update_entity.call_args[0][3]["config"]["rules"] == [
        {
            "direction": "ingress",
            "protocol": "tcp",
            "port": 5432,
            "remote_group_id": group,
        }
    ]


def test_nf_set_refuses_a_no_op():
    with (
        mock.patch.object(nfs_commands.base_client, "get_user_api_client"),
        mock.patch.object(
            nfs_commands.base_client,
            "get_entity",
            return_value={
                "uuid": SG,
                "kind": "dns",
                "config": {"forwarders": ["1.1.1.1"]},
            },
        ),
    ):
        result = testing.CliRunner().invoke(
            nfs_commands.nf_set_cmd, ["some-nf"], obj=mock.MagicMock()
        )
    assert result.exit_code != 0
    assert "Nothing to change" in result.output


def test_security_group_add_creates_empty_group():
    add_entity, _ = _run(
        security_commands.security_group_add_cmd,
        ["-n", "web", "-p", PROJECT],
    )
    assert "rules" not in add_entity.call_args.args[2]


def test_security_group_rule_add_creates_independent_row():
    add_entity, update_entity = _run(
        security_commands.rule_add_cmd,
        ["web", "ingress:tcp:22"],
        entity={"uuid": SG, "project_id": PROJECT, "rules": []},
    )
    collection, data = add_entity.call_args.args[1:]
    assert collection == security_commands.c.SECURITY_GROUP_RULE_COLLECTION
    assert data == {
        "uuid": data["uuid"],
        "project_id": PROJECT,
        "security_group": SG,
        "direction": "ingress",
        "protocol": "tcp",
        "port": 22,
    }
    update_entity.assert_not_called()


@pytest.mark.parametrize("missing", [False, True])
@pytest.mark.parametrize("by_uuid", [False, True])
def test_security_group_rule_del_deletes_only_exact_row(missing, by_uuid):
    rules = [
        {"uuid": NODE, "direction": "ingress", "protocol": "tcp", "port": 443},
        {
            "uuid": SUBNET,
            "direction": "ingress",
            "protocol": "tcp",
            "port": 22,
            "remote_ip": "10.0.0.0/8",
        },
    ]
    if not missing:
        rules.append(
            {
                "uuid": PROJECT,
                "direction": "ingress",
                "protocol": "tcp",
                "port": 22,
                "remote_ip": None,
                "remote_group_id": None,
            }
        )
    with (
        mock.patch.object(security_commands.base_client, "get_user_api_client"),
        mock.patch.object(
            security_commands.base_client, "get_entity", return_value={"uuid": SG}
        ),
        mock.patch.object(
            security_commands.base_client,
            "list_entities",
            return_value=([] if missing else [rules[-1]]) if by_uuid else rules,
        ) as list_entities,
        mock.patch.object(security_commands.base_client, "delete_entity") as delete,
        mock.patch.object(security_commands.base_client, "update_entity") as update,
    ):
        result = testing.CliRunner().invoke(
            security_commands.rule_del_cmd,
            ["web", PROJECT if by_uuid else "ingress:tcp:22"],
            obj=mock.MagicMock(),
        )
    assert result.exit_code == (1 if missing else 0), result.output
    assert list_entities.call_args.kwargs == {
        "security_group": SG,
        **({"uuid": PROJECT} if by_uuid else {}),
    }
    update.assert_not_called()
    if missing:
        assert "No such rule" in result.output
        delete.assert_not_called()
    else:
        assert delete.call_args.args[1:] == (
            security_commands.c.SECURITY_GROUP_RULE_COLLECTION,
            PROJECT,
        )


@pytest.mark.parametrize(
    "group,collection,field",
    [
        (
            security_commands.security_groups_group,
            security_commands.c.PORT_SECURITY_GROUP_COLLECTION,
            "security_group",
        ),
    ],
)
def test_group_bind_and_unbind_use_independent_owned_pair(group, collection, field):
    entity = {"uuid": NODE, "project_id": PROJECT}
    add, _ = _run(group.commands["bind"], [SG, NODE], entity=entity)
    assert add.call_args.args[1] == collection
    data = add.call_args.args[2]
    assert data == {
        "uuid": data["uuid"],
        "project_id": PROJECT,
        "port": NODE,
        field: SG,
    }
    with (
        mock.patch.object(security_commands.base_client, "get_user_api_client"),
        mock.patch.object(
            security_commands.base_client, "get_entity", return_value=entity
        ),
        mock.patch.object(
            security_commands.base_client,
            "list_entities",
            return_value=[{"uuid": SUBNET}],
        ) as list_entities,
        mock.patch.object(security_commands.base_client, "delete_entity") as delete,
    ):
        result = testing.CliRunner().invoke(
            group.commands["unbind"], [SG, NODE], obj=mock.MagicMock()
        )
    assert result.exit_code == 0, result.output
    assert list_entities.call_args.args[1] == collection
    assert list_entities.call_args.kwargs == {
        "project_id": PROJECT,
        "port": NODE,
        field: SG,
    }
    assert delete.call_args.args[1:] == (collection, SUBNET)


def test_group_unbind_refuses_missing_pair():
    with (
        mock.patch.object(security_commands.base_client, "get_user_api_client"),
        mock.patch.object(
            security_commands.base_client,
            "get_entity",
            return_value={"uuid": NODE, "project_id": PROJECT},
        ),
        mock.patch.object(
            security_commands.base_client, "list_entities", return_value=[]
        ),
        mock.patch.object(security_commands.base_client, "delete_entity") as delete,
    ):
        result = testing.CliRunner().invoke(
            security_commands.security_groups_group.commands["unbind"],
            [SG, NODE],
            obj=mock.MagicMock(),
        )
    assert result.exit_code == 1
    assert "not bound" in result.output
    delete.assert_not_called()


@pytest.mark.parametrize("floating", [False, True])
def test_address_add_defaults_to_reservation_and_accepts_floating_port(floating):
    add, _ = _run(
        addresses_commands.address_add_cmd,
        ["-p", PROJECT, "-s", SUBNET]
        + (["--kind", "floating", "--port", NODE] if floating else []),
    )
    data = add.call_args.args[2]
    assert data["kind"] == ("floating" if floating else "reservation")
    if floating:
        assert data["port"] == NODE
    else:
        assert "port" not in data
    assert "address" not in data


def test_address_update_disassociates_with_null_port():
    _, update = _run(addresses_commands.address_update_cmd, [SG, "--no-port"])
    assert update.call_args.args[3] == {"port": None}


def test_network_list_reads_allocated_driver_state():
    row = {
        "driver_spec": {"driver": "ovs_evpn", "mtu": 1450},
        "driver_state": {"vni": 42, "rt": "64512:42", "mtu": 1400},
    }
    assert networks_commands.FIELDS_MAP["Driver"](row) == "ovs_evpn"
    assert networks_commands.FIELDS_MAP["VNI"](row) == "42"
    assert networks_commands.FIELDS_MAP["RT"](row) == "64512:42"
    assert networks_commands.FIELDS_MAP["MTU"](row) == "1400"
