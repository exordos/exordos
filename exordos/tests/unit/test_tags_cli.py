#    Copyright 2026 Genesis Corporation.
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

from importlib import import_module
from types import SimpleNamespace
from unittest import mock

from click.testing import CliRunner
import pytest

from exordos.cmd.base import create_entity_group

UUID = "11111111-1111-1111-1111-111111111111"
GROUPS = [
    ("compute.sets", "sets_group"),
    ("configs", "configs_group"),
    ("dns.domains", "domains_group"),
    ("em.services", "services_group"),
    ("iam.idp", "idps_group"),
    ("iam.permission", "permissions_group"),
    ("network.lb", "lbs_group"),
    ("secret.certificate", "certificates_group"),
    ("secret.passwords", "passwords_group"),
    ("secret.rsa_keys", "rsa_keys_group"),
    ("secret.secrets", "secrets_group"),
    ("secret.ssh_keys", "ssh_keys_group"),
    ("vs.values", "values_group"),
]


@pytest.mark.parametrize("module_name,group_name", GROUPS)
@pytest.mark.parametrize(
    "options,tags",
    [
        (["--tag", "env:prod", "--tag", "team a"], ["env:prod", "team a"]),
        (["--clear"], []),
    ],
)
def test_tags_sends_only_tags(module_name, group_name, options, tags):
    module = import_module(f"exordos.cmd.{module_name}.commands")
    group = getattr(module, group_name)
    with (
        mock.patch("exordos.cmd.base.base_client") as client,
        mock.patch("exordos.cmd.base.show_data") as show,
    ):
        result = CliRunner().invoke(
            group, ["tags", UUID, *options], obj=SimpleNamespace(auth_data={})
        )
    assert result.exit_code == 0, result.output
    client.update_entity.assert_called_once_with(
        client.get_user_api_client.return_value,
        module.ENTITY_COLLECTION,
        UUID,
        {"tags": tags},
    )
    show.assert_called_once_with(client.update_entity.return_value)


@pytest.mark.parametrize("options", [[], ["--clear", "--tag", "prod"]])
def test_tags_rejects_invalid_options_before_request(options):
    group = create_entity_group("item", "/items/", {}, add_tags_command=True)
    with mock.patch("exordos.cmd.base.base_client") as client:
        result = CliRunner().invoke(group, ["tags", UUID, *options])
    assert result.exit_code == 2
    client.get_user_api_client.assert_not_called()
    client.update_entity.assert_not_called()


def test_tags_is_not_available_by_default():
    group = create_entity_group("item", "/items/", {})
    result = CliRunner().invoke(group, ["tags", UUID, "--clear"])
    assert result.exit_code == 2
    assert "No such command" in result.output


