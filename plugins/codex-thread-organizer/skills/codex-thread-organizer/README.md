# Codex Thread Organizer: Response-Shaping Rationale

## Target response

When an operator says “organize” or “rename all chats,” the model should produce
an evidence-based pass over every conversation the current native surface
returns. It must not silently narrow the request to Codex tasks, mistake a
bounded recent page for complete history, or claim that a conversation was
renamed when the native operation cannot mutate it.

The target is not simply prettier titles. It is an honest result that separates
what was returned, what could be read, what could be renamed, and what remains
inaccessible or unfinished.

## Why the instruction design is structured this way

### Scope before kind filtering

The description and first workflow step repeatedly name ChatGPT conversations,
pinned conversations, and every returned kind. This is deliberate repetition:
without it, a model sees a Codex-packaged skill and takes the tempting shortcut
of filtering to Codex tasks before it inventories the sidebar. The wording makes
the required response start with the full returned surface, then classify it.

### The explicit `limit: 50` explanation

The limit is explained before the workflow because “50” otherwise invites a
plausible but wrong response: treating it as 50 repositories, 50 total chats,
or all history. Stating that pins are additive and that the non-pinned page is
bounded directs the model to calculate and report coverage rather than infer
completeness from a round number.

### Separate visibility, readability, and title mutability

The skill requires `title-mutable` and `not title-mutable` classification instead
of treating an unsupported title operation as a reason to exclude a conversation.
That distinction is designed to evoke an inventory/reporting response for
ChatGPT conversations even when only Codex tasks can be renamed. It prevents the
false conclusion “I cannot rename it, therefore I cannot see or review it.”

### Bodies and cross-task evidence before status titles

Titles, previews, and working directories are easy shortcuts, but they do not
establish the latest user request, supersession, or remaining work. Requiring
body reading and cross-task review before classification is meant to make the
model derive status markers from evidence instead of applying generic completion
emoji or grouping tasks by repository name alone.

### Coverage accounting before the final report

The required report totals—coverage status, mutable, skipped, unsupported, and
inaccessible—force the model to expose the difference between a useful bounded
pass and a complete-history claim. This is the response-level safeguard against
calling a partial result “all chats.”

## What a maintainer should preserve

Do not simplify this into “rename all Codex chats” or remove the repeated scope
and coverage language merely because it seems redundant. Those parts are the
mechanism that steers the model away from the specific shortcuts above. Change
them only with new capability evidence or a replacement that still evokes the
same honest inventory-and-classification response.

## Deliberate boundary

This is a human-maintainer rationale, not agent instruction. The active behavior
is defined only by `SKILL.md` and references that `SKILL.md` explicitly routes
to.
