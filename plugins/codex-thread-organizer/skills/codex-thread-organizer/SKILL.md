---
name: codex-thread-organizer
description: >-
  Organize related Codex sidebar or ChatGPT web conversations from their bodies:
  make evidence-backed semantic titles, clusters, relationships, and (for
  ChatGPT) Project proposals. Use when conversation history is unclear, related
  chats need grouping, or ChatGPT Projects and titles need deliberate cleanup.
---

# Unified Codex and ChatGPT Conversation Organizer

This is a thin router. It never classifies a conversation from its title, path,
timestamp, or Project alone. Read the selected conversation bodies, retain the
shared record, reconcile the cluster, then choose the adapter for the surface.

## Always Load

1. [shared conversation analysis](references/conversation-analysis.md)
2. [shared semantic emoji taxonomy](references/semantic-emoji-taxonomy.md)
3. [shared title rules](references/title-rules.md)

## Choose One Adapter

- **Codex sidebar** — use [the Codex adapter](references/codex-sidebar-adapter.md)
  for native inventory, task-body reads, direct title changes, lifecycle/current-owner
  reasoning, and bounded-coverage reporting. Packaging is Codex-only; this does
  not place the skill in the shared cross-consumer package.
- **ChatGPT web** — use [the ChatGPT adapter](references/chatgpt-web-adapter.md)
  for browser/archive acquisition, detailed body summaries, Projects, proposal
  review, approved browser changes, and read-back. Do not transfer Codex lifecycle
  or current-owner labels to ChatGPT chats.

When the requested surface contains both kinds, inventory and analyze them with
the shared rules, then execute each adapter independently. A browser agent may
acquire bodies, identifiers, and detailed summaries for a bounded cluster; the
coordinating agent alone reconciles relationships and proposals across clusters.
