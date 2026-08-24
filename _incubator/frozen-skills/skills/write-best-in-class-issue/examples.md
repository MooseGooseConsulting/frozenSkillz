# Best-in-Class Issue — Examples

Five examples: a Full design issue, a Partial bug report, an over-ceremonized
anti-example, a Minimal bump, and a "must that was a choice" before/after. Each
is condensed to show shape, not length, and described generically so the skill
stays repo-independent.

## Full mode — design issue (condensed from the reference issue's shape)

```markdown
## Outcome and status

Design an agent-to-agent repository reconciler with two jobs: review work at
an authoring boundary and return specific criticism to the model that can
still fix it; and periodically reconcile recent traces with repository state
so lasting knowledge does not disappear between sessions. This issue designs
and gates the reconciler; it does not activate it. The activation gate and
completion evidence below define what must be true before a later issue may
turn it on.

## Sequencing decision — 2026-07-20

Blocked on the primary executor role in [the executor issue]. Do not implement
this reviewer until the executor runtime is fully standing and has passed
[the executor issue]'s acceptance.

## Hard boundary: reviewer, not executor

This issue does not own PR execution. The reviewer may inspect, criticize,
publish a verdict, block a clean status, or reopen an unsupported closure. It
must not own the implementation task or run the live change as a hidden side
effect. Execution is owned by [the executor issue].

## What the research established

| Component | Shipped capability | Boundary for this issue | This issue's dependency: required or chosen |
|---|---|---|---|
| Session-capture tool | agent capture; SQLite→central sync; read-only API | session evidence corpus, not the active reviewer | Chosen — the reviewer reads its sync output; polling the source database directly was not evaluated |
| Agent runtime | HMAC webhooks, cron, zero-token gates | execution substrate; still needs a dedicated profile | Required — webhook signature validation is the only supported trust boundary (docs linked) |
| Git host | PR/issue webhooks, commit statuses, reopen API | closing keywords do not prove acceptance; failed webhooks not redelivered | Required — the reopen API is the only supported un-close path (docs linked) |

## Activation gate

A clean/enforcing verdict is forbidden until: the central session API is
healthy; backup/restore is exercised; the preserved archive is full-pushed
with fidelity reconciled; ≥2 producer agents and 1 agent runtime are visible
centrally; continuous sync/catch-up is proven. Until then, result is
`incomplete`, never `clean`.

## Contracts

`ReviewResult` = status (clean | needs_correction | incomplete | error) +
coverage snapshot + findings[] (kind, severity, claim, expected owner,
evidence anchors, stable fingerprint) + delivery state. Replaying identical
inputs must not create a duplicate comment, issue, or correction agent.

## Regression and completion evidence

- [ ] Replaying [a specific prior issue]'s premature closure finds its unmet
      acceptance conditions, reopens it, and wakes correction without human
      approval.
- [ ] A PR whose author bypasses the PR template still receives a required
      verdict for each head SHA.
- [ ] Stale producer data, an ID collision, or incompatible schema returns
      `incomplete`, never `clean`.

## Cross-repository ownership

- [this issue]: semantic policy, dispatcher, reviewer, profile.
- [the central-plane issue]: central session-store placement.
- [the executor issue]: stateful executor and PR-to-task path.
- [the archiver issue]: production read-only provider and derived ledger.

## Primary source basis

- Session-capture tool pinned release, Session API, parsers (linked).
- Agent runtime pinned release, webhooks, cron, hooks (linked).
- Git host webhook events, signature validation, issue reopen API (linked).
```

## Partial mode — bug report done right (condensed from a real memory over-commit)

```markdown
# Host A auto-starts more guest memory than it has

## Outcome

Host A's auto-start guest set is over-committed; one more start will OOM the
host. Bring the auto-start set under physical memory.

## The gap (live, 2026-08-14)

| | MiB |
|---|---|
| physical | 65,536 |
| swap | 0 |
| sum of auto-start guest allocations | 71,680 |
| headroom | −6,144 |

## Hard constraint

Do not roll the control plane to fix this. Source: the 2026-08-14 incident —
a control-plane node hit SystemOOM, went NotReady, and faulted four storage
volumes; the operator has ruled out any fix that restarts a control-plane
guest until the stable workers are standing.

## Acceptance

- [ ] `sum(auto-start allocations) < physical − 4,096 MiB` on Host A, measured
      the same way as the table above.
- [ ] No control-plane guest was restarted (uptime unchanged).
```

Note the hard constraint **cites its source**. "Do not roll the control plane"
is a requirement here because an incident and an operator instruction stand
behind it — not because it is how things are usually done. That is Step 2 of the
skill applied in Partial mode.

## Over-ceremonized — what NOT to do (a one-line bump padded to Full)

```markdown
## Outcome and status

This issue bumps the node OS from patch 10 to patch 11. This is design work
informed by source research, not a deployed service.

## Hard boundary: bumper, not executor

This issue does not roll the live control plane. It only pins the new version.

## Activation gate

The bump may not be applied until: the changelog is read; the matrix is
verified; the boot image is regenerated; all pins are updated as a set; the
operator has confirmed; the moon is in the right phase.

## Regression and completion evidence

- [ ] The version number is higher than the previous version number.
- [ ] No file references the old version.
```

This is the failure mode: a Minimal-mode task padded with gates that do not
reduce abuse surface. The correct version is the Minimal example below.

## Minimal mode — a one-patch bump triaged right (condensed from a real matrix-pinned OS bump)

```markdown
# Node OS patch 11 is available; decide whether to bump

One patch ahead of the pinned release. This is a matrix pin (node OS + boot
image schematic + kube minor): a bump means regenerating the boot image and
re-pinning the installer reference in the four places that carry it, as a set.

**Acceptance:** the changelog is read and one of two decisions is recorded in
this issue with the changelog linked — (a) it carries security content → a
matrix refresh is scheduled with all four pins updated together, or (b) it does
not → this issue closes as "fold into the next deliberate matrix bump." Closing
with neither decision recorded, or without the changelog link, fails acceptance.
**Rollback** (if bumped): standing nodes keep the patch-10 boot image; revert
the four pins.

Evidence: [upstream release notes for patch 11]
```

Note what it does **not** have: no sequencing section, no boundary section, no
activation gate, no contracts. It has a clear title, the matrix-pin constraint,
an acceptance that can actually be failed (a decision must be recorded), a
rollback, and an evidence link. That is the correct quality bar for a one-patch
bump.

## A "must" that was a choice — before / after (Step 2)

**Before** (as an agent-authored plan actually carried it forward from a README):

```markdown
The orchestration API cannot declare extra disks, so per-host templates must
supply the data disk. Each control-plane host therefore needs its own template
with the disk baked in.
```

Every clause is true, and the reader is now designing three templates around a
requirement nobody imposed. "So" fused a fact with a choice; the alternative was
never named; "must" was inherited, not sourced.

**After** (same facts, status carried):

```markdown
The orchestration API cannot declare a second disk — its storage schema has a
single boot-volume field (required; source linked). The existing storage nodes
supply the disk via a per-host template. That is a **choice**: the alternative
is to clone boot-only and attach the disk after clone with one host command,
which was not evaluated when the storage nodes were built (unknown why — no
decision note; asked the operator). For the control planes this issue proposes
attach-after-clone, because the disk is an addition to a node whose primary
job is compute.
```

The second version is longer by three lines and is the only one that is safe to
act on later: the requirement has a source, the choice has an alternative, and
the unknown is marked and routed instead of filled with a generated reason.
