# How to Write an AGENTS.md

AGENTS.md is the file every agent in the repo reads first. It is the universal entry point (Codex, Cursor, OpenCode, Claude via a one-line `CLAUDE.md` pointer).

Every line pays a token cost on every session. The discipline is not “what could be useful.” It is “what does the agent need to start correctly, and where does it find everything else.”

A good AGENTS.md: (1) points at NORTH_STAR for identity, (2) routes by task. Anything beyond that is drift.

---

## The Load-Bearing Principle

> Inline nothing. AGENTS.md is a pure router: authority order, task routes, a stop rule, and commands. Identity lives in NORTH_STAR.md. Current work lives in Issues and/or `docs/plans/`. Everything else loads lazily via bare paths.

- Bare paths (`See architecture.md`) are instructions; the agent Reads them only when needed.
- Do not put `@` references inside AGENTS.md to architecture, plans, decisions, or components — that defeats the router by eager-loading everything.
- `CLAUDE.md` is a one-line pointer to AGENTS only (see Compatibility). NORTH_STAR is reached because AGENTS’s first line says to read it.

## The 60-Line Cap

Hard-capped at 60 lines. Routes, commands, and hard rules may fill the budget; inlined identity, decisions, procedures, or status defeat the cap.

A line earns its slot only if it is a route, a command, or a hard rule that is needed often, costly to get wrong, and cannot be deferred to a lazy read.

---

## Order of Operations

1. NORTH_STAR.md (identity, goals, anti-goals, pillars)
2. architecture.md (technical decisions and shape)
3. AGENTS.md (the route)

Write AGENTS.md last. Current work homes (Issues / plans) are routed from AGENTS; they are not above AGENTS in the authority ladder.

---

## What AGENTS.md Owns and Does Not Own

Owns:

- agent onboarding pointer
- authority routing
- essential commands
- hard working rules
- optional find-table for topic living docs
- compatibility note for tool-specific stubs

Does not own:

- project purpose → `NORTH_STAR.md`
- technical strategy → `architecture.md`
- current task state → Issues and/or `docs/plans/`
- durable decisions → `docs/decisions/`
- subsystem depth → `docs/components/` or topic docs
- long procedures → `docs/workflows/`
- archives → **git** (not `docs/history/`)

---

## What Goes In

| Section | When to include |
|---|---|
| NORTH_STAR pointer (first line) | Always |
| Authority order line | Always once multiple authority docs exist |
| Route by task / find-table | Always once more than one task category |
| Commands | When agents must run real commands |
| Working rules | Project-wide enforceable rules only |
| Compatibility | When CLAUDE.md or similar exists |

**Minimum viable:** NORTH_STAR pointer + route-by-task + authority line + stop rule.

Skip handoff sections that tell agents to update PROGRESS or roll into `docs/history/`.

---

## No Inline Identity

First line:

```
Read NORTH_STAR.md first. Do not infer intent from code.
```

Do not paraphrase NORTH_STAR. Do not put goals, anti-goals, pillars, or status in the pointer.

---

## The Decision Tree

Teaching form (ASCII). Production form under the 60-line cap is a compressed list (see `examples/AGENTS.md`).

```
What are you about to do?
│
├─ Understand intent, scope, boundaries
│  → NORTH_STAR.md
│
├─ Make a technical or architectural decision
│  → NORTH_STAR.md · architecture.md · docs/decisions/
│
├─ Implement, fix, resume active work
│  → GitHub Issues and/or docs/plans/ (whichever this repo uses)
│  → architecture.md / topic docs for the subsystem
│
├─ Draft, edit, review/critique, migrate, reconcile, or audit authority documentation
│  → Invoke the project-docs skill
│
├─ Run a long procedure
│  → docs/workflows/
│
├─ Look up why something was done historically
│  → git log / tags / closed PRs and Issues — not docs/history/
│
├─ Operate build / CI
│  → Commands below
│
└─ Anything that crosses a goal, anti-goal, pillar, or invariant
   → Stop. Surface the conflict.
```

Rules:

- Bare paths only at leaves.
- Three to seven top-level branches.
- Branches mutually distinguishable.
- Last branch is boundary-crossing → stop.
- Procedures live in `docs/workflows/`, not inline.

Optional: a short **Find anything** table mapping concerns → topic living docs (allowed pattern; not required).

---

## Commands

One line each: `- Action: command`. No aspirational commands. No long explanations.

---

## Working Rules

Enforceable only. Five to ten max. No style nits the linter already owns.

Good: “Do not create PROGRESS.md or docs/history/.”  
Good: “Promote lasting facts, then delete temporary plans.”  
Bad: “Be thoughtful.”

---

## Compatibility

CLAUDE.md must be a one-line pointer to AGENTS. Examples of valid stubs:

```
@AGENTS.md
```

```
Read AGENTS.md.
```

No header. No prose. No second `@NORTH_STAR.md` in CLAUDE — AGENTS already routes there. Tool-specific files do not hold doctrine.

---

## Common Failure Modes

- Enumeration drift (flat list of every doc)
- `@` inside AGENTS.md
- Duplicating NORTH_STAR identity
- Routing to PROGRESS / `docs/history/`
- Aspirational commands
- Vague rules
- Missing routes to decisions / workflows / plans-or-Issues

---

## When AGENTS Disagrees

Authority: NORTH_STAR > architecture > AGENTS.

AGENTS never holds authority of its own. If commands disagree with the repo, the code wins and AGENTS updates. If routes point at deleted files, fix the routes.
