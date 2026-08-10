# Skill Tracker

Active skills live under `plugins/` and are listed in `plugins/distribution.json`; gated
skills live in `_incubator/` and are not installable. Promotion = move the skill into a
package, register it in `plugins/distribution.json`, reconcile the marketplace manifests, bump the
version (authority model: `docs/workflows/skill-authority-and-frozen-sync.md`). Quality bar = the `doppler` skill: clear trigger description (~300 chars), verified
content, scripts actually run, no project-specific leakage, progressive disclosure.

## Marketplace lane

| Skill | Status | Next action |
|---|---|---|
| `agent-github-identity` | active | None — mechanism proved end-to-end 2026-08-10 through two agent products (bot-attributed commit, pull request, and issue comment each verified via the API). Carries mechanism only; agent roster, App IDs, and helper paths stay in the consuming environment's operational repository. Per-product wiring documents only the two surfaces actually verified and gives a procedure for the rest rather than guessing config keys. |
| `delegation-contract` | active | None — adapted doctrine validated for contract compliance and single-writer coordination; outcome-quality evidence remains intentionally limited to the recorded n=1 eval. |
| `doppler` | active | Verify content is still current (owner 2026-07-31); otherwise reference standard. |
| `external-skill-intake` | active | None. |
| `omc-reference` | active | None. |
| `pdm-cli-operations` | active | None — live-qualified 2026-07-20. |
| `codex-thread-organizer` | active | Codex-only dedicated package; direct-rename contract (invocation = authorization; proposal gate removed 2026-07-31). Scope is the whole Codex-app sidebar: every conversation kind is inventoried and classified `title-mutable` / `not title-mutable`, and only the mutable ones are renamed. |
| `skill-injector` | registered, dormant/untested | Qualify end-to-end or de-register; internal rename from skill-classifier unfinished. |
| `plugin-authoring-guide` | gated | Rework; re-verify against current Claude Code docs. |
| `mcp-deployment-guide` | gated | Re-verify config paths + `mcp/` templates at repo root. |
| `agent-config-megaref` | gated | Light update; reconcile against `D:\_projects\llm-archiver` (canonical for per-tool config paths). |
| `setup-rules` | gated | Remove the uncertain "claude rules list" line; verify install flow. |
| `gh-common-workflows` | gated | Strip NORTH_STAR/Codex-specific assumptions. |
| `stacked-pr-workflow` | gated | Run the 7 PowerShell helpers or cut it. |
| `skill-manager` | gated | Verify `skills.sh` registry assumptions or cut it. |
| `session-skill-inferencer` | gated | Produced junk auto-skills in May; fix generation quality or cut. |
| `icepanel-api` | gated | Closest to ready: live-validate diagram push, diff hand-transcribed schemas against live OpenAPI, trim description to ~300 chars, rebalance content per owner (less phase-gate execution, more creativity). |

## Personal lane

Gated reference copies of `~/.agents/skills` — never marketplace candidates unless
de-personalized.

