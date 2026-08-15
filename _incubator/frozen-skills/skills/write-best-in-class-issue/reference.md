# Best-in-Class Issue Anatomy — Reference

This is the deep reference for `write-best-in-class-issue`. The main `SKILL.md`
gives the mode router and the 8-beat checklist; this file explains *why* each beat
earns its tokens and shows the beats extracted from a real best-in-class issue:
coldaine-homelab [#29 — "After primary Hermes: build the independent semantic PR
reviewer"](https://github.com/MooseGooseConsulting/coldaine-homelab/issues/29).

#29 is the reference because its subject — an autonomous reviewer with GitHub
enforcement power — carries maximum abuse surface. Length tracks risk, not
author verbosity. A lower-risk issue should be shorter (see the mode router).

## Why each beat matters

### 1. Outcome and status up front

State what changes and **honestly whether it is deployed or design-only**. #29
opens with: "This is design work informed by source research, not a deployed
service." That single line stops a reader from filing "when will it ship?"
against an issue that is deliberately not shipping yet.

Failure without it: an agent treats a design issue as an implementation task and
starts building half the proposed components.

### 2. Sequencing / blocked-on

Name what must stand first. #29's first line: "Blocked on the primary Hermes
role in #40. Do not implement or activate this semantic reviewer until
`hermes-ops-01` is fully standing." A reader knows the activation gate before
any design.

Failure without it: an agent starts the dependent work immediately and produces
something that has no foundation to run on.

### 3. Hard scope boundary

State what the issue does **not** do. #29 has a section literally titled "Hard
boundary: reviewer, not executor" — the reviewer may inspect, criticize, and
block, but must not own the implementation task or run the live change as a hidden
side effect.

State the boundary **once** and point back to it. #29 restates this boundary in
four places; that is the one critique worth leveling at it — a single canonical
section reduces drift as the issue ages.

Failure without it: scope creep. A reviewer silently becomes an executor; a
capability silently re-implements another issue's lane.

### 4. Evidence-vs-proposal table

For each component, split **shipped capability** from **boundary for this issue**.
#29's "What the research established" table has one row per component
(AgentsView, Hermes, Codex, GitHub, LLM Archiver, PR templates) with the shipped
capability in one column and the boundary in another. Nothing proposed is
mistaken for shipped.

Failure without it: an agent builds against a capability that does not exist yet,
or cites a proposal as if it were deployed.

### 5. Activation gate

Explicit "do not activate until…" conditions. #29 forbids a clean/enforcing
verdict until the central Session API is healthy, backup/restore is exercised,
the HEPHASTUS archive is preserved and full-pushed, two Codex producers and one
Hermes runtime are visible centrally, and continuous sync/catch-up is proven.

The key design move: **coverage is a first-class result.** A clean verdict is
*forbidden* when a producer is stale, a schema mismatches, or lineage is
unknown — the result is `incomplete`, never a false `clean`. Most agent-reviewer
specs skip this; #29 makes it the spine.

Failure without it: the system ships a false "verified" on incomplete evidence.

### 6. Structured contracts

Freeze the request/result shapes, fingerprints, and coverage states *before*
implementation. #29 specifies `ReviewRequest`, `ReviewResult`, finding
fingerprints, delivery states (`resumed | steered | commented | status_posted |
reopened | correction_started | not_resumable`), and the separate ledger contract.
Replaying identical inputs must not create a duplicate comment, issue, or
correction agent.

Failure without it: idempotency is left to implementation time, where it is
always too late and never tested.

### 7. Testable acceptance / regression evidence

Falsifiable scenarios, not aspirations. #29's "Regression and completion
evidence" is a checklist like: "Replaying issue #3's premature 2026-07-15
closure finds its unmet acceptance conditions, reopens it, and wakes correction
without human approval." That is a test you can run and fail.

Contrast with "issue closure should be handled correctly" — unfalsifiable,
untestable, useless.

Failure without it: the issue closes on a vibe, not a verdict.

### 8. Cited source basis + cross-repo ownership map

Pinned versions with deep links, and an explicit map of which owning issue/PR
each concern routes to. #29 cites AgentsView v0.38.1 (with links to the exact
parser files), Hermes v2026.7.7.2, the Codex app-server protocol, and the GitHub
webhook/status/reopen docs. Its "Cross-repository ownership" section assigns
#29 = semantic policy, #26 = central plane, #28 = read-only Hermes, configs
#5/#15 = producer enrollment, llm-archiver #118 = derived persistence.

Failure without it: an agent re-implements a lane another issue owns, or builds
against a version it guessed at.

## The mode test (re-stated)

An issue earns the Full 8-beat template only when it carries abuse surface:
enforcement power, multi-owner coordination, or a build that can silently
re-implement another lane. A bug report, a version bump, or an operational task
does not carry that surface. For those, the Partial or Minimal mode is the
*correct* quality choice — the full template there is ceremony, and ceremony is
the documented failure mode (the retired `issue-pr-review` skill was disabled
for exactly this reason).

## Peer examples at the same bar

- [#81 — USB4/Thunderbolt storage fabric proposal](https://github.com/MooseGooseConsulting/coldaine-homelab/issues/81):
  live hardware reads, ASCII topology, a Phase 0 soak gate, "decisions to
  confirm," cited sources. Full mode, earned.
- [#115 — build & CI coordination epic](https://github.com/MooseGooseConsulting/coldaine-homelab/issues/115):
  an intake/coordination epic that routes rather than decides, cites live tree
  state, names conflicting open PRs, splits child issues with one outcome each.
  Full mode, earned.
- [#547 — SER10 auto-start memory over-commit](https://github.com/MooseGooseConsulting/coldaine-homelab/issues/547):
  agent-authored bug. Live `free -m` table, hard constraint ("do not roll the
  control plane"), acceptance. Partial mode, correct.
- [#401 — Talos 1.12.10 → 1.12.11 bump](https://github.com/MooseGooseConsulting/coldaine-homelab/issues/401):
  one paragraph, acceptance + rollback + evidence link. Minimal mode, correct.
