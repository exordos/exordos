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
from __future__ import annotations

import io
import os
import typing as tp

from light_s3_client import Client

from exordos import logger as logger_base
from exordos import utils
from exordos.backup import base
from exordos.backup import qcow

_MIN_MULTIPART_PART_SIZE = 5 * 1024 * 1024
_MAX_MULTIPART_PARTS = 9_999


class S3QcowBackuper(qcow.AbstractQcowBackuper):
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        host: str,
        bucket_name: str,
        region: str = "us-east-1",
        snapshot_name: str = "backup_snap",
        logger: logger_base.AbstractLogger | None = None,
    ):
        self._access_key = access_key
        self._secret_key = secret_key
        self._host = host
        self._bucket_name = bucket_name
        self._endpoint_url = endpoint_url
        self._region = region
        self._logger = logger or logger_base.ClickLogger()
        self._snapshot_name = snapshot_name

    def _upload_stream(
        self,
        stream: tp.IO,
        s3_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Upload a stream to S3."""
        s3_client = Client(
            access_key=self._access_key,
            secret_key=self._secret_key,
            region=self._region,
            server=self._endpoint_url,
        )

        if encryption:
            stream = utils.ReaderEncryptorIO(stream, encryption.key, encryption.iv)
            s3_path += self.ENCRYPTED_SUFFIX

        stream.seek(0, os.SEEK_END)
        stream_size = stream.tell()
        stream.seek(0)
        part_size = max(
            _MIN_MULTIPART_PART_SIZE,
            (stream_size + _MAX_MULTIPART_PARTS - 1) // _MAX_MULTIPART_PARTS,
        )
        response = s3_client.upload_file_multipart(
            stream,
            self._bucket_name,
            s3_path,
            part_size=part_size,
        )
        if response is None or not 200 <= response.status_code < 300:
            status_code = (
                response.status_code if response is not None else "no response"
            )
            raise RuntimeError(
                f"Failed to upload {s3_path} to S3 (status: {status_code})"
            )

    def _upload_file(
        self,
        file_path: str,
        s3_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Upload a file to S3."""
        with open(file_path, "rb") as f:
            self._upload_stream(f, s3_path, encryption)

    def backup_domain_spec(
        self,
        domain_spec: str,
        domain_backup_path: str,
        domain_filename: str = "domain.xml",
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain specification."""
        self._upload_stream(
            io.BytesIO(domain_spec.encode("utf-8")),
            domain_backup_path + "/domain.xml",
            encryption,
        )

    def backup_domain_disks(
        self,
        disks: tp.Collection[str],
        domain_backup_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain disks."""
        for disk in disks:
            s3_path = os.path.join(domain_backup_path, os.path.basename(disk))
            self._upload_file(
                disk,
                s3_path,
                encryption=encryption,
            )

    def backup(
        self,
        domains: tp.Collection[str],
        compress: bool = False,
        encryption: base.EncryptionCreds | None = None,
        **kwargs: tp.Any,
    ) -> None:
        """Backup the specified domains.

        Args:
            domains: List of domain names to backup.
            compress: Whether to compress the backup.
            encryption: Encryption credentials. If it's specified,
                the backup will be encrypted.
            **kwargs: Additional keyword arguments.
        """
        backup_path = self._host + "/" + utils.backup_path("")
        self.backup_domains(backup_path, domains, encryption)

    def rotate(self, limit: int = 5) -> None:
        """Keep the last limit backups."""
        # TODO(akremenetsky): Nothing to do for rotation right now.
        # It will be implemented later.
        pass

    def cleanup(self) -> None:
        raise NotImplementedError()

    def restore(self, backup_path: str) -> None:
        raise NotImplementedError()
