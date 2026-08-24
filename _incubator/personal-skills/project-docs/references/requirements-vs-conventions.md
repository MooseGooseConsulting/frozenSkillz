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

**"Breaks" means an outside rule is violated — not that reversing the choice
would be expensive.** Almost every implemented choice has things coupled to it by
now: swapping the store means a data migration, swapping the package manager
means relocking every workspace. That cost is real, and it is not a source.
Coupling is what a choice *acquires* after it is made; a requirement is what was
true *before* anyone chose. Ask the second question:

> **If it had been done the other way from the start, would anything outside our
> own precedent have objected?**

- **No** → Convention, however much work reversing it would now be. Record the
  coupling where it belongs — as a consequence in the decision record, or as a
  cost clause on the convention: `(chosen; alternative: Y; reversing now costs a
  data migration)` is honest, `required` is not.
- **Yes**, and you can name the API, schema, hardware fact, policy, contract,
  compliance rule, incident, upstream contract, or owner instruction →
  Requirement, with that as its source.

Coupling promoted to requirement is laundering with extra steps: it makes the
cost of change read as a law, and the next agent designs around it forever.

### The three legal exits for Unknown

1. **Find the record** — the decision note or ADR; `git blame` on the sentence,
   the PR that introduced it, the issue it closed; a commit message.
2. **Find a counterexample** — a place in the repo or the live system where X is
   *not* done and nothing broke. A counterexample refutes precedent; it does not
   overrule a source. Rule out the sources first.

   - **If the "must" traces to an authority** — policy, contract, compliance
     rule, an owner or operator instruction, a rule an incident produced, or an
     upstream project's contract — the instance does not demote it. What you have
     found is most likely an **existing violation**. Report it as one; do not
     quietly widen it into permission.
   - **If the rule is conditional or probabilistic**, "nothing broke" is only
     evidence when the instance was actually exposed to the failure the rule
     prevents. A backup rule is not refuted by a year without a restore.
   - **If the rule is defense in depth**, it will look redundant every day the
     control in front of it holds. That is the rule working, not the rule being
     unnecessary.
   - **State the claim before you test it.** "Handlers validate input at the
     boundary" is not refuted by an internal helper that never sees untrusted
     input — that instance is outside the claim.

   When the only support is this repo's own precedent, and the instance is
   genuinely inside a precisely stated claim, one counterexample demotes the
   "must" to a convention on the spot. That is the case this exit is for.
3. **Ask the owner** — batch the questions; record the answer where the sentence
   lives.

**The illegal exit:** generating a reason. A plausible rationale you produced
yourself is not evidence, and writing it down converts a habit into a law for
every reader after you.

---

## Where each state lives (default stack)

| State | Home | Form |
|---|---|---|
| Requirement | `architecture.md` → **Constraints and Conventions**, constraints list (arc42 §2 analogue), or inline in the section it governs | one line + source |
| Invariant | `architecture.md` → Architectural Invariants | rule + failure mode it prevents |
| Convention | `architecture.md` → **Constraints and Conventions**, conventions list; a component doc; or `docs/workflows/` | one line + alternative (+ reason or decision link) |
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
> ✓ "The orchestration API cannot declare a second disk (required: its storage
> schema has one boot-volume field — linked). The template supplies it (chosen;
> alternative: attach after clone with one host command; not evaluated when the
> storage nodes were built)."

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

Only **normative** uses classify — sentences that tell someone working here what
they are obliged to do. The same words appear in prose that obliges no one:

- a question — "*should* findings be advisory only?" in Open Architecture Questions;
- a count or measurement — "*only* three services exist";
- a quotation or a historical note — "the 2026-05 incident report said hosts *must* match";
- a statement about an outside system's behavior — "the API *always* returns 404
  for a missing key" (a fact to cite as a source, not a rule addressed to us).

Mark these **n/a** on the audit row and leave the prose alone. `n/a` is a
classification, not a fourth marker: nothing is written into the doc for it and
it never triggers a rewrite. But a lexical match that describes *our own*
practice is not n/a — "we *always* pin digests" is a modal claim about this repo
and classifies normally.

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

Do not invent sources. **Source and reason are different fields and they fail
independently** — a requirement can have a source and no recorded reason, and
that is a complete entry.

When the owner says "must" and cannot say why, the question is whether the owner
is *imposing* the rule or *relaying* one:

- **Imposing** ("use pnpm") — the owner is the authority, so the owner is the
  source. Record it as a Requirement: `[OWNER]` + `(required: owner, <date>;
  reason not recorded)`. You have already taken the "ask" exit; record the
  non-answer and move on. Do not backfill a reason, and do not demote the rule
  because the reason is missing.
- **Relaying** ("I think CI requires pnpm") — the owner is not the source; the CI
  config is, if it says so. That is Unknown until you find the record: mark it,
  take the "record" exit, and if nothing backs it, it is a convention.

