# Optional workflows

These patterns are available when the shape of the request warrants them. They are not prerequisites
for ordinary recall, and they do not impose a provider order.

## Incident or interruption reconstruction

1. Define the cutoff time, timezone, machines, harnesses, and whether the user wants recognizable
   root conversations, child execution records, or both.
2. Inventory the relevant sources without mutating or importing them. Preserve parent/child and
   continuation relationships.
3. Read prompts and terminal events around the cutoff. One transcript can contain multiple requests,
   and work can finish after the cutoff.
4. Report state at the cutoff separately from later outcome. `No terminal event observed` is more
   precise than assuming either completion or interruption.

## Unknown artifact or conversation hunt

Use independent evidence lanes only when they match plausible locations:

- transcript or archive search for agent-harness work;
- repository/document search for a saved artifact;
- activity memory or browser history for application/title/time clues;
- authenticated provider history or export for a web-hosted conversation body.

Expand genuine spelling, speech-to-text, title, and identifier variants, but keep the target distinct
from adjacent work on the same topic. Classify results as:

- **lead:** semantic, OCR, title, or recollection clue;
- **metadata-confirmed:** identifier, path, URL, title, or time observed;
- **content-opened:** source inspected but only partial or adjacent evidence found;
- **source-recovered:** requested content opened and directly verified.

Do not turn an activity-memory hit or sidebar title directly into a source-recovered claim.

## Large transcript or corpus analysis

Narrow by the fields the question requires before reading bodies. Use summaries or search results to
choose candidates, then inspect the relevant transcript windows. If delegation is available and the
volume merits it, assign readers non-overlapping sessions or turn ranges and give each:

- the semantic question and requested output fields;
- the source authority and any known omissions;
- exact session IDs or bounded ranges;
- the distinction between direct records, derived fields, and inference.

A `chat_history_researcher` custom agent can be used for this bounded work, but it is not required and
has no mandatory LOCALIZE/ANALYZE sequence. Reconcile contradictions against the authoritative source.

## Coverage-gap recovery

When a likely source is missing the session, first determine whether the gap is caused by scope,
freshness, ingestion, retention, authentication, or unsupported harness/schema coverage. Use another
index or raw store if it records the same needed field. Import, synchronize, rebuild an index, or run
another write/maintenance action only when the user asked for maintenance or when repairing the gap
is necessary and authorized.

For a meaningful negative conclusion, name the relevant surfaces searched, the scope and time window,
and the important surfaces unavailable or omitted. Use `narrow`, `moderate`, or `broad` only when that
label helps the user understand coverage; never claim exhaustive coverage without verifying it.
