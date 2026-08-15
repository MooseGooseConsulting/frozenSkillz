# Cross-Thread Relevance Review Design

## Status

Owner-approved capability; implementation design awaiting owner review.

## Goal

For a repository or project family, review related accessible Codex thread bodies together and produce an evidence-backed, read-only assessment of which threads remain current, which are durable references, and which later work may supersede or duplicate them.

## Why this belongs in the organizer

A flat sidebar does not merely hide threads behind bad titles. It also makes it difficult to tell whether an older plan remains authoritative, whether later work completed it, or whether a newer conversation replaced it. A title-only classifier cannot make that judgment safely because the relevant evidence is distributed across multiple conversations and, where available, the repository itself.

## First-version boundary

The first version is a native-Codex, proposal-only review workflow.

It does:

- inventory accessible threads;
- attribute threads to a repository or project family using working directory, repository identity, and transcript evidence;
- read the relevant bodies, including later substantive outcomes and unresolved work;
- compare related threads and identify evidence-backed relationships;
- emit a durable review manifest.

It does not:

- rename, pin, archive, reparent, delete, merge, or alter any thread;
- classify a thread as irrelevant only because it is old;
- treat a current title, preview, or first user message as sufficient evidence;
- claim a relationship across repositories without supporting evidence;
- include ChatGPT web conversations or inaccessible Codex threads.

## Inputs and attribution

The review begins with an accessible Codex thread inventory. For each candidate, the workflow records its ID, host, title, timestamps, working directory, and available preview only as routing metadata.

Repository attribution is determined in this order:

1. Resolve the actual repository root from the thread's working directory when it remains available.
2. Use a stable repository or project identity named in the body, such as a repository name, remote, branch, issue, pull request, artifact, or explicit path.
3. Use a stable user-provided project-family override when one exists.
4. Otherwise classify the thread as unassigned rather than guessing.

A dated task folder, an attachment path, or a title alone is not repository identity.

## Evidence collection

For every thread in a selected family, the reviewer reads enough of the body to identify:

- the dominant purpose and deliverable;
- later pivots or corrections;
- substantive outcome and remaining work;
- referenced branches, commits, pull requests, issues, files, and artifacts;
- explicit links to earlier or later conversations;
- whether the thread itself says it supersedes, continues, or corrects another thread.

Long threads may be paged selectively, but the opening request, later substantive outcome, and relevant relationship evidence must be read before a classification is emitted.

## Relationship model

Each thread receives one review classification and zero or more directed relationships.

| Classification | Meaning |
|---|---|
| `current` | The best available current source for a workstream or decision. |
| `completed-reference` | Its scoped work has a durable result worth retaining, even if later work exists. |
| `superseded` | Later identified work replaces its plan, decision, implementation, or authoritative outcome. |
| `duplicate` | It substantially repeats another thread without a distinct durable result. |
| `needs-review` | Evidence is incomplete, conflicting, or too weak for a safe conclusion. |

| Relationship | Direction and meaning |
|---|---|
| `continues` | Later thread advances remaining work from an earlier thread. |
| `supersedes` | Later thread replaces the earlier thread's operative result. |
| `corrects` | Later thread repairs or reverses a material earlier conclusion. |
| `duplicates` | Threads substantially cover the same work without distinct durable outcomes. |
| `independent` | Same family, but no meaningful operational relationship. |

`current` is not synonymous with newest, and `completed-reference` is not a candidate for removal merely because it is old.

## Evidence and confidence policy

Every relationship records a short evidence summary and one of three confidence levels:

- `high`: explicit successor language, a shared named artifact or issue/PR with later verified state, or direct repository evidence.
- `medium`: aligned subject, repository, deliverable, and chronology strongly support the relationship, but no explicit successor statement exists.
- `low`: a plausible connection exists but decisive evidence is absent; classify as `needs-review`, not `superseded` or `duplicate`.

Age ranks review priority only. It can never, by itself, produce `superseded`, `duplicate`, `irrelevant`, or an archive recommendation.

## Manifest

The read-only output contains one record per reviewed thread:

| Field | Purpose |
|---|---|
| `thread_id`, `host_id` | Stable target identity. |
| `repository_family` and attribution basis | Explain why threads were compared. |
| `current_title` | Human review context only; never classification evidence. |
| `classification` and `confidence` | Review conclusion. |
| `related_threads` | Directed relationship, target IDs, and evidence. |
| `outcome_summary` and `remaining_work` | Body-derived context. |
| `proposed_follow_up` | `keep`, `review`, or a separately authorized future mutation candidate. |

The manifest also records inventory coverage, inaccessible threads, unassigned threads, ambiguous relationships, and the exact review time.

## Mutation boundary

This feature has no archive, pin, reparent, or rename side effect. A later authorized batch may consume high-confidence review results, but it must recheck the live thread state and use the existing mutation and read-back rules. No automated archival policy is introduced by this design.

## Acceptance checks for the first implementation

1. A reviewer can select one repository or project family and obtain a manifest without changing any native thread state.
2. Every `superseded` or `duplicate` classification links to specific supporting thread IDs or repository evidence.
3. An old but completed durable reference remains distinguishable from a superseded thread.
4. A sparse or ambiguous thread becomes `needs-review`, not a guessed relationship.
5. A report makes it possible for the owner to review proposed follow-up actions without reopening every thread.
6. The workflow reports that it cannot cover inaccessible threads rather than treating them as irrelevant.
