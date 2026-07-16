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

import ipaddress
import json
import pathlib
import socket
import typing as tp
import uuid as sys_uuid

import questionary
import rich_click as click

from exordos import constants as c
from exordos.clients import base_client
from exordos.common import status as status_lib
from exordos.repo import fs as repo_fs
from exordos.repo import local_server
from exordos.repo import utils as repo_utils

if tp.TYPE_CHECKING:
    from exordos.common.cmd_context import ContextObject

DEFAULT_REPO_NAME = "exordos-dev-repo"
DEFAULT_PRIORITY = 4096
DEFAULT_TIMEOUT = 600.0


def _load_build_inventory(element_dir: pathlib.Path) -> dict[str, dict]:
    build_repo = repo_fs.FSRepoDriver(str(element_dir))
    inventory_path = pathlib.Path(build_repo.elements_path) / "inventory.json"
    if not inventory_path.exists():
        raise click.ClickException(
            f"No build output found at '{element_dir}'. Run `exordos build` first."
        )
    with open(inventory_path) as f:
        return json.load(f)["elements"]


def _find_local_ip_in_network(
    network: ipaddress.IPv4Network,
) -> ipaddress.IPv4Address | None:
    """Find a local interface IP address that belongs to *network*.

    Uses a connected UDP socket so the OS selects the source interface
    for *network* without sending any packets.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.1)
            s.connect((str(network.network_address), 1))
            local_ip = ipaddress.IPv4Address(s.getsockname()[0])
            if local_ip in network:
                return local_ip
    except OSError:
        pass
    return None


def _is_local_realm(config: dict[str, tp.Any], realm: str | None = None) -> bool:
    """Check whether the given (or current) realm is local.

    A realm is considered local when:
      1. ``local: true`` is set in the realm configuration.
      2. If ``meta.cidr`` is present, a local interface has an IP in that
         network.
    """
    realm_name = realm or config.get("current-realm")
    if not realm_name:
        return False

    realm_config = (config.get("realms") or {}).get(realm_name)
    if not realm_config:
        return False

    if not realm_config.get("local", False):
        return False

    meta = realm_config.get("meta", {})
    cidr_str = meta.get("cidr")
    if cidr_str:
        try:
            network = ipaddress.IPv4Network(cidr_str)
        except ValueError:
            return False
        return _find_local_ip_in_network(network) is not None

    return True


def _get_local_host_bind(config: dict[str, tp.Any], realm: str | None = None) -> str:
    """Return the bind address for the local HTTP server.

    Uses the host IP from the given (or current) realm's ``meta.cidr`` network.
    Raises an error if no local IP matching the realm CIDR is found.
    """
    realm_name = realm or config.get("current-realm")
    if realm_name:
        realm_config = (config.get("realms") or {}).get(realm_name, {})
        cidr_str = realm_config.get("meta", {}).get("cidr")
        if cidr_str:
            try:
                network = ipaddress.IPv4Network(cidr_str)
                local_ip = _find_local_ip_in_network(network)
                if local_ip is not None:
                    return str(local_ip)
            except ValueError:
                pass
    raise click.ClickException(
        "Unable to determine a local IP address reachable from the realm. "
        "Ensure the current realm has a valid 'meta.cidr' set and this "
        "machine has an interface in that network."
    )


def _cleanup_existing_repo_elements(
    client: tp.Any,
    repository: dict[str, tp.Any],
    e_name: str,
    e_version: str,
    timeout: float,
    force: bool,
) -> None:
    existing_repo_elements = base_client.list_entities(
        client,
        c.REPOSITORY_ELEMENT_COLLECTION,
        name=e_name,
        version=e_version,
        repository=repository["uuid"],
    )
    if not existing_repo_elements:
        return

    if not force:
        raise click.ClickException(
            f"Element '{e_name}' ({e_version}) already exists in repository. "
            "Use --force to reinstall."
        )
    for element in existing_repo_elements:
        status = element.get("status")
        if status not in ("AVAILABLE",):
            base_client.action_entity(
                client,
                c.REPOSITORY_ELEMENT_COLLECTION,
                "uninstall",
                element["uuid"],
            )
            with status_lib.status_done(
                f"Cleaning up {e_name} ({e_version}), waiting to become AVAILABLE..."
            ):
                repo_utils.wait_for_repo_element(
                    client, repository["uuid"], e_name, e_version, "AVAILABLE", timeout
                )
        base_client.delete_entity(
            client, c.REPOSITORY_ELEMENT_COLLECTION, element["uuid"]
        )


def _deploy_element(
    client: tp.Any,
    repository: dict[str, tp.Any],
    e_name: str,
    e_version: str,
    timeout: float,
    force: bool = False,
) -> None:
    """Deploy an element to a realm via the given repository.

    Workflow:
        1. Clean up existing repository elements with the same name and
           version (uninstall + delete). Requires ``force`` when such
           elements exist, otherwise raises ``click.ClickException``.
        2. Refresh the repository and wait for the target element to
           become AVAILABLE.
        3. Decide how to apply the element:
            - If an element with the same name is already INSTALLED
              (any version), call ``upgrade`` on it pointing at the new
              version.
            - Otherwise call ``install`` on the new element directly.
        4. Wait for the element to become ACTIVE and report success.

    Args:
        client: API client used to communicate with the realm.
        repository: Repository entity dict the element is deployed from.
        e_name: Element name to deploy.
        e_version: Element version to deploy.
        timeout: Maximum time in seconds to wait for repository sync and
            element state transitions.
        force: When True, removes existing repository elements with the
            same name and version before deploying. When False and such
            elements exist, raises ``click.ClickException``.

    Raises:
        click.ClickException: If existing elements are found without
            ``force``, or if the element fails to reach the expected
            state within ``timeout``.
    """
    _cleanup_existing_repo_elements(
        client, repository, e_name, e_version, timeout, force
    )

    base_client.action_entity(
        client, c.REPOSITORY_COLLECTION, "refresh", repository["uuid"]
    )

    with status_lib.status_done(f"Waiting for {e_name} ({e_version}) to sync..."):
        repo_element = repo_utils.wait_for_repo_element(
            client, repository["uuid"], e_name, e_version, "AVAILABLE", timeout
        )

    # Check if an element with the same name is already installed.
    # Query the EM elements collection to see if the element exists there.
    # If so, upgrade it to the new version; otherwise install fresh.
    em_elements = base_client.list_entities(client, c.ELEMENT_COLLECTION, name=e_name)
    installed = next(iter(em_elements), None)

    if installed:
        manifest_ref = installed.get("manifest", "")
        if not manifest_ref:
            raise click.ClickException(
                f"Element {installed['name']} has no manifest reference"
            )
        manifest_uuid = manifest_ref.rstrip("/").split("/")[-1]
        base_client.action_entity(
            client,
            c.REPOSITORY_ELEMENT_COLLECTION,
            "upgrade",
            manifest_uuid,
            target=repo_element["uuid"],
        )
    else:
        base_client.action_entity(
            client,
            c.REPOSITORY_ELEMENT_COLLECTION,
            "install",
            repo_element["uuid"],
        )

    with status_lib.status_done(f"Waiting for {e_name} to become ACTIVE..."):
        repo_utils.wait_for_element_active(
            client,
            e_name,
            e_version,
            timeout,
            stable_checks=repo_utils.STABLE_CHECKS,
        )

    click.echo(
        f"Element {click.style(f'{e_name} ({e_version})', fg='green')} "
        "was deployed successfully"
    )


@click.command(
    "deploy",
    help=(
        "Deploy a built element to a realm. The element must already be "
        "built (`exordos build`). With no --repository, the local build "
        "output is served in-process and installed directly -- no push "
        "needed. With --repository, the build is pushed first, exactly "
        "like `exordos push`, then installed."
    ),
)
@click.option(
    "-e",
    "--element-dir",
    default=lambda: pathlib.Path(c.DEF_GEN_OUTPUT_DIR_NAME),
    type=click.Path(path_type=pathlib.Path),
    help="Directory where element artifacts are stored (output of `exordos build`)",
)
@click.option(
    "-t",
    "--repository",
    "repository",
    default=None,
    help=(
        "Repository name (key from the `repositories` section in "
        "~/.exordos/exordosctl.yaml). Selects push mode: push the build "
        "to this repository first, then install. If omitted, local mode "
        "is used instead (no push)."
    ),
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=sys_uuid.UUID(int=0),
    help="Project UUID, required only if the dev repository doesn't exist yet",
)
@click.option(
    "--dev-repo-name",
    default=DEFAULT_REPO_NAME,
    show_default=True,
    help="Name of the local dev repository used to publish deployed elements",
)
@click.option(
    "--dev-repo-priority",
    type=int,
    default=DEFAULT_PRIORITY,
    show_default=True,
    help="Priority of the local dev repository (0-4096)",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force push even if the element already exists (push mode only)",
)
@click.option(
    "--timeout",
    type=float,
    default=DEFAULT_TIMEOUT,
    show_default=True,
    help="Seconds to wait for repository sync and element install to complete",
)
@click.option(
    "--element",
    default=None,
    help=(
        "Name of the element to deploy from the build inventory. "
        "If omitted and multiple elements are available, an interactive "
        "prompt is shown. If only one element exists, it is selected "
        "automatically."
    ),
)
@click.option(
    "-r",
    "--realm",
    default=None,
    help=(
        "Name of the realm to deploy to. If omitted, the current realm "
        "from the configuration is used."
    ),
)
@click.option(
    "-c",
    "--exordosctl-cfg-file",
    default=c.CONFIG_FILE,
    help="Name of the exordosctl configuration file",
)
@click.pass_obj
def deploy_cmd(
    obj: "ContextObject",
    element_dir: pathlib.Path,
    repository: str | None,
    project_id: sys_uuid.UUID,
    dev_repo_name: str,
    dev_repo_priority: int,
    force: bool,
    timeout: float,
    element: str | None,
    exordosctl_cfg_file: str,
    realm: str | None,
) -> None:
    inventory_elements = _load_build_inventory(element_dir)
    if realm:
        if realm not in (obj.cfg.get("realms") or {}):
            raise click.ClickException(
                f"Realm '{realm}' not found in configuration. "
                f"Available: {', '.join(sorted((obj.cfg.get('realms') or {}).keys()))}"
            )
        obj.auth_data["realm"] = realm
    client = base_client.get_user_api_client(obj.auth_data)

    available = sorted(inventory_elements.keys())
    if element is not None:
        if element not in inventory_elements:
            raise click.ClickException(
                f"Element '{element}' not found in build inventory. "
                f"Available: {', '.join(available)}"
            )
        e_name = element
    elif len(available) > 1:
        e_name = questionary.select(
            "Select element to deploy",
            choices=available,
        ).ask()
        if not e_name:
            click.echo("No element selected, aborting")
            return
    else:
        e_name = available[0]

    # FIXME: In the build repo only a single version is available.
    e_version = tuple(inventory_elements[e_name].keys())[0]

    # Local mode: serve the build directory over a temporary HTTP server
    # and install the element directly from it. This only works with a
    # local realm where there is direct network connectivity between the
    # host and the realm's Core VM.
    if not repository and _is_local_realm(obj.cfg, realm):
        bind_host = _get_local_host_bind(obj.cfg, realm)

        with local_server.serve_directory(element_dir, bind_host) as base_url:
            url = f"{base_url}{c.ELEMENT_REPO_PATH}/"
            driver_spec = {"kind": "nginx", "url": url}
            repository_spec = repo_utils.ensure_repository(
                client,
                dev_repo_name,
                driver_spec,
                project_id,
                dev_repo_priority,
                sync_mode="copy",
            )
            _deploy_element(client, repository_spec, e_name, e_version, timeout, force)
            return

    if not repository:
        raise click.ClickException(
            "No repository specified and not a local realm. "
            "Cannot deploy without a repository."
        )

    # Push mode: full deploy cycle for remote repositories.
    # 1. Push the build artifacts to the remote repository.
    # 2. Add or actualize the repository entry in the realm.
    # 3. Install the element from the repository.
    repo_driver = repo_utils.load_repo_driver_from_settings(
        exordosctl_cfg_file,
        repository,
    )
    repo_utils.do_push(repo_driver, element_dir, force=force, latest=False)

    url = f"{repo_driver.elements_path.rstrip('/')}/"
    if not url.startswith(("http://", "https://")):
        raise click.ClickException(
            f"Push target '{repository}' isn't network-reachable "
            f"({url}). `exordos deploy` push mode requires a driver that "
            "produces an HTTP(S) URL the target realm can fetch from."
        )

    driver_spec = {"kind": "nginx", "url": url}
    repository_spec = repo_utils.ensure_repository(
        client, repository, driver_spec, project_id, dev_repo_priority, sync_mode="lazy"
    )
    _deploy_element(client, repository_spec, e_name, e_version, timeout, force)
