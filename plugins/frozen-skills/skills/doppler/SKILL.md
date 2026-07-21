---
name: doppler
description: >-
  Manage secrets with the Doppler CLI: doppler run injection, names-only
  diagnostics, set/upload secrets, service tokens for CI, and no-print hygiene.
  Use when the user mentions Doppler, doppler run, service tokens, secret
  injection, or asks to store, rotate, or verify API keys, tokens, passwords,
  or .env credentials. Do not use for ordinary non-secret environment variables
  or general app config unrelated to credentials.
---

# Doppler

If unsure whether a value is a secret, treat it as a secret. Prefer CLI injection (`doppler run -- ...`) over SDKs, vault dumps, or committed secret files.

## Operating Rules

- Do not print secret values into transcripts unless the user explicitly asks for the value.
- Prefer storing application and workstation secrets in Doppler. CI and production should store only the scoped `DOPPLER_TOKEN` or platform-required bootstrap credential.
- Document secret names, projects/configs, and injection commands; do not document secret values or one-off local token state.
- Prefer names-only or boolean checks: `doppler secrets --only-names`, `test -n "$VAR"`, or PowerShell `if ($env:VAR)`.
- Do not commit `.env`, downloaded secret exports, service tokens, fallback files, or rendered config files containing credentials.
- Use service tokens only in CI/production secret stores, never in repo files.
- Treat `doppler.yaml` as safe repo configuration: it names project/config only.
- Use `doppler run -- ...` for normal application execution. Application code should read ordinary environment variables.
- Use `doppler run --mount ...` when an application must read a secret file; prefer environment injection for normal command execution.
- Avoid `--preserve-env` for secrets unless there is a deliberate reason to let pre-existing shell values override Doppler.
- Use `--silent` for destructive secret-management commands where possible; some CLI versions print a secrets table after mutation.
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

## Intent → Action

| User wants to… | Do |
|---|---|
| See what exists without values | `doppler secrets --only-names` |
| Run app/tests with secrets | `doppler run -- …` |
| Check one var is set | `doppler run` + set/missing check (POSIX or PowerShell) |
| Store a secret | `doppler secrets set …` (prefer pipe; `--silent` when mutating) |
| CI/prod auth | Service token as `DOPPLER_TOKEN` only |

Safe set/missing checks:

```shell
doppler run -- sh -c 'test -n "$DATABASE_URL" && echo DATABASE_URL=set || echo DATABASE_URL=missing'
```

```powershell
doppler run -- powershell -NoProfile -Command "if ($env:DATABASE_URL) { 'DATABASE_URL=set' } else { 'DATABASE_URL=missing' }"
```

Only use `doppler secrets get SECRET_NAME --plain` when the user explicitly needs the raw value.

## Workflow

1. **Identify the task**: setup, list/diagnose, set/rotate, inject/run, or CI token.
2. **Check prerequisites**: CLI installed (`doppler --version`); auth via `doppler me` or `DOPPLER_TOKEN`.
3. **Resolve scope**: project/config via `doppler configure debug`, `doppler.yaml`, or `-p`/`-c`.
4. **Act** using the intent table; prefer `doppler run -- ...` for execution.
5. **Verify** with names-only or set/missing checks — never echo secret values.

## References

Load these only when needed:

- [references/setup.md](references/setup.md): install, login, `doppler.yaml`, basic `doppler run`.
- [references/commands.md](references/commands.md): command reference, mount/templates, platform notes, troubleshooting.
- [references/ci-fallbacks.md](references/ci-fallbacks.md): CI, service tokens, fallback files, Docker patterns.
- [references/homelab-notes.md](references/homelab-notes.md): **only** when the task involves coldaine-infra, ESO/`ClusterSecretStore`, Shipwright, or GHCR PAT wiring.

## Review Checklist

Before promoting or committing Doppler work:

- `doppler --version`
- `doppler configure debug`
- `doppler secrets --only-names`
- Run the target command through `doppler run -- ...`
- Confirm no secret values were added to files, logs, diffs, or transcripts.
