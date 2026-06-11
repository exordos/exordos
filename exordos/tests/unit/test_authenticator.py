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
import unittest
from unittest import mock

import bazooka
import pytest

from exordos.clients import base


class TestPasswordPrompt:
    """Tests for PasswordPrompt class."""

    def test_caches_password_on_first_call(self):
        """Test that password is cached after first call."""
        with mock.patch(
            "exordos.clients.base.click.prompt", return_value="secret123"
        ) as mock_prompt:
            prompt = base.PasswordPrompt()

            # First call should invoke the prompt function
            result1 = prompt()
            assert result1 == "secret123"
            assert mock_prompt.call_count == 1

            # Second call should use cached value
            result2 = prompt()
            assert result2 == "secret123"
            assert mock_prompt.call_count == 1

    def test_returns_same_cached_value(self):
        """Test that multiple calls return the same cached value."""
        with mock.patch("exordos.clients.base.click.prompt", return_value="secret123"):
            prompt = base.PasswordPrompt()

            results = [prompt() for _ in range(5)]
            assert all(r == "secret123" for r in results)


class TestCoreIamAuthenticator:
    """Tests for CoreIamAuthenticator class."""

    def test_default_client_slug_constant(self):
        """Test that DEFAULT_CLIENT_SLUG is set to 'default'."""
        assert base.DEFAULT_CLIENT_SLUG == "default"

    def test_url_uses_default_slug(self):
        """Test that URL uses 'default' slug when default client_uuid is used."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
        }
        mock_client.post.return_value = mock_response

        auth = base.CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
        )

        # Check URL formation
        assert (
            auth._url
            == "https://example.com/api/core/v1/iam/clients/default/actions/get_token/invoke"
        )

    def test_url_with_custom_uuid(self):
        """Test that URL uses custom client_uuid when provided."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
        }
        mock_client.post.return_value = mock_response

        custom_uuid = "12345678-1234-1234-1234-123456789abc"
        auth = base.CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            client_uuid=custom_uuid,
            http_client=mock_client,
        )

        assert (
            auth._url
            == f"https://example.com/api/core/v1/iam/clients/{custom_uuid}/actions/get_token/invoke"
        )

    def test_no_client_id_in_request_data(self):
        """Test that client_id and client_secret are not in request data."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
        }
        mock_client.post.return_value = mock_response

        auth = base.CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
        )

        auth.authenticate()

        # Check that client_id and client_secret are NOT in _data
        assert "client_id" not in auth._data
        assert "client_secret" not in auth._data
        # But other fields are present
        assert auth._data["grant_type"] == "password"
        assert auth._data["username"] == "testuser"
        assert auth._data["password"] == "testpass"

    def test_password_prompt_deferred_until_authenticate(self):
        """Test that password_prompt is called only when authentication starts."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
        }
        mock_client.post.return_value = mock_response
        password_prompt = mock.MagicMock(return_value="testpass")

        auth = base.CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password_prompt=password_prompt,
            http_client=mock_client,
        )

        password_prompt.assert_not_called()

        auth.authenticate()

        password_prompt.assert_called_once()
        _, kwargs = mock_client.post.call_args
        assert kwargs["data"]["password"] == "testpass"


class TestCoreIamAuthenticatorOTP:
    """Tests for OTP (2FA) handling in CoreIamAuthenticator."""

    def test_otp_prompt_called_on_invalid_client_with_otp(self):
        """Test that otp_prompt is called when server returns invalid_client with OTP error."""
        mock_client = mock.MagicMock()

        # First call fails with OTP error, second succeeds
        error_response = mock.MagicMock()
        error_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "The provided otp code is invalid",
        }
        error_cause = mock.MagicMock()
        error_cause.response = error_response

        success_response = mock.MagicMock()
        success_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
        }

        mock_client.post.side_effect = [
            bazooka.exceptions.UnauthorizedError(error_cause),
            success_response,
        ]

        otp_prompt = mock.MagicMock(return_value="123456")

        auth = base.CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
            otp_prompt=otp_prompt,
        )

        auth.authenticate()

        # OTP prompt should be called
        otp_prompt.assert_called_once()

        # Second call should include X-OTP header
        calls = mock_client.post.call_args_list
        assert len(calls) == 2
        second_call_headers = calls[1][1].get("headers", {})
        assert second_call_headers.get("X-OTP") == "123456"

    def test_otp_prompt_not_called_without_otp_error(self):
        """Test that otp_prompt is not called for regular auth errors."""
        mock_client = mock.MagicMock()

        error_response = mock.MagicMock()
        error_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid credentials",
        }
        error_cause = mock.MagicMock()
        error_cause.response = error_response

        mock_client.post.side_effect = bazooka.exceptions.UnauthorizedError(error_cause)

        otp_prompt = mock.MagicMock(return_value="123456")

        auth = base.CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
            otp_prompt=otp_prompt,
        )

        with pytest.raises(bazooka.exceptions.UnauthorizedError):
            auth.authenticate()

        # OTP prompt should NOT be called
        otp_prompt.assert_not_called()

    def test_otp_prompt_not_called_when_none(self):
        """Test that no OTP prompt happens when otp_prompt is None."""
        mock_client = mock.MagicMock()

        error_response = mock.MagicMock()
        error_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "The provided otp code is invalid",
        }
        error_cause = mock.MagicMock()
        error_cause.response = error_response

        mock_client.post.side_effect = bazooka.exceptions.UnauthorizedError(error_cause)

        auth = base.CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
            otp_prompt=None,
        )

        with pytest.raises(bazooka.exceptions.UnauthorizedError):
            auth.authenticate()

    def test_otp_case_insensitive_matching(self):
        """Test that OTP error detection is case insensitive."""
        mock_client = mock.MagicMock()

        error_response = mock.MagicMock()
        error_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "The provided OTP code is INVALID",
        }
        error_cause = mock.MagicMock()
        error_cause.response = error_response

        success_response = mock.MagicMock()
        success_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
        }

        mock_client.post.side_effect = [
            bazooka.exceptions.UnauthorizedError(error_cause),
            success_response,
        ]

        otp_prompt = mock.MagicMock(return_value="654321")

        auth = base.CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
            otp_prompt=otp_prompt,
        )

        auth.authenticate()

        otp_prompt.assert_called_once()


