# Choosing a source

Choose the source that stores the requested field across the required scope. Availability, coverage,
and freshness are live facts: probe them rather than assuming that an installed client, configured
credential, or known database contains the needed sessions.

## Capability matrix

| Surface | Useful capabilities | Important limitations |
|---|---|---|
| Raw harness transcripts | Original message records, tool payloads and results, event order, raw metadata, and often parent/child links | Harness-specific schemas; large or compacted files; local files cover only the machines and retention windows present |
| AgentsView | Search and drill-down across ingested harnesses; local or central archives; machine/project/session inventories; usage and derived health/outcome fields | Indexed coverage and sync freshness must be checked; projected fields and generated labels are not substitutes for raw records; exact capabilities vary by version and backend |
| Kurrent Capacitor | Search and turn-level drill-down; repository/session-chain context; PR/file review context when those features and relationships are available | Native and imported harness coverage differ; optional analytics, project, or review features can be plan- or server-gated; summaries and scores are derived |
| Pieces | Captured application/window/page/time context, OCR, and surrounding activity useful for locating a web or desktop conversation | Activity memory is not the conversation transcript; coverage is capture-dependent; OCR, URLs, timestamps, scores, and entities can be noisy |
| Provider export/history | Conversation body and provider-owned identifiers for chats hosted by ChatGPT, Claude.ai, Gemini, or another web service | Requires the correct account and access; browser retrieval can be slow and stateful; provider views or exports may omit harness-only tool/event metadata |
| Current repository or live system | Present implementation, review, deployment, and runtime truth | Does not by itself explain the earlier conversation or intent |

No row is a universal first choice. An exact payload question can start at a known raw file. A broad
cross-harness topic search can start at the archive with the best verified coverage. A question about
an earlier agent's PR/file rationale can start at a surface that records those relationships. A plain
question about the current PR or file belongs to the current repository or review authority instead
of chat history. A web-chat title or approximate time can start with activity or browser history.

## Authority and corroboration

Use the source that owns the field:

- Raw harness transcript: exact harness-emitted payloads, metadata, and sequence.
- Provider history or export: exact provider-hosted conversation body and provider identifiers.
- Index/archive: its own ingestion status, relationships, and documented derived metrics.
- Activity memory: what its capture observed, not what the underlying conversation necessarily said.
- Current code, PR, or runtime: whether the discussed work is now present and working.

One request can require more than one authority. For example, an archive can locate a session, the
raw transcript can establish the tool result, and the live repository can show whether that result
still reflects the current code.

## Coverage questions

Before a broad negative or aggregate claim, check the dimensions that matter:

- harnesses and provider-hosted histories included;
- local versus fleet/central stores;
- machines, repositories/projects, child or continuation sessions, and automated sessions;
- earliest/latest indexed time and synchronization status;
- content fields indexed or omitted, including tool bodies, system records, and deleted/archived
  conversations;
- optional features, account/plan gates, and authentication boundaries.

A failure in one route is evidence about that route, not proof that the conversation does not exist.
Choose another source only when it can answer the same requested field or when it supplies a distinct
field needed to finish the task.
