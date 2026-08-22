# Codex Sidebar Adapter

Use native list, body-read, and title-change operations for the conversations
the Codex app exposes. Exhaust available pages. If the API limits the listing,
report `bounded` coverage, its exact limit, and `partial coverage`; never call it
all chats. Classify each result as `title-mutable` or `not title-mutable` using
the actual native capability.

After shared analysis, retain the Codex-only lifecycle state: `done`,
`active-remaining`, `continued-elsewhere`, or `parked-unclear`. Identify a
current owner only from cross-read evidence. This lifecycle and owner logic does
not apply to ChatGPT web conversations.

Build a shared semantic title, then use these Codex status markers only where
body evidence supports them: `✅` done; `🟡` concrete remaining action; `🔴` the
clearest highest-priority unfinished task; `⏸️` named external/user wait; `🚧`
specific blocker; `📌` canonical reference; `↪️` named continuation/supersession;
`🗄️` archive candidate. At most one attention marker and one lifecycle marker;
avoid contradictory states. Keep the verified 60 UTF-16-unit ceiling.

Immediately recheck title before writing, skip concurrent changes, mutate only
`title-mutable` items, and read every changed title back. Report coverage plus
changed, already-correct, skipped, not title-mutable, and concurrent-change totals.
