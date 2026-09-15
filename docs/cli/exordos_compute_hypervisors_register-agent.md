
# exordos_compute_hypervisors_register-agent

Register a universal-agent node in the core and install its encryption key locally (e.g. the SDN evpn_node agent on this hypervisor).

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute hypervisors register-agent [OPTIONS]                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```

## Options

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--name`

  Name for the agent node

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Project in which to register the node

* `node_uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  Node UUID (generated if omitted)

* `cores`:
    * Type: integer
    * Default: `1`
    * Usage: `-c
--cores`

* `ram`:
    * Type: integer
    * Default: `1024`
    * Usage: `-r
--ram`

* `root_disk`:
    * Type: integer
    * Default: `10`
    * Usage: `--root-disk`

  Root disk size in GiB

* `machine_type`:
    * Type: choice
    * Default: `hw`
    * Usage: `-m
--machine-type`

  HW registers a bare node identity (no VM is provisioned) for an agent running on this host, e.g. the hypervisor's evpn_node agent. VM creates a regular compute node.

* `image`:
    * Type: text
    * Default: `none`
    * Usage: `--image`

  Image for the node (required for VM; unused for HW)

* `key_path`:
    * Type: text
    * Default: `none`
    * Usage: `--key-path`

  Where to install the node's encryption key [default: /var/lib/exordos/universal_agent/private_key; with --write-config: /var/lib/exordos/universal_agent_sdn/private_key]

* `pool_ref`:
    * Type: text
    * Default: `none`
    * Usage: `--pool`

  Machine pool served by this hypervisor: its hypervisor_node is set to the new node, so the core schedules the pool's guest SDN wiring (evpn) to this agent. 'auto' picks the only pool of the installation

* `write_config`:
    * Type: boolean
    * Default: `false`
    * Usage: `--write-config`

  Also write the SDN universal-agent config + systemd unit on this host and enable the service (orch/status endpoints derived from the realm endpoint)

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute hypervisors register-agent [OPTIONS]                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```
