#    Copyright 2025 Genesis Corporation.
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

import time
import uuid as sys_uuid

from bazooka import exceptions as bazooka_exc
import rich_click as click

from exordos import constants as c
from exordos import logger
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.compute import common as compute_common
from exordos.cmd.network import common as net_common
from exordos.common.table import show_data

ENTITY = "node"
ENTITY_COLLECTION = c.NODE_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Cores": "cores",
    "RAM": "ram",
    "IP": lambda x: x.get("default_network", {}).get("ipv4", "unknown"),
    "Disks": compute_common.extract_disks_from_entity,
    "Image": compute_common.extract_image_from_entity,
    "Status": "status",
}

cn_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP, "cn")


def _validate_hostname(hostname: str) -> None:
    if not utils.is_valid_hostname(hostname):
        raise click.ClickException(f"Invalid hostname: {hostname}")


@click.command("add", help="Add a new node to the Exordos installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the node",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the node",
)
@click.option(
    "-c",
    "--cores",
    type=int,
    default=1,
    show_default=True,
    help="Number of cores to allocate for the node",
)
@click.option(
    "-r",
    "--ram",
    type=int,
    default=1024,
    show_default=True,
    help="Amount of RAM in Mb to allocate for the node",
)
@click.option(
    "-d",
    "--root-disk",
    type=int,
    default=10,
    show_default=True,
    help="Number of GiB of root disk to allocate for the node",
)
@click.option(
    "-i",
    "--image",
    type=str,
    required=True,
    help="Name of the image to deploy",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="node",
    help="Name of the node",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the node",
)
@click.option(
    "--hostname",
    type=str,
    default=None,
    help="Hostname of the node",
)
@click.option(
    "--network",
    type=str,
    default=None,
    help=(
        "Give the node one leg on this network (UUID or name). Shorthand for "
        "`--interface network=<ref>`; use --interface for anything more."
    ),
)
@click.option(
    "--interface",
    "interfaces",
    type=str,
    multiple=True,
    default=(),
    help=(
        "A leg of the node, repeatable: "
        "subnet=<ref>[,address=<ip>][,index=<n>][,sg=<ref>][,public=<ref>], "
        "or port=<ref>[,index=<n>] to adopt a port that already exists. "
        "Index 0 is the primary leg, whose address the node publishes as its "
        "own; left unset, legs are numbered in the order given."
    ),
)
@click.option(
    "--no-network",
    is_flag=True,
    default=False,
    help=(
        "Give the node no networking at all. Different from saying nothing, "
        "which places it on the installation's default network."
    ),
)
@click.option(
    "--wait",
    type=bool,
    is_flag=True,
    default=False,
    help="Wait until the node is running",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    cores: int,
    ram: int,
    root_disk: int,
    image: str,
    name: str,
    description: str,
    hostname: str | None,
    network: str | None,
    interfaces: tuple[str, ...],
    no_network: bool,
    wait: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    log = logger.ClickLogger()
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "cores": cores,
        "ram": ram,
        "name": name,
        "description": description,
        "disk_spec": {
            "kind": "root_disk",
            "size": root_disk,
            "image": image,
        },
    }
    if hostname is not None:
        _validate_hostname(hostname)
        data["hostname"] = hostname
    if no_network and (network or interfaces):
        raise click.ClickException(
            "--no-network says the node wants no legs; it cannot be combined "
            "with --network or --interface"
        )
    if network and interfaces:
        raise click.ClickException(
            "--network is shorthand for a single --interface; give one or the other"
        )
    # Three states, and an empty list is not the absent one: no flag at all
    # leaves `interfaces` unset, which is how a node says nothing and gets
    # placed on the installation's default network.
    if no_network:
        data["interfaces"] = []
    elif network:
        data["interfaces"] = [
            {
                "kind": "subnet",
                "network": net_common.resolve(client, c.NETWORK_COLLECTION, network),
            }
        ]
    elif interfaces:
        data["interfaces"] = [
            net_common.parse_interface(client, spec) for spec in interfaces
        ]
    try:
        entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    except bazooka_exc.BadRequestError as e:
        # A core older than node interfaces refuses the unknown field. Its
        # `default_network` would not pin a network either, so there is
        # nothing to fall back to.
        if "interfaces" in data and "interfaces" in e.cause.response.text:
            raise click.ClickException(
                "This core does not support node interfaces: "
                "--network, --interface and --no-network need a newer core"
            )
        raise
    if not wait:
        show_data(entity)
        return
    while entity["status"] != "ACTIVE":
        log.info(f"Waiting for node to be ready. Status: {entity['status']}")
        time.sleep(2)
        entity = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(entity)


