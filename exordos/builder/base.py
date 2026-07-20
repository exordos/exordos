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

import abc
import dataclasses
import json
import os
import pathlib
import typing as tp
import uuid

import yaml

from exordos import constants as c


@dataclasses.dataclass
class Image:
    """Image representation."""

    ENV_IMG_PREFIX = "GEN_IMG_FORMAT"
    DEF_IMG_FORMAT = "raw"

    script: str
    profile: c.ImageProfileType = "ubuntu_24"
    profile_version: str = "latest"
    formats: list[str] = dataclasses.field(default_factory=lambda: ["raw"])
    name: str | None = None
    envs: list[str] | None = None
    override: dict[str, tp.Any] | None = None

    @property
    def format(self) -> str:
        """Return the primary (first) image format."""
        return self.formats[0]

    @property
    def names(self) -> tuple[str, ...]:
        """Return all image names with their extensions."""
        if self.name is None:
            return tuple()

        result = []
        for fmt in self.formats:
            if fmt in ("gz", "zst"):
                # Compression formats are applied to raw images
                result.append(f"{self.name}.raw.{fmt}")
            else:
                result.append(f"{self.name}.{fmt}")
        return tuple(result)

    @classmethod
    def _resolve_formats(cls, raw_format_str: str) -> list[str]:
        """Resolve image formats from a comma-separated string."""
        raw_format_str = raw_format_str.strip()
        if raw_format_str.startswith(cls.ENV_IMG_PREFIX):
            # Extract key and default image format if they present
            if "=" in raw_format_str:
                env_key, img_formats = raw_format_str.split("=", 1)
            else:
                env_key, img_formats = raw_format_str, None

            try:
                img_formats = os.environ[env_key]
            except KeyError:
                if not img_formats:
                    raise ValueError(
                        f"Image format {raw_format_str} is not found in the environment "
                        f"and no default value is provided"
                    )

            # Save extracted formats back to the string
            raw_format_str = img_formats

        formats = list(dict.fromkeys(f.strip() for f in raw_format_str.split(",")))

        # Validate formats
        for f in formats:
            if f not in c.ImageFormatType.__args__:
                raise ValueError(
                    f"Invalid image format: {f}, "
                    f"expected one of {c.ImageFormatType.__args__}"
                )

        return formats

    @classmethod
    def from_config(
        cls, image_config: dict[str, tp.Any], work_dir: pathlib.Path
    ) -> "Image":
        """Create an image from configuration."""
        image_config = image_config.copy()
        script = image_config.pop("script")
        if not os.path.isabs(script):
            script = os.path.join(work_dir, script)

        # Determine the image format(s). The value may be a comma-separated
        # string of formats, e.g. "raw, qcow2" or "gz, qcow2".
        raw_format_value = str(image_config.pop("format", cls.DEF_IMG_FORMAT))
        formats = cls._resolve_formats(raw_format_value)

        return cls(script=script, formats=formats, **image_config)


@dataclasses.dataclass
class Config:
    """Config representation."""

    abs_path: str
    path: str

    @classmethod
    def from_config(cls, config: dict[str, tp.Any], work_dir: pathlib.Path) -> "Config":
        """Create a config from configuration."""
        abs_path = os.path.join(work_dir, config["path"])
        return cls(abs_path=abs_path, path=config["path"])


@dataclasses.dataclass
class Artifact:
    """Artifact representation."""

    abs_path: str
    path: str

    @classmethod
    def from_config(
        cls, config: dict[str, tp.Any], work_dir: pathlib.Path
    ) -> "Artifact":
        """Create an artifact from configuration."""
        abs_path = os.path.join(work_dir, config["path"])
        return cls(abs_path=abs_path, path=config["path"])


@dataclasses.dataclass
class GeneratedArtifact:
    """Artifact produced by running a script/executable.

    The script is executed in ``work_dir`` and its resulting files are
    matched via glob ``patterns`` (also resolved against ``work_dir``).
    """

    script: str
    work_dir: str
    patterns: list[str]

    @classmethod
    def from_config(
        cls, config: dict[str, tp.Any], work_dir: pathlib.Path
    ) -> "GeneratedArtifact":
        """Create a generated artifact from configuration."""
        if "path" in config:
            raise ValueError(
                "Artifact configuration cannot have both 'path' and 'script'"
            )

        script = config["script"]
        if not os.path.isabs(script):
            script = os.path.join(work_dir, script)
        script = os.path.abspath(script)

        artifact_work_dir = config.get("work_dir", ".")
        if not os.path.isabs(artifact_work_dir):
            artifact_work_dir = os.path.join(work_dir, artifact_work_dir)
        artifact_work_dir = os.path.abspath(artifact_work_dir)

        patterns = config["artifacts"]
        if not patterns:
            raise ValueError("'artifacts' patterns are required for a script artifact")

        return cls(script=script, work_dir=artifact_work_dir, patterns=patterns)


