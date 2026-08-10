# Documentation Router

This file is only an entrypoint. Repository policy and procedures live in the documents below; load only the sources relevant to the task.

| Task | Source |
|---|---|
| Understand the repository and package layout | `README.md` |
| Check whether a skill is active, gated, or ready for promotion | `docs/skill-review/tracker.md` |
| Change skill authority, packaging, distribution, synchronization, or promotion | `docs/workflows/skill-authority-and-frozen-sync.md`, then `plugins/distribution.json` |
| Understand or change how a non-client runtime consumes skills | `docs/workflows/skill-authority-and-frozen-sync.md` → **Skill Consumer Shapes**, then `docs/deployments/hermes.md` |
| Persist or set up agent configuration in a project repo | `docs/workflows/project-agent-config.md`, direction in `docs/platform/REFINED-V1.md` |
| Change machine-global Codex prompts or custom agents | `docs/workflows/codex-global-config.md`, then `config/codex/global/` |
| Evaluate or import an external skill, plugin, agent, or repository | `plugins/frozen-skills/skills/external-skill-intake/SKILL.md`, then `docs/workflows/external-skill-intake.md` |
| Work on a specific active skill | Its `SKILL.md` under `plugins/` and any references it routes to |
| Update marketplace or plugin metadata | The affected root marketplace catalog and package-native manifest under `plugins/` |
| Run repository validation | `README.md` → **Validation** |
| Review current work | GitHub Issues and pull requests; use `docs/superpowers/plans/` only where a current plan is explicitly linked |
| Recover historical context | Git history, merged pull requests, and closed issues |

When sources disagree, the task-specific source above wins over summaries in `README.md` or client compatibility files. Fix the stale downstream text in the same change.

## Cursor Cloud specific instructions

This repo is Python 3 CLI/validation tooling (skills, plugin manifests, and synchronizers) — there is no server or web UI to run.

- Use `python3`; there is no `python` shim on the VM. `README.md` and CI examples that write `python ...` should be run as `python3 ...`.
- The only third-party dependency is `PyYAML` (see `requirements-validation.txt`), installed to the user site by the startup update script. Everything else is stdlib.
- Full validation surface (mirrors `.github/workflows/validate.yml`): `python3 scripts/validate_manifests.py`, `python3 -m unittest discover -s tests -v`, and the whitespace lint `git diff --check HEAD -- . ':(exclude)_incubator/scout/*/source/**'`.
- The synchronizer is the runnable "app". Exercise it against a throwaway destination outside the repo (the destination must be disjoint from the checkout), e.g. `python3 scripts/sync_frozen_skills.py --consumer codex --apply --destination /tmp/frozen-skills-smoke` then re-run with `--check` to prove convergence. `--check` exits nonzero (1 = drift, 2 = conflict) by design.
- `sync_frozen.py` defaults its Codex destinations to `~/.codex`; pass `--skills-destination`/`--codex-home` when smoke-testing so you don't touch the real home config.
