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

"""The realm repo driver: Bearer auth and the repository index."""

import json
import pathlib
from unittest import mock

import pytest
import requests
import yaml

from exordos.builder import base as builder_base
from exordos.repo import realm

URL = "http://repo.test/repo/00000000-0000-0000-0000-000000000000"
ELEMENTS = f"{URL}/exordos-elements"


class FakeServer:
    """A WebDAV repo in memory: PUT stores, GET/HEAD read, DELETE drops."""

    def __init__(self):
        self.files: dict[str, bytes] = {}
        self.auth_headers: list[str | None] = []
        self.deleted: list[str] = []

    def send(self, request, **kwargs):
        self.auth_headers.append(request.headers.get("Authorization"))
        resp = requests.Response()
        resp.request = request
        resp.url = request.url
        if request.method == "PUT":
            body = request.body
            if hasattr(body, "read"):
                body = body.read()
            self.files[request.url] = body
            resp.status_code = 201
        elif request.method in ("GET", "HEAD"):
            if request.url in self.files:
                resp.status_code = 200
                resp._content = self.files[request.url]
            else:
                resp.status_code = 404
                resp._content = b""
        elif request.method == "DELETE":
            self.deleted.append(request.url)
            resp.status_code = 204 if self.files.pop(request.url, None) else 404
            resp._content = b""
        return resp


class FakeAuthenticator:
    def get_auth_header(self):
        return {"Authorization": "Bearer realm-token"}


@pytest.fixture
def server():
    return FakeServer()


@pytest.fixture
def driver(server, monkeypatch):
    d = realm.RealmRepoDriver(
        url=URL, authenticator=FakeAuthenticator(), logger=mock.MagicMock()
    )
    adapter = requests.adapters.HTTPAdapter()
    monkeypatch.setattr(adapter, "send", server.send)
    d._session.mount("http://", adapter)
    return d


def _element(tmp_path, name="empty", version="0.1.0"):
    manifest = tmp_path / f"{name}.yaml"
    manifest.write_text(f"name: {name}\nversion: {version}\n")
    return builder_base.ElementInventory(
        name=name, version=version, manifests=[pathlib.Path(manifest)]
    )


def _index(server):
    return json.loads(server.files[f"{ELEMENTS}/inventory.json"])


def test_every_request_carries_the_realm_token(driver, server, tmp_path):
    driver.push(_element(tmp_path))

    assert server.auth_headers
    assert set(server.auth_headers) == {"Bearer realm-token"}


def test_push_indexes_the_published_inventory(driver, server, tmp_path):
    driver.push(_element(tmp_path))

    published = json.loads(server.files[f"{ELEMENTS}/empty/0.1.0/inventory.json"])
    assert _index(server) == {"elements": {"empty": {"0.1.0": published}}}
    assert f"{ELEMENTS}/empty/0.1.0/manifests/empty.yaml" in server.files


def test_push_keeps_what_the_index_already_holds(driver, server, tmp_path):
    driver.push(_element(tmp_path, "empty", "0.1.0"))
    driver.push(_element(tmp_path, "empty", "0.2.0"))
    driver.push(_element(tmp_path, "other", "1.0.0"))

    index = _index(server)["elements"]
    assert set(index) == {"empty", "other"}
    assert set(index["empty"]) == {"0.1.0", "0.2.0"}


def test_remove_drops_the_element_from_the_index(driver, server, tmp_path):
    driver.push(_element(tmp_path, "empty", "0.1.0"))
    driver.push(_element(tmp_path, "empty", "0.2.0"))

    driver.remove(_element(tmp_path, "empty", "0.1.0"))
    assert set(_index(server)["elements"]["empty"]) == {"0.2.0"}

    driver.remove(_element(tmp_path, "empty", "0.2.0"))
    assert _index(server) == {"elements": {}}


def test_realm_authenticator_uses_the_realm_context(tmp_path):
    cfg = tmp_path / "exordosctl.yaml"
    cfg.write_text(
        yaml.safe_dump(
            {
                "current-realm": "orion",
                "realms": {
                    "orion": {
                        "endpoint": "https://orion.test/api/core",
                        "current-context": "admin",
                        "contexts": {"admin": {"user": "admin", "password": "p"}},
                    }
                },
            }
        )
    )

    auth = realm.realm_authenticator(cfg_path=str(cfg))

    assert auth._url.startswith("https://orion.test/api/core/v1/iam/clients/")
    assert auth._data["username"] == "admin"


def test_unknown_realm_is_an_error(tmp_path):
    cfg = tmp_path / "exordosctl.yaml"
    cfg.write_text(yaml.safe_dump({"realms": {}}))

    with pytest.raises(ValueError, match="nope"):
        realm.realm_authenticator("nope", cfg_path=str(cfg))


