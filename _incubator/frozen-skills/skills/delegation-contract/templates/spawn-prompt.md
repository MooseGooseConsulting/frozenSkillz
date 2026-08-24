# Spawn Prompt Template

Fill every field. If one is genuinely empty, say so explicitly — "no prior attempts" is information; a missing heading is not.

```markdown
**Objective.** <finished state, not activity> — and what I'll do with the result:
<downstream use, so you can judge relevance>

**Ledger items.** Covers <numbers>. Why these exist: <the reasoning behind them,
not a restatement of the checkbox text>

**Context you can't infer.** <decided in conversation / tried and abandoned /
true but unwritten / constraints whose reasons aren't in the code>

**Where to look / what to skip.** <paths, symbols, commands, ledger path>
Skip: <stale sources, frozen files, tools that will time out>

**Out of scope.** <what not to touch, and what another worker currently owns>

**Expected output.** <shape> under 40 lines, per the return contract.
Returning to me, not to the user.

**Authority.** Yours: <decide alone>. Mine: <return for a ruling>.
If <condition>, stop and ask rather than guessing.
```

## Self-check before sending

Not "did I fill all seven." Ask:

> **If this worker makes a reasonable decision I did not anticipate, does it have what it needs to make a good one?**

If the answer is no, the missing thing is almost always the *why* (field 2) or the *authority boundary* (field 7). Those are the two that get dropped under time pressure and the two that cause the most rework.
