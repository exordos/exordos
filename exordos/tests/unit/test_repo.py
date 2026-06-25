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

"""Unit tests for exordos.clients.repo module."""

from unittest.mock import patch
import urllib.request

import pytest

from exordos import constants as c
from exordos.clients import repo


class TestJoinUrl:
    """Tests for _join_url function."""

    def test_join_simple_parts(self):
        result = repo._join_url("http://example.com", "v1", "manifest.yaml")
        assert result == "http://example.com/v1/manifest.yaml"

    def test_join_with_trailing_slash(self):
        result = repo._join_url("http://example.com/", "v1", "manifest.yaml")
        assert result == "http://example.com/v1/manifest.yaml"

    def test_join_multiple_slashes(self):
        result = repo._join_url("http://example.com///", "///v1///", "///manifest.yaml")
        assert result == "http://example.com/manifest.yaml"


class TestExtractHrefs:
    """Tests for repo._extract_hrefs function."""

    def test_extract_double_quoted_hrefs(self):
        html = '<a href="v1.0.0/">v1.0.0/</a><a href="v1.1.0/">v1.1.0/</a>'
        result = repo._extract_hrefs(html)
        assert result == ["v1.0.0/", "v1.1.0/"]

    def test_extract_single_quoted_hrefs(self):
        html = "<a href='v1.0.0/'>v1.0.0/</a><a href='v1.1.0/'>v1.1.0/</a>"
        result = repo._extract_hrefs(html)
        assert result == ["v1.0.0/", "v1.1.0/"]

    def test_extract_mixed_quotes(self):
        html = "<a href=\"v1.0.0/\">v1.0.0/</a><a href='v1.1.0/'>v1.1.0/</a>"
        result = repo._extract_hrefs(html)
        assert result == ["v1.0.0/", "v1.1.0/"]

    def test_extract_case_insensitive(self):
        html = '<A HREF="v1.0.0/">v1.0.0/</A>'
        result = repo._extract_hrefs(html)
        assert result == ["v1.0.0/"]

    def test_extract_empty_html(self):
        result = repo._extract_hrefs("")
        assert result == []

    def test_extract_exordos_repo_hrefs(self):
        html = """
        <html>
<head><title>Index of /exordos-elements/core/</title></head>
<body>
<h1>Index of /exordos-elements/core/</h1><hr><pre><a href="../">../</a>
<a href="0.0.1-dev%2B20260526064918.9cab54f9/">0.0.1-dev+20260526064918.9cab54f9/</a>                 26-May-2026 06:53       -
<a href="0.0.1-rc%2B20260611184306.3149c87a/">0.0.1-rc+20260611184306.3149c87a/</a>                  11-Jun-2026 18:46       -
<a href="0.0.10/">0.0.10/</a>                                            14-May-2026 12:02       -
<a href="0.0.9/">0.0.9/</a>                                             12-May-2026 12:50       -
<a href="0.1.6/">0.1.6/</a>                                             12-Jun-2026 06:42       -
<a href="0.1.7-dev%2B20260612115329.b6dfbd16/">0.1.7-dev+20260612115329.b6dfbd16/</a>                 12-Jun-2026 11:57       -
<a href="0.1.7-rc%2B20260615112705.cb7a83ab/">0.1.7-rc+20260615112705.cb7a83ab/</a>                  15-Jun-2026 11:31       -
<a href="latest/">latest/</a>                                            12-Jun-2026 06:42       -
</pre><hr></body>
</html>
        """
        result = repo._extract_hrefs(html)
        assert len(result) == 9
        assert "latest/" in result


