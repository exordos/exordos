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
import shutil
import socket
import subprocess
import typing as tp
from urllib.parse import urlparse
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.compute.hypervisors import commands as hyper_commands
from exordos.common.crypto import write_root_owned_file
from exordos.common.run import run_command
from exordos.common.table import show_data
from exordos.logger import ClickLogger

# Must match gcl_sdk's StorageClusterAgentDriver.get_capabilities()
# (MetaCoordinatorAgentDriver's default: the keys of its __model_map__) -
# pre-declaring it here lets the scheduler place this cluster onto the
# agent right away, instead of waiting for its first self-registration.
STORAGE_CLUSTER_AGENT_CAPABILITIES = ["storage_cluster"]

DISK_SPEEDS = ["COLD", "WARM", "HOT"]

# rawstor-ost's own default backing store (systemd/rawstor-ost.service in
# librawstor) - used here only to know what "no --location given" means.
RAWSTOR_DEFAULT_BACKING_STORE = "file:///var/lib/rawstor"
RAWSTOR_OST_CONF_PATH = "/etc/rawstor-ost.conf"
RAWSTOR_OST_ENDPOINT_PORT = 7777

ENTITY = "storage"
ENTITY_COLLECTION = c.STORAGE_CLUSTER_COLLECTION


def _pool0(entity: dict, field: str, default: str = "Unknown"):
    pools = entity.get("storage_pools") or [{}]
    return pools[0].get(field, default)


FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Description": "description",
    "Speed": lambda e: _pool0(e, "speed"),
    "Ephemeral": lambda e: _pool0(e, "ephemeral"),
    "Total": lambda e: _pool0(e, "capacity_usable"),
    "Available": lambda e: _pool0(e, "available_actual"),
    "Status": "status",
}


storages_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, group_name="storages"
)


@click.command("add", help="Add a new storage cluster")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the storage cluster",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="storage",
    help="Name of the storage cluster",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the storage cluster",
)
@click.option(
    "--driver-spec",
    multiple=True,
    help=(
        "Driver specification key/value pairs, e.g. --driver-spec kind=rawstor "
        "--driver-spec location=file:///var/lib/rawstor --driver-spec "
        "endpoint=ost://10.0.0.5:7777 --driver-spec speed=HOT "
        "--driver-spec ephemeral=false"
    ),
)
@click.option(
    "--storage-pools",
    type=str,
    default=None,
    help=(
        "Storage pools as a JSON list, for a cluster with more than the "
        'single "default" pool `storages init` creates, e.g. \'[{"kind": '
        '"thin_storage_pool", "name": "default", "speed": "HOT", '
        '"ephemeral": false, "capacity_usable": 100}]\''
    ),
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    driver_spec: tuple[str, ...],
    storage_pools: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data: dict = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "driver_spec": utils.convert_input_multiply(driver_spec),
    }
    if storage_pools is not None:
        data["storage_pools"] = json.loads(storage_pools)
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


@click.command("update", help=f"Update {ENTITY}")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help=f"Description of the {ENTITY}",
)
@click.option(
    "--driver-spec",
    multiple=True,
    help=(
        "Driver specification key/value pairs to merge into the existing "
        "one. The format is 'key=value'. For example: --driver-spec a=b"
    ),
)
@click.option(
    "--storage-pools",
    type=str,
    default=None,
    help="Storage pools as a JSON list, replacing the current ones entirely.",
)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    name: str | None,
    description: str | None,
    driver_spec: tuple[str, ...],
    storage_pools: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data: dict = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description

    driver_spec_dict = utils.convert_input_multiply(driver_spec)
    if driver_spec_dict:
        cluster_data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
        current_spec = cluster_data.get("driver_spec") or {}
        data["driver_spec"] = {**current_spec, **driver_spec_dict}
    if storage_pools is not None:
        data["storage_pools"] = json.loads(storage_pools)

    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


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


