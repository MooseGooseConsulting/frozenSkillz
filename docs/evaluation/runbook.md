# Evaluation Runbook

How to run every recurring operation. Everything here is read-only against the
corpora and non-acting against skills unless a human lands a change.

Prerequisites:

- `agent-control-plane` checkout (the skill-analysis worktree carries the eval tree):
  `D:\_projects\agent-control-plane-skill-analysis`
- Python 3.13+; `PyYAML` optional (a stdlib fallback covers the registry)
- Ollama running locally with the configured extraction model for extraction runs
  (`ollama pull llama3.2:3b`; override with `EVAL_EXTRACTOR_MODEL`)
- For the durable store: `pip install "psycopg[binary]"` and `EVAL_STORE_DSN` pointing
  at the homelab Postgres (phase-gated — see below)

## 1. Run extraction manually

```powershell
cd D:\_projects\agent-control-plane-skill-analysis
python -m eval.extractors.driver --extractor forensic-signals --batch 25 --store jsonl:eval/out
```

The driver fails fast (~1s) if Ollama is down, and aborts before any work if the store
is unreachable. Per-session failures are counted, never fatal. Watermarks live in the
store, so re-runs are cheap and skipped days catch up.

To run against homelab Postgres once the phase gate clears:

```powershell
$env:EVAL_STORE_DSN = "postgresql://user@agentsview-db.moosegoose.xyz/dbname"
python -m eval.extractors.driver --all --store pg
```

Schema DDL lives in `eval/extractors/store.py` (`DDL`) and the spec in
`eval/library/extractors/forensic-signals/v1.md`.

### Phase gate (before any scheduled run)

1. Schema exists on the homelab (or the jsonl store is the deliberate target).
2. One manual bounded batch has run end-to-end.
3. A human has spot-checked extracted signals against the raw sessions
   (KCap `get_turn` / AgentsView for the same session ids).

Only after all three: register the timer (`eval/automation/Register-EvalTasks.ps1`).

## 2. Run a per-project review

1. Kick off (or receive the scheduled kickoff): the batch lists candidate episodes
   with the signal that selected each and the recommended reader prompt.
2. Dispatch one bounded episode per reader — `repo-forensic-miner` for friction,
   `doc-use-investigator` for documentation questions, `deployment-debrief` for a
   single skill's deployment.
3. Synthesize with `corpus-synthesis` (memos only, never raw dumps).
4. Land the smallest supported change in frozenSkillz — or record "no change yet" in
   the tracker.

## 3. Run a fleet review

Same shape, fleet scale: aggregate the signal store across repos (counts with
denominators, harness concentration), retrieve 2–5 representative episodes per top
cluster, close-read with `corpus-behavioral-miner`, attribute global vs repo-local.

## 4. Run a comparison

```powershell
python -m eval.comparison.compare --stores eval/out --out eval/out/comparison
```

Read `comparison.md` for facet counts, `comparison.jsonl` for per-session detail.
Divergence on a consequential question → collect a discriminating case; do not
average.

## 5. Add or version a variant

1. New variant: a directory under the right `eval/library/` subtree with `v1.md`.
   New version of an existing variant: `v2.md` beside it, never an overwrite.
2. One-line rationale in `eval/library/CALIBRATION.md`.
3. Calibrate against `golden-set/` before the catalog adopts the version.
4. Update `eval/library/CATALOG.md` (status, calibration).

## 6. Register the timers (deliberate, reviewed)

```powershell
# Review eval/automation/*.md and Register-EvalTasks.ps1 first. Then, elevated:
.\eval\automation\Register-EvalTasks.ps1                    # extraction only
.\eval\automation\Register-EvalTasks.ps1 -IncludeKickoff    # + Codex review kickoff
```

The Cursor Automation equivalent (review kickoff on a schedule) is created through
the Automations editor; the draft lives in `eval/automation/README.md`.

## 7. Route a skill to its repos

```powershell
python scripts/sync_frozen_skills.py --repo Owner/repo --check  --destination <project>/.agents/skills
python scripts/sync_frozen_skills.py --repo Owner/repo --apply  --destination <project>/.agents/skills
```

Then add the thin route in the project's AGENTS.md (e.g. "PDM fleet operations →
invoke the `pdm-cli-operations` skill") and merge `.frozen-skills-mcp.json` into the
project's client MCP config per its own convention.
