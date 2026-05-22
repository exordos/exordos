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

import os
import typing as tp
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common import compute
from exordos.common.table import show_data

ENTITY = "ssh_key"
ENTITY_COLLECTION = c.SSH_KEY_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Target": "target",
    "User": "user",
    "Status": "status",
}

ssh_keys_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, add_clear_command=True
)


@click.command(
    "add",
    help=f"Add a new {ENTITY} to the Exordos installation, examples: `exordos secret ssh_keys add "
    f"--node 2cc70850-3df7-4234-b9c1-0e20ed3672c7 --user ubuntu --target_public_key ~/.ssh/id_rsa.pub` or "
    f"`exordos secret ssh_keys add --element dbaas --user ubuntu --target_public_key ~/.ssh/id_rsa.pub`",
)
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {ENTITY}",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=False,
    help=f"Name of the project in which to deploy the {ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    required=False,
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help=f"Description of the {ENTITY}",
)
@click.option(
    "--realm",
    default=False,
    is_flag=True,
    help="add ssh keys to all realm nodes and sets",
)
@click.option(
    "--element",
    type=str,
    required=False,
    help="element uuid or name",
)
@click.option(
    "--node",
    type=str,
    required=False,
    help="node uuid",
)
@click.option(
    "--node_set",
    type=str,
    required=False,
    help="node_set uuid",
)
@click.option(
    "--user",
    type=str,
    default=c.BOOTSTRAP_USER,
    help=f"user name of the {ENTITY}",
)
@click.option(
    "--target_public_key",
    type=str,
    required=False,
    help="key or path to it, for example: /home/user/.ssh/id_rsa.pub",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str,
    realm: bool,
    element: str | None,
    node: str | None,
    node_set: str | None,
    user: str,
    target_public_key: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    data: dict[str, tp.Any] = {
        "description": description,
        "user": user,
    }
    if uuid is not None:
        data["uuid"] = str(sys_uuid.uuid4())
    if name is not None:
        data["name"] = name

    if target_public_key is not None:
        path = os.path.expanduser(target_public_key)
        if os.path.exists(path):
            with open(path, "r") as f:
                target_public_key = f.read()
        data["target_public_key"] = target_public_key.strip()

    if not any([node, node_set, element, realm]):
        raise click.ClickException(
            "Either node or node_set or element or realm must be specified"
        )
    if realm:
        targets = compute.get_compute_targets_all(client)
    elif element is not None:
        element_data = base_client.get_entity(client, c.ELEMENT_COLLECTION, element)
        targets = compute.get_compute_targets_from_element(client, element_data)
    elif node is not None:
        target_entity = base_client.get_entity(client, c.NODE_COLLECTION, node)
        targets = [
            {
                "target": {
                    "kind": "node",
                    "node": target_entity["uuid"],
                },
                "name": target_entity["name"],
                "project_id": target_entity["project_id"],
            }
        ]
    else:
        target_entity = base_client.get_entity(client, c.SET_COLLECTION, node_set)
        targets = [
            {
                "target": {
                    "kind": "node_set",
                    "node": target_entity["uuid"],
                },
                "name": target_entity["name"],
                "project_id": target_entity["project_id"],
            }
        ]

    if project_id is None:
        project_id = targets[0]["project_id"]
    data["project_id"] = str(project_id)

    for target in targets:
        data_copy = data.copy()
        if not data_copy.get("uuid"):
            data_copy["uuid"] = str(sys_uuid.uuid4())
        if not data_copy.get("name"):
            data_copy["name"] = f"ssh_key_to_{target['name']}"
        data_copy["target"] = target["target"]
        entity = base_client.add_entity(client, ENTITY_COLLECTION, data_copy)
        click.echo(f"{ENTITY} {entity['uuid']} to target {target['name']} created")
        show_data(entity)


@click.command("update", help=f"Update {ENTITY}")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=None,
    help=f"Name of the project in which to deploy the {ENTITY}",
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
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description

    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


ssh_keys_group.add_command(add_cmd, aliases=["a"])
ssh_keys_group.add_command(update_cmd, aliases=["u"])
