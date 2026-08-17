# Ideas Ledger: The Circular Self-Improving Workflow

Status: recovery document. Captures ideas from discussions (June-August 2026) that did not
land in `trace-distillation-contract.md`. Each idea is sourced with a date and context so it
can be evaluated for incorporation or explicitly deferred.

The trace distillation contract defines the **capture layer**: a mechanical scheduled job that
distills agent sessions into structured Postgres rows. This ledger captures the **broader
circular workflow** — the loop where distilled sessions feed back into skill changes, which
generate new sessions, which get distilled, which surface new patterns. The contract
deliberately stops at capture; these ideas describe what happens around and beyond it.

---

## 1. The Closed-Loop Pattern (the "Ralph Loop")

**Source:** Hyperagent / ChatGPT discussion, 2026-07-22

A self-improving agent that builds, tests, and deploys autonomously in a closed loop, audits
its own work against a rubric, and persists learnings to a knowledge base that feeds back into
the next cycle. Named "Ralph Loop" in the discussion.

**Key property:** the loop's output (learnings, audit findings) is the input to the next
iteration. This is the shape the trace distillation pipeline is meant to serve — distill →
examine → change skill → new sessions → distill again.

**Not in contract:** the contract defines capture only. The feedback path from distilled rows
back to skill changes is described as a "consumer" but the loop's closure mechanics are not
specified.

---

## 2. Multi-Agent Debate Is a Martingale

**Source:** Hyperagent conversation, 2026-07-18, citing NeurIPS 2025 paper

> "A NeurIPS 2025 paper proved vanilla multi-agent debate is a martingale — it doesn't improve
> correctness; majority voting accounts for all the gains."

> "A May 2026 paper found 63.6% of agent 'conformity' is agents flipping correct to wrong
> because LLMs treat the structural appearance of reasoning as evidence. Collapse-to-loudest-
> agent is the default behavior, not a bug."

**Implication for the pipeline:** any examination layer that uses multi-agent debate or council
voting to judge distilled sessions will not improve correctness over a single reviewer. What
the research says would actually work:

- **Independent verifier agents** checking claims against external evidence (not against each
  other's reasoning)
- **Diversity-aware retention:** keep the most *disagreeing* messages, not the most *confident*
- **Belief tracking with log-odds** instead of majority vote

**Not in contract:** the contract is silent on how the examination layer should be structured.
This research constrains the design: do not build a council-voting reviewer.

---

## 3. Builder Self-Critique vs. Separate Critic

**Source:** Multiple discussions, 2026-07-16 through 2026-07-23

An open design question across several sessions:

- **Option A:** the same builder agent critiques its own work (self-critique loop)
- **Option B:** a separate critic agent reviews the builder's output

**Failure mode identified:** "same model writing and grading its own work" — the builder
rationalizes its own mistakes rather than genuinely catching them, because it has no
adversarial pressure.

**Resolution direction:** separate CI agent that operates independently of the builder, with
its own rubric and blast-radius awareness. Different model/context than the builder to prevent
the self-grading failure mode.

**Not in contract:** the distiller is mechanical (no judging), but the examination layer that
consumes distilled rows must use a different model/context than the agent that produced the
session under review. This is a design constraint on consumers.

---

## 4. The Session Reviewer Retrospective (Step 9)

**Source:** Claude conversation, 2026-07-31

The decommissioned nightly reviewer gained a retrospective phase: after grading sessions, it
ran the retrospective skill timelines, checked its own memory and existing learnings docs
before writing, so a repeat observation upgraded an existing proposal in place instead of
duplicating.

> "Whole-history reasoning compounds run over run instead of resetting like a session-scoped
> agent would."

**Write boundary:** dated append-only entries to a target skill's `## Learnings`. Anything
structural — triggers, workflow rewrites, deletions — routes to `proposals.md`.

**Not in contract:** the contract says "learning-over-time lives in the accumulating database,
not in agent memory." This retrospective pattern is the mechanism: the distilled store is
checked before writing new findings, so repeated observations upgrade rather than duplicate.

---

## 5. The Ceremony Problem

**Source:** Claude conversation, 2026-07-31 (the Unity-editor-ops overturn)

> "A 196/196 pass rate on tests the same agent wrote minutes earlier, for code no one can see
> running, is ceremony wearing a test harness."

The core failure: an agent grades skill compliance ("followed the batch-mode recipe verbatim")
as if that were success. The skill's recipe is legitimate, but in that session it functioned as
an enabler — it let a disconnected loop keep manufacturing green checkmarks instead of stopping.

**Rubric fix applied:** a third mandatory question — "did the session end with an owner-visible
outcome?" Self-written tests passing is explicitly not an outcome.

**The /loop + keep-going skill = bad combination:** the loop's incentive is to fill ticks; a
recipe for working around a blocked resource turns a blocker that should halt the loop into a
hundred ticks of self-referential output.

> "If the primary resource (Unity/MCP) is unavailable for 2 consecutive ticks, stop and report."

**Not in contract:** the `harm_cost` field captures "ceremony" as a value, but the deeper
lesson — that skills can *enable* ceremony by providing workarounds for blocked resources —
is a pattern the examination layer must watch for, not just a field to populate.

---

## 6. Owner Reaction as Ground Truth

**Source:** Claude conversation, 2026-07-31; also in session reviewer rubric v4

> "The owner's closing reaction is the ground truth, and self-written tests passing is
> explicitly not an outcome."

> "Whether your next message after a skill fires is a correction (the most honest effectiveness
> signal in this corpus)."

