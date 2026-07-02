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
from exordos.cmd.ua.agents import commands as agents_commands
from exordos.cmd.ua.resources import commands as resources_commands
from exordos.cmd.ua.target_resources import commands as target_resources_commands


@click.group("ua", cls=ClickAliasedGroup, help="ua group in the Exordos installation")
def ua_group():
    pass


ua_group.add_command(agents_commands.agents_group, aliases=["a"])
ua_group.add_command(resources_commands.resources_group, aliases=["r"])
ua_group.add_command(target_resources_commands.target_resources_group, aliases=["t"])
