#    Copyright 2026 Genesis Corporation.
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
from __future__ import annotations

import json
from pathlib import Path
import socket
import subprocess
from urllib.parse import urlparse
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.aliases import ClickAliasedGroup
from exordos.cmd.base import create_entity_group
from exordos.cmd.compute.hypervisors import commands as hyper_commands
from exordos.common.crypto import write_root_owned_file
from exordos.common.run import run_command
from exordos.common.table import show_data
from exordos.logger import ClickLogger

DISK_SPEEDS = ["COLD", "WARM", "HOT"]
RAWSTOR_OST_ENDPOINT_PORT = 7777
LOCAL_CONFIG_DIR = Path("/etc/rawstor-ost/instances")
NODE_COLLECTION = "v1/storage/nodes/"
POOL_COLLECTION = "v1/storage/pools/"


@click.group("storages", cls=ClickAliasedGroup)
def storages_group():
    """Manage storage clusters, OST nodes and shared-capacity pool policies."""


clusters_group = create_entity_group(
    "storage cluster",
    c.STORAGE_CLUSTER_COLLECTION,
    {
        "UUID": "uuid",
        "Name": "name",
        "MDS": lambda e: e["driver_spec"]["endpoint"],
        "Status": "status",
        "Available bytes": lambda e: e.get("capacity_info", {}).get("available", 0),
    },
    group_name="clusters",
)


def _filter_cluster(entities, kwargs):
    cluster_name = kwargs.get("cluster")
    if not cluster_name:
        return entities
    ctx = click.get_current_context()
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    cluster = base_client.get_entity(client, c.STORAGE_CLUSTER_COLLECTION, cluster_name)
    return [entity for entity in entities if entity["cluster"] == cluster["uuid"]]


nodes_group = create_entity_group(
    "storage node",
    NODE_COLLECTION,
    {
        "UUID": "uuid",
        "Name": "name",
        "Cluster": "cluster",
        "Endpoint": "endpoint",
        "Failure domain path": "failure_domain_path",
        "Weight": "weight",
    },
    group_name="nodes",
    post_fetch_handler=_filter_cluster,
    extra_options=[click.Option(["--cluster"], help="Filter by cluster name or UUID")],
)
pools_group = create_entity_group(
    "storage pool",
    POOL_COLLECTION,
    {
        "UUID": "uuid",
        "Name": "name",
        "Cluster": "cluster",
        "Speed": "speed",
        "Ephemeral": "ephemeral",
        "Mirrors": "mirrors",
        "Failure domain": "failure_domain",
        "Chunk bytes": "chunk_size",
    },
    group_name="pools",
    post_fetch_handler=_filter_cluster,
    extra_options=[click.Option(["--cluster"], help="Filter by cluster name or UUID")],
)


def _client(ctx):
    return base_client.get_user_api_client(ctx.obj.auth_data)


def _cluster_uuid(client, name):
    return base_client.get_entity(client, c.STORAGE_CLUSTER_COLLECTION, name)["uuid"]


def _validate_uri(value, scheme):
    try:
        parsed = urlparse(value)
        if (
            parsed.scheme != scheme
            or not parsed.hostname
            or not parsed.port
            or parsed.path not in ("", "/")
            or parsed.username
            or parsed.query
            or parsed.fragment
            or any(ch.isspace() for ch in value)
        ):
            raise ValueError()
    except ValueError:
        raise click.ClickException(f"Expected {scheme}://host:port")
    return parsed