class TestCoreIamAuthenticatorTokenCache(unittest.TestCase):
    """Tests for token caching in CoreIamAuthenticator."""

    def test_caches_tokens_after_authentication(self):
        """Test that tokens are cached after successful authentication."""
        from unittest.mock import MagicMock
        from unittest.mock import patch

        from exordos.token_cache import TokenCache

        realm = "test-realm"

        # Mock HTTP client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "cached_access_token",
            "refresh_token": "cached_refresh_token",
        }
        mock_client.post.return_value = mock_response

        # Mock TokenCache to verify save_tokens is called
        mock_cache = MagicMock(spec=TokenCache)

        with patch("exordos.clients.base.TokenCache", return_value=mock_cache):
            # Create authenticator with realm
            auth = base.CoreIamAuthenticator(
                base_url="https://example.com/api/core",
                username="testuser",
                password="testpass",
                http_client=mock_client,
                realm=realm,
            )

            # Authenticate
            auth.authenticate()

            # Verify save_tokens was called with correct arguments
            mock_cache.save_tokens.assert_called_once_with(
                realm,
                "cached_access_token",
                "cached_refresh_token",
            )

    def test_loads_cached_tokens_on_init(self):
        """Test that cached tokens are loaded on initialization."""
        from unittest.mock import MagicMock
        from unittest.mock import patch

        from exordos.token_cache import TokenCache

        realm = "test-realm"
        cached_access = "pre_cached_access"
        cached_refresh = "pre_cached_refresh"

        # Mock HTTP client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }
        mock_client.post.return_value = mock_response

        # Mock TokenCache to return cached tokens
        mock_cache = MagicMock(spec=TokenCache)
        mock_cache.load_tokens.return_value = {
            "access_token": cached_access,
            "refresh_token": cached_refresh,
        }

        with patch("exordos.clients.base.TokenCache", return_value=mock_cache):
            # Create authenticator with realm but no explicit tokens
            # It should load from cache
            auth = base.CoreIamAuthenticator(
                base_url="https://example.com/api/core",
                username="testuser",
                password="testpass",
                http_client=mock_client,
                realm=realm,
            )

            # Verify load_tokens was called (may be called multiple times in the __init__)
            self.assertTrue(mock_cache.load_tokens.called)

            # After all initialization, the final values should be from cache
            self.assertEqual(auth._access_token, cached_access)
            self.assertEqual(auth._refresh_token, cached_refresh)


class TestGetOtpPrompt:
    """Tests for _get_otp_prompt function from cli module."""

    def test_returns_otp_code_when_provided(self):
        """Test that _get_otp_prompt returns otp_code when provided."""
        from exordos.cmd.cli import _get_otp_prompt

        result = _get_otp_prompt("123456")
        assert result == "123456"

    def test_prompts_when_otp_code_none(self, monkeypatch):
        """Test that _get_otp_prompt prompts user when otp_code is None."""
        from exordos.cmd import cli

        mock_prompt = mock.MagicMock(return_value="987654")
        monkeypatch.setattr(cli.click, "prompt", mock_prompt)

        result = cli._get_otp_prompt(None)

        mock_prompt.assert_called_once_with("OTP code", hide_input=False)
        assert result == "987654"

    def test_prompts_when_otp_code_empty(self, monkeypatch):
        """Test that _get_otp_prompt prompts when empty string provided (falsy)."""
        from exordos.cmd import cli

        mock_prompt = mock.MagicMock(return_value="999999")
        monkeypatch.setattr(cli.click, "prompt", mock_prompt)

        result = cli._get_otp_prompt("")

        mock_prompt.assert_called_once_with("OTP code", hide_input=False)
        assert result == "999999"
