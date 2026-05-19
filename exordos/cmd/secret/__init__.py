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
from exordos.cmd.secret.certificate import commands as certificate_commands
from exordos.cmd.secret.passwords import commands as password_commands
from exordos.cmd.secret.rsa_keys import commands as rsa_keys_commands
from exordos.cmd.secret.ssh_keys import commands as ssh_keys_commands


@click.group(
    "secret", cls=ClickAliasedGroup, help="Secret group in the Exordos installation"
)
def secret_group():
    pass


secret_group.add_command(certificate_commands.certificates_group, aliases=["c"])  # noqa
secret_group.add_command(password_commands.passwords_group, aliases=["p"])  # noqa
secret_group.add_command(rsa_keys_commands.rsa_keys_group, aliases=["r"])  # noqa
secret_group.add_command(ssh_keys_commands.ssh_keys_group, aliases=["s"])  # noqa
