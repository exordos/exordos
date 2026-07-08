
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

* `y`:
    * Type: boolean
    * Default: `false`
    * Usage: `--yes
-y`

  Automatically answer yes for all questions

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
│    --yes         -y        Automatically answer yes for all questions                                                                                                                                                                                                                                   │
│ *  --vhost-uuid      UUID  [required]                                                                                                                                                                                                                                                                   │
│ *  --lb-uuid         UUID  [required]                                                                                                                                                                                                                                                                   │
│    --help                  Show this message and exit.                                                                                                                                                                                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
