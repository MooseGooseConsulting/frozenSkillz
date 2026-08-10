# Skill Evaluation and Deployment Learning

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

## Choose the Depth That Matches the Question

Two related activities live here:

1. **Deployment learning** asks whether agents understood a skill, where it entered work, how it
   appeared to help or hurt, and what was missing, vague, overspecific, or intrusive. Use the
   personal `skill-analysis` skill. Build a candidate manifest, extract one trajectory per case
   reader, and give a separate corpus reader the completed memos. The output is lessons and
   improvement hypotheses, not mandatory labels or a lifecycle verdict.
2. **Controlled lifecycle evaluation** tests a consequential trigger, behavior, promotion, or
   removal decision. Use comparable trials, deterministic outcome checks where possible, and the
   optional structured fields later in this document.

Do not escalate deployment learning into controlled evaluation merely to make the result look more
rigorous. Use replay or scoring only when the decision actually needs them.

## What This Process Must Distinguish

An activation count is inventory, not effectiveness. A `SKILL.md` read can mean the skill was
invoked, inspected while editing it, loaded because another skill required it, or loaded and then
ignored. Likewise, a quiet next user message is not acceptance, and a green self-written test is
not an owner-visible outcome.

When a lifecycle claim depends on the complete funnel, distinguish:

```text
eligible opportunity
  -> activation was appropriate
  -> skill materially shaped behavior
  -> task reached an owner-visible outcome
  -> owner accepted, corrected, or gave no verdict
```

Never substitute a later stage for an earlier one or infer acceptance from silence. During
deployment learning, explore these as questions in the case debrief rather than forcing every
trajectory into one value at every stage.

## Two Complementary Evidence Tracks

### Track A — Historical field evidence

Use AgentsView and `chat-history` to learn how the skill behaves in real work. The first review of
a skill uses the complete available history, not an arbitrary recent month. Subsequent reviews use
both the full-history baseline and the cohort since the reviewed skill version changed.

Historical evidence establishes prevalence, real failure modes, harness differences, and owner
reactions. It does **not** establish causation by itself: difficult tasks may attract a skill, and
the same task may have failed without it.

### Track B — Controlled paired replay

Replay authentic historical prompts under comparable conditions:

- current skill;
- proposed skill revision, when evaluating a change; and
- no skill or the prior version when the question is whether the skill earns its cost.

Run at least three trials per condition. Compare outcomes, not just compliance: correctness,
completion, owner-visible state, unnecessary steps, latency/tool use, and new failure modes. A
skill can be followed perfectly and still make the task worse.

Field evidence supplies ecological validity; paired replay supplies the strongest available causal
signal. A keep/remove or trigger-change verdict should normally use both.

## Surfaces and Ownership

- **AgentsView is the source corpus.** Do not create a second transcript database for skill
  evaluation.
- **Derived query tooling belongs in `agent-control-plane`.** Detection, census, sampling, and
  labeling exports must be reproducible from AgentsView and must not mutate it.
- **Cases and lifecycle decisions belong here.** `frozenSkillz` owns skill versions, controlled
  cases, regression status, and the tracker verdict.

Invoke the personal `skill-analysis` skill for this cross-repository workflow. Do not recreate its
AgentsView extraction or aggregate-analysis lane under `frozenSkillz`.

Keep raw or sensitive trajectories outside git. Commit reproducible queries, compact labels,
aggregate results, and the decision—not transcript dumps.

## Proportionality

Do not run the full process on every skill every month:

1. **Census:** cheap, automated, produces a review queue but no verdict.
2. **Field review:** triggered by owner correction, surprising activation rate, repeated load with
   no material use, a version change, or a scheduled review of a high-impact skill.
3. **Paired replay:** required before consequential keep/remove decisions, promotion, or a trigger
   or behavior change whose benefit is uncertain.

A narrow trigger wording fix backed by clear owner correction may not need a fleet-wide research
project. It still needs its regression case and a later post-change field check.

## Case Memos and Optional Structured Fields

The primary counting unit is one **session x skill**, not raw reads. Page-by-page reads and repeated
loads in one session count once, with repetition recorded separately as a possible thrash signal.

Deployment learning uses the open-ended one-case prompt in
`_incubator/personal-skills/skill-analysis/references/deployment-debrief.md`; it does not require the
table below. When a controlled evaluation needs comparable fields, use only the fields that serve
the actual decision:

| Field | Allowed values |
|---|---|
| Opportunity | should trigger / should not trigger / ambiguous |
| Activation | explicit runtime tag / installed `SKILL.md` read / transitive requirement / none / unknown |
| Context | task use / skill editing or inspection / meta-evaluation / unknown |
| Material use | shaped behavior / loaded then ignored / contradicted / indeterminate |
| Outcome | achieved / partial / failed / unknown, with owner-visible evidence |
| Owner response | explicit acceptance / explicit correction / no verdict |
| Harm or cost | none / ceremony / delay / scope drift / wrong tool or route / other |
| Attribution | strong / plausible / weak, with rationale |
| Skill identity | source path plus commit, package version, or content hash; unknown when unrecoverable |
| Delayed aftermath | survived / reinforced / corrected later / reverted / unknown |
| Rubric identity | rubric version or content hash used for this judgment |

Do not judge an old session against today's skill text unless the historical version is known.

## Population and Sampling

