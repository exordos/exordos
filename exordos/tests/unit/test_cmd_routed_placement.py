# Copyright 2026 Genesis Corporation.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0

from unittest import mock

from click.testing import CliRunner
import pytest

from exordos.cmd.compute.hypervisors import commands as hypervisors
from exordos.cmd.compute.sets import commands as sets

IDENTIFIER = "11111111-1111-1111-1111-111111111111"


def invoke(command, args, update=False):
    module = sets if command is sets.add_cmd else hypervisors
    with (
        mock.patch.object(module.base_client, "get_user_api_client"),
        mock.patch.object(
            module.base_client,
            "update_entity" if update else "add_entity",
            return_value={},
        ) as write,
    ):
        result = CliRunner().invoke(command, args, obj=mock.Mock())
        assert result.exit_code == 0, result.output
        return write.call_args.args[-1]


@pytest.mark.parametrize(
    "options,placement",
    [
        ([], None),
        (["--placement-kind", "anti-affinity"], {"kind": "anti-affinity"}),
        (
            ["--placement-scope", "pool"],
            {"kind": "soft-anti-affinity", "scope": "pool"},
        ),
        (
            ["--placement-kind", "anti-affinity", "--placement-scope", "site"],
            {"kind": "anti-affinity", "scope": "site"},
        ),
    ],
)
def test_set_placement_preserves_api_default_scope(options, placement):
    payload = invoke(
        sets.add_cmd,
        ["-p", IDENTIFIER, "-i", "ubuntu", "--network", IDENTIFIER, *options],
    )
    assert payload["default_network"] == {"network": IDENTIFIER}
    assert payload.get("placement") == placement


def test_hypervisor_add_and_update_send_site():
    assert invoke(hypervisors.add_cmd, ["-n", "pool", "--site", "dc1"])["site"] == "dc1"
    assert (
        invoke(hypervisors.update_cmd, [IDENTIFIER, "--site", "dc2"], update=True)[
            "site"
        ]
        == "dc2"
    )


@pytest.mark.parametrize(
    "option,ephemeral", [(None, None), ("--durable", False), ("--ephemeral", True)]
)
def test_set_disk_policy_can_select_durable_cloud_storage(option, ephemeral):
    payload = invoke(
        sets.add_cmd, ["-p", IDENTIFIER, "-i", "ubuntu"] + ([option] if option else [])
    )
    if ephemeral is None:
        assert "ephemeral" not in payload["disk_spec"]
    else:
        assert payload["disk_spec"]["ephemeral"] is ephemeral
