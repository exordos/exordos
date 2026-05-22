
# ee_define

Add resource to manifest

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos ee define [OPTIONS] UUID_NAME                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid_name`

* `editor`:
    * Type: choice
    * Default: `nano`
    * Usage: `-e
--editor`

  Editor (nano or vim)

* `repository`:
    * Type: text
    * Default: `https://repo.exordos.com/exordos-elements/`
    * Usage: `-r
--repository`

  Repository endpoint

* `resource_type`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--resource-type`

  Type of resource to define

* `resource_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--resource-name`

  Name of resource to define

* `resource_var`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--resource-var`

  Variables to pass to the resource template. The format is 'key=value'. For example: --resource-var cpu=1 --resource-var ram=1024

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos ee define [OPTIONS] UUID_NAME                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```
