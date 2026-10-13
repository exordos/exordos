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
from __future__ import annotations

from unittest import mock
import uuid

from click.testing import CliRunner
import pytest

from exordos.cmd.iam import iam_group
from exordos.cmd.iam.user import commands
from exordos.common.cmd_context import ContextObject


@pytest.mark.parametrize("interactive", [False, True])
def test_change_password_sends_user_and_passwords(interactive: bool) -> None:
    user = "00000000-0000-0000-0000-000000000000"
    args = ["u", "change_password", user, "-o", "old-password"]
    if not interactive:
        args.extend(["-n", "new-password"])

    with (
        mock.patch.object(commands, "base_client") as client,
        mock.patch("questionary.password") as password,
    ):
        password.return_value.ask.return_value = "new-password"
        result = CliRunner().invoke(
            iam_group,
            args,
            obj=ContextObject(
                auth_data={},
                cfg_path=None,
                developer_key_path=None,
                cfg={},
                need_update=None,
            ),
        )

        assert result.exit_code == 0, result.exception
        client.action_entity.assert_called_once_with(
            client.get_user_api_client.return_value,
            commands.ENTITY_COLLECTION,
            "change_password",
            uuid.UUID(user),
            old_password="old-password",
            new_password="new-password",
        )
        assert f"Password changed for user {user}" in result.output
        if interactive:
            password.assert_called_once_with(f"Enter new_password for user {user}:")
        else:
            password.assert_not_called()
