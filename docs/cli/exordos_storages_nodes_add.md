
# exordos_storages_nodes_add

Register an initialized OST in a cluster's MDS topology

## Usage

```console

 Usage: exordos storages nodes add [OPTIONS]

```

## Options

* `cluster` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--cluster`

  Cluster name or UUID

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `--name`

  Local instance name; defaults to hostname

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `--uuid`

* `endpoint`:
    * Type: text
    * Default: `none`
    * Usage: `--endpoint`

  OST URI; read from local init configuration if omitted

* `failure_domain_path` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--failure-domain-path`

  dc/row/rack/server; outer levels may be omitted

* `weight`:
    * Type: float range
    * Default: `1.0`
    * Usage: `--weight`

* `description`:
    * Type: text
    * Default: ``
    * Usage: `--description`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos storages nodes add [OPTIONS]

```
