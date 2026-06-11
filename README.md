<p align="center">
  <img src="https://github.com/exordos/exordos/actions/workflows/tests.yml/badge.svg" alt="Tests workflow">
  <img src="https://img.shields.io/pypi/pyversions/exordos" alt="PyPI - Python Version">
  <img src="https://img.shields.io/pypi/dm/exordos" alt="PyPI - Downloads">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License">
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="logo_black.svg">
    <source media="(prefers-color-scheme: light)" srcset="logo_white.svg">
    <img height="256" src="logo_white.svg" alt="exordos svg logo">
  </picture>
</p>

# Exordos CLI

**📚 CLI Documentation:** [exordos.github.io/exordos](https://exordos.github.io/exordos/) | **📚 Platform Documentation:** [exordos.github.io/exordos_core](https://exordos.github.io/exordos_core/)

Exordos CLI is the official command-line interface for the [Exordos platform](https://github.com/infraguys/exordos_core). It provides a unified toolset for managing the full lifecycle of Exordos projects — from building and provisioning elements to bootstrapping installations, managing backups, and interacting with a running Exordos environment.

# 🚀 To start using Exordos

Install the CLI with a single command:

```bash
curl -fsSL https://repo.exordos.com/install.sh | sh
```

## What Exordos CLI does

Exordos CLI bridges the gap between your local development environment and the Exordos platform. With a single binary you can:

- **Build projects** — compile Exordos project images and artifacts from a declarative `exordos.yaml` configuration.
- **Bootstrap installations** — spin up local virtual machine environments from built images for development and testing.
- **Manage installations** — connect via SSH, list, and remove running Exordos instances.
- **Interact with the platform** — manage elements, IAM, secrets, compute nodes, realms, and more through a rich set of subcommands.
- **Automate backups** — run periodic or one-shot backups of installations with compression, encryption, rotation, and disk-overflow protection.

> **For a full overview of all commands and configuration options, visit the [documentation](https://exordos.github.io/exordos/).**

# 💡 Contributing

Contributing to the project is highly appreciated! However, some rules should be followed for successful inclusion of new changes in the project:

- All changes should be done in a separate branch.
- Changes should include not only new functionality or bug fixes, but also tests for the new code.
- After the changes are completed and **tested**, a Pull Request should be created with a clear description of the new functionality. Add one of the project maintainers as a reviewer.
- Changes can be merged only after receiving approval from one of the project maintainers.
