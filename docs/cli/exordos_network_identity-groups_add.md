
# exordos_network_identity-groups_add

Add a new identity group

## Usage

```console

 Usage: exordos network identity-groups add [OPTIONS]

```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the group

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the group

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Project UUID

* `network` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-N
--network`

  Network the group belongs to (UUID or name)

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos network identity-groups add [OPTIONS]

```
