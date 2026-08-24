# Return Contract — what a worker owes back

The send contract's mirror. Adapted from the pattern in `Rylaa/fable5-opus5-orchestrator`, whose return side was rigorous and worth keeping.

State this contract in the spawn prompt by reference; do not restate it inline every time.

## The five parts

Every substantive worker returns:

1. **Ledger items addressed, by number.** Which of the cited items this work covers, and their state. An item you could not address is reported, not silently dropped.
2. **Summary.** What was done and what it means for the next decision.
3. **Verbatim evidence the conclusion depends on** — code, config, errors, quotes. **At most 10 lines inline.** Anything longer goes to `./.workflow/scratch/` and the report carries the path.
4. **Confidence.** Either `confident` or `uncertain because X`. Uncertainty is a valid deliverable, not a failure to report. A worker that never reports doubt is guessing quietly.
5. **Out of scope but noticed.** Things seen that were not this worker's job. This is how adjacent problems surface without anyone acting on them unilaterally.

## The cap

**40 lines total.** A return that violates the contract is rejected and re-run — never silently accepted. Accepting a bad return once teaches that the contract is decorative.

The cap exists because the orchestrator's context is the scarce resource. Bulk belongs on disk; the orchestrator reads briefs and paths, not dumps.

## Why the cap is not a length rule in disguise

The send side is deliberately *not* length-gated; this side is. That asymmetry is intentional:

- **Outbound**, more context is usually better — the worker starts empty and cannot ask about what it cannot see.
- **Inbound**, more context is usually worse — the orchestrator already holds the plan, and every line of dump displaces reasoning capacity it needs for the next decision.

Compressing on the way back is the worker's job precisely because it just read the material and knows what mattered.

## Verification returns

A verifier's return is the same five parts, with two additions:

- It states, item by item, what is **missing, wrong, or unaddressed** — that is its only job.
- It is the sole closer of `- [ ] V.`. No builder closes its own verification.

Findings become new phases. Re-verify after fixes. **Cap at 3 verify→fix cycles**, then stop and report the open items to the user rather than looping.
