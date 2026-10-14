
# exordos_network_networks_add

Add a new network

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network networks add [OPTIONS]                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the network

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the network

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Project UUID

* `mtu`:
    * Type: integer
    * Default: `none`
    * Usage: `--mtu`

  Overlay MTU (default: underlay MTU - 50, allocated by the core)

* `access`:
    * Type: choice
    * Default: `private`
    * Usage: `--access`

  private: this project only; public: visible/allocatable to everyone

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network networks add [OPTIONS]                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
```
