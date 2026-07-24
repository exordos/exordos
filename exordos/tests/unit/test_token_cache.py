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

"""Tests for token cache functionality."""

import json
import os
import tempfile
import unittest

from exordos.token_cache import TokenCache


class TestTokenCache(unittest.TestCase):
    """Tests for TokenCache class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = TokenCache(cache_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.cache.cache_file):
            os.unlink(self.cache.cache_file)
        os.rmdir(self.temp_dir)

    def test_save_and_load_tokens(self):
        """Test saving and loading tokens for a username and realm."""
        username = "testuser"
        realm = "test-realm"
        access_token = "test_access_token_123"
        refresh_token = "test_refresh_token_456"

        self.cache.save_tokens(username, realm, access_token, refresh_token)

        self.assertTrue(os.path.exists(self.cache.cache_file))
        loaded_tokens = self.cache.load_tokens(username, realm)

        self.assertIsNotNone(loaded_tokens)
        self.assertEqual(loaded_tokens["access_token"], access_token)
        self.assertEqual(loaded_tokens["refresh_token"], refresh_token)

    def test_load_for_changed_username_returns_no_tokens(self):
        """Test that a username has no tokens for another username's key."""
        self.cache.save_tokens("first-user", "test-realm", "access", "refresh")

        loaded_tokens = self.cache.load_tokens("second-user", "test-realm")

        self.assertIsNone(loaded_tokens)
        self.assertTrue(os.path.exists(self.cache.cache_file))

    def test_load_from_empty_file(self):
        """Test loading tokens when cache file is empty."""
        with open(self.cache.cache_file, "w") as f:
            json.dump({}, f)

        loaded_tokens = self.cache.load_tokens("testuser", "test-realm")
        self.assertIsNone(loaded_tokens)

    def test_save_for_changed_username_replaces_cached_tokens(self):
        """Test that saving tokens for another username replaces the cache."""
        self.cache.save_tokens(
            "first-user", "test-realm", "first-access", "first-refresh"
        )
        self.cache.save_tokens(
            "second-user", "test-realm", "second-access", "second-refresh"
        )

        with open(self.cache.cache_file, "r") as f:
            data = json.load(f)

        self.assertEqual(
            data,
            {
                "test-realm_first-user": {
                    "access_token": "first-access",
                    "refresh_token": "first-refresh",
                },
                "test-realm_second-user": {
                    "access_token": "second-access",
                    "refresh_token": "second-refresh",
                },
            },
        )

    def test_save_multiple_realm_username_keys(self):
        """Test saving tokens for multiple realm and username keys."""
        self.cache.save_tokens(
            "testuser", "first-realm", "first-access", "first-refresh"
        )
        self.cache.save_tokens(
            "testuser", "second-realm", "second-access", "second-refresh"
        )

        self.assertEqual(
            self.cache.load_tokens("testuser", "first-realm"),
            {"access_token": "first-access", "refresh_token": "first-refresh"},
        )
        self.assertEqual(
            self.cache.load_tokens("testuser", "second-realm"),
            {"access_token": "second-access", "refresh_token": "second-refresh"},
        )

    def test_clear_tokens_removes_only_realm_tokens(self):
        """Test clearing tokens for one realm preserves the other realm."""
        self.cache.save_tokens(
            "testuser", "first-realm", "first-access", "first-refresh"
        )
        self.cache.save_tokens(
            "testuser", "second-realm", "second-access", "second-refresh"
        )

        self.cache.clear_tokens("testuser", "first-realm")

        self.assertIsNone(self.cache.load_tokens("testuser", "first-realm"))
        self.assertEqual(
            self.cache.load_tokens("testuser", "second-realm"),
            {"access_token": "second-access", "refresh_token": "second-refresh"},
        )

    def test_cache_file_permissions(self):
        """Test that cache file has correct permissions."""
        username = "testuser"
        access_token = "test_access"
        refresh_token = "test_refresh"

        # Save tokens
        self.cache.save_tokens(username, "test-realm", access_token, refresh_token)

        # Verify file permissions (should be 0o600)
        file_mode = os.stat(self.cache.cache_file).st_mode & 0o777
        self.assertEqual(file_mode, 0o600)
