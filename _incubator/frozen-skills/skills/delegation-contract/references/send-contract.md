# Send Contract — the seven fields

What the orchestrator owes a worker. Every substantive spawn carries all seven, not as a form but because each closes a specific gap created by the context boundary.

Exempt: sub-minute lookups (one grep, one read, one fetch). Nothing is being judged, so nothing needs briefing.

## Why seven, and not "write a good prompt"

Each field exists because of something an agent does that a function does not:

| The agent... | So you must supply |
|---|---|
| adapts when reality contradicts your plan — if it knows why | **2 · the why** |
| meets situations you did not foresee | **7 · authority** |
| cannot ask about what it cannot see | **3 · non-inferable context** |
| expands into any space left unbounded | **5 · out of scope** |
| judges relevance against a goal it must know | **1 · objective + downstream use** |
| pays rediscovery cost you already paid | **4 · where to look / what to skip** |
| writes a status update if unsure of its audience | **6 · output + size bound** |

## The fields

**1 · Objective, and what you'll do with the result.** The finished state, not the activity. *"Auth middleware rejects expired tokens with 401 and a structured body"* — not *"look at the auth middleware."* A worker that cannot tell when it is done will stop early or never stop.

State the downstream use: *"find where auth is implemented; I need the pattern to add OAuth"* beats *"search for auth files."* Knowing what the answer feeds is what lets it judge relevance — a judgment you cannot pre-encode as a step.

**2 · Ledger items, with the why.** Cite the item numbers this worker owns *and* restate the reasoning. Ledger lines are one-line checkboxes: they carry the WHAT and almost never the WHY. The item says "reject expired tokens." The why — *"a prior incident let 30-day-stale tokens through and we chose explicit rejection over silent refresh"* — is what stops the worker solving it the wrong way.

**This is the field most often dropped and the one that most often causes rework.**

**3 · Context the worker cannot infer.** Anything decided in conversation, rejected earlier, or true-but-unwritten. Constraints whose reasons are not visible in the code. Approaches already tried and abandoned. Absence is invisible: nothing in the repo hints that a decision was ever made, so the worker will never think to ask.

**4 · Where to look — and what to skip.** Concrete entry points: paths, symbols, commands, the ledger path, prior work-product paths. Not *"the auth code"* but `src/middleware/auth.ts`.

Name the dead ends too — the source that looks authoritative and is stale, the tool that will time out, the vendored directory. Steering away costs the same as steering toward.

**5 · Out of scope.** What NOT to touch: adjacent code that looks broken but is deliberate, refactors belonging to another phase, files a parallel worker currently owns. Without this a capable worker helpfully expands until it collides with a sibling or with a decision that was yours.

**6 · Expected output, with a size bound.** What you need to make the next decision — a diff, a brief, a verdict, a path. Point at the return contract rather than restating it.

Bound it: *"return only the failing tests with their error messages"* beats *"report the test run."* Name the consumer, and say it is not addressing the user.

**7 · Authority.** What the worker decides alone versus what it returns for a ruling. *"Pick the error-message wording; do not change the status code without asking."* Silence produces one of two failures: a worker that stalls on trivia, or one that quietly makes a call that was yours.

Give it a rule for the unforeseen, since you cannot enumerate the branches: proceed on judgment, or come back and ask.

## Worked example

> **Objective.** `POST /sessions` rejects expired refresh tokens with 401 and `{error:"token_expired"}`; unexpired behavior unchanged. I need this before wiring the mobile retry path, so the error shape matters more than the internals.
>
> **Ledger items.** Covers 4 and 5. Why: incident 2026-06-11 — stale tokens up to 30 days old were silently refreshed. We chose explicit rejection over silent refresh so clients see the failure and re-auth; silent refresh hid the problem for six weeks.
>
> **Context you can't infer.** We tried a sliding-window refresh in June and reverted it — it made session length unpredictable for the mobile client. Don't reintroduce it. The 30-day figure comes from the incident, not from config.
>
> **Where to look / skip.** `src/middleware/auth.ts` (`verifyRefresh`), tests in `tests/auth/expiry.test.ts`. Ledger at `.workflow/LEDGER.md`. Skip `src/legacy/session_v1.ts` — looks wrong, deliberately frozen.
>
> **Out of scope.** Access-token TTL is phase 3 and another worker holds it. Don't touch it.
>
> **Expected output.** Diff plus the standard return contract, under 40 lines. Note any call site that assumed refresh never fails. Returning to me, not to the user.
>
> **Authority.** Yours: error wording, test structure, where the check sits in the middleware chain. Mine: the status code, the error key, anything touching token TTL. If the fix requires changing a caller's contract, stop and ask.

## On mechanizing this

If a hook ever checks for these fields, check for *content*, not length — and treat it as a floor on effort, not a quality bar. Five empty headings satisfy any regex. It is still worth having, because it is checked when the prompt is written rather than self-marked afterward.

Do not gate on prompt size. Measured default spawn prompts cluster near 1300 characters, and length says nothing about whether the recipient can handle surprise.
