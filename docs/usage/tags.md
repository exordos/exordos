# Resource tags

Supported create commands accept repeated `--tag` options. Existing update
commands accept `--tag` to replace the list and `--clear-tags` to remove it:

```bash
exordos dns domains add -p PROJECT_UUID -n example.com --tag env:prod
exordos dns domains update DOMAIN_UUID --tag env:test --tag team:platform
exordos dns domains update DOMAIN_UUID --clear-tags
```

Omitting these options leaves tags unchanged on update and uses the server's
default on creation. `--tag` and `--clear-tags` cannot be combined. Tags on
`configs add-from-env` and `secret ssh_keys add` apply to every resource created
by the command. Groups without an existing create or update command retain the
dedicated `tags` command below.

Use the `tags` subcommand to replace or clear the tags of a Core resource.
Repeat `--tag` for every tag in the new list. The command sends only the `tags`
field to the existing update API and displays the updated resource.

```bash
exordos dns domains tags DOMAIN_UUID --tag env:prod --tag team:platform
exordos secret certificates tags CERTIFICATE_UUID --tag dns:public
exordos dns domains tags DOMAIN_UUID --clear
```

`--tag` replaces the complete list rather than appending to it. To retain an
existing tag, include it in the new list. Values containing spaces should be
quoted. `--clear` removes all tags and cannot be combined with `--tag`.
Omitting both options is an error and does not send a request.

The command is available in these groups:

- `compute sets`
- `configs`
- `dns domains`
- `em services`
- `iam idps`
- `iam permissions`
- `network load_balancers`
- `secret certificates`
- `secret passwords`
- `secret rsa_keys`
- `secret secrets`
- `secret ssh_keys`
- `vs values`

The existing API permissions apply. Resource types without a writable `tags`
field, including read-only repository elements, do not expose this command.
Core may reprocess a resource after an update according to its existing
lifecycle behavior.
