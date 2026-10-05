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

from unittest import mock

from bazooka import exceptions
from click.testing import CliRunner
import pytest

from exordos import constants
from exordos.cmd.em.elements import commands
from exordos.common.cmd_context import ContextObject
from exordos.repo import utils


def _manifest(tmp_path):
    path = tmp_path / "app.yaml"
    path.write_text("name: app\nversion: 1.0\n")
    return path


def _error(error_type, status):
    cause = mock.Mock()
    cause.response.status_code = status
    return error_type(cause)


@pytest.mark.parametrize(
    "catalog",
    [
        [],
        [
            {
                "uuid": "catalog-id",
                "manifest": {"name": "app"},
                "installation_state": "UNINSTALLED",
            }
        ],
    ],
)
def test_repeated_manifest_install_stops_before_upload(tmp_path, catalog):
    manifest = _manifest(tmp_path)
    client = mock.Mock()
    context = ContextObject({}, "", "", {}, False)
    with (
        mock.patch.object(
            commands.base_client, "get_user_api_client", return_value=client
        ),
        mock.patch.object(
            commands.base_client,
            "list_entities",
            side_effect=[
                catalog,
                [{"version": "1.0", "manifest": "/v1/em/manifests/direct-id"}],
            ],
        ) as listing,
        mock.patch.object(commands.repo_utils, "ensure_repository") as ensure,
        mock.patch.object(commands.repo_utils, "do_upload") as upload,
    ):
        result = CliRunner().invoke(commands.install_cmd, [str(manifest)], obj=context)
    assert result.exit_code == 1
    assert "already installed" in result.output
    assert "update" in result.output
    assert listing.call_args_list == [
        mock.call(client, constants.REPOSITORY_ELEMENT_COLLECTION, name="app"),
        mock.call(client, constants.ELEMENT_COLLECTION, name="app"),
    ]
    ensure.assert_not_called()
    upload.assert_not_called()


@pytest.mark.parametrize("status", [400, 409])
def test_repeated_upload_accepts_existing_version(tmp_path, capsys, status):
    manifest = _manifest(tmp_path)
    with (
        mock.patch.object(
            utils.base_client, "_get_entity_uuid", return_value="repo-id"
        ),
        mock.patch.object(utils, "wait_for_repository_active"),
        mock.patch.object(
            utils.base_client,
            "list_entities",
            side_effect=[
                [],
                [
                    {
                        "repository": "/v1/repo/repositories/repo-id",
                        "manifest": {"name": "app", "version": 1.0},
                    }
                ],
            ],
        ),
        mock.patch.object(
            utils.base_client,
            "action_entity",
            side_effect=_error(
                exceptions.ConflictError
                if status == 409
                else exceptions.BadRequestError,
                status,
            ),
        ) as upload,
    ):
        utils.do_upload(mock.Mock(), "repo", manifest)
    assert "already in the repository" in capsys.readouterr().out
    upload.assert_called_once()


def test_upload_propagates_other_api_errors(tmp_path):
    manifest = _manifest(tmp_path)
    with (
        mock.patch.object(
            utils.base_client, "_get_entity_uuid", return_value="repo-id"
        ),
        mock.patch.object(utils, "wait_for_repository_active"),
        mock.patch.object(utils.base_client, "list_entities", return_value=[]),
        mock.patch.object(
            utils.base_client,
            "action_entity",
            side_effect=_error(exceptions.ForbiddenError, 403),
        ),
        pytest.raises(exceptions.ForbiddenError),
    ):
        utils.do_upload(mock.Mock(), "repo", manifest)


def test_existing_version_skips_upload_on_current_core(tmp_path, capsys):
    manifest = _manifest(tmp_path)
    with (
        mock.patch.object(
            utils.base_client, "_get_entity_uuid", return_value="repo-id"
        ),
        mock.patch.object(utils, "wait_for_repository_active"),
        mock.patch.object(
            utils.base_client,
            "list_entities",
            return_value=[
                {
                    "repository": "/v1/repo/repositories/repo-id",
                    "manifest": {"name": "app", "version": 1.0},
                }
            ],
        ),
        mock.patch.object(utils.base_client, "action_entity") as upload,
    ):
        utils.do_upload(mock.Mock(), "repo", manifest)
    upload.assert_not_called()
    assert "already in the repository" in capsys.readouterr().out


def test_same_version_in_another_repository_does_not_skip_upload(tmp_path):
    manifest = _manifest(tmp_path)
    with (
        mock.patch.object(
            utils.base_client, "_get_entity_uuid", return_value="repo-id"
        ),
        mock.patch.object(utils, "wait_for_repository_active"),
        mock.patch.object(
            utils.base_client,
            "list_entities",
            return_value=[{"repository": "/v1/repo/repositories/other-repo"}],
        ),
        mock.patch.object(utils.base_client, "action_entity") as upload,
    ):
        utils.do_upload(mock.Mock(), "repo", manifest)
    upload.assert_called_once()


def test_conflict_without_an_existing_version_remains_an_error(tmp_path):
    manifest = _manifest(tmp_path)
    with (
        mock.patch.object(
            utils.base_client, "_get_entity_uuid", return_value="repo-id"
        ),
        mock.patch.object(utils, "wait_for_repository_active"),
        mock.patch.object(utils.base_client, "list_entities", return_value=[]),
        mock.patch.object(
            utils.base_client,
            "action_entity",
            side_effect=_error(exceptions.ConflictError, 409),
        ),
        pytest.raises(exceptions.ConflictError),
    ):
        utils.do_upload(mock.Mock(), "repo", manifest)


