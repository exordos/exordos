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
from types import SimpleNamespace
from unittest import mock

from bazooka import exceptions as bazooka_exc
from click.testing import CliRunner
import pytest

from exordos.cmd.em.elements import commands

EMPTY = {"uuid": "e1", "name": "empty", "version": "0.0.14", "status": "ACTIVE"}
DEPENDENT = {"uuid": "e2", "name": "dependent", "version": "1.0.0", "status": "ACTIVE"}


def test_list_cmd_orders_elements_by_name() -> None:
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(
            commands.base_client, "list_entities", return_value=[EMPTY, DEPENDENT]
        ),
    ):
        result = CliRunner().invoke(
            commands.ee_group, ["list"], obj=SimpleNamespace(auth_data={})
        )

    assert result.exit_code == 0, result.output
    assert result.output.index("dependent") < result.output.index("empty")


def _invoke_clear(listings: list, action_side_effect=None, args=()) -> tuple:
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(
            commands.base_client, "list_entities", side_effect=listings
        ) as list_entities,
        mock.patch.object(
            commands.base_client, "action_entity", side_effect=action_side_effect
        ) as action_entity,
        mock.patch.object(commands.time, "sleep"),
    ):
        result = CliRunner().invoke(
            commands.clear, ["-y", *args], obj=SimpleNamespace(auth_data={})
        )
    return result, list_entities, action_entity


def test_clear_waits_for_async_uninstall() -> None:
    result, list_entities, action_entity = _invoke_clear(
        [[EMPTY], [EMPTY], [EMPTY], [{**EMPTY, "status": "AVAILABLE"}]]
    )

    assert result.exit_code == 0, result.output
    assert "successfully uninstalled" in result.output
    assert list_entities.call_count == 4
    action_entity.assert_called_once()


def test_clear_retries_failed_uninstall() -> None:
    result, _, action_entity = _invoke_clear(
        [[EMPTY, DEPENDENT], [EMPTY], []],
        action_side_effect=[RuntimeError("depends"), None, None],
    )

    assert result.exit_code == 0, result.output
    assert action_entity.call_count == 3
    assert "Uninstall of empty rejected, will retry: depends" in result.output
    assert "Waiting for 1 element(s) to be uninstalled" in result.output


def test_clear_fails_fast_when_all_uninstalls_rejected() -> None:
    result, list_entities, _ = _invoke_clear(
        [[EMPTY]], action_side_effect=RuntimeError("403 Forbidden")
    )

    assert result.exit_code == 1
    assert "Remaining: empty (403 Forbidden)" in result.output
    list_entities.assert_called_once()


def test_clear_timeout() -> None:
    with mock.patch.object(commands.time, "monotonic", side_effect=[0, 0, 11]):
        result, _, action_entity = _invoke_clear(
            [[EMPTY], [EMPTY]], args=("--timeout", "10")
        )

    assert result.exit_code == 1
    assert "Remaining: empty" in result.output
    action_entity.assert_called_once()


def test_clear_timeout_reports_uninstall_error() -> None:
    with mock.patch.object(commands.time, "monotonic", side_effect=[0, 0, 11]):
        result, _, _ = _invoke_clear(
            [[{**EMPTY, "status": "IN_PROGRESS"}]] * 2,
            action_side_effect=RuntimeError("409 Conflict"),
            args=("--timeout", "10"),
        )

    assert result.exit_code == 1
    assert "Remaining: empty (409 Conflict)" in result.output


def test_clear_waits_for_uninstall_requested_earlier() -> None:
    requested = {**EMPTY, "installation_state": "UNINSTALLED"}
    result, _, action_entity = _invoke_clear(
        [[requested], [requested], []],
        action_side_effect=RuntimeError("Element must be installed"),
    )

    assert result.exit_code == 0, result.output
    action_entity.assert_not_called()


