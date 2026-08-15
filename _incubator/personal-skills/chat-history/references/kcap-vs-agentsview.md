# KCAP vs AgentsView — capability briefing

Last updated: 2026-08-15. Based on KCAP v0.11.20 (`@kurrent/kcap`) and AgentsView v0.40.1.

Both tools record AI-agent sessions and make them searchable. They overlap on session recording and
retrieval but diverge sharply on what else they do with the data. This document is the comparative
reference; operational procedures stay in `kurrent-capacitor.md` and `agentsview.md`.

## Data footprint (as observed)

| Metric | KCAP | AgentsView |
|---|---|---|
| Agents supported | Claude Code only | 12 (Claude, Codex, OpenCode, Cursor, Kimi, Antigravity, Kilo, Cowork, VS Code Copilot, Gemini, Amp, Copilot) |
| Sessions recorded | server-side, count unknown locally | 9,356 local + Postgres archive |
| Messages stored | server-side summaries and turn access | 538,636 with full content, thinking text, token usage |
| Tool calls tracked | not exposed per-call | 531,644 with category, input/output, file path, skill, subagent link |
| Secret findings | none | 216 across 9 rule types |
| Usage events | plan-gated analytics | 13,908 with per-model token breakdowns |
| Full-text search | natural-language via MCP | FTS5 on messages, recall entries, and recall evidence |
| Storage location | Kurrent server (cloud) | Local SQLite + optional Postgres sync |

## Integration architecture

### KCAP

Hooks-based Claude Code plugin. Registers 8 hook events (SessionStart ×2, SessionEnd, SubagentStart,
SubagentStop, Notification, Stop, PermissionRequest, UserPromptSubmit) and 6 MCP server families
(sessions, review, memory, flows, workitems, analytics). The `kcap.exe` binary handles both hooks
and MCP stdio transport. Data lives on the Kurrent server; the local binary is a client.

Auto-triggered skills use YAML frontmatter `description` fields in SKILL.md for intent matching.
Ten skills ship: recap, agent-flows, review-flows, validate-plan, work-items, guided-tour, errors,
disable, hide, and an implicit memory skill. Most are rarely invoked because the MCP tools serve the
same purpose directly.

### AgentsView

Daemon-based local service. Parses transcript files from Claude, Codex, Cursor, Copilot, and other
agents into a normalized SQLite schema (65+ tables). A background daemon at `127.0.0.1:8080`
exposes an HTTP API (v2). Postgres sync pushes to a remote archive. An MCP surface
(`agentsview mcp`) exposes `search_sessions`, `list_sessions`, `get_session_overview`,
`get_messages`, `search_content`, `get_usage_summary`, and `query_recall` for in-session use. A CLI
provides the same plus write and maintenance surfaces.

## Capability comparison

### Session recording and retrieval

Both record sessions. KCAP records via hooks and stores on its server, exposing sessions through MCP
tools (`search_sessions`, `get_session_summary`, `list_turns`, `get_turn`,
`get_session_transcript`). AgentsView parses local transcript files into SQLite, storing every
message with full content, thinking text, and token counts. AgentsView stores locally; KCAP stores
remotely.

AgentsView's message-level storage means you have the complete transcript, not a server-side
summary. KCAP's natural-language search is convenient but AgentsView's FTS5 and semantic/hybrid
search cover the same retrieval need, plus you can run arbitrary SQL against the normalized schema.

**Edge: AgentsView** for data completeness and local ownership. **Edge: KCAP** for natural-language
convenience out of the box.

### Multi-agent support

AgentsView tracks 12 agent types natively: Claude (2,383 sessions), Codex (3,028), OpenCode
(1,412), Cursor (500), Kimi (462), Antigravity (429), Kilo (424), Cowork (332), VS Code Copilot
(215), Gemini (163), Amp (6), Copilot (2). KCAP records Claude Code only, though it can import
sessions from Codex, Cursor, Copilot, Gemini, Kiro, Pi, OpenCode, and Antigravity via `kcap import`.

The difference: AgentsView normalizes all agents into one schema automatically. KCAP imports are a
manual step and the imported sessions live on the Kurrent server.

