# Copyright 2026 Genesis Corporation.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0

import os

import rich_click as click


def credential_options(command):
    options = [
        click.option(
            "--auth-type",
            type=click.Choice(["v3applicationcredential", "v3password"]),
            default="v3applicationcredential",
            show_default=True,
        ),
        click.option("--application-credential-id"),
        click.option("--username"),
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
    username,
    os_project_id,
    os_project_name,
    user_domain_name,
    project_domain_name,
):
    if auth_type == "v3applicationcredential":
        if not application_credential_id:
            raise click.UsageError("--application-credential-id is required")
        if username or os_project_id or os_project_name:
            raise click.UsageError(
                "Password options cannot be used with application credentials"
            )
        return {
            "application_credential_id": application_credential_id,
            "application_credential_secret": os.environ.get("OS_APPLICATION_CREDENTIAL_SECRET")
            or click.prompt("Application credential secret", hide_input=True),
        }
    if application_credential_id:
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
        "password": os.environ.get("OS_PASSWORD") or click.prompt("OpenStack password", hide_input=True),
    }
    if os_project_id:
        auth["project_id"] = os_project_id
    else:
        auth.update(
            project_name=os_project_name, project_domain_name=project_domain_name
        )
    return auth
