# Codex

Snapshot checked 2026-07-07; verify live state for current-version or active-configuration questions.

## Identity

Codex is the client/harness. OpenAI is the provider, and the configured model is a separate value
in `config.toml` or session metadata. Do not classify every OpenAI-backed session as Codex.

- CLI snapshot: `codex` -> `C:\Users\pmacl\.local\bin\codex.ps1`, version
  `codex-cli 0.142.5`.
- Config root: `C:\Users\pmacl\.codex`.

## Surfaces

| Surface | Path | Notes |
|---|---|---|
| Main config | `C:\Users\pmacl\.codex\config.toml` | Snapshot top-level settings included model, reasoning effort, approval, sandbox, service tier, agents, and plugins. |
| Plugins | `config.toml` plugin blocks and `C:\Users\pmacl\.codex\plugins\` | Installed/enabled sets are live state. |
| Skills | `C:\Users\pmacl\.codex\skills\` | Codex runtime/system surface. |
| Rules and hooks | `C:\Users\pmacl\.codex\rules\`, `C:\Users\pmacl\.codex\hooks\` | Inspect live contents for supported/current behavior. |
| Raw sessions | `C:\Users\pmacl\.codex\sessions\<year>\...\*.jsonl` | Also see archived sessions and `history.jsonl` in the transcript reference. |
| Auth/secrets | `C:\Users\pmacl\.codex\auth.json`, `C:\Users\pmacl\.codex\secrets\` | Sensitive; identify location only unless secret access is explicitly required. |

## Diagnostics

```powershell
codex --version
Get-Command codex
Select-String -Path "$env:USERPROFILE\.codex\config.toml" -Pattern '^(model|approval_policy|sandbox_mode)'
```

For transcript paths and raw field availability, see
[Raw transcripts and field availability](transcripts-and-fields.md). For cross-session retrieval, use
`chat-history`.
