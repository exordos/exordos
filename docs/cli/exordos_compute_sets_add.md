
# exordos_compute_sets_add

Add a new set to the Exordos installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute sets add [OPTIONS]                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the set

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project in which to deploy the set

* `cores`:
    * Type: integer
    * Default: `1`
    * Usage: `-c
--cores`

  Number of cores to allocate for each node in the set

* `ram`:
    * Type: integer
    * Default: `1024`
    * Usage: `-r
--ram`

  Amount of RAM in Mb to allocate for each node in the set

* `root_disk`:
    * Type: integer
    * Default: `10`
    * Usage: `-d
--root-disk`

  Number of GiB of root disk to allocate for each node in the set

* `image` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--image`

  Name of the image to deploy

* `name`:
    * Type: text
    * Default: `set`
    * Usage: `-n
--name`

  Name of the set

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the set

* `replicas`:
    * Type: integer
    * Default: `1`
    * Usage: `--replicas`

  Number of replicas (nodes) in the set

* `wait`:
    * Type: boolean
    * Default: `false`
    * Usage: `--wait`

  Wait until the set is active

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute sets add [OPTIONS]                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
 Add a new set to the Exordos installation                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID     UUID of the set                                                                                                                                                                                                                                                          │
│ *  --project-id   -p  UUID     UUID of the project in which to deploy the set [required]                                                                                                                                                                                                                │
│    --cores        -c  INTEGER  Number of cores to allocate for each node in the set [default: 1]                                                                                                                                                                                                        │
│    --ram          -r  INTEGER  Amount of RAM in Mb to allocate for each node in the set [default: 1024]                                                                                                                                                                                                 │
│    --root-disk    -d  INTEGER  Number of GiB of root disk to allocate for each node in the set [default: 10]                                                                                                                                                                                            │
│ *  --image        -i  TEXT     Name of the image to deploy [required]                                                                                                                                                                                                                                   │
│    --name         -n  TEXT     Name of the set                                                                                                                                                                                                                                                          │
│    --description  -D  TEXT     Description of the set                                                                                                                                                                                                                                                   │
│    --replicas         INTEGER  Number of replicas (nodes) in the set [default: 1]                                                                                                                                                                                                                       │
│    --wait                      Wait until the set is active                                                                                                                                                                                                                                             │
│    --help                      Show this message and exit.                                                                                                                                                                                                                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
