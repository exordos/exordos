
# hypervisors_init

Initialize hypervisor

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute hypervisors init [OPTIONS]                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
```

## Options

* `romfile_version`:
    * Type: text
    * Default: `latest`
    * Usage: `--romfile-version`

  version of the rom file

* `pool_name`:
    * Type: text
    * Default: `default`
    * Usage: `--pool-name`

  storage pool name

* `packer`:
    * Type: boolean
    * Default: `false`
    * Usage: `-p
--packer`

  Install packer

* `user`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--user`

  username

* `add`:
    * Type: boolean
    * Default: `false`
    * Usage: `--add`

  After initialization, register the hypervisor in the orchestrator (same as running `hypervisors add`), using the top-level `exordos --endpoint/--user/--password` credentials. --uuid/--name/--description/--avail-cores/--avail-ram/--cores-ratio/--ram-ratio/--machine-type/--iface-mtu/--machine-prefix only apply in this mode. --network/--network-type/--network-bridge/--boot-network/--boot-bridge always set up this host's local libvirt networks regardless of --add, and additionally feed the registered driver_spec when combined with it.

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the hypervisor. Defaults to a UUID derived from /etc/machine-id, so re-running this command with --add updates the same hypervisor instead of registering a new one each time.

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the hypervisor. Defaults to this machine's hostname.

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the hypervisor

* `avail_cores`:
    * Type: integer
    * Default: `none`
    * Usage: `--avail-cores`

  Number of CPU cores available for VMs on this hypervisor. Auto-detected from the local machine if not set.

* `avail_ram`:
    * Type: integer
    * Default: `none`
    * Usage: `--avail-ram`

  Amount of RAM in Mb available for VMs on this hypervisor. Auto-detected from the local machine if not set.

* `cores_ratio`:
    * Type: float
    * Default: `none`
    * Usage: `--cores-ratio`

* `ram_ratio`:
    * Type: float
    * Default: `none`
    * Usage: `--ram-ratio`

* `machine_type`:
    * Type: choice
    * Default: `none`
    * Usage: `-m
--machine-type`

* `connection_uri`:
    * Type: text
    * Default: `qemu:///system`
    * Usage: `--connection-uri`

  Connection URI the orchestrator will use to reach this hypervisor. Hypervisors are expected to only run VMs local to themselves, so the default connects over the local libvirt Unix socket. Override only for backward compatibility or exotic setups, e.g. 'qemu+tcp://10.0.0.1/system' for remote access.

* `network`:
    * Type: text
    * Default: `exordos-core-net`
    * Usage: `--network`

  Name of the libvirt network used for VMs on this hypervisor - this is the logical name the orchestrator itself assigns ports by (see the stand's original bootstrap), not necessarily a literal host device. Don't rename it unless the orchestrator's own main network is actually named differently. For --network-type bridge, --network-bridge names the real underlying device.

* `network_type`:
    * Type: choice
    * Default: `network`
    * Usage: `--network-type`

  Type of the libvirt network used for VMs on this hypervisor

* `network_bridge`:
    * Type: text
    * Default: `none`
    * Usage: `--network-bridge`

  Host bridge device --network forwards onto. Only used when --network-type is 'bridge'; defaults to --network's own value if not given (i.e. the local libvirt network and the host bridge device happen to share one name).

* `boot_network`:
    * Type: text
    * Default: `exordos-core-boot-net`
    * Usage: `--boot-network`

  Name of the libvirt network new machines PXE-boot on before getting their real network port. DHCP (with the PXE next-server option) for it is served centrally over the realm's shared L2, the same way as for --network - not by anything local to this host.

* `boot_bridge`:
    * Type: text
    * Default: `none`
    * Usage: `--boot-bridge`

  Host bridge device the boot network forwards onto, if it's a different L2 than --network's bridge (e.g. the stand's bootstrap host reaches the boot subnet's DHCP over a separate NIC from the main one). Only used when --network-type is 'bridge'; defaults to --network's bridge if not given.

* `iface_mtu`:
    * Type: integer
    * Default: `1500`
    * Usage: `--iface-mtu`

  MTU for the VM network interface

* `machine_prefix`:
    * Type: text
    * Default: `vm-`
    * Usage: `--machine-prefix`

  Prefix for VM names created on this hypervisor

* `agent_name`:
    * Type: text
    * Default: `universal_agent`
    * Usage: `--pool-agent-name`

  Name of the universal agent to run LocalPoolAgentDriver under. The default targets the standard agent (merging in if this host is also a registered compute node). Use a different name to run a separate, dedicated agent instead - required if the standard agent here is already configured for a different core.

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos compute hypervisors init [OPTIONS]                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
```
