---
name: codex-thread-organizer
description: Organize Codex sidebar tasks or ChatGPT web conversations from their bodies. Use for evidence-based titles, related-work grouping, cross-surface bridges, emoji semantics, ChatGPT Project proposals, and approved renames or moves.
---

# Conversation organizer

## Boundary

Packaging is Codex-only: this is a dedicated Codex package. It can organize two
evidence surfaces:

- Codex sidebar tasks, using Codex's native task controls.
- Authenticated ChatGPT web history, using the ChatGPT web UI after approval.

Do not infer the contents of a ChatGPT web conversation from a title shown in a
Codex sidebar. If the requested surface is unavailable, say which surface is
unavailable and do not substitute an invented inventory.

## Load order

Always read:

1. [Shared conversation model](references/shared-conversation-model.md)
2. [Semantic emoji taxonomy](references/emoji-taxonomy.md)

Then select the needed evidence surface:

- For Codex sidebar tasks, read [Codex sidebar adapter](references/codex-sidebar-adapter.md).
- For ChatGPT conversations at `chatgpt.com`, read [ChatGPT web adapter](references/chatgpt-web-adapter.md).
- To relate ChatGPT conversations to Codex tasks, read both adapters and the
  [cross-surface bridge](references/cross-surface-bridge.md).

Do not combine the mutation rules from the two adapters. In particular, Codex
lifecycle markers and the verified Codex title limit do not apply to ChatGPT
web titles. A cross-surface bridge is evidence for organization, never by
itself authority to mutate either surface.

## Common rule

Read bodies before proposing a title, relationship, Project placement, or
cross-surface bridge. A title is a compact retrieval label for actual work, not
a guess from a colored marker, age, sidebar preview, or existing sidebar title.
