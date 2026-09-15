
# exordos_network_security-groups_add

Add a new security group

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network security-groups add [OPTIONS]                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the group

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the group

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

* `rule_specs`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--rule`

  Allow rule <ingress|egress>:<tcp|udp|icmp|any>[:<port>][@<remote_cidr>|@<identity_group>], e.g. ingress:tcp:22 or ingress:tcp:5432@db (repeatable). Naming a group is ingress-only: what a packet carries is its sender's identity.

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos network security-groups add [OPTIONS]                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
```
