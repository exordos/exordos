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

import datetime
import hashlib
import hmac
import logging
import time
import typing as tp
from urllib import parse
from xml.etree import ElementTree

import requests

_LOG = logging.getLogger(__name__)

_MIN_MULTIPART_PART_SIZE = 5 * 1024 * 1024
_MAX_MULTIPART_PART_SIZE = 5 * 1024 * 1024 * 1024
_MAX_MULTIPART_PARTS = 10_000
_REQUEST_TIMEOUT = (10, 300)
_MAX_REQUEST_ATTEMPTS = 4
_BACKOFF_FACTOR = 0.5
_TRANSIENT_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
_TRANSIENT_ERROR_CODES = frozenset(
    {"InternalError", "RequestTimeout", "ServiceUnavailable", "SlowDown"}
)


class S3BackupError(RuntimeError):
    """An S3 request required to create a backup failed."""


class S3BackupClient:
    """Minimal path-style S3 client used only for backup uploads."""

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: str,
        session: requests.Session | None = None,
    ) -> None:
        endpoint = parse.urlsplit(endpoint_url.rstrip("/"))
        if (
            endpoint.scheme not in {"http", "https"}
            or not endpoint.netloc
            or endpoint.username is not None
            or endpoint.password is not None
            or endpoint.path not in {"", "/"}
            or endpoint.query
            or endpoint.fragment
        ):
            raise ValueError("S3 endpoint must be an HTTP(S) origin without a path")

        self._endpoint = f"{endpoint.scheme}://{endpoint.netloc}"
        self._host = endpoint.netloc
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._session = session or requests.Session()

    def upload(
        self,
        stream: tp.BinaryIO,
        bucket: str,
        key: str,
        size: int,
    ) -> None:
        """Upload a seekable stream and verify the resulting object size."""
        if not bucket or not key:
            raise ValueError("S3 bucket and key must not be empty")
        if size < 0:
            raise ValueError("S3 object size must not be negative")

        part_size = max(
            _MIN_MULTIPART_PART_SIZE,
            (size + _MAX_MULTIPART_PARTS - 1) // _MAX_MULTIPART_PARTS,
        )
        if part_size > _MAX_MULTIPART_PART_SIZE:
            raise ValueError("S3 object is too large for a multipart upload")

        stream.seek(0)
        if size <= part_size:
            self._put_object(stream, bucket, key, size)
        else:
            self._upload_multipart(stream, bucket, key, size, part_size)

        self._verify_object(bucket, key, size)

    def _put_object(
        self, stream: tp.BinaryIO, bucket: str, key: str, size: int
    ) -> None:
        path = self._object_path(bucket, key)
        body_hash = self._stream_hash(stream, size)
        url = self._endpoint + path
        for attempt in range(_MAX_REQUEST_ATTEMPTS):
            stream.seek(0)
            headers = self._signed_headers("PUT", path, "", body_hash)
            try:
                response = self._session.request(
                    "PUT",
                    url,
                    headers=headers,
                    data=stream,
                    timeout=_REQUEST_TIMEOUT,
                    allow_redirects=False,
                )
            except (requests.ConnectionError, requests.Timeout) as error:
                if attempt + 1 == _MAX_REQUEST_ATTEMPTS:
                    raise S3BackupError(f"S3 PUT request failed: {error}") from error
                self._sleep(attempt)
                continue
            except requests.RequestException as error:
                raise S3BackupError(f"S3 PUT request failed: {error}") from error

            if response.status_code == 200:
                return
            if (
                response.status_code in _TRANSIENT_STATUS_CODES
                and attempt + 1 < _MAX_REQUEST_ATTEMPTS
            ):
                self._sleep(attempt)
                continue
            code, message = self._xml_error(response.content)
            raise S3BackupError(
                f"S3 PUT request failed with HTTP {response.status_code}: "
                f"{code}: {message}"
            )

        raise AssertionError("Unreachable S3 PUT state")

    def _upload_multipart(
        self,
        stream: tp.BinaryIO,
        bucket: str,
        key: str,
        size: int,
        part_size: int,
    ) -> None:
        upload_id = self._create_multipart_upload(bucket, key)
        completed = False
        try:
            parts: list[tuple[int, str]] = []
            remaining = size
            part_number = 1
            while remaining:
                if part_number > _MAX_MULTIPART_PARTS:
                    raise S3BackupError("S3 multipart upload exceeds 10,000 parts")

                body = self._read_exact(stream, min(part_size, remaining))
                response = self._request(
                    "PUT",
                    bucket,
                    key,
                    query={"partNumber": str(part_number), "uploadId": upload_id},
                    body=body,
                )
                etag = response.headers.get("ETag")
                if not etag:
                    raise S3BackupError(
                        f"S3 did not return an ETag for part {part_number}"
                    )
                parts.append((part_number, etag))
                remaining -= len(body)
                part_number += 1

            self._complete_multipart_upload(bucket, key, upload_id, parts)
            completed = True
        except BaseException:
            if not completed:
                self._abort_multipart_upload(bucket, key, upload_id)
            raise

    def _create_multipart_upload(self, bucket: str, key: str) -> str:
        response = self._request(
            "POST",
            bucket,
            key,
            query={"uploads": ""},
            retry=False,
        )
        upload_id = self._xml_value(response.content, "UploadId")
        if not upload_id:
            raise S3BackupError("S3 did not return a multipart upload ID")
        return upload_id

    def _complete_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        parts: list[tuple[int, str]],
    ) -> None:
        root = ElementTree.Element("CompleteMultipartUpload")
        for part_number, etag in parts:
            part = ElementTree.SubElement(root, "Part")
            ElementTree.SubElement(part, "ETag").text = etag
            ElementTree.SubElement(part, "PartNumber").text = str(part_number)
        body = ElementTree.tostring(root, encoding="utf-8")

        for attempt in range(_MAX_REQUEST_ATTEMPTS):
            response = self._request(
                "POST",
                bucket,
                key,
                query={"uploadId": upload_id},
                body=body,
            )
            root_name = self._xml_root_name(response.content)
            if root_name == "CompleteMultipartUploadResult":
                return
            if root_name != "Error":
                raise S3BackupError(
                    "S3 returned an invalid multipart completion response"
                )

            code, message = self._xml_error(response.content)
            if (
                code not in _TRANSIENT_ERROR_CODES
                or attempt + 1 == _MAX_REQUEST_ATTEMPTS
            ):
                raise S3BackupError(
                    f"S3 multipart completion failed: {code}: {message}"
                )
            self._sleep(attempt)

        raise AssertionError("Unreachable multipart completion state")

    def _abort_multipart_upload(self, bucket: str, key: str, upload_id: str) -> None:
        try:
            self._request(
                "DELETE",
                bucket,
                key,
                query={"uploadId": upload_id},
                expected_statuses=frozenset({204}),
            )
        except S3BackupError as error:
            _LOG.warning("Failed to abort S3 multipart upload: %s", error)

    def _verify_object(self, bucket: str, key: str, expected_size: int) -> None:
        response = self._request(
            "HEAD",
            bucket,
            key,
            retry_statuses=_TRANSIENT_STATUS_CODES | {404},
        )
        content_length = response.headers.get("Content-Length")
        try:
            actual_size = int(content_length) if content_length is not None else None
        except ValueError as error:
            raise S3BackupError("S3 returned an invalid object size") from error
        if actual_size != expected_size:
            raise S3BackupError(
                f"S3 object size mismatch: expected {expected_size}, got {actual_size}"
            )

    def _request(
        self,
        method: str,
        bucket: str,
        key: str,
        *,
        query: dict[str, str] | None = None,
        body: bytes = b"",
        expected_statuses: frozenset[int] = frozenset({200}),
        retry: bool = True,
        retry_statuses: frozenset[int] = _TRANSIENT_STATUS_CODES,
    ) -> requests.Response:
        path = self._object_path(bucket, key)
        canonical_query = self._canonical_query(query or {})
        url = self._endpoint + path
        if canonical_query:
            url += "?" + canonical_query
        attempts = _MAX_REQUEST_ATTEMPTS if retry else 1

        for attempt in range(attempts):
            body_hash = hashlib.sha256(body).hexdigest()
            headers = self._signed_headers(method, path, canonical_query, body_hash)
            try:
                response = self._session.request(
                    method,
                    url,
                    headers=headers,
                    data=body,
                    timeout=_REQUEST_TIMEOUT,
                    allow_redirects=False,
                )
            except (requests.ConnectionError, requests.Timeout) as error:
                if attempt + 1 == attempts:
                    raise S3BackupError(
                        f"S3 {method} request failed: {error}"
                    ) from error
                self._sleep(attempt)
                continue
            except requests.RequestException as error:
                raise S3BackupError(f"S3 {method} request failed: {error}") from error

            if response.status_code in expected_statuses:
                return response
            if response.status_code in retry_statuses and attempt + 1 < attempts:
                self._sleep(attempt)
                continue

            code, message = self._xml_error(response.content)
            raise S3BackupError(
                f"S3 {method} request failed with HTTP {response.status_code}: "
                f"{code}: {message}"
            )

        raise AssertionError("Unreachable S3 request state")

    def _signed_headers(
        self,
        method: str,
        path: str,
        canonical_query: str,
        payload_hash: str,
    ) -> dict[str, str]:
        now = datetime.datetime.now(datetime.timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")
        canonical_headers = (
            f"host:{self._host}\n"
            f"x-amz-content-sha256:{payload_hash}\n"
            f"x-amz-date:{amz_date}\n"
        )
        signed_headers = "host;x-amz-content-sha256;x-amz-date"
        canonical_request = "\n".join(
            [
                method,
                path,
                canonical_query,
                canonical_headers,
                signed_headers,
                payload_hash,
            ]
        )
        credential_scope = f"{date_stamp}/{self._region}/s3/aws4_request"
        string_to_sign = "\n".join(
            [
                "AWS4-HMAC-SHA256",
                amz_date,
                credential_scope,
                hashlib.sha256(canonical_request.encode()).hexdigest(),
            ]
        )
        signing_key = self._signing_key(date_stamp)
        signature = hmac.new(
            signing_key, string_to_sign.encode(), hashlib.sha256
        ).hexdigest()
        authorization = (
            "AWS4-HMAC-SHA256 "
            f"Credential={self._access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        return {
            "Authorization": authorization,
            "Host": self._host,
            "X-Amz-Content-SHA256": payload_hash,
            "X-Amz-Date": amz_date,
        }

    def _signing_key(self, date_stamp: str) -> bytes:
        key = hmac.new(
            f"AWS4{self._secret_key}".encode(), date_stamp.encode(), hashlib.sha256
        ).digest()
        for value in (self._region, "s3", "aws4_request"):
            key = hmac.new(key, value.encode(), hashlib.sha256).digest()
        return key

    @staticmethod
    def _object_path(bucket: str, key: str) -> str:
        encoded_bucket = parse.quote(bucket, safe="-_.~")
        encoded_key = parse.quote(key, safe="/-_.~")
        return f"/{encoded_bucket}/{encoded_key}"

    @staticmethod
    def _canonical_query(query: dict[str, str]) -> str:
        encoded = [
            (parse.quote(key, safe="-_.~"), parse.quote(value, safe="-_.~"))
            for key, value in query.items()
        ]
        return "&".join(f"{key}={value}" for key, value in sorted(encoded))

    @staticmethod
    def _read_exact(stream: tp.BinaryIO, size: int) -> bytes:
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            chunk = stream.read(remaining)
            if not chunk:
                raise S3BackupError(
                    "Backup stream ended before the expected object size"
                )
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    @staticmethod
    def _stream_hash(stream: tp.BinaryIO, size: int) -> str:
        digest = hashlib.sha256()
        remaining = size
        stream.seek(0)
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            if not chunk:
                raise S3BackupError(
                    "Backup stream ended before the expected object size"
                )
            digest.update(chunk)
            remaining -= len(chunk)
        return digest.hexdigest()

    @staticmethod
    def _xml_root_name(content: bytes) -> str | None:
        try:
            return ElementTree.fromstring(content).tag.rsplit("}", 1)[-1]
        except ElementTree.ParseError:
            return None

    @staticmethod
    def _xml_value(content: bytes, name: str) -> str | None:
        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError:
            return None
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == name:
                return element.text
        return None

    @classmethod
    def _xml_error(cls, content: bytes) -> tuple[str, str]:
        code = cls._xml_value(content, "Code") or "UnknownError"
        message = cls._xml_value(content, "Message") or content.decode(errors="replace")
        return code, message

    @staticmethod
    def _sleep(attempt: int) -> None:
        time.sleep(_BACKOFF_FACTOR * (2**attempt))
