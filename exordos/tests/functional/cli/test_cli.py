# Copyright 2023 VK
#
# All Rights Reserved.
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
import tempfile

from click.globals import get_current_context
from click.testing import CliRunner

from exordos import utils
from exordos.cmd import cli
from exordos.cmd.settings import config as settings_config


class TestCli:
    def setup_method(self):
        self.runner = CliRunner()
        self._config = os.path.join(
            utils.PROJECT_PATH,
            "exordos",
            "tests",
            "functional",
            "utils",
            "exordosctl.yaml",
        )
        self._def_args = ["--config", self._config]

    def test_base_commands(self, cli_runner):

        result = cli_runner.invoke(cli.exordos)
        assert result.exit_code == 0

        result = cli_runner.invoke(cli.exordos, ["version"])
        assert result.exit_code == 0
        assert result.output

    def test_save_config(self, cli_runner, cli_config_data):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            saved = settings_config.load_config(
                get_current_context(silent=True), f.name
            )
            assert saved["current-realm"] == cli_config_data["current-realm"]

    def test_view_command(self, cli_runner):
        result = cli_runner.invoke(
            cli.exordos, self._def_args + ["settings", "view", "--raw"]
        )
        assert result.exit_code == 0
        assert "default-realm" in result.output

    def test_current_realm_command(self, cli_runner):
        result = cli_runner.invoke(
            cli.exordos, self._def_args + ["settings", "current-realm"]
        )
        assert result.exit_code == 0
        assert "default-realm" in result.output

    def test_use_realm_command(self, cli_runner, cli_config_data):
        new_realm = "slavoniy-realm"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            result = cli_runner.invoke(
                cli.exordos, ["--config", f.name, "settings", "use-realm", new_realm]
            )
            assert result.exit_code == 0
            assert f"Switched to realm '{new_realm}'" in result.output

    def test_list_realms_command(self, cli_runner):
        result = cli_runner.invoke(
            cli.exordos, self._def_args + ["settings", "list-realms"]
        )
        assert result.exit_code == 0
        assert "default-realm" in result.output

    def test_set_realm_command(self, cli_runner, cli_config_data):
        new_realm = "test-realm"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            result = cli_runner.invoke(
                cli.exordos,
                [
                    "--config",
                    f.name,
                    "settings",
                    "set-realm",
                    new_realm,
                    "--endpoint",
                    "http://example.com",
                ],
            )
            assert result.exit_code == 0
            assert f"realm '{new_realm}' set" in result.output

    def test_set_realm_with_local_and_meta(self, cli_runner, cli_config_data):
        new_realm = "test-realm-meta"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            result = cli_runner.invoke(
                cli.exordos,
                [
                    "--config",
                    f.name,
                    "settings",
                    "set-realm",
                    new_realm,
                    "--endpoint",
                    "http://example.com",
                    "--local",
                    "--meta",
                    "cidr=10.20.0.0/22",
                    "--meta",
                    "region=eu",
                ],
            )
            assert result.exit_code == 0
            assert f"realm '{new_realm}' set" in result.output

            saved = settings_config.load_config(
                get_current_context(silent=True), f.name
            )
            realm_data = saved["realms"][new_realm]
            assert realm_data["local"] is True
            assert realm_data["meta"]["cidr"] == "10.20.0.0/22"
            assert realm_data["meta"]["region"] == "eu"

    def test_delete_realm_command(self, cli_runner, cli_config_data):
        new_realm = "test-realm"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            result = cli_runner.invoke(
                cli.exordos,
                [
                    "--config",
                    f.name,
                    "settings",
                    "set-realm",
                    new_realm,
                    "--endpoint",
                    "http://example.com",
                ],
            )
            assert result.exit_code == 0

            result = cli_runner.invoke(
                cli.exordos, ["--config", f.name, "settings", "delete-realm", new_realm]
            )
            assert result.exit_code == 0

    def test_config_set_get_unset_command(self, cli_runner, cli_config_data):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            result = cli_runner.invoke(
                cli.exordos, ["--config", f.name, "settings", "set", "key", "value"]
            )
            assert result.exit_code == 0
            assert "Set key to value" in result.output

            result = cli_runner.invoke(
                cli.exordos, ["--config", f.name, "settings", "get", "key"]
            )
            assert result.exit_code == 0
            assert "value" in result.output

            result = cli_runner.invoke(
                cli.exordos, ["--config", f.name, "settings", "unset", "key"]
            )
            assert result.exit_code == 0
            assert "Unset key" in result.output

    def test_context_command(self, cli_runner, cli_config_data):
        realm = "slavoniy-realm"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            result = cli_runner.invoke(
                cli.exordos,
                [
                    "--config",
                    f.name,
                    "settings",
                    "set-context",
                    realm,
                    "--name",
                    "new-context",
                    "--user",
                    "test-user",
                    "--password",
                    "test-password",
                ],
            )
            assert result.exit_code == 0
            assert f"Context 'new-context' for realm '{realm}' set" in result.output

            result = cli_runner.invoke(
                cli.exordos, self._def_args + ["--config", f.name, "settings", "view"]
            )
            assert result.exit_code == 0
            assert "test-password" in result.output

            result = cli_runner.invoke(
                cli.exordos,
                [
                    "--config",
                    f.name,
                    "settings",
                    "rename-context",
                    "new-context",
                    "new-new-context",
                    "--realm",
                    realm,
                ],
            )
            assert result.exit_code == 0
            assert "Context 'new-context' renamed to 'new-new-context'" in result.output

            result = cli_runner.invoke(
                cli.exordos,
                [
                    "--config",
                    f.name,
                    "settings",
                    "delete-context",
                    "new-new-context",
                    "--realm",
                    realm,
                ],
            )
            assert result.exit_code == 0
            assert "Context 'new-new-context' deleted" in result.output

    def test_repo_commands(self, cli_runner):
        result = cli_runner.invoke(cli.exordos, ["repo", "--help"])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "update" in result.output

    def test_repo_elements_commands(self, cli_runner):
        result = cli_runner.invoke(cli.exordos, ["repo", "elements", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "show" in result.output

    def test_list_repos_command(self, cli_runner):
        result = cli_runner.invoke(
            cli.exordos, self._def_args + ["settings", "repo", "list"]
        )
        assert result.exit_code == 0
        assert "default-repo" in result.output
        assert "another-repo" in result.output
        # password is masked by default
        assert "admin" not in result.output

    def test_list_repos_show_sensitive(self, cli_runner):
        result = cli_runner.invoke(
            cli.exordos,
            self._def_args + ["settings", "repo", "list", "--show-sensitive"],
        )
        assert result.exit_code == 0
        assert "admin" in result.output

    def test_add_repo_command(self, cli_runner, cli_config_data):
        new_repo = "test-repo"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            result = cli_runner.invoke(
                cli.exordos,
                [
                    "--config",
                    f.name,
                    "settings",
                    "repo",
                    "add",
                    new_repo,
                    "--driver",
                    "nginx",
                    "--url",
                    "http://example.com:8080/",
                    "--username",
                    "user",
                    "--password",
                    "pass",
                ],
            )
            assert result.exit_code == 0
            assert f"repo '{new_repo}' set" in result.output

    def test_delete_repo_command(self, cli_runner, cli_config_data):
        repo = "another-repo"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            settings_config.save_config(cli_config_data, f.name)
            result = cli_runner.invoke(
                cli.exordos, ["--config", f.name, "settings", "repo", "delete", repo]
            )
            assert result.exit_code == 0
            assert f"repo '{repo}' deleted" in result.output
