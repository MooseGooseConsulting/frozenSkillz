# Codex Thread Organizer Design

This is human-facing design rationale. Codex does not load this README when the
skill fires; `skills/codex-thread-organizer/SKILL.md` and its routed references
are the runtime instruction surface.

## Product decision

The organizer is a direct-execution tool, not a proposal-only or Notion-report
workflow. When a user asks it to rename chats on a selected supported surface,
body review is the evidence gate and the requested rename is applied. Every
change is refreshed immediately before mutation and visibly read back, so the
skill does not overwrite a concurrent human edit or claim an unverified action.

Proposal-only behavior was rejected because it turns a request to organize a
history into a report that leaves the history unchanged. The correct safety
boundary is narrower: require body evidence, make the selected client explicit,
respect the user's authorization for the specific action, preserve distinct
container types, and verify the live result.

## Two surfaces, not one blended history

The package runs in Codex Desktop, but it supports two deliberately separate
conversation surfaces:

- **Codex sidebar:** native inventory, body reads, lifecycle/current-owner
  review, and direct native title mutation for `title-mutable` rows.
- **ChatGPT web:** an explicitly requested, authenticated, controllable
  `chatgpt.com` browser pass. It has independent inventory, body review, title
  mutation, and optional explicitly authorized Project actions.

A ChatGPT conversation displayed in Codex is not automatically the same
resource as a ChatGPT-web conversation. Titles, dates, preview text, project
labels, working directories, and emoji are discovery hints, never bridge
evidence. A cross-surface claim requires both bodies plus a shared concrete
request, artifact, decision, or explicit reference.

This boundary prevents the failure mode of treating Codex tasks, ChatGPT chats,
Codex sidebar sections, Codex project objects, and ChatGPT Projects as one kind
of thing. They are five different resources with different capabilities and
authorization requirements.

## Evidence and mutation model

The shared conversation record captures the actual request, later corrections,
outcome, named systems or artifacts, remaining action, workstream, relationship
evidence, and mutation constraints. Workers return body-evidenced records, not
just suggested titles; the coordinator reconciles related clusters.

For both adapters:

1. Declare scope and record every coverage limitation.
2. Read bodies before deriving a relationship, title, or Project fit.
3. Refresh the reviewed title and current Project immediately before a change.
4. Skip concurrent changes rather than overwriting them.
5. Read back or visibly verify every successful mutation.

Chat-title organization authorizes title changes, not container management. A
user must specifically request a Codex section action, Codex project-object
action, or ChatGPT Project move/create/merge/archive before the relevant
container may change. This still allows direct Project operations when the
user actually asks for them; it prevents inferred reparenting from a clustering
exercise.

## Coverage model

Codex native `list_threads(limit: 50)` returns all pinned conversations plus up
to 50 most recent non-pinned rows, potentially mixing Codex and ChatGPT kinds.
An inventory is complete only after a continuation is exhausted, or when fewer
than 50 non-pinned rows are returned and no continuation exists. A full 50-row
non-pinned page without exhaustion evidence is bounded partial coverage, not
the user's entire sidebar or ChatGPT account history.

ChatGPT web work is divided into explicit, repeatable cohorts of at most 30
body-reviewed chats. This keeps a large history honest: the completed cohort
and the deferred set are reported rather than silently treating a first page as
the entire account.

## Title language and emoji

Titles use three to five leading semantic emoji, normally three or four. The
roles are deliberately distinct: domain, work type, then a state, relationship,
retention role, or second precise domain. The taxonomy gives both a broad set
of familiar suggestions and combination seeds, avoiding the earlier failure of
using only one or two vague symbols.

Codex-sidebar titles additionally expose evidence-based lifecycle markers such
as `✅`, `🟡`, `⏸️`, `🚧`, `📌`, `↪️`, and `🗄️`. Those markers are local
sidebar metadata, not universal ChatGPT title state. ChatGPT web titles use the
same retrieval-oriented taxonomy but receive lifecycle markers only when the
user explicitly asks for a status-oriented view.

## Runtime layout

`SKILL.md` is a thin router. It selects one surface, then loads the shared
conversation model and emoji taxonomy plus the matching adapter. It routes to a
cross-surface bridge only when a user explicitly asks for one. Runtime detail
lives in the referenced files so the model does not load instructions for the
wrong client.

The package intentionally does not own a browser-export daemon, a Postgres
archive, a Notion database, or a second application control plane. Those may
improve evidence in another system, but they are not prerequisites for a real
organization pass and do not decide titles or containers.

## Packaging

This is a dedicated Codex-only package. The repository source is distributed to
the Codex consumer through `plugins/distribution.json`; it is not installed for
Claude, Cursor, or Gemini. Human design documents remain in this package while
agent-facing instructions remain under `skills/`.
