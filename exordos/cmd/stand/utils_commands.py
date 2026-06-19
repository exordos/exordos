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

import os
import subprocess
import uuid as sys_uuid

import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.text import Text
import rich_click as click

from exordos import utils
from exordos.clients import base_client
from exordos.common import compute
from exordos.common import ssh
import exordos.constants as c


@click.command(name="openapi", help="tool for creating openapi spec files", hidden=True)
@click.option(
    "-u",
    "--url",
    type=click.STRING,
    required=False,
    default=None,
    help="openapi url",
)
@click.option(
    "-e",
    "--endpoint",
    required=False,
    default=None,
)
@click.argument(
    "path",
    required=False,
    type=click.Path(exists=False, dir_okay=False),
    help="Path to target file",
)
@click.pass_context
def openapi_spec(ctx: click.Context, url: str, endpoint: str, path: str) -> None:
    import ruamel.yaml

    from exordos.clients.base_client import get_user_api_client

    if url:
        response = requests.get(url, timeout=10).json()
        response.raise_for_status()
        data = response.json()
    else:
        auth_data = ctx.obj.auth_data
        if endpoint:
            auth_data["endpoint"] = endpoint
        client = get_user_api_client(auth_data)
        data = client.filter("specifications/3.0.3")

    path = path or os.path.expanduser("~/.openapi.yaml")
    with open(path, "w") as f:
        yaml = ruamel.yaml.YAML()
        yaml.indent(sequence=4, offset=2)
        yaml.dump(data, f)
    click.secho(f"OpenAPI spec written to {path}", fg="green")
    return None


@click.command("hello", help="Display hello message")
def hello() -> None:
    msg = """
▄▖       ▌     
▙▖▚▘▛▌▛▘▛▌▛▌▛▘
▙▖▞▖▙▌▌ ▙▌▙▌▄▌
"""
    click.echo(msg)


