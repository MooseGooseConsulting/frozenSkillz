# Requirements vs Conventions — the Modality Procedure

Authority docs are read later by agents that have only the text. The single most
common way such a doc becomes unsafe is not a missing section — it is a **"must"
that was never a must**: a past choice, recorded as a fact, read back as a law.

This file is the procedure for keeping the two apart. It applies to every
authority document and every living-overflow doc, in every mode of this skill
(write, review, reconcile, migrate). The status labels in
`architecture-md-guide.md` keep *shipped* from being confused with *proposed*;
this procedure keeps *required* from being confused with *chosen*. They are
orthogonal axes on the same claims.

---

## The Modality Principle

> An authority doc may record what was chosen, but it must not let the agent
> confuse what was chosen with what was required.

Every "must" wears a source. Every choice names its alternative. Anything else is
marked unknown and routed — never filled in.

---

## Why this is a procedure and not a reminder

Three facts make the failure structural, so no amount of "be careful" fixes it:

1. **The information is not in the text.** From "we do X" alone, a reader cannot
   tell whether X was required or preferred — the same sentence is consistent
   with both. This is the identifiability problem known from constraint learning:
   many (constraint, preference) pairs explain the same trajectory. Intelligence
   does not recover what was never recorded.
2. **Agents default to the strong reading.** Absent modality, honoring a
   constraint looks like diligence and relaxing one looks reckless. A more capable
   model makes it *worse*: it can generate a plausible rationale on demand that
   makes the convention feel load-bearing.
3. **The engineering canon already separates them.** arc42 puts *constraints*
   (rules imposed on you — "we must use the company-managed Postgres platform")
   in one chapter and *decisions* (choices you made — "we will use Postgres")
   in another, with the instruction: if it is not truly non-negotiable, it is not
   a constraint. ADRs have carried "alternatives considered" since 2011 so the
   *why-not* survives. This procedure applies that canon at sentence granularity,
   because the sentences that get laundered are the small ones below any ADR
   threshold.

Chesterton's fence says do not *remove* what you do not understand. This is the
mirror rule: do not *enshrine* what you do not understand. Both fail at the same
missing step — go find out why.

---

## Vocabulary

Three states. Every modal sentence in an authority doc is in exactly one.

| State | Definition | What it must carry | RFC 2119 voice |
|---|---|---|---|
| **Requirement** | Imposed from **outside the repo's own precedent**: an API or schema that lacks the field; a hardware or physical fact; an explicit owner/operator instruction; a policy, contract, or compliance rule; an incident that produced a rule; an upstream project's contract. | Its **source**, inline or one link away. | MUST / MUST NOT |
| **Convention** | **Chosen.** Its only support is "we do it this way," "the doc says so," or "we did it last time." | The **alternative not taken**, and the reason if known — inline, or a link to the decision note. | SHOULD / "we do X" |
| **Unknown** | Modality not yet established. | Explicit marking, plus **one of the three exits taken** (below). | "current practice; not established whether required" |

Two refinements:

- **A convention becomes a requirement when an authority imposes it.** "Always use
  pnpm" is a convention until the owner says "always use pnpm" — then the owner
  is the source, and it is cited as such (`required: owner, 2026-08-14`). arc42
  lists coding standards under constraints for exactly this reason. The source
  is what changes, not the test.
- **An invariant is a self-imposed requirement.** The owner is the authority; the
  named failure mode is the reason (see `architecture-md-guide.md` →
  Architectural Invariants). Invariants already require a *why*; this procedure
  requires the same of every other "must".

### The test

**What breaks if we don't?**

- Something breaks, or someone with authority objects → Requirement. Name it.
- Nothing breaks; it would just be different → Convention. Name the alternative.
- You cannot answer → Unknown. Take an exit. Do not answer for them.

### The three legal exits for Unknown

1. **Find the record** — the decision note or ADR; `git blame` on the sentence,
   the PR that introduced it, the issue it closed; a commit message.
2. **Find a counterexample** — a place in the repo or the live system where X is
   *not* done and nothing broke. One counterexample demotes a "must" to a
   convention on the spot.
3. **Ask the owner** — batch the questions; record the answer where the sentence
   lives.

