# frozenSkillz

Cross-platform agent skills, rules, and plugin metadata for reusable agent workflows.

`frozenSkillz` is the reviewed source repository and marketplace. `frozen-skills` is the shared active package. Consumer-restricted skills live in dedicated plugin packages, and `plugins/distribution.json` composes the exact synchronizer allowlist for Claude, Codex, Cursor, or Gemini. Dedicated packages appear only in approved consumer catalogs. Content under `_incubator/` is stored for review and is never installed.

This repository is not a dumping ground for local client caches, raw external repos, or unreviewed experimental skill copies.

## Plugins

| Plugin | Category | Status | Purpose |
|---|---|---|---|
| `frozen-skills` | reference | active | Shared package for reviewed cross-consumer skills. |
| `codex-thread-organizer` | productivity | active, Codex-only | Dedicated Codex package for task-history organization; absent from other consumer catalogs. |
| `skill-injector` | development | experimental, untested | UserPromptSubmit hook and subagent prompt quality gate for LLM-assisted skill suggestions. Review/test before enabling. |

Historical reference/workflow skills remain gated in `_incubator/` until they pass the quality bar in `docs/skill-review/tracker.md`.

## Skill Analysis Ownership

Do not run fleet activation/effectiveness analysis from this repository. The
[`agent-control-plane`](https://github.com/MooseGooseConsulting/agent-control-plane) repository
owns read-only AgentsView extraction, candidate manifests, declared analysis corpora,
one-trajectory case memos, cross-case lessons, and analysis tooling.

`frozenSkillz` owns the other side of the boundary: skill text and versions, trigger examples,
packaging, and lifecycle state. The live personal
`skill-analysis` skill routes between the two; its reviewed gated mirror is
`_incubator/personal-skills/skill-analysis/`.

## Synchronize a Computer

Clone or update this repository on each computer, then run the cross-platform synchronizer:

```powershell
python scripts/sync_frozen_skills.py --consumer codex --check
python scripts/sync_frozen_skills.py --consumer codex --apply
```

For a complete Codex update, synchronize both reviewed skills and native global
configuration through the unified entrypoint:

```powershell
python scripts/sync_frozen.py --consumer codex --check
python scripts/sync_frozen.py --consumer codex --apply
```

The existing skill synchronizer remains the component responsible for exact skill
directories. The Codex adapter handles native files with different ownership rules
and preserves unrelated content in `~/.codex/AGENTS.md`; see
[`docs/workflows/codex-global-config.md`](docs/workflows/codex-global-config.md).

Every run selects either `--consumer` or a named `--deployment` subset. Codex defaults to its private `~/.codex/skills` root; Claude, Cursor, and Gemini require an explicit `--destination` until a consumer-private default is qualified. The synchronizer:

- validates that the Claude, Codex, Cursor, and Gemini manifests have the same plugin identity and version;
- installs or updates the shared package plus only dedicated packages in the selected consumer's distribution;
- leaves unrelated personal skills alone;
- records the selected consumer and managed content in `.frozen-skills-sync.json`;
- rejects a destination already managed for another consumer;
- refuses to overwrite an unmanaged or locally modified destination skill.

Use `--destination <path>` for another local skill root. Use `--prune` to remove unchanged, previously managed skills that have left the selected distribution. `--force` overwrites local conflicts and should be used only after reviewing the reported plan.

A destination that must receive only part of a distribution uses a named deployment from `plugins/distribution.json:deployments`, which requires an explicit `--destination` plus `--prune`. A deployment either names its consumer and selects from that consumer's set, or omits `consumer` because it is a non-client runtime and may then select only shared skills. See [`docs/workflows/skill-authority-and-frozen-sync.md`](docs/workflows/skill-authority-and-frozen-sync.md) → **Deployment Subsets**.

The destination must be disjoint from the repository: it cannot be inside the frozenSkillz checkout or contain that checkout. This enforces outward-only deployment and prevents reverse synchronization into reviewed source.

Do not use the shared `~/.agents/skills` root as an implicit target for a consumer-restricted skill. An explicit destination is still allowed for controlled migrations or tests. After pulling a new revision on any computer, `--check` exits nonzero when that consumer needs synchronization; `--apply` converges it to the selected allowlist.

## Client-managed Plugin Install

Claude Code can instead let its marketplace manage a client-specific plugin copy:

```bash
/plugin marketplace add Coldaine/frozenSkillz
/plugin install frozen-skills@coldaine-skills
```

That command auto-discovers the five shared skills in the `frozen-skills` package. It does not install the physically separate `codex-thread-organizer` package, populate a Codex skill root, or install anything from `_incubator/`.

The Codex marketplace separately exposes the valid `codex-thread-organizer` plugin package. Cursor and Gemini remain separately validated packaging surfaces. Manifest presence alone is not an installer; use `sync_frozen_skills.py --consumer <name>` for a verified local installation unless a specific client provides and documents its own plugin installer.

## Active Skills

`frozen-skills` currently registers these shared skills:

- `delegation-contract`: brief and receive work across agent boundaries with explicit context, authority, output, and single-writer coordination rules.
- `doppler`: Doppler CLI and secret-injection workflow guidance that avoids exposing secret values.
- `external-skill-intake`: sandbox, inventory, score, evaluate, and package external skill/plugin/agent repos before any promotion.
- `omc-reference`: maintain Oh My ClaudeCode as a separate Claude Code plugin from Codex without importing OMC workflow rules into ordinary Codex work.
- `pdm-cli-operations`: inspect and operate Proxmox fleets through the official PDM client, with exact target selection and terminal task proof for mutations.

The dedicated `codex-thread-organizer` package is available to Codex only. It reads related task bodies, renames Codex tasks with sparse semantic titles, identifies the current owner of unfinished work, and supports periodic Codex organization runs.

## External Skill Intake

Do not import external repositories directly into `plugins/`. Evaluate them through:

- `plugins/frozen-skills/skills/external-skill-intake/SKILL.md`
- `docs/workflows/external-skill-intake.md`
- `_incubator/scout/<YYYY-MM-DD>-<repo>/`

Candidate source stays read-only under `source/`; mined ideas go to scout analysis files, eval runs, decision logs, and adapted frozenSkillz-owned paths only after review.

## Repository Layout

```text
.claude-plugin/                  Claude Code marketplace catalog
.codex-plugin/                   Codex-facing marketplace metadata
.cursor-plugin/                  Cursor-facing marketplace metadata
gemini-marketplace.json          Gemini-facing marketplace metadata
plugins/
  frozen-skills/                 Active consumer-scoped skill plugin
    skills/                      Shared active skills
  codex-thread-organizer/        Dedicated Codex-only plugin package
    skills/                      Codex-only skill source
  distribution.json             Exact shared/consumer package composition
  skill-injector/                Experimental hook plugin
scripts/
  sync_frozen_skills.py          Manifest-driven local synchronizer
_incubator/                      Gated skills and scout snapshots
docs/
  skill-review/                  Quality gate and tracker
  workflows/                     Long-form workflows
```

For the source-to-computer authority model and synchronization process, see
`docs/workflows/skill-authority-and-frozen-sync.md`.

## Validation

This repo does not use a single package manager. Validate the touched surface directly:

```powershell
# One-time: install the packages the validators need (currently PyYAML, used to
# parse SKILL.md frontmatter the same way agent clients do). CI installs the
# same pinned file, so a check that passes locally cannot silently skip there.
python -m pip install -r requirements-validation.txt

# JSON manifests
Get-Content .claude-plugin/marketplace.json -Raw | ConvertFrom-Json | Out-Null
Get-Content .codex-plugin/marketplace.json -Raw | ConvertFrom-Json | Out-Null
Get-Content .cursor-plugin/marketplace.json -Raw | ConvertFrom-Json | Out-Null
Get-Content gemini-marketplace.json -Raw | ConvertFrom-Json | Out-Null
Get-Content plugins/frozen-skills/.claude-plugin/plugin.json -Raw | ConvertFrom-Json | Out-Null
Get-Content plugins/frozen-skills/.codex-plugin/plugin.json -Raw | ConvertFrom-Json | Out-Null
Get-Content plugins/frozen-skills/.cursor-plugin/plugin.json -Raw | ConvertFrom-Json | Out-Null
Get-Content plugins/frozen-skills/gemini-extension.json -Raw | ConvertFrom-Json | Out-Null

# Repo checks
python scripts/validate_manifests.py
python -m unittest discover -s tests -v
git diff --check
```

For skill additions, verify every `plugins/distribution.json` path exists in the correct shared or dedicated package and every native manifest component path resolves inside its package.

## Contribution Rules

- Add a cross-consumer skill under `plugins/frozen-skills/skills/<name>/SKILL.md` only after passing the review gate. Add a restricted skill only in a dedicated plugin package.
- Register every active skill and consumer package in `plugins/distribution.json`; make reviewed changes in its physical package, then synchronize outward.
- Treat managed copies under `~/.agents/skills` as runtime outputs. Do not silently copy local edits back into the reviewed source.
- Keep external scout snapshots under `_incubator/scout/` and never edit scout `source/` after import.
- Keep `plugins/distribution.json`, native plugin metadata, marketplace membership, and release versions aligned. Never place a restricted skill in the shared auto-discovery package.
- Do not commit secret values, client runtime caches, or local installed-skill copies.
