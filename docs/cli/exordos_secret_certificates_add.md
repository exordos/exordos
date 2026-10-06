# exordos_secret_certificates_add

Add a new certificate to the Exordos installation

## Usage

```console

 Usage: exordos secret certificates add [OPTIONS]

```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the certificate

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the certificate

* `name`:
    * Type: text
    * Default: `test_certificate`
    * Usage: `-n
--name`

  Name of the certificate

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the certificate

* `email` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-e
--email`

  Email address to use for the certificate

* `domains` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-d
--domain`

  Domain of the certificate, wildcards are allowed. Can be repeated

* `method`:
    * Type: choice
    * Default: `dns_core`
    * Usage: `-m
--method`

  Method (provider) to issue and manage the certificate

* `tags`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--tag`

  Set the complete tag list. Repeat for each tag.

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console

 Usage: exordos secret certificates add [OPTIONS]

 Add a new certificate to the Exordos installation

╭─ Options ────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID        UUID of the certificate                    │
│ *  --project-id   -p  UUID        Name of the project in which to deploy the │
│                                   certificate [required]                     │
│    --name         -n  TEXT        Name of the certificate                    │
│    --description  -D  TEXT        Description of the certificate             │
│ *  --email        -e  TEXT        Email address to use for the certificate   │
│                                   [required]                                 │
│ *  --domain       -d  TEXT        Domain of the certificate, wildcards are   │
│                                   allowed. Can be repeated [required]        │
│    --method       -m  [dns_core]  Method (provider) to issue and manage the  │
│                                   certificate [default: dns_core]            │
│    --tag              TEXT        Set the complete tag list. Repeat for each │
│                                   tag.                                       │
│    --help                         Show this message and exit.                │
╰──────────────────────────────────────────────────────────────────────────────╯
```