def _backing_store_capacity_gb(location: str) -> int:
    """Total capacity, in GiB, of a `file://` backing store's filesystem."""
    path = location.removeprefix("file://") or "/"
    try:
        usage = shutil.disk_usage(path)
    except OSError:
        return 0
    return usage.total >> c.GB_SHIFT


def provision_rawstor_cluster(
    log: ClickLogger,
    add_sudo: bool,
    location: str | None,
    speed: str,
    ephemeral: bool,
    endpoint: str | None,
    core_endpoint: str,
) -> tuple[dict, list[dict]]:
    """Install and configure a local rawstor-ost, returning
    (driver_spec, storage_pools) ready to register via `storages add`.
    """
    log.info("Installing rawstor packages...")
    hyper_commands.install_rawstor_packages(["librawstor", "rawstor-ost"], add_sudo)

    if location is not None:
        log.info("Configuring rawstor-ost's backing store...")
        write_root_owned_file(
            f"LOCATION={location}\n", RAWSTOR_OST_CONF_PATH, mode="644"
        )
        run_command(["systemctl", "restart", "rawstor-ost"], sudo=add_sudo)

    final_location = location or RAWSTOR_DEFAULT_BACKING_STORE
    final_endpoint = endpoint or _detect_local_endpoint(core_endpoint)

    driver_spec = {
        "kind": "rawstor",
        "location": final_location,
        "endpoint": final_endpoint,
        "speed": speed,
        "ephemeral": ephemeral,
    }
    storage_pools = [
        {
            # ThinStoragePool.KIND - storage_pools is a KindModelSelectorType
            # on the server, so each entry needs its discriminator.
            "kind": "thin_storage_pool",
            "name": "default",
            "speed": speed,
            "ephemeral": ephemeral,
            "capacity_usable": _backing_store_capacity_gb(final_location),
        }
    ]
    return driver_spec, storage_pools


# Dispatch table for `storages init --type <...>` - adding a backend
# besides rawstor means registering another provisioner here, not
# branching inside init_cmd itself.
STORAGE_TYPE_PROVISIONERS: dict[str, tp.Callable] = {
    "rawstor": provision_rawstor_cluster,
}


