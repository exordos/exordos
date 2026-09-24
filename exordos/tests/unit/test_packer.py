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

import signal
import subprocess
import threading
from unittest.mock import MagicMock

import pytest

from exordos.builder import base
from exordos.builder import packer


class TestPackerVariable:
    def test_packer_var_int(self) -> None:
        var = packer.PackerVariable(name="cpus", value=1)
        assert var.render() == "cpus = 1"

    def test_packer_var_str(self) -> None:
        var = packer.PackerVariable(name="disk_size", value="10G")
        assert var.render() == 'disk_size = "10G"'

    def test_packer_content(self) -> None:
        content = packer.PackerVariable.variable_file_content(
            {"disk_size": "10G", "cpus": 1, "memory": 1024}
        )
        assert content == 'disk_size = "10G"\ncpus = 1\nmemory = 1024'


class TestPackerBuilder:
    def test_run_pre_build_failure_is_not_masked(self, tmp_path, monkeypatch) -> None:
        def fail_pre_build(*args, **kwargs):
            raise FileNotFoundError(2, "No such file or directory", "packer")

        builder = packer.PackerBuilder()
        monkeypatch.setattr(builder, "pre_build", fail_pre_build)
        image = base.Image(script="install.sh", name="img")

        with pytest.raises(FileNotFoundError) as exc_info:
            builder.run(str(tmp_path), image, [], output_dir=str(tmp_path / "out"))

        assert exc_info.value.filename == "packer"

    def test_build_cancel_interrupts_running_process(self, monkeypatch) -> None:
        started = threading.Event()
        interrupted = threading.Event()

        class FakePopen:
            def __init__(self, args):
                self.args = args
                started.set()

            def wait(self):
                assert interrupted.wait(timeout=5)
                return 1

            def send_signal(self, sig):
                assert sig == signal.SIGINT
                interrupted.set()

        monkeypatch.setattr(packer.subprocess, "Popen", FakePopen)
        builder = packer.PackerBuilder()
        image = base.Image(script="install.sh", name="img")
        errors = []

        def build():
            try:
                builder.build("image_dir", image)
            except subprocess.CalledProcessError as e:
                errors.append(e)

        thread = threading.Thread(target=build)
        thread.start()
        assert started.wait(timeout=5)
        builder.cancel()
        thread.join(timeout=5)

        assert len(errors) == 1
        assert errors[0].returncode == 1

    def test_build_after_cancel_does_not_start_packer(self, monkeypatch) -> None:
        popen = MagicMock()
        monkeypatch.setattr(packer.subprocess, "Popen", popen)
        builder = packer.PackerBuilder()
        builder.cancel()

        with pytest.raises(RuntimeError, match="cancelled"):
            builder.build("image_dir", base.Image(script="install.sh", name="img"))

        popen.assert_not_called()
