
# exordos_storages_nodes_init

Install and start a local OST without registering it in a cluster

## Usage

```console

 Usage: exordos storages nodes init [OPTIONS]

```

## Options

* `storage_type` (REQUIRED):
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `--type`

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `--name`

  Local OST instance name; defaults to hostname

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `--uuid`

  Stable OST identity

* `location`:
    * Type: text
    * Default: `none`
    * Usage: `--location`

  Backing URI; defaults to file:///var/lib/rawstor/UUID

* `bind_address`:
    * Type: text
    * Default: `0.0.0.0:7777`
    * Usage: `--bind`

* `endpoint`:
    * Type: text
    * Default: `none`
    * Usage: `--endpoint`

  Advertised ost://host:port; auto-detected if omitted

* `rawstor_version`:
    * Type: text
    * Default: `none`
    * Usage: `--rawstor-version`

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
