# Qwen Code

Configuration snapshot checked 2026-06-08 and root rechecked 2026-07-07. Raw-format facts updated
from AgentsView `v0.40.1` at commit `9ef48912` and its pinned Qwen Code producer source.

## Identity

Qwen Code is a client/harness. The Qwen model family and its serving provider are separate. A
`.qwen` directory alone does not prove the CLI is currently installed or which model/provider was
used.

- Config root: `C:\Users\pmacl\.qwen`.
- Snapshot contents were minimal: `installation_id`, `output-language.md`, an empty `logs.json`, and
  debug text.
- No `qwen` CLI was found on `PATH` in the 2026-07-07 snapshot.

## Diagnostics

```powershell
Get-Command qwen -ErrorAction SilentlyContinue
Get-ChildItem "$env:USERPROFILE\.qwen" -Recurse -File | Select-Object FullName,Length
```

The canonical transcript location and raw fields are in
[Raw transcripts and field availability](transcripts-and-fields.md). Use `chat-history` if the goal
is to locate prior Qwen conversations.
