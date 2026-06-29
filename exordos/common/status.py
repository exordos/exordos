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

import contextlib
import typing as tp

import rich.console
import rich.status

from exordos.logger import ClickLogger
from exordos.logger import DummyLogger


@contextlib.contextmanager
def status_done(message: str) -> tp.Generator[rich.status.Status, None, None]:
    """Show a spinner while the body executes and print a checkmark on success.

    Silences :class:`ClickLogger` output during the block so intermediate
    log messages don't interleave with the spinner. On successful exit
    replaces the spinner line with a green checkmark followed by *message*.
    """
    _real = ClickLogger.__instance__
    ClickLogger.__instance__ = DummyLogger()
    try:
        with rich.status.Status(message, spinner="dots") as status:
            yield status
    finally:
        ClickLogger.__instance__ = _real
    rich.console.Console().print(f"[green]\u2713[/green] {message}")
