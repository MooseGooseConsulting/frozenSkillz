# Kurrent Capacitor route

Use KCap when the user supplies a repository, project, PR, file, session-chain, or implementation-
history anchor, or explicitly asks for KCap. Prefer the `kcap-sessions` MCP tools when available.
Ambient current-repository context may scope a search, but a working directory alone does not make
KCap the first provider. For generic transcript discovery, start with the broadest provider or
harness index suggested by the request, then use KCap to drill into identified candidates.

The first KCap search is a probe, not a verdict. An empty, noisy, or weak result means the query
failed; it does not establish that the conversation is missing from KCap. Before switching
providers, run a bounded retry set with materially different shapes:

1. the user's natural-language question scoped to the current repository or project;
2. stable exact anchors such as a session fragment, PR, file, command, quotation, or distinctive
   phrase;
3. a relaxed scope over date, machine, agent, child, continuation, or session chain; and
4. when the task is a swarm or comparison, the parent/session population plus child or continuation
   queries.

Record each query and its result in the localization artifact. If the user says the source should
be in KCap, treat that as a retrieval warning: keep KCap active through the retry set and check
capability/coverage before reporting absence. Only then widen to AgentsView or another provider.

## Capability gate

Check the live surface before depending on optional features:

```powershell
kcap status --no-update-check
kcap whoami --no-update-check
kcap projects
```

Projects require a supporting plan. Analytics require a server that implements the analytics
endpoints. Treat a 403 or unsupported-server response as an unavailable branch and continue through
session search or AgentsView.

## Session discovery and drill-down

Use the MCP sequence:

1. `search_sessions` with a natural-language question; default to the current repo or pass
   `repo: "all"` only when cross-repo discovery is intended.
2. If the result is empty or weak, repeat `search_sessions` with the exact-anchor, relaxed-scope,
   and swarm/comparison queries above before treating the route as incomplete.
3. `get_session_summary` to orient on a candidate.
4. `list_turns` to map the session semantically without loading its entire transcript.
5. `get_turn` for one complete turn, or `get_session_transcript` around the returned event index.
6. Preserve `agent_id` when the hit belongs to a subagent stream.

CLI fallback:

```powershell
kcap recap --repo
kcap recap <session-id>
kcap recap --per-turn <session-id>
kcap recap --get-turn <n> <session-id>
kcap recap --chain <session-id>
kcap recap --full <session-id>
```

Use `--full` only after a summary or turn map shows that the whole transcript is required.

## PR and file reasoning

Use the read-only review MCP routes to recover implementation context:

- `get_pr_summary`
- `list_pr_files`
- `list_sessions`
- `get_file_context`
- `search_context`
- `get_transcript`

Read the current diff and repository authority separately. Transcript reasoning explains what the
agent intended; it does not prove the implementation is correct.

## Import and coverage

KCap can import Claude, Codex, Cursor, Copilot, Gemini, Kiro, Pi, OpenCode, and Antigravity
sessions. Scope imports deliberately by repo, organization, working directory, date, or session.
Do not run broad imports merely to answer a lookup when the server already has the session.

## Scores, summaries, and evaluations

- Treat session-search scores as candidate ordering only.
- Treat generated summaries and per-turn prose as navigation; open the relevant turn for
  consequential claims.
- `kcap eval` is an LLM-as-judge workflow, not deterministic transcript retrieval. It can take
  minutes and persist results. Do not invoke it during ordinary history lookup unless the user asks
  for evaluation.
- Use governed analytics only when available. State the queried field definitions and do not turn
aggregate telemetry into a claim about conversation quality.
