# Stand Specification

For more complicated cases when you need to start an installation with several nodes (that are treated as baremetal nodes) you may use a `stand specification`. The stand specification is a YAML file that describes the Exordos installation — how many bootstrap nodes, how many baremetal nodes, their characteristics, and other parameters.

Use option `--stand-spec` or `-s` for the `bootstrap` command to specify a file with the stand description:

```sh
exordos bootstrap -i output/exordos-core.raw -f -m core -s data/stands/stand-small.yaml
```

## Format

Field | Description
---|---
`name` | Name of the stand (used as a prefix for created VMs)
`bootstraps` | List of bootstrap nodes. Each entry defines `memory` (MB) and `cores`
`baremetals` | List of baremetal nodes. Each entry defines `name`, `memory` (MB), and `cores`

## Example

```yaml
name: dev-andromeda
bootstraps:
  - memory: 2048
    cores: 2
baremetals:
  - name: node-alpha
    memory: 2048
    cores: 2
  - name: node-beta
    memory: 2048
    cores: 2
```

This stand creates one bootstrap node and two baremetal nodes, each with 2 GB RAM and 2 CPU cores.
