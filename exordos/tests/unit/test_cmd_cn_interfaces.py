#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

"""What `cn add` sends when it is told about the node's networking.

Three states, and an empty list is not the absent one: no flag leaves
`interfaces` unset, which is how a node says nothing and is placed on the
installation's default network.
"""

from unittest import mock

from click import testing
import pytest
import rich_click as click

from exordos.cmd.compute.nodes import commands as nodes_commands
from exordos.cmd.network import common as net_common

PROJECT = "11111111-1111-1111-1111-111111111111"
RESOLVED = "22222222-2222-2222-2222-222222222222"

BASE_ARGS = [
    "-p",
    PROJECT,
    "-i",
    "http://img/base.raw",
    "-n",
    "node-1",
]


def _run(args):
    """Invoke `cn add` with the API client mocked out; return the payload."""
    with (
        mock.patch.object(nodes_commands.base_client, "get_user_api_client"),
        mock.patch.object(
            nodes_commands.base_client, "add_entity", return_value={}
        ) as add_entity,
        mock.patch.object(
            nodes_commands.base_client,
            "get_entity",
            return_value={"uuid": RESOLVED},
        ),
    ):
        result = testing.CliRunner().invoke(
            nodes_commands.add_cmd, BASE_ARGS + args, obj=mock.MagicMock()
        )
    if result.exit_code != 0:
        return result
    return add_entity.call_args.args[2]


def test_saying_nothing_sends_nothing():
    """The absent state. Placement is the installation's business."""
    assert "interfaces" not in _run([])


def test_no_network_sends_an_empty_list():
    assert _run(["--no-network"])["interfaces"] == []


def test_the_network_shorthand_is_one_leg():
    assert _run(["--network", "private"])["interfaces"] == [
        {"kind": "subnet", "network": RESOLVED}
    ]


def test_an_interface_carries_its_ports_configuration():
    """The point of the shape: a floating address in the same command.

    Attaching one used to be a second `network ports update` against a port
    the caller first had to find.
    """
    payload = _run(
        ["--interface", "subnet=private,address=10.100.0.7,sg=web,public=fip"]
    )
    assert payload["interfaces"] == [
        {
            "kind": "subnet",
            "subnet": RESOLVED,
            "address": "10.100.0.7",
            "config": {
                "kind": "simple",
                "public": {"address": RESOLVED},
                "security_groups": [RESOLVED],
            },
        }
    ]


def test_several_interfaces_keep_the_order_they_were_given():
    payload = _run(
        ["--interface", "subnet=mgmt", "--interface", "subnet=private,index=0"]
    )
    assert [i.get("index") for i in payload["interfaces"]] == [None, 0]


def test_the_shorthand_and_the_long_form_are_not_combined():
    result = _run(["--network", "private", "--interface", "subnet=private"])
    assert result.exit_code != 0
    assert "one or the other" in result.output


def test_no_network_is_not_combined_with_a_leg():
    result = _run(["--no-network", "--network", "private"])
    assert result.exit_code != 0
    assert "cannot be combined" in result.output


@pytest.mark.parametrize(
    "args", [["--network", "private"], ["--interface", "subnet=a"], ["--no-network"]]
)
def test_add_cmd_on_a_core_without_interfaces_says_so(args):
    from bazooka import exceptions as bazooka_exc

    cause = mock.MagicMock()
    cause.response.status_code = 400
    cause.response.text = (
        "{'interfaces': [{'kind': 'subnet'}]} is not compatible with model Node"
    )
    with (
        mock.patch.object(nodes_commands.base_client, "get_user_api_client"),
        mock.patch.object(
            nodes_commands.base_client,
            "add_entity",
            side_effect=bazooka_exc.BadRequestError(cause),
        ),
        mock.patch.object(
            nodes_commands.base_client, "get_entity", return_value={"uuid": RESOLVED}
        ),
        mock.patch.object(net_common, "resolve", return_value=RESOLVED),
    ):
        result = testing.CliRunner().invoke(
            nodes_commands.add_cmd, BASE_ARGS + args, obj=mock.MagicMock()
        )
    assert result.exit_code != 0
    assert "does not support node interfaces" in result.output


# --- the parser on its own ------------------------------------------------


def _parse(spec):
    client = mock.MagicMock()
    with mock.patch.object(
        net_common, "resolve", side_effect=lambda _c, _coll, ref: RESOLVED
    ):
        return net_common.parse_interface(client, spec)


def test_a_leg_names_exactly_one_of_subnet_or_network():
    with pytest.raises(click.ClickException, match="exactly one"):
        _parse("subnet=a,network=b")
    with pytest.raises(click.ClickException, match="exactly one"):
        _parse("address=10.0.0.1")


@pytest.mark.parametrize(
    "spec",
    ["subnet=a,index=first", "subnet=a,colour=blue", "subnet=a,sg", "subnet="],
)
def test_junk_is_refused_rather_than_ignored(spec):
    with pytest.raises(click.ClickException):
        _parse(spec)


def test_groups_accumulate_within_one_leg():
    """A port carries a set of groups; one is not a special case."""
    parsed = _parse("subnet=a,sg=web,sg=db")
    assert parsed["config"]["security_groups"] == [RESOLVED, RESOLVED]


# --- a leg the node adopts rather than builds -------------------------------


def test_a_port_is_adopted_as_its_own_kind():
    parsed = _parse("port=web-port")

    assert parsed == {"kind": "port", "port": RESOLVED}


def test_an_adopted_port_still_takes_an_index():
    """Where the leg sits in the node is the node's to say; everything else
    about the port is the port's."""
    parsed = _parse("port=web-port,index=1")

    assert parsed == {"kind": "port", "port": RESOLVED, "index": 1}


@pytest.mark.parametrize(
    "spec",
    [
        "port=p,subnet=a",
        "port=p,network=n",
        "port=p,address=10.0.0.1",
        "port=p,sg=web",
        "port=p,public=fip",
    ],
)
def test_what_only_a_built_leg_can_say_is_refused_on_an_adopted_one(spec):
    """Refused rather than dropped: an adopted port keeps its own
    configuration, so a caller who writes these means something that is not
    going to happen."""
    with pytest.raises(click.ClickException, match="keeps its own configuration"):
        _parse(spec)