**Edge: AgentsView**, clearly.

### Quality and health signals

AgentsView computes health grades (A/B/C/D/F) and outcome classification (completed / abandoned /
errored) from transcript signals without any LLM cost. Tracked signals include: tool failure counts,
tool retry counts, edit churn, consecutive failure maximums, short prompt counts, missing success
criteria, missing verification, duplicate prompts, no-code-context counts, runaway tool loop counts,
context pressure maximum, compaction counts, and mid-task compaction counts.

KCAP's quality analysis is `kcap eval`, an LLM-as-judge workflow that runs 13 fixed questions across
4 categories (safety, plan adherence, quality, efficiency). It costs LLM compute per run and
persists results.

Both have limits. AgentsView's penalty model is heuristic — a high score does not prove the task
succeeded. KCAP's evals are LLM opinions, not deterministic. But AgentsView's signals are free to
compute and always present; KCAP's evals are on-demand and paid.

**Edge: AgentsView** for always-on quality signals at zero marginal cost. KCAP evals are deeper
but narrower and costlier.

### Secret detection

AgentsView scans transcripts for leaked credentials: GitHub PATs, OpenAI keys, Google API keys,
Hugging Face tokens, Anthropic keys, AWS access keys, private key blocks, Slack tokens, Stripe
secrets. 216 findings observed across 9 rule types with confidence levels, exact locations, and
redacted matches.

KCAP has no secret detection.

**Edge: AgentsView**, exclusively.

### Cost and usage tracking

AgentsView stores per-message usage events with input/output/cache creation/cache read/reasoning
token breakdowns. A `model_pricing` table maps model patterns to microdollar costs. A separate
`cursor_usage_events` table tracks Cursor-specific billing. The `usage` and `usage daily` CLI
commands report across sessions.

KCAP's analytics MCP family (`get_analytics_schema`, `query_analytics`) could provide this, but it
is plan-gated (returns HTTP 403 `analytics_not_in_plan` on the current plan).

**Edge: AgentsView**, both in data and accessibility.

### Memory and recall

KCAP's memory system (`kcap-memory` MCP) stores durable learnings scoped to user, team, org, or
repo. Memories are saved, searched, updated, archived, and rescoped through MCP tools. The
SessionStart hook injects relevant memories automatically — this is the key UX advantage.

AgentsView has a full recall infrastructure (20 tables) covering: entries with
type/scope/status/review state/confidence/uncertainty, evidence linking to transcript spans with
ordinal precision, FTS5 and embedding-backed search, extraction generations with model/segmenter
versioning, provenance chains, supersession tracking, and transferability flags. The schema is
more sophisticated than KCAP's flat memory model. However, **it is currently empty** — 0 recall
entries, 0 evidence records, 0 extract generations. The infrastructure exists but is not wired up.

**Edge: KCAP** today, because its memory actually has content and injects at session start.
**Architecturally: AgentsView** is more capable once activated.

### Insights

AgentsView has an `insights` table for LLM-generated analysis with template versioning, structured
JSON, provenance, and caching. Currently empty (0 rows). KCAP does not have a direct equivalent
outside of its eval system.

**Edge: neither** — both are absent in practice.

### PR and review context

KCAP's review MCP family (`get_pr_summary`, `list_pr_files`, `list_sessions`, `get_file_context`,
`search_context`, `get_transcript`) links sessions to PRs and provides implementation-reasoning
retrieval. This is purpose-built for "why was this code written this way?" questions.

AgentsView can answer the same question by searching messages and tool calls, but doesn't have
dedicated PR-linking. The `session_project_identity_snapshots` table tracks git remotes, branches,
and worktree relationships, which helps correlate sessions to repos, but not to specific PRs.

**Edge: KCAP** for PR-specific context retrieval.

### Agent Flows

KCAP's flows system (`kcap-flows` MCP) spawns independent hosted agents on a daemon for iterative
multi-participant workflows. Two flavors: generic agent flows (dynamic YAML definitions, arbitrary
participants, guardrail errors, role-surface safety gate) and review flows (code-review and
spec-review templates with round-based sign-off). Tools: `start_flow`, `send_to_participant`,
`get_flow_status`, `close_flow`, plus review-specific aliases.

