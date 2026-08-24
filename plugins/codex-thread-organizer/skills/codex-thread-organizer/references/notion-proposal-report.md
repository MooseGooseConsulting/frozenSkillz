# Notion proposal report

Every successful organizer route ends by creating one dated page in the
**Codex Desktop Chat Organization Reports** Notion database. Resolve that
database by title, fetch its live data-source schema, and do not hard-code a
personal workspace identifier.

Set these database properties:

| Property | Local Codex route | ChatGPT web route |
| --- | --- | --- |
| `Workflow` | `Codex local title review` | `ChatGPT web proposal` |
| `Scope` | `Codex desktop only` | `Codex desktop only` |
| `Freshness` | `Point-in-time — not current` | `Point-in-time — not current` |
| `Chats Reviewed` | Count of body-reviewed tasks | Count of body-reviewed chats |
| `Chats Renamed` | `0` | `0` |
| `Status` | `Captured` | `Captured` |

The page title starts with the run date and route. Its body begins with a clear
warning: this is historical, point-in-time evidence, **not current state**, and
it is exclusively an organizer proposal report. A later run must re-read the
live conversations and repository context instead of treating the report as
current truth.

Include the selected route, scope/coverage, worker and model roster, live
coding-project/repository context and when it was checked, deferred/unavailable
coverage, and the complete evidence worksheet required by the selected adapter.
Every body-reviewed conversation row needs a direct source link. Include direct
links for every cited Codex task, ChatGPT chat, repository, pull request,
issue, file, artifact, or Project where the source exposes one. Do not replace
a missing direct link with a label-only assertion; record the row as unavailable
or incomplete instead.

End with `No action executed` and list each proposed title, Project move, Project
creation, Project merge-by-proposed-moves, or archive candidate as a proposal.
Do not call a local title operation or a ChatGPT browser mutation before, while,
or after writing the report.
