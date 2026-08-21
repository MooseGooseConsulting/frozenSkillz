# Best-in-Class Issue — Examples

Three examples, one per mode. Each is condensed to show shape, not length.

## Full mode — design issue (condensed from the reference issue's shape)

```markdown
## Sequencing decision — 2026-07-20

Blocked on the primary executor role in [the executor issue]. Do not implement
this reviewer until the executor runtime is fully standing and has passed
[the executor issue]'s acceptance.

## Outcome and status

Design (not deploy) an agent-to-agent repository reconciler with two jobs:
review work at an authoring boundary and return specific criticism to the model
that can still fix it; and periodically reconcile recent traces with repository
state so lasting knowledge does not disappear between sessions.

## Hard boundary: reviewer, not executor

This issue does not own PR execution. The reviewer may inspect, criticize,
publish a verdict, block a clean status, or reopen an unsupported closure. It
must not own the implementation task or run the live change as a hidden side
effect. Execution is owned by [the executor issue].

## What the research established

| Component | Shipped capability | Boundary for this issue |
|---|---|---|
| Session-capture tool | agent capture; SQLite→central sync; read-only API | session evidence corpus, not the active reviewer |
| Agent runtime | HMAC webhooks, cron, zero-token gates | execution substrate; still needs a dedicated profile |
| Git host | PR/issue webhooks, commit statuses, reopen API | closing keywords do not prove acceptance; failed webhooks not redelivered |

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

## Over-ceremonized — what NOT to do (a one-line bump padded to Full)

```markdown
## Outcome and status

This issue bumps Talos 1.12.10 → 1.12.11. This is design work informed by source
research, not a deployed service.

## Hard boundary: bumper, not executor

This issue does not roll the live control plane. It only pins the new version.

## Activation gate

The bump may not be applied until: the changelog is read; the matrix is
verified; the schematic ISO is regenerated; all pins are updated as a set; the
operator has confirmed; the moon is in the right phase.

## Regression and completion evidence

- [ ] The version number is higher than the previous version number.
- [ ] No file references the old version.
```

This is the failure mode: a Minimal-mode task padded with gates that do not
reduce abuse surface. The correct version is the Minimal example below.

## Minimal mode — a one-line bump done right (condensed from a real matrix-pinned OS bump)

```markdown
From the 2026-08-10 maintenance-steward review. One patch ahead; built with
Go 1.25.12. This is a matrix pin (Talos OS + Image Factory schematic + kube
1.35.x): a bump means regenerating the schematic ISO and re-pinning the
installer reference in `infra/k8s/talos/README.md`,
`talos/patches/platform-bootstrap.yaml`, `capmox/target-cluster.yaml`, and
`capmox/n5-worker.yaml` as a set.

**Acceptance:** read the 1.12.11 changelog; if it carries security content,
schedule the matrix refresh; otherwise fold into the next deliberate Talos/kube
matrix bump. Rollback: standing nodes keep the 1.12.10 ISO; revert the pins.

Evidence: https://github.com/siderolabs/talos/releases/tag/v1.12.11
```

Note what it does **not** have: no sequencing section, no boundary section, no
activation gate, no contracts. It has a clear title, the matrix-pin constraint,
acceptance, rollback, and an evidence link. That is the correct quality bar for
a one-patch bump.
