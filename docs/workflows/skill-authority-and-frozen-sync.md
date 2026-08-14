# Skill Authority and Computer Synchronization

This repository has two deliberate authority lanes. Distribution-listed active skills are reviewed here and synchronized outward to consumer-specific roots. Personal or gated skills are authored in the live personal root and mirrored into `_incubator/` for durable review. Mixing those directions recreates the drift this workflow is designed to prevent.

## Authority Model

### Active distributed skills

An active consumer distribution is the composition of:

1. shared skills under `plugins/frozen-skills/skills/<skill-name>/`, listed in `plugins/distribution.json:shared`; and
2. restricted skills in dedicated `plugins/<package>/skills/<skill-name>/` packages, listed only in approved `consumer_packages` and consumer lanes.

`plugins/distribution.json` is the exact synchronizer allowlist. The synchronizer refuses to run if its release identity/version differs from native manifests, and it loads the shared package plus only packages declared for the explicitly selected consumer. For this lane, the repository copy is authoritative and each consumer-specific managed copy is runtime output.

The physical split is a packaging boundary, not decoration. Claude Code automatically discovers every skill below a plugin's default `skills/` directory and has no per-skill manifest exclusion. Current Codex ingestion also requires a plugin's `skills` path to resolve to that package's default `skills/` directory. Therefore a restricted skill needs a dedicated package, and only approved consumer catalogs may expose it. See the [Claude plugin structure contract](https://github.com/anthropics/claude-code/blob/main/claude-code/plugins/plugin-dev/skills/plugin-structure/SKILL.md) and [OpenAI plugin packaging path rules](https://developers.openai.com/plugins/build/plugins#path-rules).

### Personal or gated skills

Personal skills that are not in the active distribution are authored under:

```text
~/.agents/skills/<skill-name>/
```

When this repository tracks one of those skills, its durable evaluation mirror lives under:

```text
_incubator/personal-skills/<skill-name>/
```

The live personal copy is authoritative for this lane. `_incubator/` is review material and is never installed by the active synchronizer.

| Surface | Role |
|---|---|
| `plugins/frozen-skills/skills` | Reviewed shared active source, natively auto-discovered across consumers. |
| Dedicated `plugins/<package>/skills` | Reviewed active source restricted to approved consumers. |
| `plugins/distribution.json` | Exact shared-plus-consumer package composition for synchronization, plus any named deployment subsets. |
| Four native `plugins/frozen-skills` manifests | Client packaging metadata and shared plugin identity/version contract. |
| Consumer-specific skill root | Managed runtime destination for the selected consumer's active skills. Codex defaults to `~/.codex/skills`. |
| `~/.agents/skills` | Shared authoring/discovery source for personal or gated skills; not a safe default for consumer-restricted active sync. |
| `_incubator/personal-skills` | Durable review mirror for tracked personal/gated skills; never installed. |
| Client plugin/cache directories | Client-managed runtime state, when a client has its own installer. |

The management record at the selected destination's `.frozen-skills-sync.json` names its consumer, and its deployment when one is selected, and distinguishes managed copies from unrelated skills. A destination managed for one consumer cannot be reused for another consumer, and a destination managed by one deployment cannot be reused by another deployment or by the full consumer distribution.

Legacy schema-1 state from the old shared-root synchronizer is rejected instead of guessed or auto-migrated. Use a fresh consumer-private destination, or perform a separately reviewed migration after reconciling every existing skill.

## Synchronize Active Skills to a Computer

Clone this repository once on each computer. After cloning or pulling a new revision, inspect and apply the local plan:

```powershell
python scripts/sync_frozen_skills.py --consumer codex --check
python scripts/sync_frozen_skills.py --consumer codex --apply
```

Both commands validate the distribution first. `--check` writes nothing and exits with:

- `0` when every active skill and the management record are current;
- `1` when a safe install, update, adoption, or removal is pending;
- `2` when the distribution is invalid or local content conflicts with it.

`--apply` writes only the selected consumer's active skills and management record. Codex defaults to its private `~/.codex/skills` root. A matching pre-existing skill is adopted without rewriting it. A previously managed, unchanged copy is safely updated. An unmanaged or locally modified copy is reported as a conflict and left untouched.

Every run must select either `--consumer` or `--deployment`. Claude, Cursor, and Gemini also require `--destination` until a consumer-private default has been explicitly qualified. This prevents the synchronizer from guessing a root that may be shared with another client.

For a non-default root:

```powershell
python scripts/sync_frozen_skills.py --consumer claude --apply --destination "C:\path\to\claude-skills"
```

On macOS or Linux, the same Python command works with POSIX paths.

The destination must be disjoint from the repository. The synchronizer rejects a destination inside the checkout and a destination that contains the checkout. It never reverse-synchronizes installed content into reviewed active source.

## Skill Consumer Shapes

