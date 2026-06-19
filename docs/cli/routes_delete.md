
# routes_delete

Delete route

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network routes delete [OPTIONS] UUID                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `vhost_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--vhost-uuid`

* `lb_uuid` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--lb-uuid`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network routes delete [OPTIONS] UUID                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
 Delete route                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --vhost-uuid  UUID  [required]                                                                                                                                                                                                                                                                       │
│ *  --lb-uuid     UUID  [required]                                                                                                                                                                                                                                                                       │
│    --help              Show this message and exit.                                                                                                                                                                                                                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
