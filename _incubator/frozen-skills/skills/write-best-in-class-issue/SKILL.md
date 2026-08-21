---
name: write-best-in-class-issue
description: >-
  Author a GitHub issue that is safe to act on later by a human or an agent:
  outcome-first, evidence-cited, every "must" either sourced or marked as a
  choice, with testable acceptance. Use when creating or substantially revising
  any issue; it routes design, governance, epic, and proposal work to a full
  template and bug reports, bumps, and operational tasks to terse modes. Do not
  use for PR descriptions, commit messages, or issue comments.
---

# Write a Best-in-Class Issue

A best-in-class issue makes a piece of work **safe to act on later** — by a human
*or* an agent. It is not a long issue. It is a structured one: outcome-first,
evidence-cited, with explicit boundaries and testable acceptance — and it carries
the status of every claim it makes (shipped or proposed, required or chosen), so a
later reader never has to guess. The reference model is the kind of issue that
designs a reviewer, a capability, or a multi-part build (for example: a
semantic-reviewer design issue, a storage-fabric proposal, or a build/CI
coordination epic).

## Step 1 — Pick the mode (do this first)

Match depth to the issue's risk. Over-applying the full template to a one-line
bump is the failure mode this skill exists to prevent.

| Issue type | Mode | Apply |
|---|---|---|
| Design / governance / epic / proposal | **Full** | All 8 beats, with 2/5/6 conditional (see below) |
| Bug report (human- or agent-authored) | **Partial** | Outcome, the gap, acceptance; the hard constraint (with its source) only when a real external boundary exists — an ordinary bug with no such boundary skips it rather than inventing one |
| Already-decided implementation, or a low-risk open design question — a feature, refactor, test, or doc change | **Partial** | Outcome, what changes (or the open question, marked Unknown per Step 2), acceptance; a hard constraint only when a real boundary exists |
| Bump / one-line operational — **no live mutation** | **Minimal** | Title + Acceptance + Rollback + a linked evidence source only |
| Bump / operational that **mutates a live running system** (control-plane roll, service restart) | **Partial** | Outcome, the live-mutation boundary as the hard constraint, acceptance, and Rollback (as in Minimal); a gap section only when the mutation is fixing an actual defect |

The Minimal/Partial line is **"does it mutate a live running system,"** not "is it a bump." A
pin, digest, or manifest change consumed later is Minimal; a version bump that rolls the live
control plane is Partial.

Route through the table first. The Minimal fallback is for non-mutating operational items
only — a bug report is Partial even when it designs nothing. If an issue does not design,
coordinate, or propose something consequential, **do not use Full**. When unsure, ask the
operator which mode before drafting.

### Conditional beats in Full mode

Beats 2, 5, and 6 are **conditional**, not universal — verified against real issues:

- **Beat 2 (sequencing)** — include when the issue is *blocked on* something external, or when it coordinates parts that have their own internal ordering or dependencies. A coordination epic that decides nothing and has no internal ordering has no sequencing to state.
- **Beat 5 (activation gate)** — include whenever the capability the issue describes will eventually be activated or deployed, even when this issue itself only designs it; gate that future activation on the conditions this issue defines. Omit only when nothing described here is ever activated — a pure choice or decision issue with no capability behind it.
- **Beat 6 (structured contracts)** — include only when there are *contracts worth freezing*. A spike proposal, a capability decision, or an issue whose contracts live in another repo correctly omit it.

## Step 2 — Requirement or convention? (every mode)

Before you write **must**, **cannot**, **so**, **therefore**, or **required** —
anywhere in the issue, in any mode — classify it:

- **Requirement** — has a source outside pure habit: an API or schema that lacks
  the field, a hardware or physical fact, an explicit operator instruction, an
  incident, or a binding source the repository actually enforces — a committed
  policy document, schema, ADR, or contribution rule — even when that source
  lives in this repository. Cite the source inline; "lives in this repo" does
  not by itself demote a binding document to Convention.
- **Convention** — its only support is unwritten precedent: "we did it last
  time," "that's how the last one looked," with no document the repository
  enforces standing behind it. Write it as a choice: what was chosen, the
  alternative not taken, and why (if known).
