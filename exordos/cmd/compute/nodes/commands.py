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
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.compute import common as compute_common
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
    "Disk type": compute_common.extract_disk_type_from_entity,
    "Image": compute_common.extract_image_from_entity,
    "Status": "status",
}

cn_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP, "cn")


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
    "--disk-type",
    type=click.Choice(["qcow2", "rawstor"]),
    default="qcow2",
    show_default=True,
    help="Backend to store the root disk on",
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
    disk_type: str,
    name: str,
    description: str,
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
            "disk_kind": {"kind": disk_type},
        },
    }
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
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
    "--disk-type",
    type=click.Choice(["qcow2", "rawstor"]),
    default="qcow2",
    show_default=True,
    help="Backend to store the root disk on",
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
    disk_type: str,
    name: str,
    description: str,
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
            disk_type=disk_type,
            name=name,
            description=description,
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
            disk_type=disk_type,
            name=name,
            description=description,
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
            "disk_kind": {"kind": disk_type},
        },
    }
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
    if "hypervisor" in details:
        show_data(details["hypervisor"], output=output, msg="Hypervisor")


cn_group.add_command(add_cmd, aliases=["a"])
cn_group.add_command(update_cmd, aliases=["u"])
