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

import io
import os
from pathlib import Path
from unittest import mock

from exordos.backup import base
from exordos.backup.s3 import S3QcowBackuper
from exordos.utils import ReaderEncryptorIO


def _backuper(region: str | None = "us-east-1") -> S3QcowBackuper:
    return S3QcowBackuper(
        endpoint_url="https://s3.example.test",
        access_key="access-key",
        secret_key="secret-key",
        host="test-host",
        bucket_name="test-bucket",
        region=region,
    )


@mock.patch("exordos.backup.s3.s3_client.S3BackupClient")
def test_upload_stream_uses_internal_client(client_class: mock.MagicMock) -> None:
    stream = io.BytesIO(b"backup")

    _backuper(region="eu-central-1")._upload_stream(stream, "domain/disk.qcow2")

    client_class.assert_called_once_with(
        endpoint_url="https://s3.example.test",
        access_key="access-key",
        secret_key="secret-key",
        region="eu-central-1",
    )
    client_class.return_value.upload.assert_called_once_with(
        stream,
        "test-bucket",
        "domain/disk.qcow2",
        6,
    )


@mock.patch("exordos.backup.s3.s3_client.S3BackupClient")
def test_upload_stream_preserves_environment_region(
    client_class: mock.MagicMock,
) -> None:
    with mock.patch.dict(os.environ, {"AWS_DEFAULT_REGION": "eu-west-1"}):
        backuper = S3QcowBackuper(
            "https://s3.example.test",
            "access-key",
            "secret-key",
            "test-host",
            "test-bucket",
            "legacy-snapshot-name",
        )

    backuper._upload_stream(io.BytesIO(b"backup"), "domain/disk.qcow2")

    assert backuper._snapshot_name == "legacy-snapshot-name"
    assert client_class.call_args.kwargs["region"] == "eu-west-1"


@mock.patch("exordos.backup.s3.s3_client.S3BackupClient")
def test_upload_stream_preserves_aws_profile_region(
    client_class: mock.MagicMock,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config"
    config_path.write_text("[profile backup]\nregion = ap-southeast-2\n")
    environment = {
        "AWS_CONFIG_FILE": str(config_path),
        "AWS_PROFILE": "backup",
    }
    with mock.patch.dict(os.environ, environment, clear=True):
        backuper = _backuper(region=None)

    backuper._upload_stream(io.BytesIO(b"backup"), "domain/disk.qcow2")

    assert client_class.call_args.kwargs["region"] == "ap-southeast-2"


@mock.patch("exordos.backup.s3.s3_client.S3BackupClient")
def test_upload_stream_encrypts_content_and_suffixes_key(
    client_class: mock.MagicMock,
) -> None:
    encryption = base.EncryptionCreds(b"0123456789abcdef", b"fedcba9876543210")

    _backuper()._upload_stream(io.BytesIO(b"backup"), "domain.xml", encryption)

    uploaded_stream, bucket, key, size = client_class.return_value.upload.call_args.args
    assert isinstance(uploaded_stream, ReaderEncryptorIO)
    assert bucket == "test-bucket"
    assert key == "domain.xml.encrypted"
    assert size == 6


def test_reader_encryptor_supports_repeated_eof_reads() -> None:
    stream = ReaderEncryptorIO(
        io.BytesIO(b"backup"),
        b"0123456789abcdef",
        b"fedcba9876543210",
    )

    encrypted = stream.read(1024)

    assert stream.read(1024) == b""
    assert stream.read(1024) == b""
    stream.seek(0)
    assert stream.read(1024) == encrypted


def test_reader_encryptor_preserves_length_and_read_size_contract() -> None:
    plaintext = b"backup payload"
    stream = ReaderEncryptorIO(
        io.BytesIO(plaintext),
        b"0123456789abcdef",
        b"fedcba9876543210",
    )

    chunks = []
    while chunk := stream.read(3):
        assert len(chunk) <= 3
        chunks.append(chunk)

    assert len(b"".join(chunks)) == len(plaintext)