1. **Census the full indexed population.** Report database coverage dates, harnesses, total
   sessions, detectable activation channels, missing providers, and detector limitations.
2. **Separate usage from meta-work.** Editing, reviewing, or evaluating a skill is not evidence that
   it helped with its intended task.
3. **Build the denominator.** Sample prompts where the skill should have fired but did not, as well
   as prompts where it did fire. Without opportunities, false-negative and false-positive rates
   cannot be estimated.
4. **Stratify the transcript sample.** Include every explicit owner correction; activations since
   the last skill version change; a random sample across harnesses and time; high-cost/thrashy
   sessions; and matched no-fire opportunities. Keep strata visible instead of blending them into
   one score.
5. **Preserve scarce evidence.** For low-volume skills, review all available task-use episodes and
   report `insufficient evidence`; do not manufacture confidence from percentages with tiny `n`.

The rolling recent window is a drift detector, not the evaluation population. Monthly or
August-only counts may identify what to inspect, but never support an effectiveness verdict alone.

## Controlled Evaluation Method

Use this full method for a controlled lifecycle question. For observational deployment learning,
follow the manifest → one-case memo → separate corpus-reader workflow in `skill-analysis` and stop
when it produces useful lessons or bounded improvement hypotheses.

1. **Fingerprint the evaluated skill.** Record its source path and exact commit, package version,
   or content hash. Record the trigger text separately from the procedural body so the two can
   receive different verdicts.
2. **Run the historical census and construct the sample.** Use all indexed history plus the
   post-version cohort, applying the population and sampling rules above. Publish coverage and
   denominators before rates.
3. **Review real episodes.** Use `chat-history` to read the selected trajectories. Two reviewers
   independently label ambiguous or high-impact episodes; calibrate disagreements against the
   raw conversation and observable final state. Owner corrections outrank inferred sentiment.
   When a repository, PR, or runtime target is named, check later churn, reverts, CI, and follow-up
   fixes from that exact surface; otherwise label delayed aftermath `unknown`.
4. **Derive controlled scenarios from real history.** Use the `chat-history` skill to find authentic past
   moments where the skill would have been invoked. Never invent synthetic prompts you imagine the
   user might say — fabricated scenarios test the wrong thing. Prefer scenarios with **known ground
   truth** (the original episode's verified outcome), so correctness is checkable rather than vibes.
5. **Create one temporary run directory outside the repository.** Worker artifacts (candidate maps,
   analyses) go there with exact unique paths. Do not commit raw transcripts or long history
   excerpts to the repository; reference local paths from the case file instead.
6. **Run paired conditions.** Run the skill as it is actually invoked and include the appropriate
   comparison condition (prior version, proposed revision, or no skill). Follow each skill's real
   contract. Record coverage gaps honestly. **Run at least 3 trials per scenario per condition.**
7. **Score with a two-layer rubric:**
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
8. **Reconcile field and replay evidence.** Explain agreements and contradictions. Do not average
   away a field failure because a synthetic replay passed, or declare causation from correlation.
9. **Record the case and the runs.** Case definitions live in `evals/cases/<YYYY-MM-DD>-<skill>.md`
   (scenario, verbatim trigger, source session, ground truth, rubric). Run results live in
   `evals/runs/<YYYY-MM-DD>-<case-slug>/` with scorer notes per trial, per the intake protocol's
   storage shape.
10. **Make separate decisions:**
   - **Trigger:** keep / narrow / broaden / disable / insufficient evidence.
   - **Behavior:** keep / revise / remove / insufficient evidence.
   - **Lifecycle:** active / gated / regression-covered / re-review after more task-use episodes.
11. **Feed findings back.** Skill-text changes go through the normal authority and frozen-sync
   workflow (`docs/workflows/skill-authority-and-frozen-sync.md`). Conflicting findings stay
   visible; do not average disagreement into false certainty. After a fix lands, rerun the case —
   passing cases move to the regression suite for that skill.

## Cadence

- **After any trigger or skill-body change:** run the affected regression cases and review the
  post-change cohort once real sessions exist.
- **Monthly:** refresh the activation/opportunity census as a drift and sampling queue only.
- **Quarterly:** rerun the stratified transcript review for high-volume or high-cost skills.
- **Immediately after an owner correction:** add the episode to the review queue and decide whether
  it exposes a trigger defect, a behavior defect, or unrelated agent failure.

No scheduled run may auto-promote, delete, or rewrite a skill. It may produce a review queue;
versioned changes still require the paired evidence and an owner-visible decision.

## Minimum Effective Output

Deployment learning is complete when it records corpus coverage, individually extracted case memos,
cross-case patterns and counterexamples, owner corrections, improvement hypotheses, and important
unknowns. It does not need paired replay or lifecycle verdicts unless the requested decision depends
on them.

A controlled lifecycle evaluation is complete only when it states:

- corpus coverage and blind spots;
- activation detector and session x skill denominator;
- opportunity denominator, including sampled no-fire cases;
- task-use versus meta-use counts;
- labeled transcript sample with explicit `n` per stratum;
- paired replay results per condition and trial;
- outcome and owner-response evidence;
- separate trigger, behavior, and lifecycle verdicts;
- exact skill version evaluated and the next recheck condition.

Anything less than the controlled list remains deployment learning or exploratory analysis; that is
not a defect when it answers the question actually asked.
