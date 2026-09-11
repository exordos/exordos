
# storages_init

Initialize a storage cluster

## Usage

```console
                                                                                
 Usage: exordos storages init [OPTIONS]                                         
                                                                                
```

## Options
* `storage_type` (REQUIRED): 
  * Type: choice 
  * Default: `sentinel.unset`
  * Usage: `--type`

  Storage backend type


* `location`: 
  * Type: text 
  * Default: `none`
  * Usage: `--location`

  Backing store for the storage backend (e.g. file:///var/lib/rawstor for rawstor). Defaults to the backend's own default if not given.


* `speed`: 
  * Type: choice 
  * Default: `hot`
  * Usage: `--speed`

  Speed tier disks scheduled onto this cluster's pool will be tagged with


* `ephemeral`: 
  * Type: boolean 
  * Default: `false`
  * Usage: `--ephemeral`

  Whether this cluster's pool is ephemeral storage


* `endpoint`: 
  * Type: text 
  * Default: `none`
  * Usage: `--endpoint`

  Network address (ost://host:port) other hosts use to reach this cluster. Auto-detected from the interface used to reach the core if not given - override on a multi-homed storage node.


* `add`: 
  * Type: boolean 
  * Default: `false`
  * Usage: `--add`

  After initialization, register the storage cluster in the orchestrator (same as running `storages add`), using the top-level `exordos --endpoint/--user/--password` credentials.


* `uuid`: 
  * Type: uuid 
  * Default: `none`
  * Usage: `-u
--uuid`

  UUID of the storage cluster. Defaults to a UUID derived from /etc/machine-id.


* `name`: 
  * Type: text 
  * Default: `none`
  * Usage: `-n
--name`

  Name of the storage cluster. Defaults to this machine's hostname.


* `description`: 
  * Type: text 
  * Default: ``
  * Usage: `-D
--description`

  Description of the storage cluster


* `agent_name`: 
  * Type: text 
  * Default: `universal_agent`
  * Usage: `--agent-name`

  Name of the universal agent to run StorageClusterAgentDriver under. The default targets the standard agent (merging in if this host is also a registered compute node or hypervisor).


* `help`: 
  * Type: boolean 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



## CLI Help

```console
                                                                                
 Usage: exordos storages init [OPTIONS]                                         
                                                                                
```

