# Periodic Codex Automation

## Mechanism

Recurring organization is a periodic Codex automation that explicitly invokes `$codex-thread-organizer`. The frozenSkillz package remains Codex-only and is not installed automatically merely because the repository contains it. Creating the automation is a separate operator action.

## Each Run

1. Inventory tasks changed since the previous successful run and the related recent tasks needed to understand their workstreams.
2. Read the actual conversation bodies for every task whose state or title may change.
3. Cluster by semantic workstream, treating the working directory as a routing clue rather than identity.
4. Cross-read each cluster and identify `done`, `active-remaining`, `continued-elsewhere`, and `parked-unclear` tasks plus the current owner of each unfinished workstream.
5. Construct three-to-five-emoji titles with a domain, work type, and a
   body-evidenced state, relationship, retention role, or second precise domain.
6. Rename only tasks whose bodies were actually read and classified; inaccessible
   and `parked-unclear` tasks keep their titles and go to the report instead.
   Apply through native Codex operations and read every title back.
7. Report renamed tasks, important unfinished current owners, tasks continued elsewhere, archive candidates, parked uncertainties, and coverage gaps.

Use subagents when multiple independent project clusters make the review large enough to parallelize. Each subagent reads the actual conversation bodies for its assigned cluster and returns evidence; the main automation reconciles the classifications before applying titles.

Run an occasional wider inventory so an older current owner or successor does not fall outside the incremental window. Age helps choose what to inspect; it does not decide completion, abandonment, or archive candidacy.

## Checkpoint

Record the most recent successfully reviewed update boundary after the run finishes and the renamed titles have been read back. If a run stops early, reuse the prior successful boundary next time.

## Report

Every run returns:

- inventory and body-reading coverage;
- old and resulting titles;
- completion state and current-owner relationships;
- concrete remaining actions for `🟡` tasks;
- archive-candidate reasons;
- inaccessible or `parked-unclear` tasks needing review.