**Evolution:** the July rubric treated closing reaction as ground truth. The August reframing
softened this to "just evidence" and added "silence ≠ acceptance." The contract adopts the
softer version: `owner_reaction` can be `no verdict`, and silence is never acceptance.

**Not in contract:** the "next message after a skill fire is a correction" signal — this is a
cheap, high-signal derived metric that could be computed directly from AgentsView without full
distillation. It's a candidate for a pre-distillation triage filter.

---

## 7. The Measurement Loop That Has Nothing to Measure

**Source:** Claude conversation, 2026-07-30

> "The analysis itself did land in agent-control-plane (the ceremony scorecard script and
> learnings docs), so the measurement loop exists — it just has nothing to measure yet because
> no intervention shipped."

The pattern: analysis runs, findings are produced, but the fixes are never applied. The loop
is open — it measures but does not act. The trace distillation pipeline risks the same fate if
distilled rows accumulate without anyone acting on them.

**Not in contract:** the contract's stop conditions prevent premature consumer scheduling, but
do not address the opposite failure — the store exists, is correct, and is never consulted.

---

## 8. ProjectBroadside: The Concrete Circular Workflow

**Source:** ChatGPT conversation (ProjectBroadside), 2026-07-27

The most concrete instantiation of the "big circular, self-improving workflow":

> "An autonomous sound-design factory that repeatedly examines the game, imagines what ought to
> exist, implements it, then examines the improved game again."

**Five persistent queues:**
1. Coverage queue — game situations still needing sonic analysis
2. Production queue — designed audio events awaiting generation
3. Self-QA/rework queue — things the agents themselves think failed
4. Human review queue — finished sounds that deserve your ears
5. Feedback/revision queue — your review comments that should alter assets and design rules

**The crucial loop — contextual re-audit:**
> "After implementation: Play/inspect newly sonified event. 'Now that this exists, what else is
> conspicuously missing?' New events → feed into mark situation → design loop."

**Example cascade:** gunshot exists → recoil now feels silent → recoil added → gun
crew/rigging contrast becomes obvious → broadside needs aggregate layer → distant response
needs separate treatment.

**Human review as asynchronous feedback loop:**
> "Your review does not belong between Generate and Attach. Agent work keeps moving → Audio
> Master Ledger → Review Queue → Patrick listens → approve / critique / replace → Review
> feedback ledger → Agent consumes feedback."

