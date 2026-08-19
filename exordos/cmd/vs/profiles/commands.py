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

import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import fill_table
from exordos.common.table import print_table
from exordos.common.table import show_data

ENTITY = "profile"
ENTITY_COLLECTION = c.PROFILE_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "ProfileType": "profile_type",
    "Active": "active",
    "Status": "status",
}
VARIABLE_FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Value": "value",
    "Status": "status",
}


profiles_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@profiles_group.command(
    "info", help="Show profile and variables which take their value from it"
)
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "--output",
    "-o",
    default=c.DEFAULT_TABLE_FORMAT,
    type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
    help="the output format, defaults to table",
)
@click.pass_context
def info_cmd(
    ctx: click.Context,
    uuid: str,
    output: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    profile = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(profile, output, "Profile")

    # Find variables with the profile setter bound to this profile
    variables = []
    for variable in base_client.list_entities(client, c.VARIABLE_COLLECTION):
        setter = variable.get("setter") or {}
        if setter.get("kind") != "profile":
            continue
        for item in setter.get("profiles", []):
            if str(item["profile"]) == str(profile["uuid"]):
                variables.append(
                    {
                        "uuid": variable["uuid"],
                        "name": variable["name"],
                        "value": item["value"],
                        "status": variable.get("status", ""),
                    }
                )
                break

    print_table(
        fill_table(variables, VARIABLE_FIELDS_MAP),
        output,
        "Variables in this profile",
    )


@profiles_group.command("activate", help="Activate profile")
@click.argument(
    "uuid",
    type=str,
)
@click.pass_context
def activate_profile_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    uuid = data["uuid"]
    base_client.action_entity(client, ENTITY_COLLECTION, "activate", uuid)
    click.echo(f"Profile with name {data['name']} was activated")


@click.command("add", help="Add a new profile to the Exordos installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the profile",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the profile",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="profile",
    help="Name of the profile",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the profile",
)
@click.option(
    "-t",
    "--profile_type",
    type=str,
    default="GLOBAL",
    help="Profile_type (ELEMENT, GLOBAL)",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
    profile_type: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "profile_type": profile_type,
    }
    data = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(data)


profiles_group.add_command(add_cmd, aliases=["a"])
