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
| MCP servers | `C:\Users\pmacl\.cursor\mcp.json` | The 2026-07-07 snapshot listed Pieces, morph-mcp, notebooklm-mcp, and context7; names and enabled state require a live check. |
| Rules | `C:\Users\pmacl\.cursor\rules\` and IDE settings | Project-local `.cursor` files may also exist. |
| Skills | `C:\Users\pmacl\.cursor\skills\`, `C:\Users\pmacl\.cursor\skills-cursor\` | The semantic difference between the two roots was not established in the recovered snapshot. |
| Plugins/extensions | `C:\Users\pmacl\.cursor\plugins\`, `C:\Users\pmacl\.cursor\extensions\` | |
| Other data | `C:\Users\pmacl\.cursor\ai-tracking\`, `worktrees\` | Purpose and transcript relationship were not established by the recovered snapshot. |
| Setup snapshot | `C:\Users\pmacl\.cursor\CURSOR_CONFIGURATION_REPORT.md` | A 2026-05-26 report described the workstation as predominantly global-configured; it is historical evidence, not current runtime state. |

That report estimated roughly 95% global and 5% project-level configuration, observed that recently
opened repositories generally lacked project-local Cursor rules/MCP/skills, and described more
surface as installed than used. These are historical observations, not instructions to prune or a
claim about the current repositories.

## Diagnostics

```powershell
cursor-agent --version
Get-Content "$env:USERPROFILE\.cursor\mcp.json" -Raw | ConvertFrom-Json |
  ForEach-Object { $_.mcpServers.PSObject.Properties.Name }
```

The canonical transcript location and verified/unknown fields are in
[Raw transcripts and field availability](transcripts-and-fields.md). Use `chat-history` for
conversation retrieval. See [Harness coverage and known gaps](coverage-gaps.md) for unresolved
skills, rules, worktree, and CLI questions.
