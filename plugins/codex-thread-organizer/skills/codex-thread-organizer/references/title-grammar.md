# Sparse Codex Title Grammar

## Purpose

Make adjacent Codex tasks recognizable in a narrow sidebar. The emoji explains
the **type of work**, while concise words say what concrete work occurred. It
does not claim priority, completion, blocking state, or any other lifecycle
status.

## Prefix shape

Use one to three leading semantic emoji, normally one or two:

1. project, product, or domain when it materially distinguishes nearby tasks;
2. work type; and
3. a more specific semantic emoji only when needed.

The words following the emoji name a concrete system/artifact plus action,
decision, failure, or outcome. Do not use emoji as decoration or instead of the
retrieval words.

## Work-type emoji

| Emoji | Meaning | Use when |
| --- | --- | --- |
| `🔍` | Research, audit, or investigation | The outcome is findings or diagnosis |
| `🛠️` | Implementation or repair | The task materially changes a system or artifact |
| `🧭` | Planning or orientation | The durable outcome is scope, a plan, or a decision frame |
| `📝` | Documentation | Documentation is the primary deliverable |
| `🧹` | Cleanup or pruning | The dominant work removes, consolidates, or retires clutter |

Treat these as defaults rather than an exhaustive taxonomy. Use a clearer
project/domain symbol from the semantic emoji taxonomy when it helps a user
scan related chats.

Do not add `✅`, `🟡`, `🔴`, `⏸️`, `🚧`, `📌`, `↪️`, or `🗄️` as a title marker in
this workflow. A review may record lifecycle or retention findings in Notion,
but the proposed title remains a type-and-subject label.

## Construction pass

1. Read the task body and compare it with its body-derived workstream.
2. Write a plain title from the dominant final work.
3. Add the known project/domain emoji when it distinguishes the title.
4. Add a work-type emoji when it gives useful at-a-glance context.
5. State the semantic meaning of every proposed emoji in the report.
6. Revise once for ambiguity, decoration, and truncation.
7. Measure the final title in UTF-16 code units and keep it within the empirical
   60-unit Codex ceiling. Use a literal trailing ellipsis when shortening is
   necessary.

## Examples

| Body evidence | Proposed title |
| --- | --- |
| Repository audit that finds a stale deployment setting | `☁️ 🔍 Deployment setting audit` |
| Fix to the local serving configuration | `🤖 🛠️ Local serving configuration fix` |
| Plan for a cross-service organization pass | `🧭 Cross-service organizer plan` |
| A durable guide for a project's runbook | `🏠 📝 Homelab runbook guidance` |

These examples are proposal labels only. This skill writes them to Notion and
does not apply them to Codex tasks.
