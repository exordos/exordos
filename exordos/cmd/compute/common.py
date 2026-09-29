#    Copyright 2025-2026 Genesis Corporation.
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

import os
import re


def write_agent_key(path: str, key: str) -> None:
    """Write a node's agent encryption key to ``path`` with mode 0600.

    Created with the mode rather than chmod-ed into it: between the two there
    is a private key on disk readable by whoever is on the machine, and the
    umask decides how wide that window is.
    """
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(key)
    # An existing file keeps its mode through O_CREAT, so say it anyway.
    os.chmod(path, 0o600)


def extract_disks_from_entity(entity: dict) -> str:
    """Extract disks information from entity."""
    if "disk_spec" not in entity:
        return "Unknown"

    if entity["disk_spec"]["kind"] == "root_disk":
        return f"{entity['disk_spec']['size']}"

    if entity["disk_spec"]["kind"] == "disks":
        disks = [str(d["size"]) for d in entity["disk_spec"]["disks"]]
        return ",".join(disks)

    return "Unknown"


def extract_image_from_entity(entity: dict) -> str:
    """Extract image information from entity."""
    if "disk_spec" not in entity:
        return "Unknown"

    if entity["disk_spec"]["kind"] == "root_disk":
        return entity["disk_spec"]["image"]

    if entity["disk_spec"]["kind"] == "disks":
        return entity["disk_spec"]["disks"][0]["image"]

    return "Unknown"


# Second universal agent on a hypervisor host: the SDN (evpn) agent that
# wires guests into the overlay. Kept apart from the primary agent's state.
SDN_AGENT_KEY_PATH = "/var/lib/exordos/universal_agent_sdn/private_key"
SDN_AGENT_CONF_PATH = "/etc/exordos_universal_agent/sdn_agent.conf"
SDN_AGENT_UNIT = "exordos-universal-agent-sdn"
SDN_AGENT_UNIT_PATH = f"/etc/systemd/system/{SDN_AGENT_UNIT}.service"
SYSTEM_UUID_PATH = "/sys/class/dmi/id/product_uuid"

# The node's own agent, registered with the installation the host belongs
# to — a different one from the core this SDN agent joins.
PRIMARY_AGENT_CONF_PATH = "/etc/exordos_universal_agent/exordos_universal_agent.conf"
PRIMARY_AGENT_UNIT = "exordos-universal-agent"
EVPN_DRIVER = "EvpnAgentCapabilityDriver"

SDN_AGENT_CONF_TEMPLATE = """[DEFAULT]

[universal_agent]
orch_endpoint = http://{host}:11011
status_endpoint = http://{host}:11012
caps_drivers = EvpnAgentCapabilityDriver
uuid = {node_uuid}
payload_path = /var/lib/exordos/universal_agent_sdn/payload.json
private_key_path = {key_path}
"""

SDN_AGENT_UNIT_TEMPLATE = """[Unit]
Description=Exordos Universal Agent (SDN)
After=network-online.target

[Service]
Restart=on-failure
RestartSec=5s
TimeoutStopSec=5
ExecStart=exordos-universal-agent --config-file {conf_path}

[Install]
WantedBy=multi-user.target
"""


def read_system_uuid():
    """The machine's firmware uuid — the identity the universal agent's
    encryptor uses, so a host agent's node uuid must equal it."""
    import uuid as sys_uuid

    import click

    try:
        with open(SYSTEM_UUID_PATH) as f:
            return sys_uuid.UUID(f.read().strip())
    except (OSError, ValueError) as e:
        raise click.ClickException(
            f"Cannot read the system uuid from {SYSTEM_UUID_PATH} ({e}); "
            "pass --uuid explicitly"
        )


def edit_caps_drivers(content: str, driver: str, *, add: bool) -> str | None:
    """Add a driver to, or drop it from, an agent config's ``caps_drivers``.

    Returns the new content, or None when there is nothing to do, so a
    caller can tell whether the agent needs a restart. Only the option's
    own lines are rewritten, in the shape they are written in: one driver
    per indented continuation line (the core's config template) or a
    single inline list. Everything else in the file (comments, other
    sections, credentials) stays byte-for-byte.
    """
    lines = content.splitlines(keepends=True)
    for start, line in enumerate(lines):
        if re.match(r"\s*caps_drivers\s*=", line):
            break
    else:
        if not add:
            return None
        for start, line in enumerate(lines):
            if line.strip() == "[universal_agent]":
                break
        else:
            raise ValueError("no [universal_agent] section to add a driver to")
        start += 1
        lines.insert(start, "caps_drivers =\n")
    end = start + 1
    while end < len(lines) and re.match(r"\s+\S", lines[end]):
        end += 1
    block = "".join(lines[start:end])
    drivers = [d.strip() for d in block.split("=", 1)[1].split(",") if d.strip()]
    if (driver in drivers) == add:
        return None
    if add:
        drivers.append(driver)
    else:
        drivers.remove(driver)
    if "\n" in block.strip():
        rendered = "caps_drivers =\n" + "".join("    %s,\n" % d for d in drivers)
        rendered = rendered.rstrip(",\n") + "\n"
    else:
        rendered = "caps_drivers = %s\n" % ", ".join(drivers)
    return "".join(lines[:start]) + rendered + "".join(lines[end:])


