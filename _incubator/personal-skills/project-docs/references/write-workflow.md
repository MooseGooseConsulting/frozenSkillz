# Writing a New Authority Doc

Generation workflow for a primary document that does not yet exist. Before choosing a template,
inventory the repository and owner's declared authority documents, paths, responsibilities, and
order. If a declared stack exists, author, review, migrate, or reconcile within that stack; an
explicitly declared nonstandard authority document is in scope. Do not make ordinary documentation
authoritative merely because it is markdown or adjacent to an authority doc.

`NORTH_STAR.md` → `architecture.md` → `AGENTS.md` is the default primary stack only when no
declared stack exists. The default's doc-specific guides own section definitions.

For current-work homes (Issues / `docs/plans/`), see `current-work-and-lifecycle.md` — those are not authority primaries.

Two on-ramps: interview (greenfield) vs review + reconcile (docs already in motion). Use the interview for what is truly new.

<interview>

## Step 1: Interview the Owner

Do not open a template. Ask open-ended questions.

| Default doc when no declared stack exists | Questions |
|---|---|
| NORTH_STAR.md | "What is this thing?" / "Why are you building it?" / "What will people assume this is that it isn't?" / "Where is this going?" / "Hard tradeoffs so far?" |
| architecture.md | "What technical approach and why?" / "What is Current vs Planned vs still open?" / "Major components?" / "Choices that would invalidate the project if reversed?" |
| AGENTS.md | "What does an agent need on first entry?" / "What commands actually work?" / "Hard rules on every PR?" / "Where does current work live (Issues vs plans)?" |

Listen for the owner's phrasing. Do not invent constraints they did not state.

Exit when you can describe the doc without them correcting you.

</interview>

<draft>

## Step 2: Draft from the Owner's Words

| Default doc when no declared stack exists | Minimum viable |
|---|---|
| NORTH_STAR.md | Opener + Goals + at least one Anti-Goal |
| architecture.md | Architecture Thesis + Status Legend + System Shape table |
| AGENTS.md | NORTH_STAR pointer + route-by-task + stop rule (≤60 lines) |

Rules:

- Use the owner's phrasing.
- Mark unknowns `[OPEN]`.
- Do not invent constraints.

</draft>

<provenance>

## Step 3: Tag Provenance

- `[OWNER]` — direct words or faithful paraphrase
- `[INFERRED]` — synthesized; flag for review
- `[OPEN]` — not decided

High-authority elements (pillars, invariants, hard rules) must be `[OWNER]` or deleted / asked.

</provenance>

<review>

## Step 4: Review with the Owner

Confirm every `[INFERRED]` and `[OPEN]`, omitted sections, and the opener / thesis / first-line pointer.

</review>

<finalize>

## Step 5: Finalize

Remove provenance tags. Optional frontmatter:

```yaml
---
title: [Project Name] [Doc Name]
date: [today]
author: [owner]
status: living
last_confirmed: [today]
---
```

| Default doc when no declared stack exists | Path |
|---|---|
| NORTH_STAR.md | `docs/NORTH_STAR.md` or root `NORTH_STAR.md` |
| architecture.md | `docs/architecture.md` or root `architecture.md` |
| AGENTS.md | Root `AGENTS.md` (always) |
| CLAUDE.md | Root stub: one-line pointer to AGENTS (skip if declared an authority doc) |

When a declared stack exists, its declared paths and roles control; do not create or rename the
default files merely to conform to this table.

Do not create PROGRESS.md.

</finalize>

<revision>

## Revising an Existing Doc

1. Inventory the declared authority stack and the requested document's role.
2. Run `review-checklist.md`.
3. Fix only what needs changing.
4. Update `last_confirmed` if used.
5. Run `authority-flow.md`.
6. For finished temporary docs: promote then delete (`current-work-and-lifecycle.md`).

</revision>
