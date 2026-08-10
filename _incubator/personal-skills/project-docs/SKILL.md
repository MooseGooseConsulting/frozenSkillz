---
name: project-docs
description: >
  Create, review, or repair project authority docs only when explicitly asked to
  author, rewrite, critique, migrate, reconcile, or audit NORTH_STAR.md,
  architecture.md, AGENTS.md, CLAUDE.md routing, or legacy PROGRESS.md. Do not
  use for ordinary repo work, README edits, status checks, or incidental doc mentions.
---

# Project Docs Authoring

## Trigger Gate

Use this skill only when the requested deliverable is an authority-document draft,
edit, review/critique, migration, reconciliation, or documentation-authority audit.
An explicit request to use `project-docs` also qualifies.

Do not load it for general repository review, conversation completeness checks,
implementation work, operational configuration, a README-only change, or merely
because the repository contains AGENTS.md or other documentation. If documentation
changes are incidental to another task, follow the owning task or skill.

<context>
Authority hierarchy (no status diary in the ladder):

NORTH_STAR (intent) → architecture (technical strategy and shape) →
AGENTS (thin router). Current work lives in GitHub Issues and/or
`docs/plans/`. Finished work is promoted into living homes, then the
temporary file is deleted. Git / tags / PRs are the archive.

AGENTS.md is a pure router, not a container. It states authority order,
routes each task category to the doc that owns it, lists real commands,
and stops. Project identity lives in NORTH_STAR; do not restate it in
AGENTS. CLAUDE.md is a one-line pointer to AGENTS.md — no second doctrine
file.

Authority flows one direction. When a downstream doc disagrees with an
upstream doc, the downstream doc is wrong until the owner revises upstream
on purpose.

This skill drafts, reviews, reconciles, and migrates. It does not block
PRs, run CI, or assign Guardian severities.

Owner statements establish intent and requirements. Tests, measurements, and
live probes establish technical or runtime evidence. Migration provenance is
not automatically durable product intent, and a plan is not implementation.
Do not blur these categories merely to fit a preferred document shape.
</context>

<task_router>

| User wants to... | Load these files |
|---|---|
| Create a new authority doc that does not exist | `references/write-workflow.md` + the relevant doc guide |
| Review or critique an existing authority doc | `references/review-checklist.md` + the relevant doc guide |
| Reconcile multiple docs against each other | `references/authority-flow.md` |
| Migrate instructions into the AGENTS.md pattern | `references/agents-md-guide.md` + `references/write-workflow.md` |
| Handle current work / finished work / leftover PROGRESS | `references/current-work-and-lifecycle.md` (+ `references/progress-md-guide.md` only if migrating legacy PROGRESS away) |
| Understand the future Guardian boundary | `references/guardian-relationship.md` |

Per-document guides:

| Doc | Guide |
|---|---|
| NORTH_STAR.md | `references/north-star-guide.md` |
| architecture.md | `references/architecture-md-guide.md` |
| AGENTS.md | `references/agents-md-guide.md` |
| Legacy PROGRESS.md (migrate away only) | `references/progress-md-guide.md` |

Exemplars: `examples/NORTH_STAR.md`, `examples/architecture.md`,
`examples/AGENTS.md`, `examples/CLAUDE.md`.

Infrastructure / GitOps parallel set: `examples/infra/`.

</task_router>

<scope>

Primary documents:
- `NORTH_STAR.md` — intent, goals, anti-goals, pillars
- `architecture.md` — technical strategy, system shape, invariants
- `AGENTS.md` — agent entrypoint and operating contract (router only)

Living overflow (legal homes for content expelled from primaries):
- `docs/decisions/` — ADRs
- `docs/components/` **or** topic living docs (e.g. `systems/<topic>.md`) — deep subsystem truth
- `docs/workflows/` — long procedures
- `docs/plans/` — active executable plans (optional if Issues carry the work)

Do **not** recommend:
- `PROGRESS.md` (legacy; migrate away)
- `docs/history/` as a rolling archive (git is the archive)
- `docs/README.md` meta-indexes, HANDOFF.md / STATUS.md renames of PROGRESS

