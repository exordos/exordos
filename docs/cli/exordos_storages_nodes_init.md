
# exordos_storages_nodes_init

Install OST packages and prepare the local agent; OSTs are started by reconciliation after add

## Usage

```console

 Usage: exordos storages nodes init [OPTIONS]

```

## Options

* `storage_type` (REQUIRED):
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `--type`

* `agent`:
    * Type: text
    * Default: `universal_agent`
    * Usage: `--agent`

  Local universal agent service instance to configure

* `version`:
    * Type: text
    * Default: `none`
    * Usage: `--version`

  Override RAWSTOR_VERSION for installed packages

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos storages nodes init [OPTIONS]

```
