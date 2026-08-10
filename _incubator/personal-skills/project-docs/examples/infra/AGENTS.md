# AGENTS.md

Read NORTH_STAR.md first. Do not infer intent from code or manifests.

Authority order: NORTH_STAR > architecture.md > AGENTS.md. Downstream never overrides upstream.

## Route by task

- Understand intent, scope, boundaries → NORTH_STAR.md
- Make a technical or architectural decision → NORTH_STAR.md, architecture.md, docs/decisions/
- Change the VM substrate → tofu/, docs/components/substrate.md
- Change the cluster (nodes, bootstrap) → talos/, docs/components/talos.md
- Change shared services (ingress, secrets, storage, db) → platform/, docs/components/platform.md
- Add or change a workload → apps/, docs/components/apps.md
- Pick up active work, blockers → GitHub Issues and/or docs/plans/
- Run a long procedure (bootstrap, disaster recovery) → docs/workflows/
- Look up completed work → git log / tags / closed PRs (not docs/history/)
- Draft, migrate, reconcile, or audit authority documentation → invoke the project-docs skill
- Anything crossing a goal, anti-goal, pillar, or invariant → Stop. Surface the conflict.

## Commands

- Provision substrate: `tofu -chdir=tofu apply`
- Bootstrap cluster: `talosctl apply-config ...` then `talosctl bootstrap`
- Check reconcile status: `kubectl get -A <reconciler resources>`
- Diff repo vs cluster: `<reconciler> diff`

## Working rules

- No hand-edited live state. Changes land as commits and reconcile.
- Manifests only in tofu/, talos/, platform/, apps/. No prose docs there; one-line pointer exception only.
- No undocumented architectural decisions for storage, database, ingress, or secrets strategy.
- Status means applied, not authored.
- Promote lasting facts, then delete finished plans/scratch. Do not create PROGRESS.md or docs/history/.
- Branch from main; PR to main.

## Compatibility

CLAUDE.md contains only `@AGENTS.md` (or `Read AGENTS.md.`). No prose, no header.
