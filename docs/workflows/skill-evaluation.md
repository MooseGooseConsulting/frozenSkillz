# Skill Evaluation (Stress-Testing Existing Skills)

How to evaluate a skill this repository already owns (frozen, personal, or incubator). For
evaluating *external* candidates before intake, use
`plugins/frozen-skills/skills/external-skill-intake/references/evaluation-protocol.md` instead.

## Principle

A skill evaluation watches the behavior the skill evokes, then reasons backward: was that the
appropriate behavior for the situation, where did it drift, what should it have done instead, and
what change to the skill text does that imply? Scores are bookkeeping; the observations are the
deliverable. Do not reduce the rubric to countable metrics — they miss the point.

Practitioner rules that apply directly:

- Use a rubric only when behavior must stay consistent across runs, not for one-off tasks
  (HyperAgent: a rubric is a persistent "definition of quality" stored alongside skills).
- A model grading its own work can repeat its own misunderstanding. Pair every rubric with known
  ground truth, deterministic checks where possible, and human review (HyperAgent, Anthropic).
- Grade the **outcome**, not the transcript: the agent claiming success is not evidence; check the
  final state against ground truth (Anthropic, "Demystifying evals for AI agents").
- Agents are non-deterministic. **Every scored run is multiple trials**, not one run with a caveat.
  Run at least 3 trials per scenario per scoring event; record each trial's result, not an average
  impression. A single passing run is an anecdote, not a measurement.
- Do not grade against one imagined path: an agent that deviates from the expected route but solves
  the task better is a finding about the rubric, not a failure. The qualitative review decides
  whether a deviation was worse or better.
- Capability vs. regression: new eval cases are capability evals (expected to start at a low pass
  rate, a hill to climb). Once the skill passes consistently, the case **graduates into the
  regression suite** and must keep passing on every future edit to that skill. Eval cases in
  `evals/cases/` are therefore permanent assets, not one-time scratch.

## Method

1. **Derive scenarios from real history.** Use the `chat-history` skill to find authentic past
   moments where the skill would have been invoked. Never invent synthetic prompts you imagine the
   user might say — fabricated scenarios test the wrong thing. Prefer scenarios with **known ground
   truth** (the original episode's verified outcome), so correctness is checkable rather than vibes.
2. **Create one temporary run directory outside the repository.** Worker artifacts (candidate maps,
   analyses) go there with exact unique paths. Do not commit raw transcripts or long history
   excerpts to the repository; reference local paths from the case file instead.
3. **Run the skill as it is actually invoked.** Follow the skill's own contract (stages, delegates,
   artifact rules). Record coverage gaps honestly — a provider that was unavailable means that route
   was not exercised, and the scorer notes must say so. **Run at least 3 trials per scenario.**
4. **Score with a two-layer rubric:**
   - *Hard gates — only where a genuine non-negotiable exists.* A gate is a failure that should
     veto the whole trial regardless of other strengths (e.g. a retrieval skill returning an
     answer that contradicts known ground truth). Most criteria are quality gradients, not gates;
     many evaluations will have no gates at all. Do not manufacture gates to make the rubric look
     rigorous.
   - *Layer 1 — behavioral assertions.* Pass / partial / fail checks derived from the skill's own
     contract, judged against the observed trajectory (e.g. for `chat-history`: LOCALIZE before
     ANALYZE, artifacts written to the run directory, chat returns stayed briefs, candidate map
     complete, coverage gaps reported).
   - *Layer 2 — qualitative review.* For each scenario: what behavior was evoked; was it
     appropriate; what went wrong; what should it have done instead; what does that imply for the
     skill text. This layer, not the scores, is where findings live.
5. **Record the case and the runs.** Case definitions live in `evals/cases/<YYYY-MM-DD>-<skill>.md`
   (scenario, verbatim trigger, source session, ground truth, rubric). Run results live in
   `evals/runs/<YYYY-MM-DD>-<case-slug>/` with scorer notes per trial, per the intake protocol's
   storage shape.
6. **Feed findings back.** Skill-text changes go through the normal authority and frozen-sync
   workflow (`docs/workflows/skill-authority-and-frozen-sync.md`). Conflicting findings stay
   visible; do not average disagreement into false certainty. After a fix lands, rerun the case —
   passing cases move to the regression suite for that skill.