@click.command("update", help="Update an existing node")
@click.pass_context
@click.option(
    "-u",
    "--uuid_or_name",
    type=str,
    required=True,
    help="UUID or name of the node to update",
)
@click.option(
    "-c",
    "--cores",
    type=int,
    default=None,
    help="Number of cores to allocate for the node",
)
@click.option(
    "-r",
    "--ram",
    type=int,
    default=None,
    help="Amount of RAM in Mb to allocate for the node",
)
@click.option(
    "-d",
    "--root-disk",
    type=int,
    default=None,
    help="Number of GiB of root disk to allocate for the node",
)
@click.option(
    "-i",
    "--image",
    type=str,
    default=None,
    help="Name of the image to deploy",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the node",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the node",
)
@click.option(
    "--wait",
    type=bool,
    is_flag=True,
    help="Wait until the node is running",
)
def update_cmd(
    ctx: click.Context,
    uuid_or_name: str,
    cores: int | None,
    ram: int | None,
    root_disk: int | None,
    image: str | None,
    name: str | None,
    description: str | None,
    wait: bool,
) -> None:
    update_data = {}
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    try:
        entity = base_client.get_entity(client, ENTITY_COLLECTION, uuid_or_name)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"Node with UUID or name {uuid_or_name} not found")

    if cores is not None:
        update_data["cores"] = cores
    if ram is not None:
        update_data["ram"] = ram
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description

    if root_disk is not None or image is not None:
        update_data["disk_spec"] = entity["disk_spec"]

        if update_data["disk_spec"]["kind"] == "root_disk":
            update_data["disk_spec"]["size"] = (
                root_disk or update_data["disk_spec"]["size"]
            )
            update_data["disk_spec"]["image"] = (
                image or update_data["disk_spec"]["image"]
            )
        elif update_data["disk_spec"]["kind"] == "disks":
            update_data["disk_spec"]["disks"][0]["size"] = (
                root_disk or update_data["disk_spec"]["disks"][0]["size"]
            )
            update_data["disk_spec"]["disks"][0]["image"] = (
                image or update_data["disk_spec"]["disks"][0]["image"]
            )
        else:
            raise click.ClickException(
                f"Unsupported disk spec kind: {update_data['disk_spec']['kind']}"
            )

    if not update_data:
        raise click.ClickException("No updates provided")

    entity = base_client.update_entity(
        client, ENTITY_COLLECTION, uuid_or_name, update_data
    )
    if not wait:
        show_data(entity)
        return
    log = logger.ClickLogger()
    while entity["status"] != "ACTIVE":
        log.info(f"Waiting for node to be ready. Status: {entity['status']}")
        time.sleep(2)
        entity = base_client.get_entity(client, ENTITY_COLLECTION, uuid_or_name)
    show_data(entity)


@cn_group.command("add-or-update", help="Add a new node or update an existing one")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the node",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the node",
)
@click.option(
    "-c",
    "--cores",
    type=int,
    default=1,
    show_default=True,
    help="Number of cores to allocate for the node",
)
@click.option(
    "-r",
    "--ram",
    type=int,
    default=1024,
    show_default=True,
    help="Amount of RAM in Mb to allocate for the node",
)
@click.option(
    "-d",
    "--root-disk",
    type=int,
    default=10,
    show_default=True,
    help="Number of GiB of root disk to allocate for the node",
)
@click.option(
    "-i",
    "--image",
    type=str,
    required=True,
    help="Name of the image to deploy",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="node",
    help="Name of the node",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the node",
)
@click.option(
    "--hostname",
    type=str,
    default=None,
    help="Hostname of the node",
)
@click.option(
    "--wait",
    type=bool,
    is_flag=True,
    default=False,
    help="Wait until the node is running",
)
def add_or_update_node_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    cores: int,
    ram: int,
    root_disk: int,
    image: str,
    name: str,
    description: str,
    hostname: str | None,
    wait: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        return ctx.invoke(
            add_cmd,
            uuid=uuid,
            project_id=project_id,
            cores=cores,
            ram=ram,
            root_disk=root_disk,
            image=image,
            name=name,
            description=description,
            hostname=hostname,
            wait=wait,
        )

    try:
        base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    except bazooka_exc.NotFoundError:
        return ctx.invoke(
            add_cmd,
            uuid=uuid,
            project_id=project_id,
            cores=cores,
            ram=ram,
            root_disk=root_disk,
            image=image,
            name=name,
            description=description,
            hostname=hostname,
            wait=wait,
        )

    data = {
        "cores": cores,
        "ram": ram,
        "name": name,
        "description": description,
        "disk_spec": {
            "kind": "root_disk",
            "size": root_disk,
            "image": image,
        },
    }
    if hostname is not None:
        _validate_hostname(hostname)
        data["hostname"] = hostname
    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    if not wait:
        show_data(entity)
        return None
    log = logger.ClickLogger()
    while entity["status"] != "ACTIVE":
        log.info(f"Waiting for node to be ready. Status: {entity['status']}")
        time.sleep(2)
        entity = client.get(c.NODE_COLLECTION, uuid=uuid)
    show_data(entity)
    return None


@cn_group.command("info", help=f"Show detailed information about the {ENTITY}")
@click.pass_context
@click.argument(
    "node",
    type=str,
    required=True,
    help=f"{ENTITY} UUID or name",
)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
def info_cmd(ctx: click.Context, node: str, output: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entity = base_client.get_entity(client, ENTITY_COLLECTION, node)
    show_data(entity, output=output)
    details = base_client.action_entity(
        client, ENTITY_COLLECTION, "details", entity["uuid"], invoke=False
    )
    # The details action returns the hypervisor UUID, or None if not placed yet
    if details.get("hypervisor"):
        show_data({"uuid": details["hypervisor"]}, output=output, msg="Hypervisor")


cn_group.add_command(add_cmd, aliases=["a"])
cn_group.add_command(update_cmd, aliases=["u"])
