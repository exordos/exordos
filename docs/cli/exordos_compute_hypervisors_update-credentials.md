
# exordos_compute_hypervisors_update-credentials

Replace credentials within the same OpenStack project

## Usage

```console

 Usage: exordos compute hypervisors update-credentials [OPTIONS] HYPERVISOR

```

## Options

* `hypervisor` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `hypervisor`

* `auth_type`:
    * Type: choice
    * Default: `v3applicationcredential`
    * Usage: `--auth-type`

* `application_credential_id`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--application-credential-id`

* `username`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--username`

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

 Usage: exordos compute hypervisors update-credentials [OPTIONS] HYPERVISOR

```
