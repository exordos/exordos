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

import questionary
from rich.live import Live
import rich_click as click

from exordos import constants as c
from exordos import utils
from exordos.clients import base_client
from exordos.cmd.aliases import ClickAliasedGroup
from exordos.common.table import fill_table
from exordos.common.table import print_table
from exordos.common.table import show_data


def add_dynamic_parents(parents: list[str] | None = None):
    def decorator(f):
        if parents is None:
            return f
        for parent in parents:
            f = click.option(
                f"--{parent}-uuid",
                type=click.UUID,
                required=True,
            )(f)
        return f

    return decorator


def create_entity_group(
    entity_name: str,
    entity_collection: str,
    fields_map: dict,
    group_name: str | None = None,
    add_list_command: bool = True,
    add_show_command: bool = True,
    add_delete_command: bool = True,
    add_clear_command: bool = False,
    parents: list[str] | None = None,
) -> ClickAliasedGroup:
    """Create a universal click group for entity management."""

    @click.group(
        group_name or f"{entity_name}s",
        cls=ClickAliasedGroup,
        invoke_without_command=True,
        help=f"Manage {entity_name}s in the Exordos installation",
    )
    def entity_group():
        pass

    # List command
    if add_list_command:

        @click.command("list", help=f"List {entity_name}s")
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
        @click.option(
            "--output",
            "-o",
            default=c.DEFAULT_TABLE_FORMAT,
            type=click.Choice(c.TABLE_FORMATS, case_sensitive=False),
            help="the output format, defaults to table",
        )
        @click.option(
            "-w",
            "--watch",
            show_default=True,
            is_flag=True,
            help=f"Watch the list of {entity_name}s",
        )
        @click.option(
            "--interval",
            type=click.FloatRange(min=0.1),
            default=0.5,
            help="Refresh interval in seconds.",
        )
        @add_dynamic_parents(parents)
        @click.pass_context
        def list_cmd(
            ctx: click.Context,
            filters: tuple[str, ...],
            output: str,
            watch: bool,
            interval: float,
            **kwargs,
        ) -> None:
            client = base_client.get_user_api_client(ctx.obj.auth_data)
            filters = utils.convert_input_multiply(filters)
            if watch:
                with Live(refresh_per_second=4) as live:
                    while True:
                        entities = base_client.list_entities(
                            client, entity_collection.format(**kwargs), **filters
                        )
                        live.update(fill_table(entities, fields_map), refresh=True)
                        time.sleep(interval)
            else:
                entities = base_client.list_entities(
                    client, entity_collection.format(**kwargs), **filters
                )
                print_table(fill_table(entities, fields_map), output)

        entity_group.add_command(list_cmd, aliases=["l"])

    # Show command
    if add_show_command:

        @click.command("show", help=f"Show {entity_name}")
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
        @add_dynamic_parents(parents)
        @click.pass_context
        def show_cmd(
            ctx: click.Context,
            uuid: str,
            output: str,
            **kwargs,
        ) -> None:
            client = base_client.get_user_api_client(ctx.obj.auth_data)
            data = base_client.get_entity(
                client, entity_collection.format(**kwargs), uuid
            )
            show_data(data, output)

        entity_group.add_command(show_cmd, aliases=["get", "g"])

    # Delete command
    if add_delete_command:

        @click.command("delete", help=f"Delete {entity_name}")
        @click.argument(
            "uuid",
            type=str,
            required=True,
        )
        @add_dynamic_parents(parents)
        @click.pass_context
        def delete_cmd(
            ctx: click.Context,
            uuid: str,
            **kwargs,
        ) -> None:
            client = base_client.get_user_api_client(ctx.obj.auth_data)
            base_client.delete_entity(client, entity_collection.format(**kwargs), uuid)
            click.echo(f"{entity_name} {uuid} deleted")

        entity_group.add_command(delete_cmd, aliases=["d"])

    if add_clear_command:

        @click.command("clear", help=f"Delete all {entity_name}s")
        @click.option(
            "--y", "-y", help="Automatically answer yes for all questions", is_flag=True
        )
        @click.pass_context
        def clear_cmd(ctx: click.Context, y: bool) -> None:
            client = base_client.get_user_api_client(ctx.obj.auth_data)
            entities = base_client.list_entities(client, entity_collection)
            for entity in entities:
                if (
                    y
                    or questionary.confirm(
                        f"Delete {entity_name} {entity['uuid']} ({entity.get('name', '')})?"
                    ).ask()
                ):
                    base_client.delete_entity(client, entity_collection, entity["uuid"])
                    click.echo(f"{entity_name} {entity['uuid']} deleted")

        entity_group.add_command(clear_cmd, aliases=["c"])

    return entity_group
