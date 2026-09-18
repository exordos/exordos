
# exordos_metapaas_mail_instances_add

Add a new instance

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas mail instances add [OPTIONS]                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the instance

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  UUID of the project in which to deploy the instance

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the instance

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `--description`

  Description of the instance

* `domain` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-d
--domain`

  Mail domain to serve, for example: example.com

* `version` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-v
--version`

  UUID or name of the mail version

* `cpu` (REQUIRED):
    * Type: integer range
    * Default: `sentinel.unset`
    * Usage: `--cpu`

  Number of CPU cores per node

* `ram` (REQUIRED):
    * Type: integer range
    * Default: `sentinel.unset`
    * Usage: `--ram`

  RAM per node in MB

* `disk_size` (REQUIRED):
    * Type: integer range
    * Default: `sentinel.unset`
    * Usage: `--disk-size`

  Disk size per node in GB

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas mail instances add [OPTIONS]                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
 Add a new instance                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID                                UUID of the instance                                                                                                                                                                                                                          │
│ *  --project-id   -p  UUID                                UUID of the project in which to deploy the instance [required]                                                                                                                                                                                │
│ *  --name         -n  TEXT                                Name of the instance [required]                                                                                                                                                                                                               │
│    --description      TEXT                                Description of the instance                                                                                                                                                                                                                   │
│ *  --domain       -d  TEXT                                Mail domain to serve, for example: example.com [required]                                                                                                                                                                                     │
│ *  --version      -v  TEXT                                UUID or name of the mail version [required]                                                                                                                                                                                                   │
│ *  --cpu              INTEGER RANGE [1<=x<=128]           Number of CPU cores per node [required]                                                                                                                                                                                                       │
│ *  --ram              INTEGER RANGE [512<=x<=1073741824]  RAM per node in MB [required]                                                                                                                                                                                                                 │
│ *  --disk-size        INTEGER RANGE [8<=x<=1073741824]    Disk size per node in GB [required]                                                                                                                                                                                                           │
│    --help                                                 Show this message and exit.                                                                                                                                                                                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
