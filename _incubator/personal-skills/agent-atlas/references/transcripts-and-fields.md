# Raw transcripts and field availability

This reference answers storage and raw-format questions about the producing client or harness. It
does not define how to search, retrieve, rank, or analyze prior conversations; use `chat-history`
for that.

## Evidence boundary

Checked against the AgentsView `v0.40.1` registry and parser source at commit
`9ef48912bdbe844c1e60cd97c07eb0d5cca0f988`, its pinned producer/source inventory in
`docs/internal/session-format-sources.md`, and names-only schema probes of current local Claude Code,
Codex, and Kimi artifacts. The source inventory distinguishes producer source, first-party
documentation, and observed/no-public-source formats.

`D:\_projects\llm-archiver\tools\*.yaml` is a stale downstream normalization catalog. It can be a
lead for older artifact locations, but it is not authority for current raw formats or for declaring
that a raw field is absent. In particular, its Codex tool-call declaration, Kilo legacy-task path,
and Kimi `context.jsonl` preference do not match the current AgentsView parser registry.

“Unknown” below means the consulted raw-format evidence does not establish the field. It does not
mean that the harness, provider, or model lacked the information at runtime.

## Raw stores and fields

| Client/harness | Current raw store and format | Raw fields established by current evidence |
|---|---|---|
| Claude Code | Project-scoped JSONL under `${CLAUDE_CONFIG_DIR:-~/.claude}/projects/**`, including subagent JSONL. | Top-level records include `sessionId`, `uuid`/`parentUuid`, `timestamp`, `cwd`, `gitBranch`, `entrypoint`, `version`, `sessionKind`, and per-turn `promptSource` when present. Assistant `message` objects carry `id`, `model`, structured content blocks (`text`, `thinking`, `tool_use`, `tool_result`), and `usage` with input, output, cache-creation, and cache-read fields. A provider field was not established. |
| Codex | Rollout JSONL under `~/.codex/sessions/<year>/<month>/<day>/rollout-*.jsonl` and `~/.codex/archived_sessions/`; a separate session-index JSONL supplies discovery metadata. Sibling `~/.codex/history.jsonl` is an append-oriented prompt/activity hint, not the full transcript. | `session_meta.payload` includes session identity, `cwd`, Git metadata, `originator`, `cli_version`, and `model_provider`. `turn_context.payload` includes `model`, `effort`, permission/sandbox state, and turn identity. `response_item.payload` includes messages, reasoning, `function_call`/`function_call_output`, and `custom_tool_call`/`custom_tool_call_output` with structured arguments/results. `event_msg` includes task/subagent events and `token_count`; raw last/total usage includes input, cached input, cache-write input, output, reasoning output, and totals. |
| GitHub Copilot CLI | Flat session JSONL or `~/.copilot/session-state/<session>/events.jsonl`; `~/.copilot/session-store.db` is a derived history index. | Event envelopes carry IDs, parent IDs, type, timestamp, and data; the `session.start` event carries the native session ID. Tool start/complete records share `data.toolCallId` and have independent timestamps. Shutdown metrics can persist input, output, cache-read, cache-write, and reasoning tokens. Current consulted evidence does not establish a reliable raw model/provider field. |
| Gemini CLI | `~/.gemini/tmp/<project>/chats/session-*.jsonl`; older `session-*.json` recordings remain accepted. | Records carry roles/content, timestamps, model IDs, tool calls/results, and usage derived from Gemini API metadata: input, output, cached, thoughts, tool, and total tokens. Provider identity beyond the Gemini/Google harness context is not separately established here. |
| Cursor | Legacy text and newer JSONL below `~/.cursor/projects/<project>/agent-transcripts/`; Cursor also maintains a separate SQLite history index. | Roles/attribution can be reconstructed, but current evidence establishes no reliable per-message token, cache, reasoning, cost, provider, or model fields. Those fields are unknown, not negative claims about the runtime. |
| Antigravity IDE | Per-session SQLite databases, optionally with trajectory JSON sidecars, under the `.gemini/antigravity` family. | Reverse-engineered generation metadata or sidecars can provide model plus uncached input, output (including thinking), and cache-read usage. Exact schema/provider identity is not publicly documented; decode failures remain possible. |
| Antigravity CLI | Newer per-session SQLite databases or older encrypted protobuf files under `.gemini/antigravity-cli`, with trajectory/history/brain sidecars when present. | Sidecars can carry model, input, output, thinking-output, and cache-read data. Exact encrypted/protobuf schema and provider field availability remain unknown. |
| OpenCode | Current `~/.local/share/opencode/opencode.db` SQLite plus legacy `storage/session`, `storage/message`, and `storage/part` JSON trees. | Session rows carry directory/project/title/time metadata. Assistant message data persists `modelID`, `providerID`, input/output/cache-read/cache-write usage, and other message metadata. Part data represents text, reasoning, and structured tools including call ID, input, status, output, and tool metadata such as bash exit/timeout state. |
| Kilo Code (current) | `~/.local/share/kilo/kilo.db`, shared by the current OpenCode-based extension and Kilo CLI; legacy OpenCode-compatible JSON trees may also exist below the same root. | Uses the OpenCode session/message/part family: model identity, input/output/cache-read/cache-write usage, structured tool state, session/project metadata, and native session IDs. The current registry uses `kilo.db`, not editor task folders. |
| Kilo Code (legacy) | VS Code-family `globalStorage/kilocode.kilo-code/tasks/<uuid>/` containing `task_metadata.json`, `api_conversation_history.json`, and `ui_messages.json`. | Historical pre-OpenCode format. `ui_messages.json` can carry structured tool/reasoning records plus input, output, cache-read, cache-write, explicit USD cost, and `usageMissing`. New sessions moved to `kilo.db`; do not treat this legacy location as current Kilo storage. |
| Kimi CLI / Kimi Code | `~/.kimi/sessions/<workspace>/<session>/wire.jsonl` for legacy layout and `~/.kimi-code/sessions/<workspace>/<session>/agents/<agent>/wire.jsonl` for current/subagent layout. | Legacy nested event types include `TurnBegin`, `ContentPart`, `ToolCall`, `ToolResult`, `StatusUpdate`, and `TurnEnd`. Current top-level types include `config.update`, `turn.prompt`/`turn.steer`, `context.append_loop_event`, `llm.request`, and `usage.record`; loop events carry content, structured tool calls/results, `step.end` model/finish/usage data, and timestamps. Names-only inspection of current `wire.jsonl` verified top-level `llm.request.provider`, `llm.request.model`, and `llm.request.modelAlias`; `config.update.modelAlias` and `usage.record.model` were also present. Current usage can include input/output/cache fields; older wire logs may omit model and expose only aggregate output. AgentsView `v0.40.1` reads `wire.jsonl`. The downstream llm-archiver catalog's `context.jsonl` preference is not current raw-format authority. |
| Qwen Code | `~/.qwen/projects/<encoded-project>/chats/<session>.jsonl`. | Gemini-derived records include roles, content/thinking parts, structured function calls/responses, top-level `model`, and `usageMetadata` fields such as prompt, candidates/output, cached-content, thoughts, and total tokens. Session ID is the JSONL filename stem. |
| Goose | No Goose entry exists in the AgentsView `v0.40.1` registry or source inventory consulted here. | Current raw location, format, provider/model fields, and usage fields are unknown in this reference. Old LevelDB/`sessions.db` paths from llm-archiver remain stale downstream leads only. |