def test_loader_passes_the_active_settings_to_the_realm_driver(tmp_path, monkeypatch):
    from exordos.repo import utils as repo_utils

    cfg = tmp_path / "custom.yaml"
    cfg.write_text(
        yaml.safe_dump(
            {
                "repositories": {"orion": {"driver": "realm", "url": URL}},
                "current-realm": "orion",
                "realms": {
                    "orion": {
                        "endpoint": "https://orion.test/api/core",
                        "current-context": "admin",
                        "contexts": {"admin": {"user": "admin", "password": "p"}},
                    }
                },
            }
        )
    )

    logins = []
    monkeypatch.setattr(
        realm.base_client.CoreIamAuthenticator,
        "authenticate",
        lambda self: logins.append(self._url),
    )

    driver = repo_utils.load_repo_driver_from_settings(str(cfg), "orion")

    assert isinstance(driver, realm.RealmRepoDriver)
    assert driver.name == "orion"
    assert driver._session.auth._authenticator._url.startswith("https://orion.test/")
    # Logged in once up front, so an expired cached token is not reused.
    assert len(logins) == 1


def test_realm_login_can_ask_for_otp(tmp_path):
    cfg = tmp_path / "exordosctl.yaml"
    cfg.write_text(
        yaml.safe_dump(
            {
                "current-realm": "orion",
                "realms": {
                    "orion": {
                        "endpoint": "https://orion.test/api/core",
                        "current-context": "admin",
                        "contexts": {"admin": {"user": "admin", "password": "p"}},
                    }
                },
            }
        )
    )

    assert realm.realm_authenticator(cfg_path=str(cfg))._otp_prompt is not None


def test_remove_deletes_directories_by_their_collection_uri(driver, server, tmp_path):
    # nginx WebDAV answers 409 to a DELETE of a directory without the slash.
    driver.push(_element(tmp_path))
    driver.remove(_element(tmp_path))

    dirs = [u for u in server.deleted if not u.rsplit("/", 1)[-1].count(".")]
    assert f"{ELEMENTS}/empty/0.1.0/" in dirs
    assert f"{ELEMENTS}/empty/0.1.0/manifests/" in dirs
    assert all(u.endswith("/") for u in dirs)


@pytest.mark.parametrize("via", ["driver_option", "settings"])
def test_loader_hands_the_global_otp_code_to_the_realm_login(
    tmp_path, monkeypatch, via
):
    # `exordos --otp-code N push ...` must not prompt: no TTY in CI.
    from exordos.repo import utils as repo_utils

    cfg = tmp_path / "custom.yaml"
    cfg.write_text(
        yaml.safe_dump(
            {
                "repositories": {"orion": {"driver": "realm", "url": URL}},
                "current-realm": "orion",
                "realms": {
                    "orion": {
                        "endpoint": "https://orion.test/api/core",
                        "current-context": "admin",
                        "contexts": {"admin": {"user": "admin", "password": "p"}},
                    }
                },
            }
        )
    )
    monkeypatch.setattr(
        realm.base_client.CoreIamAuthenticator, "authenticate", lambda self: None
    )

    def otp_prompt():
        return "123456"

    if via == "settings":
        driver = repo_utils.load_repo_driver_from_settings(
            str(cfg), "orion", otp_prompt
        )
    else:
        driver = repo_utils.load_repo_driver(
            "exordos.yaml",
            "orion",
            str(tmp_path),
            str(cfg),
            "realm",
            (f"url={URL}",),
            otp_prompt=otp_prompt,
        )

    assert driver._session.auth._authenticator._otp_prompt() == "123456"


@pytest.mark.parametrize(
    "user,password", [("upload", "secret"), ("upload", None), (None, "secret")]
)
def test_realm_authenticator_explicit_credentials_override_cached_identity(
    tmp_path, user, password
):
    cfg = tmp_path / "settings.yaml"
    cfg.write_text(
        yaml.safe_dump(
            {
                "current-realm": "orion",
                "realms": {
                    "orion": {
                        "endpoint": "https://orion.test/api/core",
                        "current-context": "admin",
                        "contexts": {
                            "admin": {
                                "user": "admin",
                                "login": "saved-login",
                                "password": "saved-password",
                                "access_token": "saved-token",
                                "refresh_token": "saved-refresh",
                            }
                        },
                    }
                },
            }
        )
    )
    with mock.patch.object(realm.base_client, "CoreIamAuthenticator") as factory:
        realm.realm_authenticator(cfg_path=str(cfg), user=user, password=password)
    kwargs = factory.call_args.kwargs
    assert kwargs["username"] == (user or "admin")
    assert kwargs["password"] == (password or "saved-password")
    assert kwargs["login"] == (None if user else "saved-login")
    assert kwargs["access_token"] is None
    assert kwargs["refresh_token"] is None
    assert kwargs["realm"] is None