@clusters_group.command(
    "add", help="Create a core MDS with persistent and ephemeral WARM pools"
)
@click.option("--type", "storage_type", type=click.Choice(["rawstor"]), required=True)
@click.option("--name", required=True)
@click.option("--uuid", type=click.UUID, default=None)
@click.option("--description", default="")
@click.option(
    "--mds-host", default=None, help="Core address reachable from hypervisors"
)
@click.option("--mds-port", type=click.IntRange(1, 65535), default=None)
@click.pass_context
def clusters_add_cmd(ctx, storage_type, name, uuid, description, mds_host, mds_port):
    client = _client(ctx)
    clusters = base_client.list_entities(client, c.STORAGE_CLUSTER_COLLECTION)
    used_ports = {
        urlparse(cluster["driver_spec"]["endpoint"]).port for cluster in clusters
    }
    if any(cluster["name"] == name for cluster in clusters):
        raise click.ClickException(f"Cluster {name} already exists")
    if mds_port is None:
        mds_port = (
            click.prompt("MDS port on the core", type=click.IntRange(1, 65535))
            if clusters
            else 7776
        )
    if mds_port in used_ports:
        raise click.ClickException(f"MDS port {mds_port} is already used")
    host = mds_host or urlparse(ctx.obj.auth_data["endpoint"]).hostname
    if not host:
        raise click.ClickException(
            "Specify --mds-host or a core API endpoint with a hostname"
        )
    host = f"[{host}]" if ":" in host and not host.startswith("[") else host
    endpoint = f"mds://{host}:{mds_port}/"
    _validate_uri(endpoint, "mds")
    entity = base_client.add_entity(
        client,
        c.STORAGE_CLUSTER_COLLECTION,
        {
            "uuid": str(uuid or sys_uuid.uuid4()),
            "name": name,
            "description": description,
            "driver_spec": {"kind": storage_type, "endpoint": endpoint},
        },
    )
    show_data(entity)


@clusters_group.command("update")
@click.argument("identifier")
@click.option("--name", default=None)
@click.option("--description", default=None)
@click.pass_context
def clusters_update_cmd(ctx, identifier, name, description):
    data = {
        key: value
        for key, value in {"name": name, "description": description}.items()
        if value is not None
    }
    show_data(
        base_client.update_entity(
            _client(ctx), c.STORAGE_CLUSTER_COLLECTION, identifier, data
        )
    )


def _require_local_privileges() -> None:
    if not hyper_commands._check_debian_like():
        raise click.ClickException(
            "This command is only supported on Debian-based systems."
        )
    if (
        not hyper_commands.is_root()
        and subprocess.call(["sudo", "-n", "true"], stderr=subprocess.DEVNULL) != 0
    ):
        if subprocess.call(["sudo", "-v"]) != 0:
            raise click.ClickException("Failed to obtain sudo privileges. Aborting.")


def _detect_local_endpoint(
    core_endpoint: str, port: int = RAWSTOR_OST_ENDPOINT_PORT
) -> str:
    """Auto-detect this host's routable IP by asking the OS which local
    interface it would use to reach the core - the same network
    hypervisors need to reach this storage node's rawstor-ost over.

    A connected UDP socket never actually sends a packet; the OS still
    has to pick a source interface for it, which is what's read back.
    """
    core_host = urlparse(core_endpoint).hostname
    try:
        resolved = socket.gethostbyname(core_host)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.5)
            s.connect((resolved, 1))
            local_ip = s.getsockname()[0]
    except OSError as e:
        raise click.ClickException(
            "Unable to auto-detect a local IP address to advertise as this "
            f"cluster's endpoint (tried to reach {core_host}: {e}). "
            "Pass --endpoint explicitly instead."
        )
    return f"ost://{local_ip}:{port}"


def _instance_path(name):
    if (
        not name
        or any(
            ch
            not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
            for ch in name
        )
        or name in (".", "..")
    ):
        raise click.ClickException(
            "OST instance name may contain letters, digits, dots, underscores and hyphens"
        )
    return LOCAL_CONFIG_DIR / f"{name}.json"


def _read_instance(name):
    path = _instance_path(name)
    try:
        return json.loads(hyper_commands.read_with_sudo(str(path)))
    except (OSError, hyper_commands.exceptions.RunException):
        raise click.ClickException(
            f"OST {name} is not initialized; run storages nodes init first or pass --endpoint and --uuid"
        )


