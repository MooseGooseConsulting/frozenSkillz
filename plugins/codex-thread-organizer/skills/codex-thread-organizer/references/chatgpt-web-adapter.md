# ChatGPT web proposal adapter

Use this adapter only for the explicitly selected **ChatGPT web proposal**
route in Codex Desktop. It is a browser-backed evidence pass that writes a
linked Notion proposal report. It never changes ChatGPT.

Browser retrieval is performed by the configured `chrome_pilot` worker. The
analysis role is reserved for an explicitly configured **Codex 5.3 Spark**
subagent; do not silently replace that requested profile with another model. If
that profile is unavailable, record the route as blocked before producing
organization conclusions.

## Declare the review scope first

Never default to a full-history body review. A history with thousands of chats
is organized through explicit, repeatable cohorts, not one impossible pass.

A body-review cohort contains at most 30 conversations. For a larger request,
partition by a user-requested recent range, named Project, date range, or
explicit candidate set, and record the next deferred cohort. Do not relabel all
history as one bounded cohort.

Before opening bodies, record:

| Scope field | Required record |
| --- | --- |
| Requested coverage | Requested set: recent 30, named Project, date range, topic, or explicit chat list |
| Inventory coverage | History rows inspected to select candidates, plus what remains uninspected |
| Body-review cohort | At most 30 conversations opened and classified from their bodies |
| Deferred set | Conversations left for a later cohort, why, and the next cohort |

History titles, previews, dates, and existing Project labels may select a
candidate cohort, but are `inventory-only` hints. They establish no topic,
relationship, disposition, or proposal. Do not call an all-history request
complete until every accessible chat was body-reviewed; otherwise report the
completed cohort and deferred coverage.

## Gather the corpus

Use ChatGPT's history container, including lazy-loaded history, for the
declared inventory coverage. Open every chat in the body-review cohort and make
the shared chat card from its body, including its direct `chatgpt.com` link. An
independently analyzed cluster returns detailed cards and source links, not
titles alone. The coordinating agent verifies cited bodies before claiming a
relationship across clusters.

If a cohort chat cannot be opened, record its link/identity as unavailable and
exclude it from title or Project proposals. State partial cohort coverage; do
not silently shrink the requested set.

When Codex work is in scope, open the actual Codex task bodies for the declared
bridge cohort and read [cross-surface bridge](cross-surface-bridge.md). Do not
bridge from matching ChatGPT/Codex titles, previews, or Project labels.

## Initial triage: decide the proposed home

A ChatGPT Project is one possible home, not a default. For each body-reviewed
chat, select a disposition supported by body evidence:

| Disposition | Meaning | Project proposal |
| --- | --- | --- |
| `project-home` | Durable work with an existing coherent ChatGPT Project | Propose moving to that existing Project |
| `canonical-reference` | Best known answer, decision, artifact, or source among body-reviewed chats in this cohort for a recurring question | Retain it as a named reference; move only when a Project genuinely fits |
| `standalone-reference` | Useful answer that is not durable Project work | Improve its title; do not force a Project |
| `new-project-candidate` | Coherent durable workstream with no existing Project fit | Propose a new Project only when the new-Project evidence rule is met |
| `archive-candidate` | Trivial, one-off, or resolved material | Flag as a possible later archive; do not archive |
| `duplicate-or-superseded` | Useful result is represented by another identified chat | Link its representative; propose no Project change unless the destination is clear |
| `needs-human-choice` | The body does not establish a confident home or retention decision | Keep unchanged and state the ambiguity |

Use `project-home` only for a durable shared outcome with a real existing
Project fit. A new Project requires an explicit ongoing user project or a
coherent workstream with at least two body-reviewed chats and no existing fit.
A `project-merge-candidate` identifies source Projects, target Project, and the
exact reviewed chats that would move. It is a proposal; it does not claim a UI
operation would merge Projects.

## Write the ChatGPT proposal report

Group the cards into workstreams, compare their body evidence, and identify at
most one `canonical-reference` among successfully body-reviewed chats in the
declared cohort per concrete question or decision. Its title names what it lets
the user find again, not merely its original question.

Create the Notion report with the scope declaration first, then an evidence
worksheet with exactly one row per body-reviewed chat:

| Conversation link | Current title / Project | Detailed body summary | Workstream, relationship, and evidence | Codex bridge link/result | Disposition and retrieval reason | Proposed title and semantic emoji meaning | Project proposal |
| --- | --- | --- | --- | --- | --- | --- | --- |

The Project proposal is exactly one of `move-existing`, `create-new`,
`merge-by-proposed-moves`, or `none`. A new Project includes name, purpose, and
reviewed seed chats. A merge includes source, target, and exact proposed moves.
Every cited repository, artifact, Codex task, and ChatGPT chat has a direct
link.

Self-grade every proposed row: it must be body-reviewed, in the declared
cohort, supported by concrete body evidence, retrievable by title, and use one
to three semantic emoji with a stated reason. A confirmed bridge may inform a
proposal; plausible or unresolved bridges remain visible uncertainty. Do not
turn lifecycle/status markers into ChatGPT title emoji.

End the report with `No action executed`: do not use Rename, Move to Project,
Create Project, Merge, or Archive browser controls under this skill.
