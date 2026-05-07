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
        - configs/my-config.yaml
        - templates/my-template.yaml
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
