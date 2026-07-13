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
from exordos.cmd.quota.limit import commands as limits_commands
from exordos.cmd.quota.reservation import commands as reservations_commands


@click.group(
    "quota", cls=ClickAliasedGroup, help="quota group in the Exordos installation"
)
def quota_group():
    pass


quota_group.add_command(limits_commands.limits_group, aliases=["l"])
quota_group.add_command(reservations_commands.reservations_group, aliases=["r"])
