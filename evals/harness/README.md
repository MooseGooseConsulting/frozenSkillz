# Controlled `chat-history` replay

This is an **operator-run** comparison, not a test suite. `npm test` only validates the YAML; it
does not contact a model. Nothing in this repository schedules `npm run controlled-eval`.

Before an intentional run, create two disposable workspaces outside this repository with identical
corpus fixtures and tool access:

- `current-skill` contains `.agents/skills/chat-history/` with the exact skill revision under test.
- `no-skill-baseline` contains no `chat-history` skill anywhere in its project hierarchy.

Use a dedicated `CODEX_HOME` that has the login needed for the run but no personal skills. Set:

```powershell
$env:CHAT_HISTORY_EVAL_ROOT = 'D:\temp\chat-history-eval'
$env:CHAT_HISTORY_EVAL_CURRENT_SKILL_WORKSPACE = 'D:\temp\chat-history-eval\current-skill'
$env:CHAT_HISTORY_EVAL_BASELINE_WORKSPACE = 'D:\temp\chat-history-eval\no-skill-baseline'
$env:CHAT_HISTORY_EVAL_CODEX_HOME = 'D:\temp\chat-history-eval\codex-home'
npm run controlled-eval
```

The command verifies that each directory exists, writes `results.json` outside the repository, and
runs each scenario three times under each condition with `--no-cache`. It makes twelve intentional
agent calls. The configuration has deterministic outcome/provenance gates only; review the
trajectories and run results qualitatively before drawing conclusions.
