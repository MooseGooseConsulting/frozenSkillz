# Doppler Setup

Install, authenticate, and link a directory to a project/config. Validate current syntax with `doppler <command> --help` before editing durable scripts.

## Install

```shell
# Windows
winget install doppler

# macOS
brew install dopplerhq/cli/doppler

# Linux / CI
(curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh || wget -t 3 -qO- https://cli.doppler.com/install.sh) | sh
```

## Authenticate And Link

```shell
doppler login
doppler setup -p my-project -c dev
doppler run -- python app.py
```

Commit a team setup file (`doppler.yaml`):

```yaml
setup:
  project: my-project
  config: dev

flags:
  analytics: false
  env-warning: false
  update-check: false
```

Then teammates can run:

```shell
doppler setup --no-interactive
doppler run -- your-command
```

## Running Commands

POSIX:

```shell
doppler run -- uv run pytest
doppler run -p my-project -c dev -- ./scripts/test.sh
doppler run --command './configure && ./process-jobs'
```

PowerShell:

```powershell
doppler run -- uv run pytest
doppler run -p my-project -c dev -- powershell -NoProfile -File .\scripts\test.ps1
doppler run --command "uv run pytest"
```

Use `--command` for shell operators, pipelines, and command strings. Use `-- ...` for normal argv forwarding.

## Adding Secrets

```shell
doppler secrets set API_KEY value
printf '%s' "$CERT_CONTENTS" | doppler secrets set CERT_PEM
doppler secrets upload secrets.env
```

PowerShell:

```powershell
doppler secrets set API_KEY value
Get-Content -Raw .\cert.pem | doppler secrets set CERT_PEM
doppler secrets upload .\secrets.env
```

Prefer piping multiline values instead of pasting them into shell history. Prefer `--silent` on mutating commands when the CLI would otherwise print a secrets table.
