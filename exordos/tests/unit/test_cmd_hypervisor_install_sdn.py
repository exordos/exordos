#    Copyright 2026 Genesis Corporation.
#    Licensed under the Apache License, Version 2.0 (the "License")

"""What `hypervisors init --sdn` puts on a hypervisor host."""

import os
from unittest import mock

import pytest
import rich_click as click

from exordos.cmd.compute import common as compute_common
from exordos.cmd.compute.hypervisors import commands


def _calls(mock_run):
    return [" ".join(str(a) for a in c.args[0]) for c in mock_run.call_args_list]


def _curl_writes(payload):
    """A run_command side effect: the curl step writes ``payload`` to its
    ``-o`` path so the checksum and tar have a real archive to work on."""

    def fake_run(cmd, **kwargs):
        if "curl" in cmd:
            with open(cmd[cmd.index("-o") + 1], "wb") as fh:
                fh.write(payload)

    return fake_run


def test_gobgp_is_fetched_and_installed(tmp_path, monkeypatch):
    import hashlib

    payload = b"gobgp-release-tarball"
    monkeypatch.setattr(
        compute_common, "GOBGP_SHA256", hashlib.sha256(payload).hexdigest()
    )
    with (
        mock.patch.object(
            commands, "run_command", side_effect=_curl_writes(payload)
        ) as run,
        mock.patch.object(commands.os.path, "exists", return_value=False),
    ):
        commands._install_gobgp("http://repo/gobgp.tar.gz")
    joined = _calls(run)
    assert any("curl" in c and "http://repo/gobgp.tar.gz" in c for c in joined)
    assert any(c.startswith("tar -xf") for c in joined)
    assert any("install -m 0755" in c and "/usr/local/bin/" in c for c in joined)


def test_gobgp_with_a_bad_checksum_is_refused():
    # A tampered download must never be installed as root.
    with (
        mock.patch.object(
            commands, "run_command", side_effect=_curl_writes(b"tampered")
        ) as run,
        mock.patch.object(commands.os.path, "exists", return_value=False),
        pytest.raises(click.ClickException),
    ):
        commands._install_gobgp("http://repo/gobgp.tar.gz")
    # It refused before extracting/installing.
    assert not any(c.startswith("tar -xf") for c in _calls(run))


def test_gobgp_already_there_is_left_alone():
    with (
        mock.patch.object(commands, "run_command") as run,
        mock.patch.object(commands.os.path, "exists", return_value=True),
    ):
        commands._install_gobgp("http://repo/gobgp.tar.gz")
    assert run.call_count == 0


def test_connector_uses_the_host_python(tmp_path):
    """The connector's gobgp v3 stubs are generated for a current protobuf
    runtime, so it is built with the host's own python instead of an
    interpreter fetched to satisfy cp38-only wheels."""
    with (
        mock.patch.object(commands, "run_command") as run,
        mock.patch.object(commands.os, "makedirs"),
        mock.patch.object(commands.os.path, "exists", return_value=False),
    ):
        commands._install_connector("/src/evpn_connector")
    joined = _calls(run)
    assert any(f"python3 -m venv {compute_common.EVPN_VENV}" in c for c in joined)
    assert any("pip install" in c and "/src/evpn_connector" in c for c in joined)
    assert not any("uv" in c for c in joined)


def test_agent_venv_and_symlink(tmp_path):
    link = tmp_path / "exordos-universal-agent"
    with (
        mock.patch.object(commands, "run_command") as run,
        mock.patch.object(compute_common, "AGENT_BIN", str(link)),
        mock.patch.object(commands.os.path, "exists", return_value=False),
        mock.patch.object(commands.os.path, "islink", return_value=False),
    ):
        run.return_value.returncode = 0
        commands._install_sdn_agent("gcl-sdk")
    joined = _calls(run)
    assert any("python3 -m venv" in c for c in joined)
    assert any("import gcl_sdk.agents.universal.drivers.evpn" in c for c in joined)
    assert any(c.endswith("install -q gcl-sdk") for c in joined)
    # The unit calls the bare name, so it has to be on PATH.
    assert os.readlink(link).endswith("/bin/exordos-universal-agent")


def test_units_are_written_but_not_enabled(tmp_path):
    gobgpd, connector = tmp_path / "gobgpd.service", tmp_path / "evpn.service"
    with (
        mock.patch.object(commands, "run_command") as run,
        mock.patch.object(compute_common, "GOBGPD_UNIT_PATH", str(gobgpd)),
        mock.patch.object(compute_common, "CONNECTOR_UNIT_PATH", str(connector)),
    ):
        commands._write_fabric_units()
    assert "gobgpd -f /etc/gobgp.conf" in gobgpd.read_text()
    assert "evpn-connector --config-file" in connector.read_text()
    joined = _calls(run)
    assert joined == ["systemctl daemon-reload"]