**The illegal exit:** generating a reason. A plausible rationale you produced
yourself is not evidence, and writing it down converts a habit into a law for
every reader after you.

---

## Where each state lives (default stack)

| State | Home | Form |
|---|---|---|
| Requirement | `architecture.md` → **Constraints** (arc42 §2 analogue), or inline in the section it governs | one line + source |
| Invariant | `architecture.md` → Architectural Invariants | rule + failure mode it prevents |
| Convention | `architecture.md` → **Conventions**, a component doc, or `docs/workflows/` | one line + alternative (+ reason or decision link) |
| Decision with consequences | `docs/decisions/` (ADR / MADR) | context · options considered · outcome · consequences |
| Unknown | wherever the sentence is | marked, with the exit taken or `[OPEN]` |

Below the ADR threshold, an inline `(chosen; alternative: …)` is sufficient. The
point is not ceremony; it is that the road not taken is *named* where the reader
will meet the choice.

When the repository declares a different stack, keep the states and put them
where that stack keeps constraints and decisions. The states are not tied to
these filenames.

---

## Writing rules

### The so-clause rule

Never join a fact to a choice with **so / therefore / hence / thus / which is why
/ must therefore** without naming the alternative or linking the decision.

> ✗ "The orchestration API cannot declare a second disk, **so** the template
> supplies it."
>
> ✓ "The orchestration API cannot declare a second disk (**required**: its
> storage schema has one boot-volume field — linked). The template supplies it
> (**chosen**; alternative: attach after clone with one host command; not
> evaluated when the storage nodes were built)."

Every clause of the ✗ sentence is true. That is what makes it dangerous.

### Sentence templates

- Requirement: `X. (required: <source>)` or `X — required by <source>.`
- Convention: `We do X. (chosen; alternative: Y; because Z)` or `(chosen; alternative: Y; reason not recorded — see <decision>)`
- Unknown: `X is current practice; whether it is required is not established (<exit taken> / [OPEN]).`

Markers are plain text so they survive every renderer and every grep. Do not
invent a fourth marker.

### Modality words

The words that trigger the rule: **must, must not, cannot, can't, never, always,
only, required, requires, needs to, has to, mandatory, forbidden, so, therefore,
hence, thus, which is why**. When you write one, classify.

Do not respond by deleting modality words to dodge the rule. A doc with no
"must" in it has not solved anything; it has hidden the requirements too.

---

## Authoring pass (extends `write-workflow.md`)

Add to the architecture.md interview:

- "Which of these could you change tomorrow without asking anyone?" → conventions.
- "Which would break something, or violate someone's rule — whose?" → requirements; the *whose/what* is the source.
- For each "must" the owner states: "What breaks if we don't?"
- For each choice: "What else did you consider?" — record it even if the answer is "nothing"; *"alternative: none considered"* is honest and useful.

Drafting: apply the sentence templates as you write, not afterwards. Provenance
tags (`[OWNER]` / `[INFERRED]` / `[OPEN]`) already govern *who said it*; the
modality marker governs *what kind of statement it is*. A Requirement needs
both a provenance tag and a source; `[OWNER]` alone is the source only when the
owner is the imposing authority.

Do not invent sources. If the owner says "must" and cannot say why, it is
`[OWNER]` + Unknown, and the exit is "ask" — which you have just done; record
the non-answer and move on. Do not backfill a reason.

---

## Audit pass (retrofit on existing docs)

Run when reviewing an existing authority doc, when reconciling, or on request.
It is mechanical up to the classification step and stays mechanical afterwards.

1. **Collect.** Grep the doc for the modality words above. One row per hit:
   `sentence · file:line · state · source-or-alternative · action`.
2. **Classify.** For each hit apply the test. Fill `state` with R / C / U.
3. **Resolve U in exit order.** Record → counterexample → ask. Batch the asks
   into one message to the owner. Do not proceed to step 4 for a U until an exit
   has been *taken* (not merely chosen).
4. **Rewrite.** Each hit into one of the three template forms, in place. Fused
   "so" clauses split into their fact and their choice.
5. **Report.** Findings by state. Every R→C demotion is a finding in its own
   right — it means an agent has been obeying something optional. List them; the
   owner decides whether any should be *promoted* to a requirement by fiat (which
   is legal, and then the owner is the source).

