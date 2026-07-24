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

import os
import typing as tp
import uuid as sys_uuid

from bazooka import Client
from bazooka import exceptions as bazooka_exc
import certifi
import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base as http_client
from exordos.common.crypto import write_agent_private_key

os.environ["SSL_CERT_FILE"] = certifi.where()
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 5


def get_user_api_client(
    auth_data: dict,
    timeout: tp.Tuple[int, int] | None = None,
) -> http_client.CollectionBaseClient:
    bazooka_client = Client(
        default_timeout=timeout or (CONNECT_TIMEOUT, READ_TIMEOUT),
    )
    # Use provided realm or extract from auth_data
    auth = http_client.CoreIamAuthenticator(
        base_url=auth_data["endpoint"],
        username=auth_data.get("username", auth_data.get("user")),
        login=auth_data.get("login"),
        password=auth_data.get("password"),
        access_token=auth_data.get("access_token"),
        refresh_token=auth_data.get("refresh_token"),
        scope=auth_data.get("scope"),
        ttl=auth_data.get("ttl"),
        refresh_ttl=auth_data.get("refresh_ttl"),
        http_client=bazooka_client,
        password_prompt=auth_data.get("password_prompt"),
        otp_prompt=auth_data.get("otp_prompt"),
        realm=auth_data.get("realm"),
    )
    client = http_client.CollectionBaseClient(
        base_url=auth_data["endpoint"],
        auth=auth,
        http_client=bazooka_client,
    )
    return client


def _get_entity_uuid(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid_or_name: sys_uuid.UUID | str,
) -> sys_uuid.UUID | str:
    if not utils.is_valid_uuid(entity_uuid_or_name):
        entities = list_entities(client, collection, name=entity_uuid_or_name)
        if entities:
            if len(entities) > 1:
                raise click.ClickException(
                    f"Multiple entities ({collection}) with name {entity_uuid_or_name} found"
                )
            return entities[0]["uuid"]
        else:
            raise click.ClickException(
                f"entity ({collection}) with name {entity_uuid_or_name} not found"
            )
    return entity_uuid_or_name


def list_entities(
    client: http_client.CollectionBaseClient, collection: str, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(collection, **filters)


def get_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid_or_name: sys_uuid.UUID | str,
):
    if not utils.is_valid_uuid(entity_uuid_or_name):
        entities = list_entities(client, collection, name=entity_uuid_or_name)
        if entities:
            if len(entities) > 1:
                raise click.ClickException(
                    f"Multiple entities ({collection}) with name {entity_uuid_or_name} found"
                )
            return entities[0]
        else:
            raise click.ClickException(
                f"entity ({collection}) with name {entity_uuid_or_name} not found"
            )
    return client.get(collection, uuid=entity_uuid_or_name)


def add_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    data: dict[str, tp.Any],
    handle_conflict_error: bool = True,
) -> dict[str, tp.Any]:
    try:
        entity = client.create(collection, data=data)
    except bazooka_exc.ConflictError:
        if handle_conflict_error:
            raise click.ClickException(f"Already exists: {data}")
        raise
    return entity


def update_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid_or_name: sys_uuid.UUID | str,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    return client.update(
        collection, _get_entity_uuid(client, collection, entity_uuid_or_name), **data
    )


def delete_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid_or_name: sys_uuid.UUID | str,
) -> None:
    client.delete(
        collection, uuid=_get_entity_uuid(client, collection, entity_uuid_or_name)
    )


def action_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    action: str,
    uuid: sys_uuid.UUID | str,
    invoke: bool = True,
    **kwargs,
) -> None:
    try:
        client.do_action(collection, uuid=uuid, name=action, invoke=invoke, **kwargs)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"UUID {uuid} not found")


def register_agent_and_write_key(
    client: http_client.CollectionBaseClient,
    node_uuid: str,
    key_path: str,
    agent_uuid: str | None = None,
    capabilities: list[str] | None = None,
) -> None:
    """Register this node's universal agent with Core (if not already)
    and write its node encryption key to disk.

    Registering ahead of the agent's own first run lets this fetch the
    key via the `issue_key` action right after - the agent daemon's own
    self-registration later just updates this same record instead of
    conflicting with it.

    `agent_uuid` defaults to `node_uuid`, matching the standard universal
    agent's own default (`UniversalAgent.from_system_uuid()`), which is
    also a node itself. A custom agent_uuid is only needed for an agent
    that isn't the node's own standard agent.
    """
    agent_uuid = agent_uuid or node_uuid

    try:
        client.create(
            c.AGENT_COLLECTION,
            data={
                "uuid": agent_uuid,
                "name": f"universal_agent_{agent_uuid[:8]}",
                "node": node_uuid,
                "capabilities": {"capabilities": capabilities or []},
                "facts": {"facts": []},
            },
        )
    except bazooka_exc.ConflictError:
        pass

    private_key_base64 = client.do_action(
        c.AGENT_COLLECTION, "issue_key", agent_uuid, invoke=True
    )["key"]
    write_agent_private_key(private_key_base64, key_path)


def add_fields_to_url(
    collection: str,
    fields: tuple[str, ...],
) -> str:
    if not fields:
        return collection
    fields_query = "&".join(f"fields={f}" for f in fields)
    separator = "&" if "?" in collection else "?"
    collection = f"{collection}{separator}{fields_query}"
    return collection