@dataclasses.dataclass
class Element:
    """Element representation in the exordos.yaml configuration."""

    manifest: pathlib.Path | None = None
    images: list[Image] = dataclasses.field(default_factory=list)
    artifacts: list[Artifact | GeneratedArtifact] = dataclasses.field(
        default_factory=list
    )
    configs: list[Config] = dataclasses.field(default_factory=list)

    def __str__(self):
        if self.manifest:
            return f"<Element manifest={self.manifest}>"

        if self.images and len(self.images) > 0:
            name = ", ".join([f"{i.profile}" for i in self.images])
            return f"<Element images={name}>"

        return f"<Element {str(self)}>"

    def name(self, exordos_dir: pathlib.Path) -> str | None:
        with open(exordos_dir / self.manifest, "r") as f:
            manifest = yaml.safe_load(f)
        return manifest.get("name")

    @classmethod
    def from_config(
        cls, element_config: tp.Dict[str, tp.Any], work_dir: pathlib.Path
    ) -> "Element":
        """Create an element from configuration."""
        image_configs = element_config.pop("images", [])
        images = [Image.from_config(img, work_dir) for img in image_configs]

        config_configs = element_config.pop("configs", [])
        configs = [Config.from_config(config, work_dir) for config in config_configs]

        artifacts_configs = element_config.pop("artifacts", [])
        artifacts = [
            GeneratedArtifact.from_config(artifact, work_dir)
            if "script" in artifact
            else Artifact.from_config(artifact, work_dir)
            for artifact in artifacts_configs
        ]

        # Convert manifest to Path if present
        manifest = element_config.pop("manifest", None)
        if manifest is not None:
            manifest = pathlib.Path(manifest)

        return cls(
            images=images,
            configs=configs,
            artifacts=artifacts,
            manifest=manifest,
            **element_config,
        )


@dataclasses.dataclass
class ElementInventory:
    """Element inventory."""

    file_name = pathlib.Path("inventory.json")

    # Base namespace for the element index. Per-category namespaces are
    # derived from this one so each category gets a stable, distinct UUID
    # space.
    _INDEX_NAMESPACE = uuid.uuid5(
        uuid.UUID("3b621be9-1acf-42db-a686-6f3bede48527"), "exordos"
    )

    name: str
    version: str
    images: tp.Collection[pathlib.Path] = dataclasses.field(default_factory=tuple)
    manifests: tp.Collection[pathlib.Path] = dataclasses.field(default_factory=tuple)
    configs: tp.Collection[pathlib.Path] = dataclasses.field(default_factory=tuple)
    templates: tp.Collection[pathlib.Path] = dataclasses.field(default_factory=tuple)
    artifacts: tp.Collection[pathlib.Path] = dataclasses.field(default_factory=tuple)
    # Derived automatically in __post_init__; never set externally.
    index: dict[str, dict[str, str]] = dataclasses.field(
        init=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        """Compute the element index automatically."""
        self.index = self.compute_index()

    @classmethod
    def categories(cls) -> tuple[str, str, str, str, str]:
        return "images", "manifests", "configs", "templates", "artifacts"

    @classmethod
    def compute_index_entry(
        cls, category: str, name: str, version: str, path: pathlib.Path
    ) -> str:
        """Compute a single index key for one item.

        Returns the UUID (as a string) that maps to ``path.name`` under
        the given ``category`` for element ``name``/``version``.
        """
        namespace = uuid.uuid5(cls._INDEX_NAMESPACE, category)
        key = f"{name}-{version}-{path.name}"
        return str(uuid.uuid5(namespace, key))

    def compute_index(self) -> dict[str, dict[str, str]]:
        """Build the index: ``{category: {uuid: file_name}}``.

        Each category gets its own UUID namespace derived from the base
        namespace. The key for an item is ``uuid5(category_namespace,
        f"{name}-{version}-{basename}")``.
        """
        index: dict[str, dict[str, str]] = {}
        for category in self.categories():
            entries: dict[str, str] = {}
            for path in getattr(self, category):
                entries[
                    self.compute_index_entry(category, self.name, self.version, path)
                ] = path.name
            index[category] = entries
        return index

    def to_dict(self) -> dict[str, tp.Any]:
        data = {
            "name": self.name,
            "version": self.version,
            "index": self.index,
        }
        for category in self.categories():
            data[category] = [str(p) for p in getattr(self, category)]
        return data

    def replace_with_abspath(self, inventory_dir: pathlib.Path) -> "ElementInventory":
        """Create a copy of inventory but with abs path."""
        kwargs = {
            "name": self.name,
            "version": self.version,
        }
        for category in self.categories():
            abs_paths = []
            for p in getattr(self, category):
                if p.is_absolute():
                    abs_paths.append(p)
                else:
                    # Resolve to absolute path relative to inventory_dir
                    abs_paths.append((inventory_dir / category / p).resolve())
            kwargs[category] = abs_paths
        return ElementInventory(**kwargs)

    def save(self, path: pathlib.Path) -> None:
        """Save the element inventory to a path."""
        with open(path / self.file_name, "w") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

    @classmethod
    def load(cls, path: pathlib.Path, index: int = 0) -> "ElementInventory":
        """Create an element inventory from a path."""
        if path.is_dir():
            path = path / cls.file_name

        with open(path, "r") as f:
            inventory = json.load(f)

        # Backward compatibility: support both single
        # inventory and list of inventories
        if isinstance(inventory, list):
            try:
                inventory = inventory[index]
            except IndexError:
                raise ValueError(
                    f"Inventory index {index} not found in list of "
                    f"{len(inventory)} inventories"
                )

        kwargs = {
            "name": inventory["name"],
            "version": inventory["version"],
        }
        for category in cls.categories():
            kwargs[category] = [pathlib.Path(p) for p in inventory.get(category, [])]

        return cls(**kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, tp.Any]) -> "ElementInventory":
        """Create an element inventory from a dictionary."""
        kwargs = {
            "name": data["name"],
            "version": data["version"],
        }
        for category in cls.categories():
            kwargs[category] = [pathlib.Path(p) for p in data.get(category, [])]
        return cls(**kwargs)


