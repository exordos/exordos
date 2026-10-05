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

from click.testing import CliRunner

from exordos import constants as c
from exordos.cmd.secret import secret_group
from exordos.common.cmd_context import ContextObject


def _invoke(*args: str):
    return CliRunner().invoke(
        secret_group,
        list(args),
        obj=ContextObject(
            auth_data={},
            cfg_path=None,
            developer_key_path=None,
            cfg={},
            need_update=None,
        ),
    )


def _key(uuid: str, kind: str, target: str) -> dict:
    return {"uuid": uuid, "name": uuid, "target": {"kind": kind, kind: target}}


@mock.patch("exordos.cmd.secret.ssh_keys.commands.base_client")
class TestSshKeysPruneCli:
    def test_prune_cmd_deletes_keys_without_targets(self, client) -> None:
        keys = [
            _key("k-node-alive", "node", "node-alive"),
            _key("k-node-gone", "node", "node-gone"),
            _key("k-set-alive", "node_set", "set-alive"),
            _key("k-set-gone", "node_set", "set-gone"),
        ]
        client.list_entities.side_effect = lambda _client, collection: {
            c.NODE_COLLECTION: [{"uuid": "node-alive"}],
            c.SET_COLLECTION: [{"uuid": "set-alive"}],
            c.SSH_KEY_COLLECTION: keys,
        }[collection]

        result = _invoke("ssh_keys", "prune", "-y")

        assert result.exit_code == 0, result.output
        api = client.get_user_api_client.return_value
        assert client.delete_entity.call_args_list == [
            mock.call(api, c.SSH_KEY_COLLECTION, "k-node-gone"),
            mock.call(api, c.SSH_KEY_COLLECTION, "k-set-gone"),
        ]

    def test_prune_cmd_nothing_to_delete(self, client) -> None:
        client.list_entities.side_effect = lambda _client, collection: {
            c.NODE_COLLECTION: [{"uuid": "node-alive"}],
            c.SET_COLLECTION: [],
            c.SSH_KEY_COLLECTION: [_key("k", "node", "node-alive")],
        }[collection]

        result = _invoke("s", "p", "-y")

        assert result.exit_code == 0, result.output
        client.delete_entity.assert_not_called()
