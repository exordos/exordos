
# exordos_metapaas_types_update

Update type

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas types update [OPTIONS] UUID                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the type, the PaaS slug, for example: s3

* `description`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--description`

  Description of the type

* `element_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-e
--element-name`

  Name of the element the PaaS is exposed under, for example: s3aas

* `package`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--package`

  Pip distribution name, a wheel/sdist URL or an urn:artifacts:<uuid>

* `version`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-v
--version`

  Version pin of the package

* `index_url`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--index-url`

  Pip index URL to install the package from

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: exordos metapaas types update [OPTIONS] UUID                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
 Update type                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --name          -n  TEXT  Name of the type, the PaaS slug, for example: s3                                                                                                                                                                                                                              │
│ --description       TEXT  Description of the type                                                                                                                                                                                                                                                       │
│ --element-name  -e  TEXT  Name of the element the PaaS is exposed under, for example: s3aas                                                                                                                                                                                                             │
│ --package           TEXT  Pip distribution name, a wheel/sdist URL or an urn:artifacts:<uuid>                                                                                                                                                                                                           │
│ --version       -v  TEXT  Version pin of the package                                                                                                                                                                                                                                                    │
│ --index-url         TEXT  Pip index URL to install the package from                                                                                                                                                                                                                                     │
│ --help                    Show this message and exit.                                                                                                                                                                                                                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
