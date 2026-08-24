# Cursor

Snapshot checked 2026-07-07; verify live state for current-version or active-configuration questions.

## Identity

Cursor IDE and `cursor-agent` are client/harness surfaces. Their configured provider and model are
separate metadata and may vary by session.

- IDE snapshot: `C:\Program Files\cursor\`; `cursor` resolves through
  `resources\app\bin\cursor.cmd`.
- Agent CLI snapshot: `cursor-agent` ->
  `C:\Users\pmacl\AppData\Local\cursor-agent\cursor-agent.ps1`.
- Config root: `C:\Users\pmacl\.cursor`.

## Surfaces

| Surface | Path | Notes |
|---|---|---|
| MCP servers | `C:\Users\pmacl\.cursor\mcp.json` | Server names and enabled state are live facts. |
| Rules | `C:\Users\pmacl\.cursor\rules\` and IDE settings | Project-local `.cursor` files may also exist. |
| Skills | `C:\Users\pmacl\.cursor\skills\`, `C:\Users\pmacl\.cursor\skills-cursor\` | The semantic difference between the two roots was not established in the recovered snapshot. |
| Plugins/extensions | `C:\Users\pmacl\.cursor\plugins\`, `C:\Users\pmacl\.cursor\extensions\` | |
| Other data | `C:\Users\pmacl\.cursor\ai-tracking\`, `worktrees\` | Purpose and transcript relationship were not established by the recovered snapshot. |
| Setup snapshot | `C:\Users\pmacl\.cursor\CURSOR_CONFIGURATION_REPORT.md` | A 2026-05-26 report described the workstation as predominantly global-configured; it is historical evidence, not current runtime state. |

## Diagnostics

```powershell
cursor-agent --version
Get-Content "$env:USERPROFILE\.cursor\mcp.json" -Raw | ConvertFrom-Json |
  ForEach-Object { $_.mcpServers.PSObject.Properties.Name }
```

The canonical transcript location and verified/unknown fields are in
[Raw transcripts and field availability](transcripts-and-fields.md). Use `chat-history` for
conversation retrieval.
