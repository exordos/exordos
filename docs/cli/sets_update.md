
# sets_update

Update an existing set

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute sets update [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid_or_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-u
--uuid_or_name`

  UUID or name of the set to update

* `cores`:
    * Type: integer
    * Default: `none`
    * Usage: `-c
--cores`

  Number of cores to allocate for the set

* `ram`:
    * Type: integer
    * Default: `none`
    * Usage: `-r
--ram`

  Amount of RAM in Mb to allocate for the set

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the set

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the set

* `root_disk`:
    * Type: integer
    * Default: `none`
    * Usage: `-d
--root-disk`

  Number of GiB of root disk to allocate for the set

* `image`:
    * Type: text
    * Default: `none`
    * Usage: `-i
--image`

  Name of the image to deploy

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute sets update [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
 Update an existing set                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --uuid_or_name  -u  TEXT     UUID or name of the set to update [required]                                                                                                                                                                                                                            │
│    --cores         -c  INTEGER  Number of cores to allocate for the set                                                                                                                                                                                                                                 │
│    --ram           -r  INTEGER  Amount of RAM in Mb to allocate for the set                                                                                                                                                                                                                             │
│    --name          -n  TEXT     Name of the set                                                                                                                                                                                                                                                         │
│    --description   -D  TEXT     Description of the set                                                                                                                                                                                                                                                  │
│    --root-disk     -d  INTEGER  Number of GiB of root disk to allocate for the set                                                                                                                                                                                                                      │
│    --image         -i  TEXT     Name of the image to deploy                                                                                                                                                                                                                                             │
│    --help                       Show this message and exit.                                                                                                                                                                                                                                             │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
