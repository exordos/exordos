
# storages_update

Update storage

## Usage

```console
                                                                                
 Usage: exordos storages update [OPTIONS] UUID                                  
                                                                                
```

## Options
* `uuid` (REQUIRED): 
  * Type: text 
  * Default: `sentinel.unset`
  * Usage: `uuid`

  


* `name`: 
  * Type: text 
  * Default: `none`
  * Usage: `-n
--name`

  Name of the storage


* `description`: 
  * Type: text 
  * Default: `none`
  * Usage: `-D
--description`

  Description of the storage


* `driver_spec`: 
  * Type: text 
  * Default: `sentinel.unset`
  * Usage: `--driver-spec`

  Driver specification key/value pairs to merge into the existing one. The format is 'key=value'. For example: --driver-spec a=b


* `storage_pools`: 
  * Type: text 
  * Default: `none`
  * Usage: `--storage-pools`

  Storage pools as a JSON list, replacing the current ones entirely.


* `help`: 
  * Type: boolean 
  * Default: `false`
  * Usage: `--help`

  Show this message and exit.



## CLI Help

```console
                                                                                
 Usage: exordos storages update [OPTIONS] UUID                                  
                                                                                
 Update storage                                                                 
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --name           -n  TEXT  Name of the storage                               │
│ --description    -D  TEXT  Description of the storage                        │
│ --driver-spec        TEXT  Driver specification key/value pairs to merge     │
│                            into the existing one. The format is 'key=value'. │
│                            For example: --driver-spec a=b                    │
│ --storage-pools      TEXT  Storage pools as a JSON list, replacing the       │
│                            current ones entirely.                            │
│ --help                     Show this message and exit.                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

