#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

"""`hypervisors init --sdn`: one command makes a host an SDN hypervisor."""

import configparser
import contextlib
from unittest import mock
import uuid as sys_uuid

from click.testing import CliRunner

from exordos.cmd.compute import common as compute_common
from exordos.cmd.compute.hypervisors import commands as hv
from exordos.tests.unit.test_hypervisors_cli import _FAKE_AGENT_TARGET
from exordos.tests.unit.test_hypervisors_cli import _obj
from exordos.tests.unit.test_hypervisors_cli import _patch_common_init_deps

NODE = "44444444-4444-4444-4444-444444444444"
PROJECT = "11111111-1111-1111-1111-111111111111"
REMOTE_POOL = {
    "uuid": "55555555-5555-5555-5555-555555555555",
    "driver_spec": {
        "kind": "libvirt",
        "connection_uri": "qemu+tcp://10.20.0.1/system",
    },
}
LOCAL_POOL = {
    "uuid": "66666666-6666-6666-6666-666666666666",
    "driver_spec": {"kind": "exordos_local_hyper", "node": NODE},
}
AGENT_CONF = """[universal_agent]
orch_endpoint = http://10.20.0.2:11011
caps_drivers = LocalPoolAgentDriver

[LocalPoolAgentDriver]
meta_file = /var/lib/exordos/universal_agent/pool_meta.json
"""
SDN_ARGS = ["--sdn", "--sdn-connector", "/src/evpn_connector"]


def _init(args, pools, existing_config=AGENT_CONF, root=True, extra=()):
    """Run `init` with every host and API step mocked; return the mocks."""
    mocks = {}
    with contextlib.ExitStack() as stack:
        stack.enter_context(_patch_common_init_deps())

        def patch(name, target=hv, **kwargs):
            mocks[name] = stack.enter_context(mock.patch.object(target, name, **kwargs))

        patch("is_root", return_value=root)
        patch("_install_packages")
        patch("_install_sdn_fabric")
        patch("_install_sdn_agent")
        patch("_pip_install_sdk")
        patch("register_agent_cmd")
        patch("_serve_pool_overlay")
        patch("local_agent_node_uuid", return_value=NODE)
        patch("resolve_agent_install_target", return_value=_FAKE_AGENT_TARGET)
        patch("_read_existing_config", return_value=existing_config)
        patch("write_root_owned_file")
        patch("run_command", return_value=mock.Mock(returncode=0))
        patch("get_user_api_client", target=hv.base_client)
        patch("list_entities", target=hv.base_client, return_value=pools)
        patch(
            "get_entity",
            target=hv.base_client,
            side_effect=lambda _c, _coll, ref: next(
                p for p in pools if p["uuid"] == ref
            ),
        )
        for name, kwargs in extra:
            patch(name, **kwargs)
        result = CliRunner().invoke(
            hv.init_cmd,
            args,
            obj=_obj(auth_data={"endpoint": "http://10.20.0.2/api/core"}),
        )
    return result, mocks


def _restarts(run):
    return [c for c in run.call_args_list if "restart" in c.args[0]]


def test_init_cmd_without_sdn_takes_no_sdn_step():
    result, m = _init([], pools=[REMOTE_POOL])

    assert result.exit_code == 0, result.output
    for name in (
        "_install_sdn_fabric",
        "_install_sdn_agent",
        "_pip_install_sdk",
        "register_agent_cmd",
        "_serve_pool_overlay",
        "list_entities",
    ):
        m[name].assert_not_called()


def test_init_cmd_sdn_refuses_without_root_before_installing_anything():
    result, m = _init(SDN_ARGS, pools=[REMOTE_POOL], root=False)

    assert result.exit_code != 0
    assert "root" in result.output
    m["_install_packages"].assert_not_called()


def test_init_cmd_sdn_needs_a_connector():
    result, m = _init(["--sdn"], pools=[REMOTE_POOL])

    assert result.exit_code != 0
    assert "--sdn-connector" in result.output
    m["_install_packages"].assert_not_called()


def test_init_cmd_sdn_on_a_remote_pool_registers_a_dedicated_agent():
    result, m = _init(SDN_ARGS + ["--sdn-project-id", PROJECT], pools=[REMOTE_POOL])

    assert result.exit_code == 0, result.output
    m["_install_sdn_fabric"].assert_called_once_with(
        "/src/evpn_connector", compute_common.GOBGP_DEFAULT_URL
    )
    m["_install_sdn_agent"].assert_called_once_with("gcl-sdk")
    kwargs = m["register_agent_cmd"].call_args.kwargs
    assert kwargs["pool_ref"] == REMOTE_POOL["uuid"]
    assert kwargs["project_id"] == sys_uuid.UUID(PROJECT)
    assert kwargs["machine_type"] == "HW"
    assert kwargs["write_config"] is True
    m["write_root_owned_file"].assert_not_called()