- **Unknown** — you cannot tell. Say so in the issue ("not yet established whether
  X is required"), then take one of the three legal exits: **find the record**
  (decision note, ADR, blame, the PR that introduced it), **find a
  counterexample** (a place in the repo where X is not done and nothing broke),
  or **ask the operator**.

The test is **what breaks if we don't?** "Nothing breaks, it would just be
different" is a convention. Do not resolve an Unknown by generating a rationale:
a plausible reason you produced yourself is not evidence, and writing it down
turns a habit into a law for every reader after you. This applies to Partial
mode's hard constraint too — "do not roll the control plane" cites the incident
that made it a constraint.

## Step 3 — Draft the beats (Full mode)

Copy this checklist and fill each beat. Each beat earns its tokens only when the
issue carries abuse surface — a reviewer with enforcement power, a capability
that touches multiple owners, a build that can silently re-implement another
lane.

```
- [ ] 1. Outcome and status up front — what changes, and honestly whether it is
       deployed or design-only.
- [ ] 2. Sequencing / blocked-on — what must stand first, before any design.
       (Conditional: only when the issue is blocked on something external, or
       coordinates parts with their own internal ordering.)
- [ ] 3. Hard scope boundary — what this issue does NOT do (e.g. "reviewer, not
       executor"). State the boundary once; point back to it instead of restating.
- [ ] 4. Status table — for each component, split what is *shipped* from what
       is *proposed*. For each normative claim this issue makes about that
       component (a dependency, a "must," a design commitment) — not for the
       component's own descriptive facts — split what is *required* (source
       cited) from what is *chosen* (alternative named). Nothing proposed is
       mistaken for shipped; nothing chosen is mistaken for required; a fact is
       never laundered into a mandate by forcing it through this axis.
- [ ] 5. Activation gate — explicit "do not activate until…" conditions. For a
       capability that emits verdicts (a reviewer, a gate, a check), a clean
       verdict is forbidden when evidence is incomplete; for a capability that
       does not, activation itself stays blocked on the same conditions.
       (Conditional: include whenever the described capability will eventually
       be activated, even if this issue only designs it. Omit only when nothing
       described here is ever activated.)
- [ ] 6. Structured contracts — the request/result shapes, fingerprints, or
       coverage states the work freezes before implementation.
       (Conditional: only when there are contracts worth freezing. A spike, a
       capability decision, or an issue whose contracts live in another repo
       correctly omits this.)
- [ ] 7. Testable acceptance / regression evidence — falsifiable scenarios, not
       aspirations. "Replaying X finds Y" beats "X should be handled."
- [ ] 8. Cited source basis + ownership map — pinned versions with deep links,
       and which owning issue/PR each concern routes to. Cross-repo routing only
       when more than one repository is actually involved.
```

**Partial mode:** beat 1 (outcome), beat 7 (acceptance); the gap only when the
issue is fixing an actual defect; the hard constraint with its source (Step 2)
only when a real external boundary exists; rollback for a live-mutation
operational issue; a live-measurement table when measurements exist.
**Minimal mode:** title, acceptance, rollback, a linked evidence source (the
release notes or changelog entry backing the bump).

## Step 4 — Anti-ceremony check

Before posting, re-read the draft and cut anything that does not reduce abuse
surface or make acceptance falsifiable:

- A boundary stated four times is restated three times too many — keep one.
- A gate that duplicates an item already in the issue's own checklist or plan is
  drift waiting to happen.
- "Evidence" that is really a plan, a merged PR, or an agent statement — when
  live/deployment evidence is required — is a finding, not a clean verdict.

If a beat is empty or forced, the issue is probably in the wrong mode. Demote
it to Partial or Minimal rather than padding.

## Step 5 — Verify the draft

- [ ] Mode matches the Step 1 table; no beat is padded.
- [ ] Every must / cannot / so / therefore / required is sourced, written as a
      choice, or marked Unknown with an exit taken (Step 2).
- [ ] Acceptance is falsifiable — someone could run it and fail it.
- [ ] Every cross-reference resolves (open the linked issue/PR before citing).
- [ ] No secret values; no unrelated project paths, machine names, or personal
      identifiers leaked in from a source example. A legitimate
      cross-repository issue/PR link that beat 8 calls for is not leakage.

## Reference and examples

- For the full anatomy, a worked teardown of a real best-in-class design issue, and
  why the requirement-or-convention step exists, see [reference.md](reference.md).
- For a good Full issue, a Partial bug report, an over-ceremonized anti-example, an
  appropriately-terse Minimal bump, and a "must that was a choice" before/after, see
  [examples.md](examples.md).
