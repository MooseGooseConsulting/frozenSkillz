# How to Write an architecture.md

`architecture.md` explains the app's technical shape and direction.

It is aspirational and operational. It says how the app is being put together and structured: what it is built in; what sidecars, services, stores, queues, or integrations are involved; what the approach is; what the key differentiator is; what is current, planned, candidate, and deferred; and where deeper technical details live.

The real problem with this document is not aspiration. The problem is **unlabeled aspiration** — and its quieter twin, **unlabeled choice**.

---

## The Load-Bearing Principle

> architecture.md may describe where we are going, but it must not let the agent confuse where we are going with what already exists.

Every forward-looking claim wears a status label. The labels are the seam between strategy and code.

## The Modality Principle

> architecture.md may record what was chosen, but it must not let the agent confuse what was chosen with what was required.

Every "must" wears a source; every choice names its alternative; anything else is marked unknown and routed. Status labels keep *shipped* apart from *proposed*; modality keeps *required* apart from *chosen*. Two axes, same claims. The full procedure — vocabulary, the test, the three exits, the audit — is `requirements-vs-conventions.md`.

---

## What architecture.md Owns and Does Not Own

`architecture.md` owns:

- the chosen technical approach
- target architecture
- current implementation shape
- major components and boundaries
- runtime / deployment model
- sidecars, services, queues, stores, integrations
- technical differentiators
- architectural constraints (each with its source), conventions (each with its alternative), and invariants
- links to ADRs and detailed component docs

`architecture.md` does not own:

- project purpose and anti-goals → `NORTH_STAR.md`
- current task handoff → GitHub Issues and/or `docs/plans/`
- long decision rationale → `docs/decisions/`
- deep subsystem documentation → `docs/components/` or topic living docs
- long procedures → `docs/workflows/`
- completed work archives → **git** (do not create `docs/history/` for this)

When component detail bloats architecture.md, move it to `docs/components/` or a topic living doc. When a decision deserves its own context-rationale-consequences write-up, move it to `docs/decisions/` and add it to the ADR Index.

---

## What Goes In, What's Optional, What Accretes

| Section | When to include | When to skip or defer |
|---|---|---|
| Architecture Thesis | Always once the project has any technical shape. | Never skip on a project with code. |
| Status Legend | Always. Even a thesis-only doc benefits from it. | Never skip. |
| System Shape (table with status) | Always once there's more than one component. | Single-component projects can describe the shape in prose. |
| Key Technical Differentiator | When the project's value depends on a specific technical choice. | Generic CRUD apps without architectural distinctiveness. |
| Target Architecture | When the project has a deliberate target shape that differs from current. | If current == target, the Current Architecture section suffices. |
| Current Architecture | Always once code exists. | Pre-implementation projects can defer. |
| Major Components (table) | When the project has more than two named components. | Single-component projects skip. |
| Constraints and Conventions | As soon as the doc contains a "must" or a "we always." Requirements with sources; conventions with alternatives. | A doc with no modal claims yet. Do not pad it — an empty section is honest. |
| Architectural Invariants | When the project has rules that hold across all components. | Early projects without earned invariants leave the section empty until experience produces them. |
| ADR Index | When `docs/decisions/` has ADRs. | If no ADRs exist yet, the section appears when the first one is written. |
| Open Architecture Questions | When undecided choices affect downstream work. | If everything is decided, the section is empty. |
| Links | Always once neighboring docs exist. | Solo doc state only. |

**Minimum viable architecture.md: Architecture Thesis + Status Legend + System Shape table.**

---

## The Status Legend

Use exactly these four labels:

- **Current** — implemented or directly reflected in the repo.
- **Planned** — decided direction, not fully implemented.
- **Candidate** — plausible option, not decided.
- **Deferred** — intentionally not being built now.

For declarative or GitOps repos (infrastructure-as-code, Kubernetes manifests, Terraform/OpenTofu), read "implemented or directly reflected in the repo" as *applied to the live system* (reconciled, present in cluster or remote state), not merely that a manifest has been authored. An authored-but-unapplied manifest is **Planned**, not Current. The four labels do not change; only their reading sharpens for repos where the manifest in the tree is not yet the running state.

Every forward-looking claim wears one. Anything in a table or diagram that represents future-state architecture must have a status label. Prose that describes future-state must inline the label, like: *"The Guardian runtime (Deferred) may inspect PRs..."*

### Rules

- **Four labels only.** Do not invent "In Progress," "Stretch," "Maybe." The four labels cover all cases. If a thing is partly implemented, label it Current and note the gap in prose.
- **Labels apply to claims, not docs.** A single document can mix Current, Planned, Candidate, and Deferred items. That is the point.
- **Promote and demote deliberately.** When a Planned item ships, change the label to Current in the same PR. When a Candidate is rejected, change to Deferred and note the rationale.

