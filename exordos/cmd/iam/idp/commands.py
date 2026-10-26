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

import json
import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.cmd.base import tag_options
from exordos.cmd.base import tags_payload
from exordos.common.table import show_data

ENTITY = "idp"
ENTITY_COLLECTION = c.IDP_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Project": "project_id",
    "Scope": "scope",
    "Iam_client": lambda x: (x.get("iam_client") or "").split("/")[-1],
    "Status": "status",
}

idps_group = create_entity_group(
    ENTITY, ENTITY_COLLECTION, FIELDS_MAP, add_tags_command=True
)


@click.command("add", help=f"Add a new {ENTITY} to the Exordos installation")
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
    "-D",
    "--description",
    type=str,
    default="",
    help=f"Description of the {ENTITY}",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Uuid of the project",
)
@click.option(
    "-i",
    "--iam-client",
    type=click.UUID,
    required=True,
    help="Uuid of iam_client",
)
@click.option(
    "--scope",
    type=str,
    required=False,
    help="scope",
)
@click.option(
    "--nonce-required/--no-nonce-required",
    "--nonce_required",
    "nonce_required",
    default=True,
    help="Whether nonce is required",
)
@click.option(
    "--callback",
    type=str,
    required=True,
    help="JSON string for callbacks",
)
@tag_options()
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    iam_client: sys_uuid.UUID,
    scope: str | None,
    nonce_required: bool,
    callback: str,
    tags: tuple[str, ...] = (),
) -> None:
    tag_data = tags_payload(tags)
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    try:
        # Convert string to dictionary
        callback_data = json.loads(callback)
    except json.JSONDecodeError:
        click.echo(f"Error: Invalid JSON string: '{callback}'", err=True)
        return

    data = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "iam_client": f"{c.CLIENT_COLLECTION}{iam_client}",
        "nonce_required": nonce_required,
        "callback": callback_data,
    }
    if scope is not None:
        data["scope"] = scope

    data.update(tag_data)
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


idps_group.add_command(add_cmd, aliases=["a"])


@click.command("update", help=f"Update {ENTITY}")
@click.pass_context
@click.argument("uuid", type=str)
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
    "-i",
    "--iam-client",
    type=click.UUID,
    default=None,
    help="Uuid of iam_client",
)
@click.option(
    "--scope",
    type=str,
    default=None,
    help="scope",
)
@click.option(
    "--nonce-required/--no-nonce-required",
    default=None,
    help="Whether nonce is required",
)
@click.option(
    "--callback",
    type=str,
    default=None,
    help="JSON string for callbacks",
)
@tag_options(update=True)
def update_cmd(
    ctx: click.Context,
    uuid: str,
    name: str | None,
    description: str | None,
    iam_client: sys_uuid.UUID | None,
    scope: str | None,
    nonce_required: bool | None,
    callback: str | None,
    tags: tuple[str, ...] = (),
    clear_tags: bool = False,
) -> None:
    data = tags_payload(tags, clear_tags)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if iam_client is not None:
        data["iam_client"] = f"{c.CLIENT_COLLECTION}{iam_client}"
    if scope is not None:
        data["scope"] = scope
    if nonce_required is not None:
        data["nonce_required"] = nonce_required
    if callback is not None:
        try:
            data["callback"] = json.loads(callback)
        except json.JSONDecodeError:
            raise click.BadParameter(
                f"Invalid JSON string: '{callback}'", param_hint="--callback"
            )

    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


idps_group.add_command(update_cmd, aliases=["u"])


@click.command(
    "well-known",
    help=f"Show OpenID configuration (.well-known) of the {ENTITY}",
)
@click.pass_context
@click.argument("uuid", type=str)
def well_known_cmd(ctx: click.Context, uuid: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    idp_uuid = base_client._get_entity_uuid(client, ENTITY_COLLECTION, uuid)
    data = client.get(
        f"{ENTITY_COLLECTION}{idp_uuid}/.well-known/", "openid-configuration"
    )
    click.echo(json.dumps(data, indent=2))


idps_group.add_command(well_known_cmd, aliases=["wk"])
