# Choosing between KCap and AgentsView

Distilled from the 2026-08-15 capability research (KCAP v0.11.20 vs AgentsView v0.40.1). Full
analysis: `docs/skill-corpus-analysis/kcap-vs-agentsview-research.md` in the `frozenSkillz` repo.
That path only resolves when the current working tree is that checkout; when this skill runs
against a different project, treat this file as the complete reference instead of following the
link.

## Start with AgentsView when

- The search spans harnesses or machines, or the harness is unknown. AgentsView natively indexes
  12 agent types; KCap records Claude Code only natively (others require manual `kcap import`).
- The task needs full transcript content — every message, thinking text, tool input/output,
  token usage — stored locally and queryable with FTS5/semantic/hybrid search or SQL.
- The task needs telemetry: health grades, outcome classification, tool-failure/edit-churn
  signals, usage/cost accounting, or secret-findings data. All computed locally at zero LLM cost.
- Data must stay local. AgentsView's own store is SQLite; KCap sessions live on the Kurrent
  server regardless of configuration. This only holds for AgentsView when its optional Postgres
  sync is not configured or is disabled — when sync is active, treat it as data ownership
  (you control the remote), not strict locality.

## Start with KCap when

- The question is PR- or file-specific ("why was this code written this way?"): KCap's review MCP
  family (`get_pr_summary`, `list_pr_files`, `get_file_context`, `search_context`) links sessions
  to PRs directly. AgentsView has no PR linkage.
- The task is repo-scoped and the repo is Claude Code work: natural-language `search_sessions`
  plus `list_turns`/`get_turn` is faster than composing AgentsView queries.

## Never route here first

- **AgentsView recall** (`query_recall`, `recall query`): the recall infrastructure exists (20
  tables, evidence-linked) but is EMPTY — 0 entries. Use recall only as a lead check, never as a
  primary surface, until extraction has been run.
- **KCap analytics MCP family**: plan-gated on the current plan (HTTP 403 `analytics_not_in_plan`).
  Probe once per environment; on 403, fall back to AgentsView usage/health surfaces.
- **KCap workitems MCP family**: plan-gated on the current plan (HTTP 403
  `work_items_not_in_plan`). This is orchestration, not history retrieval, so it is out of scope
  for `chat-history` regardless (see below) — but note AgentsView has no fallback for it either;
  AgentsView does not model work items. On 403, report the capability as unavailable rather than
  substituting AgentsView usage/health telemetry.
- **KCap for non-Claude sessions** unless an import is known to have covered them.

## Unique-but-out-of-scope KCap surfaces

Agent Flows, Work Items, and automatic memory injection are KCap exclusives, but they are not
history-retrieval surfaces. Do not route a chat-history task through them; note them only when
the user's goal is workflow orchestration or persistent memory rather than retrieval.
