---
name: write-best-in-class-issue
description: >-
  Author a best-in-class GitHub issue for design, governance, epic, or proposal
  work: outcome-first, evidence-cited, with explicit boundaries, an activation
  gate, testable acceptance, and cross-repo ownership routing. Use when creating
  or substantially revising an issue that designs a system, defines a capability,
  coordinates multiple work items, or proposes a build. Do not load for
  operational tasks, one-line version bumps, or routine bug reports — those need
  only a clear title, the gap, and acceptance; applying the full template there
  is ceremony, not quality.
---

# Write a Best-in-Class Issue

A best-in-class issue makes a complex, easily-abused piece of work **safe to act
on later** — by a human *or* an agent. It is not a long issue. It is a structured
one: outcome-first, evidence-cited, with explicit boundaries and testable
acceptance. The reference model is the kind of issue that designs a reviewer, a
capability, or a multi-part build (for example: a semantic-reviewer design issue,
a storage-fabric proposal, or a build/CI coordination epic).

## Step 1 — Pick the mode (do this first)

Match depth to the issue's risk. Over-applying the full template to a one-line
bump is the failure mode this skill exists to prevent.

| Issue type | Mode | Apply |
|---|---|---|
| Design / governance / epic / proposal | **Full** | All 8 beats, with 2/5/6 conditional (see below) |
| Bug report (human- or agent-authored) | **Partial** | Beats 1, 3 (as "the gap"), 7; beat 4 is common when live measurements exist |
| Bump / one-line operational — **no live mutation** | **Minimal** | Title + Acceptance + Rollback only |
| Bump / operational that **mutates a live running system** (control-plane roll, service restart) | **Partial** | Treat as a bug: beats 1, 3, 7 — the hard constraint is the live-mutation boundary |

The Minimal/Partial line is **"does it mutate a live running system,"** not "is it a bump." A
pin, digest, or manifest change consumed later is Minimal; a version bump that rolls the live
control plane is Partial.

If the issue does not design, coordinate, or propose something consequential,
**stop and use Minimal**. When unsure, ask the operator which mode before drafting.

### Conditional beats in Full mode

Beats 2, 5, and 6 are **conditional**, not universal — verified against real issues:

- **Beat 2 (sequencing)** — include only when the issue is *blocked on* something. A coordination epic that "decides nothing" has no blocker.
- **Beat 5 (activation gate)** — include only when the issue *deploys or activates*. A pure design/decision issue has no activation.
- **Beat 6 (structured contracts)** — include only when there are *contracts worth freezing*. A spike proposal, a capability decision, or an issue whose contracts live in another repo correctly omit it.

## Step 2 — Draft the beats (Full mode)

Copy this checklist and fill each beat. Each beat earns its tokens only when the
issue carries abuse surface — a reviewer with enforcement power, a capability
that touches multiple owners, a build that can silently re-implement another
lane.

```
- [ ] 1. Outcome and status up front — what changes, and honestly whether it is
       deployed or design-only.
- [ ] 2. Sequencing / blocked-on — what must stand first, before any design.
       (Conditional: only when the issue is blocked on something.)
- [ ] 3. Hard scope boundary — what this issue does NOT do (e.g. "reviewer, not
       executor"). State the boundary once; point back to it instead of restating.
- [ ] 4. Evidence-vs-proposal table — for each component, split "shipped
       capability" from "boundary for this issue." Nothing proposed is mistaken
       for shipped.
- [ ] 5. Activation gate — explicit "do not activate until…" conditions. A clean
       verdict is forbidden when evidence is incomplete.
       (Conditional: only when the issue deploys or activates.)
- [ ] 6. Structured contracts — the request/result shapes, fingerprints, or
       coverage states the work freezes before implementation.
       (Conditional: only when there are contracts worth freezing. A spike, a
       capability decision, or an issue whose contracts live in another repo
       correctly omits this.)
- [ ] 7. Testable acceptance / regression evidence — falsifiable scenarios, not
       aspirations. "Replaying X finds Y" beats "X should be handled."
- [ ] 8. Cited source basis + cross-repo ownership map — pinned versions with deep
       links, and which owning issue/PR each concern routes to.
```

For Partial mode, keep beats 1, 3 (as "the gap"), 7. For Minimal, keep 1 and 7.

## Step 3 — Anti-ceremony check

Before posting, re-read the draft and cut anything that does not reduce abuse
surface or make acceptance falsifiable:

- A boundary stated four times is restated three times too many — keep one.
- A gate that duplicates a Phase-1 checklist item is drift waiting to happen.
- "Evidence" that is really a plan, a merged PR, or an agent statement — when
  live/deployment evidence is required — is a finding, not a clean verdict.

If a beat is empty or forced, the issue is probably in the wrong mode. Demote
it to Partial or Minimal rather than padding.

## Step 4 — Verify

- [ ] Description is third person, ~300–450 chars, with WHAT + WHEN + a non-trigger guard.
- [ ] SKILL.md body under 500 lines (it is).
- [ ] Every cross-repo reference resolves (open the linked issue/PR before citing).
- [ ] No secret values, no project-specific path leakage into a shared skill.

## Reference and examples

- For the full anatomy with a worked teardown of a real best-in-class design issue, see [reference.md](reference.md).
- For a good condensed issue, an over-ceremonized one, and an appropriately-terse bump, see [examples.md](examples.md).
