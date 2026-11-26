
# exordos_storages_pools_add

Add a policy sharing its cluster's capacity

## Usage

```console
                                                                                
 Usage: exordos storages pools add [OPTIONS]                                    
                                                                                
```

## Options

* `cluster` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--cluster`

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--name`

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `--uuid`

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `--description`

* `failure_domain`:
    * Type: choice
    * Default: `none`
    * Usage: `--failure-domain`

* `mirrors`:
    * Type: integer range
    * Default: `none`
    * Usage: `--mirrors`

* `ephemeral`:
    * Type: boolean
    * Default: `none`
    * Usage: `--ephemeral`

* `tier`:
    * Type: choice
    * Default: `none`
    * Usage: `--tier`

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  Output format; JSON prints one resource object (an array for bulk creation).

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: exordos storages pools add [OPTIONS]                                    
                                                                                
```
