# Codex sidebar proposal adapter

Use this adapter only for the explicitly selected **local Codex title review**
route in Codex Desktop. It produces a Notion proposal report; it does not
rename a task.

Read the detailed Codex rules:

1. [Cross-task review](cross-task-review.md) for body-based workstream,
   lifecycle, current-owner, and cross-task evidence rules.
2. [Title grammar](title-grammar.md) for semantic type emoji and the verified
   60 UTF-16 code-unit ceiling.
3. [Periodic automation](periodic-automation.md) only when the user explicitly
   requests a recurring, proposal-only local-Codex review.

Inventory every accessible sidebar conversation and preserve its coverage
status. Exhaust every native page, cursor, or load-more control before claiming
complete coverage. If a native limit prevents exhaustion, record the exact
limit and retain partial coverage. A bounded inventory remains partial coverage.
Record each exposed task as `title-mutable` or `not title-mutable`; never omit
the latter. Capture a direct Codex task link for every body-reviewed task.

## Review workers

When the inventory has two or more independent coding-project clusters, dispatch
multiple `gpt-5.6-luna` subagents: one non-overlapping cluster per subagent.
Each returns linked body cards with the latest relevant user request, concrete
repository/artifact evidence, outcome, remaining work, and relationships. The
coordinating agent compares these cards with the live coding-project/repository
context before making a cross-cluster claim. It must not treat a dated prior
report as current project evidence.

If the declared review has only one independent cluster, say so rather than
claiming a multi-agent comparison. Do not substitute title matching for the
body-based corpus review.

## Write the local proposal report

For every body-reviewed `title-mutable` task, write to Notion:

- the direct Codex task link and title observed during review;
- body-derived summary, workstream, evidence, and relevant live repository
  context;
- proposed title with a semantic **type** emoji and its stated meaning;
- lifecycle/current-owner finding when known, without turning it into a title
  status marker unless the user specifically requests a separate future title
  policy; and
- `No action executed`.

Keep each proposed local title within 60 UTF-16 code units; use a literal
trailing ellipsis if it must be shortened. Include `not title-mutable`,
unavailable, and partial-coverage rows in the report, with no invented title.
Set the report's `Chats Renamed` property to `0`.

For a ChatGPT-to-Codex bridge, open the actual Codex task body and read
[cross-surface bridge](cross-surface-bridge.md). A Codex title or sidebar
preview is never proof of what the task concerns.
