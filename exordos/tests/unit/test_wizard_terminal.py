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
from __future__ import annotations

import builtins
import subprocess
import sys
import textwrap

import questionary

from exordos.wizards.wizards import terminal


def test_cli_imports_without_posix_terminal_modules() -> None:
    script = textwrap.dedent(
        """
        import builtins

        original_import = builtins.__import__

        def import_without_posix_terminal_modules(name, *args, **kwargs):
            if name == "readline":
                raise ModuleNotFoundError("No module named 'readline'")
            if name == "simple_term_menu":
                raise NotImplementedError("Windows is currently not supported")
            return original_import(name, *args, **kwargs)

        builtins.__import__ = import_without_posix_terminal_modules
        import exordos.cmd.cli
        """
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_framed_prompt_without_readline_uses_initial_text(
    monkeypatch,
) -> None:
    monkeypatch.setattr(terminal, "readline", None)
    monkeypatch.setattr(builtins, "input", lambda: "")

    assert terminal.framed_prompt("Name", initial_text="example") == "example"


def test_selector_without_simple_term_menu_preserves_duplicate_index(
    monkeypatch,
) -> None:
    class Prompt:
        def unsafe_ask(self) -> int:
            return 2

    def select(title, choices):
        assert title == "Select"
        assert [choice.title for choice in choices] == ["same", "other", "same"]
        assert [choice.value for choice in choices] == [0, 1, 2]
        return Prompt()

    monkeypatch.setattr(terminal, "simple_term_menu", None)
    monkeypatch.setattr(questionary, "select", select)

    assert terminal.selector(["same", "other", "same"], "Select") == 2
