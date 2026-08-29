# Skill Tracker

Active skills live under `plugins/` and are listed in `plugins/distribution.json`; gated
skills live in `_incubator/` and are not installable. Promotion = move the skill into a
package, register it in `plugins/distribution.json`, reconcile the marketplace manifests, bump the
version (authority model: `docs/workflows/skill-authority-and-frozen-sync.md`). Quality bar = the `doppler` skill: clear trigger description (~300 chars), verified
content, scripts actually run, no project-specific leakage, progressive disclosure.

## Marketplace lane

| Skill | Status | Next action |
|---|---|---|
| `agent-github-identity` | gated | Demoted 2026-08-24: the per-write skill adds prompt and operational overhead while GitHub attribution remains environment-specific. Retained under `_incubator/frozen-skills` for reference only; do not distribute or reactivate it without a demonstrated native identity path for each supported agent product. |
| `delegation-contract` | gated | Demoted 2026-08-21: the skill imposed a broad ledger, briefing, return, and verification protocol but shipped no agent-launch or enforcement mechanism. The n=1 evaluation measured contract compliance rather than improved outcomes. Keep in `_incubator/` until its scope is reduced to an honest briefing reference or a complete operational delegation system is implemented and evaluated. |
| `factory-mission-control` | gated | New 2026-08-28: one Notion-controlled router for mission packets, explicitly authorized Factory runs, return evidence, cross-dispatched review, and evidence-backed learning. It is under `_incubator/frozen-skills`, not installed or distributed; it creates no hook, daemon, scheduler, or launch adapter. Before promotion, exercise the select-conversation → packet → authorized headless run → return/review loop on a real bounded mission, then test blocked and scope-change branches plus the learning threshold. |
| `doppler` | active | Trigger narrowed 2026-08-10 to direct secret/injection work; opaque authentication through a trusted client or launcher is a non-trigger. |
| `external-skill-intake` | active | None. |
| `codex-thread-organizer` | active | Codex-only dedicated package; direct-rename contract (invocation = authorization; proposal gate removed 2026-07-31). Scope is the whole Codex-app sidebar: every conversation kind is inventoried and classified `title-mutable` / `not title-mutable`, and only the mutable ones are renamed. |
| `skill-injector` | registered, dormant/untested | Qualify end-to-end or de-register; internal rename from skill-classifier unfinished. |
| `plugin-authoring-guide` | gated | Rework; re-verify against current Claude Code docs. |
| `mcp-deployment-guide` | gated | Re-verify config paths + `mcp/` templates at repo root. |
| `agent-config-megaref` | gated | Light update; reconcile against `D:\_projects\llm-archiver` (canonical for per-tool config paths). |
| `setup-rules` | gated | Remove the uncertain "claude rules list" line; verify install flow. |
| `gh-common-workflows` | gated | Strip NORTH_STAR/Codex-specific assumptions. |
| `stacked-pr-workflow` | gated | Run the 7 PowerShell helpers or cut it. |
| `session-skill-inferencer` | gated | Produced junk auto-skills in May; fix generation quality or cut. |
| `unifi-udm-access` | gated | New 2026-08-13. Surface routing verified live against UniFi Network 10.6.94 / UniFi OS 5.1.27; `scripts/udmssh.py` run end-to-end (reads succeed, exit codes propagate). Before promotion: re-verify the endpoint inventory on a second console and a different Network version, since the Legacy API carries no version contract; confirm the write guidance (`rest/*` PUT replaces the whole object) against an actual round-trip rather than inference. |
| `write-best-in-class-issue` | gated | New 2026-08-15. Mode-scoped issue-authoring skill (Full / Partial / Minimal) distilled from real design/proposal/epic/bug/bump issues, de-personalized to stay repo-independent; main `SKILL.md` routes to a `reference.md` teardown and `examples.md` (Full / Partial / over-ceremonized / Minimal / must-that-was-a-choice). Router validated 2026-08-15 against 10 real issues across all three modes: refined the Minimal/Partial boundary to "mutates a live running system" (not "is it a bump") and made Full-mode beats 2/5/6 conditional. Same day, added Step 2 (requirement or convention: every "must" is sourced, written as a choice, or marked Unknown with a legal exit) and widened beat 4 to a status table (shipped/proposed + required/chosen), from one real agent-authored plan that carried a README convention forward as a requirement; Step 5 now verifies the drafted issue rather than the skill file. Before promotion: run one more Partial-mode pass on a live-mutation bump to confirm the boundary fix; confirm the anti-ceremony guard prevents over-application to operational tasks (the retired `issue-pr-review` failure mode); and run Step 2 against a set of real agent-authored issues/plans that carry "must" statements — at least one where the must was a convention — to see whether the classification is applied and whether it changes the draft. |
| `icepanel-api` | gated | Closest to ready: live-validate diagram push, diff hand-transcribed schemas against live OpenAPI, trim description to ~300 chars, rebalance content per owner (less phase-gate execution, more creativity). |

## Personal lane

Gated reference copies of `~/.agents/skills` — never marketplace candidates unless
de-personalized.

