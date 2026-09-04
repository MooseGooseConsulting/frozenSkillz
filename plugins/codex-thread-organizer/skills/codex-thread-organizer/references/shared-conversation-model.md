# Shared conversation model

Use this model on either route before assigning a title, relationship, or
Project placement. It describes what the conversation says; the selected
adapter decides whether the client exposes a safe mutation.

## Conversation record

For each body-reviewed conversation, record:

| Field | Record |
| --- | --- |
| Identity | Stable ID, direct source link when available, source surface, current title, and current container if exposed |
| Body summary | Opening request, later corrections, delivered outcome, concrete systems or artifacts, and unresolved work |
| Workstream | The durable project, system, decision, or problem the conversation belongs to |
| Evidence | Specific body details supporting the summary, title, Project fit, and every cross-conversation claim |
| Relationship | `continues`, `supersedes`, `duplicates`, `corrects`, `related`, or `independent`, with the other record when applicable |
| Proposed treatment | Title, container action only if explicitly authorized, confidence, and any unreadable or concurrent-change limit |

Titles, previews, dates, working directories, Project labels, and emoji are
routing clues. They are not enough by themselves to establish a topic,
relationship, cross-surface identity, or Project fit. Leave unreadable rows
unchanged and report the coverage gap rather than converting a title-only guess
into a fact.

## Relationship rules

- `continues`: later work carries the same concrete work forward.
- `supersedes`: later work replaces a prior operative result.
- `duplicates`: the conversations independently pursue materially the same
  request or outcome.
- `corrects`: later work fixes a stated error in earlier work.
- `related`: shared context without one of the stronger relationships.
- `independent`: no material relationship is established.

Every relationship other than `independent` requires body evidence from both
conversations. Keep parallel workstreams separate even when they share a
repository, a Project, or broad vocabulary.

## Title principle

Write the concrete subject plus action, decision, failure, or outcome that lets
the user retrieve the conversation without reopening it. Emoji communicate
three or more distinct semantic roles; they never replace the important nouns
and verbs.
