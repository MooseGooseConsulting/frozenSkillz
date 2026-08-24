# ChatGPT Conversation Organizer: Implementation Plan

## Product gate

The first deliverable is the improved `codex-thread-organizer` skill, not the
database or exporter. It succeeds when a live-browser ChatGPT pass can produce
detailed summaries, coherent workstream groups, relationship evidence,
emoji-backed titles, Project proposals, and a self-graded reviewable proposal
for the requested 30 recent chats.

The Pion fork and Postgres archive are parallel evidence infrastructure. They
must improve later runs without blocking the live-browser skill path.

## FrozenSkillz files to author

| Path | Role | Contents |
| --- | --- | --- |
| `plugins/codex-thread-organizer/README.md` | Human design document | System flow, boundaries, worksheet, grading rubric, and delivery gates. Already added. |
| `plugins/codex-thread-organizer/skills/codex-thread-organizer/SKILL.md` | Thin agent router | Always-read shared references; choose Codex or ChatGPT adapter; require plan adherence and reconciliation; contain no schema or exporter implementation detail. |
| `references/shared-conversation-model.md` | Shared analysis contract | Required body-derived summary fields, cluster rules, relationship definitions, title specificity rules, and worker return format. |
| `references/emoji-taxonomy.md` | Shared semantic emoji authority | Emoji meaning, CLDR/Unicode provenance, ambiguity warnings, approved combinations, and emoji-research dispatch contract. |
| `references/codex-sidebar-adapter.md` | Codex-only execution | Native inventory/title capability, lifecycle/current-owner reasoning, Codex status markers, and bounded coverage. |
| `references/chatgpt-web-adapter.md` | ChatGPT-only execution | Lazy-history inventory, live-browser evidence, Project grouping, proposal-first browser mutations, and optional Postgres evidence input. |
| `references/proposal-review.md` | Shared quality gate | Evidence worksheet, self-grade rubric, approval boundary, and worker/reviewer reconciliation. |
| `agents/openai.yaml` and `evals/triggers.json` | Discovery contract | Updated ChatGPT-web triggers and user-facing description without turning the package into a general browser-tab organizer. |
| `tests/test_codex_thread_organizer.py` and focused fixtures | Regression protection | Router/reference shape, adapter separation, worker-return requirements, proposal gates, and no-status-in-ChatGPT assertions. |

Keep the current `cross-task-review.md`, `title-grammar.md`, and
`periodic-automation.md` only where their Codex-specific content remains true.
Move shared rules into the new shared references rather than duplicating them.

## ChatGPT batch analysis

The ChatGPT adapter, not a generic worker framework, owns this procedure.

1. Scroll the ChatGPT history container until the requested batch is actually
   loaded; do not confuse the initially rendered sidebar rows with the batch.
2. Divide a large requested batch into bounded browser-reading assignments.
3. Each worker opens its assigned chats and returns one concrete chat card:
   source ID, current title, Project, opening request, later correction, actual
   outcome, distinguishing nouns, named artifacts, related chat IDs, and
   uncertainty. A title without that card is discarded.
4. The main pass compares the cards together. For every proposed cross-chat
   relationship or Project move, it opens the cited source chats itself before
   retaining the claim.
5. The main pass produces the worksheet, title/emoji/Project proposal, and
   grade. In ChatGPT mode it waits for approval before browser changes.

This is how the skill checks subagent work: it checks claims against the cited
chat bodies, not by asking a generic reviewer to restate the proposal.
### Emoji-research dispatch

Dispatch a separate emoji researcher whenever the taxonomy lacks a requested
semantic category, a 2025/2026 emoji is proposed, or client rendering is
uncertain. Require official Unicode version, CLDR short name, code point or
sequence, semantic fit, ambiguity warning, and target-client rendering result.
Do not use an unverified candidate merely because it looks appropriate.

The initial approved-combination set is:

- `🤖🧪` agent research and evaluation.
- `☁️🖥️` cloud compute, GPU rental, and serving.
- `🛰️🤖` robotics, sensing, and autonomy.
- `🛰️🔌` sensor power, networking, and bring-up.
- `🏠💧` home and irrigation systems.
- `💾💸` storage hardware and pricing.
- `🧭🏗️` architecture direction and system design.
- `🎨🏭` generative-media production systems.

## Proposal artifact and grade

The coordinator reports a concise evidence worksheet instead of private
reasoning traces. Each chat row includes current state, detailed summary,
cluster basis, relationship evidence, old/new title, emoji meaning, Project
action, confidence, and actionability.

Grade each row and workstream against these gates:

| Gate | Required outcome | On failure |
| --- | --- | --- |
| Body coverage | Read enough body to identify request, outcome, and specific nouns. | Leave unchanged. |
| Summary fidelity | Claims track body evidence. | Rewrite or mark uncertain. |
| Cluster coherence | Shared work is stronger than superficial similarity. | Split or make independent. |
| Relationship evidence | IDs and concrete evidence support the claimed relation. | Downgrade or remove it. |
| Title specificity | Recognizable without reopening the chat. | Rewrite. |
| Emoji fit | Every emoji has a documented category contribution. | Remove it. |
| Project fit | Existing Project is a clear home. | Keep current Project or propose separately. |
| Mutation capability | The target client exposes the approved operation. | Keep proposal-only. |

Only passing, approved rows mutate. The report records applied, skipped, failed,
and concurrently changed operations from the command or browser action; it does
not reopen chats solely to verify a change.

## Parallel evidence infrastructure

### `Coldaine/chatgpt-exporter`

- Wholesale MIT fork of `pionxzh/chatgpt-exporter`, retaining upstream remote,
  build, UI, API modules, pagination, Project support, and raw mapping fetch.
- Add only strict sync behavior, a run-scoped browser command, events, a
  temporary no-attachment transport payload, portable headful execution, and
  normalized Postgres import.
- Do not copy exporter source into the frozenSkillz plugin or write a second
  ChatGPT HTTP collector.

### `coldaine-homelab`

- Provision `chatgpt_history` as a dedicated database on `pg18-core`.
- Create owner, sync-writer, and read-only organizer roles over private TLS.
- Store normalized conversations, Projects, membership, messages, branches,
  hashes, sync state, summaries, clusters, relationships, proposals, and
  applied actions.
- Do not retain attachment binaries, ZIP collections, or raw-export archives.

## Delivery order

1. Rewrite and forward-test the skill against fixtures, then execute the live
   30-chat proposal path. This is the first product milestone.
2. Provision the dedicated Postgres database and least-privilege access.
3. Fork Pion wholesale and add strict portable synchronization.
4. Add `postgres_archive` as an optional ChatGPT evidence input without
   changing the shared analysis, review, or mutation rules.

Do not claim the organizer feature is complete because the exporter builds or
the database is provisioned. The first acceptance gate is a high-quality,
proposal-first organization pass over real ChatGPT chats.
