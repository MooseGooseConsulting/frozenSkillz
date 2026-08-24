---
name: delegation-contract
description: Brief and receive work from subagents so intent survives the handoff. Use when delegating multi-phase work, spawning subagents or parallel workers, writing a Task or Agent prompt, fanning out research, or deciding whether to delegate at all. Covers what a spawn prompt must carry, what a worker must return, and which work must stay single-threaded.
---

# Delegation Contract

Use this when work is about to cross an agent boundary — you are writing a spawn prompt, fanning out parallel workers, or deciding whether to delegate at all.

Do not use it for a single-file edit you can finish yourself, or for a sub-minute lookup (one grep, one read, one fetch). Those are tool calls, not delegations.

## First principle

**You are briefing an agent, not calling a function.** A subagent begins with a fresh, isolated context window — no conversation history, no files you read, no earlier tool results. Your prompt is its *entire* briefing, and it will reason and choose rather than execute.

The test for any spawn prompt: **if this worker makes a reasonable decision you did not anticipate, does it have what it needs to make a good one?**

## Rules

1. **Decide the shape before the prompt.** Reads may fan out freely; **writes stay single-threaded**. Parallel writers are blind to each other's intermediate decisions and reconcile only at merge. See `references/orchestration-shape.md`.
2. **Write the ledger before delegating.** Every requirement, constraint, and edge case as one `- [ ] N. <item>` line in `./.workflow/LEDGER.md`, ending with `- [ ] V. fresh-eyes verification passed`. Files survive compaction; conversation context does not. See `templates/ledger.md`.
3. **Every substantive spawn carries all seven fields.** Objective, ledger items *with the why*, non-inferable context, where to look and what to skip, out of scope, expected output, and authority. See `references/send-contract.md`.
4. **Every worker returns the five parts, capped.** Ledger items addressed by number, summary, verbatim evidence (>10 lines to disk plus path), confidence, and what it noticed out of scope. A violating return is re-run, not silently accepted. See `references/return-contract.md`.
5. **Batch before you multiply.** Every spawn pays fixed overhead. Five greps are one worker with a checklist, not five workers.
6. **Verify with fresh eyes.** The verifier did not build the work. It receives the request, the ledger path, and the work-product paths — and only it closes `V.`. Cap at 3 verify→fix cycles, then stop and report open items.
7. **Ambiguity goes to the user, not into a guess.** A requirement you cannot resolve is not a requirement you get to invent.

## What this does not fix

A briefing is written at t=0. It cannot transfer decisions a sibling worker makes at t>0. Roughly a third of observed multi-agent failures are inter-agent misalignment, which no prompt reaches — that is why rule 1 is a structural rule and comes first.

## References

- `references/send-contract.md` — the seven fields, with a worked example
- `references/return-contract.md` — the five-part return and its cap
- `references/orchestration-shape.md` — when to delegate, batching, single-threaded writes, research fan-out, verification

## Templates

- `templates/ledger.md`
- `templates/spawn-prompt.md`
