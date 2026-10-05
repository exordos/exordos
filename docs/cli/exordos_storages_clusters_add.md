
# exordos_storages_clusters_add

Create a core MDS with persistent and ephemeral WARM pools

## Usage

```console

 Usage: exordos storages clusters add [OPTIONS]

```

## Options

* `storage_type` (REQUIRED):
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `--type`

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--name`

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `--uuid`

* `description`:
    * Type: text
    * Default: ``
    * Usage: `--description`

* `host`:
    * Type: text
    * Default: `none`
    * Usage: `--host`

  Core address reachable from hypervisors

* `port`:
    * Type: integer range
    * Default: `none`
    * Usage: `--port`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos storages clusters add [OPTIONS]

```
