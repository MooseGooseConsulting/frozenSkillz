---
name: codex-thread-organizer
description: >-
  Organize Codex sidebar conversations or explicitly requested ChatGPT web
  conversations from their bodies. Use for unclear titles, related-work review,
  unfinished-work ownership, or deliberate chat cleanup; do not use for generic
  summaries or other clients' histories.
---

# Codex Thread Organizer

Organize conversation history from body evidence, not titles, previews, dates,
or container names. This is a direct-execution skill: when the user's request
authorizes renaming a selected route, apply supported title changes, recheck
them, and report the result. It is not a proposal-only or Notion-report skill.

## Select one surface before acting

- **Codex sidebar** is the default only when the request names Codex, its
  sidebar, or its tasks. It uses native list, read, and title operations. Read
  [the Codex sidebar adapter](references/codex-sidebar-adapter.md).
- **ChatGPT web** requires an explicit request for `chatgpt.com`, the ChatGPT
  website, or web-history organization, plus a controllable authenticated
  browser. Read [the ChatGPT web adapter](references/chatgpt-web-adapter.md).
- If a request could mean either surface, ask which one. Do not treat a ChatGPT
  conversation visible in the Codex sidebar as the same resource as its
  ChatGPT-web counterpart.
- For an explicitly requested comparison of both surfaces, use both adapters
  and [the cross-surface bridge](references/cross-surface-bridge.md). A shared
  title, Project name, emoji, or date is not proof of identity.

On every route, first read [the shared conversation model](references/shared-conversation-model.md)
and [the emoji taxonomy](references/emoji-taxonomy.md). The package README is
human-facing design rationale; do not load it as runtime instructions.

## Common execution contract

1. Declare the selected surface and the requested coverage. Record unreadable
   rows and coverage limits; never silently shrink the requested cohort.
2. Read every conversation body used for classification, relationship,
   renaming, or Project placement. Build body-evidenced workstream and
   relationship records before choosing a title.
3. Use [the title grammar](references/title-grammar.md). Applied titles use
   three to five meaningful leading emoji, normally three or four, plus
   concrete words that distinguish the conversation without reopening it.
4. A conversation title, a Codex sidebar section, a Codex project object, and a
   ChatGPT Project are different resources. A request to organize chats
   authorizes chat-title changes only. Do not create, rename, move, merge, or
   archive any container unless the user explicitly names that container action.
5. Immediately before each mutation, refresh the target and compare its current
   title and, where relevant, Project with the reviewed record. Skip a changed
   target rather than overwriting a concurrent user edit. Verify each successful
   rename or move in the live surface and report applied, skipped, failed, and
   not-mutable targets separately.

Use subagents only when independent workstream clusters make parallel body
review useful. Give each worker a non-overlapping cluster and require the body
evidence supporting its result; the coordinator owns cross-cluster decisions.

## Codex lifecycle review

For the Codex-sidebar route, read [cross-task review](references/cross-task-review.md)
before assigning lifecycle markers. It establishes `done`, `active-remaining`,
`continued-elsewhere`, and `parked-unclear`, plus the current owner of each
unfinished workstream. Those lifecycle markers are Codex-sidebar metadata; do
not copy them into ChatGPT-web titles unless the user explicitly requests a
status-oriented ChatGPT view.

## Recurring runs

Read [periodic automation](references/periodic-automation.md) only when the
user asks for recurring Codex-sidebar maintenance. The ChatGPT-web route is
interactive browser work, not a background daemon.
