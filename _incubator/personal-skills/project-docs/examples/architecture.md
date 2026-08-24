# architecture.md

## Architecture Thesis

This project is built as a local-first documentation-governance system for agentic coding workflows.

The core architectural bet is that project drift is best controlled by keeping a small set of authority documents in the repo, while allowing a future Guardian runtime to mirror and evaluate those documents outside the repo.

## Status Legend

- **Current** — implemented or directly reflected in the repo.
- **Planned** — decided direction, not fully implemented.
- **Candidate** — plausible option, not decided.
- **Deferred** — intentionally not being built now.

## System Shape

| Area | Status | Approach |
|---|---|---|
| Documentation skill | Current | A skill guides agents through creating, reviewing, and reconciling project docs. |
| Authority docs | Current | The repo uses `NORTH_STAR.md`, `architecture.md`, and `AGENTS.md`. Current work lives in Issues and/or `docs/plans/`. |
| Claude compatibility | Current | `CLAUDE.md` is a one-line pointer to `AGENTS.md` and holds no doctrine. |
| Guardian runtime | Deferred | A later runtime may inspect PRs or repo changes for drift against the authority docs. |
| Off-repo governance store | Candidate | A mirrored North Star store may live outside the repo to reduce self-modification risk. |

## Key Technical Differentiator

The differentiator is not “more documentation.”

The differentiator is **structured authority**:

- `NORTH_STAR.md` owns intent.
- `architecture.md` owns technical strategy and system shape.
- `AGENTS.md` owns routing and hard operating rules (not identity or status).
- Issues / `docs/plans/` own current work.
- ADRs own durable decisions.
- Temporary docs are promoted into living homes, then deleted; git is the archive.

Agents are not asked to read everything. They are routed to the right authority for the kind of question they are answering.

## Target Architecture

```text
                 AGENTS.md
          agent entrypoint / router
                    │
                    ▼
 ┌─────────────────────────────────────┐
 │       Project Authority Docs         │
 │                                     │
 │  NORTH_STAR.md  →  architecture.md  │
 │         │                │           │
 │         └──────┬─────────┘           │
 │                ▼                     │
 │         docs/decisions/              │
 │   components/topics · workflows      │
 └─────────────────────────────────────┘
                    │
         Issues / docs/plans/ (current work)
                    │
                    ▼
          future Guardian runtime
       drift review / PR review
```

## Current Architecture

The current implementation is a documentation-pattern skill, not the Guardian runtime.

The skill performs:

1. document inventory
2. task classification
3. per-document generation or review workflow
4. authority-flow check
5. suggested edits or review findings
6. promote-then-delete guidance for finished temporary docs

## Major Components

| Component | Status | Responsibility | Detail |
|---|---|---|---|
| `project-docs/SKILL.md` | Current | Router for authority-document authoring/editing, review/critique, migration, reconciliation, and audits | skill root |
| `references/north-star-guide.md` | Current | North Star writing/review rules | references/ |
| `references/agents-md-guide.md` | Current | AGENTS.md router guidelines | references/ |
| `references/architecture-md-guide.md` | Current | Architecture.md writing/review rules | references/ |
| `references/current-work-and-lifecycle.md` | Current | Issues/plans + promote-then-delete | references/ |
| `references/progress-md-guide.md` | Current | Legacy PROGRESS migrate-away only | references/ |
| Guardian runtime | Deferred | Future repo/PR drift detection system | — |

## Constraints and Conventions

**Constraints** (required; source named):

- `CLAUDE.md` exists at the repo root even though it holds no doctrine — required: Claude Code auto-loads `CLAUDE.md`, not `AGENTS.md`, so the pointer is the only way that tool reaches the router.
- `AGENTS.md` is the cross-tool entrypoint name — required: the AGENTS.md convention adopted by Codex, Cursor, Jules, and Factory; renaming it makes those tools miss it.

**Conventions** (chosen; alternative named):

- `AGENTS.md` is capped at 60 lines — chosen; alternative: no cap; because a long router gets eager-read and defeats lazy loading.
- Current work lives in Issues and/or `docs/plans/`, not `PROGRESS.md` — chosen; alternative: a rolling `PROGRESS.md`; because it became a burial ground for durable decisions (see the retirement note in the project-docs skill).
- Status labels are exactly four (Current / Planned / Candidate / Deferred) — chosen; alternative: free-form status; because a closed set is greppable and cannot be padded with "Stretch" or "Maybe."

## Architectural Invariants

- `AGENTS.md` must remain a router, not a giant documentation index. Prevents every agent from eager-loading the whole doc set on entry.
- `architecture.md` may include target architecture, but forward-looking claims must be labeled. Prevents an agent from treating a Planned component as available.
- Do not create `PROGRESS.md` or roll finished work into `docs/history/`. Prevents durable decisions from being buried in a diary nobody reads back.
- Durable architecture decisions belong in ADRs, not buried in plans or scratch notes. Prevents the rationale from being lost when the plan is deleted.
- The skill must not pretend to be the Guardian runtime. Prevents an authoring tool from acquiring blocking power it was never given.

## ADR Index

| ADR | Status | Summary |
|---|---|---|
| `docs/decisions/0001-use-agents-md.md` | accepted | Use `AGENTS.md` as the cross-tool agent entrypoint. |
| `docs/decisions/0002-claude-md-shim.md` | accepted | Reduce `CLAUDE.md` to a one-line pointer to `AGENTS.md`. |
| `docs/decisions/0003-skill-vs-guardian.md` | proposed | Keep the documentation skill separate from the future Guardian runtime. |

## Open Architecture Questions

- Should the Guardian mirror authority docs into an orphan branch, a separate repo, or an external store?
- Does the future Guardian run as a CLI, GitHub Action, local hook, or all three?
- Should doc review findings be advisory only, or can they become blocking in PR contexts?

## Links

- `NORTH_STAR.md` — project intent
- `AGENTS.md` — agent entrypoint
- Issues / `docs/plans/` — current work
- `docs/decisions/` — architectural decisions
- `docs/components/` — subsystem documentation
- `docs/workflows/` — longer operating procedures