| Skill | Next action |
|---|---|
| `chat-history` | Current personal skill; neutral source-of-truth router. It routes from the requested field to the surface authoritative for that field, keeps recording harness separate from model/provider/account identity, and treats raw harness transcripts as authority for exact tool payloads and raw metadata. The reviewed `chat_history_researcher` profile is a thin optional Luna/high/fast worker for bounded large-corpus searches or long-transcript analysis: it follows the skill and the coordinator's bounded assignment and carries no independent routing or source-authority policy. Repository review has not established live synchronization or current runtime selection for this revision. Before promotion, validate the neutral routes against representative cross-harness retrievals and large-corpus delegation. |
| `agent-atlas` | Recovered factual router for explicit questions about agent harness installation, configuration, hooks, skills, diagnostics, and transcript formats. It owns the reusable per-harness facts that `chat-history` may consult, but it does not retrieve or analyze prior conversations and imposes no configuration workflow or authority hierarchy. Current transcript facts are checked against AgentsView v0.40.1 at commit `9ef48912`; older llm-archiver declarations are labeled as downstream leads rather than current authority. This revision is repository-only and has not been installed or runtime-tested. |
| `ulw-plan` | Gated personal candidate restored 2026-08-25 from the deleted PR #76 Scout snapshot of `oh-my-openagent@4.14.0`. Retains the Prometheus planning workflow, clear/unclear intent routing, two-filter question triage, decision-complete plan bar, and scaffold script. OMO-specific `.omo/` paths, approval language, and harness tool names remain upstream material; adapt and evaluate before any promotion. |
| `ulw-research` | Gated personal candidate restored 2026-08-25 from the deleted PR #76 Scout snapshot of `oh-my-openagent@4.14.0`. Retains exhaustive research waves, EXPAND lead/dead-end reporting, no-worker-recursion, executable verification, claim-ledger gates, and citation-backed synthesis. OMO-specific orchestration/tool names remain upstream material; adapt and evaluate before any promotion. |
| `retrospective` | Revived 2026-07-31 (owner overruled deletion — key skill): timeline script now covers all harnesses via AgentsView `--db` mode. Trigger settled 2026-08-03: manual `/retrospective` invocation, since the Letta Session Reviewer that would have fired it was decommissioned; revisit when the owner's intended successor reviewer exists — confirmed 2026-08-14 as planned but deliberately not shaped like the retired nightly agent (see `tools/session-review/README.md`). Remaining before promotion: de-personalize. |
| `project-docs` | Disabled 2026-08-24 at operator request. The live personal copy was moved to `C:\Users\pmacl\.agents\skills-disabled\project-docs`; the Claude junction was removed; and the `_incubator/personal-skills/project-docs` snapshot is retained as inert review material only. Do not load, sync, promote, or treat this skill as authoritative unless the operator explicitly re-enables it. |
| `skill-analysis` | New live personal skill with an exact incubator mirror. Thin `SKILL.md` routes to purpose, corpus assembly, one-trajectory debrief, synthesis, and examples. Clean-room routing passed, followed by the first historical study: 545 `project-docs` candidate episodes across 291 sessions (543 observed activations plus 2 explicit no-load cases), 24 selected trajectories with one retrieval gap, and all 18 PDM-centered episodes. Separate memo-only synthesis informed narrow wording changes. AgentsView extraction and findings live in `agent-control-plane`; skill text and distribution stay here. |
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
| `explore` | Already deleted from the live root (noticed 2026-07-31; not in quarantine — 155 codex sessions had read it, owner unaware it existed). The explorer-subagent lane in [#71](https://github.com/Coldaine/frozenSkillz/issues/71) is its replacement. |

Deleted forever 2026-07-31 (owner order): `review-claudemd`, `claude-md-enhancer`,
`skill-finder` — live dirs were already broken (empty or missing SKILL.md) and their
incubator copies are removed in the same change; git history is the only archive.
`retrospective` was in the original deletion order, but the owner reversed that the
same day — it is a key skill. Revived from a recovered copy with the timeline script
extended to all harnesses (see Personal lane row). Also removed the empty
`~/.codex/skills/codex-primary-runtime/` dir (live only, never tracked here).

## Fleet effectiveness review

**Process status (2026-08-10): exploratory, not a proven recurring evaluator.** The July work ran
a full-corpus activation census, corrected Codex's hidden `SKILL.md` read channel, and manually
regraded selected transcripts. The behavior-first reviewer was calibrated through evolving v1-v3
prompts, but the final v4 wording did not receive its own calibration run. The Letta schedule was
registered but never demonstrated a production nightly batch before it was decommissioned on
2026-08-03. Consequently, the results below are useful historical findings—not a fleet-wide
appropriate-use rate, a causal effectiveness estimate, or evidence that monitoring is currently
running. The replacement method is `docs/workflows/skill-evaluation.md`.

### Retired July grading rule (historical only)

The July work used subagents to read transcripts around recent fires and treated the owner's
closing reaction as a “ground truth” signal. That grading rule is removed: an explicit owner
response is useful evidence, while silence is not acceptance, and it does not supply a global
grade or causal conclusion. AgentsView `health_score` remains only a historical thrash detector
(tool failures / edit churn; 85% of all sessions grade A), never a success measure. A historical
“fire” was usually a `SKILL.md` read, so editing or studying a skill could count as usage.

**2026-07-28 corpus analysis** (~7,300 sessions; instrument lives in the local
`agent-control-plane` learnings repo — `projects/agent-ceremony-*.md`,
`tools/ceremony_metrics.py`, `tools/classified.csv` = all 308 skills classified.
Machine-local evidence: the verdicts below are the durable record, the corpus is
not rerunnable from this repository):

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
