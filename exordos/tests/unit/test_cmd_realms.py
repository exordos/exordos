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
import rich_click as click

from exordos.cmd.em.elements import commands as elements_commands
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


def _invoke_delete(
    cfg: dict,
    clear_cmd,
    ecosystem_error=None,
    ecosystem_realms=(),
    stands=None,
    list_error=None,
    delete_error=None,
) -> tuple:
    stand = SimpleNamespace(name="test-core")
    infra = mock.Mock()
    if list_error is not None:
        infra.list_stands.side_effect = list_error
    else:
        infra.list_stands.return_value = [stand] if stands is None else stands
    infra.delete_stand.side_effect = delete_error
    obj = ContextObject(
        auth_data={"endpoint": "http://10.20.0.2/api/core", "realm": "main"},
        cfg_path="",
        developer_key_path="",
        cfg=cfg,
        need_update=None,
    )

    with (
        mock.patch.object(
            commands, "get_ecosystem_client", side_effect=ecosystem_error
        ),
        mock.patch.object(
            commands.base_client, "list_entities", return_value=list(ecosystem_realms)
        ),
        mock.patch.object(
            commands.libvirt_infra, "LibvirtInfraDriver", return_value=infra
        ),
        mock.patch.object(commands, "get_stand_core_ip", return_value="10.40.0.2"),
        mock.patch.object(elements_commands, "clear", clear_cmd),
        mock.patch("time.sleep"),
    ):
        result = CliRunner().invoke(commands.delete_cmd, ["test-core"], obj=obj)

    return result, infra, stand


REALMS_CFG = {
    "realms": {
        "main": {"endpoint": "http://10.20.0.2/api/core"},
        "test-core": {
            "endpoint": "http://10.40.0.2/api/core",
            "current-context": "admin",
            "contexts": {"admin": {"user": "admin", "password": "secret"}},
        },
    }
}


def test_delete_cmd_clears_target_realm() -> None:
    used_auth_data = []

    @click.command()
    @click.option("-y", "y", is_flag=True)
    @click.pass_context
    def clear_cmd(ctx: click.Context, y: bool) -> bool:
        used_auth_data.append(ctx.obj.auth_data)
        return True

    result, infra, stand = _invoke_delete(REALMS_CFG, clear_cmd)

    assert result.exit_code == 0, result.output
    assert used_auth_data[0]["endpoint"] == "http://10.40.0.2/api/core"
    assert used_auth_data[0]["realm"] == "test-core"
    assert used_auth_data[0]["password"] == "secret"
    infra.delete_stand.assert_called_once_with(stand)


def test_delete_cmd_warns_on_clear_failure() -> None:
    @click.command()
    @click.option("-y", "y", is_flag=True)
    def clear_cmd(y: bool) -> bool:
        raise click.ClickException("api is down")

    result, infra, stand = _invoke_delete(REALMS_CFG, clear_cmd)

    assert result.exit_code == 0, result.output
    assert "Failed to clear local realm test-core" in result.output
    assert "api is down" in result.output
    infra.delete_stand.assert_called_once_with(stand)


def test_delete_cmd_skips_clear_without_config_realm() -> None:
    clear_cmd = mock.Mock()

    result, infra, stand = _invoke_delete(
        {"realms": {"main": {"endpoint": "http://10.20.0.2/api/core"}}}, clear_cmd
    )

    assert result.exit_code == 0, result.output
    assert "skipping elements cleanup" in result.output
    clear_cmd.assert_not_called()
    infra.delete_stand.assert_called_once_with(stand)


def test_delete_cmd_deletes_local_realm_without_ecosystem_auth() -> None:
    clear_cmd = mock.Mock()

    result, infra, stand = _invoke_delete(
        {"realms": {"main": {"endpoint": "http://10.20.0.2/api/core"}}},
        clear_cmd,
        ecosystem_error=RuntimeError("bad creds"),
    )

    assert result.exit_code == 0, result.output
    infra.delete_stand.assert_called_once_with(stand)


def test_delete_cmd_prefers_local_realm_over_ecosystem() -> None:
    clear_cmd = mock.Mock()

    with mock.patch.object(commands.base_client, "delete_entity") as delete_entity:
        result, infra, stand = _invoke_delete(
            {"realms": {"main": {"endpoint": "http://10.20.0.2/api/core"}}},
            clear_cmd,
            ecosystem_realms=[{"name": "test-core", "uuid": "r1"}],
        )

    assert result.exit_code == 0, result.output
    delete_entity.assert_not_called()
    infra.delete_stand.assert_called_once_with(stand)


def test_list_cmd_without_ecosystem_auth() -> None:
    infra = mock.Mock()
    infra.list_stands.return_value = []

    with (
        mock.patch.object(
            commands, "get_ecosystem_client", side_effect=RuntimeError("bad creds")
        ),
        mock.patch.object(
            commands.libvirt_infra, "LibvirtInfraDriver", return_value=infra
        ),
    ):
        result = CliRunner().invoke(
            commands.list_cmd, obj=SimpleNamespace(auth_data={}, cfg={})
        )

    assert result.exit_code == 0, result.output


def test_delete_cmd_warns_when_realm_not_found() -> None:
    result, infra, _ = _invoke_delete(REALMS_CFG, mock.Mock(), stands=[])

    assert result.exit_code == 0, result.output
    # Teardown warnings must go to stderr, so stdout stays machine-readable
    assert "Realm test-core not found, nothing to delete" in result.stderr
    infra.delete_stand.assert_not_called()


def test_delete_cmd_warns_on_delete_stand_failure() -> None:
    result, infra, stand = _invoke_delete(
        REALMS_CFG, mock.Mock(), delete_error=RuntimeError("virsh is gone")
    )

    assert result.exit_code == 0, result.output
    assert "Failed to delete local realm test-core" in result.output
    assert "virsh is gone" in result.output
    infra.delete_stand.assert_called_once_with(stand)


def test_delete_cmd_warns_when_stands_cannot_be_listed() -> None:
    result, infra, _ = _invoke_delete(
        REALMS_CFG, mock.Mock(), list_error=RuntimeError("no libvirt")
    )

    assert result.exit_code == 0, result.output
    assert "Unable to list local stands: no libvirt" in result.output
    infra.delete_stand.assert_not_called()
