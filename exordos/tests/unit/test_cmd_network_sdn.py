#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

from unittest import mock

from click import testing
import pytest
import rich_click as click

from exordos.cmd.network import common as net_common
from exordos.cmd.network.networks import commands as networks_commands
from exordos.cmd.network.nfs import commands as nfs_commands
from exordos.cmd.network.ports import commands as ports_commands
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


def test_port_add_builds_simple_config():
    add_entity, _ = _run(
        ports_commands.port_add_cmd,
        [
            "-p",
            PROJECT,
            "-s",
            SUBNET,
            "-N",
            NODE,
            "-g",
            "web",
            "--no-dhcp",
        ],
    )
    data = add_entity.call_args[0][2]
    assert data["subnet"] == SUBNET
    assert data["node"] == NODE
    assert data["config"] == {
        "kind": "simple",
        "security_groups": [SG],
        "dhcp": False,
    }
    assert data["port_security"] is True


def test_port_update_keeps_untouched_config_keys():
    """The kind is a polymorphic whole: an update that only sets one knob
    must not drop the groups already on the port."""
    _, update_entity = _run(
        ports_commands.port_update_cmd,
        ["some-port", "--dns"],
        entity={
            "uuid": "55555555-5555-5555-5555-555555555555",
            "config": {"kind": "simple", "security_groups": [SG], "dhcp": False},
        },
    )
    data = update_entity.call_args[0][3]
    assert data["config"] == {
        "kind": "simple",
        "security_groups": [SG],
        "dhcp": False,
        "dns": True,
    }


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
