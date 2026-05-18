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

ENTITY = "set"
ENTITY_COLLECTION = c.SET_COLLECTION


FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Cores": "cores",
    "RAM": "ram",
    "Disks": compute_common.extract_disks_from_entity,
    "Image": compute_common.extract_image_from_entity,
    "NodeType": "node_type",
    "Status": "status",
}


sets_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command("add", help="Add a new set to the Exordos installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the set",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="UUID of the project in which to deploy the set",
)
@click.option(
    "-c",
    "--cores",
    type=int,
    default=1,
    show_default=True,
    help="Number of cores to allocate for each node in the set",
)
@click.option(
    "-r",
    "--ram",
    type=int,
    default=1024,
    show_default=True,
    help="Amount of RAM in Mb to allocate for each node in the set",
)
@click.option(
    "-d",
    "--root-disk",
    type=int,
    default=10,
    show_default=True,
    help="Number of GiB of root disk to allocate for each node in the set",
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
    default="set",
    help="Name of the set",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the set",
)
@click.option(
    "--replicas",
    type=int,
    default=1,
    show_default=True,
    help="Number of replicas (nodes) in the set",
)
@click.option(
    "--wait",
    type=bool,
    is_flag=True,
    default=False,
    help="Wait until the set is active",
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
    replicas: int,
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
        "replicas": replicas,
        "disk_spec": {
            "kind": "root_disk",
            "size": root_disk,
            "image": image,
        },
    }
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    if not wait:
        show_data(entity)
        return
    while entity["status"] != "ACTIVE":
        log.info(f"Waiting for set to be ready. Status: {entity['status']}")
        time.sleep(2)
        entity = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(entity)


@click.command("update", help="Update an existing set")
@click.pass_context
@click.option(
    "-u",
    "--uuid_or_name",
    type=str,
    required=True,
    help="UUID or name of the set to update",
)
@click.option(
    "-c",
    "--cores",
    type=int,
    default=None,
    help="Number of cores to allocate for the set",
)
@click.option(
    "-r",
    "--ram",
    type=int,
    default=None,
    help="Amount of RAM in Mb to allocate for the set",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the set",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the set",
)
@click.option(
    "-d",
    "--root-disk",
    type=int,
    default=None,
    help="Number of GiB of root disk to allocate for the set",
)
@click.option(
    "-i",
    "--image",
    type=str,
    default=None,
    help="Name of the image to deploy",
)
def update_cmd(
    ctx: click.Context,
    uuid_or_name: str,
    cores: int | None,
    ram: int | None,
    name: str | None,
    description: str | None,
    root_disk: int | None,
    image: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    try:
        entity = base_client.get_entity(client, ENTITY_COLLECTION, uuid_or_name)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"Set with UUID or name {uuid_or_name} not found")

    update_data = {}
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
    show_data(entity)


sets_group.add_command(add_cmd, aliases=["a"])
sets_group.add_command(update_cmd, aliases=["u"])
