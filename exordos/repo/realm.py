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

import json
import pathlib
import typing as tp
from urllib import parse
import uuid

import requests
import rich_click as click
import yaml

from exordos import constants as c
from exordos import logger as logger_base
from exordos.builder import base as builder_base
from exordos.clients import base as base_client
from exordos.cmd.settings import config as settings_config
from exordos.repo import nginx


class _BearerAuth(requests.auth.AuthBase):
    """Sign every request with a fresh token of the realm's IAM login."""

    def __init__(self, authenticator: base_client.CoreIamAuthenticator):
        self._authenticator = authenticator

    def __call__(self, request):
        request.headers.update(self._authenticator.get_auth_header())
        return request


def realm_authenticator(
    realm: str | None = None,
    cfg_path: str = c.CONFIG_FILE,
    otp_prompt: tp.Callable[[], str] | None = None,
    user: str | None = None,
    password: str | None = None,
    endpoint: str | None = None,
    access_token: str | None = None,
) -> base_client.CoreIamAuthenticator:
    """Build an authenticator from a realm's current context in settings."""
    if endpoint is not None and (
        cfg_path is None or not pathlib.Path(cfg_path).exists()
    ):
        config = {}
    else:
        with open(cfg_path) as f:
            config = yaml.safe_load(f) or {}
    realm_name = realm or settings_config.get_current_realm(config)
    realm_conf = settings_config.get_realm(config, realm_name)
    if not realm_conf and endpoint is None:
        raise ValueError(f"Realm {realm_name!r} not found in settings")
    context = settings_config.get_context(realm_conf)
    project_id = context.get("project_id")
    explicit_credentials = (
        user is not None
        or password is not None
        or endpoint is not None
        or access_token is not None
    )
    if not explicit_credentials:
        access_token = context.get("access_token")
    return base_client.CoreIamAuthenticator(
        base_url=endpoint if endpoint is not None else realm_conf["endpoint"],
        username=user if user is not None else context.get("user"),
        login=None if user is not None else context.get("login"),
        password=password if password is not None else context.get("password"),
        access_token=access_token,
        refresh_token=None if explicit_credentials else context.get("refresh_token"),
        scope=f"project:{project_id}" if project_id else None,
        realm=None if explicit_credentials else realm_name,
        password_prompt=base_client.PasswordPrompt(),
        otp_prompt=otp_prompt or (lambda: click.prompt("OTP code", hide_input=False)),
    )


class RealmRepoDriver(nginx.NginxRepoDriver):
    """The element repository a managed realm serves from its node.

    Nginx WebDAV, like `NginxRepoDriver`, with two differences:

    - every request carries a Bearer token of the realm's IAM login, which
      the realm core checks (`authorize_repo_upload`): the token's project
      must be the one in `url` (`.../repo/<project_id>`), or the token
      unscoped and allowed to upload;
    - the repository index (`<url>/exordos-elements/inventory.json`), which
      the realm core reads, is kept here: nothing server-side builds it.
    """

    # Gets the active settings path (`exordos --config`) from the loader.
    READS_SETTINGS = True

    def __init__(
        self,
        url: str | None = None,
        name: str = "realm_repo",
        realm: str | None = None,
        cfg_path: str = c.CONFIG_FILE,
        logger: logger_base.AbstractLogger = logger_base.ClickLogger(),
        authenticator: base_client.CoreIamAuthenticator | None = None,
        otp_prompt: tp.Callable[[], str] | None = None,
        user: str | None = None,
        password: str | None = None,
        endpoint: str | None = None,
        access_token: str | None = None,
    ):
        if url is None:
            if endpoint is None:
                raise ValueError(
                    "The realm driver requires an endpoint or repository URL"
                )
            config = {}
            if cfg_path is not None and pathlib.Path(cfg_path).exists():
                with open(cfg_path) as f:
                    config = yaml.safe_load(f) or {}
            realm_name = realm or settings_config.get_current_realm(config)
            realm_conf = settings_config.get_realm(config, realm_name)
            context = settings_config.get_context(realm_conf)
            project_id = context.get("project_id") or str(uuid.UUID(int=0))
            endpoint_url = parse.urlsplit(endpoint)
            url = parse.urlunsplit(
                (
                    endpoint_url.scheme,
                    endpoint_url.netloc,
                    f"/repo/{project_id}",
                    "",
                    "",
                )
            )
        super().__init__(url=url, name=name or "realm_repo", logger=logger)
        if authenticator is None:
            authenticator = realm_authenticator(
                realm,
                cfg_path,
                otp_prompt,
                user=user,
                password=password,
                endpoint=endpoint,
                access_token=access_token,
            )
            # Use an explicitly supplied access token directly. Otherwise
            # log in (or refresh) before the push in case cached tokens expired.
            if access_token is None:
                authenticator.authenticate()
        self._session.auth = _BearerAuth(authenticator)

    @property
    def index_path(self) -> str:
        return f"{self.elements_path}/inventory.json"

    def _read_index(self) -> dict:
        response = self._session.get(self.index_path)
        if response.status_code == 404:
            return {"elements": {}}
        self._check_response(response, "read the repository index")
        index = response.json()
        index.setdefault("elements", {})
        return index

    def _write_index(self, index: dict) -> None:
        response = self._session.put(
            self.index_path, data=json.dumps(index, indent=2).encode("utf-8")
        )
        self._check_response(response, "update the repository index")

    def push(
        self,
        element: builder_base.ElementInventory,
        latest: bool = False,
        workers: int = 1,
    ) -> None:
        super().push(element, latest=latest, workers=workers)

        # Index exactly the inventory the push just published.
        response = self._session.get(self.elements_inventory_path(element))
        self._check_response(
            response, f"read the inventory of {element.name} {element.version}"
        )
        # Read-modify-write: concurrent pushes to one repository may lose an
        # entry; pushing that element again restores it.
        index = self._read_index()
        index["elements"].setdefault(element.name, {})[element.version] = (
            response.json()
        )
        self._write_index(index)

    def remove(self, element: builder_base.ElementInventory) -> None:
        index = self._read_index()
        versions = index["elements"].get(element.name, {})
        if versions.pop(element.version, None) is not None:
            if not versions:
                del index["elements"][element.name]
            self._write_index(index)
        super().remove(element)
