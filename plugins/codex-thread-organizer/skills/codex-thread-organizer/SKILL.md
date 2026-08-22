---
name: codex-thread-organizer
description: >-
  Use when Codex sidebar titles are unclear, related tasks need completion or
  supersession review, important unfinished work is hard to find, or a periodic
  Codex organization pass is requested. Covers every conversation the Codex app's
  sidebar exposes, including ChatGPT conversations shown there.
---

# Codex Thread Organizer

Organize the conversations the Codex app exposes from their actual conversation bodies. When this skill is invoked, inventory the selected sidebar surface, rename the conversations the native title operation can act on, read the resulting titles back, and summarize the important unfinished work.

## Boundary

- This skill covers what the Codex app's sidebar exposes, including ChatGPT conversations that appear there. Conversations the native title operation cannot act on are still inventoried and classified; they are reported honestly rather than renamed.
- Anything the Codex sidebar does not expose is out of scope; there is no other client's history to reach from here.
- Packaging is Codex-only: the source lives in frozenSkillz's dedicated Codex package and is not auto-installed with every skill.
- A periodic Codex automation is the mechanism for recurring organization; the skill is not a background daemon.

## What the native 50-item limit means

The native `list_threads` operation's `limit` applies to **non-pinned
conversations**, not repositories. With `limit: 50`, it returns all pinned
conversations in full **plus up to 50 most recent non-pinned conversations**,
in recency order. Either set can contain Codex or ChatGPT conversations.

- Thus, an inventory can contain more than 50 entries: for example, eight pins
  plus a full 50-entry non-pinned page is a 58-conversation inventory.
- “50” never means 50 repositories, 50 Codex tasks, or all ChatGPT history.
- A returned ChatGPT conversation should be read by its returned ID, but a
  stale or unavailable individual ID is an explicit per-entry coverage gap. The
  native title operation may still reject a readable ChatGPT conversation; that
  is a title-capability distinction, not a visibility distinction.
- Unless pagination or a load-more capability is available and exhausted, this
  is a bounded, partial view—not the complete sidebar or account history.

## Workflow

1. **Inventory every accessible sidebar conversation.** Use the native list operation before filtering by kind. Record task ID, kind, host ID, current title, update time, working directory, project ID, and summary or preview. Never exclude ChatGPT conversations, pinned conversations, or another returned kind merely because it is not a Codex task. Apply the native-limit semantics above: `limit: 50` means 50 most recent non-pinned conversations plus all pinned conversations, not repositories. If the operation has a page, cursor, or load-more control, exhaust it. If its maximum result count prevents that, record a `bounded inventory` with `partial coverage`, state the exact limit and pinned count, and never describe the result as “all chats.”
2. **Classify title capability.** For each inventoried conversation, determine whether the native title operation supports its kind. Mark supported targets `title-mutable`; mark unsupported targets `not title-mutable` with the exact failed operation or missing capability. A request to organize or rename “all chats” scopes every accessible conversation; it does not authorize silently shrinking that scope.
3. **Form tentative workstream clusters.** Use repository identity, project, branch, pull request, issue, artifact, and semantic goal. A working directory is a routing clue, not proof that tasks belong together.
4. **Read the actual conversation bodies.** For every task being classified or renamed, identify the opening request, later changes of scope, delivered outcome, concrete required action, user acceptance or dispute, and references to successor tasks or durable artifacts.
5. **Cross-read related tasks.** Compare every recent relevant task in the workstream before deciding which task owns unfinished work. Follow [references/cross-task-review.md](references/cross-task-review.md).
6. **Classify and title.** Determine whether each task is `done`, `active-remaining`, `continued-elsewhere`, or `parked-unclear`, then apply [references/title-grammar.md](references/title-grammar.md).
7. **Rename the `title-mutable` targets.** Recheck each `title-mutable` target's current title immediately before mutation; skip and report concurrent changes. Use the native Codex title operation. Re-read every resulting title and correct any mismatch or truncation. Do not write an internal state store or pretend a `not title-mutable` kind was renamed.
8. **Report the result.** Report the inventory total with its coverage status — `complete`, or `bounded` with the exact limit from step 1 — and separate mutated, already-correct, skipped, and `not title-mutable` totals. Never present a bounded total as a complete one. List renamed tasks, the current owner of each unfinished workstream, important concrete remaining actions, tasks continued elsewhere, parked uncertainties, and archive candidates.
9. **Export before detailed synthesis.** When the user asks for detailed summaries, durable retention, or a database, follow [durable native transcript export](references/durable-transcript-export.md). Use the native `list_threads` and paginated `read_thread` operations first; do not replace them with browser scraping merely because a chat title lacks a summary. Preserve the bounded-inventory evidence and native turn data locally before deriving summaries.

When several project clusters can be reviewed independently, dispatch one subagent per cluster. Give each subagent the task IDs and require it to read the actual conversation bodies. The main agent reconciles relationships and titles across the returned clusters.

## Title Contract

- Use one to five leading semantic symbols, never five by default. Most titles need one to three.
- Keep the words specific and recognizable, normally about 5–12 words.
- Preserve exact product, repository, issue, pull request, and artifact names when they aid recognition.
- Keep the final title within 60 UTF-16 code units, the empirically observed native Codex title ceiling: a verified 2026-07-20 batch found longer values persisted with a literal trailing ellipsis. That ceiling is verified for `title-mutable` Codex targets; document a different verified limit before applying one to another conversation kind.
- `✅` means the latest relevant user request was satisfied and no concrete required action remains in that task. It does not claim that the broader project is finished.
- `🟡` means a concrete required action remains in the current owner task.
- Use `🔴` sparingly on the clearest highest-priority unfinished task; omit it when the comparison is unclear.
- `⏸️` means a named user or external response is the next required event; `🚧` means a specific obstacle blocks the required outcome.
- `🗄️` marks a reasonable archive candidate. It may accompany `✅`, or identify an older unfinished task whose work clearly continued elsewhere.
- Use `📌` and `↪️` only when cross-reading establishes a canonical task or a named successor.

Examples:

```text
🌊 🧹 Crest Research Pruning
🌊 🧹 ✅ Crest Research Pruning
🟡 🌊 🛠️ Broadside Implementation Continuation
🗄️ ↪️ 🧛 Vampire Survivors Continuation
🗄️ ✅ Techdeals PR #84 Review
```

## Completion Check

Before adding `✅`, answer these questions from the task body:

1. What was the latest relevant user request?
2. Did the answer, artifact, change, test, publication, or other requested outcome actually satisfy it?
3. Does any required execution, verification, recovery, decision, or user input remain?
4. Did a later user turn extend the scope or dispute the claimed result?

Optional ideas, recommendations, and explicitly deferred future phases do not block completion. A bounded task can be complete while its broader project remains unfinished. A planning task is complete when the requested plan was delivered; a request to implement that plan is not complete merely because the plan exists.

## Periodic Automation

Read [references/periodic-automation.md](references/periodic-automation.md) when defining or running recurring organization. Each run uses the same inventory, title-capability classification, body-reading, cross-task classification, rename, read-back, and unfinished-work report workflow.
