
# exordos_compute_cn_add

Add a new node to the Exordos installation

## Usage

```console

 Usage: exordos compute cn add [OPTIONS]

```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the node

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the node

* `cores`:
    * Type: integer
    * Default: `1`
    * Usage: `-c
--cores`

  Number of cores to allocate for the node

* `ram`:
    * Type: integer
    * Default: `1024`
    * Usage: `-r
--ram`

  Amount of RAM in Mb to allocate for the node

* `root_disk`:
    * Type: integer
    * Default: `10`
    * Usage: `-d
--root-disk`

  Number of GiB of root disk to allocate for the node

* `image` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--image`

  Name of the image to deploy

* `name`:
    * Type: text
    * Default: `node`
    * Usage: `-n
--name`

  Name of the node

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the node

* `hostname`:
    * Type: text
    * Default: `none`
    * Usage: `--hostname`

  Hostname of the node

* `network`:
    * Type: text
    * Default: `none`
    * Usage: `--network`

  Give the node one leg on this network (UUID or name). Shorthand for `--interface network=<ref>`; use --interface for anything more.

* `interfaces`:
    * Type: text
    * Default: `()`
    * Usage: `--interface`

  A leg of the node, repeatable: subnet=<ref>[,address=<ip>][,index=<n>][,public=<address>|floating-from=<subnet>], or port=<ref>[,index=<n>] to adopt a port that already exists. Index 0 is the primary leg, whose address the node publishes as its own; left unset, legs are numbered in the order given.

* `no_network`:
    * Type: boolean
    * Default: `false`
    * Usage: `--no-network`

  Give the node no networking at all. Different from saying nothing, which places it on the installation's default network.

* `wait`:
    * Type: boolean
    * Default: `false`
    * Usage: `--wait`

  Wait until the node is running

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos compute cn add [OPTIONS]

 Add a new node to the Exordos installation

╭─ Options ────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID     UUID of the node                              │
│ *  --project-id   -p  UUID     Name of the project in which to deploy the    │
│                                node [required]                               │
│    --cores        -c  INTEGER  Number of cores to allocate for the node      │
│                                [default: 1]                                  │
│    --ram          -r  INTEGER  Amount of RAM in Mb to allocate for the node  │
│                                [default: 1024]                               │
│    --root-disk    -d  INTEGER  Number of GiB of root disk to allocate for    │
│                                the node [default: 10]                        │
│ *  --image        -i  TEXT     Name of the image to deploy [required]        │
│    --name         -n  TEXT     Name of the node                              │
│    --description  -D  TEXT     Description of the node                       │
│    --hostname         TEXT     Hostname of the node                          │
│    --network          TEXT     Give the node one leg on this network (UUID   │
│                                or name). Shorthand for `--interface          │
│                                network=<ref>`; use --interface for anything  │
│                                more.                                         │
│    --interface        TEXT     A leg of the node, repeatable:                │
│                                subnet=<ref>[,address=<ip>][,index=<n>][,publ │
│                                ic=<address>|floating-from=<subnet>], or      │
│                                port=<ref>[,index=<n>] to adopt a port that   │
│                                already exists. Index 0 is the primary leg,   │
│                                whose address the node publishes as its own;  │
│                                left unset, legs are numbered in the order    │
│                                given.                                        │
│    --no-network                Give the node no networking at all. Different │
│                                from saying nothing, which places it on the   │
│                                installation's default network.               │
│    --wait                      Wait until the node is running                │
│    --help                      Show this message and exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```
