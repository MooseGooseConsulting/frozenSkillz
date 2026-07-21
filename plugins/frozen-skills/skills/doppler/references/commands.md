# Doppler Command Reference

Use this reference when the root skill does not contain enough detail. Validate current syntax with `doppler <command> --help` before editing durable scripts.

## Contents

- Authentication
- Setup And Configuration
- Secret Management
- Mounting Secrets
- Template Substitution
- Secret References
- Environment Variables
- Troubleshooting

## Authentication

```shell
doppler login
doppler login --scope ./
doppler logout
doppler me
```

Local developer auth is saved in the Doppler config directory. CI and production should use service tokens through `DOPPLER_TOKEN`.

## Setup And Configuration

```shell
doppler setup
doppler setup -p my-project -c dev
doppler setup --no-interactive
doppler configure
doppler configure --all
doppler configure debug
doppler configure unset project config --scope /path/to/project
```

Directory scopes are path based. If a project moves, rerun `doppler setup`.

## Secret Management

```shell
doppler secrets --only-names
doppler secrets set KEY value
doppler secrets get KEY
doppler secrets get KEY --plain
doppler --silent secrets delete KEY --yes
doppler secrets upload secrets.env
doppler secrets download --no-file --format json
doppler secrets download --no-file --format env
```

Avoid `--plain` in agent transcripts unless the user explicitly needs the value. Prefer `--silent` for deletes because some CLI versions print a post-delete secrets table.

PowerShell multiline upload:

```powershell
Get-Content -Raw .\secret.pem | doppler secrets set SECRET_PEM
```

POSIX multiline upload:

```shell
cat ./secret.pem | doppler secrets set SECRET_PEM
```

## Mounting Secrets

`doppler run --mount ...` exposes secrets through an ephemeral mounted file path and does not inject the secrets into the environment. The path is available as `DOPPLER_CLI_SECRETS_PATH`.

```shell
doppler run --mount secrets.json -- cat secrets.json
doppler run --mount .env --format env -- ./start.sh
doppler run --mount config.yml --mount-template config.yml.tmpl -- ./start.sh
```

Some frameworks reject named pipes or ephemeral files. If that happens, use environment injection with plain `doppler run -- ...`.

## Template Substitution

Doppler templates use Go `text/template` syntax.

```shell
doppler secrets substitute config.yaml.tmpl
doppler secrets substitute config.yaml.tmpl --output config.yaml
```

Example template:

```yaml
host: {{.HOST}}
port: {{.PORT}}
private_key: {{tojson .PRIVATE_KEY}}
{{with .OPTIONAL_LOGFILE}}
logfile: {{.}}
{{end}}
```

Useful functions:

- `tojson`: render a value as a JSON string.
- `fromjson`: parse a JSON secret into template data.

Rendered files can contain credentials. Keep them ignored unless they are credential-free.

## Secret References

Secret values can reference other secrets:

```text
${SECRET_NAME}
${config.SECRET_NAME}
${project.config.SECRET_NAME}
```

References resolve when secrets are read. If a reference cannot resolve, Doppler may return the literal reference string, so check application startup diagnostics for unresolved placeholders.

## Environment Variables

Doppler injects project secrets as ordinary environment variables into the child process.

Doppler control variables include:

| Variable | Purpose |
|---|---|
| `DOPPLER_TOKEN` | Service token for CI/production |
| `DOPPLER_PROJECT` | Project selection |
| `DOPPLER_CONFIG` | Config selection |
| `DOPPLER_PASSPHRASE` | Fallback encryption/decryption passphrase |
| `DOPPLER_API_HOST` | API endpoint |
| `DOPPLER_CONFIG_DIR` | Local config directory |

Doppler-provided child-process variables include:

| Variable | Purpose |
|---|---|
| `DOPPLER_PROJECT` | Active project |
| `DOPPLER_CONFIG` | Active config |
| `DOPPLER_ENVIRONMENT` | Active environment |
| `DOPPLER_CLI_VERSION` | CLI version |
| `DOPPLER_CLI_SECRETS_PATH` | Mounted file path when using `--mount` |

## Troubleshooting

Wrong or missing secret:

```shell
doppler configure debug
doppler secrets --only-names
doppler run -- sh -c 'test -n "$MY_SECRET" && echo MY_SECRET=set || echo MY_SECRET=missing'
```

PowerShell:

```powershell
doppler run -- powershell -NoProfile -Command "if ($env:MY_SECRET) { 'MY_SECRET=set' } else { 'MY_SECRET=missing' }"
```

Wrong directory scope:

```shell
doppler configure --all
doppler configure unset project config --scope /path/to/wrong/scope
```

Fallback file decryption failure:

```shell
doppler run clean --dry-run
doppler run --no-fallback -- ./start.sh
```

Installer path missing in CI:

```shell
(curl -Ls https://cli.doppler.com/install.sh | sh -s -- --no-install --no-package-manager)
./doppler run -- ./build.sh
```
