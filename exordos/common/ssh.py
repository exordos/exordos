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

from contextlib import contextmanager
import os
import shutil
import tempfile
import time
import typing as tp

import rich_click as click

from exordos.clients import base_client
import exordos.constants as c


def generate_random_ssh_key_name(prefix: str = "id_ssh") -> str:
    """Generate a random SSH key name.

    Args:
        prefix: Prefix for the key name. Defaults to "id_ssh".

    Returns:
        Random key name in format: prefix-randomhex
    """
    random_hex = os.urandom(4).hex()
    return f"{prefix}_{random_hex}"


@contextmanager
def generate_keys(
    key_pair_name: str | None = None,
    permanent: bool = False,
    key_dir: str | None = None,
) -> tp.Generator[tuple[str, str], tp.Any, None]:
    """Context manager for generating SSH key pair.

    Args:
        key_pair_name: Name for the key pair (without extension).
        permanent: If True, keys are saved to a persistent directory.
                   If False, keys are created in a temporary directory.
        key_dir: Directory for permanent keys. Defaults to ~/.ssh/ if not specified.
                 Only used when permanent=True.

    Yields:
        Tuple of (private_key_path, public_key_path)
    """

    if permanent:
        # Save to persistent directory
        target_dir = key_dir or os.path.expanduser("~/.ssh")
        os.makedirs(target_dir, exist_ok=True)
    else:
        # Use temporary directory
        target_dir = tempfile.mkdtemp()

    key_pair_name = key_pair_name
    private_key_path = os.path.join(target_dir, key_pair_name)
    public_key_path = os.path.join(target_dir, f"{key_pair_name}.pub")

    # Check if both keys already exist
    keys_exist = os.path.exists(private_key_path) and os.path.exists(public_key_path)

    if not keys_exist:
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        # Generate new keys
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        public_key = private_key.public_key()

        with open(private_key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        with open(public_key_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.OpenSSH,
                    format=serialization.PublicFormat.OpenSSH,
                )
            )

        os.chmod(private_key_path, 0o600)

    try:
        yield private_key_path, public_key_path
    finally:
        if not permanent:
            shutil.rmtree(target_dir)


def wait_for_ssh_keys(
    client, ssh_keys: list, check_interval: float = 1.0, attempts: int = 20
) -> None:
    """
    Wait until all ssh_keys have status ACTIVE
    """

    i = 0
    while not all(ssh_key["status"] == "ACTIVE" for ssh_key in ssh_keys):
        time.sleep(check_interval)
        ssh_keys = [
            base_client.get_entity(client, c.SSH_KEY_COLLECTION, ssh_key["uuid"])
            for ssh_key in ssh_keys
        ]
        i += 1
        if i > attempts:
            raise click.ClickException(
                "Timeout waiting for waiting ACTIVE status for ssh keys"
            )
