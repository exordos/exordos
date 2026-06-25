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

import os
import pathlib
import shutil
import tempfile

import rich_click as click

from exordos import utils
from exordos.builder import builder as simple_builder
from exordos.builder.packer import PackerBuilder
import exordos.constants as c
from exordos.logger import ClickLogger
from exordos.spec import schema


@click.command(
    "build",
    help=(
        "Build a Exordos element. The command build all images, manifests "
        "and other artifacts required for the element. The manifest in the "
        "project may be a raw YAML file or a template using Jinja2 "
        "templates. For Jinja2 templates, the following variables are "
        "available by default: \n\n"
        "- {{ version }}: version of the element \n\n"
        "- {{ name }}: name of the element \n\n"
        "- {{ manifests }}: list of manifests \n\n"
        "\n\n"
        "Additional variables can be passed using the --manifest-var "
        "options."
    ),
)
@click.option(
    "-c",
    "--exordos-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "--deps-dir",
    default=None,
    help="Directory where dependencies will be fetched",
)
@click.option(
    "-o",
    "--output-dir",
    default=pathlib.Path(c.DEF_GEN_OUTPUT_DIR_NAME),
    type=click.Path(path_type=pathlib.Path),
    help="Directory where output artifacts will be stored",
)
@click.option(
    "-i",
    "--ssh-public-key",
    multiple=True,
    type=click.Path(exists=True, path_type=pathlib.Path),
    help=(
        "Path to a public SSH key file to inject into the VM. Can be specified "
        "multiple times. If not provided, no key will be injected."
    ),
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Rebuild if the output already exists",
)
@click.option(
    "--manifest-var",
    multiple=True,
    help=(
        "Additional variables to pass to the manifest template. "
        "The format is 'key=value'. For example: --manifest-var "
        "key1=value1 --manifest-var key2=value2"
    ),
)
@click.option(
    "-v",
    "--validate",
    default=True,
    is_flag=True,
    help="Validate the manifest after building",
)
@click.argument("project_dir", type=click.Path(), default=".")
@click.pass_context
def build_cmd(
    ctx: click.Context,
    exordos_cfg_file: str,
    deps_dir: str | None,
    output_dir: pathlib.Path,
    ssh_public_key: tuple[pathlib.Path, ...],
    force: bool,
    manifest_var: tuple[str, ...],
    validate: bool,
    project_dir: str,
) -> None:
    manifest_vars = utils.convert_input_multiply(manifest_var)

    if os.path.exists(output_dir) and not force:
        click.secho(
            f"The '{output_dir}' directory already exists. Use '--force' "
            "flag to remove current artifacts and new build.",
            fg="yellow",
        )
        return
    elif os.path.exists(output_dir) and force:
        shutil.rmtree(output_dir)

    # Load SSH keys
    developer_keys = ""
    for key_path in ssh_public_key:
        with open(key_path) as f:
            developer_keys += f.read().strip() + "\n"
    if not developer_keys:
        developer_keys = utils.get_keys_by_path_or_env(None, ctx.obj.developer_key_path)

    # Find path to exordos configuration
    try:
        gen_config, gen_config_path = utils.get_exordos_config(
            project_dir, exordos_cfg_file
        )
    except FileNotFoundError:
        raise click.ClickException(
            f"Exordos configuration file not found in {project_dir}"
        )

    # NOTE(slashburygin): openapi_schema_validator is very heavy for cli, need replace it to simple validator
    spec = utils.load_spec()
    schema.validate_yaml(gen_config, spec)
    # Take all build sections from the configuration
    builds = {k: v for k, v in gen_config.items() if k.startswith("build")}
    if not builds:
        click.secho("No builds found in the configuration", fg="yellow")
        return

    version = utils.get_project_version(project_dir)

    logger = ClickLogger()
    packer_image_builder = PackerBuilder(logger)

    # Path where exordos.yaml configuration file is located
    exordos_dir = pathlib.Path(gen_config_path).parent

    for _, build_cfg in builds.items():
        builder = simple_builder.SimpleBuilder.from_config(
            exordos_dir, build_cfg, packer_image_builder, output_dir, version, logger
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            builder.fetch_dependency(deps_dir or temp_dir)
            builder.build(developer_keys, manifest_vars, validate)
