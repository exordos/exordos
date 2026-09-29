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

from exordos.cmd.network import network_group
from exordos.common.cmd_context import ContextObject

UUID = "11111111-1111-1111-1111-111111111111"
PROJECT_ID = "22222222-2222-2222-2222-222222222222"
LB_UUID = "33333333-3333-3333-3333-333333333333"
VHOST_UUID = "44444444-4444-4444-4444-444444444444"
POOL_UUID = "55555555-5555-5555-5555-555555555555"
VHOST_URL = f"/v1/network/lb/{LB_UUID}/vhosts/"
ROUTE_URL = f"/v1/network/lb/{LB_UUID}/vhosts/{VHOST_UUID}/routes/"


def _invoke(*args: str):
    return CliRunner().invoke(
        network_group,
        list(args),
        obj=ContextObject(
            auth_data={},
            cfg_path=None,
            developer_key_path=None,
            cfg={},
            need_update=None,
        ),
    )


@mock.patch("exordos.cmd.network.vhosts.commands.show_data")
@mock.patch("exordos.cmd.network.vhosts.commands.base_client")
class TestVhostsCli:
    def test_add_cmd_http(self, client, _show) -> None:
        result = _invoke(
            "vhosts",
            "create",
            "-u",
            UUID,
            "-p",
            PROJECT_ID,
            "--lb-uuid",
            LB_UUID,
            "-n",
            "web",
            "--domain",
            "a.example.com",
            "--domain",
            "b.example.com",
        )

        assert result.exit_code == 0, result.output
        client.add_entity.assert_called_once_with(
            client.get_user_api_client.return_value,
            VHOST_URL,
            {
                "uuid": UUID,
                "project_id": PROJECT_ID,
                "name": "web",
                "description": "",
                "protocol": "http",
                "port": 80,
                "domains": ["a.example.com", "b.example.com"],
                "cert": None,
                "proxy_protocol_from": None,
                "enabled": True,
            },
        )

    def test_add_cmd_https_reads_cert_files(self, client, _show, tmp_path) -> None:
        crt = tmp_path / "tls.crt"
        key = tmp_path / "tls.key"
        crt.write_text("CRT")
        key.write_text("KEY")

        result = _invoke(
            "vhosts",
            "add",
            "-p",
            PROJECT_ID,
            "--lb-uuid",
            LB_UUID,
            "--protocol",
            "https",
            "--port",
            "443",
            "--domain",
            "example.com",
            "--cert",
            str(crt),
            "--key",
            str(key),
        )

        assert result.exit_code == 0, result.output
        data = client.add_entity.call_args.args[2]
        assert data["cert"] == {"kind": "raw", "crt": "CRT", "key": "KEY"}
        assert data["port"] == 443

    def test_add_cmd_cert_without_key(self, client, _show, tmp_path) -> None:
        crt = tmp_path / "tls.crt"
        crt.write_text("CRT")

        result = _invoke(
            "vhosts", "add", "-p", PROJECT_ID, "--lb-uuid", LB_UUID, "--cert", str(crt)
        )

        assert result.exit_code != 0
        assert "Both --cert and --key" in result.output
        client.add_entity.assert_not_called()

    def test_update_cmd_sends_only_given_fields(self, client, _show) -> None:
        result = _invoke(
            "vhosts",
            "update",
            UUID,
            "--lb-uuid",
            LB_UUID,
            "--port",
            "8080",
            "--disabled",
        )

        assert result.exit_code == 0, result.output
        client.update_entity.assert_called_once_with(
            client.get_user_api_client.return_value,
            VHOST_URL,
            UUID,
            {"port": 8080, "enabled": False},
        )


@mock.patch("exordos.cmd.network.routes.commands.show_data")
@mock.patch("exordos.cmd.network.routes.commands.base_client")
class TestRoutesCli:
    def test_add_cmd_backend_pool(self, client, _show) -> None:
        result = _invoke(
            "routes",
            "create",
            "-u",
            UUID,
            "-p",
            PROJECT_ID,
            "--lb-uuid",
            LB_UUID,
            "--vhost-uuid",
            VHOST_UUID,
            "--pool",
            POOL_UUID,
            "--value",
            "/api",
            "--allowed-ip",
            "10.0.0.0/8",
        )

        assert result.exit_code == 0, result.output
        client.add_entity.assert_called_once_with(
            client.get_user_api_client.return_value,
            ROUTE_URL,
            {
                "uuid": UUID,
                "project_id": PROJECT_ID,
                "name": "",
                "description": "",
                "enabled": True,
                "condition": {
                    "kind": "prefix",
                    "value": "/api",
                    "allowed_ips": ["10.0.0.0/8"],
                    "actions": [
                        {
                            "kind": "backend",
                            "pool": POOL_UUID,
                            "protocol": {"kind": "http"},
                        }
                    ],
                },
            },
        )

    def test_add_cmd_raw_kind(self, client, _show) -> None:
        result = _invoke(
            "routes",
            "add",
            "-p",
            PROJECT_ID,
            "--lb-uuid",
            LB_UUID,
            "--vhost-uuid",
            VHOST_UUID,
            "--kind",
            "raw",
            "--pool",
            POOL_UUID,
        )

        assert result.exit_code == 0, result.output
        assert client.add_entity.call_args.args[2]["condition"] == {
            "kind": "raw",
            "actions": [{"kind": "backend", "pool": POOL_UUID}],
        }

    def test_add_cmd_condition_json(self, client, _show) -> None:
        condition = {
            "kind": "exact",
            "value": "/",
            "actions": [{"kind": "redirect", "url": "https://example.com"}],
        }

        result = _invoke(
            "routes",
            "add",
            "-p",
            PROJECT_ID,
            "--lb-uuid",
            LB_UUID,
            "--vhost-uuid",
            VHOST_UUID,
            "--condition",
            '{"kind": "exact", "value": "/", "actions": '
            '[{"kind": "redirect", "url": "https://example.com"}]}',
        )

        assert result.exit_code == 0, result.output
        assert client.add_entity.call_args.args[2]["condition"] == condition

    def test_add_cmd_without_condition(self, client, _show) -> None:
        result = _invoke(
            "routes",
            "add",
            "-p",
            PROJECT_ID,
            "--lb-uuid",
            LB_UUID,
            "--vhost-uuid",
            VHOST_UUID,
        )

        assert result.exit_code != 0
        assert "Either --condition or --pool" in result.output
        client.add_entity.assert_not_called()

    def test_update_cmd_keeps_condition(self, client, _show) -> None:
        result = _invoke(
            "routes",
            "update",
            UUID,
            "--lb-uuid",
            LB_UUID,
            "--vhost-uuid",
            VHOST_UUID,
            "-n",
            "renamed",
        )

        assert result.exit_code == 0, result.output
        client.update_entity.assert_called_once_with(
            client.get_user_api_client.return_value,
            ROUTE_URL,
            UUID,
            {"name": "renamed"},
        )

    def test_update_cmd_replaces_condition(self, client, _show) -> None:
        result = _invoke(
            "routes",
            "update",
            UUID,
            "--lb-uuid",
            LB_UUID,
            "--vhost-uuid",
            VHOST_UUID,
            "--pool",
            POOL_UUID,
            "--backend-protocol",
            "https",
        )

        assert result.exit_code == 0, result.output
        assert client.update_entity.call_args.args[3] == {
            "condition": {
                "kind": "prefix",
                "value": "/",
                "actions": [
                    {
                        "kind": "backend",
                        "pool": POOL_UUID,
                        "protocol": {"kind": "https"},
                    }
                ],
            }
        }