class TestCheckRepo:
    """Tests for check_repo function."""

    def test_check_repo_success(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b"OK"
            repo.Repository("http://example.com").check_repo()
            mock_get.assert_called_once_with("http://example.com")

    def test_check_repo_failure(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.side_effect = Exception("Connection error")
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository("http://example.com").check_repo()
            assert "Failed to access repository" in str(exc_info.value)


class TestGetElementUrl:
    """Tests for get_element_url function."""

    def test_get_element_url_basic(self):
        result = repo.Repository(c.ELEMENT_REPO_URL).element_url("demo")
        assert result == f"{c.ELEMENT_REPO_URL}/demo"

    def test_get_element_url_with_trailing_slash(self):
        result = repo.Repository(f"{c.ELEMENT_REPO_URL}/").element_url("demo")
        assert result == f"{c.ELEMENT_REPO_URL}/demo"


class TestGetElementHtml:
    """Tests for get_element_html function."""

    def test_get_element_html_success(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b"<html><body>content</body></html>"
            result = repo.Repository.element_html("http://example.com/demo")
            assert result == "<html><body>content</body></html>"

    def test_get_element_html_not_found(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.side_effect = Exception("404 Not Found")
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository.element_html("http://example.com/demo")
            assert "not found" in str(exc_info.value).lower()


class TestGetVersions:
    """Tests for get_versions function."""

    @pytest.fixture
    def sample_html(self):
        return '<a href="1.0.0/">1.0.0/</a><a href="1.0.7-dev1/">1.0.7-dev1/</a><a href="1.1.0/">1.1.0/</a><a href="latest/">latest/</a>'

    def test_get_versions_basic(self, sample_html):
        result = repo.Repository(c.ELEMENT_REPO_URL).get_versions("demo", sample_html)
        assert result == ["1.0.0", "1.0.7-dev1", "1.1.0", "latest"]

    def test_get_versions_skip_latest(self, sample_html):
        result = repo.Repository(c.ELEMENT_REPO_URL).get_versions(
            "demo", sample_html, skip_latest=True
        )
        assert "latest" not in result
        assert result == ["1.0.0", "1.0.7-dev1", "1.1.0"]

    def test_get_versions_stable_only(self, sample_html):
        result = repo.Repository(c.ELEMENT_REPO_URL).get_versions(
            "demo", sample_html, stable=True
        )
        assert "latest" not in result
        assert all("rc" not in v and "dev" not in v for v in result)

    def test_get_versions_empty(self):
        with pytest.raises(repo.ManifestNotFound):
            repo.Repository(c.ELEMENT_REPO_URL).get_versions(
                "demo",
            )

    def test_get_versions_empty_with_error(self):
        with pytest.raises(repo.ManifestNotFound):
            repo.Repository(c.ELEMENT_REPO_URL).get_versions(
                "demo", "", skip_latest=False
            )


class TestGetLatestVersion:
    """Tests for repo._get_latest_version function."""

    def test_get_latest_version_with_explicit_version(self):
        result = repo.Repository(c.ELEMENT_REPO_URL)._get_latest_version(
            "http://example.com/demo", "<html>", "1.0.0", "demo"
        )
        assert result == "1.0.0"

    def test_get_latest_version_from_versions_list(self):
        versions = ["v1.0.0", "v1.1.0", "v1.2.0"]
        result = repo.Repository(c.ELEMENT_REPO_URL)._get_latest_version(
            "http://example.com/demo", "<html>", None, "demo", versions
        )
        assert result == "v1.2.0"

    def test_get_latest_version_empty_versions(self):
        with pytest.raises(repo.ManifestNotFound):
            repo.Repository(c.ELEMENT_REPO_URL)._get_latest_version(
                "http://example.com/demo", "<html>", None, "demo", []
            )


class TestGetInventoryUrl:
    """Tests for get_inventory_url function."""

    def test_get_inventory_url_basic(self):
        result = repo.Repository.get_inventory_url("http://example.com/demo", "1.0.0")
        assert result == "http://example.com/demo/1.0.0/inventory.json"


class TestGetElementInventory:
    """Tests for repo.get_element_inventory function."""

    def test_get_element_inventory_success(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b'{"elements": {"demo": {}}}'
            result = repo.Repository._element_inventory(
                "http://example.com/inventory.json"
            )
            assert result == {"elements": {"demo": {}}}

    def test_get_element_inventory_parse_error(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b"invalid json"
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository._element_inventory("http://example.com/inventory.json")
            assert "parse" in str(exc_info.value).lower()


class TestGetManifestUrl:
    """Tests for get_manifest_url function."""

    def test_manifest_url_basic(self):
        result = repo.Repository._manifest_url(
            "http://example.com/demo", "1.0.0", "manifest"
        )
        assert result == "http://example.com/demo/1.0.0/manifests/manifest"


class TestGetArtifactUrl:
    """Tests for get_artifact_url function."""

    def test_artifact_url_basic(self):
        result = repo.Repository._artifact_url(
            "http://example.com/demo", "1.0.0", "artifact.tar.gz"
        )
        assert result == "http://example.com/demo/1.0.0/artifacts/artifact.tar.gz"


class TestGetElementOpenapiArtifact:
    """Tests for get_element_openapi_artifact function."""

    def test_element_openapi_artifact_success(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b"openapi: 3.0.0\ninfo:\n  title: Test"
            result = repo.Repository._element_openapi_artifact(
                "http://example.com/artifact.yaml"
            )
            assert result["openapi"] == "3.0.0"
            assert result["info"]["title"] == "Test"

    def test_element_openapi_artifact_parse_error(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b"broken: yaml: : :"
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository._element_openapi_artifact(
                    "http://example.com/artifact.yaml"
                )
            assert "parse" in str(exc_info.value).lower()


class TestGetManifest:
    """Tests for _get_manifest function."""

    def test_get_manifest_success(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b"key: value"
            result = repo.Repository.get_manifest_by_url(
                "http://example.com/manifest.yaml"
            )
            assert result == {"key": "value"}

    def test_get_manifest_not_mapping(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b"- item1\n- item2"
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository.get_manifest_by_url("http://example.com/manifest.yaml")
            assert "not a YAML mapping" in str(exc_info.value)

    def test_get_manifest_parse_error(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b"invalid: yaml: :"
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository.get_manifest_by_url("http://example.com/manifest.yaml")
            assert "parse" in str(exc_info.value).lower()


class TestGetManifestPathFromInventory:
    """Tests for get_manifest_path_from_inventory function."""

    def test_get_manifest_path_found(self):
        inventory = {
            "manifests": [
                "/demo/1.0.0/manifests/demo.yaml",
                "/demo/1.0.0/manifests/demo-openapi.yaml",
            ]
        }
        result = repo.Repository.get_manifest_path_from_inventory(
            inventory, "demo", "http://example.com"
        )
        assert result == "/demo/1.0.0/manifests/demo.yaml"

    def test_get_manifest_path_not_found(self):
        inventory = {
            "manifests": [
                "/demo/1.0.0/manifests/other.yaml",
            ]
        }
        with pytest.raises(repo.ManifestNotFound) as exc_info:
            repo.Repository.get_manifest_path_from_inventory(
                inventory, "demo", "http://example.com"
            )
        assert "not found in inventory" in str(exc_info.value).lower()


class TestDownloadManifest:
    """Tests for download_manifest function."""

    def test_download_manifest_basic(self):
        with patch("exordos.clients.repo.Repository.check_repo"):
            with patch("exordos.clients.repo.Repository.element_url") as mock_get_url:
                mock_get_url.return_value = "http://example.com/demo"
                with patch(
                    "exordos.clients.repo.Repository.element_html"
                ) as mock_get_html:
                    mock_get_html.return_value = '<a href="1.0.0/">1.0.0/</a>'
                    with patch(
                        "exordos.clients.repo.Repository._get_latest_version"
                    ) as mock_latest:
                        mock_latest.return_value = "1.0.0"
                        with patch(
                            "exordos.clients.repo.Repository.get_inventory_url"
                        ) as mock_inv_url:
                            mock_inv_url.return_value = (
                                "http://example.com/demo/1.0.0/inventory.json"
                            )
                            with patch(
                                "exordos.clients.repo.Repository.get_element_inventory"
                            ) as mock_inv:
                                mock_inv.return_value = {
                                    "manifests": ["/demo/1.0.0/manifests/demo.yaml"]
                                }
                                with patch(
                                    "exordos.clients.repo.Repository._manifest_url"
                                ) as mock_man_url:
                                    mock_man_url.return_value = "http://example.com/demo/1.0.0/manifests/demo.yaml"
                                    with patch(
                                        "exordos.clients.repo.Repository.get_manifest"
                                    ) as mock_man:
                                        mock_man.return_value = {"version": "1.0.0"}
                                        result = repo.Repository(
                                            "http://example.com"
                                        ).get_manifest("demo", "1.0.0")
                                        assert result == {"version": "1.0.0"}


class TestDownloadManifestInventory:
    """Tests for download_manifest_inventory function."""

    def test_download_manifest_inventory_basic(self):
        with patch("exordos.clients.repo.Repository.check_repo"):
            with patch("exordos.clients.repo.Repository.element_url") as mock_get_url:
                mock_get_url.return_value = "http://example.com/demo"
                with patch(
                    "exordos.clients.repo.Repository.element_html"
                ) as mock_get_html:
                    mock_get_html.return_value = '<a href="1.0.0/">1.0.0/</a>'
                    with patch(
                        "exordos.clients.repo.Repository.get_versions"
                    ) as mock_versions:
                        mock_versions.return_value = ["1.0.0"]
                        with patch(
                            "exordos.clients.repo.Repository._get_latest_version"
                        ) as mock_latest:
                            mock_latest.return_value = "1.0.0"
                            with patch(
                                "exordos.clients.repo.Repository.get_inventory_url"
                            ) as mock_inv_url:
                                mock_inv_url.return_value = (
                                    "http://example.com/demo/1.0.0/inventory.json"
                                )
                                with patch(
                                    "exordos.clients.repo.Repository._element_inventory"
                                ) as mock_inv:
                                    mock_inv.return_value = {
                                        "manifests": ["/demo/1.0.0/manifests/demo.yaml"]
                                    }
                                    with patch(
                                        "exordos.clients.repo.Repository.get_manifest_path_from_inventory"
                                    ) as mock_path:
                                        mock_path.return_value = (
                                            "/demo/1.0.0/manifests/demo.yaml"
                                        )
                                        with patch(
                                            "exordos.clients.repo.Repository._manifest_url"
                                        ) as mock_man_url:
                                            mock_man_url.return_value = "http://example.com/demo/1.0.0/manifests/demo.yaml"
                                            with patch(
                                                "exordos.clients.repo.Repository.get_manifest_by_url"
                                            ) as mock_man:
                                                mock_man.return_value = {
                                                    "version": "1.0.0"
                                                }
                                                manifest, inventory = repo.Repository(
                                                    "http://example.com"
                                                ).get_element_inventory("demo", "1.0.0")
                                                assert manifest == {"version": "1.0.0"}
                                                assert inventory == {
                                                    "manifests": [
                                                        "/demo/1.0.0/manifests/demo.yaml"
                                                    ]
                                                }


class TestGetAllElements:
    """Tests for get_all_elements function."""

    def test_get_all_elements_success(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b'{"elements": {"demo": {}, "api": {}}}'
            result = repo.Repository("http://example.com").get_all_elements()
            assert result == ["api", "demo"]

    def test_get_all_elements_404(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_http_error = urllib.request.HTTPError(
                "http://example.com/inventory.json", 404, "Not Found", None, None
            )
            mock_get.side_effect = [mock_http_error]
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository("http://example.com").get_all_elements()
            assert "Failed to access repository" in str(exc_info.value)


class TestGetElementVersions:
    """Tests for get_element_versions function."""

    def test_get_element_versions_basic(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.side_effect = [
                b"repo root",
                b'<a href="1.0.0/">1.0.0/</a><a href="1.1.0/">1.1.0/</a><a href="latest/">latest/</a>',
            ]

            result = repo.Repository("http://example.com").get_element_versions("demo")
            assert "latest" not in result
            assert result == ["1.0.0", "1.1.0"]

    def test_get_element_versions_not_found(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.side_effect = [
                b"repo root",
                Exception("404 Not Found"),
            ]
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository("http://example.com").get_element_versions("demo")
            assert "not found" in str(exc_info.value).lower()

    def test_get_element_versions_empty(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.side_effect = [
                b"repo root",
                b"<html></html>",
            ]
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository("http://example.com").get_element_versions("demo")
            assert "No version directories" in str(exc_info.value)


class TestGetElementVersionsByInventory:
    """Tests for get_element_versions_by_inventory function."""

    def test_get_element_versions_by_inventory_success(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = (
                b'{"elements": {"demo": {"1.0.0": {}, "1.1.0": {}}}}'
            )
            result = repo.Repository(
                "http://example.com"
            ).get_element_versions_by_inventory("demo")
            assert result == ["1.0.0", "1.1.0"]

    def test_get_element_versions_by_inventory_not_found(self):
        with patch("exordos.clients.repo._http_get") as mock_get:
            mock_get.return_value = b'{"elements": {"api": {"1.0.0": {}}}}'
            with pytest.raises(repo.ManifestNotFound) as exc_info:
                repo.Repository("http://example.com").get_element_versions_by_inventory(
                    "demo"
                )
            assert "not found in inventory" in str(exc_info.value).lower()
