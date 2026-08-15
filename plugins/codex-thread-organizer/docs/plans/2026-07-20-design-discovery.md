# Codex Sidebar Organizer — Design Discovery

## Status

- Phase: requirements recovery and owner interview
- Design approval: not yet granted
- Implementation: not started
- Skill: not created
- Scheduled automation: not created
- Next gate: owner reviews recovered requirements, then the design interview resumes one consequential decision at a time

This document recovers the interrupted design turn from Codex thread `019f73e9-4471-7661-8797-f23486e03fdb`. It is active working material, not settled architecture. When design discovery finishes, lasting intent belongs in `NORTH_STAR.md`, technical decisions belong in `architecture.md` and `docs/decisions/`, and this plan should be deleted after its executable successor is approved.

Authority note: `[OWNER]` records direct or faithfully recovered owner requirements. `[INFERRED]` and `[OPEN]` are candidate design material, not implementation authorization.

## Owner's concept, reflected back

[OWNER] The desired core is a Codex skill that acts on actual persisted Codex threads. It automatically inspects the available thread universe, infers what each thread is actually for, gives it a compact human-readable visual identity, represents important project or workstream relationships, and keeps the organization current through scheduled runs.

[OWNER] The title itself becomes a rich visual language. It may carry between one and five emoji-like symbols, followed by words that preserve the specific subject and outcome. The symbols are useful because they survive narrow-sidebar truncation and let the user recognize classes of work before reading every word.

[OWNER] The reason this is exciting is not merely cleaner naming. Codex has accumulated valuable decisions, investigations, implementations, failures, and unfinished work, but the flat interface makes that history cognitively inaccessible. If the latent structure can be projected back into the existing sidebar, the past work becomes navigable without waiting for a new first-party organizational interface.

## Proven feasibility

The earlier spike established the following direct evidence:

| Capability | Result |
|---|---|
| Inventory recent Codex threads | 30-thread cohort recovered successfully |
| Read enough history to understand thread evolution | 50 transcript pages and 271 turns used in the final report |
| Generate distinct semantic titles | 30 unique proposals; 25 high-confidence, five medium-confidence |
| Preserve related-project distinctions | Broadside plan, completion, and correction threads received distinct identities |
| Apply supported title changes | Two authorized live renames succeeded |
| Preserve Unicode | Emoji, a variation selector, and an em dash read back exactly |
| Pin/archive operations | Exposed by the native Codex environment; not exercised in the live title trial |
| Scheduled execution | Codex scheduled tasks can explicitly invoke skills; no task has been created for this project |

See `evidence/codex-thread-title-first-pass.md` and `evidence/codex-thread-title-methodology.md`.

## Recovered requirement inventory

These IDs organize discovery; only requirements promoted into `NORTH_STAR.md` after owner review become authoritative.

| ID | Requirement | Provenance | State |
|---|---|---|---|
| D-R1 | Inventory accessible Codex threads with stable thread IDs and metadata. | inferred from executed spike | candidate |
| D-R2 | Read enough transcript history to identify dominant purpose, pivots, outcome, and remaining work. | owner + executed spike | candidate |
| D-R3 | Generate concrete natural-language titles of approximately 5–12 words, allowing longer titles when recognition materially improves. | owner-authored spike | candidate |
| D-R4 | Prefix titles with a configurable density of one to five emoji-like semantic symbols. | owner | candidate |
| D-R5 | Use project/workstream groupings when they materially improve recognition. | owner | candidate |
| D-R6 | Keep related threads distinguishable by phase or outcome instead of collapsing them under a project name. | owner-approved audit | candidate |
| D-R7 | Operate read-only for proposal/review before applying bulk changes. | owner-approved audit workflow | candidate |
| D-R8 | Support on-demand and scheduled maintenance. | owner | candidate |
| D-R9 | Verify every applied mutation by reading it back. | inferred safety requirement | candidate |
| D-R10 | Preserve decisions, evidence, and requirements in a Git repository. | owner | accepted |
| D-R11 | Consider pin/archive triage in addition to titles. | prior discussion | open |
| D-R12 | Provide a richer visualization or dashboard in addition to changing the native sidebar. | owner interest | open |
| D-R13 | Preserve explicit user overrides across future classifications. | inferred need | open |
| D-R14 | Avoid repeatedly renaming stable threads simply because a scheduled run sees new activity. | inferred need | open |
| D-R15 | Support rollback of an applied batch. | inferred safety requirement | open |
| D-R16 | Perform a descriptive candidate pass and a separate critique/revision pass across the title set before application. | owner-authored spike | candidate |
| D-R17 | Audit every batch with thread IDs, old/final titles, confidence, rationale, verification, totals, failures, mutation mechanism, changed stores/APIs, backup location when applicable, and recurring-workflow issues. | owner-authored spike | candidate |
| D-R18 | Prefer supported Codex title operations; any direct metadata fallback requires closed clients, authoritative-store discovery, timestamped backup, practical atomicity, and preservation of unrelated state. | owner-authored spike, clarified by native-operation trial | candidate |
| D-R19 | Act on actual persisted Codex threads, not ChatGPT web chats, tab titles, extensions, or display-only aliases. | owner-authored spike | candidate |
| D-R20 | Support reviewing the complete accessible inventory; bounded cohorts remain valid for evaluation and staged rollout. | owner-authored spike + executed 30-thread cohort | candidate |
| D-R21 | After an authorized batch scope, apply refined titles without per-thread confirmation and verify every write. | owner-authored spike | candidate |
| D-R22 | Review related accessible threads for each repository or project family together to determine whether later work has made an older thread no longer relevant or superseded. | owner, 2026-07-21 | accepted |

