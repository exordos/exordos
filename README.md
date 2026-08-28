<p align="center">
  <a href="https://github.com/exordos/exordos/actions/workflows/tests.yml"><img src="https://github.com/exordos/exordos/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <a href="https://github.com/exordos/exordos/actions/workflows/build.yml"><img src="https://github.com/exordos/exordos/actions/workflows/build.yml/badge.svg" alt="Build binary"></a>
  <a href="https://github.com/exordos/exordos/actions/workflows/publish-to-pypi.yml"><img src="https://github.com/exordos/exordos/actions/workflows/publish-to-pypi.yml/badge.svg" alt="Publish Python package"></a>
  <a href="https://pypi.org/project/exordos/"><img src="https://img.shields.io/pypi/v/exordos" alt="PyPI - Version"></a>
  <a href="https://pypi.org/project/exordos/"><img src="https://img.shields.io/pypi/pyversions/exordos" alt="PyPI - Python Version"></a>
  <a href="https://pypi.org/project/exordos/"><img src="https://img.shields.io/pypi/dm/exordos" alt="PyPI - Downloads"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License"></a>
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

Exordos CLI is the official command-line interface for the [Exordos Core platform](https://github.com/exordos/exordos_core). It provides a unified toolset for managing the full lifecycle of Exordos projects — from building and provisioning elements to bootstrapping installations, managing backups, and interacting with a running Exordos Core environment.

# 🚀 To start using Exordos

Install the CLI with a single command:

```bash
curl -fsSL https://repo.exordos.com/install.sh | sh
```

## What Exordos CLI does

Exordos CLI bridges the gap between your local development environment and the Exordos Core platform. With a self-contained installation you can:

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

## Local test environment on Ubuntu

The test environments require a working Python 3 installation. Check both command names:

```bash
python3 --version
python --version
```

If `python3` works but the unversioned `python` command is missing, install Ubuntu's compatibility package:

```bash
sudo apt update
sudo apt install python-is-python3
```

`python-is-python3` only provides the `python -> python3` link; it does not install Python 3 itself.

Tox uses `uv` for environment creation. In a sandbox or another restricted environment where `~/.cache/uv` is read-only, point the cache to a writable temporary directory:

```bash
UV_CACHE_DIR="${TMPDIR:-/tmp}/uv-cache" tox -e develop
```