def test_realm_driver_forwards_explicit_credentials():
    with mock.patch.object(realm, "realm_authenticator") as factory:
        realm.RealmRepoDriver(url=URL, realm="orion", user="upload", password="secret")
    assert factory.call_args.kwargs == {
        "user": "upload",
        "password": "secret",
        "endpoint": None,
    }
    factory.return_value.authenticate.assert_called_once()


@pytest.mark.parametrize("from_settings", [False, True])
def test_loader_passes_credentials_to_realm_driver(
    tmp_path, monkeypatch, from_settings
):
    from exordos.repo import utils as repo_utils

    cfg = tmp_path / "settings.yaml"
    cfg.write_text(
        yaml.safe_dump({"repositories": {"repo": {"driver": "realm", "url": URL}}})
    )
    factory = mock.Mock()
    monkeypatch.setattr(
        repo_utils.utils, "load_from_entry_point", lambda *args: factory
    )
    repo_utils.load_repo_driver(
        "absent.yaml",
        "repo",
        str(tmp_path),
        str(cfg),
        None if from_settings else "realm",
        (f"url={URL}",),
        user="upload",
        password="secret",
    )
    assert factory.call_args.kwargs["user"] == "upload"
    assert factory.call_args.kwargs["password"] == "secret"


def test_loader_rejects_credentials_for_other_drivers():
    from exordos.repo import utils as repo_utils

    with pytest.raises(realm.click.UsageError, match="realm driver"):
        repo_utils.load_repo_driver(
            "absent.yaml", None, ".", driver_kind="nginx", user="upload"
        )


def test_realm_authenticator_explicit_endpoint_without_settings(tmp_path):
    with mock.patch.object(realm.base_client, "CoreIamAuthenticator") as factory:
        realm.realm_authenticator(
            cfg_path=str(tmp_path / "missing.yaml"),
            endpoint="https://dcda9a.exordos.io/api/core",
            user="admin",
            password="secret",
        )
    assert factory.call_args.kwargs["base_url"] == "https://dcda9a.exordos.io/api/core"
    assert factory.call_args.kwargs["username"] == "admin"
    assert factory.call_args.kwargs["password"] == "secret"


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://28de8b.exordos.io/api/core",
        "https://28de8b.exordos.io/api/core/",
        "https://28de8b.exordos.io:8443/api/core",
    ],
)
def test_realm_driver_infers_admin_repository_from_endpoint(tmp_path, endpoint):
    driver = realm.RealmRepoDriver(
        endpoint=endpoint,
        cfg_path=str(tmp_path / "missing.yaml"),
        authenticator=FakeAuthenticator(),
    )
    origin = endpoint.split("/api/core")[0]
    assert driver.elements_path == (
        f"{origin}/repo/00000000-0000-0000-0000-000000000000/exordos-elements"
    )


def test_realm_driver_infers_selected_project(tmp_path):
    cfg = tmp_path / "settings.yaml"
    cfg.write_text(
        yaml.safe_dump(
            {
                "current-realm": "orion",
                "realms": {
                    "orion": {
                        "current-context": "project",
                        "contexts": {"project": {"project_id": "selected-project"}},
                    }
                },
            }
        )
    )
    driver = realm.RealmRepoDriver(
        endpoint="https://realm.test/api/core",
        cfg_path=str(cfg),
        authenticator=FakeAuthenticator(),
    )
    assert (
        driver.elements_path
        == "https://realm.test/repo/selected-project/exordos-elements"
    )


def test_realm_driver_explicit_url_overrides_endpoint():
    driver = realm.RealmRepoDriver(
        url=URL,
        endpoint="https://realm.test/api/core",
        authenticator=FakeAuthenticator(),
    )
    assert driver.elements_path == f"{URL}/exordos-elements"


def test_realm_driver_requires_endpoint_without_url():
    with pytest.raises(ValueError, match="endpoint or repository URL"):
        realm.RealmRepoDriver(authenticator=FakeAuthenticator())


def test_loader_uses_endpoint_without_driver_params(tmp_path):
    from exordos.repo import utils as repo_utils

    with mock.patch.object(realm, "realm_authenticator") as factory:
        driver = repo_utils.load_repo_driver(
            "absent.yaml",
            None,
            str(tmp_path),
            str(tmp_path / "missing.yaml"),
            driver_kind="realm",
            endpoint="https://28de8b.exordos.io/api/core",
            user="admin",
            password="secret",
        )
    assert driver.elements_path == (
        "https://28de8b.exordos.io/repo/00000000-0000-0000-0000-000000000000/exordos-elements"
    )
    assert factory.call_args.kwargs["user"] == "admin"
    assert factory.call_args.kwargs["password"] == "secret"
