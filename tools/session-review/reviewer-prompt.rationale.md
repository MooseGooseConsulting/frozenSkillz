# reviewer-prompt.md — rationale

Companion to `reviewer-prompt.md` (required for every agent prompt: the prompt says
*what*, this file says *why*, what we're tuning, and what each rubric field is for).
`wake-prompt.md` is covered at the bottom.

## Why this prompt exists

The reviewer answers one question per session: **did this session actually serve the
owner, and what did the fired skills contribute?** Its verdicts replace two failed
grading methods: AgentsView's `health_score` (a thrash counter — 85% of sessions grade
A; it cannot see success) and skill-compliance reading ("the agent followed the skill
verbatim" — disproven as a success measure by the unity-editor-ops session, where
verbatim compliance coexisted with total failure).

## What we are tuning

The prompt is an instrument, and instruments drift. The tuning loop:

1. **Golden set** (calibration table at the bottom of the prompt): sessions with
   owner-verified expected verdicts. The judge must reproduce them after every prompt or
   model change. Every owner overturn adds a row — the set grows by exactly the judge's
   mistakes.
2. **Consistency**: independent wakes must produce field-identical verdicts on the same
   input (verified runs 1-2).
3. **Responsiveness**: a rubric gap found in traces must be fixable with one versioned
   field change and verified the same day (demonstrated: v2 pushback, found and closed
   2026-07-31).

## Field-by-field rationale

| Field | Why it exists / what failure it catches |
|---|---|
| `goal`, `goal_reached` | Anchors the verdict to what the owner actually asked, not what the agent chose to do. Rule: owner's closing reaction is ground truth for outcomes. |
| `owner_visible_outcome` | Forces "what changed that the owner can see?" — self-written tests passing and documents produced explicitly do not count (unity-editor-ops lesson: 196/196 self-graded green in a failed session). |
| `closing_sentiment` | The end-state reaction, deliberately scoped to the closing window so recovered sessions aren't punished for mid-flight turbulence. |
| `thrash` | Repeated failures, churn, loop-spinning. Includes the blocked-resource rule: a needed resource being down should halt work, not redirect it into adjacent output. |
| `ceremony` | Evidence documents / gates / approval theater produced during operational work the owner never asked to audit — the register this whole project exists to suppress. |
| per-skill `effect` | The payload for the skill tracker: shaped / ignored / hurt / meta, each requiring a quote. `meta` exists because ~half of some skills' "usage" is sessions editing the skill itself. |
| `pushback` (v2) | Mid-session owner corrections/frustration with the worst verbatim quote. Added because v1's closing-window scoping silently discarded an owner blowup at ordinal 134 that the judge had demonstrably read. Doesn't alter outcomes — records turbulence. |
| `implementation_quality` (v3) | Corroborates the chat against the actual diffs (read-only `git show` of the session's commits). Catches quiet failure: polite sessions that merged poor work. Bounded in v4: only `artifacts.repo` or a transcript-named path — no filesystem hunts. |
| `aftermath` (v3) | What time did to the work: reverts, fix-commits, re-churn of the same files. Retrospective grading means this evidence usually already exists. The strongest detector of quiet failure. |
| `claims_gap` (v3) | Mechanical: completion claimed with no verification execution after the last edit (`verification_signals`). Caught, on first use, a "Done… Pushed" claim where the final script was never run. |
| `mutation_candidate` | The smallest skill edit that would have changed this session's outcome; process/gate additions are banned so the reviewer cannot reinvent ceremony. |
| `confidence` + abstention | A wrong confident grade poisons the tracker; `insufficient` / `not_inspectable` are first-class verdicts (exercised honestly in run 4). |

## Priority of evidence (v4, owner-directed)

Behavior first, artifacts second. The behavioral trajectory — what the agent did, what
skills did to it, how the owner reacted — is the point of the system; artifact checks
corroborate it and may never displace or shorten it. This was made explicit after the
owner flagged that "judge the work, not the chat" framing risked flipping the
instrument into a code reviewer that loses the behavioral story.

## Bias guards baked into the prompt

No quote → no claim (anti-hallucination). Don't reward prose (anti-verbosity bias).
Compliance ≠ success (anti-sycophancy toward skills). Abstain freely (anti-overreach —
LLM judges are unreliable on thin evidence). Structured enums validated in code by
`record_verdict.py` (anti-format-drift).

## Version log

| Version | Date | Change |
|---|---|---|
| v1 | 2026-07-31 | Initial rubric: goals, sentiment, thrash, ceremony, skill effects, mutations, confidence. Calibration runs 1-2: 7/7, field-identical. |
| v2 | 2026-07-31 | + mandatory `pushback` (mid-session frustration was being discarded by closing-window scoping). Run 3 verified. |
| v3 | 2026-07-31 | + `implementation_quality`, `aftermath`, `claims_gap` (owner: "can it detect poor implementation, or just key off me yelling?"). Run 4 verified, incl. honest abstention. |
| v4 | 2026-07-31 | Behavior-first primacy rule; artifact inspection bounded to named paths, read-only, no hunts (owner pushback on scope drift). |

## wake-prompt.md (runbook) rationale

The wake prompt makes the agent the operator (no driver script): pull freshest rubric,
sweep skill versions, condense, grade one-at-a-time (context discipline — earlier
sessions must not bleed into later verdicts), validate every verdict through code,
commit only its own paths on its own branch. The calibration gate (`CALIBRATED` marker,
owner-created only) keeps an untrusted judge from feeding the tracker.
