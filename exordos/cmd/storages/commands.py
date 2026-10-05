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

import os
import socket
import subprocess
from urllib.parse import urlparse
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.aliases import ClickAliasedGroup
from exordos.cmd.base import create_entity_group
from exordos.cmd.compute.hypervisors import commands as hyper_commands
from exordos.common.run import run_command
from exordos.common.table import show_data
from exordos.logger import ClickLogger

DISK_SPEEDS = ["COLD", "WARM", "HOT"]
RAWSTOR_OST_ENDPOINT_PORT = 7777
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
    add_show_command=False,
)


@click.command("show", help="Show storage cluster")
@click.argument("uuid", type=str, required=True)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.pass_context
def clusters_show_cmd(ctx, uuid, output):
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    cluster = base_client.get_entity(client, c.STORAGE_CLUSTER_COLLECTION, uuid)
    show_data({k: v for k, v in cluster.items() if k != "storage_pools"}, output)


clusters_group.add_command(clusters_show_cmd, aliases=["get", "g"])


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
        "Agent": "agent",
        "Status": "status",
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
        "Chunk size": lambda e: utils.human_readable_size(e["chunk_size"]),
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
@click.option("--host", default=None, help="Core address reachable from hypervisors")
@click.option("--port", type=click.IntRange(1, 65535), default=None)
@click.pass_context
def clusters_add_cmd(ctx, storage_type, name, uuid, description, host, port):
    client = _client(ctx)
    clusters = base_client.list_entities(client, c.STORAGE_CLUSTER_COLLECTION)
    used_ports = {
        urlparse(cluster["driver_spec"]["endpoint"]).port for cluster in clusters
    }
    if any(cluster["name"] == name for cluster in clusters):
        raise click.ClickException(f"Cluster {name} already exists")
    if port is None:
        port = (
            click.prompt("MDS port on the core", type=click.IntRange(1, 65535))
            if clusters
            else 7776
        )
    if port in used_ports:
        raise click.ClickException(f"MDS port {port} is already used")
    host = host or urlparse(ctx.obj.auth_data["endpoint"]).hostname
    if not host:
        raise click.ClickException(
            "Specify --host or a core API endpoint with a hostname"
        )
    host = f"[{host}]" if ":" in host and not host.startswith("[") else host
    endpoint = f"mds://{host}:{port}/"
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


@nodes_group.command("init", help="Install OST packages on the local host")
@click.option("--type", "storage_type", type=click.Choice(["rawstor"]), required=True)
@click.option(
    "--version", default=None, help="Override RAWSTOR_VERSION for installed packages"
)
def init_cmd(storage_type, version):
    _require_local_privileges()
    add_sudo = not hyper_commands.is_root()
    log = ClickLogger()
    log.info("[1/2] Downloading and installing rawstor packages...")
    hyper_commands.install_rawstor_packages(
        ["librawstor", "rawstor-ost"], add_sudo, version=version
    )
    log.info("[2/2] Installing storage dependencies (this may take several minutes)...")
    run_command(
        [
            "env",
            "DEBIAN_FRONTEND=noninteractive",
            "apt-get",
            "install",
            "-y",
            "python3-venv",
            "zfsutils-linux",
            "zfs-dkms",
            f"linux-headers-{os.uname().release}",
        ],
        sudo=add_sudo,
    )
    log.important("OST packages installed successfully")