Documentation lives in the authority docs and living overflow homes.
Implementation directories hold implementation, not prose — a one-line pointer
is the only exception.

README.md is outside this authority hierarchy. This skill does not assign README a
purpose, require it to point to AGENTS.md, or reduce it to a title. Only change a
README when the user explicitly includes it in the requested documentation scope.

The skill does NOT create or rewrite docs unless the user asks. Neighboring
docs are never silently rewritten as a side effect of working on one doc.

Derive topology from the repository's declared authority and the owner's
explicit decisions before applying these defaults. Do not create a competing
router or reinterpret an existing file's purpose without authorization.

</scope>

<smallest_change>

Make the smallest authority change that satisfies the requested deliverable,
reconcile only directly affected downstream text, and stop.

Do not infer directory renames, new schemas, auditors, CI gates, lifecycle
systems, enforcement tooling, or PR decomposition. If the request reveals one
of those as a separate need, name it as unresolved; do not build it unless the
user explicitly asks.

</smallest_change>

<minimum_viable_stack>

Do not create every primary document merely to satisfy the pattern.

- `AGENTS.md` is always recommended.
- `NORTH_STAR.md` when intent is non-obvious or drift-prone.
- `architecture.md` when technical shape is complex enough to go stale.
- Current work: Issues and/or `docs/plans/` — not a fourth primary doc.
- Topic living docs are optional; use when a repo outgrows a single architecture.md.

A new repo can start with `AGENTS.md` alone. Do not push for completeness.

</minimum_viable_stack>

<output_types>

Returns one of: proposed draft · patch-style edit plan · review report ·
authority-flow summary · migration recommendation (including promote-then-delete).

Findings cite the relevant section. Suggested edits are concrete.

</output_types>

<vocabulary>

| Skill (authoring time) | Guardian (PR / runtime) |
|---|---|
| finding | violation |
| review note | severity |
| conflict | blocker |
| alignment issue | policy violation |
| authority-flow check | enforcement |
| suggested edit | CI failure / PR gate |

See `references/guardian-relationship.md`.

</vocabulary>

## Learnings

### 2026-07-16

#### What Worked
- Settled owner preference: no PROGRESS; no `docs/history/` roll-off; Issues/`docs/plans` for current work; promote lasting facts then **delete** temporary docs; AGENTS thin router; CLAUDE one-line → AGENTS.
- Topic living docs + AGENTS find-table (coldaine-configurations PR #16) as an allowed optional shape, not a universal mandate.
- Restoring a discoverable `SKILL.md` after a references-only live root regression.

#### What Failed
- Teaching “movement, not deletion” into `docs/history/` — that was the sprawl machine (dated-record convention).
- Keeping PROGRESS as a recommended primary while the owner was deleting it across repos.
- Live `~/.agents/skills/project-docs` missing `SKILL.md` — skill undiscoverable despite intact references.

#### Configuration Notes
- Live canonical: `~/.agents/skills/project-docs/`. Gated evaluation copy: `frozenSkillz/_incubator/personal-skills/project-docs/`. Stay gated until promotion bar; do not auto-publish to marketplace.
- Claude Code: junction `~/.claude/skills/project-docs` → `~/.agents/skills/project-docs`.

### 2026-06-29 (preserved — the guardrail behind promote-then-delete)
- **Do not recommend deleting a doc that still reflects verified live state.** Recommending "delete PROGRESS" while it had just been reconciled to live secrets/cluster state (kubectl + helmfile diff) produced conflicting advice in the same session. Promote-then-delete removes *superseded/temporary* content — not the current, load-bearing handoff. Promote first; delete only once the lasting facts are in their living home. This is the scar that promote-then-delete is built around; keep it.
- **Do not assert live state from a doc alone.** Stating cluster blockers from PROGRESS without running `kubectl` on the session machine drew correct owner pushback ("how do you know?"). A doc is a claim to verify, not ground truth.