**Not in contract:** this is the shape the trace distillation pipeline should ultimately
serve. The distilled store is the "Audio Master Ledger" equivalent — the system of record. The
five queues map to: candidate selection (coverage), review queue (production), self-QA
(examination findings), human review (spot-check), and feedback (skill changes).

---

## 9. Convergence Mechanics from External Systems

**Source:** Hyperagent conversation, 2026-07-18

Three external systems researched for their converge-build patterns:

### agent-workflows (sjarmak/agent-workflows, March 2026)
21 Claude Code skills. Chain: `/diverge` (N independent agents, different lenses —
technical/UX/risk/prior-art — they never see each other's output) → `/converge` (structured
debate, steel-man rule, "lead moderates not advocates," convergence report records what
evidence was decisive and preserves dissent) → `/premortem` → `/scaffold` → `/focus` (build).

**Catch:** Team Lead synthesizes convergence rather than agents eliminating each other. Human
gating between phases. Not "drop and walk away."

### Shipyard AI (sethshoultes/shipyard-ai, April 2026)
Daemon watches a `prds/` folder. Drop a markdown file → auto-runs: 2 rounds of debate →
distill → synthesize → plan → build → QA → creative review → board review with ship/no-ship
vote → ship. Come back to shipped.

**Catch:** persona-based not evidence-based convergence. Built for one CMS. But the shape —
drop goal, walk away, come back to shipped — is there.

