![Tests workflow](https://github.com/exordos/exordos/actions/workflows/tests.yml/badge.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/exordos)
![PyPI - Downloads](https://img.shields.io/pypi/dm/exordos)

# Exordos cli

The tools to manager life cycle of Exordos projects

# Installation of binary

To install the `exordos` binary, follow this step:

 ```sh
 curl -fsSL https://repository.genesis-core.tech/install.sh | sudo sh
 ```

# Requirements

Before you can install and use exordos you need to install several requirements:

- [packer](https://www.packer.io/)
- [libvirt](https://libvirt.org/)
- [qemu](https://www.qemu.org/)

## Ubuntu

Install packages

```sh
sudo apt update
sudo apt install qemu-kvm qemu-utils libvirt-daemon-system libvirt-dev mkisofs
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME"/.local/bin/env
uv tool install tox --with tox-uv
```

Add user to group

```sh
sudo adduser $USER libvirt
sudo adduser $USER kvm
```

Install packer like described in [this article](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/packer-quickstart#from-y-mirror)

# Install

To install the `exordos` package, follow these steps:

1. Clone the repository:

    ```sh
    git clone https://github.com/exordos/exordos.git
    ```

2. Navigate to the project directory:

    ```sh
    cd exordos
    ```

3. Initialize virtual environment:

   ```bash
   tox -e develop
   source .tox/develop/bin/activate
   ```

# Quickstart

## Build

Firstly you need to build the Exordos project. Navigate to your project directory and run the exordos build command, specifying the path to your project root directory as an argument. This will build the project according to the configuration defined in the `exordos.yaml` file.

Here are some examples of how to use the build command:

```sh
exordos build /path/to/my/project
```

There are some useful options for the exordos build command.

- Build a Exordos project with a custom developer key path:

```sh
exordos build -i /path/to/my/developer/key /path/to/my/project
```

- Build a Exordos project with the --force option to rebuild if the output already exists:

```sh
exordos build -f /path/to/my/project
```

Look at the `exordos build --help` command for more options.

## Bootstrap

To bootstrap a Exordos installation locally, use the exordos bootstrap command. This command creates and boots a virtual machine with the specified Exordos image.

One of the key options for the bootstrap command is `--launch-mode`, which allows you to specify the launch mode for the application. There are three available modes:

- `element`: This is the default mode, which launches the installation as a single element.
- `core`: This mode launches the installation as a core.
- `custom`: This mode allows you to launch the installation with a custom configuration.

Here are some examples of how to use the `--launch-mode` option:

```sh+
exordos bootstrap -i output/exordos-element.raw
```

Launch the installation in `core` mode:

```sh
exordos bootstrap -i output/exordos-core.raw -m core
```

# Usage

The package provides a command line interface for building Exordos projects, managing Exordos installations and cover many other useful aspects. To use the command line interface, run the `exordos` command from the command line. For full documentation about CLI commands, run `exordos --help`.

For every Exordos project the directory `exordos` should exist in the project root. The project configuration file should be named `exordos.yaml` in this directory. For example my project structure looks like this:

```sh
.
├── my_project
│   └── main.py
├── project_settings.json
├── pyproject.toml
└── README.md
```

The project should be extended as follows:

```sh
.
├── my_project
│   └── main.py
├── exordos
│   └── exordos.yaml
├── README.md
├── project_settings.json
├── pyproject.toml
└── README.md
```

## Exordos configuration file

The `exordos.yaml` file contains the configuration for the Exordos project. It should be placed in the `exordos` directory. It consists of several sections such as build, deploy, etc.

Example of the `exordos.yaml` file:

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
        - configs/my-cofig.yaml
        - templates/my-template.yaml
```

## Build project

The `exordos build` command builds the project. The build process is described in the `build` section of the `exordos.yaml` file. The mandatory argument is path to the project root directory.

Build a Exordos project.

```sh
exordos build my_project
```

This will build the Exordos project in the `my_project` directory using the default configuration file will be located in `my_project/exordos/exordos.yaml`.

After build the project output artifacts will be stored in the `output` directory.
For detailed information about the `exordos build` command run `exordos build --help`.

## Manage Exordos installation locally

To bootstrap Exordos installation locally, run the `exordos bootstrap` command. The mandatory argument is path to the exordos image. For instance,

```sh
exordos bootstrap output/exordos-core.raw
```

This command will create and boot a virtual machine with the specified Exordos image `output/exordos-core.raw`. The default name of the installation is `exordos-core`. For detailed information about the `exordos bootstrap` command run `exordos bootstrap --help`.

To connect to the Exordos installation, run the `exordos ssh` command. For instance,

```sh
exordos ssh
```

To list exordos installations, run the `exordos ps` command. For instance,

```sh
exordos ps
```

To delete Exordos installation, run the `exordos delete` command. For instance,

```sh
exordos delete exordos-core
```

### Stand specification

For more complicated cases when you need to start an installation with several nodes (that are treated as baremetal nodes) you may use `stand specification`. The stand specification is a YAML file describes the Exordos installation. it specifies how many bootstrap nodes, how many baremetal nodes, their characteristics and other parameters. For instance, it may look like this:

[Small stand](data/stands/stand-small.yaml)

Use option `--stand-spec` or `-s` for the `bootstrap` command to specify file with stand description. For instance,

```sh
exordos bootstrap -i output/exordos-core.raw -f -m core -s data/stands/stand-small.yaml
```

## Versions

Semver is used for project versioning. There are three types of versions:

- stable version - format `X.Y.Z`
- release candidate version - format `X.Y.Z-rc+YYYYMMDDHHMMSS.commit_hash[:8]`
- development version - format `X.Y.Z-dev+YYYYMMDDHHMMSS.commit_hash[:8]`

Stable version looks like `1.0.0`, only three digits. Release candidate version looks like `0.0.1-rc+20250224092842.e11604e9`. Development version looks like `0.0.1-dev+20250223180245.fb195339`.

To get project version, run the `exordos get-version` with path to the project root directory as an argument to the command. For instance,

```sh
exordos get-version /path/to/my_project
```

## Backups

The `backup` command is used to backup the current installation. This guide provides a brief overview of the command and its usage, along with several examples to get you started.

The basic syntax of the `backup` command is as follows:

```bash
exordos backup -d /path/to/backup/directory
```

Run the above command to backup the current installation to the specified directory. The command will create a subdirectory for each domain and copy its disks to the specified directory. The backup will repeat every 24 hours by default.

To configure period of backup, run the following command:

```bash
exordos backup -d /path/to/backup/directory -p 1h
```

The above command will backup the current installation to the specified directory every hour.

There is an option to do a backup once and exit:

```bash
exordos backup -d /path/to/backup/directory -oneshot
```

The above command will backup the current installation to the specified directory once and exit.

### Basic Backup

Run backup periodically of all libvirt domains and store it in the current directory:

```bash
exordos backup
```

### Backup Specific Domain

Run backup periodically of a specific libvirt domain and store it in the current directory:

```bash
exordos backup -n domain-name
```

### Exclude Specific Domains

Use `--exclude-name` (or `--no`) to skip specific domains or patterns. `--name` and `--exclude-name/--no` cannot be used together.

For example:

```bash
exordos backup --exclude-name domain-foo --exclude-name domain-bar --exclude-name "domain-stand-*"
```

### Custom Periodic Backup

Run backup periodically of all libvirt domains and store it in the current directory:

```bash
exordos backup -p 1h
```

Available periods are: `1m`, `5m`, `15m`, `30m`, `1h`, `3h`, `6h`, `12h`, `1d`, `3d`, `7d`

### OneShot Backup

Run backup of all libvirt domains and store it in the current directory:

```bash
exordos backup -oneshot
```

This command will backup the current installation to the specified directory once and exit.

### Compressed Backup

Run backup of all libvirt domains and store a compressed archive of the backup in the current directory:

```bash
exordos backup --compress
```

### Encrypted Backup

Run backup of all libvirt domains and store an encrypted archive of the backup in the current directory:

NOTE: It works only with `--compress` flag

You need to set the environment variables `GEN_DEV_BACKUP_KEY` and `GEN_DEV_BACKUP_IV` to encrypt the backup. The key and IV must be greater or equal to 6 bytes and less or equal to 16 bytes.

```bash
export GEN_DEV_BACKUP_KEY=secret_key
export GEN_DEV_BACKUP_IV=secret_iv

exordos backup --compress --encrypt
```

For decryption, use the `exordos backup-decrypt` command.

```bash
exordos backup-decrypt backup.tar.gz.encrypted
```

### Restore backups

Look at the wiki page [backups](https://exordos.github.io/exordos/backups/) for information on how to restore backups.

### Rotation

For the periodic backup, you can set the number of backups to keep(rotation number). The default value is 5. Use the `--rotate` option to set the number of backups to keep:

```bash
exordos backup --rotate 10
```

### Prevent disk overflow

Backups can take a lot of disk space and it can be a reason to crash the whole system if a disk will be full. To prevent such a situation you can set a threshold for disk space that should be free. If during a backup process this threshold will be reached, the backup process will stop. Use the `--min-free-space` option to set the threshold in GB.

```bash
exordos backup --min-free-space 50
```
