# Exordos CLI

Exordos CLI is the official command-line interface for the [Exordos platform](https://github.com/infraguys/exordos_core). It provides a unified toolset for managing the full lifecycle of Exordos projects — from building and provisioning elements to bootstrapping installations, managing backups, and interacting with a running Exordos environment.

**📚 Platform Documentation:** [exordos.github.io/exordos_core](https://exordos.github.io/exordos_core/)

With a single binary you can:

- **Build projects** — compile Exordos project images and artifacts from a declarative `exordos.yaml` configuration.
- **Bootstrap installations** — spin up local virtual machine environments from built images for development and testing.
- **Manage installations** — connect via SSH, list, and remove running Exordos instances.
- **Interact with the platform** — manage elements, IAM, secrets, compute nodes, realms, and more through a rich set of subcommands.
- **Automate backups** — run periodic or one-shot backups of installations with compression, encryption, rotation, and disk-overflow protection.

## Install

### Binary (recommended)

Install the CLI with a single command:

```bash
curl -fsSL https://repository.genesis-core.tech/install.sh | sudo sh
```

### Via uv

```bash
uv tool install exordos
```

### Via pip

```bash
pip install exordos
```

---

For basic usage (managing a running Exordos platform) no further dependencies are needed.

If you want to **build elements locally** (compile images with Packer and QEMU) or **bootstrap a local platform deployment** (spin up a local Exordos installation for development and testing), install the additional dependencies below.

### Local build dependencies

#### QEMU and libvirt (Ubuntu)

```bash
sudo apt update
sudo apt install qemu-kvm qemu-utils libvirt-daemon-system libvirt-dev mkisofs
sudo adduser $USER libvirt
sudo adduser $USER kvm
```

You may need to re-login for the group changes to take effect.

#### Packer

Download [Packer version 1.9.2](https://hashicorp-releases.yandexcloud.net/packer/1.9.2/) or earlier (due to licensing limitations) and place the binary into `/usr/local/bin/` or any other directory in your `$PATH`.

## Quickstart

This section covers the core workflow: initializing a project, building an element, publishing it to a registry, and deploying it to a running Exordos installation.

For a step-by-step walkthrough with a real example project, see the [App Developer Guide](https://exordos.github.io/exordos_core/app-developer-guide/#quick-start) in the platform documentation.

## Exordos configuration file

Each Exordos project is described by an `exordos.yaml` file. See [exordos.yaml reference](exordos-yaml.md) for the full format and examples.

## Build project

The `exordos build` command builds the elements defined in `exordos.yaml`. The mandatory argument is the path to the project root directory.

```sh
exordos build my_project
```

After a successful build, output artifacts are stored in the `output` directory. For full reference see the [build documentation](https://exordos.github.io/exordos_core/app-developer-guide/build/).

## Stand specification

For multi-node installations, use a stand specification file to describe the topology. See [stand specification](stand-spec.md).

## Backups

For backing up Exordos installations, see the [backups documentation](backups.md).

## Versioning

For the project versioning scheme used by Exordos, see [versioning](versioning.md).
