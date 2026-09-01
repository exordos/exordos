
# exordos_ee_ssh

copy exordos element from local git repo to element nodes, example cmd: exordos e e ssh empty

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos ee ssh [OPTIONS] NAME                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
```

## Options

* `user`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--user`

  ssh user name

* `public_key`:
    * Type: path
    * Default: `sentinel.unset`
    * Usage: `-i
--public-key`

  key or path to it, for example: /home/user/.ssh/id_rsa.pub

* `private_key`:
    * Type: path
    * Default: `sentinel.unset`
    * Usage: `-p
--private-key`

  key or path to it, for example: /home/user/.ssh/id_rsa.pub

* `y`:
    * Type: boolean
    * Default: `false`
    * Usage: `--y
-y`

  Automatically answer yes for all questions

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `name`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos ee ssh [OPTIONS] NAME                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
```