@nodes_group.command(
    "init", help="Install and start a local OST without registering it in a cluster"
)
@click.option("--type", "storage_type", type=click.Choice(["rawstor"]), required=True)
@click.option(
    "--name", default=None, help="Local OST instance name; defaults to hostname"
)
@click.option("--uuid", type=click.UUID, default=None, help="Stable OST identity")
@click.option(
    "--location",
    default=None,
    help="Backing URI; defaults to file:///var/lib/rawstor/UUID",
)
@click.option("--bind", "bind_address", default="0.0.0.0:7777", show_default=True)
@click.option(
    "--endpoint",
    default=None,
    help="Advertised ost://host:port; auto-detected if omitted",
)
@click.option(
    "--rawstor-version",
    default=None,
    help="Override RAWSTOR_VERSION for installed packages",
)
@click.pass_context
def init_cmd(
    ctx, storage_type, name, uuid, location, bind_address, endpoint, rawstor_version
):
    name = name or socket.gethostname()
    path = _instance_path(name)
    bind_uri = _validate_uri(f"ost://{bind_address}", "ost")
    endpoint = endpoint or _detect_local_endpoint(
        ctx.obj.auth_data["endpoint"], bind_uri.port
    )
    _validate_uri(endpoint, "ost")
    if path.exists():
        existing = _read_instance(name)
        if uuid is not None and str(uuid) != existing["uuid"]:
            raise click.ClickException("An initialized OST's UUID cannot be changed")
        uuid = sys_uuid.UUID(existing["uuid"])
        location = location or existing["location"]
    uuid = uuid or sys_uuid.uuid5(hyper_commands._default_hypervisor_uuid(), name)
    location = location or f"file:///var/lib/rawstor/{uuid}"
    if any(ch.isspace() for ch in location) or not location.startswith("file:///"):
        raise click.ClickException(
            "Backing store must be an absolute file:/// URI without whitespace"
        )
    _require_local_privileges()
    add_sudo = not hyper_commands.is_root()
    hyper_commands.install_rawstor_packages(
        ["librawstor", "rawstor-ost"], add_sudo, version=rawstor_version
    )
    run_command(["systemctl", "disable", "--now", "rawstor-ost"], sudo=add_sudo)
    backing = location.removeprefix("file://")
    run_command(["mkdir", "-p", backing], sudo=add_sudo)
    run_command(["chown", "rawstor:rawstor", backing], sudo=add_sudo)
    unit_name = f"rawstor-ost@{uuid}.service"
    unit = f"""[Unit]
Description=Rawstor OST {name}
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=rawstor
Group=rawstor
StateDirectory=rawstor/{uuid}
ExecStart=/usr/bin/rawstor-ost --bind={bind_address} {location}
Restart=always
RestartSec=5
ProtectSystem=strict
ReadWritePaths={backing}
ProtectHome=true
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
"""
    write_root_owned_file(unit, f"/etc/systemd/system/{unit_name}", mode="644")
    write_root_owned_file(
        json.dumps(
            {
                "uuid": str(uuid),
                "name": name,
                "kind": storage_type,
                "endpoint": endpoint.rstrip("/"),
                "location": location,
                "bind": bind_address,
            },
            indent=2,
        )
        + "\n",
        str(path),
        mode="644",
    )
    run_command(["systemctl", "daemon-reload"], sudo=add_sudo)
    run_command(["systemctl", "enable", "--now", unit_name], sudo=add_sudo)
    run_command(["systemctl", "restart", unit_name], sudo=add_sudo)
    ClickLogger().important(f"OST {name} initialized: {endpoint}, UUID {uuid}")


@nodes_group.command(
    "add", help="Register an initialized OST in a cluster's MDS topology"
)
@click.option("--cluster", required=True, help="Cluster name or UUID")
@click.option("--name", default=None, help="Local instance name; defaults to hostname")
@click.option("--uuid", type=click.UUID, default=None)
@click.option(
    "--endpoint",
    default=None,
    help="OST URI; read from local init configuration if omitted",
)
@click.option(
    "--failure-domain-path",
    required=True,
    help="dc/row/rack/server; outer levels may be omitted",
)
@click.option(
    "--weight",
    type=click.FloatRange(min=0, min_open=True),
    default=1.0,
    show_default=True,
)
@click.option("--description", default="")
@click.pass_context
def nodes_add_cmd(
    ctx, cluster, name, uuid, endpoint, failure_domain_path, weight, description
):
    name = name or socket.gethostname()
    if endpoint is None:
        local = _read_instance(name)
        endpoint = local["endpoint"]
        if uuid is not None and str(uuid) != local["uuid"]:
            raise click.ClickException("UUID must match the initialized OST")
        uuid = sys_uuid.UUID(local["uuid"])
    elif uuid is None:
        raise click.ClickException(
            "Remote registration requires --uuid to preserve OST identity"
        )
    _validate_uri(endpoint, "ost")
    client = _client(ctx)
    data = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "cluster": _cluster_uuid(client, cluster),
        "kind": "rawstor",
        "endpoint": endpoint.rstrip("/"),
        "failure_domain_path": failure_domain_path,
        "weight": weight,
    }
    show_data(base_client.add_entity(client, NODE_COLLECTION, data))


