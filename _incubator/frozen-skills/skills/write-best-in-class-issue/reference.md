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

### 4. Status table (shipped vs proposed; required vs chosen)

For each component, split **shipped capability** from **boundary for this issue**.
The reference issue's "What the research established" table has one row per
component (a session-capture tool, an agent runtime, a coding agent, the git
host, an archiver, and PR/commit templates) with the shipped capability in one
column and the boundary in another. Nothing proposed is mistaken for shipped.

The same table carries a second axis: for every "must" the issue states, whether
it is **required** (a source outside the repo's own precedent — cited) or
**chosen** (a decision, with the alternative not taken named). Nothing chosen is
mistaken for required. See "Why the requirement-or-convention step" below.

Failure without it: an agent builds against a capability that does not exist yet,
cites a proposal as if it were deployed — or carries a past choice forward as a
law and designs the next system around a constraint nobody imposed.

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

### 8. Cited source basis + ownership map

Pinned versions with deep links, and an explicit map of which owning issue/PR
each concern routes to. The reference issue cites the session-capture tool's
pinned release (with links to the exact parser files), the agent runtime's
pinned release, the coding agent's app-server protocol, and the git host's
webhook/status/reopen docs. Its "Cross-repository ownership" section assigns
each concern to its owning issue — the semantic policy, the central plane, the
read-only operations role, producer enrollment, and the derived persistence
layer. Cross-repository routing is only required when more than one repository
is actually involved; a single-repo design still names its owning issues.

Failure without it: an agent re-implements a lane another issue owns, or builds
against a version it guessed at.

## Why the requirement-or-convention step

Step 2 of the skill exists because the most common way an issue becomes unsafe
to act on later is not a missing beat — it is a **"must" that was never a must**.

The mechanism, described generically from a real case: an orchestration API
could not declare a second disk on a virtual machine. The repo's docs recorded
the workaround as *"the API cannot declare extra disks, so the template supplies
them."* Every clause was true. But "so" fused a fact (the API lacks the field)
with a choice (put the disk in the template — instead of, say, attaching it
after clone). The docs never named the alternative, so a later agent planning a
*different* node class read "template supplies the disk" as a hard requirement,
carried it into a plan, and — when challenged — produced a plausible rationale
for why it had to be that way. It could not reconstruct the original reason,
because none was written down. Nothing broke; it just would have been different.

Three things make this failure structural rather than careless:

- **The information is not in the text.** From "we did X" alone, a reader cannot
  tell whether X was required or preferred — the same statement is consistent
  with both. This is the identifiability problem known from inverse-constraint
  learning: many (constraint, preference) pairs explain the same trajectory. No
  amount of intelligence recovers what was never recorded.
- **Aligned models tilt toward "ought."** Absent modality, an agent defaults to
  the strongest reading, because honoring a constraint looks like diligence and
  relaxing one looks reckless. A smarter model makes it *worse*: it can generate
  a rationale on demand that makes the convention feel load-bearing.
- **The canon already has the writer-side fix.** Architecture decision records
  have carried "alternatives considered" since 2011 precisely so the *why-not*
  survives. An issue is the same kind of artifact: it will be read later by
  someone who has only the text.

So the skill does two things. On the writer side, beat 4 makes every "must" show
its status. On the reader side, Step 2 forces the author to classify each "must"
*before* writing it, and — when the answer is Unknown — permits only the three
exits that add information (find the record, find a counterexample, ask) and
forbids the one that fabricates it (generate a reason). Chesterton's fence says
do not remove what you do not understand; this is the mirror rule: do not
*enshrine* what you do not understand. Both fail at the same missing step — go
find out why.

## The mode test (re-stated)

An issue earns the Full 8-beat template only when it carries abuse surface:
enforcement power, multi-owner coordination, or a build that can silently
re-implement another lane. A bug report, a version bump, or an operational task
does not carry that surface. For those, the Partial or Minimal mode is the
*correct* quality choice — the full template there is ceremony, and ceremony is
the documented failure mode (the retired `issue-pr-review` skill was disabled
for exactly this reason).

## Validation against real issues

The router and beat prescriptions were tested against 10 real issues spanning
all three modes. Findings that changed the skill:

- **Minimal/Partial boundary:** the line is "does it mutate a live running
  system," not "is it a bump." A control-plane version bump rolls the live
  cluster → Partial (hard-constraint beat), not Minimal. A pin or digest
  change consumed later stays Minimal.
- **Beat 6 (structured contracts) is conditional:** three real Full-mode
  issues (a spike proposal, a coordination epic, a capability decision whose
  contracts live in another repo) correctly omit it. Forcing it there is
  over-prescription.
- **Beats 2 (sequencing) and 5 (activation gate) are conditional:** a
  coordination epic that "decides nothing" correctly omits both.
- **Partial bug reports commonly include beat 4** (live measurement tables)
  even though it is not required — note it as common, not forbidden.
- **"State the boundary once"** validated: the reference issue restates its
  boundary four times, confirming the critique.

**Not yet validated:** Step 2 (requirement or convention) was added 2026-08-15
from one real agent-authored plan that laundered a convention into a
requirement. It has not yet been run against a set of real issues; that is a
promotion-gate item in the tracker. The expected finding is that most "must"
statements in agent-authored issues have no cited source.

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
- **A co-location plan that failed Step 2** (negative example): an agent-authored
  plan carried "per-host templates must supply the data disk" from a README into
  a design for a different node class. The README's "cannot declare … so the
  template supplies" fused an API fact with a choice; the plan restated it as a
  requirement and never named the post-clone alternative. Correct form: "the API
  cannot declare a second disk (source: its storage schema has one boot-volume
  field); the existing nodes supply it via the template — a choice; attaching
  after clone is the alternative and was not evaluated."
