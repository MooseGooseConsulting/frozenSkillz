# OpenCode and oh-my-openagent

Snapshot checked 2026-07-07; verify live state for current-version or active-configuration questions.

## Identity

OpenCode is the client/harness. oh-my-openagent is an orchestration/configuration layer for
OpenCode. Providers such as OpenRouter and individual model identifiers are separate from both.

- CLI snapshot: `opencode` -> `C:\Users\pmacl\AppData\Roaming\npm\opencode.ps1`, version
  `1.17.12`.
- Config root: `C:\Users\pmacl\.config\opencode`.

## Surfaces

| Surface | Path | Notes |
|---|---|---|
| oh-my-openagent config | `.config\opencode\oh-my-openagent.json` | The unsuffixed file was live in the snapshot; timestamped backup siblings also existed. |
| Profiles | `.config\opencode\profiles\`, `model-profiles.md`, `burner-vs-code-opus.jsonc` | |
| Provider inventory | `.config\opencode\AVAILABLE_PROVIDERS.md` | Availability does not prove a provider is active. |
| Agent contract | `.config\opencode\AGENTS.md` | |
| Skills/LSP | `.config\opencode\skills\`, `.config\opencode\lsp.json` | |
| Auth | `.local\share\opencode\auth.json`, `account.json` | Sensitive; location only. |

## Diagnostics

```powershell
opencode --version
```

See [OpenRouter](openrouter.md) for provider routing. The canonical transcript store/schema facts
are in [Raw transcripts and field availability](transcripts-and-fields.md). Use `chat-history` for
retrieval or analysis.
