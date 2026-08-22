# Durable native transcript export

Use this lane only when the user asks for detailed summaries, a durable archive,
or a database of Codex/ChatGPT chats exposed in Codex.

## Retrieval

1. Call the native `list_threads` operation with `limit: 50`. Record every
   returned pinned thread and every returned non-pinned thread in UI order; do
   not filter ChatGPT or Codex entries out of the inventory.
2. State the coverage precisely. The result is the app's bounded recent
   inventory: all returned pins plus at most 50 returned non-pinned mixed-kind
   entries. It is not a claim about all account history.
3. Read the first page for every selected entry in bounded parallel batches,
   using the native maximums currently accepted by `read_thread`:
   `turnLimit: 10`, `maxOutputCharsPerItem: 20000`, and
   `includeOutputs: false`. Persist the `thread`, `attachments`, and every
   turn/item returned. One initial read per selected chat is unavoidable because
   the app exposes no bulk transcript-export operation.
4. Queue only entries whose first or subsequent page reports `page.hasMore`.
   For each queued entry, pass `page.nextCursor` back to `read_thread` and
   continue until its cursor is exhausted. Record every cursor/page outcome,
   including unavailable or failed reads. Do not serially page chats that are
   already complete on their first read.
5. Only use browser rendering if native retrieval is unavailable for a selected
   chat and the user explicitly accepts that fallback. Label any such record
   `browser-rendered`, never `native-complete`.

## SQLite evidence model

Keep the export private and outside a source repository. At minimum record:

- `exports`: started/completed time, requested limit, native inventory limit,
  pinned/non-pinned counts, and coverage statement.
- `conversations`: export ID, UI order, thread ID, kind, title, project/host
  context, updated time, and read outcome.
- `pages`: conversation ID, page ordinal, input cursor, next cursor, has-more
  flag, retrieval time, and any error.
- `turns`: conversation ID, source turn ID, ordinal, status/timing fields, and
  the complete native items JSON.
- `attachments`: conversation ID and the complete native attachment JSON.

Do not reduce the stored evidence to a generated summary. Generated summaries
belong in a separate derived table or artifact that records the source export
and conversation IDs.
