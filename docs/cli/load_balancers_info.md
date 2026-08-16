
# load_balancers_info

Show load balancer details with vhosts and backend_pools

## Usage

```console
                                                                                
 Usage: exordos network load_balancers info [OPTIONS] UUID                      
                                                                                
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `output`:
    * Type: choice
    * Default: `table`
    * Usage: `--output
-o`

  the output format, defaults to table

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: exordos network load_balancers info [OPTIONS] UUID                      
                                                                                
 Show load balancer details with vhosts and backend_pools                       
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --output  -o  [json|html|table|yaml]  the output format, defaults to table   │
│ --help                                Show this message and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯
```
