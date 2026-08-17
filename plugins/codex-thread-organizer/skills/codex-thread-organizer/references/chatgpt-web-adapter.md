# ChatGPT web adapter

Use this adapter only for authenticated conversations at `chatgpt.com`. This
is a browser-backed organization pass, not a title-only sidebar cleanup.

## Declare the review scope first

Never default to a full-history body review. A history with thousands of chats
must be organized in explicit, repeatable cohorts, not one impossible pass.

A body-review cohort contains at most 30 conversations. For a larger request,
partition the work by a user-requested recent range, named Project, date range,
or explicit candidate set, and record the next deferred cohort. Do not relabel
all of history as one bounded cohort.

Before opening bodies, state:

| Scope field | Required record |
| --- | --- |
| Requested coverage | The user's requested set, such as recent 30, a named Project, an identified topic, or an explicit chat list |
| Inventory coverage | Which history range/rows were inspected to select candidates, and what remains uninspected |
| Body-review cohort | At most 30 conversations whose bodies will actually be opened and classified |
| Deferred set | Conversations deliberately left for a later cohort, why, and the next cohort to review |

History titles, previews, dates, and existing Project labels may select a
candidate cohort, but they are `inventory-only` hints. They establish no topic,
relationship, disposition, or mutation. Do not call a requested all-history
organization complete unless every accessible chat has actually been body
reviewed; otherwise report the completed cohort and deferred coverage.

## Gather the actual conversations

Use the ChatGPT history container, including its lazy-loaded history, for the
declared inventory coverage. Initial visible rows are not the whole history.
Open every conversation in the body-review cohort and make the shared chat card
from its body. If an independent cluster is delegated, the subagent returns
detailed cards, not proposed titles alone. The main agent checks cited bodies
before claiming a relationship across clusters.

If a cohort conversation cannot be opened, record its identifier/title as
unavailable and exclude it from rename and Project-move proposals. State
partial cohort coverage plainly; do not silently shrink the requested set.

When Codex work is in scope, open the actual Codex task bodies for the declared
bridge cohort and read [cross-surface bridge](cross-surface-bridge.md). Do not
bridge from a matching ChatGPT or Codex title, sidebar preview, or Project label.

## Initial triage: decide the home before proposing a move

A ChatGPT Project is one possible home, not the default destination. For each
body-reviewed chat, assign one disposition from its body evidence:

| Disposition | Meaning | Initial proposal |
| --- | --- | --- |
| `project-home` | Durable work that belongs with an existing, coherent ChatGPT Project | Propose that existing Project and a specific title |
| `canonical-reference` | The best known answer, decision, artifact, or source **within this declared cohort** for a question likely to recur | Retain it as the cohort's named reference; move it only if a Project genuinely fits |
| `standalone-reference` | A useful answer worth finding again, but not part of a durable Project | Improve its title; do not force a Project move |
| `archive-candidate` | Trivial, one-off, or already-resolved material that should no longer crowd active history | Flag for separate user approval; do not archive automatically |
| `duplicate-or-superseded` | An older or parallel chat whose useful result is represented by another identified chat | Link it to the representative chat; propose no move unless its destination is clear |
| `needs-human-choice` | The body is meaningful but does not establish a confident home or retention decision | Keep unchanged and state the exact ambiguity |

Use `project-home` only when the work has a durable shared outcome and a real
existing Project fits it. A single useful answer is often a
`standalone-reference`; a short question with no lasting value is often an
`archive-candidate`. Do not create a catch-all Project for one-off questions.

A new Project is a `new-project-candidate`, not a default: propose it only for
an explicit ongoing user project or a coherent workstream with at least two
body-reviewed chats and no existing Project fit. A `project-merge-candidate`
identifies its source Projects, target Project, and the exact reviewed chats
that would move; it does not claim that a ChatGPT move automatically merges
Projects.

## Produce a proposal before mutation

Group the body-reviewed cards into workstreams, compare relationships, and
identify at most one `canonical-reference` **within the declared cohort** per
concrete question or decision unless the evidence shows distinct answers. Carry
the cohort scope with that label. A `canonical-reference` title must name what
it lets the user find again, not merely the chat's original question.

Show the scope declaration before the evidence worksheet. The worksheet has one
row per body-reviewed conversation, never one row per inventory-only candidate:

| Conversation | Current title / Project | Detailed body summary | Workstream, relationship, and evidence | Codex bridge | Disposition and retrieval reason | Proposed title and emoji meaning | Project action |
| --- | --- | --- | --- | --- | --- | --- | --- |

`Project action` is exactly one of: `move-existing`, `create-new`,
`merge-by-approved-moves`, or `none`. A new Project proposal includes its name,
purpose, and reviewed seed chats. A merge proposal includes the source and
target Projects, and no action is implied until each move is approved.

Then self-grade the proposal. For every actionable row, check that:

1. The conversation is in the declared body-review cohort; inventory-only and
   deferred conversations have no classification or proposed mutation.
2. The summary, relationship, title, and disposition are supported by body evidence.
3. The title names a concrete system/artifact and action/outcome, or the
   specific answer/decision that makes a reference retrievable.
4. Each emoji has a stated semantic reason, there are one to three at most, and
   no Codex lifecycle/status marker has been added.
5. `move-existing` is proposed only for `project-home`; `create-new` meets the
   new-Project evidence rule; a merge names source, target, and exact moves.
6. Archive candidates remain proposals, duplicate/superseded chats identify
   their representative chat, and unavailable chats have no invented proposal.
7. Each Codex bridge is `confirmed`, `plausible`, `unresolved`, or `no-link`
   with body evidence; only confirmed bridges inform proposals.

Correct or omit rows that fail these checks. Present the worksheet, the
self-grade, and the exact actionable subset to the user for approval.

## Apply only approval

After the user approves particular rows, use ChatGPT's own Rename and Move to
project controls for those rows only. Create a new Project only after separate
explicit approval and only if the UI exposes that control; otherwise report it
as unavailable. A Project merge consists only of the individually approved
moves to its target; do not claim a merge when the UI does not expose one.
Treat archive as a separate explicitly approved action; this adapter does not
infer archive approval from an approved rename or Project move. Browser mutation
belongs to this ChatGPT adapter; it is not a general browser-tab operation. Do
not require a separate post-mutation readback pass unless the user asks for one.
