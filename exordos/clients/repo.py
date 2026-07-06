#    Copyright 2025 Genesis Corporation.
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
from pathlib import Path
import re
import typing as tp
import urllib.parse
import urllib.request

import yaml

from exordos import constants as c
from exordos.common import version as version_lib
from exordos.exceptions import ManifestNotFound


def _join_url(*parts: str) -> str:
    # Join URL parts ensuring single slashes
    base = parts[0]
    for p in parts[1:]:
        base = urllib.parse.urljoin(base.rstrip("/") + "/", p)
    return base


def _http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": f"{c.PKG_NAME}/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()


def _extract_hrefs(html: str) -> list[str]:
    # Extract href values from simple directory listings
    return re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)


class Repository:
    def __init__(self, repository_url: str):
        self.repository_url = repository_url

    def element_url(
        self,
        manifest_name: str,
    ) -> str:
        return _join_url(self.repository_url, manifest_name)

    @classmethod
    def element_html(cls, element_url: str) -> str:
        try:
            element_html = _http_get(element_url).decode("utf-8", errors="ignore")
            return element_html
        except Exception as exc:
            raise ManifestNotFound(f"Element not found at {element_url}: {exc}")

    @classmethod
    def get_inventory_url(
        cls,
        element_url: str,
        version: str,
    ) -> str:
        return _join_url(element_url, version, "inventory.json")

    def get_versions(
        self,
        manifest_name: str,
        element_html: str | None = None,
        skip_latest: bool = False,
        stable: bool = False,
    ) -> list[str]:
        element_url = self.element_url(manifest_name)
        if not element_html:
            element_html = self.element_html(element_url)
        versions = _extract_hrefs(element_html)
        if not versions:
            raise ManifestNotFound(
                f"No version directories found for element '{manifest_name}' "
                f"at {element_url}, (html: {str(element_html)})"
            )
        # Remove last slash from all versions
        versions = [v.rstrip("/") for v in versions]
        # Remove latest version from list if exists
        if skip_latest and "latest" in versions:
            versions.remove("latest")
        if stable:
            versions = [
                v
                for v in versions
                if version_lib.is_version(v) and version_lib.is_stable_version(v)
            ]
        return versions

    def check_repo(self) -> None:
        try:
            _http_get(self.repository_url).decode("utf-8", errors="ignore")
        except Exception as exc:
            raise ManifestNotFound(
                f"Failed to access repository: {self.repository_url}: {exc}"
            )

    def get_all_elements(self) -> list[str]:
        inventory_url = _join_url(self.repository_url, "inventory.json")
        try:
            result = _http_get(inventory_url)
        except urllib.request.HTTPError as exc:
            if exc.code == 404:
                raise ManifestNotFound(
                    f"Failed to access repository: {inventory_url}: {exc}"
                )
            raise
        inventory = json.loads(result)
        return sorted(inventory["elements"].keys())

    def get_element_versions(self, element_name: str) -> list[str]:
        try:
            # 1) List repository root to ensure element exists
            # (optional but validates repo)
            _http_get(self.repository_url).decode("utf-8", errors="ignore")
        except Exception as exc:
            raise ManifestNotFound(
                f"Failed to access repository: {self.repository_url}: {exc}"
            )

        # 2) List element directory to get versions
        element_url = _join_url(self.repository_url, element_name)
        try:
            element_html = _http_get(element_url).decode("utf-8", errors="ignore")
        except Exception as exc:
            raise ManifestNotFound(
                f"Element '{element_name}' not found at {element_url}: {exc}"
            )

        version_dirs = [h for h in _extract_hrefs(element_html)]
        if not version_dirs:
            raise ManifestNotFound(
                f"No version directories found for element '{element_name}' "
                f"at {element_url}"
            )
        # Remove last slash from all versions
        version_dirs = [v.rstrip("/") for v in version_dirs]
        # Remove latest version from list if exists
        if "latest" in version_dirs:
            version_dirs.remove("latest")
        return version_dirs

    def get_element_versions_by_inventory(self, element_name: str) -> list[str]:
        inventory_url = _join_url(self.repository_url, "inventory.json")
        result = _http_get(inventory_url)
        inventory = json.loads(result)
        if element_name not in inventory["elements"]:
            raise ManifestNotFound(
                f"Element '{element_name}' not found in inventory at {inventory_url}"
            )
        return sorted(inventory["elements"][element_name].keys())

    def get_manifest(
        self, element_name: str, element_version: str | None = None
    ) -> dict:
        self.check_repo()

        element_url = self.element_url(element_name)
        if not element_version:
            element_html = self.element_html(element_url)
            latest_dir = self._get_latest_version(
                element_url, element_html, element_version, element_name
            )
        else:
            latest_dir = element_version

        inventory_url = self.get_inventory_url(element_url, latest_dir)
        inventory = self._element_inventory(inventory_url)

        target_manifest_path = self.get_manifest_path_from_inventory(
            inventory, element_name, inventory_url
        )

        manifest_url = self._manifest_url(element_url, latest_dir, target_manifest_path)
        manifest = self.get_manifest_by_url(manifest_url)
        return manifest

    def get_element_inventory(
        self, element_name: str, element_version: str
    ) -> tp.Tuple[dict[str, tp.Any], dict[str, tp.Any]]:
        self.check_repo()

        element_url = self.element_url(element_name)

        if not element_version:
            element_html = self.element_html(element_url)
            versions = self.get_versions(element_name, element_html)
            try:
                latest_dir = self._get_latest_version(
                    element_url, element_html, element_version, element_name, versions
                )
            except Exception as exc:
                raise ManifestNotFound(
                    f"Failed to parse versions for '{element_name}' at {element_url}: {exc}"
                )
        else:
            latest_dir = element_version

        inventory_url = self.get_inventory_url(element_url, latest_dir)
        inventory = self._element_inventory(inventory_url)

        target_manifest_path = self.get_manifest_path_from_inventory(
            inventory, element_name, inventory_url
        )

        manifest_url = self._manifest_url(element_url, latest_dir, target_manifest_path)
        manifest = self.get_manifest_by_url(manifest_url)
        return manifest, inventory

    def openapi_spec(self, element_name: str, element_version: str) -> dict:
        element_url = self.element_url(element_name)

        manifest, inventory = self.get_element_inventory(element_name, element_version)
        for artifact in inventory.get("artifacts", []):
            if "openapi" in artifact:
                artifact_url = self._artifact_url(
                    element_url, element_version, artifact
                )
                user_api_spec = self._element_openapi_artifact(artifact_url)
                return user_api_spec
        return {}

    @classmethod
    def get_manifest_path_from_inventory(
        cls, inventory: dict[str, tp.Any], manifest_name: str, inventory_url: str
    ) -> str:
        target_manifest_path = None
        for manifest_path in inventory["manifests"]:
            stem = Path(manifest_path).stem
            if stem == manifest_name:
                target_manifest_path = manifest_path
        if target_manifest_path is None:
            raise ManifestNotFound(
                f"Manifest '{manifest_name}' not found in inventory at {inventory_url}"
            )
        return target_manifest_path

    @classmethod
    def get_manifest_by_url(cls, manifest_url: str) -> dict[str, tp.Any]:
        try:
            data = _http_get(manifest_url)
            manifest = yaml.safe_load(data)
            if not isinstance(manifest, dict):
                raise ManifestNotFound(
                    f"Manifest at {manifest_url} is not a YAML mapping"
                )
            return manifest
        except ManifestNotFound:
            raise
        except Exception as exc:
            raise ManifestNotFound(
                f"Failed to download or parse manifest at {manifest_url}: {exc}"
            )

    @classmethod
    def _element_inventory(cls, inventory_url: str) -> dict[str, tp.Any]:
        try:
            inventory = json.loads(_http_get(inventory_url))
            return inventory
        except Exception as exc:
            raise ManifestNotFound(
                f"Failed to download or parse inventory at {inventory_url}: {exc}"
            )

    @classmethod
    def _element_openapi_artifact(cls, artifact_url: str) -> dict[str, tp.Any]:
        try:
            artifact = yaml.safe_load(_http_get(artifact_url))
            return artifact
        except Exception as exc:
            raise ManifestNotFound(
                f"Failed to download or parse artifact at {artifact_url}: {exc}"
            )

    @classmethod
    def _manifest_url(
        cls,
        element_url: str,
        version: str,
        manifest_name: str,
    ) -> str:
        return _join_url(element_url, version, "manifests/", manifest_name)

    @classmethod
    def _artifact_url(
        cls,
        element_url: str,
        version: str,
        artifact_name: str,
    ) -> str:
        return _join_url(element_url, version, "artifacts/", artifact_name)

    def _get_latest_version(
        self,
        element_url: str,
        element_html: str | None,
        manifest_version: str | None,
        manifest_name: str,
        versions: list[str] | None = None,
    ) -> str:
        if manifest_version is None:
            versions = versions or self.get_versions(manifest_name, element_html)

            # Pick the highest semantic version
            try:
                latest_dir = max(versions)
            except Exception as exc:
                raise ManifestNotFound(
                    f"Failed to parse versions for '{manifest_name}' at {element_url}: {exc}"
                )
        else:
            latest_dir = manifest_version
        return latest_dir
