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

import questionary
import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "user"
ENTITY_COLLECTION = c.USER_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Username": "username",
    "First Name": lambda x: x.get("first_name", ""),
    "Last Name": lambda x: x.get("last_name", ""),
    "Email": "email",
    "Status": "status",
}

users_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command("add", help=f"Add a new {ENTITY}")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=f"test_{ENTITY}",
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-p",
    "--password",
    type=str,
    required=False,
    help=f"Password of the {ENTITY}. If not provided, will be asked interactively",
    hide_input=True,
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help=f"Description of the {ENTITY}",
)
@click.option(
    "--first_name",
    type=str,
    required=False,
)
@click.option(
    "--last_name",
    type=str,
    required=False,
)
@click.option(
    "--surname",
    type=str,
    required=False,
)
@click.option(
    "--phone",
    type=str,
    required=False,
)
@click.option(
    "--email",
    type=str,
    required=True,
)
@click.option(
    "--email_verified",
    type=bool,
    is_flag=True,
    default=False,
)
@click.option(
    "--confirmation_code",
    type=str,
    required=False,
)
@click.option(
    "--confirmation_code_made_at",
    type=str,
    required=False,
)
@click.option(
    "--otp_secret",
    type=str,
    required=False,
)
@click.option(
    "--otp_enabled",
    type=bool,
    is_flag=True,
    default=False,
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    password: str | None,
    description: str,
    first_name: str | None,
    last_name: str | None,
    surname: str | None,
    phone: str | None,
    email: str | None,
    email_verified: bool,
    confirmation_code: str | None,
    confirmation_code_made_at: str | None,
    otp_secret: str | None,
    otp_enabled: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "username": name,
        "password": password
        or questionary.password(f"Enter password for {ENTITY} {name}:").ask(),
        "description": description,
        "email": email,
        "email_verified": email_verified,
        "otp_enabled": otp_enabled,
    }

    if first_name is not None:
        data["first_name"] = first_name
    if last_name is not None:
        data["last_name"] = last_name
    if surname is not None:
        data["surname"] = surname
    if phone is not None:
        data["phone"] = phone
    if confirmation_code is not None:
        data["confirmation_code"] = confirmation_code
    if confirmation_code_made_at is not None:
        data["confirmation_code_made_at"] = confirmation_code_made_at
    if otp_secret is not None:
        data["otp_secret"] = otp_secret

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


@users_group.command("change_password", help=f"Change password of the {ENTITY}")
@click.pass_context
@click.argument(
    "user",
    type=str,
    required=True,
    help=f"{ENTITY} UUID or username",
)
@click.option(
    "-o",
    "--old-password",
    type=str,
    required=True,
    help=f"Old password of the {ENTITY}",
)
@click.option(
    "-n",
    "--new-password",
    type=str,
    required=False,
    help=f"New password of the {ENTITY}. If not provided, will be asked interactively",
)
def change_password_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    old_password: str,
    new_password: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    data = {
        "old_password": old_password,
        "new_password": new_password
        or questionary.password(f"Enter new_password for {ENTITY} {uuid}:").ask(),
    }

    base_client.action_entity(
        client, ENTITY_COLLECTION, "change_password", uuid, **data
    )
    click.echo(f"Password changed for {ENTITY} {uuid}")


users_group.add_command(add_cmd, aliases=["a"])
