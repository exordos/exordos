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

from click.testing import CliRunner

from exordos.cmd.em.elements import commands

EMPTY = {"uuid": "e1", "name": "empty", "version": "0.0.14", "status": "ACTIVE"}
DEPENDENT = {"uuid": "e2", "name": "dependent", "version": "1.0.0", "status": "ACTIVE"}


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
