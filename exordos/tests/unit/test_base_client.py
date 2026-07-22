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
from unittest.mock import MagicMock
from unittest.mock import patch

from bazooka import exceptions as bazooka_exc

from exordos.clients import base_client


class TestRegisterAgentAndWriteKey:
    def test_registers_the_agent_and_writes_its_key(self, tmp_path) -> None:
        key_path = str(tmp_path / "private_key")
        fake_client = MagicMock()
        fake_client.do_action.return_value = {"key": "s3cr3t-key=="}

        with patch.object(base_client, "write_agent_private_key") as write_key_mock:
            base_client.register_agent_and_write_key(
                fake_client, "8d10a674-node-uuid", key_path
            )

        fake_client.create.assert_called_once_with(
            base_client.c.AGENT_COLLECTION,
            data={
                "uuid": "8d10a674-node-uuid",
                "name": "universal_agent_8d10a674",
                "node": "8d10a674-node-uuid",
                "capabilities": {"capabilities": []},
                "facts": {"facts": []},
            },
        )
        fake_client.do_action.assert_called_once_with(
            base_client.c.AGENT_COLLECTION,
            "issue_key",
            "8d10a674-node-uuid",
            invoke=True,
        )
        write_key_mock.assert_called_once_with("s3cr3t-key==", key_path)

    def test_tolerates_an_already_registered_agent(self, tmp_path) -> None:
        key_path = str(tmp_path / "private_key")
        fake_client = MagicMock()
        fake_client.create.side_effect = bazooka_exc.ConflictError(cause=MagicMock())
        fake_client.do_action.return_value = {"key": "s3cr3t-key=="}

        with patch.object(base_client, "write_agent_private_key") as write_key_mock:
            base_client.register_agent_and_write_key(
                fake_client, "node-uuid", key_path
            )

        write_key_mock.assert_called_once_with("s3cr3t-key==", key_path)
