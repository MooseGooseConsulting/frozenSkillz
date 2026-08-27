# Documentation Router

This file is only an entrypoint. Repository policy and procedures live in the documents
below; load only the sources relevant to the task.

| Task | Source |
|---|---|
| Understand the repository and package layout | `README.md` |
| Check whether a skill is active, gated, or ready for promotion | `docs/skill-review/tracker.md` |
| Handle project authority documents | Do not load or route the disabled `project-docs` skill; follow the repository's declared authority documents and task-specific workflow directly |
| Change skill authority, packaging, distribution, synchronization, or promotion | `docs/workflows/skill-authority-and-frozen-sync.md`, then `plugins/distribution.json` |
| Understand or change how a non-client runtime consumes skills | `docs/workflows/skill-authority-and-frozen-sync.md` → **Skill Consumer Shapes** |
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

When sources disagree, the task-specific source above wins over summaries in `README.md` or
client compatibility files. Fix the stale downstream text in the same change.

## Notion authority

Notion is the live authority for decisions: standing policy, the operating model, roadmaps,
the rationale behind standing rules, and the scope of agent autonomy. There is no Markdown
mirror of Notion in this repository, and creating one is not an acceptable workaround. Read
Notion live by these stable URLs before acting on anything that needs a decision.

**Scope.** Notion decides; it does not run anything. The agent-configuration and skill-
distribution documents this repository routes to stay authoritative for what they own, and a
Notion page never substitutes for an authorisation this repository's own mechanism must
issue. On disagreement: about a *decision*, Notion wins and the repository record is
corrected; about *current state*, the live system wins and both are corrected.

| Page | URL |
|---|---|
| Local AI Infrastructure (which repo and which machine owns what) | https://app.notion.com/p/3c8c4d261ef881de8396fb44f69b32b4 |
| Decisions database | https://app.notion.com/p/e23213fce2f94755af0400189541ac36 |
| Agent Evaluation | https://app.notion.com/p/3c8c4d261ef8819487f6db902be42597 |
| Agentic Tool & MCP Registry | https://app.notion.com/p/3c8c4d261ef88195b62adec587f9abf5 |

### If Notion is unreachable

- **Governance question — STOP and report.** If the answer would come from a page above, say
  "Notion is unreachable; the governing answer is unavailable" and stop. Do not infer the
  decision from Git, from a dated file, or from memory of a previous session.
- **Pure operations — PROCEED.** Executing a documented procedure, running tests, or
  answering a code-fact question needs no Notion.
- **Never mirror.** Do not copy Notion content into this repository "so it works offline".