The audit is complete when every modality word in the doc sits in a sentence
that carries a source, an alternative, or an Unknown mark with an exit taken.

### Report block

```text
### Modality findings
- required, no source — [sentence] at [file:line]; source found: [x] / exit: [record | counterexample | ask]
- convention written as must — [sentence] at [file:line]; alternative: [y]; demoted
- fused so-clause — [sentence] at [file:line]; split into: [fact (required: …)] + [choice (chosen; alternative: …)]
- unknown, unresolved — [sentence] at [file:line]; asked owner [date]
```

---

## Reader-side rule (AGENTS.md)

The authoring and audit passes fix the docs. The reader-side rule protects
against every doc that has not been fixed yet, and against docs outside the
stack. It is one hard rule, and it earns its AGENTS.md line because it is needed
often, costly to get wrong, and cannot be deferred to a lazy read:

> A "must" whose only source is precedent is a convention. Before planning
> around any constraint, find its source, a counterexample, or ask — never
> generate a reason for it.

Place it beside the existing "If a task crosses a goal, anti-goal, pillar, or
invariant: stop and surface it." It is the same kind of line.

---

## Review findings (extends `review-checklist.md`)

Structural (wrong agent behavior):

- **Laundered convention** — a fact fused to a choice with no alternative named;
  or a convention written as MUST; or a MUST without a source.
- **Fabricated source** — a rationale with no owner phrasing, link, or record
  behind it (the reader-side illegal exit, committed by the writer).
- **Unknown left unrouted** — a sentence marked (or obviously) unknown with no
  exit taken.

These sit beside "Fabricated constraints" — they are its quieter siblings.
Fabrication invents a rule; laundering promotes one.

---

## Mechanical check (optional; not built by this skill)

The audit's step 1 is a grep. A repository that wants a gate can run one: flag
any line containing a modality word that carries neither a marker (`required:` /
`chosen` / `not established`) nor a link on the same line. That is a five-line
script and it is *enforcement tooling* — this skill describes it and does not
build it unless the owner asks (see `SKILL.md` → smallest change).

If the repository adopts a linked-doc system such as lat.md, sources become
`[[wiki links]]` to constraint or decision sections and the link checker
verifies they resolve. That supplies plumbing for this procedure; it does not
replace it — a graph of unmarked "must" sentences is still a graph of laundered
conventions.

---

## Worked example (generic, from a real case)

**The doc said** (all true, in three places): *"Extra disks are template inputs;
the API cannot declare them."* · *"…the storage templates, which supply the data
disk the API cannot declare."* · *"The API can resize only the boot volume; its
storage schema has no additional-volume field, so that second disk remains a
template input."*

**What a later agent did:** planning a different node class, it carried
"templates must supply the disk" into the plan as a requirement, and when
challenged, produced a reason ("a node is born with its disk") — then admitted it
could not reconstruct the original decision, because no reason was written down.

**The audit:**

| sentence | state | finding | rewrite |
|---|---|---|---|
| "the API cannot declare them" | R | source present in prose (schema has one boot-volume field); link it | `(required: <API storage schema>)` |
| "template inputs" / "which supply" / "so … remains a template input" | C written as fact→choice | so-clause; alternative never named; original reason unrecorded → exit: ask | `(chosen; alternative: attach after clone with one host command; not evaluated when the storage nodes were built — owner asked 2026-08-15)` |

**What changed:** the requirement is now sourced, the choice now names its
alternative, and the next agent planning around it sees a choice it may make
differently — instead of a law it must design around. Nothing was deleted;
three parentheticals were added.

---

## What this procedure is not

- **Not RFC 2119 everywhere.** Only modal sentences classify. Descriptive prose,
  status labels, and routes are untouched.
- **Not an ADR for every choice.** Below the ADR threshold an inline
  `(chosen; alternative: …)` is the whole requirement.
- **Not a reason for stripping rules.** A demoted convention is still the
  convention; agents still follow it by default. The change is that they now
  know it *is* a default.
- **Not a licence to invent alternatives either.** "Alternative: none considered"
  is a valid, honest entry. The road not taken is recorded, not manufactured.
