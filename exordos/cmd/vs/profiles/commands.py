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

import typing as tp
import uuid as sys_uuid

import rich_click as click
from exordos.common.table import get_table, print_table, show_data

from exordos.clients import base_client
from exordos.cmd.aliases import ClickAliasedGroup
from exordos import utils
from exordos import constants as c


ENTITY = "profile"
ENTITY_COLLECTION = c.PROFILE_COLLECTION


@click.group(
    "profiles",
    cls=ClickAliasedGroup,
    invoke_without_command=True,
    help=f"Manage {ENTITY}s in the Exordos installation",
)
def profiles_group():
    pass


@click.command("list", help=f"List {ENTITY}s")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    help=(
        "Additional filters to pass to the api. "
        "The format is 'key=value'. For example: --f "
        "parent=11111111-1111-1111-1111-11111111111 --filters status=NEW"
    ),
)
@click.pass_context
def list_cmd(ctx: click.Context, filters: tuple[str, ...]) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    filters = utils.convert_input_multiply(filters)
    entities = base_client.list_entities(client, ENTITY_COLLECTION, **filters)
    _print_entities(entities)


@click.command("show", help=f"Show {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(data)


@click.command("delete", help="Delete profile")
@click.argument(
    "uuid",
    type=str,
)
@click.pass_context
def delete_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    base_client.delete_entity(client, ENTITY_COLLECTION, uuid)


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
    if not utils.is_valid_uuid(uuid):
        entities = base_client.list_entities(client, ENTITY_COLLECTION, name=uuid)
        if entities:
            uuid = entities[0]["uuid"]
        else:
            raise click.ClickException(f"Profile with name {uuid} not found")
    base_client.action_entity(client, ENTITY_COLLECTION, "activate", uuid)


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


def _print_entities(profiles: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("ProfileType")
    table.add_column("Active")
    table.add_column("Status")

    for profile in profiles:
        table.add_row(
            profile["uuid"],
            profile["project_id"],
            profile["name"],
            profile["profile_type"],
            str(profile["active"]),
            profile["status"],
        )

    print_table(table)


profiles_group.add_command(list_cmd, aliases=["l"])
profiles_group.add_command(show_cmd, aliases=["get", "g"])
profiles_group.add_command(delete_cmd, aliases=["d"])
profiles_group.add_command(add_cmd, aliases=["a"])
