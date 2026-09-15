
# exordos_cn_get-key

Retrieve a node's universal-agent encryption key

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos cn get-key [OPTIONS] NODE                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
```

## Options

* `node` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `node`

* `output`:
    * Type: path
    * Default: `none`
    * Usage: `-o
--output`

  Write the key to this file (mode 0600) instead of printing it

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos cn get-key [OPTIONS] NODE                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
 Retrieve a node's universal-agent encryption key                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output  -o  PATH  Write the key to this file (mode 0600) instead of printing it                                                                                                                                                                                                                       │
│ --help              Show this message and exit.                                                                                                                                                                                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
