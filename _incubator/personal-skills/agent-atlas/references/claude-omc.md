# Claude Code and OMC

Snapshot checked 2026-07-07; verify live state for current-version or active-configuration questions.

## Identity

- Claude Code is the client/harness.
- OMC (`oh-my-claude-sisyphus`) is an orchestration/plugin layer for Claude Code, not a model
  provider.
- Anthropic is the usual provider; the configured Claude model is a separate field.

## Workstation surfaces

| Surface | Path or command | Observed role |
|---|---|---|
| Vanilla root | `C:\Users\pmacl\.claude` | Default `claude` configuration root. |
| OMC root | `C:\Users\pmacl\.claude-omcc` | Separate profile selected through `CLAUDE_CONFIG_DIR`. |
| Launchers | `C:\Users\pmacl\OneDrive\Documents\PowerShell\Microsoft.PowerShell_profile.ps1` | Defines the local aliases/functions below. |
| OMC package | global npm package `oh-my-claude-sisyphus` | Provides the `omc` command. |

Observed launcher split:

| Command | Meaning |
|---|---|
| `claude` | Vanilla Claude Code. |
| `claudeDanger` | Vanilla root with `--dangerously-skip-permissions`. |
| `omcc`, `claudeOmc` | OMC profile; snapshot launchers used danger mode. |
| `omccSafe`, `claudeOmcSafe` | OMC profile without danger mode. |
| `omcProfile` | OMC CLI with `CLAUDE_CONFIG_DIR=C:\Users\pmacl\.claude-omcc`. |

The launcher definitions, not these labels, determine current behavior.

## Diagnostics

```powershell
Get-Command claude,claudeDanger,claudeOmc,claudeOmcSafe,omcProfile,omcc,omccSafe
claude --version
omcc --version
omccSafe --version
omcProfile --version
npm list -g oh-my-claude-sisyphus --depth=0
```

For transcript discovery facts, see [Raw transcripts and field availability](transcripts-and-fields.md).
For retrieving or analyzing prior Claude conversations, use `chat-history`.
