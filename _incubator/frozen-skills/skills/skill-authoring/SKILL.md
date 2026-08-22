---
name: skill-authoring
description: >-
  Create or materially revise a frozenSkillz-owned skill with appropriately
  scoped response-shaping instructions, progressive disclosure, and a durable
  human intent record. Use when authoring or redesigning SKILL.md, routed
  references, scripts, or the adjacent skill README. Not for merely using an
  existing skill or evaluating third-party skill repositories.
---

# Skill Authoring

Design the skill around the model behavior it needs to evoke, not around the
amount of documentation it could contain. Put runtime behavior in `SKILL.md` and
the references it routes to. Keep the entrypoint as thin as the task permits,
but retain the context, boundaries, gates, and routing another agent must load
to act correctly.

When creating a skill or materially changing its trigger, response design,
workflow lanes, boundaries, evidence gates, or routed resources, create or
update its adjacent human-only `README.md`. Before writing that file, read
[references/skill-readme.md](references/skill-readme.md) completely.

Do not put required runtime behavior exclusively in the README, and do not
route the target skill to its own README. The README explains the intended
causal design to future human maintainers; the `SKILL.md` and its routed
resources remain the agent-facing instruction path.

Keep new skills gated until the repository's authority and review workflow says
they are ready for promotion. Validate the finished skill and its discoverability
without mistaking frontmatter checks for behavioral proof.
