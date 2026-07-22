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
import threading
from types import SimpleNamespace
from unittest import mock

from click.testing import CliRunner

from exordos.cmd.realms import commands


def test_list_cmd_fetches_realm_sources_in_parallel() -> None:
    barrier = threading.Barrier(3)
    infra = mock.Mock()
    infra.list_stands.side_effect = lambda: (barrier.wait(timeout=1), [])[1]

    with (
        mock.patch.object(commands, "get_ecosystem_client"),
        mock.patch.object(
            commands.base_client,
            "list_entities",
            side_effect=lambda *_: (barrier.wait(timeout=1), [])[1],
        ),
        mock.patch.object(
            commands.libvirt_infra,
            "LibvirtInfraDriver",
            return_value=infra,
        ),
        mock.patch.object(
            commands,
            "check_api",
            side_effect=lambda _: (barrier.wait(timeout=1), True)[1],
        ),
    ):
        result = CliRunner().invoke(
            commands.list_cmd,
            obj=SimpleNamespace(
                auth_data={},
                cfg={"realms": {"remote": {"endpoint": "http://127.0.0.1"}}},
            ),
        )

    assert result.exit_code == 0, result.output
