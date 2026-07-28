
# backend_pools_delete

Delete backend_pool

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network backend_pools delete [OPTIONS] UUID...                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
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
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network backend_pools delete [OPTIONS] UUID...                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
 Delete backend_pool                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --yes      -y        Automatically answer yes for all questions                                                                                                                                                                                                                                      │
│ *  --lb-uuid      UUID  [required]                                                                                                                                                                                                                                                                      │
│    --help               Show this message and exit.                                                                                                                                                                                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
