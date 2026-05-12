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
from exordos.cmd.em.elements import commands as elements_commands
from exordos.cmd.em.exports import commands as exports_commands
from exordos.cmd.em.imports import commands as imports_commands
from exordos.cmd.em.manifests import commands as manifests_commands
from exordos.cmd.em.resources import commands as resources_commands
from exordos.cmd.em.services import commands as services_commands


@click.group("em", cls=ClickAliasedGroup, help="em group in the Exordos installation")
def em_group():
    pass


em_group.add_command(elements_commands.ee_group, aliases=["e", "elements"])
em_group.add_command(exports_commands.exports_group)
em_group.add_command(imports_commands.imports_group, aliases=["i"])
em_group.add_command(manifests_commands.manifests_group, aliases=["m"])
em_group.add_command(resources_commands.resources_group, aliases=["r"])
em_group.add_command(services_commands.services_group, aliases=["s"])
