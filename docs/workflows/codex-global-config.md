# Codex Global Configuration

This repository owns reviewed, machine-global Codex configuration under
`config/codex/global/`. This lane is for Codex-native prompts and custom-agent
profiles that must apply across projects. It uses the same operator-facing update
entrypoint as skill distribution, with a target-specific adapter underneath.

## Native surface mapping

The reviewed lane currently carries two custom-agent profiles and one global activation fragment;
none is embedded as prompt text in `config.toml`:

| Reviewed source | Live Codex surface | Effect |
|---|---|---|
| `agents/chrome-pilot.toml` | `~/.codex/agents/chrome-pilot.toml` | Codex discovers the custom agent whose authoritative name is `chrome_pilot`. |
| `agents/chat-history-researcher.toml` | `~/.codex/agents/chat-history-researcher.toml` | Codex discovers the optional `chat_history_researcher` specialist for bounded large-corpus retrieval and analysis. |
| `AGENTS.browser-delegation.md` | Managed block in `~/.codex/AGENTS.md` | The primary agent is instructed to delegate browser work to `chrome_pilot`. |
| No source in this profile | `~/.codex/config.toml` | Unchanged. It owns global Codex settings, not durable natural-language instructions. |

The activation chain is:

```text
frozenSkillz reviewed sources
  |-- chrome-pilot.toml ----------> ~/.codex/agents/chrome-pilot.toml
  |                                  makes the named worker discoverable
  |-- chat-history-researcher.toml -> ~/.codex/agents/chat-history-researcher.toml
  |                                  makes the named worker discoverable
  `-- browser delegation Markdown -> managed block in ~/.codex/AGENTS.md
                                     tells the primary when to use that worker
```

The agent TOML files make workers available. The global Markdown supplies browser activation policy;
the personal `chat-history` skill decides when a corpus is large enough to justify the optional
`chat_history_researcher`. The worker follows the skill's source-neutral capability routing and does
not impose its own provider order, retry policy, stage labels, or artifact format.
Because that skill remains in the gated personal lane, the global-config synchronizer requires an
installed `~/.agents/skills/chat-history/SKILL.md` with the `chat-history` identity before it will
plan or install the dependent agent. A clean machine therefore fails hard instead of receiving a
worker that cannot load its router; the incubator copy is not silently promoted or installed.

Codex discovers standalone personal agents from `~/.codex/agents/`; no duplicate named-agent entry
is required in `config.toml`. The `[agents]` table in
`config.toml` remains the home for global multi-agent settings such as enablement,
thread limits, and default subagent model or effort.

## Update delivery

Check or apply the complete Codex distribution:

```powershell
python scripts/sync_frozen.py --consumer codex --check
python scripts/sync_frozen.py --consumer codex --apply
```

`sync_frozen.py` is the operator entrypoint. It runs a conflict-checking preflight,
then delegates to two format-specific components:

- `sync_frozen_skills.py` owns exact skill directories and its distribution state.
- `sync_codex_global_config.py` owns native Codex files and partial-file blocks.

This separation avoids applying directory-replacement semantics to shared config
files while keeping one command for routine Codex updates.

The native-config adapter supports `--check`, `--diff`, `--apply`, and
`--rollback <transaction-id>`. It records source revision and content hashes under
`~/.codex/.frozenSkillz/codex-global-config/`, refuses locally modified managed
content, writes atomically, backs up every changed target in a transaction, and
re-reads each write before recording success. Explicit rollback is limited to the
latest applied transaction and refuses targets changed since that transaction, so
neither an older backup nor rollback can overwrite newer edits.

The unified command performs a shared preflight and then applies each adapter. Each
adapter enforces its own conflict and transaction boundary; the wrapper is not one
cross-adapter filesystem transaction. If an unexpected failure occurs after one
adapter succeeds, rerun `--check` to identify the remaining drift and `--apply` to
converge it.

## Ownership rules

The synchronizer owns the complete reviewed agent files named by
`scripts/sync_codex_global_config.py` under `~/.codex/agents/` and only the marked
browser-delegation block inside `~/.codex/AGENTS.md`. It preserves all other global instructions
and agent files and fails on malformed markers, unmanaged collisions at an owned agent path, and
edits to previously managed content. When a reviewed agent filename is retired, the synchronizer
removes the old live file only if it still matches the recorded managed digest; a locally modified
retired file is a conflict. The exact unmarked delegation fragment may be adopted once during
migration; arbitrary live content is never adopted as managed state.

## Runtime verification boundary

`--check` proves that reviewed files are materialized and unmodified. It does not prove that an
already-running client session has refreshed its custom-agent roster or that a particular
orchestration adapter exposes named-agent selection. Start a new Codex session after installing or
updating custom agents, delegate one bounded task to the exact named type, and inspect the spawned
thread for that profile's instructions and configured model. Treat a generic child whose task is
merely labeled with the agent name as **not runtime-loaded**.

If the active adapter exposes no named-agent selector, report that runtime boundary;
do not claim that the profile was used based only on its filename or task label.

Runtime activation was verified on 2026-08-03 with Codex CLI 0.146.0 by starting an
ephemeral `codex exec` session and dispatching a bounded Chrome task to the exact
`chrome_pilot` custom-agent type. Codex discovered the named profile, spawned that
type without a full-history fork, and the worker returned the title of the page it
opened. This confirms the installed profile is runtime-loadable; repeat the bounded
probe after changing the profile or upgrading Codex.

The predecessor `chat_history_researcher` profile was runtime-loaded on 2026-08-03 with Codex CLI
0.146.0, and the global-config migration removed its earlier filename. That historical probe does
not validate the current source-neutral profile. Re-run a bounded large-corpus task after installing
this revision, and verify that the spawned worker uses the configured Luna/high/fast profile without
inventing a provider order or mandatory stages. Named custom-agent selection rejects a full-history
fork, so coordinator instructions must provide a complete brief and use no full-history fork.

## Design references

- [Codex subagents](https://developers.openai.com/codex/subagents/): native custom-agent locations, schema, inheritance, and activation.
- [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md/): global instruction discovery and precedence.
- [Oh My OpenAgent](https://github.com/code-yeongyu/oh-my-openagent): harness-specific adapters behind a shared installation/runtime architecture.
- [Oh My ClaudeCode reference](https://github.com/Yeachan-Heo/oh-my-claudecode/blob/main/docs/REFERENCE.md): native-surface installation plus doctor checks and owned-file cleanup.
- [Superpowers](https://github.com/obra/superpowers): harness-native installation and update delivery.
