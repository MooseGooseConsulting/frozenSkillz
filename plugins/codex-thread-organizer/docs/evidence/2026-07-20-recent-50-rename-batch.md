# Recent 50 Codex Thread Rename Batch

Date: 2026-07-20
Status: applied and verified

## Outcome

- Threads discovered and inspected: 50
- Threads renamed: 49
- Threads intentionally unchanged: 1
- Inaccessible or malformed threads: 0
- Unavailable hosts: 0
- Final titles found and matched exactly on read-back: 50/50
- Unique final titles: 50
- Pin, archive, project, and conversation-content changes: 0

The exact unabridged old/new values, confidence, rationale, and verification
results are preserved in
[the machine-readable batch manifest](2026-07-20-recent-50-rename-batch.json).

## Evidence basis

The titles were derived from conversation bodies, not generated titles or
opening prompts.

- The 30-task prior cohort reused the preserved audit covering 50 transcript
  pages and 271 turns.
- The 20 newly included tasks were read from their opening request through
  later substantive turns and outcomes.
- Every newly included history longer than ten turns was paged to completion.
- Naming preferred the dominant or final substantive purpose, including pivots,
  outcomes, remaining work, and superseding tasks.

## Mutation and verification

The batch used Codex's native `set_thread_title` operation. No metadata file
was edited directly, so no state-store backup was necessary. Mutation
acknowledgements were treated as provisional until a fresh `list_threads`
inventory independently matched every final value.

Final verification:

- Expected: 50
- Found: 50
- Exact matches: 50
- Unique final titles: 50
- Failures: 0
- Literal trailing ellipses: 0

## Native title-length finding

The trial discovered that the native operation persists at most 60 UTF-16 code
units. Twenty-four initially proposed titles exceeded that limit and were stored
with a literal trailing ellipsis. They were shortened without changing their
body-derived meaning, rewritten, and read back again.

The recurring workflow must therefore:

- enforce a maximum of 60 UTF-16 code units before mutation;
- use a lower normal ceiling to leave revision headroom;
- freeze thread IDs and old titles before each batch;
- skip and report any concurrent title change;
- independently read back every applied value.

## Mutation accounting

- Unique task titles changed: 49
- Native mutation calls: 73
- Corrective calls caused by the newly discovered limit: 24
- Direct metadata files changed: none
- Backup location: not applicable because no direct state-store editing occurred
