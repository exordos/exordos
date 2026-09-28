#    Copyright 2026 Genesis Corporation.
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
from unittest.mock import patch

import pytest
import rich_click as click

from exordos.cmd.stand.commands import snapshot_cmd
from exordos.infra.libvirt import libvirt

DOMAIN_XML = """
<domain>
  <devices>
    <disk type='block' device='disk'>
      <source dev='/dev/zvol/rpool/disks/871e0ce8' index='2'/>
    </disk>
    <disk type='block' device='disk'>
      <source dev='/dev/zvol/rpool/disks/8d9d984b' index='1'/>
    </disk>
    <disk type='file' device='disk'>
      <source file='/var/lib/libvirt/images/vm.qcow2'/>
    </disk>
  </devices>
</domain>
"""


class TestGetDomainZvols:
    def test_get_domain_zvols_returns_zvol_datasets(self) -> None:
        with patch(
            "exordos.infra.libvirt.libvirt.subprocess.check_output",
            return_value=DOMAIN_XML.encode(),
        ):
            zvols = libvirt.get_domain_zvols("vm1")

        assert zvols == ["rpool/disks/871e0ce8", "rpool/disks/8d9d984b"]


class TestCmdSnapshot:
    def test_snapshot_cmd_creates_all_snapshots_in_one_call(self) -> None:
        zvols = {"vm1": ["rpool/disks/a", "rpool/disks/b"], "vm2": ["rpool/disks/c"]}

        with (
            patch(
                "exordos.cmd.stand.commands._domains_for_backup",
                return_value=["vm2", "vm1"],
            ) as domains_for_backup,
            patch(
                "exordos.cmd.stand.commands.libvirt.get_domain_zvols",
                side_effect=zvols.__getitem__,
            ),
            patch("exordos.cmd.stand.commands.subprocess.check_call") as check_call,
        ):
            snapshot_cmd.callback(name=(), exclude_name=(), snapshot_name="snap1")

        domains_for_backup.assert_called_once_with((), (), raise_on_domain_absence=True)
        check_call.assert_called_once_with(
            [
                "sudo",
                "zfs",
                "snapshot",
                "rpool/disks/a@snap1",
                "rpool/disks/b@snap1",
                "rpool/disks/c@snap1",
            ]
        )

    def test_snapshot_cmd_skips_when_no_zvols(self) -> None:
        with (
            patch(
                "exordos.cmd.stand.commands._domains_for_backup",
                return_value=["vm1"],
            ),
            patch(
                "exordos.cmd.stand.commands.libvirt.get_domain_zvols",
                return_value=[],
            ),
            patch("exordos.cmd.stand.commands.subprocess.check_call") as check_call,
        ):
            snapshot_cmd.callback(name=(), exclude_name=(), snapshot_name=None)

        check_call.assert_not_called()

    def test_snapshot_cmd_name_and_exclude_name_conflict(self) -> None:
        with pytest.raises(click.UsageError):
            snapshot_cmd.callback(
                name=("vm1",), exclude_name=("vm2",), snapshot_name=None
            )
