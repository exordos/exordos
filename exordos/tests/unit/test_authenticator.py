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
from unittest.mock import MagicMock
from unittest.mock import Mock
import typing as tp

import pytest
from bazooka import exceptions as bazooka_exc
from requests.exceptions import HTTPError

from exordos.clients.base import CoreIamAuthenticator


class TestCoreIamAuthenticator:
    """Tests for CoreIamAuthenticator class."""

    def test_default_client_slug_constant(self):
        """Test that DEFAULT_CLIENT_SLUG is set to 'default'."""
        assert CoreIamAuthenticator.DEFAULT_CLIENT_SLUG == "default"

    def test_url_uses_default_slug(self):
        """Test that URL uses 'default' slug when default client_uuid is used."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh"
        }
        mock_client.post.return_value = mock_response

        auth = CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
        )

        # Check URL formation
        assert auth._url == "https://example.com/api/core/v1/iam/clients/default/actions/get_token/invoke"

    def test_url_with_custom_uuid(self):
        """Test that URL uses custom client_uuid when provided."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh"
        }
        mock_client.post.return_value = mock_response

        custom_uuid = "12345678-1234-1234-1234-123456789abc"
        auth = CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            client_uuid=custom_uuid,
            http_client=mock_client,
        )

        assert auth._url == f"https://example.com/api/core/v1/iam/clients/{custom_uuid}/actions/get_token/invoke"

    def test_no_client_id_in_request_data(self):
        """Test that client_id and client_secret are not in request data."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh"
        }
        mock_client.post.return_value = mock_response

        auth = CoreIamAuthenticator(
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


class TestCoreIamAuthenticatorOTP:
    """Tests for OTP (2FA) handling in CoreIamAuthenticator."""

    def test_otp_prompt_called_on_invalid_client_with_otp(self):
        """Test that otp_prompt is called when server returns invalid_client with OTP error."""
        mock_client = MagicMock()
        
        # First call fails with OTP error, second succeeds
        error_response = MagicMock()
        error_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "The provided otp code is invalid"
        }
        error_cause = MagicMock()
        error_cause.response = error_response
        
        success_response = MagicMock()
        success_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh"
        }
        
        mock_client.post.side_effect = [
            bazooka_exc.UnauthorizedError(error_cause),
            success_response
        ]
        
        otp_prompt = MagicMock(return_value="123456")
        
        auth = CoreIamAuthenticator(
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
        mock_client = MagicMock()
        
        error_response = MagicMock()
        error_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid credentials"
        }
        error_cause = MagicMock()
        error_cause.response = error_response
        
        mock_client.post.side_effect = bazooka_exc.UnauthorizedError(error_cause)
        
        otp_prompt = MagicMock(return_value="123456")
        
        auth = CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
            otp_prompt=otp_prompt,
        )
        
        with pytest.raises(bazooka_exc.UnauthorizedError):
            auth.authenticate()
        
        # OTP prompt should NOT be called
        otp_prompt.assert_not_called()

    def test_otp_prompt_not_called_when_none(self):
        """Test that no OTP prompt happens when otp_prompt is None."""
        mock_client = MagicMock()
        
        error_response = MagicMock()
        error_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "The provided otp code is invalid"
        }
        error_cause = MagicMock()
        error_cause.response = error_response
        
        mock_client.post.side_effect = bazooka_exc.UnauthorizedError(error_cause)
        
        auth = CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
            otp_prompt=None,
        )
        
        with pytest.raises(bazooka_exc.UnauthorizedError):
            auth.authenticate()

    def test_otp_case_insensitive_matching(self):
        """Test that OTP error detection is case insensitive."""
        mock_client = MagicMock()
        
        error_response = MagicMock()
        error_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "The provided OTP code is INVALID"
        }
        error_cause = MagicMock()
        error_cause.response = error_response
        
        success_response = MagicMock()
        success_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh"
        }
        
        mock_client.post.side_effect = [
            bazooka_exc.UnauthorizedError(error_cause),
            success_response
        ]
        
        otp_prompt = MagicMock(return_value="654321")
        
        auth = CoreIamAuthenticator(
            base_url="https://example.com/api/core",
            username="testuser",
            password="testpass",
            http_client=mock_client,
            otp_prompt=otp_prompt,
        )
        
        auth.authenticate()
        
        otp_prompt.assert_called_once()


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
        
        mock_prompt = MagicMock(return_value="987654")
        monkeypatch.setattr(cli.click, "prompt", mock_prompt)
        
        result = cli._get_otp_prompt(None)
        
        mock_prompt.assert_called_once_with("OTP code", hide_input=False)
        assert result == "987654"

    def test_prompts_when_otp_code_empty(self, monkeypatch):
        """Test that _get_otp_prompt prompts when empty string provided (falsy)."""
        from exordos.cmd import cli
        
        mock_prompt = MagicMock(return_value="999999")
        monkeypatch.setattr(cli.click, "prompt", mock_prompt)
        
        result = cli._get_otp_prompt("")
        
        mock_prompt.assert_called_once_with("OTP code", hide_input=False)
        assert result == "999999"
