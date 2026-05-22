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

import ipaddress
import json
import os
import pathlib
import shutil
import socket
import subprocess
import time

import requests

from exordos import constants as c
from exordos import logger as logger_base
from exordos.builder import base as builder_base
from exordos.repo import base


class SimplePythonServerRepoDriver(base.AbstractRepoDriver):
    """Simple Python HTTP server driver for storing and retrieving elements.

    This driver starts a standalone Python HTTP server in the background
    to serve as a repository. Files are uploaded using HTTP PUT requests
    and downloaded using HTTP GET requests. The server runs independently
    and is managed by this driver.
    """

    def __init__(
        self,
        path: str,
        port: int = 8080,
        address: str | ipaddress.IPv4Address = "localhost",
        name: str = "proxy_repo",
        logger: logger_base.AbstractLogger = logger_base.ClickLogger(),
    ):
        """Initialize the Simple Python Server repo driver.

        Args:
            path: Local directory path where the server will serve files
            port: Port number for the HTTP server (default: 8080)
            logger: Logger instance for output
        """
        self._path = os.path.abspath(path)
        self._port = port
        self._name = name
        self._logger = logger
        self._session = requests.Session()
        self._server_process: subprocess.Popen | None = None
        self._base_url = f"http://{address}:{self._port}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def repo_path(self) -> str:
        """Get the base path for elements in the repository."""
        return f"{self._path}/{c.ELEMENT_REPO_PATH}"

    @property
    def elements_path(self) -> str:
        """Get the base path for elements in the repository."""
        return f"{self._base_url}/{c.ELEMENT_REPO_PATH}"

    def elements_inventory_path(self, element: builder_base.ElementInventory) -> str:
        """Get the inventory path for an element."""
        return (
            f"{self._base_url}/{c.ELEMENT_REPO_PATH}"
            f"/{element.name}/{element.version}/inventory.json"
        )

    def elements_inventory_path_latest(
        self, element: builder_base.ElementInventory
    ) -> str:
        """Get the inventory path for latest version of an element."""
        return f"{self._base_url}/{c.ELEMENT_REPO_PATH}/{element.name}/latest/inventory.json"

    @staticmethod
    def _is_port_in_use(port: int) -> bool:
        """Check if a port is already in use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                return result == 0
        except (socket.timeout, socket.error):
            return False

    def start_server(self) -> None:
        """Start the Python HTTP server in the background."""
        if self._server_process is not None:
            self._logger.info(f"Server already running on port {self._port}")
            return

        # Check if a Python process is already using this port
        if self._is_port_in_use(self._port):
            self._logger.info(
                f"Server already running on port {self._port} (detected existing process)"
            )
            return

        # Start the server as a background process
        self._logger.info(f"Starting Python HTTP server on port {self._port}...")
        self._server_process = subprocess.Popen(
            [
                "python3",
                "-m",
                "http.server",
                str(self._port),
                "--directory",
                self._path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=self._path,
            preexec_fn=os.setpgrp,
        )

        # Wait for server to start
        time.sleep(1)

        # Verify server is running
        if self._server_process.poll() is not None:
            stdout, stderr = self._server_process.communicate()
            self._logger.warn(f"Failed to start server: {stderr.decode('utf-8')}")

        self._logger.info(f"Server started successfully on port {self._port}")

    def stop_server(self) -> None:
        """Stop the Python HTTP server."""
        if self._server_process is None:
            return

        self._logger.info(f"Stopping server on port {self._port}...")
        self._server_process.terminate()
        self._server_process.wait(timeout=5)
        self._server_process = None

        self._logger.info("Server stopped successfully")

    def _upload_file(self, local_path: str, remote_path: str) -> None:
        """Upload a file to the server.

        Args:
            local_path: Path to the local file
            remote_path: Remote URL path
        """
        with open(local_path, "rb") as f:
            response = self._session.put(remote_path, data=f)
            response.raise_for_status()

    def _download_file(self, remote_path: str, local_path: str) -> None:
        """Download a file from the server.

        Args:
            remote_path: Remote URL path
            local_path: Local path to save the file
        """
        response = self._session.get(remote_path)
        response.raise_for_status()

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(response.content)

    def _delete_remote(self, remote_path: str) -> None:
        """Delete a file from the server.

        Args:
            remote_path: Remote URL path to delete
        """
        # Note: HTTP PUT server doesn't support DELETE by default
        # We'll parse the path and delete the file directly
        parsed_path = remote_path.replace(self._base_url, "")
        local_path = os.path.join(self._path, parsed_path.lstrip("/"))

        if os.path.exists(local_path):
            os.remove(local_path)

    def _list_remote_directory(self, remote_path: str) -> list[str]:
        """List contents of a remote directory.

        Args:
            remote_path: Remote directory URL

        Returns:
            List of items in the directory
        """
        # Parse the remote path to get local directory
        parsed_path = remote_path.replace(self._base_url, "")
        local_dir = os.path.join(self._path, parsed_path.lstrip("/"))

        if not os.path.exists(local_dir):
            return []

        items = []
        for item in os.listdir(local_dir):
            item_path = os.path.join(local_dir, item)
            if os.path.isdir(item_path):
                items.append(item)
            else:
                items.append(item)

        return items

    def init_repo(self) -> None:
        """Initialize the repo."""
        # Ensure the base path exists
        os.makedirs(self._path, exist_ok=True)

        # Start the server if not already running
        self.start_server()

        meta_url = f"{self._base_url}/exordos-repo-meta.json"

        # Check if repo is already initialized
        response = self._session.head(meta_url)
        if response.status_code == 200:
            raise base.RepoAlreadyExistsError(
                f"Repo at {self._path} already initialized."
            )

        # Create metadata
        meta = base.RepoMetaV1()
        meta_data = json.dumps(meta.to_dict(), indent=2)

        # Upload metadata file
        meta_local_path = os.path.join(self._path, "exordos-repo-meta.json")
        with open(meta_local_path, "w") as f:
            f.write(meta_data)

        # Create elements directory keeper file
        elements_keeper = os.path.join(self._path, c.ELEMENT_REPO_PATH, ".keeper")
        os.makedirs(os.path.dirname(elements_keeper), exist_ok=True)
        with open(elements_keeper, "w") as f:
            f.write("")

        self._logger.info(f"Initialized repo at {self._path}")

    def delete_repo(self) -> None:
        """Delete the repo."""
        self.stop_server()
        # Find and stop the server process if running
        if self._is_port_in_use(self._port):
            self._stop_external_server()

        # Delete elements directory
        # NOTE(slashburygin): No need to delete elements directory, because it is build's output directory
        # elements_path = os.path.join(self._path, c.ELEMENT_REPO_PATH)
        # if os.path.exists(elements_path):
        #     shutil.rmtree(elements_path)

        # Delete metadata file
        meta_path = os.path.join(self._path, "exordos-repo-meta.json")
        if os.path.exists(meta_path):
            os.remove(meta_path)

        self._logger.info(f"Deleted repo at {self._path}")

    def _stop_external_server(self) -> None:
        """Find and stop external Python HTTP server process on the same port."""
        try:
            # Find all Python processes
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, check=True
            )

            for line in result.stdout.splitlines():
                # Look for http.server with our port number
                if "http.server" in line and str(self._port) in line:
                    # Extract PID (first column)
                    parts = line.split()
                    if len(parts) >= 1:
                        pid = int(parts[1])
                        self._logger.info(
                            f"Found external server process (PID: {pid}) on port {self._port}"
                        )
                        try:
                            os.kill(pid, 15)  # SIGTERM
                            self._logger.info(f"Stopped external server process {pid}")
                        except OSError as e:
                            self._logger.warn(f"Failed to stop process {pid}: {e}")
        except subprocess.CalledProcessError as e:
            self._logger.warn(f"Failed to list processes: {e}")

    def push(
        self, element: builder_base.ElementInventory, latest: bool = False
    ) -> None:
        """Push the element to the repo."""
        element_dir = os.path.join(
            self._path, c.ELEMENT_REPO_PATH, element.name, element.version
        )

        # Check if element already exists
        inventory_path = os.path.join(element_dir, "inventory.json")
        if os.path.exists(inventory_path):
            raise base.ElementAlreadyExistsError(
                f"Element {element.name} version {element.version} already exists."
            )

        # Create element directory
        os.makedirs(element_dir, exist_ok=True)

        # Upload artifacts
        for category in element.categories():
            if artifacts := getattr(element, category):
                category_dir = os.path.join(element_dir, category)
                os.makedirs(category_dir, exist_ok=True)

                for artifact in artifacts:
                    artifact_name = os.path.basename(artifact)
                    dst_path = os.path.join(category_dir, artifact_name)
                    shutil.copyfile(artifact, dst_path)
                    self._logger.info(
                        f"Uploaded {artifact_name} to {element.name}/{element.version}"
                    )

        # Upload the inventory file
        spec = element.to_dict()
        for category in element.categories():
            spec[category] = [
                os.path.basename(artifact) for artifact in getattr(element, category)
            ]

        with open(inventory_path, "w") as f:
            json.dump(spec, f, indent=2)

        self._logger.info(f"Pushed {element.name} version {element.version}")

        if latest:
            element_dir_latest = os.path.join(
                self._path, c.ELEMENT_REPO_PATH, element.name, "latest"
            )

            os.makedirs(element_dir_latest, exist_ok=True)

            for category in element.categories():
                if artifacts := getattr(element, category):
                    category_dir = os.path.join(element_dir_latest, category)
                    os.makedirs(category_dir, exist_ok=True)

                    for artifact in artifacts:
                        artifact_name = os.path.basename(artifact)
                        dst_path = os.path.join(category_dir, artifact_name)
                        shutil.copyfile(artifact, dst_path)
                        self._logger.info(
                            f"Uploaded {artifact_name} to {element.name}/latest"
                        )

            # Upload the inventory file
            inventory_path_latest = os.path.join(element_dir_latest, "inventory.json")
            with open(inventory_path_latest, "w") as f:
                json.dump(spec, f, indent=2)

            self._logger.info(f"Pushed {element.name} version latest")

    def pull(self, element: builder_base.ElementInventory, dst_path: str) -> None:
        """Pull the element from the repo."""
        if not os.path.exists(dst_path):
            raise FileNotFoundError(f"Path {dst_path} does not exist.")

        element_dir = os.path.join(
            self._path, c.ELEMENT_REPO_PATH, element.name, element.version
        )
        inventory_path = os.path.join(element_dir, "inventory.json")

        # Check if element exists
        if not os.path.exists(inventory_path):
            raise base.RepoNotFoundError(
                f"Element {element.name} version {element.version} not found."
            )

        # Download inventory file first
        dst_inventory = os.path.join(dst_path, "inventory.json")
        shutil.copyfile(inventory_path, dst_inventory)

        # Load inventory to get the list of files
        loaded_element = builder_base.ElementInventory.load(pathlib.Path(dst_path))

        # Download all artifacts
        for category in loaded_element.categories():
            if artifacts := getattr(loaded_element, category):
                category_dir = os.path.join(dst_path, category)
                os.makedirs(category_dir, exist_ok=True)

                for artifact_path in artifacts:
                    artifact_name = os.path.basename(artifact_path)
                    remote_file = os.path.join(element_dir, category, artifact_name)
                    local_file = os.path.join(category_dir, artifact_name)

                    if os.path.exists(remote_file):
                        shutil.copyfile(remote_file, local_file)
                        self._logger.info(
                            f"Downloaded {artifact_name} from "
                            f"{element.name}/{element.version}"
                        )
                    else:
                        self._logger.warn(
                            f"File {artifact_name} not found in repository"
                        )

        self._logger.info(f"Pulled {element.name} version {element.version}")

    def remove(self, element: builder_base.ElementInventory) -> None:
        """Remove the element from the repo."""
        element_dir = os.path.join(
            self._path, c.ELEMENT_REPO_PATH, element.name, element.version
        )

        if os.path.exists(element_dir):
            import shutil

            shutil.rmtree(element_dir)
            self._logger.info(f"Removed {element.name} version {element.version}")
        else:
            self._logger.warn(
                f"Element {element.name} version {element.version} not found"
            )

    def list(self) -> dict[str, list[str]]:
        """List the elements in the repo."""
        meta_path = os.path.join(self._path, "exordos-repo-meta.json")

        # Check if repo exists
        if not os.path.exists(meta_path):
            raise base.RepoNotFoundError(f"Repo at {self._path} not found.")

        result = {}
        elements_path = os.path.join(self._path, c.ELEMENT_REPO_PATH)

        if not os.path.exists(elements_path):
            return result

        # Get list of element names
        element_names = os.listdir(elements_path)

        for name in element_names:
            if name.startswith("."):
                continue

            element_path = os.path.join(elements_path, name)
            if os.path.isdir(element_path):
                # Get list of versions for each element
                versions = [
                    v
                    for v in os.listdir(element_path)
                    if os.path.isdir(os.path.join(element_path, v)) and v != "latest"
                ]

                if versions:
                    result[name] = versions

        return result

    def inventories(self) -> dict:
        """Return the repo inventory."""
        with open(pathlib.Path(self.repo_path) / "inventory.json") as f:
            return json.load(f)["elements"]

    def inventory(
        self, element_name: str, element_version: str | None = None
    ) -> builder_base.ElementInventory:
        inventories = self.inventories()
        versions: dict = inventories.get(element_name)

        if not versions:
            raise ValueError(f"No `{element_name}` element found")

        # Get any version of element in the inventory
        if element_version is None:
            version, inventory_dict = next(iter(versions.items()))
            inventory_dir = pathlib.Path(self.repo_path) / element_name / version
            inventory = builder_base.ElementInventory.from_dict(inventory_dict)
            return inventory.replace_with_abspath(inventory_dir)

        # Get the particular version of the element
        inventory_dict = versions.get(element_version)
        if inventory_dict is None:
            raise ValueError(
                f"No `{element_name}` element with version `{element_version}` found"
            )

        inventory_dir = pathlib.Path(self.repo_path) / element_name / element_version
        inventory = builder_base.ElementInventory.from_dict(inventory_dict)
        return inventory.replace_with_abspath(inventory_dir)
