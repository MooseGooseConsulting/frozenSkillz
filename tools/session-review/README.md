# Session review system

A Letta cloud agent ("Session Reviewer") wakes nightly, reads condensed trajectories of
skill-firing AI sessions from the AgentsView database, grades each against a versioned
rubric, and accumulates verdicts and skill-mutation proposals in this repo. It exists
because skill effectiveness was previously judged by vibes and thrash counters — the
`unity-editor-ops` false-positive (a session graded "earns its keep" because a skill was
followed verbatim, while the owner's closing message was "I feel like we never really
made any progress did we?") proved that compliance is not success and that only
transcript-plus-artifact evidence can tell the difference.

## Components

| File | Role |
|---|---|
| `reviewer-prompt.md` | The grading rubric the agent applies — the prompt IS this file. |
| `reviewer-prompt.rationale.md` | Companion: why each field exists, what's being tuned, version log. Every prompt change updates both. |
| `wake-prompt.md` | The agent's nightly runbook (what a wake does, step by step). |
| `condense.py` | Turns a raw session (up to 1000+ messages) into an ~8 KB trajectory: opening ask, real user messages, claims, closing window, tool stats, skills fired (incl. codex's untagged SKILL.md-read channel), verification-ordering signals, session commits + aftermath. |
| `skill_versions.py` | Nightly SKILL.md fingerprint ledger (`skill-versions.jsonl`) so every grade records which skill version was live. |
| `record_verdict.py` | Schema validator and recorder — invalid verdicts cannot land. |
| `config.json` | Agent id, model, rubric version, nightly cap. |
| `grades/YYYY-MM.jsonl` | The verdicts (append-only, in git). |
| `grades/calibration-log.md` | Calibration run comparisons. |
| `proposals.md` | Accumulated skill-mutation candidates for owner review. |
| `CALIBRATED` (marker) | Owner-created gate: until it exists, wakes only re-grade the golden sessions. The agent may never create it. |
| `state.json` (local, gitignored) | Which sessions are already graded. |

## Operations

- **Agent:** `agent-eca49835-7c10-4049-9b68-3d42b90ea218`, Letta Cloud, `gpt-5.6-luna`,
  medium reasoning effort, ChatGPT-Pro/Codex OAuth provider.
- **Schedule:** Letta cloud cron `nightly-session-review`, `0 8 * * *` UTC (~3am
  Central), targeting machine HEPHASTUS (deviceId `8a88a521-1410-4dae-acae-4b4a3cd684ac`).
- **Runtime requirement:** a resident `letta server` on HEPHASTUS (auto-starts via the
  user Startup folder entry `letta-server.cmd`). If offline at fire time, the wake falls
  back to the cloud sandbox and safely no-ops ("machine unavailable — skipped").
- **Workspace:** the dedicated git worktree `D:\_projects\frozenSkillz-review` on branch
  `review/nightly-grades`. The agent never touches any other checkout or branch.
- **No API key.** Native scheduled wakes run under the agent's own auth. `LETTA_API_KEY`
  is only needed for headless `letta -p` CLI calls, which this design does not use.
- **Manual trigger:** register a short recurring cron (`--every 10m`) with a
  self-limiting prompt and delete it after the first run. Known Letta gotchas:
  one-shot `--at ... --once` schedules with `--computer` never fired (0.29.8);
  `letta cron delete --all` also deletes the nightly; the Windows CLI often exits 9
  after complete output — trust stdout, not exit codes.

## Build and calibration history (2026-07-31)

Design evolved through three rejected shapes: a PowerShell driver piping prompts to the
agent (killed — wrong idiom, created a needless API-key dependency), external Task
Scheduler scheduling (killed — Letta cron is the native mechanism), and unbounded
artifact review (bounded in v4 after owner pushback — behavior first).

| Run | Rubric | Result |
|---|---|---|
| 1 | v1 | 7/7 expected labels on the golden trio; independently derived the unity-editor-ops stop-condition fix as its mutation candidate. |
| 2 | v1 | 7/7 again; field-identical to run 1 across all outcomes, sentiments, and 14 skill-effect grades — judge is stable across independent wakes. |
| 3 | v2 | New `pushback` field captured the mid-session "What the fuck?…" quote that v1 discarded (trace inspection showed the judge had read it but had nowhere to record it), plus a second uncataloged pushback. |
| 4 | v3 | Artifact grounding verified both ways: located and read-only-inspected a session's real commit (`sound`, `survived`, `claims_gap: some` — final edit never executed), and honestly abstained (`not_inspectable` / `insufficient`) on an artifact-less codex session. |

## Maintenance contract

- Owner overturns of any grade go into the calibration table in `reviewer-prompt.md` —
  the golden set grows by exactly the cases the judge got wrong.
- Every rubric change bumps `rubric_version` (in the prompt, the output schema, and
  `config.json`) and updates `reviewer-prompt.rationale.md`. Verdicts from different
  versions are never comparable silently.
- Re-run the golden set after any rubric or model change before trusting new grades.
- Verdicts feed `docs/skill-review/tracker.md`; proposals are suggestions, never
  auto-applied.