AgentsView has nothing like this. It is a data store, not an agent orchestration platform.

**Edge: KCAP**, exclusively. This is a genuinely unique capability.

### Work Items

KCAP's workitems MCP family tracks SDLC items with parent→parts breakdowns and blocks/blocked-by
dependencies. Declared structure shows up in the Kurrent Capacitor web UI's "Blockers &
dependencies" view. Tools: `declare_work_item`, `declare_work_breakdown`, `declare_work_relation`,
`get_session_work_items`, `get_work_item_topology`, plus retract operations.

This is plan-gated (HTTP 403 `work_items_not_in_plan` on the current plan), but the tools exist and
work on supporting plans.

AgentsView does not model work items.

**Edge: KCAP**, exclusively (when plan supports it).

### Skills and auto-triggers

KCAP ships 10 skills with auto-trigger via YAML frontmatter intent matching. These surface
contextual guidance (recap, error diagnosis, plan validation, guided tour, flow management, work
items, visibility control).

AgentsView does not have a skills concept. It has a `skills` CLI subcommand, but this manages MCP
skill installation, not auto-triggered agent guidance.

**Edge: KCAP** for in-session guidance.

### Project identity and multi-machine sync

AgentsView's `session_project_identity_snapshots` track git remote, worktree name, worktree root
path, worktree relationship, checkout state, branch, remote resolution, and normalized remotes.
`worktree_project_mappings` correlate project identity across worktrees. Postgres sync pushes
sessions to a remote archive and the artifact pipeline handles checkpoint distribution.

KCAP knows the current repo context but doesn't model the identity resolution problem across
machines and worktrees.

**Edge: AgentsView** for multi-machine and worktree correlation.

### Data sovereignty

AgentsView stores everything locally in SQLite. Postgres sync is optional and goes to your own
server. You own the data, can query it with standard tools, and can export sessions as raw JSONL.

KCAP stores data on the Kurrent server. The local binary is a client. You depend on their server
availability, their data retention, and their access controls.

**Edge: AgentsView** for data ownership and portability.

## Plan-gated features in KCAP

Two of KCAP's six MCP families require a Team or Enterprise plan:

- **Work Items** → HTTP 403 `work_items_not_in_plan`
- **Analytics** → HTTP 403 `analytics_not_in_plan`

The other four (sessions, review, memory, flows) work on the current plan. Evals run via `kcap eval`
CLI, not MCP, and are not plan-gated.

## Could AgentsView replicate KCAP's in-session search?

Yes. AgentsView already has:

- 538K messages with FTS5 indexing.
- An MCP surface (`agentsview mcp`) with `search_sessions`, `get_messages`, `search_content`,
  `query_recall`, and other tools.
- Semantic and hybrid search modes when embeddings are active.

A hook or subagent that queries AgentsView's MCP or SQLite directly would provide in-session
transcript search across all 12 agent types, not just Claude Code. The `chat-history` skill already
routes to AgentsView for broad cross-harness retrieval.

What AgentsView cannot replicate:
- **Agent Flows** — spawning independent hosted agent instances for iterative workflows.
- **Work Items** — SDLC item tracking with breakdown and dependency declaration.
- **Automatic memory injection** — KCAP's SessionStart hook that surfaces saved learnings. This
  could be built with a hook that queries AgentsView's recall system, but the recall system is
  currently empty and would need extraction to be activated first.

## Summary judgment

KCAP's unique value is Agent Flows, Work Items, and the convenience of automatic memory injection.
For session recording, retrieval, quality analysis, cost tracking, secret detection, multi-agent
coverage, and data ownership, AgentsView is equal or ahead. The recall infrastructure in AgentsView
is architecturally more sophisticated than KCAP's memory system but is not yet activated.

For the chat-history skill specifically: use KCAP for PR-linked context and repository-scoped
session search. Use AgentsView for everything else — it has 12× the agent coverage, local data
sovereignty, full-text search across all messages, and built-in quality signals at zero LLM cost.
