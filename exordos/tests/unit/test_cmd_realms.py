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
import datetime
import threading
from types import SimpleNamespace
from unittest import mock

from bazooka import exceptions as bazooka_exc
from click.testing import CliRunner

from exordos.cmd.realms import commands
from exordos.common.cmd_context import ContextObject


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


def _invoke_claim(argv, add_entity_result=None, add_entity_error=None) -> tuple:
    obj = ContextObject(
        auth_data={"endpoint": "http://10.20.0.2/api/core", "realm": "main"},
        cfg_path="",
        developer_key_path="",
        cfg={},
        need_update=None,
    )
    add_entity = mock.Mock(
        return_value=add_entity_result if add_entity_result is not None else {},
        side_effect=add_entity_error,
    )

    with (
        mock.patch.object(commands, "get_ecosystem_client"),
        mock.patch.object(commands.base_client, "add_entity", add_entity),
        mock.patch.object(commands, "show_data"),
    ):
        result = CliRunner().invoke(commands.claim_cmd, argv, obj=obj)

    return result, add_entity


def test_claim_cmd_posts_to_the_pool_collection() -> None:
    result, add_entity = _invoke_claim(
        ["--name", "smoke-1"], add_entity_result={"uuid": "u"}
    )

    assert result.exit_code == 0
    collection = add_entity.call_args.args[1]
    assert collection == commands.POOL_COLLECTION
    assert add_entity.call_args.args[2] == {"name": "smoke-1"}
    # A 409 has to reach this command rather than being turned into a
    # generic "already exists" by the client helper.
    assert add_entity.call_args.kwargs["handle_conflict_error"] is False


def test_claim_cmd_exits_with_its_own_code_on_an_empty_pool() -> None:
    result, _ = _invoke_claim(
        ["--name", "smoke-1"],
        add_entity_error=bazooka_exc.ConflictError(cause=mock.Mock()),
    )

    assert result.exit_code == commands.POOL_EMPTY_EXIT_CODE
    assert "order one instead" in result.output


def test_claim_cmd_sends_a_timezone_aware_deadline() -> None:
    # The platform refuses a naive expires_at, so the offset must travel.
    result, add_entity = _invoke_claim(["--name", "smoke-1", "--ttl-hours", "2"])

    assert result.exit_code == 0
    expires_at = datetime.datetime.fromisoformat(
        add_entity.call_args.args[2]["expires_at"]
    )
    assert expires_at.tzinfo is not None
    assert expires_at > datetime.datetime.now(datetime.timezone.utc)


def test_claim_cmd_reads_the_ssh_key_from_its_file() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("id.pub", "w") as f:
            f.write("ssh-ed25519 AAAA test\n")

        result, add_entity = _invoke_claim(
            ["--name", "smoke-1", "--ssh-public-key", "id.pub"]
        )

    assert result.exit_code == 0
    assert add_entity.call_args.args[2]["ssh_public_key"] == "ssh-ed25519 AAAA test\n"
