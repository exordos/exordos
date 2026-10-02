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
from exordos.common.table import show_data

ENTITY = "certificate"
ENTITY_COLLECTION = c.CERTIFICATE_COLLECTION
FIELDS_MAP = {
    "UUID": "uuid",
    "Project": "project_id",
    "Name": "name",
    "Email": "email",
    "Domains": lambda x: ", ".join(x.get("domains") or []),
    "Status": "status",
}
CERTIFICATE_METHODS = ("dns_core",)

certificates_group = create_entity_group(ENTITY, ENTITY_COLLECTION, FIELDS_MAP)


@click.command("add", help="Add a new certificate to the Exordos installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the certificate",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the certificate",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_certificate",
    help="Name of the certificate",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the certificate",
)
@click.option(
    "-e",
    "--email",
    type=str,
    required=True,
    help="Email address to use for the certificate",
)
@click.option(
    "-d",
    "--domain",
    "domains",
    type=str,
    multiple=True,
    required=True,
    help="Domain of the certificate, wildcards are allowed. Can be repeated",
)
@click.option(
    "-m",
    "--method",
    type=click.Choice(CERTIFICATE_METHODS),
    default=CERTIFICATE_METHODS[0],
    show_default=True,
    help="Method (provider) to issue and manage the certificate",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
    email: str,
    domains: tuple[str, ...],
    method: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "email": email,
        "domains": list(domains),
        "method": {"kind": method},
    }
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


@click.command("update", help="Update certificate")
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
    help="Name of the project in which to deploy the certificate",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the certificate",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the certificate",
)
@click.option(
    "-e",
    "--email",
    type=str,
    default=None,
    help="Email address to use for the certificate",
)
@click.option(
    "-d",
    "--domain",
    "domains",
    type=str,
    multiple=True,
    help="Domain of the certificate, replaces the current list. Can be repeated",
)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
    email: str | None,
    domains: tuple[str, ...],
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if email is not None:
        data["email"] = email
    if domains:
        data["domains"] = list(domains)
    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


certificates_group.add_command(add_cmd, aliases=["a"])
certificates_group.add_command(update_cmd, aliases=["u"])
