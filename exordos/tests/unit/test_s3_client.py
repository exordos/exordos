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
from unittest import mock

import pytest
import requests

from exordos.backup import s3_client


@pytest.fixture
def small_multipart_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(s3_client, "_MIN_MULTIPART_PART_SIZE", 5)


def _response(
    status: int = 200,
    content: bytes = b"",
    headers: dict[str, str] | None = None,
) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response._content = content
    response.headers.update(headers or {})
    return response


def _client(session: mock.MagicMock) -> s3_client.S3BackupClient:
    return s3_client.S3BackupClient(
        endpoint_url="https://s3.example.test",
        access_key="access-key",
        secret_key="secret-key",
        region="eu-central-1",
        session=session,
    )


def test_upload_small_object_signs_encoded_path_and_verifies_size() -> None:
    session = mock.MagicMock()
    session.request.side_effect = [
        _response(),
        _response(headers={"Content-Length": "6"}),
    ]

    _client(session).upload(
        io.BytesIO(b"backup"), "test-bucket", "domain/my disk+#?.qcow2", 6
    )

    put_call, head_call = session.request.call_args_list
    assert put_call.args[:2] == (
        "PUT",
        "https://s3.example.test/test-bucket/domain/my%20disk%2B%23%3F.qcow2",
    )
    assert put_call.kwargs["timeout"] == (10, 300)
    assert put_call.kwargs["allow_redirects"] is False
    assert put_call.kwargs["data"] is not None
    assert put_call.kwargs["data"].read() == b"backup"
    assert put_call.kwargs["headers"]["Authorization"].startswith(
        "AWS4-HMAC-SHA256 Credential=access-key/"
    )
    assert head_call.args[0] == "HEAD"


def test_upload_multipart_completes_and_verifies_size(
    small_multipart_parts: None,
) -> None:
    session = mock.MagicMock()
    session.request.side_effect = [
        _response(
            content=(
                b'<InitiateMultipartUploadResult xmlns="http://s3.amazonaws.com/'
                b'doc/2006-03-01/"><UploadId>upload+id/1</UploadId>'
                b"</InitiateMultipartUploadResult>"
            )
        ),
        _response(headers={"ETag": '"part-1"'}),
        _response(headers={"ETag": '"part-2"'}),
        _response(
            content=(
                b'<CompleteMultipartUploadResult xmlns="http://s3.amazonaws.com/'
                b'doc/2006-03-01/"><ETag>"complete"</ETag>'
                b"</CompleteMultipartUploadResult>"
            )
        ),
        _response(headers={"Content-Length": "6"}),
    ]

    _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 6)

    requests_made = session.request.call_args_list
    assert [call.args[0] for call in requests_made] == [
        "POST",
        "PUT",
        "PUT",
        "POST",
        "HEAD",
    ]
    assert requests_made[0].args[1].endswith("/bucket/disk?uploads=")
    assert "partNumber=1&uploadId=upload%2Bid%2F1" in requests_made[1].args[1]
    assert b"<PartNumber>2</PartNumber>" in requests_made[3].kwargs["data"]


def test_upload_multipart_rejects_embedded_completion_error(
    small_multipart_parts: None,
) -> None:
    session = mock.MagicMock()
    completion_error = (
        b"<Error><Code>AccessDenied</Code><Message>denied</Message></Error>"
    )
    session.request.side_effect = [
        _response(content=b"<Result><UploadId>upload-id</UploadId></Result>"),
        _response(headers={"ETag": '"part-1"'}),
        _response(headers={"ETag": '"part-2"'}),
        _response(content=completion_error),
        _response(status=204),
    ]

    with pytest.raises(
        s3_client.S3BackupError,
        match="multipart completion failed: AccessDenied: denied",
    ):
        _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 6)

    assert session.request.call_args_list[-1].args[0] == "DELETE"


def test_upload_multipart_retries_transient_embedded_completion_error(
    small_multipart_parts: None,
) -> None:
    session = mock.MagicMock()
    session.request.side_effect = [
        _response(content=b"<Result><UploadId>upload-id</UploadId></Result>"),
        _response(headers={"ETag": '"part-1"'}),
        _response(headers={"ETag": '"part-2"'}),
        _response(
            content=(
                b"<Error><Code>InternalError</Code><Message>retry</Message></Error>"
            )
        ),
        _response(content=b"<CompleteMultipartUploadResult/>"),
        _response(headers={"Content-Length": "6"}),
    ]

    with mock.patch("exordos.backup.s3_client.time.sleep") as sleep:
        _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 6)

    sleep.assert_called_once_with(0.5)


def test_upload_retries_timeout_and_transient_http_status() -> None:
    session = mock.MagicMock()
    uploaded_bodies: list[bytes] = []

    def request(method: str, _url: str, **kwargs: object) -> requests.Response:
        if method == "HEAD":
            return _response(headers={"Content-Length": "6"})
        body = kwargs["data"]
        assert isinstance(body, io.BytesIO)
        uploaded_bodies.append(body.read())
        if len(uploaded_bodies) == 1:
            raise requests.Timeout("timed out")
        if len(uploaded_bodies) == 2:
            return _response(
                status=503, content=b"<Error><Code>SlowDown</Code></Error>"
            )
        return _response()

    session.request.side_effect = request

    with mock.patch("exordos.backup.s3_client.time.sleep") as sleep:
        _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 6)

    assert sleep.call_args_list == [mock.call(0.5), mock.call(1.0)]
    assert uploaded_bodies == [b"backup", b"backup", b"backup"]