If the phrasing does not settle which one it is, that is the question to batch:
"is that your rule, or something you believe is imposed on us?"

---

## Audit pass (retrofit on existing docs)

Run when reviewing an existing authority doc, when reconciling, or on request.
Collection is half mechanical and half a reading pass; everything after
classification is mechanical again.

1. **Collect — two passes.** The modality words are half the surface; a grep
   alone cannot implement this audit.
   1. **Modal pass (mechanical).** Grep the doc for the modality words above.
   2. **Declarative pass (read it).** Practice and architectural choice written
      as plain fact carry no modal word at all — "the service uses Redis,"
      "templates supply the data disk," "config lives in `X/`." No grep finds
      them, and they are the *central* laundering form: `we do X` read back as
      `X is required`. Read the doc for present-tense claims about how this
      repository builds, names, stores, deploys, or lays things out, and about
      what its components are made of. Each is a hit; each needs its source or
      its alternative exactly as a "must" does. Two bounds keep this finite: a
      claim purely descriptive of an outside system is not our choice and is not
      collected (it is a candidate *source*), and an inventory is not a claim —
      collect the *how* and *why* attached to a component, not the row that
      names it.

   One row per hit: `sentence · file:line · state · source-or-alternative · action`.
2. **Classify.** For each hit apply the test. Fill `state` with R / C / U — or
   n/a for a non-normative use of a trigger word (see **Modality words**), which
   closes the row with no further action.
3. **Resolve U in exit order.** Record → counterexample → ask. Batch the asks
   into one message to the owner. Do not proceed to step 4 for a U until an exit
   has been *taken* (not merely chosen).
4. **Rewrite — only where editing was authorized.** The request sets the mode,
   not the findings.
   - **Review-only** (a review, critique, or documentation-authority audit was
     what was asked for): put the rewrites *in the report*, as proposed
     replacement lines. Change no file. This is `SKILL.md` → the skill does not
     create or rewrite docs unless the user asks, and `<smallest_change>`'s
     distinction between proposed and applied.
   - **Edit authorized** (authoring, repair, migration, or an explicit "fix
     it"): rewrite each hit in place into one of the three template forms. Fused
     "so" clauses split into their fact and their choice.

   When in doubt, propose. A demotion the owner has not seen is not yours to
   commit.
5. **Report.** Findings by state. Every R→C demotion is a finding in its own
   right — it means an agent has been obeying something optional. List them; the
   owner decides whether any should be *promoted* to a requirement by fiat (which
   is legal, and then the owner is the source).

The audit is complete when every collected hit — from both passes — has been
classified, and:

- in **edit-authorized** mode, each R / C / U hit sits in a sentence carrying a
  source, an alternative, or an Unknown mark with an exit taken;
- in **review-only** mode, each such hit has its proposed rewrite in the report;
- n/a hits are closed by the classification alone.

A doc whose modal sentences are all marked but whose declarative choices were
never collected has not been audited.

### Report block

```text
### Modality findings
- required, no source — [sentence] at [file:line]; source found: [x] / exit: [record | counterexample | ask]
- convention written as must — [sentence] at [file:line]; alternative: [y]; demoted
- fused so-clause — [sentence] at [file:line]; split into: [fact (required: …)] + [choice (chosen; alternative: …)]
- unsourced practice (no modal word) — [sentence] at [file:line]; alternative: [y] / source: [x]
- counterexample vs a sourced rule — [sentence] at [file:line]; source [s] stands; instance at [file:line] is a violation, not a demotion
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

The audit's *modal* pass is a grep. A repository that wants a gate can run one:
flag any line containing a modality word that carries neither a marker
(`required:` / `chosen` / `not established`) nor a link on the same line. That is
a five-line script and it is *enforcement tooling* — this skill describes it and
does not build it unless the owner asks (see `SKILL.md` → smallest change).

Such a gate is a floor, not the audit. It cannot see the declarative pass — a
laundered convention written as plain fact contains no word for it to match — and
it cannot tell a normative "must" from a question. A green gate is not a
completed audit, and this file's completion condition is the one that counts.

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

- **Not RFC 2119 everywhere.** Only normative claims classify — what this repo
  requires, and what it chose. Questions, counts, quotations, status labels,
  routes, and descriptions of outside systems are marked n/a and left alone.
- **Not an ADR for every choice.** Below the ADR threshold an inline
  `(chosen; alternative: …)` is the whole requirement.
- **Not a reason for stripping rules.** A demoted convention is still the
  convention; agents still follow it by default. The change is that they now
  know it *is* a default.
- **Not a licence to invent alternatives either.** "Alternative: none considered"
  is a valid, honest entry. The road not taken is recorded, not manufactured.