### Failure mode

Unlabeled aspiration. A sentence like "The system uses Redis for caching" reads as Current. If Redis isn't actually deployed, the agent will treat it as available. The label must be present, even inside prose: *"The system uses Redis for caching (Planned)."*

---

## System Shape Table

A short table with three columns: Area, Status, Approach.

| Area | Status | Approach |
|---|---|---|
| (a major area of the system) | Current / Planned / Candidate / Deferred | (one-line description) |

### Rules

- **Five to twelve rows.** Fewer suggests the shape isn't decomposed. More suggests this should be in `docs/components/`.
- **One line per row in the Approach column.** If you need a paragraph, move that area to `docs/components/` and link.
- **Every row carries a status.** No exceptions.

---

## Major Components Table

When the project has named components (modules, services, subsystems), enumerate them:

| Component | Status | Responsibility | Detail |
|---|---|---|---|
| (name) | Current / Planned / Candidate / Deferred | (one-line responsibility) | (link to `docs/components/X.md`) |

### Rules

- **Detail links go to `docs/components/`.** Top-level architecture.md is the index, not the deep dive.
- **Components without a Detail link are suspect.** Either the component is too small to need its own doc, in which case it shouldn't be in this table, or its doc hasn't been written.

---

## Constraints and Conventions

Two short lists, kept apart on purpose. This is arc42's constraints-vs-decisions split at sentence granularity.

**Constraints** — requirements imposed from outside the repo's own precedent. One line each, with the source inline or one link away:

- (rule) — required: (API/schema limit · hardware fact · owner instruction, dated · policy · incident · upstream contract)

**Conventions** — practices this project chose. One line each, with the alternative not taken and, if known, the reason or a decision link:

- (practice) — chosen; alternative: (…); because (…) / reason not recorded — see (decision)

### Rules

- **The test is "what breaks if we don't?"** Something breaks or someone with authority objects → constraint, name it. Nothing breaks → convention, name the alternative. Cannot tell → mark it unknown and take an exit (record · counterexample · ask). See `requirements-vs-conventions.md`.
- **Never fuse a fact to a choice with "so."** "The API cannot declare X, *so* the template supplies it" is a true sentence that will be read as a law. Split it: the fact with its source, the choice with its alternative.
- **A convention promoted by the owner is a constraint** — and the owner (dated) is its source. Promotion is legal; silent promotion by a reader is not.
- **"Alternative: none considered" is a valid entry.** Record the road not taken; do not manufacture one.
- **Do not strip modality words to dodge the rule.** A doc with no "must" has hidden its requirements, not resolved them.

### Failure mode

The laundered convention. A past choice is written as a fact ("extra disks are template inputs"), a later agent reads it as a requirement, designs the next system around it, and — when challenged — invents a reason for it. Nothing broke; it just would have been different. The fix is three parentheticals, not a rewrite.

---

## Architectural Invariants

These are the rules the agent enforces when touching the system. Invariants are stronger than working rules: violating an invariant is a structural problem, not a style problem. An invariant is a *self-imposed* requirement — the owner is the authority and the named failure mode is the reason — so it obeys the same modality rule as everything else.

### Rules

- **Invariants must be earned.** A project on day one rarely has invariants. They emerge from lived experience.
- **Each invariant should be checkable.** "The skill must not pretend to be the Guardian runtime" is checkable (does the skill use Guardian vocabulary, run CI, block PRs?). "We value clean code" is not.
- **Invariants name the failure mode they prevent.** Why is this invariant in place? What goes wrong if it is broken?

### Failure mode

Invariants without rationale. The agent reads "Use TypeScript everywhere" without context and applies it to a generated script in a place where Bash would be obviously better. The invariant should say *why*.

---

## ADR Index

A small table that points at `docs/decisions/`:

| ADR | Status | Summary |
|---|---|---|
| `docs/decisions/0001-X.md` | accepted / proposed / superseded | (one-line summary) |

### Rules

- **Status values: proposed, accepted, deprecated, superseded.** These are the standard ADR statuses; do not invent variants.
- **Summary is one line.** The ADR file itself holds the context, decision, rationale, alternatives, consequences.
- **Every architecturally significant decision gets an ADR.** If a decision is "buried" in `architecture.md` prose with no ADR, that is a structural finding.

---

## Open Architecture Questions

A bulleted list of questions that affect downstream work but are not yet decided.

### Rules

- **Each open question should have an owner or a triggering event.** "Should we use Redis?" is vague. "Should we use Redis once cache hit rate exceeds X?" is concrete and resolvable.
- **When a question is answered, move it to an ADR and remove it from this section.**
- **A long-stale Open Questions list signals that the project has stopped revisiting its architecture.** Flag it.

