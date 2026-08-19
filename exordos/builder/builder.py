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

import glob
import gzip
import itertools
import json
import os
import pathlib
import shutil
import subprocess
import tarfile
import tempfile
import typing as tp
import uuid as sys_uuid

import rich_click as click
import yaml

from exordos import constants as c
from exordos.builder import base
from exordos.logger import AbstractLogger
from exordos.logger import DummyLogger
from exordos.repo import fs as repo_fs
from exordos.spec import schema


def _urn_image(uuid: str | sys_uuid.UUID) -> str:
    return f"urn:images:{uuid}"


class SimpleBuilder:
    """Simple element builder."""

    DEPS_KEY = "deps"
    ELEMENTS_KEY = "elements"

    def __init__(
        self,
        exordos_dir: pathlib.Path,
        deps: list[base.AbstractDependency],
        elements: list[base.Element],
        image_builder: base.AbstractImageBuilder,
        logger: tp.Optional[AbstractLogger] = None,
        elements_output_dir: pathlib.Path = pathlib.Path(c.DEF_GEN_OUTPUT_DIR_NAME),
        version: str = "0.0.0",
    ) -> None:
        super().__init__()
        self._deps = deps
        self._elements = elements
        self._image_builder = image_builder
        self._exordos_dir = exordos_dir
        self._logger = logger or DummyLogger()
        self._elements_output_dir = elements_output_dir
        self._version = version
        self._inventories = []
        self._repo_dir = None

        if not os.path.exists(self._elements_output_dir):
            os.makedirs(self._elements_output_dir)

    def _build_config_artifact(
        self,
        config_artifact: base.Config | base.Artifact,
        output_dir: pathlib.Path,
    ) -> pathlib.Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        dst_path = output_dir / pathlib.Path(config_artifact.path).name
        shutil.copy(config_artifact.abs_path, dst_path)

        return pathlib.Path(dst_path.name)

    def _archive_dir_zst(
        self,
        src_dir: pathlib.Path,
        dst_path: pathlib.Path,
        flatten: bool = False,
    ) -> None:
        """Archive a directory with tar and compress it with zstd.

        When ``flatten`` is True, the directory contents are placed at the
        root of the archive without the wrapper directory.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tar_path = pathlib.Path(tmp_dir) / f"{src_dir.name}.tar"
            with tarfile.open(tar_path, "w") as tar:
                if flatten:
                    for child in sorted(src_dir.iterdir()):
                        tar.add(child, arcname=child.name)
                else:
                    tar.add(src_dir, arcname=src_dir.name)

            subprocess.run(
                ["zstd", "-9", "-T0", "-f", "-o", dst_path, tar_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _build_generated_artifact(
        self,
        generated: base.GeneratedArtifact,
        output_dir: pathlib.Path,
    ) -> list[pathlib.Path]:
        """Run a script and collect the artifacts it produces."""
        if not os.access(generated.script, os.X_OK):
            raise ValueError(f"Artifact script is not executable: {generated.script}")

        output_dir.mkdir(parents=True, exist_ok=True)

        self._logger.info(f"Running artifact script: {generated.script}")
        subprocess.run([generated.script], cwd=generated.work_dir, check=True)

        result_paths: list[pathlib.Path] = []
        for pattern in generated.patterns:
            matches = sorted(glob.glob(pattern, root_dir=generated.work_dir))
            if not matches:
                raise ValueError(
                    f"No files matched artifact pattern '{pattern}' in "
                    f"{generated.work_dir}"
                )

            for match in matches:
                src = pathlib.Path(generated.work_dir) / match
                if src.is_dir():
                    dst_name = f"{src.name}.tar.zst"
                    self._archive_dir_zst(
                        src, output_dir / dst_name, flatten=generated.flatten
                    )
                    result_paths.append(pathlib.Path(dst_name))
                else:
                    shutil.copy(src, output_dir / src.name)
                    result_paths.append(pathlib.Path(src.name))

        return result_paths

    def _convert_image(
        self,
        raw_src: pathlib.Path,
        img_name: str,
        fmt: str,
    ) -> str:
        """Convert a RAW image to the requested format and return the final path."""
        if fmt == "raw":
            # Do nothing
            return f"{img_name}.raw"
        elif fmt == "qcow2":
            self._logger.info(f"Converting {img_name} to qcow2")
            tgt = raw_src.parent / f"{img_name}.qcow2"
            subprocess.run(
                [
                    "qemu-img",
                    "convert",
                    "-f",
                    "raw",
                    "-O",
                    "qcow2",
                    "-c",
                    "-o",
                    "preallocation=off,compression_type=zstd",
                    raw_src,
                    tgt,
                ],
                check=True,
            )
            return tgt.name
        elif fmt == "gz":
            self._logger.info(f"Compressing {img_name} to {img_name}.raw.gz")
            tgt = raw_src.parent / f"{img_name}.raw.gz"
            with (
                open(raw_src, "rb") as f_in,
                gzip.open(tgt, "wb", compresslevel=5) as f_out,
            ):
                shutil.copyfileobj(f_in, f_out)
            return tgt.name
        elif fmt == "zst":
            # Using subprocess with zstd utility instead of Python's compression.zstd
            # because: 1) it works on Python <3.14, 2) allows multi-threading via -T0
            self._logger.info(f"Compressing {img_name} to {img_name}.raw.zst")
            tgt = raw_src.parent / f"{img_name}.raw.zst"
            subprocess.run(
                [
                    "zstd",
                    "-9",  # The trade-off between speed and size
                    "-T0",
                    "-f",
                    "-o",
                    tgt,
                    raw_src,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return tgt.name
        else:
            raise ValueError(f"Unsupported image format: {fmt}")

    def _build_image(
        self,
        img: base.Image,
        output_dir: pathlib.Path,
        developer_keys: str | None = None,
    ) -> list[pathlib.Path]:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._image_builder.run(
                temp_dir,
                img,
                self._deps,
                developer_keys,
                str(output_dir),
            )

        # A builder always produces a RAW image. Convert to each requested format.
        raw_src = output_dir / f"{img.name}.raw"

        result_paths = []
        for fmt in img.formats:
            path = self._convert_image(raw_src, img.name, fmt)
            result_paths.append(pathlib.Path(path))

        if "raw" not in img.formats:
            os.unlink(raw_src)

        return result_paths

    def _build_images(
        self,
        element: base.Element,
        output_dir: pathlib.Path,
        developer_keys: str | None = None,
    ) -> list[pathlib.Path]:
        """Build images for the element."""
        image_paths = []
        for img in element.images:
            _paths = self._build_image(img, output_dir, developer_keys)
            image_paths.extend(_paths)

        return image_paths

    def _build_images_dict(
        self,
        element_images: list[base.Image],
        element_name: str,
        element_version: str,
    ) -> dict[str, str]:
        """Build images dictionary with URI mappings for manifest templates.

        Creates a mapping from image name variants to URIs that can be used in
        Jinja2 manifest templates. The mapping includes:
        - Base name without extension (for single images or ZST images)
        - Full name with dots and hyphens replaced by underscores

        Args:
            element_images: List of Image objects from the element
            element_name: Name of the element
            element_version: Version of the element

        Returns:
            Dictionary mapping image name variants to URIs.

        Example:
            If element_images has formats ["qcow2", "raw"] with name "foo":
            {
                "foo": "urn:images:{uuid}",
                "foo_qcow2": "urn:images:{uuid}",
                "foo_raw": "urn:images:{uuid}"
            }

            If element_images has formats ["raw.zst", "qcow2"] with name "bar":
            {
                "bar": "urn:images:{uuid}",
                "bar_raw_zst": "urn:images:{uuid}",
                "bar_qcow2": "urn:images:{uuid}"
            }
        """
        images: dict[str, str] = {}

        image_names = list(
            itertools.chain.from_iterable(img.names for img in element_images)
        )

        def add_image(name: str, include_no_ext: bool = False) -> None:
            idx = base.ElementInventory.compute_index_entry(
                "images",
                element_name,
                element_version,
                pathlib.Path(name),
            )
            if include_no_ext:
                # Remove all known image extensions from the end
                base_name = name
                for ext in [".raw.zst", ".raw.gz", ".raw", ".qcow2", ".gz", ".zst"]:
                    if base_name.endswith(ext):
                        base_name = base_name[: -len(ext)]
                        break
                image_no_ext = base_name.replace("-", "_").lower()
                images[image_no_ext] = _urn_image(idx)
            image_ext = name.replace("-", "_").replace(".", "_").lower()
            images[image_ext] = _urn_image(idx)

        if len(image_names) == 1:
            add_image(image_names[0], include_no_ext=True)
        # ZST image is more preferred. Allow to use it without extension
        elif any(i.endswith(".zst") for i in image_names):
            zst_added = False
            for image_name in image_names:
                if image_name.endswith(".zst"):
                    add_image(image_name, include_no_ext=not zst_added)
                    zst_added = True
                else:
                    add_image(image_name)
        else:
            for image_name in image_names:
                add_image(image_name)

        return images

    def _build_manifest(
        self,
        element: base.Element,
        manifests_dir: pathlib.Path,
        manifest_vars: dict[str, tp.Any] | None = None,
    ) -> list[pathlib.Path]:
        """Build manifests for the element."""
        orig_manifest_path = self._exordos_dir / element.manifest

        # Compute images indexes
        images = self._build_images_dict(
            element.images,
            manifest_vars["name"],
            manifest_vars["version"],
        )

        # Render templated manifests
        jinja2_extensions = (".jinja2", ".j2")

        if str(element.manifest).endswith(jinja2_extensions):
            # Render Jinja2 manifest
            with open(orig_manifest_path) as f:
                import jinja2

                template = jinja2.Template(f.read())
            rendered_manifest = template.render(
                manifests=[element.manifest.name],
                images=images,
                **manifest_vars,
            )

            # Remove extension from the manifest name
            manifest_name = ".".join(element.manifest.name.split(".")[:-1])
            manifest_path = manifests_dir / manifest_name

            # Save rendered manifest
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(manifest_path, "w") as f:
                f.write(rendered_manifest)
        else:
            manifest_path = manifests_dir / element.manifest.name
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(orig_manifest_path, manifest_path)

        return [pathlib.Path(manifest_path.name)]

    def fetch_dependency(self, deps_dir: str) -> None:
        """Fetch common dependencies for elements."""
        self._logger.important("Fetching dependencies")
        for dep in self._deps:
            self._logger.info(f"Fetching dependency: {dep}")
            dep.fetch(deps_dir)

    def select_element(
        self,
        name: str,
        manifest_vars: dict[str, tp.Any] | None = None,
    ) -> bool:
        """Restrict this builder to elements with the requested name."""
        manifest_vars = manifest_vars or {}
        selected = []

        for element in self._elements:
            if not element.manifest:
                continue

            element_name = manifest_vars.get("name") or element.name(self._exordos_dir)
            if element_name and element_name.strip() == name:
                selected.append(element)

        self._elements = selected
        return bool(selected)

    def build_element(
        self,
        element: base.Element,
        repo_dir: pathlib.Path,
        developer_keys: str | None = None,
        manifest_vars: dict[str, tp.Any] | None = None,
        validate: bool = False,
    ) -> base.ElementInventory | None:
        """Build an element."""
        self._logger.info(f"Building element: {element}")
        configs, artifacts = [], []

        # If manifest is not provided, build only images and return.
        # We used the `--only-images` flag earlier to skip manifest processing.
        if not element.manifest:
            self._build_images(element, repo_dir, developer_keys)
            return None

        # Prepare manifest variables
        manifest_vars = (manifest_vars or {}).copy()
        manifest_vars["version"] = self._version

        # Determine element name
        name: str = manifest_vars.get("name") or element.name(self._exordos_dir)
        if not name:
            raise click.UsageError("Element name is not provided")

        if name.startswith("{"):
            raise click.UsageError(
                "Specify manifest name using --manifest-var name=value"
            )
        name = name.strip()
        manifest_vars["name"] = name
        manifest_vars["version"] = self._version

        element_dir = repo_dir / name / self._version
        element_dir.mkdir(parents=True, exist_ok=True)

        # Render manifest
        manifests_dir = element_dir / "manifests"
        manifests = self._build_manifest(element, manifests_dir, manifest_vars)

        if validate:
            for manifest in manifests:
                path = self._repo_dir / name / self._version / "manifests" / manifest
                with open(path, "r") as f:
                    manifest = yaml.safe_load(f)
                schema.validate_manifest(
                    manifest, manifest_vars.get("repository", c.ELEMENT_REPO_URL)
                )

        # Build artifacts and configs
        seen_artifact_names: set[str] = set()
        for artifact in element.artifacts:
            artifact_dir = element_dir / "artifacts"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            if isinstance(artifact, base.GeneratedArtifact):
                _paths = self._build_generated_artifact(artifact, artifact_dir)
            else:
                _paths = [self._build_config_artifact(artifact, artifact_dir)]

            for _path in _paths:
                if _path.name in seen_artifact_names:
                    raise ValueError(f"Duplicate artifact name: {_path.name}")
                seen_artifact_names.add(_path.name)
            artifacts.extend(_paths)
        for config in element.configs:
            config_dir = element_dir / "configs"
            config_dir.mkdir(parents=True, exist_ok=True)
            _path = self._build_config_artifact(config, config_dir)
            configs.append(_path)

        # Build images
        images_dir = element_dir / "images"
        images = self._build_images(element, images_dir, developer_keys)

        inventory = base.ElementInventory(
            name=name,
            version=self._version,
            images=images,
            manifests=manifests,
            configs=configs,
            artifacts=artifacts,
        )
        inventory.save(element_dir)
        return inventory

    def build(
        self,
        developer_keys: str | None = None,
        manifest_vars: dict[str, tp.Any] | None = None,
        validate: bool = False,
    ) -> None:
        """Build all elements."""
        self._logger.important("Building elements")
        self._repo_dir = self._elements_output_dir

        # Initialize repository if any element has a manifest
        if any(e.manifest for e in self._elements):
            repo = repo_fs.FSRepoDriver(self._elements_output_dir)
            repo.init_repo()
            self._repo_dir = pathlib.Path(repo.elements_path)

        for e in self._elements:
            inventory = self.build_element(
                e,
                self._repo_dir,
                developer_keys,
                manifest_vars,
                validate,
            )
            if inventory:
                self._inventories.append(inventory)

        # Save inventories
        # TODO(akremenetsky): It's internal logic of repository and it should be
        # moved into repository models one day.
        if self._inventories:
            data = {"elements": {}}
            for inventory in self._inventories:
                data["elements"][inventory.name] = {
                    inventory.version: inventory.to_dict()
                }

            with open(self._repo_dir / "inventory.json", "w") as f:
                json.dump(data, f, indent=2, sort_keys=True)

    @classmethod
    def from_config(
        cls,
        exordos_dir: pathlib.Path,
        build_config: dict[str, tp.Any],
        image_builder: base.AbstractImageBuilder,
        elements_output_dir: pathlib.Path,
        version: str = "0.0.0",
        logger: AbstractLogger | None = None,
    ) -> "SimpleBuilder":
        """Create a builder from configuration."""
        # Prepare dependencies entries but do not fetch them
        deps = []
        dep_configs = build_config.get(cls.DEPS_KEY, [])
        for dep in dep_configs:
            dep_item = base.AbstractDependency.find_dependency(dep, exordos_dir)
            if dep_item is None:
                raise ValueError(f"Unable to handle dependency: {dep}. Unknown type.")
            deps.append(dep_item)

        # Prepare elements
        element_configs = build_config.get(cls.ELEMENTS_KEY, [])
        elements = [
            base.Element.from_config(elem, exordos_dir) for elem in element_configs
        ]

        if not elements:
            raise ValueError("No elements found in configuration")

        return cls(
            exordos_dir,
            deps,
            elements,
            image_builder,
            logger,
            elements_output_dir,
            version,
        )