| Skill | Next action |
|---|---|
| `chat-history` | Current personal skill; staged semantic-localization router implemented 2026-08-03. One or two `chat_history_researcher` workers localize through KCap, AgentsView, and Pieces, return brief candidate maps, then resume for bounded analysis written to temporary Markdown artifacts. Live copy synchronized; custom-agent profile uses Luna/high/fast and the reviewed global-config lane. Exact named-agent activation, installed-skill loading, and temporary-artifact writing passed on Codex CLI 0.146.0; forward-test a real two-stage retrieval before promotion. |
| `retrospective` | Revived 2026-07-31 (owner overruled deletion — key skill): timeline script now covers all harnesses via AgentsView `--db` mode; needs trigger decision (see SKILL.md Triggering); then de-personalize. |
| `project-docs` | Gated pending de-personalization. |
| `skill-analysis` | New live personal skill with an exact incubator mirror. Thin `SKILL.md` routes to purpose, corpus-assembly, one-trajectory debrief, synthesis, and example resources. A clean-room routing test passed; the real `project-docs` corpus pilot remains required before promotion. Analysis artifacts belong in `agent-control-plane`; skill text and regression cases stay here. |
| `skill-install` | Verify recipes. |
| `run-opencode` | Fix driver.mjs header comment re: profile writes. |
| `edit-opencode-config` | Fix canonical-root drift. |
| `phantom-substrate-inheritance` | Review. |
| `rich-visual-responses` | Keep — regraded 2026-07-31: formatting applied in 23/44 firing sessions vs 2/127 baseline. |
| `insight-extractor` | Add YAML frontmatter; fix contradictory `~/.Codex` vs `~/.claude` paths. |
| `nlm-skill` | Confirm provenance. |
| `google-stitch-ui-designer` | Confirm provenance. |
| `context7-mcp` | Complete rewrite (owner 2026-07-31) — the MCP is useful, the skill isn't. Supersedes the narrow-trigger fix; 27/39 fires never called the MCP. |
| `patrickspowerfulpresentations` | Incubating; stays personal. |
| `audio-producer` | Incubating; stays personal. Broadside examples are worked evidence — keep. |
| `explore` | Already deleted from the live root (noticed 2026-07-31; not in quarantine — 155 codex sessions had read it, owner unaware it existed). The explorer-subagent lane in [#71](https://github.com/Coldaine/frozenSkillz/issues/71) is its replacement. |

Deleted forever 2026-07-31 (owner order): `review-claudemd`, `claude-md-enhancer`,
`skill-finder` — live dirs were already broken (empty or missing SKILL.md) and their
incubator copies are removed in the same change; git history is the only archive.
`retrospective` was in the original deletion order, but the owner reversed that the
same day — it is a key skill. Revived from a recovered copy with the timeline script
extended to all harnesses (see Personal lane row). Also removed the empty
`~/.codex/skills/codex-primary-runtime/` dir (live only, never tracked here).

## Intake queue

- `obra/superpowers` `v6.1.1` (`d884ae04edebef577e82ff7c4e143debd0bbec99`) — scout,
  forensic review in progress at `_incubator/scout/2026-07-23-obra-superpowers/`.
  Pinned 172-file source and 14-skill doctree. `brainstorming` reviewed B- with moderate
  confidence. `dispatching-parallel-agents` revised to B- after an AgentsView audit found
  direct successful and failed Codex uses; confidence is strong for observed Codex
  behavior and moderate cross-harness. Remaining 12 skills are intentionally ungraded
  pending one-at-a-time review. **2026-07-31: the live pack was removed from the codex
  plugin cache**, so this pinned snapshot is now the only source; the scout's purpose
  shifts from adopt-review to salvage-mining for the rebuild lanes in
  [#71](https://github.com/Coldaine/frozenSkillz/issues/71). Leftover
  `[marketplaces.superpowers-dev]` + `superpowers:*` blocks in `~/.codex/config.toml`
  may re-sync the pack — cleanup tracked in #71.

Kubernetes adopt shortlist (premise corrected 2026-07-23 — coldaine-homelab
reconciles via Flux, not Helmfile; re-scored in
[coldaine-homelab#92](https://github.com/Coldaine/coldaine-homelab/issues/92),
closed 2026-07-25). Every external repo below goes through
`external-skill-intake` before anything is mined or adapted:

- `fluxcd/agent-skills` — adopt-pinned.
- `gitops-cluster-debug` — fork, not adopt raw (hard-requires
  `flux-operator-mcp`/`FluxInstance`; homelab runs plain `flux bootstrap`).
- `kstack` — vendor selectively (ask-before-every-mutation default and 15-minute
  cache don't fit a convergence loop).
- LukasNiessen/kubernetes-skill — take the core workflow (prove-before-mutate).
- Author a thin `k8s-platform-operator` glue skill, seeded from the
  [ionos cluster-api-provider-proxmox AGENTS.md](https://github.com/ionos-cloud/cluster-api-provider-proxmox/blob/main/AGENTS.md);
  implement authored-vs-applied against Flux Kustomizations/HelmReleases, not Helmfile.

Parked regardless of reconciler: whole Aidas dump; kubectl-MCP packs;
clouddrove/Jeffallan/sickn33/wshobson mutate cookbooks; Omni-as-CAPMOX;
kagent apply-after-generate (revisit after CAPI/CAPMOX/Flux is stable).

Scouts:

- danilo-aguiar-br/context7-cli — scout · **adopt-as-external-tool** (2026-07-31,
  owner-requested). Snapshot at `_incubator/scout/2026-07-31-context7-cli/` pinned to
  v0.5.2 / `e2f1935`. Rust CLI for the Context7 REST API with multi-key rotation
  (`CONTEXT7_API_KEYS=a,b,c` → shuffle + exponential backoff) — directly fixes the
  quota-blocking that sank `context7-mcp`. Security read clean: sole endpoint
  `context7.com/api`, zero process execution, no build.rs, zeroize'd keys, crates.io
  package matches repo. Young/unvetted (0 stars, single-day upload) → binary built from
  the reviewed snapshot, version pinned, re-review any update. Consumed by the
  `context7-mcp` full rewrite in
  [#71](https://github.com/Coldaine/frozenSkillz/issues/71); key rotation is ToS-gray
  (multiplies free-tier quota) — owner's call, recorded in the scout's `analysis.md`.

- Rylaa/fable5-opus5-orchestrator — scout · adapt-concept-only (2026-07-31).
  Snapshot at `_incubator/scout/2026-07-31-rylaa-fable5-opus5-orchestrator/`;
  tmux layer discarded. Live eval under its `evals/runs/` required before any
  Component A pattern lands in `plugins/` or `docs/`.
  First live eval landed 2026-07-31 (`evals/runs/2026-07-31-spawn-prompt-richness.md`).
  Concluded **no promotion**, and the gate above **stays closed**: it ran two arms
  instead of three and its comparative measurement is unusable, because the candidate
  arm was instrumented with the guard's own metrics log, which records nothing at or
  below the 1500-char threshold it was supposed to be measuring across. What it does
  establish, from the uncensored control arm: default spawn prompts run 1298–1378
  chars — *below* the gate — so the guard is near-inert as shipped; and it is
  Windows-portable via `python3` → `py -3`. Recommendation if ever adopted: check that
  a spawn prompt *contains* the required contract sections rather than that it is long.

## Fleet effectiveness review

**Process status (2026-08-10): exploratory, not a proven recurring evaluator.** The July work ran
a full-corpus activation census, corrected Codex's hidden `SKILL.md` read channel, and manually
regraded selected transcripts. The behavior-first reviewer was calibrated through evolving v1-v3
prompts, but the final v4 wording did not receive its own calibration run. The Letta schedule was
registered but never demonstrated a production nightly batch before it was decommissioned on
2026-08-03. Consequently, the results below are useful historical findings—not a fleet-wide
appropriate-use rate, a causal effectiveness estimate, or evidence that monitoring is currently
running. The replacement method is `docs/workflows/skill-evaluation.md`.

How grading works: a skill's grade comes from subagents reading transcripts around recent
fires — (1) did the guidance visibly shape the agent's actions, (2) was the owner's next
message acceptance or a correction, and (3) did the session end with an owner-visible
outcome — the owner's *closing* reaction is the ground truth, and self-written tests
passing is not an outcome. AgentsView `health_score` is only a thrash detector
(tool failures / edit churn; 85% of all sessions grade A) — never a success measure. A
"fire" is usually just a SKILL.md read, so editing or studying a skill counts as usage.

**2026-07-28 corpus analysis** (~7,300 sessions; instrument lives in the local
`agent-control-plane` learnings repo — `projects/agent-ceremony-*.md`,
`tools/ceremony_metrics.py`, `tools/classified.csv` = all 308 skills classified.
Machine-local evidence: the verdicts below are the durable record, the corpus is
not rerunnable from this repository):

- **Superpowers pack is the codex-ceremony driver.** Codex is the heaviest skill user
  (60% of sessions read SKILL.md via shell — untagged, so earlier counts missed it); top
  reads are `~/.codex/plugins/cache/` superpowers: `using-superpowers` (622 sessions),
  `verification-before-completion` (306 — the "Iron Law" register). Lever applied
  2026-07-30: operational-mode override in `~/.codex/AGENTS.md`, PR self-review loop
  scoped to substantial changes. **Escalated 2026-07-31: owner removed the whole pack
  from the codex cache.** Capabilities that died with it (delegation, planning,
  debugging, git-worktree lanes) get rebuilt without the ceremony register —
  [#71](https://github.com/Coldaine/frozenSkillz/issues/71). Owner nuance, same day:
  the pack's *auto-fire bootstrap* (`using-superpowers`) was the one part worth
  keeping — it is why codex out-fires every other harness on skills — so #71 carries a
  skill-activation-bootstrap lane (owner previously ran a hook for the same job); only
  the ceremony payload dies unreplaced.
- `doppler`, `project-docs`, `chat-history` (trigger narrowed to forensic-only
  2026-07-30), `parallel-web-search`, `canvas`, `create-hook` earn their keep.
- `git-master`: an `oh-my-openagent` built-in, opencode-only — not Codex. Dead since
  Jul 1 (opencode lane fading); its bad numbers came from long thrashy sessions in a
  harness no longer used, and the shipped version has since been rewritten. Ignore.
- `issue-pr-review` zombie fixed 2026-07-30: cursor kept loading it from `_disabled`
  *inside* the discovery root. Quarantine is now `~/.agents/skills-disabled/` (outside
  every scan root) — use it for all future kills.
- Long tail: 46% of all skills fired exactly once; ~10 re-implementations of the same
  planning skill (ralplan/hyperplan/ulw-plan/ultragoal) — consolidate.

**2026-07-31 transcript regrade** of the live 30-day roster (12 skills × 3 recent
sessions each, read by subagents):

- **EARNS:** `babysit` (note: never user-invoked — cursor auto-fires it on "land the
  PRs"-type prompts), `create-skill`, `skill-install`,
  `external-skill-intake`; `rich-visual-responses` — prior "cosmetic cruft" verdict
  **refuted** (23/44 firing sessions apply its formatting vs 2/127 baseline, zero owner
  complaints); `context7-mcp` when used — prior "meta-inflated" verdict **refuted**, real
  doc pulls shaped work, but 27/39 fires load-and-never-use and the service was
  quota-blocked in 10+ sessions → superseded 2026-07-31: owner escalated to a
  complete rewrite (see Personal lane row);
  `hangar-logbook` — keep, but revise persistence to markdown-first (owner asked
  verbatim 2026-07-27; it still writes into `.ts` files).
- **IGNORED:** `feature-research` — its sole prescriptive step ran 0 times across all
  examined sessions; pure context tax. **Disabled 2026-07-31** (moved to quarantine).
- **META-ONLY:** `icepanel-api` — recent fires are self-study/rewrite; fold in the
  owner's creativity-vs-phase-gates complaint before promotion.
- **INSUFFICIENT DATA:** `unity` — old "sole mutator" text caused the 2026-07-21 blowup;
  rewritten text unproven, re-grade after a real Editor session. `retrospective` — live
  skill half-deleted ~Jul 16 (SKILL.md gone, `scripts/` orphaned): restore deliberately
  or delete the remnant. **Resolved 2026-07-31: deleted, then revived the same day by
  owner order** (see Personal lane).
- **Owner-overturned (2026-07-31): `unity-editor-ops` EARNS → NOT PROVEN.** The graded
  "success" session was a 100-tick /loop that ran with Unity/MCP down almost the whole
  time; the batch-mode recipe let it keep generating self-written, self-graded green work
  ("196/196 passed") while nothing owner-visible changed. Owner in-session: "you can
  barely even see the ships"; closing message: "I feel like we never really made any
  progress did we?" Rubric fix baked in below: skill compliance ≠ session success — every
  grade must include an outcome check (owner's closing reaction + something owner-visible
  changed), and self-written tests passing is not an outcome.

**2026-07-31 owner review of the OpenAI codex pack** (`~/.codex/plugins/cache/openai-curated-remote/github/` — OpenAI-managed, version-pinned: override via AGENTS.md routing or a competing skill, never edit in place):

- `github` (296 codex sessions): a triage router — classify → route → resolve-context gates
  before any action, and its publish path deliberately ends at a **draft** PR. Owner verdict:
  too many gates; superseded by the ship-to-merged skill lane in
  [#71](https://github.com/Coldaine/frozenSkillz/issues/71).
- `yeet` (117): sound commit → push → open-PR mechanics (branch naming, scoped staging), but
  stops at a draft PR and interviews the user about scope. Seed material for ship-to-merged.
- `gh-address-comments` (120) / `gh-fix-ci`: keep — the checks-fixing loop feeds
  ship-to-merged.
- `project-docs` (208): owner affirmed keep.

## Loose ends

- `mcp/` templates at repo root belong to `mcp-deployment-guide`.
- `docs/stacked-pr-workflow/` supplementary docs belong to `stacked-pr-workflow`.
