# Gemini CLI and Antigravity

Configuration snapshot checked 2026-07-07. Raw-format facts updated from AgentsView `v0.40.1` at
commit `9ef48912`; verify live state for current-version or active-configuration questions.

## Identity

Gemini CLI and Antigravity are distinct client/harness surfaces that share a `.gemini` root on this
workstation. Google is the provider; a Gemini model identifier is separate from both client names.

- CLI snapshot: `gemini` -> `C:\Users\pmacl\.local\bin\gemini.ps1`. A scripted
  `gemini --version` returned no text in the recovered snapshot.
- Shared config root: `C:\Users\pmacl\.gemini`.

## Surfaces

| Surface | Path | Notes |
|---|---|---|
| Main settings | `C:\Users\pmacl\.gemini\settings.json` | Snapshot keys included model, security, tools, MCP, skills, IDE, agents, and context. |
| Global context | `C:\Users\pmacl\.gemini\GEMINI.md` | Global instruction/context surface. |
| Skills/extensions | `C:\Users\pmacl\.gemini\skills\`, `extensions\` | |
| Antigravity | `antigravity\`, `antigravity-cli\`, `antigravity-ide\`, `antigravity-browser-profile\` below the shared root | Antigravity does not use an independent top-level root in this snapshot. |
| Trust/policy | `trusted_hooks.json`, `trustedFolders.json`, `policies\` | |
| Accounts | `google_accounts.json` | Sensitive; do not copy contents. |

## Diagnostics

```powershell
gemini --version
Get-Content "$env:USERPROFILE\.gemini\settings.json" -Raw | ConvertFrom-Json |
  ForEach-Object { $_.PSObject.Properties.Name }
```

See [Raw transcripts and field availability](transcripts-and-fields.md) for format caveats and raw
capabilities. Use `chat-history` for prior-conversation retrieval.
