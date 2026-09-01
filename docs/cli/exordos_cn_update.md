
# exordos_cn_update

Update an existing node

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos cn update [OPTIONS]                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid_or_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-u
--uuid_or_name`

  UUID or name of the node to update

* `cores`:
    * Type: integer
    * Default: `none`
    * Usage: `-c
--cores`

  Number of cores to allocate for the node

* `ram`:
    * Type: integer
    * Default: `none`
    * Usage: `-r
--ram`

  Amount of RAM in Mb to allocate for the node

* `root_disk`:
    * Type: integer
    * Default: `none`
    * Usage: `-d
--root-disk`

  Number of GiB of root disk to allocate for the node

* `image`:
    * Type: text
    * Default: `none`
    * Usage: `-i
--image`

  Name of the image to deploy

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the node

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the node

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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos cn update [OPTIONS]                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
 Update an existing node                                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --uuid_or_name  -u  TEXT     UUID or name of the node to update [required]                                                                                                                                                                                                                           │
│    --cores         -c  INTEGER  Number of cores to allocate for the node                                                                                                                                                                                                                                │
│    --ram           -r  INTEGER  Amount of RAM in Mb to allocate for the node                                                                                                                                                                                                                            │
│    --root-disk     -d  INTEGER  Number of GiB of root disk to allocate for the node                                                                                                                                                                                                                     │
│    --image         -i  TEXT     Name of the image to deploy                                                                                                                                                                                                                                             │
│    --name          -n  TEXT     Name of the node                                                                                                                                                                                                                                                        │
│    --description   -D  TEXT     Description of the node                                                                                                                                                                                                                                                 │
│    --wait                       Wait until the node is running                                                                                                                                                                                                                                          │
│    --help                       Show this message and exit.                                                                                                                                                                                                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
