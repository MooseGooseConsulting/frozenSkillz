# Codex sidebar adapter

Use this adapter only for conversations exposed by the Codex sidebar.

Read the existing detailed Codex rules:

1. [Cross-task review](cross-task-review.md) for lifecycle, current-owner, and
   cross-task evidence rules.
2. [Title grammar](title-grammar.md) for sparse semantic titles, lifecycle
   markers, and the verified 60 UTF-16 code-unit ceiling.
3. [Periodic automation](periodic-automation.md) only when the user requests
   recurring Codex organization.

Keep each mutable Codex title within the verified 60 UTF-16 code units. If a
title must be shortened, use a literal trailing ellipsis rather than silently
losing the distinguishing outcome.

Inventory every accessible sidebar conversation and preserve its coverage
status. Exhaust every native page, cursor, or load-more control before claiming
complete coverage. If a native limit prevents exhaustion, record the exact
limit and retain partial coverage. A bounded inventory remains partial
coverage. Use Codex's native title operation only for
title-mutable tasks. Record conversations the sidebar exposes but cannot rename
as `not title-mutable` rather than silently omitting them.

For every mutable title, record the title used during review. Immediately
before the native rename, reread the current title. If it differs, skip the
task and report the concurrent change; do not overwrite it. After a successful
rename, read the title back and report the applied result.

For a ChatGPT-to-Codex bridge request, open the actual Codex task body and read
[cross-surface bridge](cross-surface-bridge.md). A Codex title or sidebar
preview is never evidence of what the task concerns.

The Codex adapter retains its lifecycle/current-owner behavior and its native
post-rename readback requirement. Those rules do not transfer to ChatGPT web.
