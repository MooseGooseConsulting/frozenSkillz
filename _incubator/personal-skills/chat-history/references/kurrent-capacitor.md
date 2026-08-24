# Kurrent Capacitor surface

Kurrent Capacitor can provide session search, turn-level drill-down, session chains, and repository,
PR, or file context when the server has indexed those relationships and the feature is available.
Use it when those stored fields answer the request. A repository-shaped working directory can scope a
query, but it does not by itself prove KCap coverage or select KCap over another suitable source.

## Capability gate

Check the live surface before depending on optional features:

```powershell
kcap status --no-update-check
kcap whoami --no-update-check
kcap projects
```

Projects require a supporting plan. Analytics require a server that implements the analytics
endpoints. Treat a 403 or unsupported-server response as an unavailable branch and continue through
an available surface that records the requested field.

## Session discovery and drill-down

The `kcap-sessions` MCP surface can expose `search_sessions`, `get_session_summary`, `list_turns`,
`get_turn`, and bounded transcript retrieval. Use the subset needed for the question. Preserve
`agent_id` when a hit belongs to a subagent stream, and distinguish a child execution record from a
root conversation.

CLI fallback:

```powershell
kcap recap --repo
kcap recap <session-id>
kcap recap --per-turn <session-id>
kcap recap --get-turn <n> <session-id>
kcap recap --chain <session-id>
kcap recap --full <session-id>
```

Use `--full` only when the question actually requires the whole transcript.

## PR and file reasoning

Use the read-only review MCP routes to recover implementation context:

- `get_pr_summary`
- `list_pr_files`
- `list_sessions`
- `get_file_context`
- `search_context`
- `get_transcript`

Read the current diff and repository authority separately. Transcript reasoning explains what the
agent intended or observed; it does not prove the implementation is correct or current.

## Import and coverage

KCap supports native capture and imports, but coverage differs by harness, installation, server, and
retention window. Check the live inventory before a cross-harness claim. Import is a write operation;
do not run it as an ordinary lookup unless repairing a demonstrated gap is in scope and authorized.

## Scores, summaries, and evaluations

- Treat session-search scores as candidate ordering only.
- Treat generated summaries and per-turn prose as navigation; open the relevant turn for
  consequential claims.
- `kcap eval` is an LLM-as-judge workflow, not deterministic transcript retrieval. It can take
  minutes and persist results. Do not invoke it during ordinary history lookup unless the user asks
  for evaluation.
- Use governed analytics only when available. State the queried field definitions and do not turn
  aggregate telemetry into a claim about conversation quality.
