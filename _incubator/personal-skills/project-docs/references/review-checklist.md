# Review Checklist

Router for critiquing an existing authority document. Per-doc guides own detailed checks; this file routes and adds the cross-doc pass.

Before selecting a default guide, inventory the repository's declared authority
owners in its root router, documentation index, and owner instructions. If it
declares a nonstandard stack, review its declared roles and routes through
`authority-flow.md`; an absent default file is not a structural or drift gap.

<by_document>

| Doc to review | Guide |
|---|---|
| NORTH_STAR.md | `north-star-guide.md` |
| architecture.md | `architecture-md-guide.md` |
| AGENTS.md | `agents-md-guide.md` — pure router, 60-line cap, bare paths, no PROGRESS/history routes |
| CLAUDE.md | One-line pointer to AGENTS only |
| Legacy PROGRESS.md | `progress-md-guide.md` — migrate away; do not refresh as living handoff |
| Plans / Issues usage | `current-work-and-lifecycle.md` |

</by_document>

<severity>

## Classifying findings

**Structural** — wrong agent behavior:
- Fabricated constraints
- AGENTS inlining doctrine / over 60 lines / `@` inside AGENTS
- CLAUDE.md with prose or multi-file doctrine
- New PROGRESS.md or recommended `docs/history/` roll-off
- Unlabeled aspiration in architecture.md

**Drift** — was right once:
- Stale `last_confirmed`
- Status labels that no longer match reality
- AGENTS still routing to deleted PROGRESS / history
- Finished plans left undeleted after promote

**Style** — sound but imprecise:
- Vague rules
- Anti-goals that ban mechanisms instead of intent
- Tool-specific cruft in shared docs

</severity>

<cross_doc>

After a single-doc review, run `authority-flow.md`.

First inventory declared authority owners and routes. When the repository
declares a stack, check that stack's upstream/downstream relationships and
routers; do not impose the default order or replacement files.

Only when no declared stack supplies those roles, use the default order:
NORTH_STAR → architecture → AGENTS.

Default quick pairs: architecture vs NORTH_STAR · plans/Issues vs architecture
· plans/Issues vs NORTH_STAR · AGENTS vs everything · CLAUDE vs AGENTS.

</cross_doc>

<reporting>

```text
## [Doc Name] Review

### Authority inventory
- declaration source: [path or owner instruction]
- selected topology: [declared stack or default]
- owners and routes: [compact inventory]

### Structural findings
- [finding] — citing [section]; suggested fix: [edit]

### Drift findings
- [finding] — citing [section]; suggested action: [promote-delete / refresh / fix route]

### Style findings
- [finding] — citing [section]; suggested rewording: [edit]

### Authority-flow findings
- [finding] — between [A] and [B]; downstream is [B]; suggested action: [edit]
```

Do not silently rewrite neighboring docs.

</reporting>
