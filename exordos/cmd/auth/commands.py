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


@click.group("auth", help="Authentication and current user management commands")
def auth_group():
    pass


@click.command("disable-otp", help="Disable two-factor authentication")
@click.option(
    "-p",
    "--password",
    default=None,
    type=str,
    help="Current password (optional, will be prompted if not provided)",
)
@click.pass_context
def disable_otp_cmd(ctx: click.Context, password: str | None) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    try:
        me_data = client.me()
    except Exception as exc:
        raise click.ClickException(str(exc))

    user_uuid = me_data.get("user", {}).get("uuid")
    if not user_uuid:
        raise click.ClickException("Unable to get current user UUID from token")

    if password is None:
        password = click.prompt("Enter your current password", hide_input=True)

    try:
        client.do_action(
            c.USER_COLLECTION,
            "disable_otp",
            sys_uuid.UUID(user_uuid),
            invoke=True,
            password=password,
        )
    except Exception as exc:
        raise click.ClickException(str(exc))

    click.secho(f"Two-factor authentication disabled for user {user_uuid}", fg="green")


auth_group.add_command(disable_otp_cmd)