## Dated OpenCode schema observation

The 2026-06-08 reverse-engineering note records `session` (`ses_*`) to `message` (`msg_*`) to `part`
(`prt_*`) relationships, plus a separate `session_message` metadata stream for `agent-switched` and
`model-switched` events. Its `data` columns were JSON text and timestamps were epoch milliseconds.
Observed part types included `step-start`, `reasoning`, `text`, `tool`, and `step-finish`; tool data
included call ID and state status/input/output.

The same observation found user prompt text in `message.data.summary`, multiple assistant message
rows for one user turn, session-to-session subagent linkage in `session.parent_id`, and intra-session
threading in `message.data.parentID`. The database was about 664 MB at that date. These are useful
schema facts from `D:\_projects\agent-control-plane\capture\scratch\opencode-session-reconstruction.md`,
not guarantees about later OpenCode releases; the current AgentsView parser remains the format
baseline above.

## Interpretation notes

- Claude Web exports and Claude Code JSONL are different producers and formats.
- OpenRouter owns no transcript path. Look under the consuming harness; provider/model fields are
  usable only when that harness records them.
- A normalized parser can omit raw data. For example, AgentsView intentionally ignores some raw
  Codex usage categories, while the raw `token_count` record still contains them.
- Current and legacy stores may coexist. Identify the producing generation before interpreting
  field availability.
