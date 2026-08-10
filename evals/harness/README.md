# Controlled `chat-history` replay

This is an **operator-run** comparison, not a test suite. `npm test` only validates the YAML; it
does not contact a model. Nothing in this repository schedules `npm run controlled-eval`.

Before an intentional run, install the pinned package graph with `npm ci` in this directory. Then
create two disposable workspaces outside this repository with identical corpus fixtures and tool
access:

- `current-skill` contains `.agents/skills/chat-history/` with the exact skill revision under test.
- `no-skill-baseline` contains no `chat-history` skill anywhere in its project hierarchy.

Use an isolated `HOME` that contains no `~/.agents/skills/chat-history`, and a dedicated
`CODEX_HOME` that has the login and the exact
`agents/chat-history-researcher.toml` profile needed for the run but no `skills/chat-history` copy.
Both conditions use the same homes; the only intended difference is the project-local skill copy.
Set:

```powershell
$env:CHAT_HISTORY_EVAL_ROOT = 'D:\temp\chat-history-eval'
$env:CHAT_HISTORY_EVAL_CURRENT_SKILL_WORKSPACE = 'D:\temp\chat-history-eval\current-skill'
$env:CHAT_HISTORY_EVAL_BASELINE_WORKSPACE = 'D:\temp\chat-history-eval\no-skill-baseline'
$env:CHAT_HISTORY_EVAL_CODEX_HOME = 'D:\temp\chat-history-eval\codex-home'
$env:CHAT_HISTORY_EVAL_HOME = 'D:\temp\chat-history-eval\home'
npm run controlled-eval
```

The command verifies that each directory exists, writes `results.json` outside the repository, and
runs each scenario three times under each condition with `--no-cache`. It records a content hash
for the installed skill and a hash for the required custom-agent profile in `run-manifest.json`
before any trials begin.

This run makes **12 top-level agent trials**. The six current-skill trials normally add two staged
worker turns each; Scenario B's three baseline trials explicitly request a worker. Plan for at
least **27 agent turns before retries**. Actual billing is provider-dependent and is not measured
by this repository. The configuration has deterministic outcome/provenance gates only; review the
trajectories and run results qualitatively before drawing conclusions.

The source tree can reconstruct older `chat-history` text, but not the historical corpus/index
state and available history-service runtime. A prior-version comparison is therefore unavailable
for this harness until an operator can supply an exact runtime snapshot; do not represent this
current-versus-no-skill comparison as a prior-version result.
