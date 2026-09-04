# Codex sidebar adapter

Use this adapter only for the Codex-sidebar route. It directly renames the
native `title-mutable` conversations the selected client exposes; it does not
operate the ChatGPT website.

## Inventory and coverage

1. Call native `list_threads` with `limit: 50` before filtering by kind. Record
   every returned pinned and non-pinned conversation, including ID, kind, host,
   title, update time, working directory, Project ID, and preview.
2. The limit applies to non-pinned conversations. All pins are additive, so an
   inventory may contain more than 50 rows. It never means 50 repositories or
   all account history.
3. Exhaust every available cursor, page, or load-more control. Report coverage
   as `complete` only after exhaustion, or when fewer than 50 non-pinned rows
   are returned and no continuation is available. If 50 non-pinned rows are
   returned without proof of exhaustion, report `bounded` with `partial
   coverage`, the requested limit, and the pinned count.
4. Readable ChatGPT rows belong in the inventory. Classify each row as
   `title-mutable` or `not title-mutable` using the native title capability;
   capability failure is not a reason to omit it.

## Resource boundary

An individual conversation is not a Codex sidebar section or a project object.
Do not create sections, move conversations between sections, rename project
objects, or infer project membership from a workstream cluster. Report proposed
groupings when requested, but mutate a container only after the user explicitly
names the container action and the native capability supports it.

## Direct rename

Read the body of every candidate, make the shared conversation record, and use
the Codex lifecycle review before assigning markers. Immediately before each
rename, refresh the target title and compare it with the reviewed title. Skip a
target changed by someone else. Apply the native title operation only to
`title-mutable` rows, then read the resulting title back and correct a verified
mismatch or truncation. Report `applied`, `already-correct`, `skipped`,
`failed`, and `not title-mutable` separately.
