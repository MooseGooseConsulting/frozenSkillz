# Orchestration Shape

Decide the shape before writing any prompt. A well-briefed worker in the wrong topology still produces conflicts a briefing cannot prevent.

## When to delegate at all

Delegate when work has **independent phases** or produces **bulky intermediates** you do not need in context.

Do it yourself when the whole change fits one sitting and a handful of files. The overhead of specifying, spawning, and reading back exceeds the work.

The failure worth naming: quietly implementing a multi-phase plan solo. It looks like progress and burns the orchestrator's context on material a worker should have absorbed.

## Reads fan out. Writes stay single-threaded.

**This is the one structural rule, and it outranks prompt quality.**

- **Read-only workers may run wide.** They share the repo concurrently and conflict with nothing.
- **Writers should be single-threaded.** Parallel writers cannot see each other's intermediate decisions and reconcile only at merge, by which point each has built on assumptions the others never learned.

If parallel edits are genuinely required, give each writer `isolation: "worktree"` and treat the merge as a real integration step with its own verification — not as a formality.

Why this ranks above the send contract: a briefing is written at t=0 and cannot carry a decision made at t>0. Inter-agent misalignment accounts for roughly a third of observed multi-agent failures and is out of reach of any prompt. Structure is the only lever that touches it.

## Batch before you multiply

Every spawn pays fixed overhead — system prompt, project rules, tool schemas — before doing anything useful.

- Five greps are **one** worker with a checklist, not five workers.
- Spawn separately only when true parallelism or isolation earns that overhead back.

## Research fan-out

The shape that works, because it keeps writes single-threaded:

1. **You** pick the questions and the sources. Never delegate that.
2. **One worker per source.** It fetches the source verbatim to `./.workflow/scratch/` **first** — the disk copy is the audit trail, with no relevance filtering during the fetch — then returns a brief built from that copy: claims, evidence, exact quotes, confidence, contradictions, and the path.
3. **One synthesizer** reads across the briefs.
4. **You** check the synthesis against the ledger and decide.

Intermediates never enter your context. The fetch-then-brief order matters: filtering during the fetch destroys the evidence before anyone can audit it.

## Verification

Mandatory before closing, and the verifier must be **fresh** — it did not build the work.

Give it the original request, the ledger path, and the work-product paths (diffs, reports — not the raw scratch dump). It reads from disk. Its only job is to find what is missing, wrong, or unaddressed, item by item.

Only the verifier closes `- [ ] V.`. Findings become new phases; re-verify after fixes; **cap at 3 cycles**, then stop and report open items rather than looping.

## Context hygiene

- Consume briefs and short verbatim snippets; bulk stays on disk.
- When a decision hinges on exact content that is short, **read it yourself.** Never decide on a summary when the source fits in a few hundred lines.
- Prefer per-task sessions. The ledger and scratch survive a clear, so finish a task, close it, start the next clean.

## What is deliberately absent

This skill carries no hooks, no process supervision, and no model-tier routing.

Enforcement machinery was evaluated and rejected: the guard hooks from the source plugin were POSIX/tmux-bound, and the one portable guard gated on prompt length against a threshold that measured default behavior never reaches. Tier routing was tied to a token economy this repo does not share.

What remains is doctrine, which is the part that transfers. If any of it is ever mechanized, check for contract *content*, never for size.