@pytest.mark.parametrize("status", [400, 409])
@pytest.mark.parametrize("concurrent", [False, True])
def test_duplicate_upload_rejects_different_content(tmp_path, concurrent, status):
    manifest = _manifest(tmp_path)
    row = {
        "repository": "/v1/repo/repositories/repo-id",
        "manifest": {"name": "app", "version": 1.0, "resources": {"untrusted": {}}},
    }
    client = mock.Mock()
    error = exceptions.ConflictError if status == 409 else exceptions.BadRequestError
    with (
        mock.patch.object(
            utils.base_client, "_get_entity_uuid", return_value="repo-id"
        ),
        mock.patch.object(utils, "wait_for_repository_active"),
        mock.patch.object(
            utils.base_client,
            "list_entities",
            side_effect=[[], [row]] if concurrent else [[row]],
        ),
        mock.patch.object(
            utils.base_client, "action_entity", side_effect=_error(error, status)
        ),
        pytest.raises(Exception, match="different manifest content"),
    ):
        utils.do_upload(client, "repo", manifest)


def test_duplicate_upload_ignores_repository_uuid_case(tmp_path):
    manifest = _manifest(tmp_path)
    with (
        mock.patch.object(
            utils.base_client, "_get_entity_uuid", return_value="REPO-ID"
        ),
        mock.patch.object(utils, "wait_for_repository_active"),
        mock.patch.object(
            utils.base_client,
            "list_entities",
            return_value=[
                {
                    "repository": "/v1/repo/repositories/repo-id",
                    "manifest": {"version": 1.0, "name": "app"},
                }
            ],
        ),
        mock.patch.object(utils.base_client, "action_entity") as upload,
    ):
        utils.do_upload(mock.Mock(), "repo", manifest)
    upload.assert_not_called()


@pytest.mark.parametrize("lazy", [False, True])
@pytest.mark.parametrize("manifest_uuid", [None, "custom-id"])
def test_manifest_reinstall_uses_repository_state_during_teardown(
    tmp_path, manifest_uuid, lazy
):
    manifest = _manifest(tmp_path)
    client = mock.Mock()
    context = ContextObject({}, "", "", {}, False)
    with (
        mock.patch.object(
            commands.base_client, "get_user_api_client", return_value=client
        ),
        mock.patch.object(
            commands.base_client,
            "list_entities",
            side_effect=[
                [
                    {
                        "uuid": "catalog-id",
                        "version": "1.0",
                        "manifest": {} if lazy else {"uuid": manifest_uuid},
                        "installation_state": "UNINSTALLED",
                    }
                ],
                [
                    {
                        "version": "1.0",
                        "manifest": f"/v1/em/manifests/{manifest_uuid or 'catalog-id'}",
                    }
                ],
            ],
        ) as listing,
        mock.patch.object(
            commands.repo_utils, "ensure_repository", return_value={"uuid": "repo-id"}
        ),
        mock.patch.object(commands.repo_utils, "do_upload") as upload,
        mock.patch.object(
            commands.base_client,
            "get_entity",
            return_value={"uuid": "catalog-id", "manifest": {"uuid": manifest_uuid}},
        ) as get,
        mock.patch.object(
            commands.repo_utils,
            "wait_for_repo_element",
            return_value={"uuid": "element-id"},
        ),
        mock.patch.object(commands.repo_utils, "install_element") as install,
    ):
        result = CliRunner().invoke(commands.install_cmd, [str(manifest)], obj=context)
    assert result.exit_code == 0, result.output
    assert listing.call_args_list == [
        mock.call(client, constants.REPOSITORY_ELEMENT_COLLECTION, name="app"),
        mock.call(client, constants.ELEMENT_COLLECTION, name="app"),
    ]
    upload.assert_called_once()
    install.assert_called_once_with(client, "element-id")
    assert get.call_count == int(lazy)


@pytest.mark.parametrize("placeholder", [None, {}])
@pytest.mark.parametrize("different", [False, True])
def test_upload_loads_lazy_manifest_before_comparison(tmp_path, placeholder, different):
    manifest = _manifest(tmp_path)
    row = {"uuid": "element-id", "repository": "/v1/repo/repositories/repo-id"}
    if placeholder is not None:
        row["manifest"] = placeholder
    content = {"name": "app", "version": 1.0}
    if different:
        content["description"] = "different"
    with (
        mock.patch.object(
            utils.base_client, "_get_entity_uuid", return_value="repo-id"
        ),
        mock.patch.object(utils, "wait_for_repository_active"),
        mock.patch.object(utils.base_client, "list_entities", return_value=[row]),
        mock.patch.object(
            utils.base_client, "get_entity", return_value={**row, "manifest": content}
        ) as get,
        mock.patch.object(utils.base_client, "action_entity") as upload,
    ):
        if different:
            with pytest.raises(Exception, match="different manifest content"):
                utils.do_upload(mock.Mock(), "repo", manifest)
        else:
            utils.do_upload(mock.Mock(), "repo", manifest)
    get.assert_called_once()
    upload.assert_not_called()
