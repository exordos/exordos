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
from exordos.cmd.dns.domains import commands as domains_commands
from exordos.cmd.dns.records import commands as records_commands


@click.group("dns", cls=ClickAliasedGroup, help="dns group in the Exordos installation")
def dns_group():
    pass


dns_group.add_command(domains_commands.domains_group, aliases=["d"])
dns_group.add_command(records_commands.records_group, aliases=["r"])