def release_evpn_from_primary_agent() -> None:
    """Take the evpn driver away from the node's own agent.

    A host that wires its guests into *another* installation's overlay runs
    two agents, and the drivers of both keep their state in one file (the
    meta path is a module constant, not a per-agent setting). Each process
    persists its own copy every iteration, so an agent that carries the
    driver while its own core never gives it an evpn resource quietly
    erases what the SDN agent just wrote — and would delete the other
    installation's ports outright if it ever were given one.

    So the primary agent gives the capability up here rather than sharing
    it: from this point the node's overlay state belongs to the SDN agent.
    """
    import subprocess

    try:
        with open(PRIMARY_AGENT_CONF_PATH) as f:
            content = f.read()
    except FileNotFoundError:
        return
    stripped = edit_caps_drivers(content, EVPN_DRIVER, add=False)
    if stripped is None:
        return
    with open(PRIMARY_AGENT_CONF_PATH, "w") as f:
        f.write(stripped)
    # try-restart: a node whose primary agent is not running keeps it that way.
    subprocess.run(["systemctl", "try-restart", PRIMARY_AGENT_UNIT], check=False)


def write_sdn_agent_service(node_uuid, endpoint: str, key_path: str) -> None:
    """Write the SDN agent config + systemd unit and enable the service."""
    import subprocess
    import urllib.parse

    host = urllib.parse.urlparse(endpoint).hostname
    os.makedirs(os.path.dirname(SDN_AGENT_CONF_PATH), exist_ok=True)
    with open(SDN_AGENT_CONF_PATH, "w") as f:
        f.write(
            SDN_AGENT_CONF_TEMPLATE.format(
                host=host, node_uuid=node_uuid, key_path=key_path
            )
        )
    with open(SDN_AGENT_UNIT_PATH, "w") as f:
        f.write(SDN_AGENT_UNIT_TEMPLATE.format(conf_path=SDN_AGENT_CONF_PATH))
    release_evpn_from_primary_agent()
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "--now", SDN_AGENT_UNIT], check=True)


# --- SDN fabric on a hypervisor host -----------------------------------------
# The overlay data plane a hypervisor runs next to libvirt: Open vSwitch (from
# the distro), gobgpd, evpn_connector and the SDN universal agent. The agent
# renders the configuration of the two daemons and starts them, so all that is
# installed here are the binaries, the venvs and the units.

# gobgp 3, which is what the installation is required to run: evpn_connector
# speaks the v3 gRPC API, and v4 renamed the proto package and the service and
# changed the NLRI encoding, so the daemon and the connector move together — a
# v4 gobgpd will not answer it.
GOBGP_DEFAULT_URL = (
    "https://github.com/osrg/gobgp/releases/download/v3.37.0/"
    "gobgp_3.37.0_linux_amd64.tar.gz"
)
# sha256 of the v3.37.0 linux/amd64 release tarball. Verifying it pins the
# binary by content — a tampered mirror or a MITM cannot land an arbitrary
# gobgpd that then runs as root. Bump alongside GOBGP_DEFAULT_URL.
GOBGP_SHA256 = "e20b2a155fe14450b9fe37e5c1a1d1bfe101eb479645f5bbea860a8fde30e522"
GOBGPD_BIN = "/usr/local/bin/gobgpd"
EVPN_DIR = "/opt/evpn"
EVPN_VENV = f"{EVPN_DIR}/venv"
SDK_VENV = "/opt/sdk_venv"
AGENT_BIN = "/usr/local/bin/exordos-universal-agent"
SDK_DEFAULT_PACKAGE = "gcl-sdk"

GOBGPD_UNIT_PATH = "/etc/systemd/system/gobgpd.service"
GOBGPD_UNIT = """[Unit]
Description=gobgpd (exordos evpn fabric)
After=network-online.target
Wants=network-online.target

[Service]
# /etc/gobgp.conf is rendered by the universal agent's evpn capability from
# the evpn_host/bgp_rr target resource; the agent (re)starts this service when
# the config changes. Not enabled here: without a config gobgpd fail-loops,
# and a host that never joins an overlay never needs it.
# The gRPC API is unauthenticated and can add or withdraw any EVPN route, so
# it listens on loopback only (gobgpd's default is every address); the
# connector and the gobgp CLI both dial localhost:50051.
ExecStart=/usr/local/bin/gobgpd -f /etc/gobgp.conf --api-hosts 127.0.0.1:50051
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
"""

CONNECTOR_UNIT_PATH = "/etc/systemd/system/evpn-connector.service"
CONNECTOR_UNIT = """[Unit]
Description=evpn-connector (exordos evpn fabric)
After=gobgpd.service openvswitch-switch.service
Wants=gobgpd.service

[Service]
# /opt/evpn/evpn_connector.cfg is rendered by the universal agent; per-guest
# client configs land in /opt/evpn/vm_conf. The agent enables and (re)starts
# this service once it writes the config.
# The fail-static flow dump defaults to /tmp/evpn_tmp_flow_file and is fed
# back to ovs-ofctl as root: a private /tmp keeps local users from planting it.
PrivateTmp=yes
WorkingDirectory=/opt/evpn
ExecStart=/opt/evpn/venv/bin/evpn-connector --config-file /opt/evpn/evpn_connector.cfg
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
"""