class AbstractDependency(abc.ABC):
    """Abstract dependency item.

    This class defines the interface for a dependency item.
    """

    dependencies_store: list["AbstractDependency"] = []

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__()
        cls.dependencies_store.append(cls)

    @abc.abstractproperty
    def img_dest(self) -> tp.Optional[str]:
        """Destination for the image."""

    @property
    def local_path(self) -> tp.Optional[str]:
        """Local path to the dependency."""
        return None

    @abc.abstractmethod
    def fetch(self, output_dir: str) -> None:
        """Fetch the dependency."""

    @abc.abstractclassmethod
    def from_config(
        cls, dep_config: tp.Dict[str, tp.Any], work_dir: pathlib.Path
    ) -> "AbstractDependency":
        """Create a dependency item from configuration."""

    @classmethod
    def find_dependency(
        cls, dep_config: tp.Dict[str, tp.Any], work_dir: pathlib.Path
    ) -> tp.Optional["AbstractDependency"]:
        """Probe all dependencies to find the right one."""
        for dep in cls.dependencies_store:
            try:
                return dep.from_config(dep_config, work_dir)
            except Exception:
                pass

        return None


class AbstractImageBuilder(abc.ABC):
    """Abstract image builder.

    This class defines the interface for building images.
    """

    @abc.abstractmethod
    def pre_build(
        self,
        image_dir: str,
        image: Image,
        deps: list[AbstractDependency],
        developer_keys: tp.Optional[str] = None,
        output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> None:
        """Actions to prepare the environment for building the image."""

    @abc.abstractmethod
    def build(
        self,
        image_dir: str,
        image: Image,
        developer_keys: tp.Optional[str] = None,
    ) -> None:
        """Actions to build the image."""

    @abc.abstractmethod
    def post_build(
        self,
        image_dir: str,
        image: Image,
    ) -> None:
        """Actions to perform after building the image."""

    def run(
        self,
        image_dir: str,
        image: Image,
        deps: list[AbstractDependency],
        developer_keys: tp.Optional[str] = None,
        output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> None:
        """Run the image builder."""
        self.pre_build(image_dir, image, deps, developer_keys, output_dir)
        self.build(image_dir, image, developer_keys)
        self.post_build(image_dir, image)


class DummyImageBuilder(AbstractImageBuilder):
    """Dummy image builder.

    Dummy builder that does nothing.
    """

    def pre_build(
        self,
        image_dir: str,
        image: Image,
        deps: list[AbstractDependency],
        developer_keys: tp.Optional[str] = None,
        output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> None:
        """Actions to prepare the environment for building the image."""
        return None

    def build(
        self,
        image_dir: str,
        image: Image,
        developer_keys: tp.Optional[str] = None,
    ) -> None:
        """Actions to build the image."""
        return None

    def post_build(
        self,
        image_dir: str,
        image: Image,
    ) -> None:
        """Actions to perform after building the image."""
        return None