### ASTGL (astgl.com, April 2026)
5-agent council, each scores ideas on 5 criteria, ranked-choice instant-runoff voting with
elimination rounds, 48-hour stall timer ("without it the council endlessly debates scoring
refinements instead of building"), kill switch.

**Catch:** builds digital products (PDFs/templates), not arbitrary software.

### spikekit (gongxhl3/spikekit, 2026-05-12)
`/spike` = throwaway experiments in `.spike/` scratch dir until approach proven OR
proven-not-to-work (dialogue-driven). `/spike-wrap` = consolidate into `design.md` + human
HTML one-pager, then delete scratch. `/spike-goal` = POLICY layer on Claude Code `/goal`.

**Not in contract:** these are candidate architectures for the examination/convergence layer
that consumes distilled rows. The divergence-then-convergence pattern, with independent
agents who never see each other's output, is the structure the research (Section 2) says
actually works — as opposed to council voting, which is a martingale.

---

## 10. Anti-Convergence and Adaptive Deliberation

**Source:** ChatGPT discussion, 2026-07-17

When multiple artifacts compete (e.g., two competing designs), instead of converging
prematurely, the system deliberately maintains diversity.

**Anti-convergence mechanism:** prevents premature consensus that could miss better
solutions. The runtime tracks when to converge vs. when to keep exploring based on confidence
thresholds and time budgets.

**Not in contract:** the examination layer must sometimes *not* converge — when two
interpretations of a session's outcome are both plausible, the distilled row should preserve
both rather than picking one. This is why `indeterminate` is a first-class value.

---

## 11. Complexity Score-Based Task Routing

**Source:** Clipboard capture, 2026-07-01

Tasks are assigned complexity scores (0-10):
- High complexity (>7) → autonomous multi-agent feedback loops
- Low complexity (<4) → single-pass builder
- Medium → builder + critic two-pass system

**Not in contract:** the distiller processes all sessions the same way. But the examination
layer could route based on session complexity — a trivial session that fired no skills needs
only navigation condensation, while a complex multi-skill session with corrections needs a
full evidence packet and deep examination.

---

## 12. Local LLM Testing Loop (7-Step Adversarial Persist)

**Source:** VS Code / Terminal, 2026-06-22

A 7-step loop for locally testing LLM-based agents:
1. Generate task prompt
2. Run agent
3. Capture output trace
4. Distill trace into rubric-aligned summary
5. Score against rubric
6. Persist scores and distilled summaries
7. Feed back as context to next prompt

**Key features:** fully local (no cloud), adversarial (actively tries to find failure modes),
persists between runs.

**Not in contract:** the trace distillation pipeline is steps 3-6 of this loop. What's missing
is the closure — step 7 (feed back as context) and the adversarial framing (actively hunting
for failure modes, not just recording what happened).

---

## 13. Compliance Interviewer — Closed-Loop Lane Graph

**Source:** Google Docs, 2026-06-09

A "compliance gate" that functions as a work journal:
- Uses a "lane graph" model where each lane is a compliance dimension (security, correctness,
  maintainability, etc.)
- The interviewer persona asks adversarial questions in each lane
- Answers are captured as work entries that form a graph of evidence
- Self-auditing: the system audits its own decisions for compliance

**Not in contract:** the `harm_cost` field captures compliance-adjacent concepts (ceremony,
delay, scope drift, wrong tool, unnecessary handoff) but as flat values. The lane graph model
would structure these as typed edges in a graph, not as a single enum field.

---

## 14. Real-Time Checker-Agents Shadowing Execution-Agents

**Source:** Pieces annotation, 2026-07 (persona summary)

> "Audit-first approach where checker-agents shadow execution-agents to surface failures in
> real-time."

**Not in contract:** the trace distillation pipeline is post-hoc (every other day, from
recorded sessions). The shadowing concept is the real-time version — checker agents that run
alongside the execution agent and flag failures as they happen. This is a fundamentally
different latency tier. The contract's stop conditions prevent scheduling consumers before
spot-check, but the shadowing concept is worth recording as a future tier.

---

## 15. Capture Plane Typed Node/Edge Ontology

**Source:** Pieces annotation, 2026-07

A structured conversation format ontology using typed nodes:
- `SourceArtifact`, `RecordShape`, `StreamRole` as node types
- `provider_produces`, `artifact_contains` as edge types

**Related:** a control-plane graph migrated from local SQLite to remote Supabase Postgres with
stable UUIDs, `cg_cards` and `cg_card_edges` tables, and live graph traversal queries.

**Not in contract:** the distilled store uses flat rows (`distilled_sessions`). The typed
graph model would represent session relationships (continues, supersedes, corrects, related)
as typed edges between session nodes, not as fields within a row. This is a richer data model
that the examination layer could benefit from.

---

## 16. Atomic "Bead" Tasking

**Source:** Pieces annotation (persona), 2026-07

> "Utilizing atomic task units ('Bead' tasking) to force granular, verifiable accountability
> across his entire fleet."

**Related:** a "Knowledge Boundary" that protects core logic from agent drift, using atomic
task units to force granular, verifiable accountability.

**Not in contract:** the distilled `user_goal` is "one sentence: what the owner actually asked
for." The Bead concept suggests that sessions should be decomposable into atomic task units,
each with its own verifiable outcome. A session that did five things should produce five
examinable units, not one distilled row.

---

## 17. Heterogeneous Agent Swarm Under Governor Control

**Source:** Pieces annotations, 2026-07

> "Swarm of sub-agents (Claude, Codex, OpenHands, Z.ai/GLM-5.2)" — "treating AI agents as
> parallel judgment-driven governors rather than subordinate tasks."

> "Treating his environment as an adversarial environment where automated agents are powerful
> but prone to 'scope hallucination'" — "ultimate arbiter of truth, treating all external
> reports as unreliable data points that require rigorous cross-referencing against measured
> ground truth."

**Not in contract:** the `harness` field records which agent produced the session, but the
examination layer's design must account for the fact that different harnesses have different
failure modes. A correction in a Codex session means something different than a correction in
a Claude session.

---

## 18. Agentic CI as Separate Agent (Blast-Radius-Aware PR Gate)

**Source:** ChatGPT, 2026-08-17

- CI is not just a script — it's an autonomous agent with its own mandate
- Uses a "blast-radius-aware" review: PR approval gate checks not just code quality but how
  much surface area the change touches
- The critic agent has a different model/context than the builder

**Two-tier review design:**
```
PR opened
    │
    ├─ deterministic CI
    └─ FAST AI REVIEW (2-5 min, horizontally scalable)
            │
            └─ MERGE READY → MERGE
                    │
              meanwhile...
              Kilo deep review (advisory / async)
```

**Policy:** "No advisory external service is allowed to impose queue latency on the merge
pipeline."

**Not in contract:** this is the merge-pipeline application of the same circular pattern. The
trace distillation pipeline feeds skill evaluation; the PR review pipeline feeds code
evaluation. Both share the same shape: capture → examine → act → new artifacts → capture again.

---

## 19. Letta-Based Reviewer Architecture

**Source:** ChatGPT / Windows Terminal, 2026-08-14

1 persistent Letta reviewer per repository, 6 concurrent PR workflow jobs. Per PR:
- Persistent reviewer (memory across PRs)
- 4 parallel ephemeral specialists: correctness, regression tests, architecture/security,
  adversarial verification
- Persistent reviewer makes final decision

**Iterative review loop:**
> "If a bot pass arrives, address it, push, and then wait for a fresh pass on the new HEAD
> before merging — that loop only exits when the bots have reviewed the exact commit being
> merged."

**Not in contract:** the contract defers "Letta/memory recurring reviewer as a consumer"
until one manual ongoing-mode cycle proves the loop. This architecture describes what that
consumer would look like when revived: persistent memory across review cycles, ephemeral
specialists for depth, and a convergence loop that only exits on exact-commit review.

---

## 20. User Corrections as Labels

**Source:** `NEWINGESTHTHIS/Promps for reasinng over agents.txt`; Claude conversation, 2026-07-31

> "Practitioner self-improvement approaches repeatedly use the human's corrections as
> particularly strong evidence."

> "User corrections should be treated almost like labels."

A dedicated extraction pass for user corrections — find every point where the user:
- says no, contradicts a claim, says something was already known/documented
- repeats a previous instruction, asks why the agent did something
- stops/cancels an approach, redirects to a tool/source
- supplies information the agent should have retrieved
- expresses surprise that the agent does not know something

> "Then look 10-20 events backward from each intervention. That's probably one of your
> highest-value heuristics because your sessions have unusually rich explicit feedback."

**Not in contract:** the `owner_reaction` field captures corrections at the session level. The
"10-20 events backward" extraction is a within-session analysis that should happen during
distillation — the evidence packet should flag the correction points and their surrounding
context, not just record "explicit correction" as a verdict.

---

## 21. Mechanical Extraction Before Causal Interpretation

**Source:** `NEWINGESTHTHIS/Promps for reasinng over agents.txt`

> "Explicitly separate mechanical extraction from causal interpretation."

The mechanical extraction produces a structured timeline:
```
Exact commands repeated: 7x `npx tsx db/hangar/find.ts battery`
Same failure output repeated: 4x <signature>
Files repeatedly read: AGENTS.md (5 reads), hangar.ts (7 reads)
Files repeatedly edited: power_monitor.py (6 distinct edit cycles)
Edit oscillations: power_monitor.py threshold: 9.9 -> 10.5 -> 9.9 -> 10.2
User interventions: T=37 "No, that's already in the database"
Subagent duplication: parent searched battery, child repeated same search
Instruction encounters: AGENTS.md read at T=4, violation first occurs at T=37
```

> "Then hand that structured timeline plus the transcript to the reasoning model. That's much
> harder for a reviewer model to bullshit its way through."

**Not in contract:** the distillation prompt extracts `skills_fired`, `outcome`, and
`owner_reaction`, but does not produce the mechanical timeline (repeated commands, edit
oscillations, reread heatmaps, subagent duplication). These are cheap to compute
deterministically and would make the distilled rows far more useful for the examination
layer.

---

## 22. Self-Reflection Before Handoff

**Source:** `_incubator/scout/2026-07-23-obra-superpowers/source/docs/plans/2025-11-28-skills-improvements-from-user-feedback.md`

> "When done, BEFORE reporting back: Take a step back and review your work with fresh eyes. Ask
> yourself: Does this actually solve the task as specified? Are there edge cases I didn't
> consider? Did I follow the pattern correctly? If tests are failing, what's the ROOT CAUSE?
> What could be better?"

**Fix workflow latency improvement:** allow implementer to fix self-identified issues during
self-reflection, rather than reporting → dispatching fixer → fixer fixes → verifying.

**Not in contract:** the distiller is a post-hoc mechanical job, but the examination layer
that consumes distilled rows could include a "self-reflection signal" — did the agent under
review demonstrate self-reflection before handoff? The presence or absence of self-reflection
is a cheap signal for skill-influence quality.

---

## 23. Configuration Change Verification Gate

**Source:** Same skills-improvements document

**The failure:** "Subagent tested 'OpenAI integration.' Got status 200 responses. Reported
'OpenAI integration working.' BUT response contained `model: claude-sonnet-4-20250514` — was
actually using Anthropic."

**The gate:**
```
BEFORE claiming configuration change works:
1. IDENTIFY: What should be DIFFERENT after this change?
2. LOCATE: Where is that difference observable?
3. RUN: Command that shows the observable difference
4. VERIFY: Output contains expected difference
5. ONLY THEN: Claim configuration change works
```

**Not in contract:** the `outcome` field captures achieved/partial/failed/unknown, but the
"what should be different and where is it observable" framing is a specific examination
pattern. The evidence packet should preserve what the agent claimed was different, so the
examiner can check whether the claim was verified or asserted.

---

## 24. Mock-Interface Drift Prevention

**Source:** Same skills-improvements document

> "Mock derived from what buggy code calls, not from interface definition."

**The gate:**
```
BEFORE writing any mock:
1. STOP — Do NOT look at the code under test yet
2. FIND: The interface/type definition for the dependency
3. READ: The interface file
4. LIST: Methods defined in the interface
5. MOCK: ONLY those methods with EXACTLY those names
6. DO NOT: Look at what your code calls
```

**Not in contract:** this is a specific failure pattern the examination layer should flag —
agents that write mocks derived from their own buggy code rather than from interface
definitions. The `harm_cost` field could capture this as "wrong tool" but the specific pattern
is worth its own detector.

---

## 25. Skill Evaluation 6-Step Learning Loop

**Source:** `docs/workflows/skill-evaluation.md`

The replacement for the decommissioned session reviewer:

1. Build a complete, read-only candidate manifest in `agent-control-plane`
2. Declare the review corpus before judging usefulness
3. Give one bounded episode to each reader
4. Give a separate synthesizer the memos and coverage summary
5. Change only the implicated surface in `frozenSkillz`
6. Validate the exact diff and relevant repository checks

> "It is deliberately a qualitative learning loop, not a scorecard, gating system, or synthetic
> experiment."

> "Future ordinary deployments become the next evidence set; do not manufacture traffic, force
> activations, or schedule a monitor."

**Not in contract:** this is the examination layer the trace distillation pipeline serves.
The contract defers it ("skill-analysis contract, reframed: one assembly pipeline, two
examinations") but the 6-step loop is the specific shape the consumer takes.

---

## 26. The Vampire Survivors Harness: Evolutionary Reasoning Loops

**Source:** ChatGPT, 2026-07-23

A three-model harness with trace-based self-improvement:
- **Builder (Codex):** writes code
- **Leader (Luna Medium Fast):** sets strategy
- **Follower (ultra-fast VLM):** handles movement

> "Trace review must run as isolated sub-agents with fresh context and structured JSON output
> to prevent self-referential acceptance and hallucinated status."

**Key concepts:**
- Layered reflex/tactic policies with reflex (pure code) as base to handle VLM latency
- Autoresearch-style meta loop: one variable change per experiment, 3 eval runs, strict
  keep/revert against median survival time
- G0-G7 gates: progression from plumbing through distillation
- "Mechanism for genuine overnight improvement"
- Keep/revert discipline: strict for experimental changes

**Not in contract:** the "trace review as isolated sub-agents with fresh context" pattern is
a design constraint on the examination layer. The distilled store should support dispatching
isolated examination agents that get only the evidence packet, not the full session or prior
examination results, to prevent self-referential acceptance.

---

## 27. The "Orchestrator of Agentic Truth" Pattern

**Source:** Pieces annotation (persona), 2026-08-17

> "He has shifted from merely architecting 'diagnostic meshes' to actively building a 'Trace
> Distillation Pipeline' that functions as a self-auditing cognitive layer."

> "His workflow is defined by 'Aggressive Signal Extraction,' driven by an increasingly
> automated forensic oversight loop."

> "Fail-fast: forcing agents to run memory pre-checks before committing resources to heavy
> tasks. If an agent fails to provide meaningful, compact results, you treat it as a failure of
> methodology, not a failure of tools."

> "Aggressive Skepticism: You treat community-provided tools and PR-review bots with high
> suspicion."

**Not in contract:** this is the meta-pattern that motivates the entire pipeline. The
distilled store is the "self-auditing cognitive layer." The "fail-fast" and "aggressive
skepticism" attitudes are design principles for the examination layer — treat missing evidence
as a failure, not an absence.

---

## Summary: What the Contract Covers vs. What This Ledger Adds

| Concept | In contract? | In this ledger |
|---|---|---|
| Mechanical distillation job | Yes (core) | — |
| Navigation condensation + evidence packets | Yes | — |
| Two Postgres tables | Yes | — |
| Idempotent upsert + watermark | Yes | — |
| Abstention as first-class value | Yes | — |
| Ownership boundaries | Yes | — |
| Failure rules + stop conditions | Yes | — |
| The closed-loop feedback pattern | Deferred (consumer) | Section 1 |
| Multi-agent debate is a martingale | No | Section 2 |
| Builder vs. critic architecture | No | Section 3 |
| Retrospective compounding | No | Section 4 |
| The ceremony problem | `harm_cost` field only | Section 5 |
| Owner reaction as ground truth | `owner_reaction` field | Section 6 |
| Measurement loop with nothing to measure | No | Section 7 |
| ProjectBroadside circular workflow | No | Section 8 |
| External convergence systems | No | Section 9 |
| Anti-convergence | `indeterminate` value | Section 10 |
| Complexity-based routing | No | Section 11 |
| 7-step adversarial testing loop | Steps 3-6 only | Section 12 |
| Compliance lane graph | `harm_cost` enum only | Section 13 |
| Real-time shadow checkers | No (post-hoc only) | Section 14 |
| Typed node/edge ontology | Flat rows only | Section 15 |
| Atomic Bead tasking | `user_goal` one sentence | Section 16 |
| Heterogeneous swarm governance | `harness` field | Section 17 |
| Agentic CI / blast-radius PR gate | No | Section 18 |
| Letta reviewer architecture | Deferred | Section 19 |
| User corrections as labels | `owner_reaction` field | Section 20 |
| Mechanical extraction before interpretation | No | Section 21 |
| Self-reflection before handoff | No | Section 22 |
| Configuration change verification gate | No | Section 23 |
| Mock-interface drift prevention | No | Section 24 |
| 6-step learning loop | Deferred (consumer) | Section 25 |
| Vampire Survivors evolutionary loops | No | Section 26 |
| Orchestrator of Agentic Truth pattern | Implicit motivation | Section 27 |

---

## Recommended Next Steps

1. **Evaluate each section** for incorporation into the contract, explicit deferral, or
   rejection with rationale.
2. **The highest-signal additions** (by frequency of appearance across discussions):
   - Mechanical extraction before interpretation (Section 21) — cheap, deterministic, makes
     distilled rows immediately more useful
   - User corrections as labels with 10-20 event backward context (Section 20) — the highest-
     value heuristic in this corpus
   - The ceremony problem as a pattern, not just a field (Section 5) — skills that *enable*
     ceremony by providing workarounds for blocked resources
   - Multi-agent debate is a martingale (Section 2) — constrains the examination layer design
3. **The loop closure** (Section 1, 7, 8) — the contract stops at capture. The feedback path
   from distilled rows to skill changes to new sessions to distillation again is the "big
   circular" workflow. It needs its own contract or the pipeline is just a database that
   nobody reads.
