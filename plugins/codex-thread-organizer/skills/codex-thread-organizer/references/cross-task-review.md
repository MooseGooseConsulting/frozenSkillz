# Cross-Task Review

## Goal

Read recent related Codex tasks together, identify the current owner of unfinished work, and distinguish completion from continuation or dormancy.

## Build the Workstream

Start with working directory, project ID, and update time as routing clues. Confirm the cluster from the actual conversation bodies using repository identity, branch, pull request, issue, artifact, durable output, and semantic goal.

The same path can contain unrelated work. Different or generic paths can contain the same workstream. A relationship requires shared work, not merely shared location or vocabulary.

For every candidate, read enough to identify:

- the latest relevant user request;
- later extensions, corrections, or disputes;
- the delivered outcome;
- every concrete required action still owed;
- named branches, commits, pull requests, issues, files, and artifacts;
- explicit continuation, duplication, correction, replacement, or weaker
  related-work evidence.

## Completion States

| State | Meaning | Visible treatment |
|---|---|---|
| `done` | The latest relevant user request was satisfied and no concrete required action remains in that task | Eligible for `✅` |
| `active-remaining` | Required work remains and this is the current owner of that workstream | Eligible for `🟡` |
| `continued-elsewhere` | The task stopped with required work remaining, but a named newer task clearly assumed that work | No `✅`; eligible for `↪️` and `🗄️` |
| `parked-unclear` | Work remains, no current owner or successor is clear, and the user's present intent cannot be inferred | No `✅`; keep visible for review |

An agent response is not completion by itself. An answer or review must cover the requested scope; a change, test, publication, or real-world operation must reach the state the user requested.

Judge the bounded task rather than the broader project. Research can be done before a purchase occurs. A pull-request update can be done before merge when merge was not requested. A dev-server demonstration can be done even though the server later stops.

Optional future work does not block `done`. A later user turn that extends the request becomes part of the completion check. Interrupted, failed, disputed, or blocked work remains unfinished until the required result is recovered or the later conversation clearly changes the scope.

## Choose the Current Owner

For each unfinished workstream, identify one current owner when the evidence supports it:

1. Prefer a task that explicitly continues the earlier work.
2. Confirm that it shares the same goal, implementation state, artifact, branch, issue, or pull request.
3. Confirm that the older task has no distinct required action excluded from the successor.
4. Classify the older task as `continued-elsewhere` and keep `✅` off it.

If an older task completed its own scoped deliverable, keep it `done` even when a successor performs a later phase. A task that delivered the requested plan is done; a task that stopped mid-implementation and was resumed elsewhere is continued elsewhere.

Parallel tasks remain separate owners. Design reconciliation, implementation, and a repository audit can share a project without superseding one another.

## Use Subagents for Larger Reviews

When the inventory contains several independent project clusters, assign one cluster to each subagent. Provide task and host IDs, require body reading, and request this compact result for every task:

- state and confidence;
- latest relevant user request;
- completion or remaining-action evidence;
- current owner, predecessor, or successor IDs;
- relationship: `continues`, `supersedes`, `duplicates`, `corrects`, `related`,
  or `independent`;
- archive-candidate judgment and reason.

The main agent compares the cluster results, resolves overlaps, constructs titles, applies the renames, and reads them back.

## Age and Archive Candidates

Age helps order the review. It does not prove abandonment, completion, or irrelevance.

`🗄️` is appropriate when a completed one-off has little continuing reference value, a duplicate has a retained canonical task, or an older unfinished task is fully carried by a named successor. A durable completed reference may remain visible. An `active-remaining` current owner and a `parked-unclear` task remain visible.

## Review Output

For each task retain: task and host IDs, workstream basis, state, confidence, latest request, outcome, remaining action, related task IDs, applied markers, archive-candidate reason, and resulting title. End with the important unfinished current owners and every parked uncertainty.
