---
name: codex-thread-organizer
description: In Codex Desktop, produce linked Notion proposals for semantic-emoji chat titles and ChatGPT Project organization. Use only when the user explicitly selects the local Codex or ChatGPT-web route; never execute a chat or Project change.
---

# Codex Desktop conversation organizer

## Boundary and router

This is a dedicated Codex package and runs **in Codex Desktop only**. It has
two deliberately separate, explicit routes:

- **Local Codex title review** — review title-mutable Codex sidebar tasks,
  compare their body-derived work with live coding-project context, and write
  title-and-semantic-emoji proposals to Notion.
- **ChatGPT web proposal** — review an explicitly declared ChatGPT web cohort,
  form body-derived title and Project proposals, and write them to Notion.

Do not infer a route from a title, Project name, or the fact that a ChatGPT
conversation appears in a Codex sidebar. If the user invokes this skill without
naming one route, ask them to select one. `allow_implicit_invocation` is off:
this organizer is not an automatic background cleanup.

Both routes are proposal-only. Do **not** invoke a native Codex title operation
or a ChatGPT Rename, Move, Create Project, Merge, or Archive control. A report
is the terminal output of the current workflow, not an approval queue that this
skill may execute later.

## Load order

Always read:

1. [Shared conversation model](references/shared-conversation-model.md)
2. [Semantic emoji taxonomy](references/emoji-taxonomy.md)
3. [Notion proposal report](references/notion-proposal-report.md)

Then select the explicit route:

- For local Codex title review, read [Codex sidebar adapter](references/codex-sidebar-adapter.md).
- For ChatGPT conversations at `chatgpt.com`, read [ChatGPT web adapter](references/chatgpt-web-adapter.md).
- To relate both routes, read both adapters and the
  [cross-surface bridge](references/cross-surface-bridge.md).

Codex lifecycle classifications and the verified 60 UTF-16 title ceiling apply
only to a local-Codex proposal. They do not transfer to ChatGPT titles. A
cross-surface bridge can inform a proposal only; it never authorizes a change.

## Corpus evidence rule

Build a corpus of readable conversation bodies and reason over its concrete
problems, repositories, files, artifacts, decisions, outcomes, and chronology.
That is how the organizer finds genuine connections across conversations.

Matching labels are not prohibited evidence; they are merely insufficient
evidence. A shared title, Project name, emoji, preview, age, or topic word
cannot by itself establish identity, a relationship, or a Project placement.
Record the body evidence and direct source links that support every proposal.