@storages_group.command("init", help="Initialize a storage cluster")
@click.option(
    "--type",
    "storage_type",
    type=click.Choice(list(STORAGE_TYPE_PROVISIONERS)),
    required=True,
    help="Storage backend type",
)
@click.option(
    "--location",
    type=str,
    default=None,
    help=(
        "Backing store for the storage backend (e.g. file:///var/lib/rawstor "
        "for rawstor). Defaults to the backend's own default if not given."
    ),
)
@click.option(
    "--speed",
    type=click.Choice(DISK_SPEEDS, case_sensitive=False),
    default="HOT",
    show_default=True,
    help="Speed tier disks scheduled onto this cluster's pool will be tagged with",
)
@click.option(
    "--ephemeral/--no-ephemeral",
    default=False,
    show_default=True,
    help="Whether this cluster's pool is ephemeral storage",
)
@click.option(
    "--endpoint",
    type=str,
    default=None,
    help=(
        "Network address (ost://host:port) other hosts use to reach this "
        "cluster. Auto-detected from the interface used to reach the core "
        "if not given - override on a multi-homed storage node."
    ),
)
@click.option(
    "--add",
    show_default=True,
    is_flag=True,
    default=False,
    help=(
        "After initialization, register the storage cluster in the "
        "orchestrator (same as running `storages add`), using the "
        "top-level `exordos --endpoint/--user/--password` credentials."
    ),
)
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the storage cluster. Defaults to a UUID derived from /etc/machine-id.",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the storage cluster. Defaults to this machine's hostname.",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the storage cluster",
)
@click.option(
    "--pool-agent-name",
    "agent_name",
    type=str,
    default=hyper_commands.DEFAULT_AGENT_NAME,
    show_default=True,
    help=(
        "Name of the universal agent to run StorageClusterAgentDriver "
        "under. The default targets the standard agent (merging in if "
        "this host is also a registered compute node or hypervisor)."
    ),
)
@click.pass_context
def init_cmd(
    ctx: click.Context,
    storage_type: str,
    location: str | None,
    speed: str,
    ephemeral: bool,
    endpoint: str | None,
    add: bool,
    uuid: sys_uuid.UUID | None,
    name: str | None,
    description: str,
    agent_name: str,
) -> None:
    """Initialize a storage node with all required components."""
    if not hyper_commands._check_debian_like():
        raise click.ClickException(
            "This command is only supported on Debian-based systems."
        )

    if subprocess.call(["sudo", "-n", "true"], stderr=subprocess.DEVNULL) != 0:
        click.secho("Sudo privileges are required to proceed.", fg="yellow")
        if subprocess.call(["sudo", "-v"]) != 0:
            raise click.ClickException("Failed to obtain sudo privileges. Aborting.")

    log = ClickLogger()
    add_sudo = not hyper_commands.is_root()
    speed = speed.upper()

    core_endpoint = ctx.obj.auth_data["endpoint"]
    core_host = urlparse(core_endpoint).hostname
    orch_endpoint = f"http://{core_host}:{hyper_commands.ORCH_API_PORT}"
    status_endpoint = f"http://{core_host}:{hyper_commands.STATUS_API_PORT}"
    agent_target = hyper_commands.resolve_agent_install_target(
        agent_name=agent_name,
        orch_endpoint=orch_endpoint,
        status_endpoint=status_endpoint,
    )

    log.info("Setting up the local universal agent's virtualenv...")
    hyper_commands.install_agent_venv(
        agent_target.venv_path,
        packages=["gcl_sdk", hyper_commands.RAWSTOR_WHEEL_URL],
    )

    log.info(f"Provisioning storage backend ({storage_type})...")
    provisioner = STORAGE_TYPE_PROVISIONERS[storage_type]
    driver_spec, storage_pools = provisioner(
        log=log,
        add_sudo=add_sudo,
        location=location,
        speed=speed,
        ephemeral=ephemeral,
        endpoint=endpoint,
        core_endpoint=core_endpoint,
    )

    if add:
        log.info("Registering storage cluster...")
        final_uuid = (
            uuid if uuid is not None else hyper_commands._default_hypervisor_uuid()
        )
        final_name = (
            name if name is not None else hyper_commands._default_hypervisor_name()
        )

        # Same as running `storages add` right after `init`.
        ctx.invoke(
            add_cmd,
            uuid=final_uuid,
            name=final_name,
            description=description,
            driver_spec=tuple(f"{k}={v}" for k, v in driver_spec.items()),
            storage_pools=json.dumps(storage_pools),
        )

        log.info("Setting up the local universal agent...")
        client = base_client.get_user_api_client(ctx.obj.auth_data)
        node_uuid = hyper_commands.local_agent_node_uuid()
        hyper_commands.reset_agent_meta_file(agent_target.meta_file)
        private_key_path = hyper_commands.write_agent_config(
            orch_endpoint=orch_endpoint,
            status_endpoint=status_endpoint,
            config_path=agent_target.config_path,
            meta_file=agent_target.meta_file,
            default_private_key_path=agent_target.default_private_key_path,
            driver_name="StorageClusterAgentDriver",
        )
        base_client.register_agent_and_write_key(
            client,
            node_uuid,
            private_key_path,
            capabilities=STORAGE_CLUSTER_AGENT_CAPABILITIES,
        )
        hyper_commands.install_agent_systemd_unit(
            exec_path=agent_target.exec_path,
            config_path=agent_target.config_path,
            unit_path=agent_target.unit_path,
            unit_name=agent_target.unit_name,
        )

    log.important("Storage environment initialized successfully")


storages_group.add_command(add_cmd, aliases=["a"])
storages_group.add_command(update_cmd, aliases=["u"])
