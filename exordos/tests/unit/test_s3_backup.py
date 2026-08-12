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
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from exordos.backup import base
from exordos.backup.s3 import S3QcowBackuper
from exordos.utils import ReaderEncryptorIO


def _backuper(region: str = "us-east-1") -> S3QcowBackuper:
    return S3QcowBackuper(
        endpoint_url="https://s3.example.test",
        access_key="access-key",
        secret_key="secret-key",
        host="test-host",
        bucket_name="test-bucket",
        region=region,
    )


@patch("exordos.backup.s3.Client")
def test_upload_stream_uses_light_s3_client(client_class: MagicMock) -> None:
    client = client_class.return_value
    client.upload_file_multipart.return_value.status_code = 200
    stream = io.BytesIO(b"backup")

    _backuper(region="eu-central-1")._upload_stream(stream, "domain/disk.qcow2")

    client_class.assert_called_once_with(
        access_key="access-key",
        secret_key="secret-key",
        region="eu-central-1",
        server="https://s3.example.test",
    )
    client.upload_file_multipart.assert_called_once_with(
        stream,
        "test-bucket",
        "domain/disk.qcow2",
        part_size=5 * 1024 * 1024,
    )


@patch("exordos.backup.s3.Client")
def test_upload_stream_scales_part_size_for_large_files(
    client_class: MagicMock,
) -> None:
    client = client_class.return_value
    client.upload_file_multipart.return_value.status_code = 200
    stream = MagicMock()
    stream.tell.return_value = 100 * 1024**3

    _backuper()._upload_stream(stream, "domain/disk.qcow2")

    assert client.upload_file_multipart.call_args.kwargs["part_size"] == 10_738_493


@patch("exordos.backup.s3.Client")
def test_upload_stream_encrypts_content_and_suffixes_key(
    client_class: MagicMock,
) -> None:
    client = client_class.return_value
    client.upload_file_multipart.return_value.status_code = 200
    encryption = base.EncryptionCreds(b"0123456789abcdef", b"fedcba9876543210")

    _backuper()._upload_stream(io.BytesIO(b"backup"), "domain.xml", encryption)

    uploaded_stream, bucket, key = client.upload_file_multipart.call_args.args
    assert isinstance(uploaded_stream, ReaderEncryptorIO)
    assert bucket == "test-bucket"
    assert key == "domain.xml.encrypted"


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


@pytest.mark.parametrize("status_code", [None, 500])
@patch("exordos.backup.s3.Client")
def test_upload_stream_raises_when_upload_fails(
    client_class: MagicMock,
    status_code: int | None,
) -> None:
    client = client_class.return_value
    if status_code is None:
        client.upload_file_multipart.return_value = None
    else:
        client.upload_file_multipart.return_value.status_code = status_code

    with pytest.raises(RuntimeError, match="Failed to upload domain.xml to S3"):
        _backuper()._upload_stream(io.BytesIO(b"backup"), "domain.xml")