def get_grandparent_process_name() -> str:
    try:
        ppid = os.getppid()

        with open(f"/proc/{ppid}/stat", "r") as f:
            stat_info = f.read().split()
            grandparent_pid = int(stat_info[3])

        with open(f"/proc/{grandparent_pid}/comm", "r") as f:
            name = f.read().strip()
            if name:
                return name
    except (FileNotFoundError, PermissionError, ValueError, IndexError):
        pass

    try:
        result = subprocess.run(
            ["ps", "-o", "comm=", "-p", str(ppid)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        name = result.stdout.strip()
        if name:
            return name
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return "unknown"


@click.command("autocomplete_help", help="Display a autocomplete help")
def autocomplete_help() -> None:
    from exordos.utils import PROJECT_PATH

    with open(
        os.path.join(PROJECT_PATH, "exordos", "autocomplete", "autocomplete_help"),
        "r",
    ) as f:
        autocomplete_data = f.read()
    click.echo(autocomplete_data)


@click.command("autocomplete", help="update exordos autocomplete for your shell")
@click.option(
    "-s",
    "--shell",
    type=click.Choice(["bash", "zsh"]),
    required=False,
    default=None,
    help="shell kind",
)
def autocomplete(shell: str | None) -> None:
    from exordos.utils import PROJECT_PATH

    if shell is None:
        shell = get_grandparent_process_name()

    if shell == "bash":
        project_complete_path = "exordos-complete.bash"
        rc_complete_path = "bashrc-complete"
        rc_file = "~/.bashrc"
    elif shell == "zsh":
        project_complete_path = "exordos-complete.zsh"
        rc_complete_path = "zshrc-complete"
        rc_file = "~/.zshrc"
    else:
        click.echo(f"autocomplete not supported for this shell {shell}")
        return
    with open(
        os.path.join(PROJECT_PATH, c.PKG_NAME, "autocomplete", project_complete_path),
        "r",
    ) as f:
        autocomplete_data = f.read()
    os.makedirs(os.path.expanduser(c.CONFIG_DIR), exist_ok=True)
    with open(os.path.expanduser(f"{c.CONFIG_DIR}/.{project_complete_path}"), "w") as f:
        f.write(autocomplete_data)
    with open(
        os.path.join(PROJECT_PATH, c.PKG_NAME, "autocomplete", rc_complete_path),
        "r",
    ) as f:
        rc_data = f.read()
    with open(os.path.expanduser(rc_file), "a+") as f:
        f.seek(0)
        if rc_data not in f.read():
            f.write(rc_data)
    click.echo("autocomplete updated. Restart your shell")


@click.command(
    help="copy exordos element from local git repo to element nodes, "
    "example cmd: exordos sync --name empty /home/user/PycharmProjects/exordos/exordos_empty"
)
@click.option(
    "-t",
    "--target-dir",
    required=False,
    type=click.Path(),
    help="Directory to copy exordos core to",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="core",
    help="Element name",
)
@click.option(
    "--user",
    type=str,
    required=False,
    help="ssh user name",
)
@click.option(
    "--y", "-y", help="Automatically answer yes for all questions", is_flag=True
)
@click.argument("project_dir", type=click.Path(), default=".")
@click.pass_context
def sync(
    ctx: click.Context,
    target_dir: str | None,
    name: str | None,
    user: str | None,
    y: bool,
    project_dir: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    repo = utils.get_repo(project_dir)

    if not target_dir and not name:
        raise click.UsageError("Please specify target directory or element name")
    target_dir = target_dir or f"/opt/{name}/"

    element_data = base_client.get_entity(client, c.ELEMENT_COLLECTION, name)
    targets = compute.get_compute_targets_from_element(client, element_data)

    key_pair_name = ssh.generate_random_ssh_key_name()
    with ssh.generate_keys(key_pair_name) as (priv_path, pub_path):
        with open(pub_path, "r") as f:
            target_public_key = f.read()
        ssh_keys = []
        try:
            ssh_key_base_data = {
                "user": str(user or c.BOOTSTRAP_USER),
                "target_public_key": target_public_key,
            }
            for target in targets:
                target_data = ssh_key_base_data.copy()
                target_data["name"] = f"{key_pair_name}_for_{target['name']}"
                target_data["uuid"] = str(sys_uuid.uuid4())
                target_data["target"] = target["target"]
                target_data["project_id"] = target["project_id"]
                ssh_key = base_client.add_entity(
                    client, c.SSH_KEY_COLLECTION, target_data
                )
                ssh_keys.append(ssh_key)

            ssh.wait_for_ssh_keys(client, ssh_keys)

            for target in targets:
                for ip in target["ips"]:
                    if y or Confirm.ask(Text(f"Do you want to deploy code to {ip}?")):
                        dest = f"{user or c.BOOTSTRAP_USER}@{ip}:{target_dir}"
                        cmd = [
                            "rsync",
                            "-e",
                            f"ssh -i {priv_path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
                            "-avzr",
                            "--exclude=.*",
                            "--exclude=__pycache__",
                            "--exclude=output",
                            f"{repo.working_dir}/",
                            dest,
                        ]
                        try:
                            subprocess.run(
                                cmd, check=True, capture_output=True, text=True
                            )
                            click.echo(
                                f"Deployed code from {repo.working_dir} to {ip}:{target_dir}"
                            )
                        except subprocess.CalledProcessError as e:
                            raise click.ClickException(e.stderr)
                        # TODO(slashburygin): restart services after deploying code
        finally:
            for ssh_key in ssh_keys:
                base_client.delete_entity(client, c.SSH_KEY_COLLECTION, ssh_key["uuid"])
    return None


INTRODUCTION_TEXT = """
# Welcome to Exordos CLI!

Exordos CLI is now installed and ready to use. Next steps:

## Development

Initialize a new element in the current directory:

```bash
exordos init
```

Learn more: [https://exordos.github.io/exordos_core/app-developer-guide/init/](https://exordos.github.io/exordos_core/app-developer-guide/init/)

Build your project as an Exordos element:

```bash
exordos build
```

Learn more: [https://exordos.github.io/exordos_core/app-developer-guide/build/](https://exordos.github.io/exordos_core/app-developer-guide/build/)

## Local Deployment

To set up a local Exordos platform instance:

Install [dependencies](https://exordos.github.io/exordos_core/usage/local_deployment/#dependencies) and bootstrap the Exordos platform locally:

```bash
exordos bootstrap -i latest -m core --ssh-public-key /path/to/your/public/key
```

Learn more: [https://exordos.github.io/exordos_core/usage/local_deployment/](https://exordos.github.io/exordos_core/usage/local_deployment/)

## References

- **Documentation**: [https://exordos.github.io/exordos_core/](https://exordos.github.io/exordos_core/)
- **Quick Start Guide**: [https://exordos.github.io/exordos_core/app-developer-guide/](https://exordos.github.io/exordos_core/app-developer-guide/)
- **Local Deployment**: [https://exordos.github.io/exordos_core/usage/local_deployment/](https://exordos.github.io/exordos_core/usage/local_deployment/)

Use `exordos autocomplete` to enable autocomplete for your shell.

Use `exordos --help` to see all available commands.
"""


@click.command("introduction", help="Display introduction guide")
def introduction() -> None:
    console = Console()
    md = Markdown(INTRODUCTION_TEXT)
    console.print(md)


@click.command("ready_api", help="Check if Exordos api is ready to use")
@click.pass_context
def ready_api(ctx: click.Context) -> None:
    from yretry import defaults

    defaults.HTTP_RETRY_ATTEMPTS = 1
    client = base_client.get_user_api_client(ctx.obj.auth_data, timeout=(1, 1))
    try:
        client.filter("")
        click.echo("Exordos Api ready to use")
    except Exception:
        raise click.ClickException(
            f"Exordos Api ({ctx.obj.auth_data['endpoint']}) not ready to use"
        )