Three different things consume material from this repository. Only the first is modeled by `--consumer`, and conflating them is what produces placeholder consumers and invented sync lanes.

| Shape | Example | How it consumes | Modeled as |
|---|---|---|---|
| Client | Claude, Codex, Cursor, Gemini | Discovers skills from a client-specific root; needs that client's packaging format and plugin manifest | The `--consumer` axis |
| Runtime | Hermes | Reads bare `SKILL.md` directories from a path; no packaging format, no manifest | A consumer-less deployment, restricted to `shared` skills |
| Service | Letta | Consumes no skills at all | Nothing — deliberately outside the sync lane |

**Clients.** The four-consumer enum is the set this repository has decided to package for. It is not the set of skill-running clients on the operator's machines: `~/.kilo/skills` currently holds four live skills that frozenSkillz does not manage and that carry no `.frozen-skills-sync.json`. Adding a fifth consumer is an explicit decision — new manifests, marketplace entries, and a qualified destination — not something that happens by discovering an unmanaged skill root.

**Runtimes.** A runtime has a filesystem path and nothing else. See [`docs/deployments/hermes.md`](../deployments/hermes.md) for the worked example.

**Services.** The former Letta Session Reviewer was decommissioned on 2026-08-03. Its
historical materials remain under `tools/session-review/`, but no cloud agent or local
launcher consumes them. If a replacement is created in Letta, it remains outside the skill
distribution lane unless an explicit deployment contract is added.

## Deployment Subsets

`--consumer` selects a client *format*, not a skill subset: a destination synchronized for a consumer always receives that consumer's entire shared-plus-restricted set. A destination that must receive only part of it — a standing runtime like Hermes, for example — is described by a named deployment.

Deployments live in the optional `deployments` object of `plugins/distribution.json`, so the distribution stays the single source of truth. There is no separate registry directory.

There are two kinds, distinguished by whether the deployment declares a `consumer`.

**Client-scoped deployment.** The destination belongs to one of the four supported clients and wants only part of that client's distribution. It names its consumer and may select from that consumer's shared-plus-restricted set:

```json
"deployments": {
  "codex-minimal": {
    "description": "Trimmed Codex set for a low-context workstation.",
    "consumer": "codex",
    "skills": ["doppler", "codex-thread-organizer"]
  }
}
```

**Runtime deployment.** The destination is not a Claude/Codex/Cursor/Gemini client at all — a service that reads bare `SKILL.md` directories, for example. It omits `consumer` entirely and may select **only shared skills**, because it has no client packaging format to render a consumer-restricted package into:

```json
"deployments": {
  "hermes-ops": {
    "description": "Reviewed shared skills exposed to the standing Hermes operations runtime. Hermes is a bare-SKILL.md service runtime, not a client: it reads skill directories from a read-only bind mount, so it declares no consumer.",
    "skills": ["doppler", "pdm-cli-operations"]
  }
}
```

Do not give a non-client runtime a placeholder consumer. A consumer that is inert today because every selected skill happens to be shared becomes a false statement the moment a restricted skill is added, and the omission is what makes the shared-only constraint enforceable.

Every listed skill must already be active in the aligned manifests for that deployment's scope — its consumer's set, or `shared` when it declares none. A deployment cannot select a skill the distribution does not carry, and a runtime deployment that names a consumer-restricted package is rejected by name.

```powershell
python scripts/sync_frozen_skills.py --check --deployment hermes-ops --destination /srv/hermes/skill-sets/hermes-ops --prune
python scripts/sync_frozen_skills.py --apply --deployment hermes-ops --destination /srv/hermes/skill-sets/hermes-ops --prune
```

Rules specific to deployment mode:

- `--deployment` requires an explicit `--destination` and mandatory `--prune`; there is no default deployment destination.
- `--deployment` and a bare `--consumer` run are alternative ways to pick the skill set. A deployment supplies its own consumer, so passing a `--consumer` that disagrees with it is an error, and passing `--consumer` at all alongside a runtime deployment is an error.
- A destination is owned by exactly one deployment (or by the full, undeployed consumer distribution) for its lifetime. Reusing a destination under a different deployment, or under the full distribution, is a conflict. Ownership is recorded in the destination's `.frozen-skills-sync.json`, which omits `consumer` for a runtime deployment.
- Pruning is exact: any top-level destination content that is neither an active deployment skill nor a still-recorded retired one is reported as a conflict, not silently ignored.
- `python scripts/validate_manifests.py` validates every deployment against the active distribution as part of ordinary manifest validation.

## Personal/Gated Skill Sync

After a deliberate rewrite or material fix of a personal skill that already has an incubator row:

1. edit and validate `~/.agents/skills/<name>/`;
2. mirror the live tree into `_incubator/personal-skills/<name>/`, including deletion of removed files;
3. update the row or notes in `docs/skill-review/tracker.md`; and
4. commit and push that mirror on a branch/PR in this repository in the same session.

