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
import uuid as sys_uuid
from unittest.mock import patch

from click.testing import CliRunner

from exordos.cmd.compute import common as compute_common
from exordos.cmd.compute.nodes import commands as nodes_commands
from exordos.common.cmd_context import ContextObject


def _obj() -> ContextObject:
    return ContextObject(
        auth_data={"endpoint": "http://10.20.0.2/api/core"},
        cfg_path=None,
        developer_key_path=None,
        cfg={},
        need_update=None,
    )


class TestAddCmdDiskSpec:
    """`--disk-type` (disk_kind) was replaced by --speed/--ephemeral,
    matching RootDiskSpec's real speed/ephemeral fields directly.
    """

    def test_defaults_to_warm_and_ephemeral(self) -> None:
        runner = CliRunner()
        with (
            patch.object(nodes_commands.base_client, "get_user_api_client"),
            patch.object(nodes_commands.base_client, "add_entity") as add_mock,
        ):
            add_mock.return_value = {"status": "NEW"}
            result = runner.invoke(
                nodes_commands.add_cmd,
                [
                    "--project-id",
                    str(sys_uuid.uuid4()),
                    "--image",
                    "ubuntu_24.04",
                ],
                obj=_obj(),
            )

        assert result.exit_code == 0, result.output
        data = add_mock.call_args.args[2]
        assert data["disk_spec"]["speed"] == "WARM"
        assert data["disk_spec"]["ephemeral"] is True
        assert "disk_kind" not in data["disk_spec"]

    def test_speed_and_ephemeral_are_forwarded(self) -> None:
        runner = CliRunner()
        with (
            patch.object(nodes_commands.base_client, "get_user_api_client"),
            patch.object(nodes_commands.base_client, "add_entity") as add_mock,
        ):
            add_mock.return_value = {"status": "NEW"}
            result = runner.invoke(
                nodes_commands.add_cmd,
                [
                    "--project-id",
                    str(sys_uuid.uuid4()),
                    "--image",
                    "ubuntu_24.04",
                    "--speed",
                    "HOT",
                    "--ephemeral",
                ],
                obj=_obj(),
            )

        assert result.exit_code == 0, result.output
        data = add_mock.call_args.args[2]
        assert data["disk_spec"]["speed"] == "HOT"
        assert data["disk_spec"]["ephemeral"] is True


class TestExtractDiskSpeedEphemeralFromEntity:
    def test_root_disk_kind(self) -> None:
        entity = {"disk_spec": {"kind": "root_disk", "speed": "HOT", "ephemeral": True}}

        assert compute_common.extract_disk_speed_from_entity(entity) == "HOT"
        assert compute_common.extract_disk_ephemeral_from_entity(entity) is True

    def test_disks_kind_uses_the_first_disk(self) -> None:
        entity = {
            "disk_spec": {
                "kind": "disks",
                "disks": [{"speed": "COLD", "ephemeral": False}],
            }
        }

        assert compute_common.extract_disk_speed_from_entity(entity) == "COLD"
        assert compute_common.extract_disk_ephemeral_from_entity(entity) is False

    def test_missing_disk_spec_is_unknown(self) -> None:
        assert compute_common.extract_disk_speed_from_entity({}) == "Unknown"
        assert compute_common.extract_disk_ephemeral_from_entity({}) == "Unknown"
