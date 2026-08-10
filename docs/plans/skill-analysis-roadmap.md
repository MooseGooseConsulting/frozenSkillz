# Plan: Skill Analysis Expansion Roadmap

Status: deferred roadmap. No phase begins until its entry condition is satisfied.

## Up Front

- **What:** Extend the proven deployment-debrief method to one additional skill question at a time.
- **Why:** Existing skills need evidence-backed trigger, instruction, and dependency fixes—not a
  speculative all-skill scoring platform.
- **How:** Admit each new capability only after the prior phase produces useful lessons grounded in
  real deployments.
- **Result:** A repeatable loop that understands how a skill is used, forms improvement hypotheses,
  makes the smallest supported change, and learns from later real use.

## How We Will Improve Existing Skills

1. Ask whether agents understood the skill, where it entered the work, what it appeared to change,
   whether it helped or hurt, and what was missing, vague, or overspecific.
2. Compare examples, counterexamples, owner corrections, and unresolved interpretations.
3. Identify the repair surface: trigger description, skill body, example, dependency rule, or no
   demonstrated skill defect.
4. Change only that surface in `frozenSkillz`.
5. Add the real prompt and expected behavior to the affected skill's regression cases.
6. Run the case before and after the change when controlled comparison is warranted.
7. Review the next real deployments; keep the change only when field behavior improves without a
   new regression.

## Purpose

Extend the narrow `project-docs` deployment-learning MVP only after it produces trustworthy, useful
lessons.
This document prevents later ideas from leaking back into the MVP.

## Phase 1 — Complete the Deployment-Learning MVP (complete)

Source: `docs/plans/skill-analysis-mvp.md`.

Exit condition:

- reviewable `project-docs` deployment debriefs and cross-case lessons exist;
- activation and comparison-sample construction are explicit;
- important interpretations cite their trajectory evidence;
- detector limitations are understood; and
- at least one real failure can become a regression case, or the result honestly says insufficient
  evidence.

Do not start later phases merely because extraction code exists.

The 2026-08-10 pilot satisfied this exit condition with a 288-session candidate manifest, 13
independently extracted cases, separate corpus synthesis, explicit coverage limits, and real
trigger/body regression candidates. Its findings remain observational; no later phase starts
implicitly.

## Phase 2 — Analyze One Skill Dependency

Question:

> Does PDM operational work unnecessarily activate Doppler when authentication remains opaque?

Scope:

- inspect only PDM-related sessions where both skills loaded, plus matched PDM sessions without a
  Doppler load;
- distinguish direct credential/injection work from ordinary opaque-launcher use;
- explain when the handoff appears useful, unnecessary, or unclear and why; and
- propose only dependency and trigger changes.

Still deferred:

- a general graph of every skill dependency;
- causal outcome claims; and
- scheduled monitoring.

Exit condition:

- the process can distinguish a legitimate secrets handoff from a workflow takeover using real
  sessions and a small regression set.

## Phase 3 — Add Controlled Replay for One Ambiguous Decision

Entry condition:

- field evidence identifies a material question that cannot be answered observationally.

Method:

- select six authentic positive prompts and six authentic negative prompts;
- compare current skill, proposed/prior skill, and no-skill conditions only when reproducible;
- run three isolated trials per condition;
- hold model, harness, tools, budget, and starting state constant;
- compare trigger choice, independent task outcome, added cost, and high-severity harm; and
- challenge evaluator interpretations against a human-reviewed subset.

Do not build a generic replay platform first. Implement only what the selected case requires.

Exit condition:

- replay changes or confirms a real lifecycle decision and produces reusable regression cases.

## Phase 4 — Generalize Across Three Distinct Failure Shapes

Candidate set:

- `project-docs`: misunderstood purpose, intrusive deployment, or unclear guidance;
- PDM → Doppler: unnecessary dependency chaining; and
- `context7-mcp`: load without material tool use.

Only now generalize shared concepts:

- activation-channel normalization;
- task-use versus meta-use classification;
- comparison sampling;
- compact deployment-debrief format; and
- trigger/body/example/handoff improvement-hypothesis format.

Exit condition:

- the same small toolchain handles all three skills without skill-specific hardcoding dominating
  the implementation.

## Phase 5 — Post-Change Field Measurement

Entry condition:

- at least one trigger or body change has landed and enough new opportunities exist.

Compare pre-change and post-change cohorts for:

- intrusive or irrelevant deployments;
- plausible missed opportunities;
- loads with no observable effect;
- unnecessary secondary skill loads; and
- explicit owner corrections.

Do not claim improvement immediately after editing skill text.

Exit condition:

- controlled cases and real post-change sessions agree, or the contradiction is documented and the
  verdict remains open.

## Phase 6 — Optional Review Queue Automation

Entry conditions:

- at least two manual analysis cycles were completed successfully;
- extraction and the deployment-debrief method remained usable across them; and
- a human actually used the resulting review queue.

Allowed automation:

- refresh read-only counts;
- flag surprising activation changes, repeated ignored loads, and explicit corrections; and
- produce a bounded review queue.

Prohibited automation:

- rewriting, promoting, disabling, or deleting skills;
- treating health or inferred completion as acceptance;
- creating another transcript database; and
- claiming the scheduler works before observing one real completed run and its durable output.

## Deferred Until Separately Authorized

- Fleet-wide grading of every skill.
- Complete per-session historical skill hashes.
- Delayed PR/file/runtime aftermath for every session.
- Live randomized A/B testing with user traffic.
- Universal decision thresholds across skills with different costs and risks.
- An autonomous skill-maintenance agent.
- A recurring cloud scheduler or resident listener.

These are separate products, not hidden completion criteria for `skill-analysis`.