def test_upload_multipart_retries_same_part_body_after_connection_error(
    small_multipart_parts: None,
) -> None:
    session = mock.MagicMock()
    session.request.side_effect = [
        _response(content=b"<Result><UploadId>upload-id</UploadId></Result>"),
        requests.ConnectionError("connection lost"),
        _response(headers={"ETag": '"part-1"'}),
        _response(headers={"ETag": '"part-2"'}),
        _response(content=b"<CompleteMultipartUploadResult/>"),
        _response(headers={"Content-Length": "6"}),
    ]

    with mock.patch("exordos.backup.s3_client.time.sleep"):
        _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 6)

    retried_part = session.request.call_args_list[2]
    assert retried_part.kwargs["data"] == b"backu"


def test_upload_multipart_aborts_when_stream_ends_early(
    small_multipart_parts: None,
) -> None:
    session = mock.MagicMock()
    session.request.side_effect = [
        _response(content=b"<Result><UploadId>upload-id</UploadId></Result>"),
        _response(headers={"ETag": '"part-1"'}),
        _response(status=204),
    ]

    with pytest.raises(s3_client.S3BackupError, match="stream ended"):
        _client(session).upload(io.BytesIO(b"short"), "bucket", "disk", 6)

    assert session.request.call_args_list[-1].args[0] == "DELETE"


def test_upload_retries_head_until_object_is_visible() -> None:
    session = mock.MagicMock()
    session.request.side_effect = [
        _response(),
        _response(status=404),
        _response(headers={"Content-Length": "6"}),
    ]

    with mock.patch("exordos.backup.s3_client.time.sleep") as sleep:
        _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 6)

    sleep.assert_called_once_with(0.5)


def test_upload_aborts_when_part_has_no_etag(small_multipart_parts: None) -> None:
    session = mock.MagicMock()
    session.request.side_effect = [
        _response(content=b"<Result><UploadId>upload-id</UploadId></Result>"),
        _response(),
        _response(status=204),
    ]

    with pytest.raises(s3_client.S3BackupError, match="did not return an ETag"):
        _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 6)

    assert session.request.call_args_list[-1].args[0] == "DELETE"


@pytest.mark.parametrize("content_length", [None, "invalid", "5"])
def test_upload_rejects_missing_invalid_or_wrong_object_size(
    content_length: str | None,
) -> None:
    session = mock.MagicMock()
    headers = {} if content_length is None else {"Content-Length": content_length}
    session.request.side_effect = [_response(), _response(headers=headers)]

    with pytest.raises(s3_client.S3BackupError, match="object size"):
        _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 6)


@pytest.mark.parametrize(
    ("bucket", "key", "size", "error"),
    [
        ("", "disk", 6, "bucket and key"),
        ("bucket", "", 6, "bucket and key"),
        ("bucket", "disk", -1, "must not be negative"),
    ],
)
def test_upload_rejects_invalid_input(
    bucket: str, key: str, size: int, error: str
) -> None:
    session = mock.MagicMock()

    with pytest.raises(ValueError, match=error):
        _client(session).upload(io.BytesIO(b"backup"), bucket, key, size)

    session.request.assert_not_called()


def test_upload_rejects_object_larger_than_multipart_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = mock.MagicMock()
    monkeypatch.setattr(s3_client, "_MAX_MULTIPART_PART_SIZE", 2)
    monkeypatch.setattr(s3_client, "_MAX_MULTIPART_PARTS", 2)

    with pytest.raises(ValueError, match="too large"):
        _client(session).upload(io.BytesIO(b"backup"), "bucket", "disk", 5)

    session.request.assert_not_called()


def test_upload_scales_multipart_part_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = mock.MagicMock()
    client = _client(session)
    stream = io.BytesIO(b"x" * 100)
    monkeypatch.setattr(s3_client, "_MIN_MULTIPART_PART_SIZE", 1)
    monkeypatch.setattr(s3_client, "_MAX_MULTIPART_PARTS", 10)

    with (
        mock.patch.object(client, "_upload_multipart") as upload_multipart,
        mock.patch.object(client, "_verify_object"),
    ):
        client.upload(stream, "bucket", "disk", 100)

    upload_multipart.assert_called_once_with(stream, "bucket", "disk", 100, 10)


@pytest.mark.parametrize(
    "endpoint",
    [
        "ftp://s3.example.test",
        "https://user:password@s3.example.test",
        "https://s3.example.test/path",
        "https://s3.example.test?query=value",
    ],
)
def test_init_rejects_invalid_endpoint(endpoint: str) -> None:
    with pytest.raises(ValueError, match=r"HTTP\(S\) origin"):
        s3_client.S3BackupClient(endpoint, "access", "secret", "us-east-1")
