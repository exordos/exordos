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
    """Manages token cache for multiple realms.

    Tokens are stored in a JSON file at ~/.exordos/tokens.json with the
    following structure:
    {
        "<realm_name>": {
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

    def load_tokens(self, realm: str) -> dict[str, tp.Any] | None:
        """Load cached tokens for a specific realm.

        Args:
            realm: Realm name to load tokens for.

        Returns:
            Dictionary with access_token and refresh_token if available,
            None if no cached tokens exist for the realm.
        """
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                return None

            realm_tokens = data.get(realm)
            if not isinstance(realm_tokens, dict):
                return None

            return {
                "access_token": realm_tokens.get("access_token"),
                "refresh_token": realm_tokens.get("refresh_token"),
            }
        except (json.JSONDecodeError, IOError):
            return None

    def save_tokens(self, realm: str, access_token: str, refresh_token: str) -> None:
        """Save tokens to cache for a specific realm.

        Args:
            realm: Realm name to save tokens for.
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

            # Update tokens for the realm
            data[realm] = {
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

    def clear_tokens(self, realm: str) -> None:
        """Clear cached tokens for a specific realm.

        Args:
            realm: Realm name to clear tokens for.
        """
        if not os.path.exists(self.cache_file):
            return

        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
            if realm in data:
                del data[realm]
                # Write back to file atomically with secure permissions (0o600)
                tmp_file = self.cache_file + ".tmp"
                fd = os.open(tmp_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with open(fd, "w") as f:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_file, self.cache_file)
        except Exception:
            pass
