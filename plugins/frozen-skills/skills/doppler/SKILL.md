---
name: doppler
description: >-
  Manage secrets with the Doppler CLI: doppler run injection, names-only
  diagnostics, set/upload secrets, service tokens for CI, and no-print hygiene.
  Use when the current task requires retrieving, injecting, setting, rotating,
  verifying, or names-only-checking a credential, whether the user asked for
  that or the task itself led there. Do not load merely because .env, tokens,
  API keys, credentials, or "secrets" appear in your own planning context or in
  files you are reading; not for config-file reads, Kubernetes Secret reads,
  database connection strings, or speculative "secrets hygiene" passes; do not
  preload because a later step might need a credential.
---

# Doppler

**Before using this skill:** confirm a credential action (retrieve, inject, set, rotate, verify, or names-only check) is part of the task you are working on right now. If not, do not proceed.

If unsure whether a value is a secret, treat it as a secret. Keep secret values out of chat, logs, diffs, committed files, and durable docs.

Use Doppler as a secrets injection layer. Prefer CLI-driven environment injection (`doppler run -- ...`) over in-process SDK calls, vault enumeration, or committed secret files.

## Operating Rules

- Do not print secret values into transcripts unless the user explicitly asks for the value.
- Prefer storing application and workstation secrets in Doppler. CI and production systems should store only the scoped `DOPPLER_TOKEN` or platform-required bootstrap credential.
- Document secret names, projects/configs, and injection commands; do not document secret values or one-off local token state.
- Prefer names-only or boolean checks: `doppler secrets --only-names`, `test -n "$VAR"`, or PowerShell `if ($env:VAR)`.
- Do not commit `.env`, downloaded secret exports, service tokens, fallback files, or rendered config files containing credentials.
- Use service tokens only in CI/production secret stores, never in repo files.
- Treat `doppler.yaml` as safe repo configuration: it names project/config only.
- Use `doppler run -- ...` for normal application execution. Application code should read ordinary environment variables.
- Use `doppler run --mount ...` when an application must read a secret file; prefer environment injection for normal command execution.
- Avoid `--preserve-env` for secrets unless there is a deliberate reason to let pre-existing shell values override Doppler.
- Use `--silent` for destructive secret-management commands where possible; some CLI versions print a secrets table after mutation.
- Do not use bare configuration display, its `--all` variant, or the configuration debug subcommand in an agent transcript. Those views include token fields, and the debug form may reveal the saved CLI token. Query only known non-secret options explicitly.
- For current command syntax, verify with `doppler --version` and `doppler <command> --help` before changing scripts or docs.

## Core Model

| Concept | Meaning |
|---|---|
| Workplace | Top-level Doppler organization |
| Project | Secret namespace for an app, service, or shared secret group |
| Config | Environment within a project, such as `dev`, `stg`, or `prd` |
| Secret | Key-value pair injected into child processes |
| Service token | Revocable token scoped to a project/config for CI or production |
| CLI token | Developer login token saved by `doppler login` |

Resolution order for most CLI commands is service token, explicit flags, local scoped config, then parent scoped config.

## Quick Start

Install:

```shell
# Windows
winget install doppler

# macOS
brew install dopplerhq/cli/doppler

# Linux / CI
(curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh || wget -t 3 -qO- https://cli.doppler.com/install.sh) | sh
```

Set up a repo:

```shell
doppler login
doppler setup -p my-project -c dev
doppler run -- python app.py
```

Commit a team setup file:

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

POSIX shells:

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

## Safe Diagnostics

Check active config:

```shell
doppler configure get project config --plain
doppler me
doppler secrets --only-names
```

Check whether a secret is injected without printing the value:

```shell
doppler run -- sh -c 'test -n "$DATABASE_URL" && echo DATABASE_URL=set || echo DATABASE_URL=missing'
```

```powershell
doppler run -- powershell -NoProfile -Command "if ($env:DATABASE_URL) { 'DATABASE_URL=set' } else { 'DATABASE_URL=missing' }"
```

Only use raw value commands for intentional secret handling:

```shell
doppler secrets get SECRET_NAME --plain
```

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

Prefer piping multiline values instead of pasting them into shell history.

## CI And Production

Create one service token per project/config and store it in the CI provider's secret store as `DOPPLER_TOKEN`:

