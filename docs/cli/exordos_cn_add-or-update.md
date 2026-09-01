
# exordos_cn_add-or-update

Add a new node or update an existing one

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos cn add-or-update [OPTIONS]                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the node

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the node

* `cores`:
    * Type: integer
    * Default: `1`
    * Usage: `-c
--cores`

  Number of cores to allocate for the node

* `ram`:
    * Type: integer
    * Default: `1024`
    * Usage: `-r
--ram`

  Amount of RAM in Mb to allocate for the node

* `root_disk`:
    * Type: integer
    * Default: `10`
    * Usage: `-d
--root-disk`

  Number of GiB of root disk to allocate for the node

* `image` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--image`

  Name of the image to deploy

* `name`:
    * Type: text
    * Default: `node`
    * Usage: `-n
--name`

  Name of the node

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the node

* `wait`:
    * Type: boolean
    * Default: `false`
    * Usage: `--wait`

  Wait until the node is running

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos cn add-or-update [OPTIONS]                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
```
