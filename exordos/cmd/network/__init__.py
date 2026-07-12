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

import rich_click as click

from exordos.cmd.aliases import ClickAliasedGroup
from exordos.cmd.network.backend_pools import commands as backend_pools_commands
from exordos.cmd.network.border import commands as border_commands
from exordos.cmd.network.lb import commands as lb_commands
from exordos.cmd.network.routes import commands as routes_commands
from exordos.cmd.network.vhosts import commands as vhosts_commands


@click.group(
    "network", cls=ClickAliasedGroup, help="network group in the Exordos installation"
)
def network_group():
    pass


network_group.add_command(lb_commands.lbs_group, aliases=["l"])
network_group.add_command(backend_pools_commands.backend_pools_group, aliases=["b"])
network_group.add_command(vhosts_commands.vhosts_group, aliases=["v"])
network_group.add_command(routes_commands.routes_group, aliases=["r"])
network_group.add_command(border_commands.borders_group, aliases=["bo"])
