
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

  Network for the primary port (UUID or name).

* `auto_floating_ip`:
    * Type: boolean
    * Default: `false`
    * Usage: `--auto-floating-ip`

  Allocate a floating IP for the primary port.

* `floating_network`:
    * Type: text
    * Default: `none`
    * Usage: `--floating-network`

  Floating pool network (UUID or name); requires --auto-floating-ip.

* `no_network`:
    * Type: boolean
    * Default: `false`
    * Usage: `--no-network`

  Send an empty default_network request: disable the SDN auto-port while retaining legacy flat placement when configured.

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
│    --uuid              -u  UUID     UUID of the node                         │
│ *  --project-id        -p  UUID     Name of the project in which to deploy   │
│                                     the node [required]                      │
│    --cores             -c  INTEGER  Number of cores to allocate for the node │
│                                     [default: 1]                             │
│    --ram               -r  INTEGER  Amount of RAM in Mb to allocate for the  │
│                                     node [default: 1024]                     │
│    --root-disk         -d  INTEGER  Number of GiB of root disk to allocate   │
│                                     for the node [default: 10]               │
│ *  --image             -i  TEXT     Name of the image to deploy [required]   │
│    --name              -n  TEXT     Name of the node                         │
│    --description       -D  TEXT     Description of the node                  │
│    --hostname              TEXT     Hostname of the node                     │
│    --network               TEXT     Network for the primary port (UUID or    │
│                                     name).                                   │
│    --auto-floating-ip               Allocate a floating IP for the primary   │
│                                     port.                                    │
│    --floating-network      TEXT     Floating pool network (UUID or name);    │
│                                     requires --auto-floating-ip.             │
│    --no-network                     Send an empty default_network request:   │
│                                     disable the SDN auto-port while          │
│                                     retaining legacy flat placement when     │
│                                     configured.                              │
│    --wait                           Wait until the node is running           │
│    --help                           Show this message and exit.              │
╰──────────────────────────────────────────────────────────────────────────────╯
```
