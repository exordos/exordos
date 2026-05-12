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
from exordos.cmd.vs.profiles import commands as profiles_commands
from exordos.cmd.vs.values import commands as values_commands
from exordos.cmd.vs.vars import commands as vars_commands


@click.group("vs", cls=ClickAliasedGroup, help="vs group in the Exordos installation")
def vs_group():
    pass


vs_group.add_command(profiles_commands.profiles_group)
vs_group.add_command(values_commands.values_group)
vs_group.add_command(vars_commands.vv_group, aliases=["v", "variables", "vars"])
