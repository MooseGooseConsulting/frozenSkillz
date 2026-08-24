# Periodic Codex Proposal Automation

## Mechanism

Recurring organization is a periodic Codex automation that explicitly invokes
`$codex-thread-organizer` with the **local Codex title review** route. It is
not enabled merely because this package is installed. Creating the automation
is a separate operator action.

Every run writes a dated, linked, proposal-only Notion report. It never changes
a Codex title and does not activate the ChatGPT web route.

## Each run

1. Inventory tasks changed since the previous successful review and the related
   recent tasks needed to understand their workstreams.
2. Read actual bodies and capture direct task links for every task that may
   receive a proposal.
3. Cluster by semantic workstream, using the working directory only as a routing
   clue rather than identity.
4. Cross-read each cluster and identify `done`, `active-remaining`,
   `continued-elsewhere`, and `parked-unclear` findings plus the current owner
   of each unfinished workstream.
5. For multiple independent clusters, dispatch the required `gpt-5.6-luna`
   review workers; reconcile their linked evidence cards against live repository
   context.
6. Construct concise type-and-subject title proposals with semantic emoji; do
   not use lifecycle/status markers in titles.
7. Write the complete report: reviewed scope, coverage gaps, current and
   proposed titles, emoji rationale, lifecycle findings, open work, archive
   candidates, and `No action executed`.

Run an occasional wider inventory so an older current owner or successor does
not fall outside the incremental window. Age helps choose what to inspect; it
does not decide completion, abandonment, or archive candidacy.

## Checkpoint

Record the most recent successfully reviewed update boundary and the Notion
report link. That checkpoint is an aid for choosing the next review window, not
evidence that a prior task or repository is currently active. If a run stops
early, preserve its partial-coverage report and retry from the prior successful
boundary.
