# AGENTS.md

Read NORTH_STAR.md first. Do not infer intent from code.

Authority on conflict: NORTH_STAR > architecture > AGENTS.
CLAUDE.md is a compatibility pointer. README has no fixed role in this template;
define any README authority explicitly for the repository that owns it.

Route by task:
- Intent, scope, boundaries      → NORTH_STAR.md
- Architectural decision         → architecture.md, docs/decisions/
- Implement, fix, resume work    → GitHub Issues and/or docs/plans/
- Long procedure                 → docs/workflows/
- Historical context             → git log / tags / closed PRs (not docs/history/)
- Draft, edit, review/critique, migrate, reconcile, or audit authority docs → invoke the project-docs skill
- Ending substantial work        → promote lasting facts into living homes; delete finished plans/scratch

If a task crosses a goal, anti-goal, pillar, or invariant: stop and surface it.

Commands: install `…` · test `…` · lint `…` · branch from main, PR to main
