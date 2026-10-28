# Copyright 2026 Genesis Corporation.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0

from unittest import mock

from bazooka import exceptions
from bazooka.client import SensitiveMicroserviceSession
from click.testing import CliRunner

from exordos.clients import base_client
from exordos.cmd.compute import compute_group
from exordos.common.cmd_context import ContextObject

PROJECT = "11111111-1111-1111-1111-111111111111"
BASE = [
    "cloud-connections",
    "add",
    "--name",
    "lab",
    "--project-id",
    PROJECT,
    "--auth-url",
    "https://identity.example/v3",
]


def invoke(args, input=None):
    return CliRunner().invoke(
        compute_group,
        args,
        input=input,
        obj=ContextObject(
            auth_data={},
            cfg_path=None,
            developer_key_path=None,
            cfg={},
            need_update=None,
        ),
    )


@mock.patch("exordos.cmd.compute.cloud_connections.commands.show_data")
@mock.patch("exordos.cmd.compute.cloud_connections.commands.base_client")
def test_application_credential_is_prompted_and_sent_only_to_api(client, show):
    result = invoke(
        BASE + ["--application-credential-id", "app"], input="private-sentinel\n"
    )
    assert result.exit_code == 0, result.output
    assert "private-sentinel" not in result.output
    client.get_user_api_client.assert_called_once_with(
        {}, sensitive=True, timeout=(5, 90)
    )
    data = client.add_entity.call_args.args[2]
    assert data["driver_spec"]["auth"] == {
        "application_credential_id": "app",
        "application_credential_secret": "private-sentinel",
    }
    assert data["project_id"] == PROJECT
    assert data["driver_spec"]["kind"] == "openstack"
    assert "auth" not in data
    assert (
        not {"cloud", "orch_endpoint", "status_endpoint", "agent_package"} & data.keys()
    )
    show.assert_called_once_with(client.add_entity.return_value)


@mock.patch("exordos.cmd.compute.cloud_connections.commands.show_data")
@mock.patch("exordos.cmd.compute.cloud_connections.commands.base_client")
def test_password_authentication_is_project_scoped(client, show):
    result = invoke(
        BASE
        + [
            "--auth-type",
            "v3password",
            "--username",
            "operator",
            "--os-project-name",
            "lab",
        ],
        input="private-sentinel\n",
    )
    assert result.exit_code == 0, result.output
    assert "private-sentinel" not in result.output
    assert client.add_entity.call_args.args[2]["driver_spec"]["auth"] == {
        "username": "operator",
        "password": "private-sentinel",
        "user_domain_name": "Default",
        "project_name": "lab",
        "project_domain_name": "Default",
    }


@mock.patch("exordos.cmd.compute.cloud_connections.commands.show_data")
@mock.patch("exordos.cmd.compute.cloud_connections.commands.base_client")
def test_credential_replacement_calls_core_api(client, show):
    client.get_entity.return_value = {
        "uuid": PROJECT,
        "driver_spec": {
            "kind": "openstack",
            "auth_url": "https://identity.example/v3",
            "auth_type": "v3applicationcredential",
            "interface": "public",
        },
    }
    result = invoke(
        [
            "cloud-connections",
            "update-credentials",
            PROJECT,
            "--application-credential-id",
            "replacement",
        ],
        input="private-sentinel\n",
    )
    assert result.exit_code == 0, result.output
    data = client.update_entity.call_args.args[3]
    assert data["driver_spec"] == dict(
        client.get_entity.return_value["driver_spec"],
        auth={
            "application_credential_id": "replacement",
            "application_credential_secret": "private-sentinel",
        },
    )
    client.get_entity.assert_called_once_with(
        client.get_user_api_client.return_value,
        "/v1/compute/cloud_connections/",
        PROJECT,
    )
    assert "private-sentinel" not in result.output


def test_missing_credential_id_is_rejected_before_prompt():
    result = invoke(BASE)
    assert result.exit_code != 0
    assert "--application-credential-id is required" in result.output


@mock.patch("exordos.cmd.compute.cloud_connections.commands.base_client")
def test_connection_conflict_does_not_print_credentials(client):
    client.add_entity.side_effect = exceptions.ConflictError(cause=mock.Mock())
    result = invoke(
        BASE + ["--application-credential-id", "app"], input="private-sentinel\n"
    )
    assert result.exit_code != 0
    assert "private-sentinel" not in result.output
    assert "Cloud connection already exists" in result.output
    assert client.add_entity.call_args.kwargs["handle_conflict_error"] is False


def test_sensitive_api_client_masks_request_bodies():
    client = base_client.get_user_api_client(
        {"no_auth": True, "endpoint": "http://core"}, sensitive=True
    )
    assert client._http_client.SESSION is SensitiveMicroserviceSession


@mock.patch("exordos.cmd.compute.cloud_connections.commands.base_client")
def test_unknown_driver_kind_is_rejected_before_credentials_are_read(client):
    result = invoke(BASE + ["--kind", "unknown"])
    assert result.exit_code != 0
    client.get_user_api_client.assert_not_called()


@mock.patch("exordos.cmd.compute.cloud_connections.commands.base_client")
def test_other_driver_kind_is_not_updated_with_openstack_credentials(client):
    client.get_entity.return_value = {"uuid": PROJECT, "driver_spec": {"kind": "other"}}
    result = invoke(["cloud-connections", "update-credentials", PROJECT])
    assert result.exit_code != 0
    assert "Credential replacement is supported for the openstack kind" in result.output
    client.update_entity.assert_not_called()
