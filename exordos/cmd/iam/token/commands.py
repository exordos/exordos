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

import uuid as sys_uuid

import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

ENTITY = "token"
ENTITY_COLLECTION = c.TOKEN_COLLECTION
SECONDS_IN_DAY = 24 * 60 * 60
FIELDS_MAP = {
    "UUID": "uuid",
    "User": "user",
    "Client": "iam_client",
    # `project` is left out: the API omits it for a token with no scope,
    # and the table reads the columns off the first row only
    "Scope": "scope",
    "Expiration": "expiration_at",
    "Renews": "auto_renew",
}


tokens_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command(
    "add",
    help=(
        f"Issue a new {ENTITY}. The signed token is in the answer to this "
        "command and nowhere else: copy it now, a read never returns it"
    ),
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
    "--user",
    type=click.UUID,
    default=None,
    help=(
        f"UUID of the user the {ENTITY} authenticates. Defaults to the "
        "account running the command; naming another user takes the "
        "iam.token.create_all permission"
    ),
)
@click.option(
    "--iam-client",
    type=click.UUID,
    default=c.DEFAULT_CLIENT_UUID,
    show_default=True,
    help=f"UUID of the IAM client that signs the {ENTITY}",
)
@click.option(
    "-s",
    "--scope",
    type=str,
    default=None,
    help="Scope of the token, e.g. 'project:<uuid>'",
)
@click.option(
    "-d",
    "--days",
    type=click.IntRange(min=1),
    default=30,
    show_default=True,
    help=f"How many days the {ENTITY} lives before it is spent",
)
@click.option(
    "--no-expire",
    is_flag=True,
    default=False,
    help=(
        "Keep the token alive instead: the platform renews it before it "
        "expires, for as long as the token exists"
    ),
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    user: sys_uuid.UUID | None,
    iam_client: sys_uuid.UUID,
    scope: str | None,
    days: int,
    no_expire: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "iam_client": f"{c.CLIENT_COLLECTION}{iam_client}",
        "expiration_delta": days * SECONDS_IN_DAY,
        "auto_renew": no_expire,
    }
    if user is not None:
        data["user"] = f"{c.USER_COLLECTION}{user}"
    if scope is not None:
        data["scope"] = scope

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


tokens_group.add_command(add_cmd, aliases=["a"])
