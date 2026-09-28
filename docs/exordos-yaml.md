# Exordos configuration file

The `exordos.yaml` file contains the configuration for the Exordos project. It should be placed in the `exordos` directory in the project root. It consists of several sections such as `build`, `deploy`, etc.

## Project structure

For every Exordos project the directory `exordos` should exist in the project root:

```sh
.
├── my_project
│   └── main.py
├── exordos
│   └── exordos.yaml
├── pyproject.toml
└── README.md
```

## Build configuration example

```yaml
# Build section. It describes the build process of the project.
build:
  # Dependencies of the project
  # This section is used to specify build dependencies
  # for the project
  deps:
      # Target path in the image
    - dst: /opt/exordos_core
      # Local path of the build machine
      path:
        src: ../../exordos_core
  
  # This section describes elements of the project.
  # Images, artifacts and manifests for every element. 
  elements:
      # List of images in the element
    - images:
      - name: exordos-core
        format: raw
        
        # OS profile for the image
        profile: ubuntu_24

        # Provisioning script
        script: images/install.sh

        # Override image build parameters, for instance Packer parameters
        override:
          disk_size: "10G"

      manifest: manifests/exordos-core.yaml
      
      # List of artifacts in the element
      artifacts:
        - path: configs/my-config.yaml
        - path: templates/my-template.yaml
```

### Building from a custom image URL

Use the `exordos_custom` profile to build an element from an existing disk
image. Set the image URL and checksum in `override`:

```yaml
build:
  elements:
    - images:
        - name: my-custom-image
          profile: exordos_custom
          format: qcow2
          script: images/install.sh
          override:
            base_image_url: "https://example.com/my-image.qcow2"
            base_image_checksum: "file:https://example.com/SHA256SUMS"
            disk_size: "10G"
            ssh_username: "ubuntu"

      manifest: manifests/my-element.yaml
```

Replace the example URLs with your disk image and its checksum file, and point
`manifest` to your element's manifest. You can also provide a checksum directly
as `base_image_checksum: "sha256:<image-sha256>"`. Set `disk_size` to at least
the virtual size of the base image.

The base image must support cloud-init's NoCloud datasource and SSH access for
the user specified by `override.ssh_username` (default: `ubuntu`). This user
must have passwordless sudo. The profile injects a temporary SSH key through
cloud-init and runs provisioning commands over SSH.

Create `exordos/images/install.sh` with your provisioning commands. If no
additional provisioning is needed, use:

```bash
#!/bin/bash
set -eu
```

Paths to the script and manifest are relative to `exordos/exordos.yaml`.
Build the element from the project root:

```bash
exordos build .
```

### Script-generated artifacts

An artifact entry may also run a script (or any executable) instead of pointing
directly at a file. The script is executed with its `work_dir` as the current
directory, and once it finishes, its own nested `artifacts` list of glob
patterns (relative to `work_dir`, `*` is supported) selects the resulting
files. If a matched entry is a directory, it is archived with `tar` and
compressed with `zstd` (e.g. a matched `dist/` directory becomes
`dist.tar.zst`); files are copied as-is. All paths (`script`, `work_dir`) are
resolved relative to the `exordos.yaml` file.

```yaml
      artifacts:
        - script: images/docs_build.sh
          work_dir: ../
          artifacts:
            - dist/
```

#### Flatten option

When a matched pattern is a directory, the archive preserves the top-level
directory name as a wrapper inside the archive by default. Set `flatten: true`
to place the directory contents at the root of the archive without the wrapper
directory. This is useful when the archive is extracted into a directory served
directly by nginx (e.g. via `alias`), where an extra wrapper directory would
cause files to be one level too deep.

```yaml
      artifacts:
        - script: images/docs_build.sh
          work_dir: ../
          flatten: true
          artifacts:
            - dist/
```

The example above produces `dist.tar.zst` containing the contents of `dist/`
(e.g. `index.html`, `assets/`, ...) without a `dist/` wrapper.

### Referencing artifacts in manifest templates

Both static and script-generated artifacts can be assigned a `name`. A named
artifact is referenceable in Jinja2 manifest templates via
`{{ artifacts.<name> }}`, which renders to the artifact's URN
(`urn:artifacts:<uuid>`):

```yaml
      artifacts:
        - path: packages/my_package.whl
          name: pip_package
```

```yaml
      artifacts:
        - script: images/build.sh
          work_dir: ../
          artifacts:
            - dist/my_package.whl
          name: pip_package
```

In a manifest template:

```jinja
  $metapaas.types:
    victoria:
      package: "{{ artifacts.pip_package }}"
```

After rendering:

```yaml
  $metapaas.types:
    victoria:
      package: "urn:artifacts:<uuid>"
```

A named artifact must produce exactly one file. If the script's glob patterns
match multiple files, a build error is raised because the name-to-URN mapping
would be ambiguous.

## Push configuration file

The push configuration is kept in a separate file — `exordos.push.yaml` — placed alongside `exordos.yaml` in the `exordos` directory. It defines one or more named push targets, each specifying a driver and a destination path.

### Format

```yaml
push:
  <target_name>:
    driver: <driver>   # e.g. "fs" for a local filesystem repository
    path: <path>       # destination path for the built artifacts
```

### Example

```yaml
push:
  local:
    driver: fs
    path: /var/lib/exordos-pools/http
```

To push to a specific target, pass the config file with the `-c` flag:

```bash
exordos push -c exordos/exordos.push.yaml
```

Manifest name discovery does not render Jinja templates. Use a static single-line top-level `name` or pass `--manifest-var name=value` for names that depend on template variables or conditions.

### Example: push to a realm's element repository

A managed realm serves an element repository from its node, one directory
per project, at `https://<realm domain>/repo/<project_id>`. Push to it with
the `realm` driver: it signs every request with a token of the realm's
login and keeps the repository index the realm core reads.

1. Add the realm to the CLI and log in to it (see [Realms](realms.md)).
   The login must be able to upload: a user of `<project_id>` (the project
   `owner` role has `repo.repository.upload`), or an unscoped admin.

2. Add a push target to `exordos/exordos.push.yaml`:

    ```yaml
    push:
      my-realm:
        driver: realm
        url: https://6def3e.exordos.io/repo/<project_id>
        realm: my-realm     # optional: the current realm by default
    ```

3. Build and push:

    ```bash
    exordos build -f .
    exordos push -c exordos/exordos.push.yaml -t my-realm
    ```

    The same without a config file:

    ```bash
    exordos push --driver realm \
      --driver-params url=https://6def3e.exordos.io/repo/<project_id> \
      --driver-params realm=my-realm
    ```

    `exordos push -f` replaces a version that is already there.

4. Install the element in the realm. The project's first push registers
   its repository in the realm core (`realm-<project_id prefix>`), so the
   element shows up there within a minute:

    ```bash
    exordos --realm my-realm elements install my-element
    ```

    A realm created before the realm core learnt its repository address
    needs the repository added once per project, at the address the realm
    core reaches it by: the realm node through the nested network gateway
    (`10.40.0.1` by default).

    ```bash
    exordos --realm my-realm repo add -p <project_id> -n realm-local \
      --refresh-rate 60 --sync-mode copy \
      --repo-url http://10.40.0.1:8081/repo/<project_id>/exordos-elements/
    ```

Images are referenced by URN in the built manifest and resolved through the
repository they come from. A manifest that writes an artifact URL itself,
such as `{{ repository }}/<element>/{{ version }}/artifacts/site.tar.zst`,
needs that address at build time:
`exordos build --manifest-var repository=http://10.40.0.1:8081/repo/<project_id>/exordos-elements`.
