---
title: Codex Sidebar Organizer North Star
date: 2026-07-20
status: draft-owner-review
last_confirmed: 2026-07-20
---

# Codex Sidebar Organizer North Star

Draft authority note: `[OWNER]` marks direct owner language or a faithful recovery of an owner requirement. `[INFERRED]` and `[OPEN]` are non-authoritative design material and must not be implemented as approved requirements. The owner still needs to review this recovered document as a whole.

## Why This Exists

[OWNER] Codex preserves a huge amount of valuable work while exposing so little organizational structure that important threads become effectively unfindable; this project builds a Codex skill that turns the actual persisted threads into a maintained visual system that can be understood at a glance.

## Goals and Requirements

### G1. Make the existing Codex thread surface visually scannable

[OWNER] Replace indistinguishable generated titles, raw attachment paths, generic prompts, and pasted plans with compact identities that remain useful when the sidebar truncates them.

- **G1-R1.** [OWNER] An organizer-generated semantic title uses between one and five leading emoji-like symbols plus a concise natural-language subject.
- **G1-R2.** [INFERRED] Symbol positions use a stable grammar rather than decoration: project/domain, work type, artifact/subsystem, lifecycle state, and importance/exception.
- **G1-R3.** [INFERRED] The first visible words distinguish neighboring threads; searchable project names may move later in the title.
- **G1-R4.** [OWNER] Unicode symbols and punctuation must persist and render through Codex's supported title operation.
- **G1-R5.** [OWNER] Natural-language titles are approximately 5–12 words, but may be longer when that materially improves recognition.

### G2. Name threads from their actual work

[OWNER] Base organization on enough of the conversation to understand what the work became, not merely the opening request.

- **G2-R1.** [OWNER] Classification considers the opening request, later changes of direction, substantive outcomes, remaining work, and superseding threads.
- **G2-R2.** [INFERRED] Every proposed classification carries confidence and evidence; ambiguity is surfaced for review rather than invented away.
- **G2-R3.** [OWNER] Related threads about the same project remain distinguishable by phase, outcome, blocker, correction, or handoff.
- **G2-R4.** [OWNER] Every proposed title receives a descriptive first pass followed by a critique-and-revision pass before application.
- **G2-R5.** [OWNER] For threads attributable to the same repository or project family, review relevant accessible conversation bodies together to determine whether later work has made an older thread no longer relevant or superseded.
- **G2-R6.** [INFERRED] A relevance or supersession recommendation should be based on the actual conversation bodies and available project evidence, not the current title or age alone. A supersession recommendation should identify the later related thread or artifact when available; otherwise it remains `needs review`.

### G3. Keep organization maintained instead of creating another cleanup chore

[OWNER] Support automatic Codex organization through on-demand use and scheduled runs.

- **G3-R1.** [OWNER] The workflow supports a read-only proposal pass before an authorized mutation pass.
- **G3-R2.** [OWNER] Once a batch scope is authorized, the workflow may apply the refined titles without requesting approval for every individual thread.
- **G3-R3.** [OWNER] Applied changes prefer supported Codex operations and are read back afterward for verification.
- **G3-R4.** [OWNER] If direct metadata editing is ever required, all Codex clients sharing the store must be closed; the authoritative stores must be identified; a timestamped backup must be created; writes should be atomic where practical; and IDs, messages, timestamps, project associations, and unrelated metadata must be preserved.
- **G3-R5.** [OPEN] Define how often an established title may change as a thread evolves.
- **G3-R6.** [OPEN] Define the scheduled cadence, notification policy, and approval boundary.
- **G3-R7.** [INFERRED] Cross-thread relevance review is a read-only proposal pass. It must not rename, pin, archive, reparent, or otherwise mutate a thread unless a later batch has an explicit authorized mutation scope.

### G4. Expose meaningful project and workstream structure

[OWNER] Group work by projects or project families when those groupings are important enough to aid recognition.

- **G4-R1.** [INFERRED] Project-family classification may use working directory, repository identity, transcript evidence, and stable user overrides.
- **G4-R2.** [OPEN] Define what makes a project family important enough to receive a symbol or explicit title suffix.
- **G4-R3.** [OPEN] Define how cross-project, standalone, homelab, and personal work should be represented.
- **G4-R4.** [OPEN] Define whether grouping in the first version means a shared title/symbol convention, supported native project reparenting, a companion visualization, or some combination. Do not claim a native hierarchy that Codex does not expose.

### G5. Make the organizational decisions durable and auditable

[OWNER] The project and its requirements live in Git so the workflow does not depend on remembering an old conversation.

- **G5-R1.** [OWNER] The idea and recovered requirements must live in a proper Git repository with a remote rather than only in a dated Codex task folder or chat transcript.
- **G5-R2.** [INFERRED] This repository should become the durable home for approved design, implementation, evaluation, and operating instructions as those artifacts are created.
- **G5-R3.** [OWNER] Every applied batch produces an audit report containing thread ID, old title, final title, confidence, rationale, verification result, inventory totals, inaccessible threads, mutation method, stores or APIs changed, backup location when applicable, and issues for recurring operation.
- **G5-R4.** [OPEN] Define rollback guarantees for title, pin, and archive changes.
- **G5-R5.** [INFERRED] Every cross-thread review should produce a durable report containing repository or project-family attribution, relationship classification, related thread IDs where known, evidence, confidence, and any proposed follow-up action.

## Anti-Goals

- **AG1.** [INFERRED] This is not an emoji decoration generator. Symbols must reduce recognition time or communicate stable meaning.
- **AG2.** [INFERRED] This is not a silent destructive cleanup bot. Uncertain archive, pin, or rename decisions must remain reviewable.
- **AG3.** [OWNER] A dashboard-only product is not the core deliverable. The core is a Codex skill that improves the actual persisted Codex thread surface; a richer visual companion remains `[OPEN]`.
- **AG4.** [OWNER] The initial scope is not ChatGPT web conversations, browser-tab titles, browser extensions, local display-only aliases, or conversation-content editing.

## Open Product Decisions

- Companion-visualizer scope and how project grouping is represented without inventing a native hierarchy.
- Exact one-to-five-symbol vocabulary and collision rules.
- Human override format and how overrides survive future scheduled runs.
- Title stability, rename frequency, and protection of user-authored titles.
- `Keep | Pin | Archive | Needs review` taxonomy and safety thresholds.
- Initial inventory scope: recent cohort, per-project cohort, or complete accessible history.
- Automation cadence, permissions, notifications, and stop conditions.
- Installation, distribution, and whether this remains a standalone repository or is promoted into a broader skills collection.
