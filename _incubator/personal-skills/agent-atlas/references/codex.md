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
| Main config | `C:\Users\pmacl\.codex\config.toml` | Snapshot top-level settings included `approval_policy`, `model`, `model_reasoning_effort`, `personality`, `sandbox_mode`, `web_search`, `service_tier`, `notify`, `agents`, and `plugins`. |
| Plugins | `config.toml` plugin blocks and `C:\Users\pmacl\.codex\plugins\` | The 2026-07-07 enabled snapshot named github, vercel, documents, spreadsheets, presentations, superpowers, notion, jam, coderabbit, cloudflare, hugging-face, computer-use, and browser. Treat the live config as current state. |
| Skills | `C:\Users\pmacl\.codex\skills\` | Codex runtime/system surface. |
| Rules and hooks | `C:\Users\pmacl\.codex\rules\`, `C:\Users\pmacl\.codex\hooks\` | Inspect live contents for supported/current behavior. |
| Auth/secrets | `C:\Users\pmacl\.codex\auth.json`, `C:\Users\pmacl\.codex\secrets\` | Sensitive; identify location only unless secret access is explicitly required. |

## Dated known issue

The 2026-07-07 snapshot recorded a `morph-mcp` version-mismatch warning at Codex startup. It was
pre-existing and unrelated to the Claude/OMC launcher split. The root cause, current presence, and
fix or suppression remain unverified.

The same snapshot observed an `.omc` marker below the Codex session area. Which component wrote it
and what it meant were not established; its presence did not make Codex an OMC/Claude session.

## Diagnostics

```powershell
codex --version
Get-Command codex
Select-String -Path "$env:USERPROFILE\.codex\config.toml" -Pattern '^(model|approval_policy|sandbox_mode)'
```

For transcript paths and raw field availability, see
[Raw transcripts and field availability](transcripts-and-fields.md). For cross-session retrieval, use
`chat-history`. For unresolved configuration and integration questions, see
[Harness coverage and known gaps](coverage-gaps.md).