---

## Review Lanes

When reviewing architecture.md, check four lanes separately:

| Lane | Question |
|---|---|
| **Current** | What exists now? Is it accurately described? |
| **Target** | What are we intentionally building toward? Are the labels right? |
| **Candidate** | What is under consideration but not decided? Is the rationale captured? |
| **Deferred / rejected** | What are we intentionally not doing now? Is the reason recorded? |
| **Modality** | Of everything stated as a "must": which are required (source?) and which are chosen (alternative?)? Run the audit pass in `requirements-vs-conventions.md`. |

---

## Architecture Problems to Flag

When reviewing, flag:

- planned architecture written as if already implemented
- candidate approach written as if accepted
- a "must" with no source, or a convention written as a must (laundered convention)
- a fact fused to a choice with "so / therefore" and no alternative named
- a rationale with no owner phrasing, link, or record behind it (fabricated source)
- current implementation missing from the system map
- technical differentiator described only in product language
- ADR-level decision buried in prose without a decision record
- component detail bloating the top-level architecture doc (move to `docs/components/`)
- roadmap material mixed into architecture without status labels
- old architecture left in place without being marked superseded
- invariants that are values statements rather than checkable rules
- empty ADR Index alongside prose-heavy architectural decisions

---

## What the Guardian Does with Each Section

| Section | Guardian asks | On violation |
|---|---|---|
| Architecture Thesis | "Does this PR contradict the project's technical thesis?" | Surface; the thesis may need revision in NORTH_STAR.md first. |
| Status Legend | "Are status labels preserved in this PR?" | Hard-block on PRs that remove or change labels without rationale. |
| System Shape / Components | "Does this PR add a Current item that was previously Planned, or break a Current item back to Planned?" | Update the status label in the same PR. |
| Constraints and Conventions | "Does this PR add a 'must' without a source, or treat a listed convention as a constraint?" | Surface. Require the source, or demote to convention with its alternative. |
| Architectural Invariants | "Does this PR violate an invariant?" | Soft-block with citation. Invariants are stronger than working rules. |
| ADR Index | "Does this PR make an architecturally significant decision without writing an ADR?" | Soft-block. Require the ADR. |
| Open Architecture Questions | "Does this PR implicitly answer an open question without resolving it?" | Surface the implicit answer; require an ADR. |

---

## Common Failure Modes

**Unlabeled aspiration.** The most common failure. Future-state claims are written as if Current. The agent reads them and treats them as fact. The fix is mechanical: add the label.

**The laundered convention.** The second most common, and the harder to see, because every sentence in it is true. A choice is recorded as a fact ("extra disks are template inputs"); a later agent reads it as a requirement; the next system is designed around a constraint nobody imposed; and when asked why, the agent supplies a reason that was never written down. The fix is mechanical too: source the requirement, name the alternative to the choice, mark and route the unknown. Procedure in `requirements-vs-conventions.md`.

**The code inventory creep.** architecture.md grows into a description of every file. The diff between architecture.md and a `tree` of the repo shrinks toward zero. The fix is to push detail down into `docs/components/` and keep the top-level doc strategic.

**The decision buried in prose.** A consequential choice (Redis vs. SQLite, monolith vs. services, sync vs. async) is mentioned in passing without a decision record. The rationale is lost; the decision is unreviewable. The fix is to write the ADR and link from the ADR Index.

**The orphaned target.** A Target Architecture diagram is drawn once, then never updated. Three months later, the actual implementation has diverged. The agent reads the diagram and acts on it. The fix is to keep the diagram in sync or remove it.

**The differentiator buried in product language.** The Key Technical Differentiator section describes user benefits instead of technical structure. "Faster for users" is not a differentiator; "in-memory column store with sub-millisecond lookup" is.

**The empty Invariants section on a mature project.** A project with months of history and no invariants has either captured them somewhere else (in which case move them) or hasn't reflected on what its rules actually are.

---

## When architecture.md and Downstream Docs Disagree

Authority flows from NORTH_STAR.md down. architecture.md derives from intent.

- If `architecture.md` describes a technical approach that contradicts a NORTH_STAR anti-goal, **NORTH_STAR wins**. architecture.md is updated, or NORTH_STAR is revised consciously.
- If `architecture.md`'s Current claims disagree with the actual code, **the code wins**. architecture.md is updated.
- If `architecture.md` and an active Issue/plan disagree about what's in flight, **architecture.md's Current/Planned labels win** for technical truth; the Issue/plan should align (or architecture is deliberately revised first).
- If `AGENTS.md` references architecture status labels that don't exist or have been renamed, **architecture.md wins**; AGENTS.md is updated.

architecture.md derives from NORTH_STAR; everything downstream of architecture.md derives from architecture.md.
