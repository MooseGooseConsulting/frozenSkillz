# Eval Case: chat-history stress test (2026-08-03)

Skill under test: `chat-history` (personal, `~/.agents/skills/chat-history/`, landed in PR #82 with
the `chat_history_researcher` worker agent).

Method: `docs/workflows/skill-evaluation.md`. Scenarios were derived from real history by a live
`chat-history` run on 2026-08-03 (LOCALIZE + ANALYZE); evidence artifacts at
`%TEMP%/chat-history-eval-2026-08-03/localize-agent-1.md` and `analyze-agent-1.md` (local paths,
not committed). Six authentic invocation patterns were found; the two below were selected because
both have verified ground truth from the original episodes.

Scope: this case is the controlled-replay half of the evaluation. It does not, by itself, establish
activation precision, missed opportunities, real-world outcome rate, or owner acceptance. Those
come from the full-history census and stratified transcript review required by the workflow.

## Scenario A — provenance reconstruction

- Verbatim trigger (source session `codex:019f1bbb-a218-7030-81ad-8486fbe74dc2`, 2026-07-01):
  "Can you help me track down which of my products or projects eventually started out as something
  called Scope Atlas or something like that? … I don't remember what it ended up transforming into."
- Exercises: vague semantic localization, noisy keywords ("planner", "atlas"), cross-harness search
  (Codex rollouts + Pieces), LOCALIZE → ANALYZE staging on a large population.
- Ground truth: Scope Atlas → Semantic Context Planner / `Coldaine/Semantic-Planner`; adjacent
  decoys (state-cartographer, Plan Graph Scheduler, GitAtlas) must be excluded.
- Note: the source session contains a literal observed invocation of this skill (ords 343–345);
  the original run is the de-facto baseline for comparison.

## Scenario B — lost-context complaint → directed retrieval

- Verbatim trigger (source session `98e65f4c-c84d-4629-94ac-e1808aa97d68`, Claude Code,
  2026-06-08): "You have no memory of creating these files… dispatch a subagent to go ahead and
  take a look and find if you can this conversation in the previous Claude code history… Figure out
  what the hell was going on."
- Exercises: post-compaction recovery, directed subagent retrieval, source-trust handling — in the
  original episode the user vetoed the llm-archiver DB and mandated raw `.jsonl` transcripts
  (trust hierarchy: raw transcripts > summaries > archive DBs).
- Ground truth: the graph-ingestion files (`graphiti_f4`, `INGESTION_GOVERNANCE`,
  `INGESTION_RATIONALE`) were created in that very session; the compaction summary's claim of "the
  other session" was wrong.

## Rubric

Scored per trial; **at least 3 trials per scenario** per scoring event
(`docs/workflows/skill-evaluation.md`). A trial fails if any hard gate fails.

### Hard gates (fail one = trial fails)

| # | Gate |
|---|---|
| G1 | Final answer matches known ground truth (outcome check, not the worker's claim of success) |
| G2 | Answer exposes provenance: which sessions/turns the evidence came from |

### Behavioral assertions (pass / partial / fail, judged on the observed trajectory)

| # | Assertion (from the skill's own contract) |
|---|---|
| 1 | LOCALIZE stage completed before any ANALYZE dispatch |
| 2 | Temporary run directory created outside the repo; workers given exact unique output paths |
| 3 | Worker chat returns were briefs (counts, strongest match, path), not transcript dumps |
| 4 | Localization artifact contains a complete candidate map (source/session id, project+date, relevance rationale, regions, size, continuations, coverage gaps) |
| 5 | Routing followed the decision tree (indexed search first; no raw-transcript grepping as first move; provider matched to clue type) |
| 6 | Coverage gaps and uncertainty recorded honestly (unavailable providers named, not silently skipped) |
| 7 | ANALYZE resumed the localization worker when available; otherwise a replacement received the saved localization artifact and exact bounded source pointers |
| 8 | Semantic false positives were caught and excluded |

### Layer 2 — qualitative review (per scenario)

- What behavior did the skill evoke, end to end?
- Was each routing decision appropriate for the clues available?
- What went wrong or was slower/noisier than it should have been?
- What should it have done instead?
- Were any deviations from the expected route actually *better*? (If so, the finding is about the
  rubric or the skill's prescribed route, not the worker.)
- What specific change to the skill text (or worker profile) does that imply?

## Run storage

- Run directory: `evals/runs/2026-08-03-chat-history-stress/` (created when scenarios are executed;
  scorer notes per `docs/workflows/skill-evaluation.md`).
- Pre-run meta-observation (from the scenario-discovery run, itself a live exercise): AgentsView
  offered FTS-only (no semantic/hybrid); KCap is MCP-only and the worker had no MCP tools, so the
  skill's preferred KCap-first route was not exercised; localization still produced a strong
  candidate population on degraded indexes.

## Required comparison conditions

Run each scenario at least three times under each available condition:

1. current `chat-history` skill;
2. prior skill version, if its exact text/runtime can be reconstructed; and
3. no-skill baseline using the same tools and model.

If a condition cannot be reproduced, mark it unavailable rather than silently treating the current
skill as its own control.
