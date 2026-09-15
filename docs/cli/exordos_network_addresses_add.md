
# exordos_network_addresses_add

Allocate an address in a subnet

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network addresses add [OPTIONS]                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the address

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Project UUID

* `subnet` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-s
--subnet`

  Subnet to allocate in (UUID/name)

* `address`:
    * Type: text
    * Default: `none`
    * Usage: `-a
--address`

  The address to reserve (allocated from the subnet if omitted)

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network addresses add [OPTIONS]                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
```
