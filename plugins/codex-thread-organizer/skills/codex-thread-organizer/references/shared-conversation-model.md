# Shared conversation model

Use this model for both adapters. It describes what the conversation says; an
adapter decides how, or whether, its title can be changed.

## Chat card

For each conversation considered, make a card from the body, not the current
title. Include:

| Field | Record |
| --- | --- |
| Conversation | Stable ID or direct UI identity, current title, and availability |
| Detailed summary | Opening request, important corrections or decisions, delivered outcome, concrete systems/artifacts, and unresolved work |
| Workstream | The durable project or problem this belongs to |
| Evidence | Specific body details that support the summary and any cross-chat claim |
| Relationship | `continues`, `supersedes`, `duplicates`, `corrects`, `related`, or `independent`, plus the other conversation when applicable |
| Cross-surface candidate | A Codex task or ChatGPT chat only when a body-evidenced bridge exists; otherwise `none` |

Do not infer a task or conversation's content, scope, or relationship from its
visible title, sidebar preview, emoji, age, or Project name. Do not title, move,
or bridge a conversation whose body is unavailable. Mark it unavailable instead
of converting a title-only guess into a fact.

## Relationships and workstreams

Group cards by the actual system, artifact, decision, or question they concern.
Do not group merely because they are recent, use the same tool, or appear under
the same Project.

- `continues`: later work carries the same concrete work forward.
- `supersedes`: later work replaces a prior approach or authoritative result.
- `duplicates`: the conversations independently pursue materially the same work.
- `corrects`: later work fixes a stated error in earlier work.
- `related`: shared context without one of the stronger relationships.
- `independent`: no material relationship found.

Every relationship other than `independent` needs body evidence from both
conversations. If independent clusters are large enough to delegate, each
subagent returns cards with those evidence details; the main agent compares the
cards before asserting a cross-cluster relationship.

## Title principle

Use the most retrievable concrete form available: system, product, or artifact
plus action, decision, failure, or outcome. Semantic emoji are secondary to
those nouns and verbs. Do not use an emoji as a substitute for the subject.