def test_init_cmd_sdn_on_a_remote_pool_needs_a_project_before_installing():
    result, m = _init(SDN_ARGS, pools=[REMOTE_POOL])

    assert result.exit_code != 0
    assert "--sdn-project-id" in result.output
    m["_install_sdn_fabric"].assert_not_called()


def test_init_cmd_sdn_on_this_hosts_pool_extends_its_agent():
    """A second agent under the host's system uuid would take the pool
    agent's record over, so the pool agent gains the overlay driver."""
    result, m = _init(
        SDN_ARGS + ["--sdn-pool", LOCAL_POOL["uuid"]],
        pools=[LOCAL_POOL, REMOTE_POOL],
    )

    assert result.exit_code == 0, result.output
    m["register_agent_cmd"].assert_not_called()
    m["_install_sdn_agent"].assert_not_called()
    m["_pip_install_sdk"].assert_called_once_with(
        _FAKE_AGENT_TARGET.venv_path, "gcl-sdk"
    )
    content, path = m["write_root_owned_file"].call_args.args[:2]
    assert path == _FAKE_AGENT_TARGET.config_path
    parser = configparser.ConfigParser()
    parser.read_string(content)
    drivers = parser.get("universal_agent", "caps_drivers")
    assert drivers == "LocalPoolAgentDriver, EvpnAgentCapabilityDriver"
    assert parser.get("LocalPoolAgentDriver", "meta_file").endswith("pool_meta.json")
    assert len(_restarts(m["run_command"])) == 1
    assert m["_serve_pool_overlay"].call_args.args[1:3] == (LOCAL_POOL["uuid"], NODE)


def test_init_cmd_sdn_rerun_leaves_a_configured_agent_running():
    configured = AGENT_CONF.replace(
        "caps_drivers = LocalPoolAgentDriver",
        "caps_drivers = LocalPoolAgentDriver, EvpnAgentCapabilityDriver",
    )
    result, m = _init(
        SDN_ARGS + ["--sdn-pool", LOCAL_POOL["uuid"]],
        pools=[LOCAL_POOL],
        existing_config=configured,
    )

    assert result.exit_code == 0, result.output
    m["write_root_owned_file"].assert_not_called()
    assert _restarts(m["run_command"]) == []
    m["_serve_pool_overlay"].assert_called_once()


def test_init_cmd_sdn_on_this_hosts_pool_without_its_agent_refuses():
    result, m = _init(
        SDN_ARGS + ["--sdn-pool", LOCAL_POOL["uuid"]],
        pools=[LOCAL_POOL],
        existing_config=None,
    )

    assert result.exit_code != 0
    assert "init --add" in result.output
    m["_install_sdn_fabric"].assert_not_called()


def test_init_cmd_add_sdn_serves_the_pool_it_registered():
    extra = (
        ("install_agent_venv", {}),
        ("add_cmd", {}),
        ("_detect_local_cores", {"return_value": 8}),
        ("_detect_local_ram_mb", {"return_value": 16384}),
        (
            "_default_hypervisor_uuid",
            {"return_value": sys_uuid.UUID(LOCAL_POOL["uuid"])},
        ),
        ("reset_agent_meta_file", {}),
        ("write_agent_config", {}),
        ("install_agent_systemd_unit", {}),
    )
    with mock.patch.object(hv.base_client, "register_agent_and_write_key"):
        result, m = _init(
            ["--add"] + SDN_ARGS, pools=[REMOTE_POOL, LOCAL_POOL], extra=extra
        )

    assert result.exit_code == 0, result.output
    m["list_entities"].assert_not_called()
    m["register_agent_cmd"].assert_not_called()
    assert m["_serve_pool_overlay"].call_args.args[1] == LOCAL_POOL["uuid"]


def test_init_cmd_sdn_refuses_an_sdk_without_the_overlay_driver():
    """pip keeps an installed gcl-sdk that has no evpn driver, and an agent
    told to load it fails on start -- taking the host's pool with it."""
    result, m = _init(
        SDN_ARGS + ["--sdn-pool", LOCAL_POOL["uuid"]],
        pools=[LOCAL_POOL],
        extra=[("run_command", {"return_value": mock.Mock(returncode=1)})],
    )

    assert result.exit_code != 0
    assert "no overlay driver" in result.output
    m["write_root_owned_file"].assert_not_called()
    assert not _restarts(m["run_command"])
    m["_serve_pool_overlay"].assert_not_called()
