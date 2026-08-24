# GitHub Copilot CLI

Snapshot checked 2026-07-07; verify live state for current-version or active-configuration questions.

## Identity

GitHub Copilot CLI is the client/harness. GitHub account authentication, the inference provider,
and the selected model are separate concerns. The current evidence consulted here does not
establish a reliable raw model/provider field; that is unknown rather than proof of absence.

- CLI snapshot: `copilot` -> `C:\Users\pmacl\AppData\Roaming\npm\copilot.ps1`, version
  `GitHub Copilot CLI 1.0.50`.
- Related CLI: `gh` -> `C:\Program Files\GitHub CLI\gh.exe`.
- Config root: `C:\Users\pmacl\.copilot`.

## Surfaces

| Surface | Path | Notes |
|---|---|---|
| Config | `C:\Users\pmacl\.copilot\config.json` | Snapshot file contained only `firstLaunchAt`. |
| Agents and hooks | `C:\Users\pmacl\.copilot\agents\`, `C:\Users\pmacl\.copilot\hooks\` | Inspect live contents for current behavior. |
| Skills | `C:\Users\pmacl\.copilot\skills\` | Client-specific skill surface. |

## Diagnostics

```powershell
copilot --version
gh auth status
```

See [Raw transcripts and field availability](transcripts-and-fields.md) for verified and unknown
raw fields. Use `chat-history` to retrieve or analyze prior Copilot conversations.
