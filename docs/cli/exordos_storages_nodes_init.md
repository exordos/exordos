
# exordos_storages_nodes_init

Install OST packages and configure the local agent

## Usage

```console

 Usage: exordos storages nodes init [OPTIONS]

```

## Options

* `storage_type` (REQUIRED):
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `--type`

* `pool_agent_name`:
    * Type: text
    * Default: `universal_agent`
    * Usage: `--pool-agent-name`

  Local universal agent service instance to create or configure

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
