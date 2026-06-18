
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

* `lb_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-d
--lb-uuid`

* `vhost_uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-v
--vhost-uuid`

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
│ *  --lb-uuid     -d  TEXT  [required]                                                                                                                                                                                                                                                                   │
│ *  --vhost-uuid  -v  TEXT  [required]                                                                                                                                                                                                                                                                   │
│    --help                  Show this message and exit.                                                                                                                                                                                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
