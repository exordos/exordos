
# ssh_keys_add

Add a new ssh_key to the Exordos installation, examples: `exordos secret ssh_keys add --node 2cc70850-3df7-4234-b9c1-0e20ed3672c7 --user ubuntu --target_public_key ~/.ssh/id_rsa.pub` or `exordos secret ssh_keys add --element dbaas --user ubuntu --target_public_key ~/.ssh/id_rsa.pub`

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos secret ssh_keys add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the ssh_key

* `project_id`:
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the ssh_key

* `name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the ssh_key

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the ssh_key

* `realm`:
    * Type: boolean
    * Default: `false`
    * Usage: `--realm`

  add ssh keys to all realm nodes and sets

* `element`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--element`

  element uuid or name

* `node`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--node`

  node uuid

* `node_set`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--node_set`

  node_set uuid

* `user`:
    * Type: text
    * Default: `ubuntu`
    * Usage: `--user`

  user name of the ssh_key

* `target_public_key`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--target_public_key`

  key or path to it, for example: /home/user/.ssh/id_rsa.pub

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos secret ssh_keys add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
 Add a new ssh_key to the Exordos installation, examples: `exordos secret ssh_keys add --node 2cc70850-3df7-4234-b9c1-0e20ed3672c7 --user ubuntu --target_public_key ~/.ssh/id_rsa.pub` or `exordos secret ssh_keys add --element dbaas --user ubuntu --target_public_key ~/.ssh/id_rsa.pub`               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --uuid               -u  UUID  UUID of the ssh_key                                                                                                                                                                                                                                                      │
│ --project-id         -p  UUID  Name of the project in which to deploy the ssh_key                                                                                                                                                                                                                       │
│ --name               -n  TEXT  Name of the ssh_key                                                                                                                                                                                                                                                      │
│ --description        -D  TEXT  Description of the ssh_key                                                                                                                                                                                                                                               │
│ --realm                        add ssh keys to all realm nodes and sets                                                                                                                                                                                                                                 │
│ --element                TEXT  element uuid or name                                                                                                                                                                                                                                                     │
│ --node                   TEXT  node uuid                                                                                                                                                                                                                                                                │
│ --node_set               TEXT  node_set uuid                                                                                                                                                                                                                                                            │
│ --user                   TEXT  user name of the ssh_key                                                                                                                                                                                                                                                 │
│ --target_public_key      TEXT  key or path to it, for example: /home/user/.ssh/id_rsa.pub                                                                                                                                                                                                               │
│ --help                         Show this message and exit.                                                                                                                                                                                                                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