```shell
doppler configs tokens create -p my-project -c prd ci-token --plain
```

GitHub Actions pattern:

```yaml
- name: Install Doppler CLI
  run: (curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh || wget -t 3 -qO- https://cli.doppler.com/install.sh) | sh
- name: Run tests
  run: doppler run -- uv run pytest
  env:
    DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
```

Service token project/config takes precedence over `doppler setup` and `-p`/`-c` flags.

## Fallback Files

Doppler may write encrypted fallback/cache files under the configured Doppler directory. Use them for availability, not as repo artifacts.

```shell
doppler run --fallback-only -- ./start.sh
doppler run --no-fallback -- ./start.sh
doppler run clean --dry-run
```

If a fallback must move between build and deploy stages, use a dedicated passphrase from the CI secret store, not a literal in YAML:

```shell
doppler secrets download --passphrase "$DOPPLER_FALLBACK_PASSPHRASE" -p my-project -c prd
doppler run --fallback ./doppler.json --passphrase "$DOPPLER_FALLBACK_PASSPHRASE" -- ./start.sh
```

## Mounting Secrets

`doppler run --mount ...` exposes secrets through an ephemeral mounted file path and does not inject the secrets into the environment. The path is available as `DOPPLER_CLI_SECRETS_PATH`.

```shell
doppler run --mount secrets.json -- cat secrets.json
doppler run --mount .env --format env -- ./start.sh
doppler run --mount config.yml --mount-template config.yml.tmpl -- ./start.sh
```

Some frameworks reject named pipes or ephemeral files. If that happens, use environment injection with plain `doppler run -- ...`.

## References

Load these only when needed:

- [references/commands.md](references/commands.md): command reference, platform notes, and troubleshooting.
- [references/ci-fallbacks.md](references/ci-fallbacks.md): CI, service tokens, fallback files, and Docker patterns.

## Review Checklist

Before promoting or committing Doppler work:

- `doppler --version`
- `doppler configure get project config --plain`
- `doppler me`
- `doppler secrets --only-names`
- Run the target command through `doppler run -- ...`
- Confirm no secret values were added to files, logs, diffs, or transcripts.

## Learnings

### 2026-06-29

#### What Worked
- Reuse one **classic** GitHub PAT (`GHCR_BUILD_TOKEN`) for both GHCR push (`kubernetes.io/dockerconfigjson` → `ghcr-push`) and Shipwright private-repo clone (`kubernetes.io/basic-auth` → `git-clone`). No separate `GITHUB_CLONE_TOKEN` if the PAT has `repo` + `write:packages`.
- Boolean Doppler checks without printing values: `doppler secrets get KEY -p PROJECT -c CONFIG --plain 2>$null` then test `$LASTEXITCODE` and `[string]::IsNullOrWhiteSpace($v)` / `$v.Length` — never echo the value.
- `doppler secrets --only-names` across projects to reconcile manifest `remoteRef.key` names vs vault (e.g. `LLM_ARCHIVAL_DB_PASSWORD` vs `LLMARCHIVER_DB_PASSWORD`).
- Audit scripts must call seed/bootstrap helpers with **read-only** flags (`-ReadOnly`); audits that invoke writers mutate production state.

#### What Failed
- Assuming credentials are missing before a Doppler names/existence audit — many keys already existed under `databases/dev` or `coldaine-k8s/dev_homelab`.
- Fine-grained GitHub PAT UI for GHCR — **no** `write:packages` under per-repo permissions; use a **classic** PAT for `ghcr.io` push.
- Treating `SOPS_AGE_KEY` as the age decrypt key when it was truncated; use `AGE_PRIVATE_KEY` when present and valid (`StartsWith('AGE-SECRET-KEY')`).

#### Configuration Notes
- ESO `ClusterSecretStore` only sees secrets in the **service token's** Doppler project/config. Keys in other projects (e.g. `secrets_managment/dev` for Proxmox, `databases/dev` for legacy names) require token scope alignment or manifest key migration to the cluster project (`coldaine-k8s/dev_homelab`).
- Shipwright git clone failure (`could not read Username for 'https://github.com'`) is usually missing `spec.source.git.cloneSecret`, not a missing Doppler key — check wiring before creating new keys.
- If user pastes a token in chat: store via `doppler secrets set ... --silent`, verify ESO sync, warn about rotation — do not repeat the token in the response.
