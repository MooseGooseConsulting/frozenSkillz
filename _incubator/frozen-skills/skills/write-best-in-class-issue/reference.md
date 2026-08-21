# Best-in-Class Issue Anatomy — Reference

This is the deep reference for `write-best-in-class-issue`. The main `SKILL.md`
gives the mode router and the 8-beat checklist; this file explains *why* each beat
earns its tokens and shows the beats extracted from a real best-in-class design
issue: one that designs an autonomous semantic PR reviewer with GitHub
enforcement power. The issue is described generically so this skill stays
repo-independent; the shape is what matters.

That issue is the reference because its subject — an autonomous reviewer with
GitHub enforcement power — carries maximum abuse surface. Length tracks risk,
not author verbosity. A lower-risk issue should be shorter (see the mode router).

## Why each beat matters

### 1. Outcome and status up front

State what changes and **honestly whether it is deployed or design-only**. The
reference issue opens with: "This is design work informed by source research,
not a deployed service." That single line stops a reader from filing "when will
it ship?" against an issue that is deliberately not shipping yet.

Failure without it: an agent treats a design issue as an implementation task and
starts building half the proposed components.

### 2. Sequencing / blocked-on

Name what must stand first. The reference issue's first line names its blocker:
"Blocked on [the primary executor role]. Do not implement or activate this
reviewer until [that executor] is fully standing." A reader knows the activation
gate before any design.

Failure without it: an agent starts the dependent work immediately and produces
something that has no foundation to run on.

### 3. Hard scope boundary

State what the issue does **not** do. The reference issue has a section literally
titled "Hard boundary: reviewer, not executor" — the reviewer may inspect,
criticize, and block, but must not own the implementation task or run the live
change as a hidden side effect.

State the boundary **once** and point back to it. The reference issue restates
this boundary in four places; that is the one critique worth leveling at it — a
single canonical section reduces drift as the issue ages.

Failure without it: scope creep. A reviewer silently becomes an executor; a
capability silently re-implements another issue's lane.

### 4. Evidence-vs-proposal table

For each component, split **shipped capability** from **boundary for this issue**.
The reference issue's "What the research established" table has one row per
component (a session-capture tool, an agent runtime, a coding agent, the git
host, an archiver, and PR/commit templates) with the shipped capability in one
column and the boundary in another. Nothing proposed is mistaken for shipped.

Failure without it: an agent builds against a capability that does not exist yet,
or cites a proposal as if it were deployed.

### 5. Activation gate

Explicit "do not activate until…" conditions. The reference issue forbids a
clean/enforcing verdict until the central session API is healthy, backup/restore
is exercised, the preserved archive is full-pushed with fidelity reconciled,
enough producers and a runtime are visible centrally, and continuous
sync/catch-up is proven.

The key design move: **coverage is a first-class result.** A clean verdict is
*forbidden* when a producer is stale, a schema mismatches, or lineage is
unknown — the result is `incomplete`, never a false `clean`. Most agent-reviewer
specs skip this; the reference issue makes it the spine.

Failure without it: the system ships a false "verified" on incomplete evidence.

### 6. Structured contracts

Freeze the request/result shapes, fingerprints, and coverage states *before*
implementation. The reference issue specifies `ReviewRequest`, `ReviewResult`,
finding fingerprints, delivery states (`resumed | steered | commented |
status_posted | reopened | correction_started | not_resumable`), and the
separate ledger contract. Replaying identical inputs must not create a duplicate
comment, issue, or correction agent.

Failure without it: idempotency is left to implementation time, where it is
always too late and never tested.

### 7. Testable acceptance / regression evidence

Falsifiable scenarios, not aspirations. The reference issue's "Regression and
completion evidence" is a checklist like: "Replaying [a specific prior issue]'s
premature closure finds its unmet acceptance conditions, reopens it, and wakes
correction without human approval." That is a test you can run and fail.

Contrast with "issue closure should be handled correctly" — unfalsifiable,
untestable, useless.

Failure without it: the issue closes on a vibe, not a verdict.

### 8. Cited source basis + cross-repo ownership map

Pinned versions with deep links, and an explicit map of which owning issue/PR
each concern routes to. The reference issue cites the session-capture tool's
pinned release (with links to the exact parser files), the agent runtime's
pinned release, the coding agent's app-server protocol, and the git host's
webhook/status/reopen docs. Its "Cross-repository ownership" section assigns
each concern to its owning issue — the semantic policy, the central plane, the
read-only operations role, producer enrollment, and the derived persistence
layer.

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

These are described by shape, not by repo/number, so this skill stays
repo-independent. Each is a real issue that earns its mode.

- **A storage-fabric proposal** (USB4/Thunderbolt mesh for Kubernetes nodes):
  live hardware reads, an ASCII topology, a Phase 0 soak gate, "decisions to
  confirm," cited upstream sources. Full mode, earned.
- **A build & CI coordination epic**: an intake/coordination epic that routes
  rather than decides, cites live tree state, names conflicting open PRs, and
  splits child issues with one observable outcome each. Full mode, earned.
- **An agent-authored memory over-commit bug** (a host's auto-start guest set
  exceeds its memory with no swap): a live `free -m` table, a hard constraint
  ("do not roll the control plane"), and acceptance. Partial mode, correct.
- **A one-patch version bump** (OS patch n → n+1, matrix-tied): one paragraph,
  acceptance + rollback + an evidence link. Minimal mode, correct.
