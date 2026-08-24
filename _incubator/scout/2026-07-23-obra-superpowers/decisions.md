# Decision Log: obra/superpowers v6.1.1

## Decision

- Date: 2026-07-23
- Reviewer: Codex with operator review
- Artifact paths: `source/skills/brainstorming/` and
  `source/skills/dispatching-parallel-agents/`
- Outcome: incubate for later
- Affected frozenSkillz paths: none promoted; forensic intake contract updated separately

## Evidence

- Inventory summary: 14 skills and a cross-harness methodology in a 172-file MIT snapshot.
- Rubric score summary: `brainstorming` 4.0/5 (B-, moderate confidence) and
  `dispatching-parallel-agents` 3.6/5 (B-, strong confidence for observed Codex behavior and
  moderate cross-harness).
- Evaluation mode and evidence paths: forensic; `analysis.md` and `evals/forensic/`.
- Safety notes: the optional companion is an executable local service; fixed historical security
  defects and current state-path behavior remain relevant to adoption.
- Maintenance notes: upstream is active and responsive, but the skill has substantial cross-harness
  and companion complexity. Parallel dispatch also depends on fast-changing harness discovery,
  context-isolation, and worker-lifecycle semantics.

## Rationale

The first two skill reviews identify useful concepts but also unresolved workflow and Codex
concerns. Direct AgentsView transcript evidence makes parallel dispatch the current priority
adaptation candidate: attributable uses demonstrate concurrency and useful synthesis in Codex. A
separate implicit match demonstrates reviewer and integration value for the broader pattern without
establishing that this skill caused those outcomes. The current operational contract still needs
authority/capability preflight, explicit fork policy, resource boundaries, and version-aware
lifecycle guidance before adaptation. Keep the pinned source and review the remaining skills one at
a time before promoting anything.

## Follow-Up

- Owner: operator and reviewing agent
- Trigger: next requested Superpowers skill review
- Required validation: extend `analysis.md`, add forensic findings, and update this decision only
  when the evidence changes the packaging outcome.
