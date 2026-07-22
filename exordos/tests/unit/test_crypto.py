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
from unittest.mock import call as mock_call
from unittest.mock import patch

from exordos.common import crypto


class TestWriteRootOwnedFile:
    """All privileged filesystem operations must go through sudo:
    callers run as a regular, sudo-capable user, not root.
    """

    def test_installs_content_via_sudo(self, tmp_path) -> None:
        dest_path = str(tmp_path / "etc" / "exordos_universal_agent" / "some.conf")
        written = {}

        def fake_run(cmd):
            if cmd[:2] == ["sudo", "install"]:
                written["content"] = open(cmd[4]).read()
                written["dest"] = cmd[5]

        with patch.object(crypto, "run_command", side_effect=fake_run) as run_mock:
            crypto.write_root_owned_file("hello world\n", dest_path, mode="644")

        assert run_mock.call_args_list[0] == mock_call(
            ["sudo", "mkdir", "-p", str(tmp_path / "etc" / "exordos_universal_agent")]
        )
        assert written["content"] == "hello world\n"
        assert written["dest"] == dest_path

    def test_installs_with_given_mode(self, tmp_path) -> None:
        dest_path = str(tmp_path / "node_private_key")

        with patch.object(crypto, "run_command") as run_mock:
            crypto.write_root_owned_file("secret\n", dest_path, mode="600")

        install_call = run_mock.call_args_list[-1][0][0]
        assert install_call[:4] == ["sudo", "install", "-m", "600"]
        assert install_call[5] == dest_path

    def test_defaults_to_a_restrictive_mode(self, tmp_path) -> None:
        # install (not cp+chmod) sets the mode atomically as it creates
        # the file - default to 600 rather than leaving it to whatever
        # cp/root's umask would otherwise produce.
        dest_path = str(tmp_path / "some_file")

        with patch.object(crypto, "run_command") as run_mock:
            crypto.write_root_owned_file("content\n", dest_path)

        install_call = run_mock.call_args_list[-1][0][0]
        assert install_call[:4] == ["sudo", "install", "-m", "600"]


class TestWriteAgentPrivateKey:
    def test_writes_with_restricted_mode(self, tmp_path) -> None:
        key_path = str(tmp_path / "node_private_key")
        written = {}

        def fake_run(cmd):
            if cmd[:2] == ["sudo", "install"]:
                written["content"] = open(cmd[4]).read()
                written["mode"] = cmd[3]

        with patch.object(crypto, "run_command", side_effect=fake_run):
            crypto.write_agent_private_key("s3cr3t==", key_path)

        assert written["content"] == "s3cr3t=="
        assert written["mode"] == "600"
