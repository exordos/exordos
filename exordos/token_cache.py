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

"""Token cache management for Exordos CLI.

This module provides functionality to cache access and refresh tokens
in ~/.exordos/tokens.json to reduce CLI execution time by avoiding
re-authentication when valid tokens are available.
"""

import json
import os
import typing as tp

import exordos.constants as c


class TokenCache:
    """Manages token cache for a username and realm.

    Tokens are stored in a JSON file at ~/.exordos/tokens.json with the
    following structure:
    {
        "<realm>_<username>": {
            "access_token": "<token>",
            "refresh_token": "<token>",
        }
    }
    """

    def __init__(self, cache_dir: str | None = None):
        """Initialize token cache.

        Args:
            cache_dir: Directory for token cache. Defaults to ~/.exordos/
        """
        self.cache_dir = cache_dir or os.path.expanduser(c.CONFIG_DIR)
        self.cache_file = os.path.join(self.cache_dir, "exordos_tokens.json")

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)

    @staticmethod
    def _cache_key(username: str, realm: str) -> str:
        """Build the cache key for a username and realm."""
        return f"{realm}_{username}"

    def load_tokens(self, username: str, realm: str) -> dict[str, tp.Any] | None:
        """Load cached tokens for a username and realm.

        Args:
            username: Username to load tokens for.
            realm: Realm to load tokens for.

        Returns:
            Dictionary with access_token and refresh_token if available,
            None if no cached tokens exist for the username and realm.
        """
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                return None

            tokens = data.get(self._cache_key(username, realm))
            if not isinstance(tokens, dict):
                return None

            return {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
            }
        except (json.JSONDecodeError, IOError):
            return None

    def save_tokens(
        self, username: str, realm: str, access_token: str, refresh_token: str
    ) -> None:
        """Save tokens to cache for a username and realm.

        Args:
            username: Username to save tokens for.
            realm: Realm to save tokens for.
            access_token: Access token to cache.
            refresh_token: Refresh token to cache.
        """
        try:
            self._ensure_cache_dir()

            # Load existing tokens or create new dict
            if os.path.exists(self.cache_file):
                try:
                    with open(self.cache_file, "r") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    data = {}
            else:
                data = {}

            # Update tokens for the username and realm.
            data[self._cache_key(username, realm)] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

            # Write back to file atomically with secure permissions (0o600)
            tmp_file = self.cache_file + ".tmp"
            fd = os.open(tmp_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            with open(fd, "w") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())

            os.replace(tmp_file, self.cache_file)
        except Exception:
            # Token caching is best-effort; do not crash the application if it fails
            pass

    def clear_tokens(self, username: str, realm: str) -> None:
        """Clear cached tokens for a username and realm.

        Args:
            username: Username whose cached tokens should be cleared.
            realm: Realm whose cached tokens should be cleared.
        """
        if not os.path.exists(self.cache_file):
            return

        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
            cache_key = self._cache_key(username, realm)
            if cache_key in data:
                del data[cache_key]
                if not data:
                    os.unlink(self.cache_file)
                    return

                tmp_file = self.cache_file + ".tmp"
                fd = os.open(tmp_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with open(fd, "w") as f:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_file, self.cache_file)
        except Exception:
            pass
