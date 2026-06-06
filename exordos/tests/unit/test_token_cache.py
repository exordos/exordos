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
        """Test saving and loading tokens for a realm."""
        realm = "test-realm"
        access_token = "test_access_token_123"
        refresh_token = "test_refresh_token_456"

        # Save tokens
        self.cache.save_tokens(realm, access_token, refresh_token)

        # Verify cache file exists
        self.assertTrue(os.path.exists(self.cache.cache_file))

        # Load tokens
        loaded_tokens = self.cache.load_tokens(realm)

        # Verify loaded tokens match saved tokens
        self.assertIsNotNone(loaded_tokens)
        self.assertEqual(loaded_tokens["access_token"], access_token)
        self.assertEqual(loaded_tokens["refresh_token"], refresh_token)

    def test_load_nonexistent_realm(self):
        """Test loading tokens for a realm that doesn't exist."""
        loaded_tokens = self.cache.load_tokens("nonexistent-realm")
        self.assertIsNone(loaded_tokens)

    def test_load_from_empty_file(self):
        """Test loading tokens when cache file is empty."""
        # Create empty cache file
        with open(self.cache.cache_file, "w") as f:
            json.dump({}, f)

        loaded_tokens = self.cache.load_tokens("test-realm")
        self.assertIsNone(loaded_tokens)

    def test_save_multiple_realms(self):
        """Test saving tokens for multiple realms."""
        realm1 = "realm1"
        realm2 = "realm2"
        access_token1 = "access1"
        refresh_token1 = "refresh1"
        access_token2 = "access2"
        refresh_token2 = "refresh2"

        # Save tokens for both realms
        self.cache.save_tokens(realm1, access_token1, refresh_token1)
        self.cache.save_tokens(realm2, access_token2, refresh_token2)

        # Load and verify both realms
        loaded_tokens1 = self.cache.load_tokens(realm1)
        loaded_tokens2 = self.cache.load_tokens(realm2)

        self.assertEqual(loaded_tokens1["access_token"], access_token1)
        self.assertEqual(loaded_tokens1["refresh_token"], refresh_token1)
        self.assertEqual(loaded_tokens2["access_token"], access_token2)
        self.assertEqual(loaded_tokens2["refresh_token"], refresh_token2)

    def test_clear_tokens(self):
        """Test clearing tokens for a realm."""
        realm = "test-realm"
        access_token = "test_access"
        refresh_token = "test_refresh"

        # Save tokens
        self.cache.save_tokens(realm, access_token, refresh_token)

        # Clear tokens
        self.cache.clear_tokens(realm)

        # Verify tokens are cleared
        loaded_tokens = self.cache.load_tokens(realm)
        self.assertIsNone(loaded_tokens)

    def test_clear_tokens_preserves_other_realms(self):
        """Test that clearing tokens for one realm preserves others."""
        realm1 = "realm1"
        realm2 = "realm2"
        access_token1 = "access1"
        refresh_token1 = "refresh1"
        access_token2 = "access2"
        refresh_token2 = "refresh2"

        # Save tokens for both realms
        self.cache.save_tokens(realm1, access_token1, refresh_token1)
        self.cache.save_tokens(realm2, access_token2, refresh_token2)

        # Clear tokens for realm1
        self.cache.clear_tokens(realm1)

        # Verify realm1 is cleared but realm2 is preserved
        loaded_tokens1 = self.cache.load_tokens(realm1)
        loaded_tokens2 = self.cache.load_tokens(realm2)

        self.assertIsNone(loaded_tokens1)
        self.assertEqual(loaded_tokens2["access_token"], access_token2)
        self.assertEqual(loaded_tokens2["refresh_token"], refresh_token2)

    def test_cache_file_permissions(self):
        """Test that cache file has correct permissions."""
        realm = "test-realm"
        access_token = "test_access"
        refresh_token = "test_refresh"

        # Save tokens
        self.cache.save_tokens(realm, access_token, refresh_token)

        # Verify file permissions (should be 0o600)
        file_mode = os.stat(self.cache.cache_file).st_mode & 0o777
        self.assertEqual(file_mode, 0o600)