## Candidate visual grammar

The saved prototype maps symbol positions as follows:

| Position | Candidate meaning | Example |
|---|---|---|
| 1 | Domain or project family | `🌊` Broadside/Crest |
| 2 | Work type or action | `🧹` cleanup/pruning |
| 3 | Artifact or subsystem | `📚` research/documentation |
| 4 | Lifecycle state | `✅`, `🟡`, `🔴` |
| 5 | Importance or exception | `⭐`, `📌`, `‼️` |
| Words | Specific subject and outcome | `Crest Pruning — Broadside` |

This grammar is a prototype, not an approved taxonomy. Important unresolved questions include whether symbol meaning should be positional, whether fewer symbols omit trailing dimensions, and how accessibility or users who dislike emoji should be handled.

## Candidate system shape

[INFERRED] The strongest first-version hypothesis is a native-sidebar-first skill with an explicit manifest:

1. **Collector:** lists threads and pages through relevant history.
2. **Interpreter:** extracts project family, work type, artifact, lifecycle, importance, subject, outcome, and confidence.
3. **Policy engine:** applies user vocabulary, overrides, stability rules, and mutation thresholds.
4. **Planner:** emits an old-versus-proposed manifest without mutations.
5. **Reviewer:** presents collisions, low-confidence cases, archive candidates, and scope.
6. **Executor:** applies only authorized title/pin/archive changes through supported Codex operations.
7. **Verifier:** reads back state and emits a result/rollback manifest.
8. **Scheduler:** reruns the same skill on an approved cadence after a manually reviewed rollout has established acceptable behavior.
9. **Visualizer (possible companion):** renders the manifest as a semantic sidebar, table, or project map.

The native Codex skill is the owner-approved core. The visualizer is an `[OPEN]` companion, not a dashboard-only alternative. Project grouping is also `[OPEN]`: the first version must explicitly choose among shared title/symbol conventions, supported native project operations, and companion-only spatial grouping.

## Prior art and the remaining gap

The initial research scan found adjacent products and suggests a remaining seam worth testing:

- [Official Codex scheduled tasks](https://learn.chatgpt.com/docs/automations) can run recurring, skill-driven work.
- [Codex app-server](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md) documents thread listing, reading, naming, archive, and related operations.
- [Codex Chat Organizer](https://tessl.io/registry/lirantal/codex-chat-organizer) reparents threads into saved projects through local-state patching after Codex exits.
- [Codex Monitor](https://www.codexmonitor.app/) is an external command center with thread controls and richer workspace orchestration.
- [Grasppy](https://grasppy.com/) turns multi-platform conversations into structured knowledge and a visual graph.

[INFERRED] The candidate gap is a native Codex skill that continuously projects semantic organization back into the user's existing thread surface through a stable visual grammar, a reviewable policy, and supported mutations. Refresh the scan before making current-market claims.

## Design interview queue

Ask one consequential question at a time. For each, provide a recommendation and explain meaningful tradeoffs.

1. Companion scope and grouping representation: title/symbol convention, supported native project operations, optional visualizer, or a combination.
2. Autonomy: propose-only, confirm-each-batch, or policy-based unattended changes.
3. Symbol language: positional grammar, free semantic tokens, or project-only symbols.
4. Project family: inference sources, importance threshold, and override format.
5. Lifecycle: state vocabulary and when status belongs in a title.
6. Title stability: protected human titles, change thresholds, and cooldown.
7. Pin/archive: definitions, confidence thresholds, and whether scheduled runs may mutate them.
8. Inventory scope: recent threads, active projects, all local history, remote hosts, and archived threads.
9. Audit and rollback: manifest storage, old/new state, batch IDs, and recovery procedure.
10. Scheduling: cadence, notifications, stop conditions, and cost limits.
11. Evaluation: representative corpus, recognition-time test, accuracy, collision rate, and false-archive tolerance.
12. Distribution: standalone skill repository, broader skill collection, and installation/update strategy.

Cross-thread relevance and supersession review is now an owner-approved capability. Its first safe design is recorded in `docs/superpowers/specs/2026-07-21-cross-thread-relevance-review-design.md`; archive and other mutation policy remain separately scoped.

## Recommended discovery stop condition

[INFERRED] Discovery should be considered complete only when the owner has approved:

- the first-version product boundary;
- the classification schema and symbol grammar;
- mutation and human-approval policy;
- title stability and override rules;
- archive/pin safety boundaries;
- scheduling behavior;
- audit, rollback, and success metrics.

At that point, write the approved design into `architecture.md` and durable decisions, ask the owner to review it, then create a separate implementation plan. Do not treat this recovered checkpoint as implementation authorization.
