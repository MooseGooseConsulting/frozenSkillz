# ChatGPT web adapter

Use this adapter only after the user explicitly selects ChatGPT web history and
an authenticated, controllable `chatgpt.com` browser surface is available. It
is a direct-execution route for user-authorized renames and explicitly requested
Project actions; it is not a proposal-only workflow.

## Inventory and body review

1. Declare a repeatable scope before opening chats: a recent range, named
   Project, date range, topic, or explicit list. Review at most 30 chat bodies
   in one cohort; report the next deferred cohort when the request is larger.
2. Inventory the actual history container, including lazy-loaded rows. Existing
   titles, dates, and Project labels are selection hints only, not evidence.
3. Open every selected chat and build the shared conversation record from its
   body. Mark unavailable chats as coverage gaps and leave them unchanged.
4. Inventory existing ChatGPT Projects before recommending a Project placement.
   A Project is a separate container, not a synonym for a workstream or a
   Codex project object.

## Direct changes

The user's request to rename selected ChatGPT chats authorizes direct title
changes after body review. Before each rename, reopen or refresh the target and
compare the current title with the reviewed value; skip any concurrent change.
Use the browser's Rename control, then visibly verify the applied title.

A request to organize chats does not authorize container changes. Move a chat
only when the user explicitly asks to move chats to Projects and the destination
is an existing, body-evidenced fit. Create, merge, rename, or archive Projects
only when the user explicitly asks for that exact action. Refresh the current
Project immediately before a move and visibly verify the applied result.

When a required browser control is absent or cannot be verified, report that
specific limitation and leave the target unchanged. Never claim a browser
mutation succeeded from an assumed or stale UI state.

## ChatGPT title treatment

Use the shared emoji taxonomy and concrete wording, normally with three
semantic emoji. Do not copy Codex lifecycle markers into a ChatGPT-web title
unless the user asked for a status-oriented view. The Codex 60 UTF-16 unit
ceiling is not a verified ChatGPT limit; use it only as a conservative style
target.
