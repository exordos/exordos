# Copyright 2026 Genesis Corporation.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0

from bazooka import exceptions
import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.cmd.base import create_entity_group
from exordos.common.table import show_data

FIELDS_MAP = {
    "UUID": "uuid",
    "Name": "name",
    "Kind": lambda value: value["driver_spec"]["kind"],
    "Scope": lambda value: str(value.get("driver_state") or {}),
    "Project": "project_id",
}
COLLECTION = c.CLOUD_CONNECTION_COLLECTION
cloud_connections_group = create_entity_group(
    "cloud connection", COLLECTION, FIELDS_MAP, group_name="cloud-connections"
)


def credential_options(command):
    options = [
        click.option(
            "--auth-type",
            type=click.Choice(["v3applicationcredential", "v3password"]),
            default="v3applicationcredential",
            show_default=True,
        ),
        click.option("--application-credential-id"),
        click.option(
            "--application-credential-secret",
            envvar="OS_APPLICATION_CREDENTIAL_SECRET",
            help="Secret; prompted without echo when omitted.",
        ),
        click.option("--username"),
        click.option(
            "--password",
            envvar="OS_PASSWORD",
            help="Password; prompted without echo when omitted.",
        ),
        click.option(
            "--os-project-id",
            help="OpenStack project UUID, distinct from Core project UUID.",
        ),
        click.option("--os-project-name"),
        click.option("--user-domain-name", default="Default", show_default=True),
        click.option("--project-domain-name", default="Default", show_default=True),
    ]
    for option in reversed(options):
        command = option(command)
    return command


def credentials(
    auth_type,
    application_credential_id,
    application_credential_secret,
    username,
    password,
    os_project_id,
    os_project_name,
    user_domain_name,
    project_domain_name,
):
    if auth_type == "v3applicationcredential":
        if not application_credential_id:
            raise click.UsageError("--application-credential-id is required")
        if username or password or os_project_id or os_project_name:
            raise click.UsageError(
                "Password options cannot be used with application credentials"
            )
        return {
            "application_credential_id": application_credential_id,
            "application_credential_secret": application_credential_secret
            or click.prompt("Application credential secret", hide_input=True),
        }
    if application_credential_id or application_credential_secret:
        raise click.UsageError(
            "Application credential options cannot be used with password authentication"
        )
    if not username or bool(os_project_id) == bool(os_project_name):
        raise click.UsageError(
            "--username and exactly one of --os-project-id or --os-project-name are required"
        )
    auth = {
        "username": username,
        "user_domain_name": user_domain_name,
        "password": password or click.prompt("OpenStack password", hide_input=True),
    }
    if os_project_id:
        auth["project_id"] = os_project_id
    else:
        auth.update(
            project_name=os_project_name, project_domain_name=project_domain_name
        )
    return auth


@cloud_connections_group.command("add", help="Register OpenStack credentials in Core")
@click.pass_context
@click.option("--name", "-n", required=True)
@click.option(
    "--project-id", "-p", type=click.UUID, required=True, help="Core project UUID"
)
@click.option(
    "--kind",
    type=click.Choice(["openstack"]),
    default="openstack",
    show_default=True,
    help="Cloud driver kind",
)
@click.option("--auth-url", required=True, help="Keystone v3 URL")
@click.option("--region", default=None)
@click.option(
    "--interface",
    type=click.Choice(["public", "internal", "admin"]),
    default="public",
    show_default=True,
)
@credential_options
def add(ctx, name, project_id, kind, auth_url, region, interface, **options):
    auth = credentials(**options)
    client = base_client.get_user_api_client(
        ctx.obj.auth_data, sensitive=True, timeout=(5, 90)
    )
    data = dict(
        name=name,
        project_id=str(project_id),
        driver_spec=dict(
            kind=kind,
            auth_url=auth_url,
            auth_type=options["auth_type"],
            auth=auth,
            region=region,
            interface=interface,
        ),
    )
    try:
        result = base_client.add_entity(
            client, COLLECTION, data, handle_conflict_error=False
        )
    except exceptions.ConflictError:
        raise click.ClickException("Cloud connection already exists") from None
    show_data(result)


@cloud_connections_group.command(
    "update-credentials", help="Replace credentials within the same OpenStack project"
)
@click.pass_context
@click.argument("connection")
@credential_options
def update_credentials(ctx, connection, **options):
    client = base_client.get_user_api_client(
        ctx.obj.auth_data, sensitive=True, timeout=(5, 90)
    )
    current = base_client.get_entity(client, COLLECTION, connection)
    spec = dict(current["driver_spec"])
    if spec["kind"] != "openstack":
        raise click.ClickException(
            "Credential replacement is supported for the openstack kind"
        )
    spec.update(auth_type=options["auth_type"], auth=credentials(**options))
    result = base_client.update_entity(
        client, COLLECTION, current["uuid"], {"driver_spec": spec}
    )
    show_data(result)
