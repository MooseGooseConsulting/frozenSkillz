# Documentation Router

This file is only an entrypoint. Repository policy and procedures live in the documents below; load only the sources relevant to the task.

## Agent Instruction Placement

- When the user asks to change the instructions or behavior of a named or
  currently active skill, edit that skill's existing `SKILL.md`. Do not use the
  root `README.md` as a substitute; change it only when the user explicitly asks
  for repository README documentation.

## Skill Intent Records

When creating or materially revising a skill, create or update that skill's
`README.md` with its human-maintainer **response-shaping rationale**. Explain:

- the model decision or response the skill's instruction design is meant to
  evoke;
- why its particular wording, ordering, boundaries, evidence gates, and routed
  resources are needed to evoke that response; and
- the tempting default behavior or demonstrated failure mode each design choice
  is meant to prevent.

Do not merely restate the skill's business purpose. This README is deliberately
**not** agent instruction: do not route to it from `SKILL.md`, and do not put
required runtime behavior there. `SKILL.md` is the agent-facing entrypoint
(often a thin router); the adjacent README lets a future maintainer understand
why the instruction design should produce the intended response before changing
it.

| Task | Source |
|---|---|
| Understand the repository and package layout | `README.md` |
| Check whether a skill is active, gated, or ready for promotion | `docs/skill-review/tracker.md` |
| Change skill authority, packaging, distribution, synchronization, or promotion | `docs/workflows/skill-authority-and-frozen-sync.md`, then `plugins/distribution.json` |
| Understand or change how a non-client runtime consumes skills | `docs/workflows/skill-authority-and-frozen-sync.md` → **Skill Consumer Shapes**, then `docs/deployments/hermes.md` |
| Persist or set up agent configuration in a project repo | `docs/workflows/project-agent-config.md`, direction in `docs/platform/REFINED-V1.md` |
| Change machine-global Codex prompts or custom agents | `docs/workflows/codex-global-config.md`, then `config/codex/global/` |
| Evaluate or import an external skill, plugin, agent, or repository | `plugins/frozen-skills/skills/external-skill-intake/SKILL.md`, then `docs/workflows/external-skill-intake.md` |
| Learn whether an existing repo-owned skill helps in real work | `docs/rubrics.md` (philosophy), then `docs/workflows/skill-evaluation.md` |
| Learn how skills are understood and deployed in real work | Use the live personal `skill-analysis` skill when installed; otherwise follow `docs/workflows/skill-evaluation.md` → **Deployment learning**. Build manifests, one-trajectory case memos, and corpus lessons in `agent-control-plane`, then return only supported skill/case/tracker changes here |
| Work on a specific active skill | Its `SKILL.md` under `plugins/` and any references it routes to |
| Update marketplace or plugin metadata | The affected root marketplace catalog and package-native manifest under `plugins/` |
| Run repository validation | `README.md` → **Validation** |
| Review current work | GitHub Issues and pull requests; use `docs/superpowers/plans/` only where a current plan is explicitly linked |
| Recover historical context | Git history, merged pull requests, and closed issues |

When sources disagree, the task-specific source above wins over summaries in `README.md` or client compatibility files. Fix the stale downstream text in the same change.
