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

import os
import pathlib
import stat
from unittest import mock

from exordos.cmd.stand import commands


def test_save_admin_password_file_uses_owner_only_permissions(
    tmp_path: pathlib.Path,
) -> None:
    password_path = tmp_path / "secrets" / "admin-password"
    previous_umask = os.umask(0o002)
    try:
        commands._save_admin_password_file(
            str(password_path), "test-password", mock.Mock()
        )
    finally:
        os.umask(previous_umask)

    assert password_path.read_text(encoding="utf-8") == "test-password"
    assert stat.S_IMODE(password_path.stat().st_mode) == 0o600
