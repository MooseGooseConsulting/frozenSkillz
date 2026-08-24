# OpenRouter

Snapshot checked 2026-07-07; verify live state for current routing questions.

## Identity

OpenRouter is a model-routing provider/API, not an agent client, harness, transcript owner, or app
configuration root. An OpenRouter-backed conversation still belongs to the consuming harness, such
as OpenCode. The selected model is another distinct identifier.

## Workstation observations

| Consumer/surface | Location | Snapshot fact |
|---|---|---|
| OpenCode provider inventory | `C:\Users\pmacl\.config\opencode\AVAILABLE_PROVIDERS.md` | Listed `openrouter`; listing did not prove it was active. |
| OpenCode auth store | `C:\Users\pmacl\.local\share\opencode\auth.json` | Sensitive; do not inspect or copy values merely to answer a routing question. |
| Process environment | `OPENROUTER*` variables | None were present in the checked shell on 2026-07-07; re-check before relying on that observation. |

Provider credentials belong in a scoped secret store or the consuming client's auth store, not in
this skill or documentation. Secret-name or presence checks do not establish which model a session
used; use harness configuration or transcript fields when available.

## Diagnostics

```powershell
Get-ChildItem env: | Where-Object Name -match 'OPENROUTER' | ForEach-Object Name
Select-String -Path "$env:USERPROFILE\.config\opencode\AVAILABLE_PROVIDERS.md" -Pattern 'openrouter'
```
