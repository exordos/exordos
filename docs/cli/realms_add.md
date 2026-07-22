
# realms_add

Add a new ecosystem realm

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos realms add [OPTIONS]                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the realm

* `name`:
    * Type: text
    * Default: `example_realm`
    * Usage: `-n
--name`

  Name of the realm

* `admin_password`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--admin-password`

  Password of the realm. If not provided, will be asked interactively

* `node_cores`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--node-cores`

* `node_ram`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--node-ram`

* `node_root_disk_size`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--node-root-disk-size`

* `node_image`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--node-image`

  Url of the realm image

* `core_version`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--core-version`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos realms add [OPTIONS]                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
 Add a new ecosystem realm                                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --uuid                 -u  UUID     UUID of the realm                                                                                                                                                                                                                                                   │
│ --name                 -n  TEXT     Name of the realm                                                                                                                                                                                                                                                   │
│ --admin-password           TEXT     Password of the realm. If not provided, will be asked interactively                                                                                                                                                                                                 │
│ --node-cores               INTEGER                                                                                                                                                                                                                                                                      │
│ --node-ram                 INTEGER                                                                                                                                                                                                                                                                      │
│ --node-root-disk-size      INTEGER                                                                                                                                                                                                                                                                      │
│ --node-image               TEXT     Url of the realm image                                                                                                                                                                                                                                              │
│ --core-version             TEXT                                                                                                                                                                                                                                                                         │
│ --help                              Show this message and exit.                                                                                                                                                                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