A GitHub issue alone is not the durable rewrite. Uncommitted incubator files are not “in frozenSkillz.” “Stay gated” means do not add the skill to a shared/dedicated active package or `plugins/distribution.json`; it does not mean skip Git.

## Completion Contract

When the operator asks to rewrite, fix, sync, or land tracked skill material into this repository (including scout/intake under `_incubator/` and related tracker updates), the work is incomplete until the applicable authority lane is durable:

| Required | Not sufficient |
|---|---|
| Active source under `plugins/` updated, or live personal source updated | Opening an issue describing the rewrite |
| Matching active or incubator repository path updated | Copying files only in an uncommitted worktree |
| Tracker updated when status/work notes change | Deferring repository publication “for later” |
| Commit + push, with a PR when not already on one | A local-only sync unless explicitly requested |

Exception: the operator explicitly says “live-only, do not touch the repo.” Otherwise, repository landing is part of the task.

## Removal and Conflict Rules

Removing a skill from one consumer lane in `plugins/distribution.json` does not delete it from that consumer's managed destination during an ordinary apply. This makes removal a separate, reviewable operation:

```powershell
python scripts/sync_frozen_skills.py --consumer codex --check --prune
python scripts/sync_frozen_skills.py --consumer codex --apply --prune
```

Pruning removes only previously managed content that still matches its recorded digest. A locally modified retired skill becomes a conflict.

`--force` permits overwriting a conflicting active skill or deleting a conflicting retired skill. Review the exact reported skill first. Force is not the normal update path and does not override a target that changes after planning.

## Pinning From a Production Consumer

A deploy script, service unit, or standing runtime that pins a specific
frozenSkillz commit for its sync must pin a commit reachable from `main`. A pin
that only resolves on an unmerged or abandoned branch is not reviewed
distribution: when that branch is deleted the consumer's sync fails, and until
then it is running content that no review gate ever approved.

## Editing and Promotion Flow

For an already active skill, make the reusable change in its shared or dedicated package, validate it, review it, merge it, and then synchronize computers outward from that repository revision.

If an active skill was accidentally edited in a local runtime copy, do not run `--force` immediately. Compare it with the repository source, deliberately port any reusable change into the repository, validate and review it, then synchronize. The conflict is evidence that authority must be reconciled.

New skills enter `_incubator/` and pass the gate in `docs/skill-review/tracker.md` before promotion. Promotion requires moving or adapting the skill into the shared package or a dedicated consumer package, registering it in `plugins/distribution.json`, exposing dedicated packages only in approved marketplaces, and aligning versions. The next synchronization installs it only for the composed consumer allowlists.

## Marketplace Installation Is Different

Claude Code supports this repository as a marketplace:

```text
/plugin marketplace add Coldaine/frozenSkillz
/plugin install frozen-skills@coldaine-skills
```

That installs the shared `frozen-skills` package into a Claude-managed plugin copy. It does not contain or install the separate `codex-thread-organizer` package, which appears only in the Codex catalog. Cursor and Gemini remain separately validated packaging surfaces. `sync_frozen_skills.py` is the repository-owned consumer-selecting local installation path.

## Required Checks

Before publishing a source or synchronization change:

```powershell
python scripts/validate_manifests.py
python -m unittest discover -s tests -v
git diff --check
```

For JSON manifests touched in the same change, also parse them with `ConvertFrom-Json`.

For an end-to-end smoke test, use a unique temporary directory, assert both commands, and remove only that verified temporary path:

```powershell
$tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$target = Join-Path $tempRoot ("frozen-skills-smoke-" + [guid]::NewGuid().ToString("N"))
try {
    python scripts/sync_frozen_skills.py --consumer codex --apply --destination $target
    if ($LASTEXITCODE -ne 0) { throw "Smoke-test apply failed: $LASTEXITCODE" }
    python scripts/sync_frozen_skills.py --consumer codex --check --destination $target
    if ($LASTEXITCODE -ne 0) { throw "Smoke-test check failed: $LASTEXITCODE" }
} finally {
    $resolvedTarget = [System.IO.Path]::GetFullPath($target)
    if ($resolvedTarget.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -and
        (Test-Path -LiteralPath $resolvedTarget)) {
        Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
    }
}
```

## Reporting

For an active distribution change, report:

- active source paths, approved consumers, and manifest/version changes;
- validation and synchronization checks;
- destination conflicts intentionally left unresolved; and
- the repository revision synchronized to each computer when deployment is in scope.

For a personal/gated or incubator/scout landing change, report:

- the live path compared and incubator path changed;
- tracker or promotion status changes;
- any live-versus-incubator delta intentionally left unsynced; and
- branch, commit, and PR URL unless the operator requested live-only work.
