
# exordos_clear-build-cache

Remove the Packer cache with downloaded base images. The cache directory is resolved the same way as Packer does: PACKER_CACHE_DIR, then $XDG_CACHE_HOME/packer, then ~/.cache/packer ('packer_cache' in the current directory on Windows).

## Usage

```console
                                                                                
 Usage: exordos clear-build-cache [OPTIONS]                                     
                                                                                
```

## Options

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: exordos clear-build-cache [OPTIONS]                                     
                                                                                
 Remove the Packer cache with downloaded base images. The cache directory is    
 resolved the same way as Packer does: PACKER_CACHE_DIR, then                   
 $XDG_CACHE_HOME/packer, then ~/.cache/packer ('packer_cache' in the current    
 directory on Windows).                                                         
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help  Show this message and exit.                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
```
