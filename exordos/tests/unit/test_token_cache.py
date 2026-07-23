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
        """Test saving and loading tokens for a username."""
        username = "testuser"
        access_token = "test_access_token_123"
        refresh_token = "test_refresh_token_456"

        self.cache.save_tokens(username, access_token, refresh_token)

        self.assertTrue(os.path.exists(self.cache.cache_file))
        loaded_tokens = self.cache.load_tokens(username)

        self.assertIsNotNone(loaded_tokens)
        self.assertEqual(loaded_tokens["access_token"], access_token)
        self.assertEqual(loaded_tokens["refresh_token"], refresh_token)

    def test_load_for_changed_username_deletes_cache_file(self):
        """Test that loading tokens for another username invalidates the cache."""
        self.cache.save_tokens("first-user", "access", "refresh")

        loaded_tokens = self.cache.load_tokens("second-user")

        self.assertIsNone(loaded_tokens)
        self.assertFalse(os.path.exists(self.cache.cache_file))

    def test_load_from_empty_file(self):
        """Test loading tokens when cache file is empty."""
        with open(self.cache.cache_file, "w") as f:
            json.dump({}, f)

        loaded_tokens = self.cache.load_tokens("testuser")
        self.assertIsNone(loaded_tokens)

    def test_save_for_changed_username_replaces_cached_tokens(self):
        """Test that saving tokens for another username replaces the cache."""
        self.cache.save_tokens("first-user", "first-access", "first-refresh")
        self.cache.save_tokens("second-user", "second-access", "second-refresh")

        with open(self.cache.cache_file, "r") as f:
            data = json.load(f)

        self.assertEqual(
            data,
            {
                "second-user": {
                    "access_token": "second-access",
                    "refresh_token": "second-refresh",
                }
            },
        )

    def test_clear_tokens(self):
        """Test clearing tokens for a username."""
        username = "testuser"
        self.cache.save_tokens(username, "test_access", "test_refresh")

        self.cache.clear_tokens(username)

        self.assertFalse(os.path.exists(self.cache.cache_file))

    def test_cache_file_permissions(self):
        """Test that cache file has correct permissions."""
        username = "testuser"
        access_token = "test_access"
        refresh_token = "test_refresh"

        # Save tokens
        self.cache.save_tokens(username, access_token, refresh_token)

        # Verify file permissions (should be 0o600)
        file_mode = os.stat(self.cache.cache_file).st_mode & 0o777
        self.assertEqual(file_mode, 0o600)
