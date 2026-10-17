#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

"""Primary port requests sent through default_network."""

from unittest import mock

from click import testing
import pytest

from exordos.cmd.compute.nodes import commands as nodes_commands

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


def test_saying_nothing_sends_no_network_request():
    payload = _run([])
    assert "default_network" not in payload
    assert "interfaces" not in payload


def test_no_network_sends_an_empty_default_request():
    assert _run(["--no-network"])["default_network"] == {}


def test_network_selects_the_primary_network():
    assert _run(["--network", "private"])["default_network"] == {"network": RESOLVED}


def test_fip_can_be_requested_without_selecting_a_network():
    assert _run(["--auto-floating-ip"])["default_network"] == {"auto_floating_ip": True}


def test_floating_network_is_an_explicit_primary_fip_selector():
    payload = _run(
        ["--network", "private", "--auto-floating-ip", "--floating-network", "public"]
    )
    assert payload["default_network"] == {
        "network": RESOLVED,
        "auto_floating_ip": True,
        "floating_network": RESOLVED,
    }


@pytest.mark.parametrize(
    "args",
    [
        ["--interface", "subnet=private"],
        ["--no-network", "--network", "private"],
        ["--no-network", "--auto-floating-ip"],
        ["--floating-network", "public"],
    ],
)
def test_invalid_or_removed_network_options_are_rejected(args):
    result = _run(args)
    assert result.exit_code != 0


@pytest.mark.parametrize("args", [["--interface", "subnet=private"], ["--no-network"]])
def test_update_has_no_network_declaration_options(args):
    result = testing.CliRunner().invoke(
        nodes_commands.update_cmd, [RESOLVED, *args], obj=mock.MagicMock()
    )
    assert result.exit_code != 0
    assert "No such option" in result.output