@nodes_group.command("update")
@click.argument("identifier")
@click.option("--name", default=None)
@click.option("--description", default=None)
@click.option("--endpoint", default=None)
@click.option("--failure-domain-path", default=None)
@click.option("--weight", type=click.FloatRange(min=0, min_open=True), default=None)
@click.pass_context
def nodes_update_cmd(ctx, identifier, **kwargs):
    data = {key: value for key, value in kwargs.items() if value is not None}
    if "endpoint" in data:
        _validate_uri(data["endpoint"], "ost")
        data["endpoint"] = data["endpoint"].rstrip("/")
    show_data(
        base_client.update_entity(_client(ctx), NODE_COLLECTION, identifier, data)
    )


def _chunk_size(ctx, param, value):
    if value is None:
        return None
    text = value.upper().removesuffix("IB").removesuffix("B")
    factor = 1
    if text[-1:] in ("K", "M", "G"):
        factor = {"K": 1 << 10, "M": 1 << 20, "G": 1 << 30}[text[-1]]
        text = text[:-1]
    try:
        size = int(text) * factor
    except ValueError:
        raise click.BadParameter("Use a byte count or a size such as 256MiB or 1GiB")
    if size <= 0 or size & (size - 1) or size > 1 << 30:
        raise click.BadParameter(
            "Chunk size must be a power of two no larger than 1GiB"
        )
    return size


def _pool_options(f):
    for option in [
        click.option(
            "--speed",
            type=click.Choice(DISK_SPEEDS, case_sensitive=False),
            default=None,
        ),
        click.option("--ephemeral/--no-ephemeral", default=None),
        click.option("--mirrors", type=click.IntRange(1, 255), default=None),
        click.option("--chunk-size", callback=_chunk_size, default=None),
        click.option(
            "--failure-domain",
            type=click.Choice(["ost", "server", "rack", "row", "dc"]),
            default=None,
        ),
        click.option("--description", default=None),
    ]:
        f = option(f)
    return f


@pools_group.command("add", help="Add a policy sharing its cluster's capacity")
@click.option("--cluster", required=True)
@click.option("--name", required=True)
@click.option("--uuid", type=click.UUID, default=None)
@_pool_options
@click.pass_context
def pools_add_cmd(ctx, cluster, name, uuid, **kwargs):
    client = _client(ctx)
    data = {key: value for key, value in kwargs.items() if value is not None}
    if "speed" in data:
        data["speed"] = data["speed"].upper()
    data.update(
        cluster=_cluster_uuid(client, cluster),
        name=name,
        uuid=str(uuid or sys_uuid.uuid4()),
    )
    show_data(base_client.add_entity(client, POOL_COLLECTION, data))


@pools_group.command("update")
@click.argument("identifier")
@click.option("--name", default=None)
@_pool_options
@click.pass_context
def pools_update_cmd(ctx, identifier, **kwargs):
    data = {key: value for key, value in kwargs.items() if value is not None}
    if "speed" in data:
        data["speed"] = data["speed"].upper()
    show_data(
        base_client.update_entity(_client(ctx), POOL_COLLECTION, identifier, data)
    )


storages_group.add_command(clusters_group, aliases=["c"])
storages_group.add_command(nodes_group, aliases=["n"])
storages_group.add_command(pools_group, aliases=["p"])
