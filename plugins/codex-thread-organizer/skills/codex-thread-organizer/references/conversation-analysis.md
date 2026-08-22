# Shared Conversation Analysis

## Evidence Record

Create one record for every selected conversation, including unreadable ones.
Retain: source ID, source kind, current title, current Project (or `none`),
update time, detailed subject summary, decisions/outcomes, important artifacts,
unresolved questions, related conversation IDs, proposed title, proposed Project,
confidence, and evidence. `unreadable` is an explicit acquisition result, never
an invitation to classify from the title.

Working directory, title, timestamp, and Project are routing clues only. A
classification needs the body and comparison with related bodies. Summaries must
state the opening request, later scope changes or corrections, delivered result,
decisions, concrete artifacts, unresolved work, and relationship evidence.

## Cluster and Relationship Pass

Cluster only on a demonstrated shared goal, artifact, implementation state,
decision, repository, issue/PR, or named successor. Compare each candidate
against every likely peer before proposing a title or Project.

Use exactly one relationship per directional comparison where evidence supports
it: `continues`, `supersedes`, `duplicates`, `corrects`, `related`, or
`independent`. Record both source and target IDs plus a short body-derived reason.
`continues` means later work carries the same unfinished objective; `supersedes`
means it replaces the operative result; `duplicates` means substantially the same
request/result; `corrects` fixes an earlier claim or direction; `related` shares a
workstream without replacing it. Do not invent a relationship for proximity.

## Required Proposal Check

Before any mutation, assess body coverage, title specificity, cluster cohesion,
emoji fit, relationship confidence, and collision risk. Revise weak proposals.
The evidence worksheet is concise scratch work: conversation IDs, body facts,
cluster basis, relationship reason, proposed title/Project, confidence, and
grade. It is not hidden reasoning or a durable local state store.

Unreadable bodies stay unmodified with their failed acquisition evidence. A
low-confidence relationship stays `independent` or unproposed rather than being
forced into a cluster.
