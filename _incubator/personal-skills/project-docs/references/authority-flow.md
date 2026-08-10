# Authority Flow

The per-doc guides catch problems inside one document. The authority-flow pass catches problems *between* documents. Run it after creating, reviewing, or revising any single document.

---

## Establish the Topology First

Before applying a hierarchy or calling an absent default document a gap:

1. Inspect the repository's root router, documentation index, explicit owner
   instructions, and any authority declarations.
2. Record a compact inventory: `path | role or claims | upstream/downstream
   routes | declaration source`.
3. If the repository declares a nonstandard authority stack, use that stack and
   its declared routes for this pass. Do not map its documents onto the default
   names, require the default files, or propose replacements just because the
   defaults are familiar.
4. Use the default topology below only when no declared stack supplies the
   relevant roles.
5. If the declared roles or order are ambiguous, report that ambiguity for the
   owner instead of choosing a competing topology.

A filename alone is not a declaration. The inventory establishes which
documents own which claims for this repository.

---

## Default Topology

```
NORTH_STAR.md
   ↓ (intent)
architecture.md
   ↓ (technical strategy)
AGENTS.md
   (routes to the above + living overflow + Issues/plans)
```

When this default applies, current work (Issues / `docs/plans/`) is **not** an authority rung. It must not contradict NORTH_STAR or architecture; if it does, that is a finding (drift), and the plan/issue is wrong until upstream is deliberately revised.

When authority docs disagree, the downstream doc is wrong. The skill surfaces the disagreement; it does not silently fix it.

---

## Pairwise Checks

For a declared nonstandard stack, compare each declared upstream/downstream
pair, its routing documents, and active work against the claims in the
inventory. The default pairs below apply only when the default topology does.

| Pair | Question | Conflict surfaces as |
|---|---|---|
| architecture.md vs NORTH_STAR.md | Does the technical approach serve stated intent without inventing new purpose? | architecture describes a system NORTH_STAR doesn't ask for; or crosses anti-goals. |
| Issues/plans vs architecture.md | Does active work match Current/Planned labels? | Plan builds something architecture marks Deferred; or treats Planned as Current. |
| Issues/plans vs NORTH_STAR.md | Is the project drifting from goals / anti-goals / pillars? | Active work pursues a banned intent. |
| AGENTS.md vs everything | Does the router route correctly without absorbing doctrine? | Inlined content; missing routes; routes to PROGRESS or `docs/history/`. |
| CLAUDE.md vs AGENTS.md | Is CLAUDE.md a one-line pointer to AGENTS? | Prose, headers, duplicated doctrine, or extra `@` targets. |

---

## How to Run the Pass

1. State the question.
2. Build the authority inventory.
3. If the inventory identifies a declared stack, open its owners and routers.
   Otherwise, open NORTH_STAR, architecture, AGENTS, and CLAUDE (if present).
   Skim active plans/Issues as needed.
4. Note agree / disagree / asymmetric gap against the selected topology.
5. Classify: **conflict**, **gap**, **alignment-only-needed**, or
   **topology ambiguity**.

Do not report an absent default file as a gap when the inventory selected a
different declared stack.

### Finding types

- **Conflict** — incompatible claims. Downstream updates, or owner revises upstream and propagates.
- **Gap** — upstream states something downstream should reflect but doesn't.
- **Alignment-only-needed** — both correct; phrasing may confuse agents.
- **Topology ambiguity** — the repository does not make the owner or order
  clear enough to choose a stack.

---

## Resolving Conflicts

For a declared nonstandard stack, the documents and routes named in its
inventory own the claims they declare. Do not force those claims into this
default mapping. Use this table only when the default topology applies.

| Claim type | Canonical home |
|---|---|
| Identity, goals, anti-goals, pillars | NORTH_STAR.md |
| Technical decisions, shape, invariants | architecture.md |
| Current implementation status | architecture.md status labels |
| Current work / blockers / next focus | Issues and/or `docs/plans/` |
| Routes, commands, hard rules | AGENTS.md |
| Durable decisions with rationale | `docs/decisions/` |

If the canonical doc is stale, the user decides. The skill does not silently rewrite upstream.

---

## Common Findings

- **Architectural drift** — architecture says local-first; a plan integrates an external API without updating architecture.
- **Buried decision** — plan or leftover PROGRESS mentions “switched Redis → SQLite”; needs an ADR + delete the temp note after promote.
- **Route gap** — AGENTS has no branch for docs or for Issues/plans.
- **Legacy leak** — AGENTS still routes to PROGRESS or `docs/history/`.
- **Doctrine leak** — AGENTS inlines goals; delete the inline.
- **CLAUDE regression** — stub grew prose; reduce to one-line → AGENTS.
- **False-default gap** — a repository declares a different authority stack;
  record the declared topology instead of requiring NORTH_STAR, architecture,
  or AGENTS.

---

## Output

```
## Authority-Flow Findings

### Authority inventory
- declaration source: [path or owner instruction]
- selected topology: [declared stack or default]
- owners and routes: [compact inventory]

### Conflicts
- (between A and B): canonical is [doc]; suggested fix: [edit]

### Gaps
- (upstream says X; downstream should reflect): suggested addition: [edit]

### Alignment notes
- (both correct but inconsistent framing): suggested rewording: [edit]
```

User decides what to apply.

---

## When To Run

- After any single-doc edit
- Before declaring a new repo's doc pattern complete
- When the user asks “are my docs in sync?”
- After deleting PROGRESS or promoting a finished plan
