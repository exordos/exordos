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
import json
import pathlib
import stat
import subprocess
import tarfile
import typing as tp
from unittest.mock import MagicMock
import uuid as sys_uuid

import pytest

from exordos.builder import base
from exordos.builder.builder import SimpleBuilder
from exordos.builder.builder import _urn_image
from exordos.logger import DummyLogger


class TestBuilder:
    def test_fetch_dependency(self, simple_builder: SimpleBuilder) -> None:
        deps_dir = "/tmp/deps_dir"
        simple_builder.fetch_dependency(deps_dir)
        for dep in simple_builder._deps:
            dep.fetch.assert_called_once_with(deps_dir)

        assert len(simple_builder._deps) > 1

    def test_from_config(self, build_config: tp.Dict[str, tp.Any], tmp_path) -> None:
        work_dir = tmp_path / "work_dir"
        work_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        builder = SimpleBuilder.from_config(
            work_dir,
            build_config,
            MagicMock(),
            output_dir,
            logger=DummyLogger(),
        )

        assert len(builder._deps) == 2
        assert len(builder._elements) == 1
        assert builder._exordos_dir == work_dir

    def test_select_element_filters_by_manifest_name(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        output_dir = tmp_path / "output"
        work_dir.mkdir()
        output_dir.mkdir()
        (work_dir / "app1.yaml").write_text("name: app1\n")
        (work_dir / "app2.yaml").write_text("name: app2\n")
        app1 = base.Element(manifest=pathlib.Path("app1.yaml"))
        app2 = base.Element(manifest=pathlib.Path("app2.yaml"))
        builder = SimpleBuilder(
            exordos_dir=work_dir,
            deps=[],
            elements=[app1, app2],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=output_dir,
        )

        assert builder.select_element("app2") is True
        assert builder._elements == [app2]

    def test_select_element_returns_false_for_unknown_name(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        output_dir = tmp_path / "output"
        work_dir.mkdir()
        output_dir.mkdir()
        (work_dir / "app.yaml").write_text("name: app\n")
        builder = SimpleBuilder(
            exordos_dir=work_dir,
            deps=[],
            elements=[base.Element(manifest=pathlib.Path("app.yaml"))],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=output_dir,
        )

        assert builder.select_element("missing") is False
        assert builder._elements == []

    def test_manifest_rendering_jinja2_variables(self, tmp_path) -> None:
        """Ensure Jinja2 variables render correctly."""
        # Arrange: temp work dir and output dir
        work_dir = tmp_path / "work"
        out_dir = tmp_path / "out"
        work_dir.mkdir()
        out_dir.mkdir()

        # Create a Jinja2 manifest template that is also valid YAML before rendering
        # so that the pre-parse with yaml.safe_load succeeds.
        manifest_rel = "myapp.yaml.j2"
        manifest_path = work_dir / manifest_rel
        manifest_content = (
            "name: my-element\n"
            'version: "{{ version }}"\n'
            "images: \"{{ images | join(',') }}\"\n"
            "metadata:\n"
            '  title: "{{ name }} v{{ version }}"\n'
            '  meta_foo: "{{ foo }}"\n'
            '  meta_bar: "{{ bar }}"\n'
        )
        manifest_path.write_text(manifest_content)

        # Prepare builder with no images to focus on manifest rendering
        builder = SimpleBuilder(
            exordos_dir=work_dir,
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=out_dir,
            version="1.2.3",
        )

        element = base.Element(manifest=pathlib.Path(manifest_rel), images=[])

        # Act
        inventory = builder.build_element(
            element=element,
            repo_dir=out_dir,
            developer_keys=None,
            manifest_vars={"foo": "FOO", "bar": "BAR"},
        )

        # Assert: rendered manifest exists without the .j2 extension
        # The manifest is now stored in a versioned subdirectory
        element_dir = out_dir / "my-element" / "1.2.3"
        manifests_dir = element_dir / "manifests"
        rendered_manifest = manifests_dir / "myapp.yaml"
        assert rendered_manifest.exists(), "Rendered manifest file not found"

        content = rendered_manifest.read_text()
        # Variables should be interpolated
        assert 'version: "1.2.3"' in content
        assert 'title: "my-element v1.2.3"' in content
        assert 'meta_foo: "FOO"' in content
        assert 'meta_bar: "BAR"' in content
        # images list is empty -> joined string should be empty quotes
        assert 'images: ""' in content

        assert inventory is not None
        assert inventory.manifests
        assert pathlib.Path(inventory.manifests[0]).name == "myapp.yaml"

    def test_manifest_rendering_preserves_filename_without_template_ext(
        self, tmp_path
    ) -> None:
        """Ensure the rendered manifest file drops the template extension (.j2/.jinja2)."""
        work_dir = tmp_path / "work"
        out_dir = tmp_path / "out"
        work_dir.mkdir()
        out_dir.mkdir()

        manifest_rel = "service.yaml.jinja2"
        manifest_path = work_dir / manifest_rel
        manifest_path.write_text('name: svc\nversion: "{{ version }}"\n')

        builder = SimpleBuilder(
            exordos_dir=work_dir,
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=out_dir,
            version="0.0.1",
        )

        element = base.Element(manifest=pathlib.Path(manifest_rel), images=[])

        builder.build_element(
            element=element,
            repo_dir=out_dir,
            developer_keys=None,
        )

        # The output manifest should be saved without the .jinja2 extension
        # The manifest is now stored in a versioned subdirectory
        assert (out_dir / "svc" / "0.0.1" / "manifests" / "service.yaml").exists()

    def test_build_multiple_manifests_writes_inventory_json(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        out_dir = tmp_path / "out"
        work_dir.mkdir()
        out_dir.mkdir()

        manifest_1 = "app1.yaml"
        manifest_2 = "app2.yaml"
        (work_dir / manifest_1).write_text("name: app1\nversion: 0\n")
        (work_dir / manifest_2).write_text("name: app2\nversion: 0\n")

        builder = SimpleBuilder(
            exordos_dir=work_dir,
            deps=[],
            elements=[
                base.Element(manifest=pathlib.Path(manifest_1), images=[]),
                base.Element(manifest=pathlib.Path(manifest_2), images=[]),
            ],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=out_dir,
            version="9.9.9",
        )

        builder.build(
            developer_keys=None,
            manifest_vars=None,
        )

        # Inventory.json is written to the exordos-elements subdirectory
        inventory_json = out_dir / "exordos-elements" / "inventory.json"
        assert inventory_json.exists()

        data = json.loads(inventory_json.read_text())
        # Inventory format is now {"elements": {...}}
        assert "elements" in data
        elements = data["elements"]
        assert isinstance(elements, dict)
        assert len(elements) == 2

        names = set(elements.keys())
        assert names == {"app1", "app2"}

        # Each element has a version key with the inventory data
        versions = {elements[name]["9.9.9"]["version"] for name in names}
        assert versions == {"9.9.9"}

        # Check manifests are stored correctly
        for name in names:
            elem_data = elements[name]["9.9.9"]
            assert elem_data["manifests"]
            manifest_name = pathlib.Path(elem_data["manifests"][0]).name
            assert manifest_name == f"{name}.yaml"

        # Manifests are now in versioned subdirectories under exordos-elements
        assert (
            out_dir / "exordos-elements" / "app1" / "9.9.9" / "manifests" / "app1.yaml"
        ).exists()
        assert (
            out_dir / "exordos-elements" / "app2" / "9.9.9" / "manifests" / "app2.yaml"
        ).exists()

    def test_image_from_config_single_format(self) -> None:
        """Image.from_config parses a single format string into a one-element list."""
        img = base.Image.from_config(
            {"script": "/tmp/install.sh", "format": "qcow2", "name": "my-img"},
            work_dir="/tmp",
        )
        assert img.formats == ["qcow2"]
        assert img.format == "qcow2"

    def test_image_from_config_multi_format(self) -> None:
        """Image.from_config parses a comma-separated format string correctly."""
        img = base.Image.from_config(
            {"script": "/tmp/install.sh", "format": "raw, qcow2", "name": "my-img"},
            work_dir="/tmp",
        )
        assert img.formats == ["raw", "qcow2"]
        assert img.format == "raw"

    def test_image_from_config_gz_qcow2(self) -> None:
        """Image.from_config parses gz,qcow2 multi-format correctly."""
        img = base.Image.from_config(
            {"script": "/tmp/install.sh", "format": "gz,qcow2", "name": "my-img"},
            work_dir="/tmp",
        )
        assert img.formats == ["gz", "qcow2"]

    def test_convert_image_raw(self, tmp_path) -> None:
        """_convert_image copies a raw image to the output dir."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        raw_src = tmp_path / "my-img.raw"
        raw_src.write_bytes(b"rawdata")

        builder = SimpleBuilder(
            exordos_dir=tmp_path,
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=tmp_path / "out",
        )
        result = builder._convert_image(raw_src, "my-img", "raw")
        assert pathlib.Path(result).name == "my-img.raw"
        assert (raw_src.parent / result).exists()

    def test_build_element_multi_format_inventory(self, tmp_path) -> None:
        """build_element lists all requested format variants in inventory images."""
        work_dir = tmp_path / "work"
        out_dir = tmp_path / "out"
        work_dir.mkdir()
        out_dir.mkdir()

        manifest_rel = "app.yaml"
        (work_dir / manifest_rel).write_text("name: myapp\nversion: 0\n")

        raw_file = tmp_path / "packer_out" / "myapp.raw"
        raw_file.parent.mkdir(parents=True)
        raw_file.write_bytes(b"fake-raw-image-data")

        img = base.Image(
            script=str(work_dir / "install.sh"),
            formats=["raw", "gz"],
            name="myapp",
        )

        mock_builder = MagicMock(spec=base.AbstractImageBuilder)

        def fake_run(image_dir, image, deps, developer_keys, output_dir):
            out = pathlib.Path(output_dir)
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{image.name}.raw").write_bytes(b"fake-raw-image-data")

        mock_builder.run.side_effect = fake_run

        builder = SimpleBuilder(
            exordos_dir=work_dir,
            deps=[],
            elements=[base.Element(manifest=pathlib.Path(manifest_rel), images=[img])],
            image_builder=mock_builder,
            logger=DummyLogger(),
            elements_output_dir=out_dir,
        )

        builder.build(
            developer_keys=None,
            manifest_vars=None,
        )

        # Inventory.json is written to the exordos-elements subdirectory
        inventory_json = out_dir / "exordos-elements" / "inventory.json"
        assert inventory_json.exists()
        data = json.loads(inventory_json.read_text())
        # Inventory format is now {"elements": {...}}
        assert "elements" in data
        elements = data["elements"]
        assert isinstance(elements, dict)
        # Images are stored under the element name and version
        images = elements["myapp"]["0.0.0"]["images"]
        image_names = [pathlib.Path(p).name for p in images]
        assert any(n.endswith(".raw") for n in image_names)
        assert any(n.endswith(".raw.gz") for n in image_names)


class TestImageNames:
    """Tests for the Image.names property."""

    def test_names_none_returns_empty(self) -> None:
        img = base.Image(script="/tmp/install.sh", formats=["raw"], name=None)
        assert img.names == tuple()

    def test_names_single_raw(self) -> None:
        img = base.Image(script="/tmp/install.sh", formats=["raw"], name="foo")
        assert img.names == ("foo.raw",)

    def test_names_qcow2(self) -> None:
        img = base.Image(script="/tmp/install.sh", formats=["qcow2"], name="foo")
        assert img.names == ("foo.qcow2",)

    def test_names_gz_appends_raw(self) -> None:
        """Compression formats are applied to raw images."""
        img = base.Image(script="/tmp/install.sh", formats=["gz"], name="foo")
        assert img.names == ("foo.raw.gz",)

    def test_names_zst_appends_raw(self) -> None:
        img = base.Image(script="/tmp/install.sh", formats=["zst"], name="foo")
        assert img.names == ("foo.raw.zst",)

    def test_names_multi_format(self) -> None:
        img = base.Image(
            script="/tmp/install.sh", formats=["raw", "gz", "qcow2"], name="bar"
        )
        assert img.names == ("bar.raw", "bar.raw.gz", "bar.qcow2")


class TestElementInventoryIndex:
    """Tests for ElementInventory index computation."""

    def test_compute_index_entry_is_deterministic(self) -> None:
        """Same inputs always produce the same UUID."""
        path = pathlib.Path("foo.raw")
        first = base.ElementInventory.compute_index_entry(
            "images", "elem", "1.0.0", path
        )
        second = base.ElementInventory.compute_index_entry(
            "images", "elem", "1.0.0", path
        )
        assert first == second
        # Result is a valid UUID string
        sys_uuid.UUID(first)

    def test_compute_index_entry_differs_per_category(self) -> None:
        path = pathlib.Path("foo.raw")
        images_key = base.ElementInventory.compute_index_entry(
            "images", "elem", "1.0.0", path
        )
        manifests_key = base.ElementInventory.compute_index_entry(
            "manifests", "elem", "1.0.0", path
        )
        assert images_key != manifests_key

    def test_compute_index_entry_differs_per_path(self) -> None:
        a = base.ElementInventory.compute_index_entry(
            "images", "elem", "1.0.0", pathlib.Path("a.raw")
        )
        b = base.ElementInventory.compute_index_entry(
            "images", "elem", "1.0.0", pathlib.Path("b.raw")
        )
        assert a != b

    def test_compute_index_entry_differs_per_version(self) -> None:
        a = base.ElementInventory.compute_index_entry(
            "images", "elem", "1.0.0", pathlib.Path("foo.raw")
        )
        b = base.ElementInventory.compute_index_entry(
            "images", "elem", "2.0.0", pathlib.Path("foo.raw")
        )
        assert a != b

    def test_compute_index_builds_all_categories(self) -> None:
        inv = base.ElementInventory(
            name="elem",
            version="1.0.0",
            images=[pathlib.Path("foo.raw")],
            manifests=[pathlib.Path("elem.yaml")],
            configs=[],
            templates=[],
            artifacts=[],
        )
        index = inv.compute_index()
        assert set(index.keys()) == set(base.ElementInventory.categories())
        assert len(index["images"]) == 1
        assert len(index["manifests"]) == 1
        assert (
            index["images"][
                base.ElementInventory.compute_index_entry(
                    "images", "elem", "1.0.0", pathlib.Path("foo.raw")
                )
            ]
            == "foo.raw"
        )
        assert (
            index["manifests"][
                base.ElementInventory.compute_index_entry(
                    "manifests", "elem", "1.0.0", pathlib.Path("elem.yaml")
                )
            ]
            == "elem.yaml"
        )

    def test_post_init_populates_index(self) -> None:
        """Index is computed automatically on construction."""
        inv = base.ElementInventory(
            name="elem",
            version="1.0.0",
            images=[pathlib.Path("foo.raw")],
        )
        assert inv.index
        assert "images" in inv.index
        assert len(inv.index["images"]) == 1

    def test_to_dict_includes_index(self) -> None:
        inv = base.ElementInventory(
            name="elem",
            version="1.0.0",
            images=[pathlib.Path("foo.raw")],
        )
        data = inv.to_dict()
        assert data["name"] == "elem"
        assert data["version"] == "1.0.0"
        assert data["index"] == inv.index
        assert data["images"] == ["foo.raw"]


class TestBuildImagesDict:
    """Tests for SimpleBuilder._build_images_dict and _urn_image."""

    def _builder(self, tmp_path) -> SimpleBuilder:
        return SimpleBuilder(
            exordos_dir=tmp_path,
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=tmp_path / "out",
        )

    def test_urn_image_format(self) -> None:
        assert _urn_image("abc-123") == "urn:images:abc-123"
        assert _urn_image(sys_uuid.UUID(int=0)) == f"urn:images:{sys_uuid.UUID(int=0)}"

    def test_single_image_includes_no_ext_key(self, tmp_path) -> None:
        builder = self._builder(tmp_path)
        img = base.Image(script="/tmp/install.sh", formats=["qcow2"], name="foo")
        result = builder._build_images_dict([img], "elem", "1.0.0")
        # Both the bare name and the name with extension are present
        assert "foo" in result
        assert "foo_qcow2" in result
        # Both point to a valid urn:images:<uuid>
        for v in result.values():
            assert v.startswith("urn:images:")
            sys_uuid.UUID(v[len("urn:images:") :])

    def test_single_zst_image_no_ext_key(self, tmp_path) -> None:
        builder = self._builder(tmp_path)
        img = base.Image(script="/tmp/install.sh", formats=["zst"], name="bar")
        result = builder._build_images_dict([img], "elem", "1.0.0")
        assert "bar" in result
        assert "bar_raw_zst" in result

    def test_multi_image_zst_gets_no_ext_key(self, tmp_path) -> None:
        """When a ZST image is present among many, it gets the bare-name key."""
        builder = self._builder(tmp_path)
        img = base.Image(
            script="/tmp/install.sh", formats=["raw.zst", "qcow2"], name="baz"
        )
        # Image.names for zst -> "baz.raw.zst", qcow2 -> "baz.qcow2"
        result = builder._build_images_dict([img], "elem", "1.0.0")
        assert "baz" in result  # bare name maps to the zst image
        assert "baz_raw_zst" in result
        assert "baz_qcow2" in result
        # The bare name and the zst-with-ext key point to the same URI
        assert result["baz"] == result["baz_raw_zst"]

    def test_multi_image_no_zst_no_bare_key(self, tmp_path) -> None:
        """Without a ZST image, no bare-name key is added."""
        builder = self._builder(tmp_path)
        img = base.Image(script="/tmp/install.sh", formats=["raw", "qcow2"], name="qux")
        result = builder._build_images_dict([img], "elem", "1.0.0")
        assert "qux" not in result
        assert "qux_raw" in result
        assert "qux_qcow2" in result

    def test_multiple_zst_images_all_present(self, tmp_path) -> None:
        """All ZST images are kept when several are present; only the first
        gets the bare-name key."""
        builder = self._builder(tmp_path)
        img1 = base.Image(script="/tmp/install.sh", formats=["zst"], name="foo")
        img2 = base.Image(script="/tmp/install.sh", formats=["zst"], name="bar")
        result = builder._build_images_dict([img1, img2], "elem", "1.0.0")
        # Both zst images are present with their full-name keys
        assert "foo_raw_zst" in result
        assert "bar_raw_zst" in result
        # Only the first zst image gets the bare-name key
        assert "foo" in result
        assert result["foo"] == result["foo_raw_zst"]
        assert "bar" not in result

    def test_index_matches_compute_index_entry(self, tmp_path) -> None:
        """The URI uuid matches compute_index_entry for the image path."""
        builder = self._builder(tmp_path)
        img = base.Image(script="/tmp/install.sh", formats=["raw"], name="foo")
        result = builder._build_images_dict([img], "elem", "1.0.0")
        expected_uuid = base.ElementInventory.compute_index_entry(
            "images", "elem", "1.0.0", pathlib.Path("foo.raw")
        )
        assert result["foo_raw"] == _urn_image(expected_uuid)

    def test_empty_images(self, tmp_path) -> None:
        builder = self._builder(tmp_path)
        assert builder._build_images_dict([], "elem", "1.0.0") == {}


def _make_script(path: pathlib.Path, body: str) -> pathlib.Path:
    path.write_text(f"#!/bin/sh\nset -e\n{body}\n")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


class TestGeneratedArtifactFromConfig:
    """Tests for base.GeneratedArtifact.from_config and Element dispatch."""

    def test_from_config_resolves_paths_relative_to_work_dir(self, tmp_path) -> None:
        artifact = base.GeneratedArtifact.from_config(
            {"script": "images/build.sh", "work_dir": "..", "artifacts": ["dist/"]},
            tmp_path,
        )
        assert artifact.script == str(tmp_path / "images/build.sh")
        assert artifact.work_dir == str((tmp_path / "..").resolve())
        assert artifact.patterns == ["dist/"]

    def test_from_config_defaults_work_dir_to_config_dir(self, tmp_path) -> None:
        artifact = base.GeneratedArtifact.from_config(
            {"script": "build.sh", "artifacts": ["out/*"]}, tmp_path
        )
        assert pathlib.Path(artifact.work_dir) == tmp_path

    def test_from_config_rejects_both_path_and_script(self, tmp_path) -> None:
        with pytest.raises(ValueError):
            base.GeneratedArtifact.from_config(
                {"path": "a", "script": "b.sh", "artifacts": ["*"]}, tmp_path
            )

    def test_element_from_config_dispatches_by_script_key(self, tmp_path) -> None:
        element = base.Element.from_config(
            {
                "artifacts": [
                    {"path": "a.txt"},
                    {"script": "b.sh", "artifacts": ["dist/"]},
                ]
            },
            tmp_path,
        )
        assert isinstance(element.artifacts[0], base.Artifact)
        assert isinstance(element.artifacts[1], base.GeneratedArtifact)


class TestBuildGeneratedArtifact:
    """Tests for SimpleBuilder._build_generated_artifact."""

    def _builder(self, tmp_path) -> SimpleBuilder:
        return SimpleBuilder(
            exordos_dir=tmp_path,
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=tmp_path / "out",
        )

    def test_file_artifact_is_copied_verbatim(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        _make_script(work_dir / "build.sh", "echo hi > out.txt")

        generated = base.GeneratedArtifact(
            script=str(work_dir / "build.sh"),
            work_dir=str(work_dir),
            patterns=["out.txt"],
        )
        builder = self._builder(tmp_path)
        output_dir = tmp_path / "artifacts"
        result = builder._build_generated_artifact(generated, output_dir)

        assert result == [pathlib.Path("out.txt")]
        assert (output_dir / "out.txt").read_text() == "hi\n"

    def test_directory_artifact_is_tar_zst_archived(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        _make_script(work_dir / "build.sh", "mkdir -p dist && echo hi > dist/file.txt")

        generated = base.GeneratedArtifact(
            script=str(work_dir / "build.sh"),
            work_dir=str(work_dir),
            patterns=["dist/"],
        )
        builder = self._builder(tmp_path)
        output_dir = tmp_path / "artifacts"
        result = builder._build_generated_artifact(generated, output_dir)

        assert result == [pathlib.Path("dist.tar.zst")]
        archive = output_dir / "dist.tar.zst"
        assert archive.exists()

        extracted_tar = tmp_path / "extracted.tar"
        subprocess.run(
            ["zstd", "-d", "-f", "-o", str(extracted_tar), str(archive)], check=True
        )
        with tarfile.open(extracted_tar) as tar:
            names = tar.getnames()
        assert "dist" in names
        assert "dist/file.txt" in names

    def test_glob_pattern_matches_multiple_files(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        _make_script(
            work_dir / "build.sh",
            "mkdir -p out && touch out/a.txt out/b.txt",
        )

        generated = base.GeneratedArtifact(
            script=str(work_dir / "build.sh"),
            work_dir=str(work_dir),
            patterns=["out/*.txt"],
        )
        builder = self._builder(tmp_path)
        output_dir = tmp_path / "artifacts"
        result = builder._build_generated_artifact(generated, output_dir)

        assert sorted(str(p) for p in result) == ["a.txt", "b.txt"]

    def test_empty_match_raises(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        _make_script(work_dir / "build.sh", "true")

        generated = base.GeneratedArtifact(
            script=str(work_dir / "build.sh"),
            work_dir=str(work_dir),
            patterns=["nothing_here/*"],
        )
        builder = self._builder(tmp_path)
        with pytest.raises(ValueError):
            builder._build_generated_artifact(generated, tmp_path / "artifacts")

    def test_non_executable_script_raises(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        script = work_dir / "build.sh"
        script.write_text("echo hi\n")

        generated = base.GeneratedArtifact(
            script=str(script), work_dir=str(work_dir), patterns=["*"]
        )
        builder = self._builder(tmp_path)
        with pytest.raises(ValueError):
            builder._build_generated_artifact(generated, tmp_path / "artifacts")


class TestBuildElementArtifacts:
    """Tests for mixed plain/generated artifacts in SimpleBuilder.build_element."""

    def test_mixed_plain_and_generated_artifacts(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        out_dir = tmp_path / "out"
        work_dir.mkdir()
        out_dir.mkdir()

        (work_dir / "app.yaml").write_text("name: myapp\nversion: 0\n")
        (work_dir / "static.txt").write_text("static content\n")
        _make_script(work_dir / "build.sh", "echo generated > generated.txt")

        element = base.Element(
            manifest=pathlib.Path("app.yaml"),
            artifacts=[
                base.Artifact(abs_path=str(work_dir / "static.txt"), path="static.txt"),
                base.GeneratedArtifact(
                    script=str(work_dir / "build.sh"),
                    work_dir=str(work_dir),
                    patterns=["generated.txt"],
                ),
            ],
        )

        builder = SimpleBuilder(
            exordos_dir=work_dir,
            deps=[],
            elements=[element],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=out_dir,
        )
        builder.build(developer_keys=None, manifest_vars=None)

        artifacts_dir = out_dir / "exordos-elements" / "myapp" / "0.0.0" / "artifacts"
        assert (artifacts_dir / "static.txt").read_text() == "static content\n"
        assert (artifacts_dir / "generated.txt").read_text() == "generated\n"

    def test_duplicate_artifact_name_raises(self, tmp_path) -> None:
        work_dir = tmp_path / "work"
        out_dir = tmp_path / "out"
        work_dir.mkdir()
        out_dir.mkdir()

        (work_dir / "app.yaml").write_text("name: myapp\nversion: 0\n")
        (work_dir / "dup.txt").write_text("static\n")
        _make_script(work_dir / "build.sh", "echo generated > dup.txt")

        element = base.Element(
            manifest=pathlib.Path("app.yaml"),
            artifacts=[
                base.Artifact(abs_path=str(work_dir / "dup.txt"), path="dup.txt"),
                base.GeneratedArtifact(
                    script=str(work_dir / "build.sh"),
                    work_dir=str(work_dir),
                    patterns=["dup.txt"],
                ),
            ],
        )

        builder = SimpleBuilder(
            exordos_dir=work_dir,
            deps=[],
            elements=[element],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=out_dir,
        )

        with pytest.raises(ValueError):
            builder.build_element(element, out_dir)


class TestGeneratedArtifactFlatten:
    """Tests for the flatten option on GeneratedArtifact."""

    def test_from_config_defaults_flatten_false(self, tmp_path) -> None:
        artifact = base.GeneratedArtifact.from_config(
            {"script": "build.sh", "artifacts": ["dist/"]}, tmp_path
        )
        assert artifact.flatten is False

    def test_from_config_flatten_true(self, tmp_path) -> None:
        artifact = base.GeneratedArtifact.from_config(
            {"script": "build.sh", "artifacts": ["dist/"], "flatten": True},
            tmp_path,
        )
        assert artifact.flatten is True

    def test_directory_artifact_archived_without_flatten(self, tmp_path) -> None:
        """Directory matched by generated artifact is archived with wrapper."""
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        _make_script(
            work_dir / "build.sh",
            "mkdir -p dist && echo hi > dist/index.html "
            "&& mkdir -p dist/assets && echo css > dist/assets/style.css",
        )

        generated = base.GeneratedArtifact(
            script=str(work_dir / "build.sh"),
            work_dir=str(work_dir),
            patterns=["dist/"],
            flatten=False,
        )
        builder = SimpleBuilder(
            exordos_dir=tmp_path,
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=tmp_path / "out",
        )
        output_dir = tmp_path / "artifacts"
        result = builder._build_generated_artifact(generated, output_dir)

        assert result == [pathlib.Path("dist.tar.zst")]
        archive = output_dir / "dist.tar.zst"
        assert archive.exists()

        extracted_tar = tmp_path / "extracted.tar"
        subprocess.run(
            ["zstd", "-d", "-f", "-o", str(extracted_tar), str(archive)],
            check=True,
        )
        with tarfile.open(extracted_tar) as tar:
            names = tar.getnames()
        assert "dist" in names
        assert "dist/index.html" in names
        assert "dist/assets" in names
        assert "dist/assets/style.css" in names

    def test_directory_artifact_archived_with_flatten(self, tmp_path) -> None:
        """Directory matched by generated artifact with flatten has no wrapper."""
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        _make_script(
            work_dir / "build.sh",
            "mkdir -p dist && echo hi > dist/index.html "
            "&& mkdir -p dist/assets && echo css > dist/assets/style.css",
        )

        generated = base.GeneratedArtifact(
            script=str(work_dir / "build.sh"),
            work_dir=str(work_dir),
            patterns=["dist/"],
            flatten=True,
        )
        builder = SimpleBuilder(
            exordos_dir=tmp_path,
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=tmp_path / "out",
        )
        output_dir = tmp_path / "artifacts"
        result = builder._build_generated_artifact(generated, output_dir)

        assert result == [pathlib.Path("dist.tar.zst")]
        archive = output_dir / "dist.tar.zst"
        assert archive.exists()

        extracted_tar = tmp_path / "extracted.tar"
        subprocess.run(
            ["zstd", "-d", "-f", "-o", str(extracted_tar), str(archive)],
            check=True,
        )
        with tarfile.open(extracted_tar) as tar:
            names = tar.getnames()
        assert "dist" not in names
        assert "index.html" in names
        assert "assets" in names
        assert "assets/style.css" in names
