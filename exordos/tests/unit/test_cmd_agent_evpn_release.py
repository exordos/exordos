#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

from unittest import mock

from exordos.cmd.compute import common as compute_common

# The shape a realm node's primary agent config actually has: the driver
# list is one entry per continuation line, evpn first.
LIVE_CONF = """[DEFAULT]
verbose = True

[universal_agent]
orch_endpoint = http://core.local:11013
caps_drivers =
    EvpnAgentCapabilityDriver,
    BorderCapabilityDriver,
    RenderAgentDriver,
    SSHKeyCapabilityDriver,
    GuestMachineCapabilityDriver,
    ServiceCapabilityDriver

[universal_agent_scheduler]
capabilities =
    em_*,
    evpn_port
"""


def _strip(conf):
    return compute_common.edit_caps_drivers(conf, compute_common.EVPN_DRIVER, add=False)


def _add(conf):
    return compute_common.edit_caps_drivers(conf, compute_common.EVPN_DRIVER, add=True)


def test_strip_evpn_driver_leaves_the_rest_of_the_list():
    out = _strip(LIVE_CONF)
    assert "EvpnAgentCapabilityDriver" not in out
    for kept in (
        "BorderCapabilityDriver",
        "RenderAgentDriver",
        "SSHKeyCapabilityDriver",
        "GuestMachineCapabilityDriver",
        "ServiceCapabilityDriver",
    ):
        assert "    %s" % kept in out
    # the last entry does not keep a dangling comma
    assert "ServiceCapabilityDriver\n" in out
    assert "ServiceCapabilityDriver,\n" not in out
    # ... and NOTHING outside the driver list moved: the [DEFAULT] section,
    # the stand-specific endpoint and every following section survive
    # byte-for-byte (on a core node this file also carries the database
    # credentials, so a rewrite that drops a prefix is not a cosmetic bug).
    before = LIVE_CONF.split("caps_drivers =")
    after = out.split("caps_drivers =")
    assert before[0] == after[0]
    assert before[1].split("\n\n", 1)[1] == after[1].split("\n\n", 1)[1]


def test_strip_evpn_driver_handles_an_inline_list():
    conf = "[universal_agent]\ncaps_drivers = EvpnAgentCapabilityDriver, RenderAgentDriver\nuuid = x\n"
    out = _strip(conf)
    assert "caps_drivers = RenderAgentDriver\n" in out
    assert "uuid = x" in out


def test_strip_evpn_driver_reports_nothing_to_do():
    """Idempotence: a config that never carried the driver is left alone,
    so re-running register-agent does not rewrite or restart anything."""
    assert _strip("caps_drivers = RenderAgentDriver\n") is None
    assert _strip("[universal_agent]\nuuid = x\n") is None


def test_add_driver_keeps_the_list_shape_and_the_rest_of_the_file():
    conf = LIVE_CONF.replace("    EvpnAgentCapabilityDriver,\n", "")
    out = _add(conf)
    assert "    ServiceCapabilityDriver,\n    EvpnAgentCapabilityDriver\n" in out
    assert out.startswith("[DEFAULT]\nverbose = True\n")
    assert out.endswith(conf.split("\n\n")[-1])
    assert _add(out) is None


def test_add_driver_to_an_inline_list_or_a_missing_option():
    conf = "[universal_agent]\ncaps_drivers = LocalPoolAgentDriver\nuuid = x\n"
    assert "caps_drivers = LocalPoolAgentDriver, EvpnAgentCapabilityDriver\n" in _add(
        conf
    )
    out = _add("[universal_agent]\nuuid = x\n")
    assert out == (
        "[universal_agent]\ncaps_drivers = EvpnAgentCapabilityDriver\nuuid = x\n"
    )


def test_the_sdn_agent_takes_the_capability_from_the_primary(tmp_path):
    """Installing the dedicated SDN agent hands the node's overlay state
    over to it: both agents' drivers share one meta file, so the primary
    must stop carrying the driver rather than share it."""
    conf = tmp_path / "exordos_universal_agent.conf"
    conf.write_text(LIVE_CONF)
    with (
        mock.patch.object(compute_common, "PRIMARY_AGENT_CONF_PATH", str(conf)),
        mock.patch("subprocess.run") as run,
    ):
        compute_common.release_evpn_from_primary_agent()

    assert "EvpnAgentCapabilityDriver" not in conf.read_text()
    assert run.call_args_list[0].args[0] == [
        "systemctl",
        "try-restart",
        compute_common.PRIMARY_AGENT_UNIT,
    ]


def test_a_node_without_a_primary_agent_is_fine(tmp_path):
    with mock.patch.object(
        compute_common, "PRIMARY_AGENT_CONF_PATH", str(tmp_path / "absent.conf")
    ):
        compute_common.release_evpn_from_primary_agent()
