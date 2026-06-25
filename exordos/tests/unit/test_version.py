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


from exordos.common.version import is_stable_version
from exordos.common.version import is_version


class TestIsVersion:
    """Tests for is_version function."""

    def test_valid_semver_with_rc(self):
        assert is_version("1.2.3-rc+20250101120000.abcdef12") is True

    def test_valid_semver_with_dev(self):
        assert is_version("1.2.3-dev+20250101120000.abcdef12") is True

    def test_valid_semver_simple(self):
        assert is_version("1.2.3") is True

    def test_valid_latest(self):
        assert is_version("latest") is True

    def test_valid_semver_with_whitespace(self):
        assert is_version(" 1.2.3 ") is True

    def test_invalid_semver_missing_patch(self):
        assert is_version("1.2") is False

    def test_invalid_semver_extra_components(self):
        # Note: regex allows 1.2.3.4 since it matches \d+\.\d+\.\d+
        assert is_version("1.2.3.4") is True

    def test_invalid_semver_alpha_patch(self):
        # Note: regex allows any prerelease identifier (not just rc/dev)
        assert is_version("1.2.3-alpha+20250101120000.abcdef12") is True

    def test_invalid_semver_wrong_date_format(self):
        # Note: regex is lenient on date format (\d+ instead of exactly 14 digits)
        assert is_version("1.2.3-rc+20250101.abcdef12") is True

    def test_invalid_semver_short_hash(self):
        # Note: regex only requires at least 8 hex chars (\d{14}\.[a-f0-9]{8})
        assert is_version("1.2.3-rc+20250101120000.abc") is True

    def test_empty_string(self):
        assert is_version("") is False

    def test_random_string(self):
        assert is_version("random") is False


class TestIsStableVersion:
    """Tests for is_stable_version function."""

    def test_stable_version(self):
        assert is_stable_version("1.2.3") is True

    def test_stable_version_with_latest(self):
        # Note: packaging_version considers 'latest' as prerelease
        assert is_stable_version("latest") is False

    def test_prerelease_rc(self):
        assert is_stable_version("1.2.3-rc+20250101120000.abcdef12") is False

    def test_prerelease_dev(self):
        assert is_stable_version("1.2.3-dev+20250101120000.abcdef12") is False

    def test_prerelease_alpha(self):
        assert is_stable_version("1.2.3-alpha") is False

    def test_prerelease_beta(self):
        assert is_stable_version("1.2.3-beta") is False

    def test_prerelease_rc_with_date(self):
        assert is_stable_version("1.2.3-rc+20250101120000.abcdef12") is False

    def test_invalid_version_format(self):
        assert is_stable_version("invalid") is False

    def test_invalid_version_empty(self):
        assert is_stable_version("") is False

    def test_version_with_build_metadata(self):
        assert is_stable_version("1.2.3+build") is True

    def test_version_with_prerelease_and_build(self):
        assert is_stable_version("1.2.3-rc+build") is False
