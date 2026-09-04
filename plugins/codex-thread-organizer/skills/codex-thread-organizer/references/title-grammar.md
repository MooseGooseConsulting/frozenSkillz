# Codex title grammar

## Purpose

Make adjacent Codex conversations recognizable without reopening them. Every
applied title starts with three to five meaningful emoji, normally three or
four, followed by concrete words. Read the [semantic emoji taxonomy](emoji-taxonomy.md)
before choosing them.

## Prefix shape

Build the prefix in this order:

1. attention, retention, and relationship markers when evidence supports them;
2. one or two domain signals;
3. a work-type signal;
4. a lifecycle marker last when the Codex lifecycle review supports one.

The three required semantic roles are domain, work type, and a distinct state,
relationship, retention role, or second precise domain. Do not use a repeated
or decorative marker to fill a position. Attention remains leftmost; lifecycle
remains last. This permits forms such as `🟡 🤖 🛠️`, `🏠 🛰️ 🔍 ✅`, and
`🗄️ ↪️ 🖥️ 🧹`.

## Status and relationship markers

| Symbol | Meaning | Use when |
| --- | --- | --- |
| `✅` | Done | The latest relevant user request was satisfied and no concrete required action remains in that conversation |
| `🟡` | Concrete follow-up | A specific required action remains in the current owner conversation |
| `🔴` | Highest-priority unfinished work | Use sparingly on the clearest priority after comparing current owners; omit when unclear |
| `⏸️` | Waiting | A named user or external response is the next required event |
| `🚧` | Blocked | A specific obstacle prevents the required outcome |
| `📌` | Canonical task or durable reference | Cross-reading identifies the conversation to retain or continue |
| `↪️` | Continued or superseded elsewhere | A named successor carries the older conversation's unfinished work or replaces its operative result |
| `🗄️` | Archive candidate | The conversation is done with little continuing value, duplicated, or fully carried by a named successor |

Use at most one attention marker (`🔴` or `🟡`) and one lifecycle marker
(`✅`, `⏸️`, or `🚧`). Retention (`🗄️` or `📌`) and relationship (`↪️`) markers
may accompany them but never contradict them: `✅` with `⏸️` or `🚧` is invalid.
`✅` and `🗄️` may coexist; an older continued conversation can use `↪️` and
`🗄️` without `✅`.

## Work-type signals

Use the work-type table in [the taxonomy](emoji-taxonomy.md#work-type-signals).
Choose the one that describes the dominant outcome, not every activity mentioned
in the conversation.

## Construction pass

1. Read and cross-task classify the conversation.
2. Write a plain title from the dominant final work.
3. Add a domain signal and a work-type signal.
4. Add a body-evidenced state, relationship, retention role, or second precise
   domain so the prefix reaches three meaningful emoji.
5. Put attention at the left edge and the lifecycle marker last.
6. Revise once for ambiguity, decoration, and truncation.
7. Keep the final title within the verified 60 UTF-16 code-unit Codex ceiling.

## Examples

| Evidence | Title |
| --- | --- |
| Agent implementation has a concrete next action | `🟡 🤖 🛠️ Agent Harness Repair` |
| Home sensor research is complete | `🏠 🛰️ 🔍 ✅ Home Sensor Comparison` |
| Older hardware cleanup continued elsewhere | `🗄️ ↪️ 🖥️ 🧹 GPU Riser Cleanup` |
| Durable security reference is complete | `📌 🔐 📝 ✅ OAuth Recovery Notes` |

## Definition of done

Add `✅` only when the latest relevant user request was satisfied with adequate
evidence and no concrete required action remains in that conversation. Judge the
bounded conversation, not the broader project. Optional recommendations and
explicitly deferred future phases do not block completion; a requested plan can
be complete while later implementation remains future work.
