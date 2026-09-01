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

from urllib.parse import urljoin

import rich_click as click

from exordos import utils
from exordos.cmd.aliases import ClickAliasedGroup
from exordos.cmd.dbaas.databases import commands as databases_commands
from exordos.cmd.dbaas.instances import commands as instances_commands
from exordos.cmd.dbaas.users import commands as users_commands
from exordos.cmd.dbaas.versions import commands as versions_commands

DBAAS_URL_PART = "/api/dbaas"


@click.group(
    "dbaas", cls=ClickAliasedGroup, help="dbaas group in the Exordos installation"
)
@click.option(
    "--dbaas-endpoint",
    default=None,
    help="Exordos dbaas API endpoint, defaults to the dbaas element behind the endpoint",
)
@click.pass_context
def dbaas_group(ctx: click.Context, dbaas_endpoint: str | None) -> None:
    # The dbaas element serves its own API, published by the core load
    # balancer next to the core API itself.
    ctx.obj.auth_data["service_endpoint"] = dbaas_endpoint or urljoin(
        utils.get_base_url(ctx.obj.auth_data.get("endpoint", "")), DBAAS_URL_PART
    )


dbaas_group.add_command(instances_commands.instances_group, aliases=["i"])
dbaas_group.add_command(databases_commands.databases_group, aliases=["d"])
dbaas_group.add_command(users_commands.users_group, aliases=["u"])
dbaas_group.add_command(versions_commands.versions_group, aliases=["v"])
