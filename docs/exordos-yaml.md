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