def _prepare_local_storage_agent(ctx, agent=None):
    _require_local_privileges()
    agent = agent or hyper_commands.DEFAULT_AGENT_NAME
    run_command(["modprobe", "zfs"], sudo=not hyper_commands.is_root())
    core_host = urlparse(ctx.obj.auth_data["endpoint"]).hostname
    if not core_host:
        raise click.ClickException("Core API endpoint must contain a hostname")
    core_host = f"[{core_host}]" if ":" in core_host else core_host
    orch_endpoint = f"http://{core_host}:{hyper_commands.ORCH_API_PORT}"
    status_endpoint = f"http://{core_host}:{hyper_commands.STATUS_API_PORT}"
    target = hyper_commands.resolve_agent_install_target(
        agent, orch_endpoint, status_endpoint
    )
    node_uuid = hyper_commands.local_agent_node_uuid()
    existing = hyper_commands._read_existing_config(target.config_path)
    agent_uuid = node_uuid
    if existing is not None:
        explicit = hyper_commands._config_value(existing, "universal_agent", "uuid", "")
        uuid5_name = hyper_commands._config_value(
            existing, "universal_agent", "uuid5_name", ""
        )
        agent_uuid = explicit or (
            str(sys_uuid.uuid5(sys_uuid.UUID(node_uuid), uuid5_name))
            if uuid5_name
            else node_uuid
        )
    elif agent != hyper_commands.DEFAULT_AGENT_NAME:
        agent_uuid = str(sys_uuid.uuid5(sys_uuid.UUID(node_uuid), agent))
    wheel = hyper_commands.RAWSTOR_WHEEL_URL
    hyper_commands.install_agent_venv(
        target.venv_path,
        packages=[os.environ.get("LOCAL_GENESIS_SDK_PATH", "gcl_sdk"), wheel],
    )
    private_key_path = hyper_commands.write_agent_config(
        orch_endpoint=orch_endpoint,
        status_endpoint=status_endpoint,
        config_path=target.config_path,
        meta_file=str(target.meta_file).replace(
            "pool_meta.json", "storage_node_meta.json"
        ),
        default_private_key_path=target.default_private_key_path,
        driver_name="StorageNodeAgentDriver",
        agent_uuid=str(agent_uuid),
    )
    base_client.register_agent_and_write_key(
        _client(ctx),
        node_uuid,
        private_key_path,
        agent_uuid=str(agent_uuid),
        capabilities=["storage_node"],
    )
    client = _client(ctx)
    registered = base_client.get_entity(client, c.AGENT_COLLECTION, str(agent_uuid))
    capabilities = registered.get("capabilities", {}).get("capabilities", [])
    if "storage_node" not in capabilities:
        base_client.update_entity(
            client,
            c.AGENT_COLLECTION,
            str(agent_uuid),
            {"capabilities": {"capabilities": [*capabilities, "storage_node"]}},
        )
    hyper_commands.install_agent_systemd_unit(
        exec_path=target.exec_path,
        config_path=target.config_path,
        unit_path=target.unit_path,
        unit_name=target.unit_name,
    )
    return str(agent_uuid), node_uuid


@nodes_group.command(
    "add",
    help="Configure the local agent, create an OST and reconcile it into the cluster topology",
)
@click.option("--cluster", required=True, help="Cluster name or UUID")
@click.option(
    "--agent",
    default=hyper_commands.DEFAULT_AGENT_NAME,
    show_default=True,
    help="Local universal agent service instance to create or configure",
)
@click.option("--name", required=True, help="Storage node resource name")
@click.option(
    "--uuid",
    type=click.UUID,
    default=None,
    help="Optional resource UUID; generated by core if omitted",
)
@click.option(
    "--location",
    default=None,
    help="Backing URI; defaults to file:///var/lib/rawstor/UUID",
)
@click.option(
    "--bind",
    "bind_address",
    default=None,
    help="Bind IP:port; defaults to 0.0.0.0 and an unused port starting at 7777",
)
@click.option(
    "--endpoint",
    default=None,
    help="Advertised ost://host:port; auto-detected if omitted",
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
    ctx,
    cluster,
    agent,
    name,
    uuid,
    location,
    bind_address,
    endpoint,
    failure_domain_path,
    weight,
    description,
):
    client = _client(ctx)
    agent_uuid, node_uuid = _prepare_local_storage_agent(ctx, agent)
    agent_entity = {"uuid": agent_uuid, "node": node_uuid}
    if bind_address is None:
        if endpoint:
            port = _validate_uri(endpoint, "ost").port
        else:
            agents = base_client.list_entities(client, c.AGENT_COLLECTION)
            host_agents = {
                a["uuid"] for a in agents if a["node"] == agent_entity["node"]
            }
            host_agents.add(agent_entity["uuid"])
            nodes = base_client.list_entities(client, NODE_COLLECTION)
            used = {
                urlparse("ost://" + n["bind_address"]).port
                for n in nodes
                if n.get("agent") in host_agents and n.get("bind_address")
            }
            port = next((p for p in range(7777, 65536) if p not in used), None)
            if port is None:
                raise click.ClickException("No free OST port in range 7777..65535")
        bind_address = f"0.0.0.0:{port}"
    bind_uri = _validate_uri(f"ost://{bind_address}", "ost")
    if endpoint is None:
        endpoint = _detect_local_endpoint(ctx.obj.auth_data["endpoint"], bind_uri.port)
    _validate_uri(endpoint, "ost")
    data = {
        "name": name,
        "description": description,
        "cluster": _cluster_uuid(client, cluster),
        "kind": "rawstor",
        "agent": agent_entity["uuid"],
        "bind_address": bind_address,
        "endpoint": endpoint.rstrip("/"),
        "failure_domain_path": failure_domain_path,
        "weight": weight,
    }
    if uuid is not None:
        data["uuid"] = str(uuid)
    if location is not None:
        data["location"] = location
    show_data(base_client.add_entity(client, NODE_COLLECTION, data))


@nodes_group.command("update")
@click.argument("identifier")
@click.option("--name", default=None)
@click.option("--description", default=None)
@click.option("--endpoint", default=None)
@click.option("--bind", "bind_address", default=None)
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
