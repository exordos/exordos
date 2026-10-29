
# exordos_compute_hypervisors_add

Add a new hypervisor

## Usage

```console

 Usage: exordos compute hypervisors add [OPTIONS]

```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the hypervisor

* `name`:
    * Type: text
    * Default: `hypervisor`
    * Usage: `-n
--name`

  Name of the hypervisor

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the hypervisor

* `avail_cores`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--avail-cores`

* `avail_ram`:
    * Type: integer
    * Default: `sentinel.unset`
    * Usage: `--avail-ram`

* `cores_ratio`:
    * Type: float
    * Default: `sentinel.unset`
    * Usage: `--cores-ratio`

* `ram_ratio`:
    * Type: float
    * Default: `sentinel.unset`
    * Usage: `--ram-ratio`

* `machine_type`:
    * Type: choice
    * Default: `sentinel.unset`
    * Usage: `-m
--machine-type`

* `driver_spec`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--driver-spec`

  Additional filters to pass to the api. The format is 'key=value'. For example: --driver-spec a=b --driver-spec e=f

* `site`:
    * Type: text
    * Default: `none`
    * Usage: `--site`

  Failure domain for placement anti-affinity

* `kind`:
    * Type: choice
    * Default: `none`
    * Usage: `--kind`

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `--project-id`

  Core project UUID

* `auth_url`:
    * Type: text
    * Default: `none`
    * Usage: `--auth-url`

  Keystone v3 URL

* `region`:
    * Type: text
    * Default: `none`
    * Usage: `--region`

* `interface`:
    * Type: choice
    * Default: `public`
    * Usage: `--interface`

* `network_defaults_file`:
    * Type: filename
    * Default: `none`
    * Usage: `--network-defaults-file`

* `auth_type`:
    * Type: choice
    * Default: `v3applicationcredential`
    * Usage: `--auth-type`

* `application_credential_id`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--application-credential-id`

* `application_credential_secret`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--application-credential-secret`

  Secret; prompted without echo when omitted.

* `username`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--username`

* `password`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--password`

  Password; prompted without echo when omitted.

* `os_project_id`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--os-project-id`

  OpenStack project UUID, distinct from Core project UUID.

* `os_project_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--os-project-name`

* `user_domain_name`:
    * Type: text
    * Default: `default`
    * Usage: `--user-domain-name`

* `project_domain_name`:
    * Type: text
    * Default: `default`
    * Usage: `--project-domain-name`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos compute hypervisors add [OPTIONS]

 Add a new hypervisor

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --uuid                   -u  UUID                    UUID of the hypervisor  │
│ --name                   -n  TEXT                    Name of the hypervisor  │
│ --description            -D  TEXT                    Description of the      │
│                                                      hypervisor              │
│ --avail-cores                INTEGER                                         │
│ --avail-ram                  INTEGER                                         │
│ --cores-ratio                FLOAT                                           │
│ --ram-ratio                  FLOAT                                           │
│ --machine-type           -m  [vm|hw]                                         │
│ --driver-spec                TEXT                    Additional filters to   │
│                                                      pass to the api. The    │
│                                                      format is 'key=value'.  │
│                                                      For example:            │
│                                                      --driver-spec a=b       │
│                                                      --driver-spec e=f       │
│ --site                       TEXT                    Failure domain for      │
│                                                      placement anti-affinity │
│ --kind                       [libvirt|exordos_local                          │
│                              _hyper|openstack|dummy                          │
│                              ]                                               │
│ --project-id                 UUID                    Core project UUID       │
│ --auth-url                   TEXT                    Keystone v3 URL         │
│ --region                     TEXT                                            │
│ --interface                  [public|internal|admin                          │
│                              ]                                               │
│ --network-defaults-file      FILENAME                                        │
│ --auth-type                  [v3applicationcredenti  [default:               │
│                              al|v3password]          v3applicationcredential │
│                                                      ]                       │
│ --application-credenti…      TEXT                                            │
│ --application-credenti…      TEXT                    Secret; prompted        │
│                                                      without echo when       │
│                                                      omitted.                │
│ --username                   TEXT                                            │
│ --password                   TEXT                    Password; prompted      │
│                                                      without echo when       │
│                                                      omitted.                │
│ --os-project-id              TEXT                    OpenStack project UUID, │
│                                                      distinct from Core      │
│                                                      project UUID.           │
│ --os-project-name            TEXT                                            │
│ --user-domain-name           TEXT                    [default: Default]      │
│ --project-domain-name        TEXT                    [default: Default]      │
│ --help                                               Show this message and   │
│                                                      exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```
