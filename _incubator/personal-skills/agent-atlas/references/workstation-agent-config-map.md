# Workstation agent client map

Snapshot checked 2026-07-07. Paths are discovery hints for Patrick's Windows workstation, not a
precedence list or proof of current runtime state.

## Client, extension, and provider boundaries

| Name | Kind | Primary workstation surface |
|---|---|---|
| Claude Code | client/harness | `C:\Users\pmacl\.claude` |
| OMC | Claude Code orchestration/plugin layer | `C:\Users\pmacl\.claude-omcc` selected through local launchers |
| Codex | client/harness | `C:\Users\pmacl\.codex` |
| Cursor / `cursor-agent` | IDE and agent client surfaces | `C:\Users\pmacl\.cursor` |
| GitHub Copilot CLI | client/harness | `C:\Users\pmacl\.copilot` |
| Gemini CLI | client/harness | `C:\Users\pmacl\.gemini` |
| Antigravity | separate client/harness sharing Gemini's root | `C:\Users\pmacl\.gemini\antigravity*` |
| OpenCode | client/harness | `C:\Users\pmacl\.config\opencode` |
| oh-my-openagent | OpenCode orchestration/configuration layer | `.config\opencode\oh-my-openagent.json` |
| Kilo Code | client/harness | `C:\Users\pmacl\.config\kilo\kilo.json` (verified with Kilo 7.4.23) |
| `@kilocode/plugin` | Kilo plugin SDK/package | Installed through Kilo/npm and resolved as a plugin module; not a client or provider |
| Kimi CLI / Kimi Code | client/harness | Configuration root not verified in this atlas; raw facts are in the transcript reference |
| Goose | client/harness | `C:\Users\pmacl\.config\goose` config candidate |
| Qwen Code | client/harness | `C:\Users\pmacl\.qwen` configuration root |
| OpenRouter | provider/router, not a client | configured inside a consuming client; no independent transcript root |

Anthropic, OpenAI, Google, OpenRouter, and other inference backends are providers. Claude, GPT,
Gemini, Qwen, and other selected identifiers may be model families. Neither category identifies the
client that owns configuration and transcripts.

## Shared workstation surfaces

| Surface | Path | Snapshot role |
|---|---|---|
| PowerShell launchers | `C:\Users\pmacl\OneDrive\Documents\PowerShell\Microsoft.PowerShell_profile.ps1` | Local commands and profile-specific environment variables. |
| Personal shared skills | `C:\Users\pmacl\.agents\skills` | Personal authoring/discovery root used by some clients; client support must be verified individually. |
| Claude compatibility skills | `C:\Users\pmacl\.claude\skills` | Claude-specific surface. |
| Codex runtime skills | `C:\Users\pmacl\.codex\skills` | Codex-specific runtime/system surface. |
| Frozen active skills | `D:\_projects\frozenSkillz\plugins\frozen-skills\skills` | Reviewed repository source, not a live client root. |
| Frozen gated skills | `D:\_projects\frozenSkillz\_incubator\personal-skills` | Review material; not installed by the active synchronizer. |

## Dated inventory observations

These are snapshots, not current-version claims:

| Checked | Observation |
|---|---|
| 2026-07-07 | Codex `0.142.5`; OpenCode `1.17.12`; Kilo `7.3.54`; GitHub Copilot CLI `1.0.50`; Goose `1.38.0`. Cursor/`cursor-agent` and Gemini were present, but the recovered snapshot did not record a reliable version for both. |
| 2026-07-07 | `.qwen` existed but `qwen` was not found on `PATH`; the earlier 2026-06-08 survey found no local Qwen chats. |
| 2026-08-24 | Kilo was `7.4.23`, and `kilo debug paths` identified `C:\Users\pmacl\.config\kilo` as its config root. |
| 2026-08-24 | `C:\Users\pmacl\.continue\skills` existed with `gws-gmail`, `gws-gmail-read`, `gws-gmail-send`, and `gws-shared`; whether Continue itself is active remains unknown. |

For raw stores and field availability, read
[Raw transcripts and field availability](transcripts-and-fields.md). If the request is to find a prior
conversation rather than explain a harness, use `chat-history`. For the repository/policy/learnings
location map, see [Where agent-tool information lives](where-information-lives.md).