def test_tags_formats_parent_collection():
    group = create_entity_group(
        "item",
        "/parents/{parent_uuid}/items/",
        {},
        parents=["parent"],
        add_tags_command=True,
    )
    with (
        mock.patch("exordos.cmd.base.base_client") as client,
        mock.patch("exordos.cmd.base.show_data"),
    ):
        result = CliRunner().invoke(
            group,
            ["tags", UUID, "--parent-uuid", UUID, "--clear"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    client.update_entity.assert_called_once_with(
        client.get_user_api_client.return_value,
        f"/parents/{UUID}/items/",
        UUID,
        {"tags": []},
    )


CREATE_ARGS = {
    "compute.sets": ["-p", UUID, "-i", "image"],
    "dns.domains": ["-p", UUID],
    "em.services": ["-p", UUID],
    "iam.idp": ["-p", UUID, "-i", UUID, "--callback", "{}"],
    "iam.permission": [],
    "secret.certificate": ["-p", UUID, "-e", "test@example.com", "-d", "example.com"],
    "secret.passwords": ["-p", UUID],
    "secret.rsa_keys": ["-p", UUID],
    "secret.secrets": ["-p", UUID],
    "secret.ssh_keys": ["--node", UUID],
    "vs.values": ["-p", UUID],
}
UPDATE_GROUPS = [
    item
    for item in GROUPS
    if item[0] in CREATE_ARGS and item[0] not in ["iam.idp", "iam.permission"]
]


@pytest.mark.parametrize(
    "module_name,group_name", [item for item in GROUPS if item[0] in CREATE_ARGS]
)
@pytest.mark.parametrize(
    "options,expected",
    [([], None), (["--tag", "env:prod", "--tag", "team a"], ["env:prod", "team a"])],
)
def test_create_tags_payload(module_name, group_name, options, expected):
    module = import_module(f"exordos.cmd.{module_name}.commands")
    with (
        mock.patch.object(module, "base_client") as client,
        mock.patch.object(module, "show_data"),
    ):
        client.get_entity.return_value = {
            "uuid": UUID,
            "name": "node",
            "project_id": UUID,
        }
        client.add_entity.return_value = {"uuid": UUID, "status": "ACTIVE"}
        result = CliRunner().invoke(
            getattr(module, group_name),
            ["add", *CREATE_ARGS[module_name], *options],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    payload = client.add_entity.call_args.args[2]
    if expected is None:
        assert "tags" not in payload
    else:
        assert payload["tags"] == expected


@pytest.mark.parametrize("module_name,group_name", UPDATE_GROUPS)
@pytest.mark.parametrize(
    "options,expected",
    [
        (["--tag", "env:prod", "--tag", "team a"], ["env:prod", "team a"]),
        (["--clear-tags"], []),
    ],
)
def test_update_tags_payload(module_name, group_name, options, expected):
    module = import_module(f"exordos.cmd.{module_name}.commands")
    args = ["-u", UUID] if module_name == "compute.sets" else [UUID]
    with (
        mock.patch.object(module, "base_client") as client,
        mock.patch.object(module, "show_data"),
    ):
        client.get_entity.return_value = {"uuid": UUID}
        result = CliRunner().invoke(
            getattr(module, group_name),
            ["update", *args, *options],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert client.update_entity.call_args.args[3]["tags"] == expected


@pytest.mark.parametrize("module_name,group_name", UPDATE_GROUPS)
def test_update_rejects_conflicting_tag_options(module_name, group_name):
    module = import_module(f"exordos.cmd.{module_name}.commands")
    args = ["-u", UUID] if module_name == "compute.sets" else [UUID]
    with mock.patch.object(module, "base_client") as client:
        result = CliRunner().invoke(
            getattr(module, group_name),
            ["update", *args, "--tag", "prod", "--clear-tags"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 2, result.output
    client.get_user_api_client.assert_not_called()


def test_create_configs_tags_apply_to_every_generated_config(monkeypatch):
    from exordos.cmd.configs import commands as module

    monkeypatch.setenv("TAGS_TEST_ENV_VALUE", "value")
    monkeypatch.setenv("TAGS_TEST_CFG_TEXT_sample", "content")
    monkeypatch.setenv("TAGS_TEST_CFG_PATH_sample", "/tmp/sample")
    with mock.patch.object(module, "base_client") as client:
        result = CliRunner().invoke(
            module.configs_group,
            [
                "add-from-env",
                UUID,
                "-p",
                UUID,
                "--env-prefix",
                "TAGS_TEST_ENV_",
                "--cfg-prefix",
                "TAGS_TEST_CFG_",
                "--tag",
                "prod",
            ],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert client.add_entity.call_count == 2
    assert all(
        call.args[2]["tags"] == ["prod"] for call in client.add_entity.call_args_list
    )


@pytest.mark.parametrize("module_name,group_name", UPDATE_GROUPS)
def test_update_without_tag_options_preserves_tags(module_name, group_name):
    module = import_module(f"exordos.cmd.{module_name}.commands")
    args = ["-u", UUID] if module_name == "compute.sets" else [UUID]
    with (
        mock.patch.object(module, "base_client") as client,
        mock.patch.object(module, "show_data"),
    ):
        client.get_entity.return_value = {"uuid": UUID}
        result = CliRunner().invoke(
            getattr(module, group_name),
            ["update", *args, "--name", "renamed"],
            obj=SimpleNamespace(auth_data={}),
        )
    assert result.exit_code == 0, result.output
    assert "tags" not in client.update_entity.call_args.args[3]