def test_install_cmd_accepts_names_uuid_and_manifest_in_order(tmp_path) -> None:
    element_uuid = "c4474e80-cc6a-4657-a333-c5be65f81eb4"
    manifest = tmp_path / "element.yaml"
    manifest.write_text("name: local\nversion: 2.0.0\n")
    with (
        mock.patch.object(commands.base_client, "get_user_api_client") as get_client,
        mock.patch.object(
            commands, "_select_element_by_name", side_effect=[EMPTY, DEPENDENT]
        ) as select,
        mock.patch.object(
            commands.repo_utils, "ensure_repository", return_value={"uuid": "repo"}
        ),
        mock.patch.object(commands.repo_utils, "do_upload") as upload,
        mock.patch.object(
            commands.repo_utils, "wait_for_repo_element", return_value={"uuid": "local"}
        ),
        mock.patch.object(commands.repo_utils, "install_element") as install,
    ):
        client = get_client.return_value
        client.get.return_value = {**EMPTY, "uuid": element_uuid}
        result = CliRunner().invoke(
            commands.install_cmd,
            ["empty", str(manifest), element_uuid, "dependent", "--version", "1.0.0"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert install.call_args_list == [
        mock.call(client, "e1"),
        mock.call(client, "local"),
        mock.call(client, element_uuid),
        mock.call(client, "e2"),
    ]
    assert select.call_args_list == [
        mock.call(client, "empty", "1.0.0"),
        mock.call(client, "dependent", "1.0.0"),
    ]
    upload.assert_called_once()
    assert result.output.count("was installed successfully") == 4


def test_install_cmd_stops_on_first_failure() -> None:
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(
            commands, "_select_element_by_name", return_value=EMPTY
        ) as select,
        mock.patch.object(
            commands.repo_utils, "install_element", side_effect=RuntimeError("failed")
        ) as install,
    ):
        result = CliRunner().invoke(
            commands.install_cmd,
            ["empty", "dependent"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code != 0
    assert str(result.exception) == "failed"
    select.assert_called_once()
    install.assert_called_once()


def test_install_cmd_preserves_interactive_selection() -> None:
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "list_entities", return_value=[EMPTY]),
        mock.patch("questionary.select") as picker,
        mock.patch.object(commands, "_select_element_by_name", return_value=EMPTY),
        mock.patch.object(commands.repo_utils, "install_element") as install,
    ):
        picker.return_value.ask.return_value = "empty"
        result = CliRunner().invoke(
            commands.install_cmd, [], obj=SimpleNamespace(auth_data={})
        )
    assert result.exit_code == 0, result.output
    install.assert_called_once()


@pytest.mark.parametrize(
    "pattern", ["ecosystem_ui_*", "ecosystem_ui_?", "ecosystem_ui_[ab]"]
)
def test_install_cmd_expands_name_globs(pattern) -> None:
    elements = [
        {"name": "ecosystem_ui_b", "version": "1.0.0", "uuid": "b"},
        {"name": "ecosystem_ui_a", "version": "1.0.0", "uuid": "a"},
        {"name": "Ecosystem_ui_c", "version": "1.0.0", "uuid": "c"},
    ]
    with (
        mock.patch.object(commands.base_client, "get_user_api_client") as get_client,
        mock.patch.object(
            commands.base_client, "list_entities", return_value=elements + elements
        ) as listing,
        mock.patch.object(
            commands, "_select_element_by_name", side_effect=[elements[1], elements[0]]
        ) as select,
        mock.patch.object(commands.repo_utils, "install_element") as install,
    ):
        result = CliRunner().invoke(
            commands.install_cmd,
            [pattern, "ecosystem_ui_*", "ecosystem_ui_a", "--version", "1.0.0"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    listing.assert_called_once()
    assert select.call_args_list == [
        mock.call(get_client.return_value, name, "1.0.0")
        for name in ("ecosystem_ui_a", "ecosystem_ui_b")
    ]
    assert install.call_args_list == [
        mock.call(get_client.return_value, uuid) for uuid in ("a", "b")
    ]


def test_update_cmd_glob_only_updates_installed_elements() -> None:
    elements = [
        {"name": "ui_current", "installation_state": "INSTALLED", "status": "NEW"},
        {
            "name": "ui_available",
            "installation_state": "UNINSTALLED",
            "status": "ACTIVE",
        },
        {"name": "ui_legacy", "status": "IN_PROGRESS"},
        {"name": "ui_unused", "status": "AVAILABLE"},
    ]
    with (
        mock.patch.object(commands.base_client, "get_user_api_client") as get_client,
        mock.patch.object(commands.base_client, "list_entities", return_value=elements),
        mock.patch.object(commands, "_select_current_element_by_name") as current,
        mock.patch.object(commands, "_select_element_by_name") as select,
        mock.patch.object(commands.base_client, "action_entity") as upgrade,
    ):
        current.side_effect = [
            {"name": name, "version": "1.0.0", "uuid": name}
            for name in ("ui_current", "ui_legacy")
        ]
        select.side_effect = [{"uuid": "new", "version": "2.0.0"}, None]
        result = CliRunner().invoke(
            commands.update_cmd, ["-y", "ui_*"], obj=SimpleNamespace(auth_data={})
        )
    assert result.exit_code == 0, result.output
    assert current.call_args_list == [
        mock.call(get_client.return_value, name) for name in ("ui_current", "ui_legacy")
    ]
    upgrade.assert_called_once_with(
        get_client.return_value,
        commands.c.REPOSITORY_ELEMENT_COLLECTION,
        "upgrade",
        "ui_current",
        target="new",
    )
    assert "already up to date" in result.output


@pytest.mark.parametrize("command", [commands.install_cmd, commands.update_cmd])
def test_install_update_cmd_unmatched_glob_fails_before_changes(command) -> None:
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "list_entities", return_value=[EMPTY]),
        mock.patch.object(commands.repo_utils, "install_element") as install,
        mock.patch.object(commands, "_update_element_by_uuid_or_name") as update,
    ):
        result = CliRunner().invoke(
            command, ["empty", "missing_*"], obj=SimpleNamespace(auth_data={})
        )
    assert result.exit_code == 1
    assert "No elements match pattern 'missing_*'" in result.output
    install.assert_not_called()
    update.assert_not_called()


def test_install_cmd_literal_manifest_with_glob_characters(tmp_path) -> None:
    manifest = tmp_path / "element[1].yaml"
    manifest.write_text("name: local\nversion: 1.0.0\n")
    with mock.patch.object(commands.base_client, "list_entities") as listing:
        assert commands._expand_element_targets(mock.Mock(), [str(manifest)]) == [
            str(manifest)
        ]
    listing.assert_not_called()


@pytest.mark.parametrize(
    "message,expected_code,expected_calls",
    [
        ("Element with the same name is already installed", 0, 2),
        ("Other validation error", 1, 1),
    ],
)
def test_install_cmd_glob_handles_installed_name_conflict(
    message, expected_code, expected_calls
) -> None:
    elements = [
        {"name": "ecosystem_ui_a", "uuid": "a", "version": "2.0.0"},
        {"name": "ecosystem_ui_b", "uuid": "b", "version": "2.0.0"},
    ]
    cause = mock.Mock()
    cause.response.text = message
    error = bazooka_exc.BadRequestError(cause)
    with (
        mock.patch.object(commands.base_client, "get_user_api_client"),
        mock.patch.object(commands.base_client, "list_entities", return_value=elements),
        mock.patch.object(commands, "_select_element_by_name", side_effect=elements),
        mock.patch.object(
            commands.base_client, "action_entity", side_effect=[error, None]
        ) as install,
    ):
        result = CliRunner().invoke(
            commands.install_cmd,
            ["ecosystem_ui_*"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == expected_code, result.output
    assert install.call_count == expected_calls
    if expected_code == 0:
        assert "ecosystem_ui_a is already installed, skipping" in result.output
        assert "ecosystem_ui_b (2.0.0) was installed successfully" in result.output
        assert "ecosystem_ui_a (2.0.0) was installed successfully" not in result.output
    else:
        assert result.exception is error
