* **Yes. The practitioner discussions materially change the prompts.** My previous versions were too “evaluation-framework” shaped and not sufficiently grounded in what operators actually notice in ugly sessions.
* The strongest recurring pattern is: **first extract observable behavioral signals from the raw trace, then ask an LLM to explain them.** Do not ask the model to free-form “analyze agent performance” from the outset.
* For your use case, I’d make the repo prompt much more like a **forensic workflow-friction miner**, and the corpus prompt much more like a **behavioral log miner**.

I reviewed recent 2026 discussions from **r/ClaudeCode / r/ClaudeAI, Hacker News, GitHub issues, and small tools people built specifically because their agents were pissing them off**. Vendor material was secondary.

### What people are actually looking for

The most concrete practitioner-built detector I found is **Squawk**. Its author wasn't grading reasoning quality; he was detecting behaviors you can actually measure across events: **same failing command again, identical edits, edit/revert oscillation, editing tests without reading implementation, weakening assertions/error handling**. The key insight is that these are *cross-event patterns*—one tool call looks fine; four together reveal the failure. ([Hacker News][1])

Similarly, an HN commenter looking at Agent Flow said that seeing a file touched **30+ times versus once** immediately exposes retry loops, and specifically wanted **re-read detection** because an agent repeatedly opening the same file is often a strong stuck signal. Agent Flow itself exposes parent/child structure, tool sequences, timing, file attention and replay specifically for this reason. ([Hacker News][2])

**Slagent** independently landed on essentially the same raw ingredients: capture **file edits, commands, test results, and user interventions**, then review the resulting session for **repeated failures, unnecessary retries, and missing project context**. Notably, its output is not just “lesson learned”; it records a proposed target, rationale and confidence. ([Hacker News][3])

And the large 413K-trajectory empirical analysis gives some backing to these operator intuitions: **repeating an identical Bash command early** correlates with failure even when controlling for the underlying task, while **early editing across many files** is another strong negative signal. That doesn't mean those are universally bad; it means they're high-value locations for your analyzer to inspect. ([Hanchen Li / Home][4])

### The big thing I would add to your prompts

**Explicitly separate mechanical extraction from causal interpretation.**

Your repo analyzer should start by producing something like:

```text
SESSION MECHANICS

Exact commands repeated:
  7x  npx tsx db/hangar/find.ts battery
  3x  rg "battery" src/

Same failure output repeated:
  4x <signature>

Files repeatedly read:
  AGENTS.md       5 reads
  hangar.ts       7 reads
  beast-ops.md    4 reads

Files repeatedly edited:
  power_monitor.py  6 distinct edit cycles

Edit oscillations:
  power_monitor.py threshold:
      9.9 -> 10.5 -> 9.9 -> 10.2

User interventions:
  T=37 "No, that's already in the database"
  T=81 "Why are you assuming that?"
  T=115 "That's not the part I own"

Subagent duplication:
  parent searched battery
  child repeated same search
  second child repeated same search

Instruction encounters:
  AGENTS.md read at T=4
  relevant rule explicitly visible
  violation first occurs at T=37
```

**Then** hand that structured timeline plus the transcript to the reasoning model.

That's much harder for a reviewer model to bullshit its way through.

---

### Another very useful distinction from actual failures

You absolutely want:

**RULE MISSING** versus **RULE PRESENT BUT NOT APPLIED**.

There's a particularly useful Claude Code issue from an operator who kept a **19-incident violation archive**. Agents read it, acknowledged it, and still repeated documented failures: guessing executable paths instead of running `which`, skipping an explicitly required tracking step even after a startup hook reminded them, and implementing a feature without wiring the integration required to activate it. ([GitHub][5])

That's extraordinarily relevant to you.

So your prompt should ask:

```text
For every user correction:

1. Was there already an instruction addressing this?
2. Had the agent actually encountered/read that instruction before the failure?
3. Was there an existing command/tool that would have resolved the uncertainty?
4. Had the agent previously used that tool successfully?
5. What happened between seeing the rule and violating it?
```

That is much better than:

> "What should we add to AGENTS.md?"

Because your example already screams **the rule exists**.

---

### User corrections should be treated almost like labels

Practitioner self-improvement approaches repeatedly use the human's corrections as particularly strong evidence. Slagent explicitly records user interventions. The community `reflection.md` prompt asks for direct user quotes and misunderstandings, although I think that particular prompt goes too far toward dumping everything into `CLAUDE.md`. ([Hacker News][3])

So I'd add a dedicated extraction pass:

```text
Find every point where the user:

- says no
- contradicts a claim
- says something was already known/documented
- repeats a previous instruction
- asks why the agent did something
- stops/cancels an approach
- redirects to a tool/source
- supplies information the agent should have retrieved
- expresses surprise that the agent does not know something
```

Then look **10–20 events backward** from each intervention.

That's probably one of your highest-value heuristics because your sessions have unusually rich explicit feedback.

---

### Also detect **same result**, not merely same command

People keep mentioning loops where commands aren't byte-for-byte identical. OpenClaw users have documented agents repeatedly issuing identical `exec` calls—even **121 repetitions** in one reported case—but more interestingly, the proposed fixes compare both **command and resulting state/output**. ([GitHub][6])

So your analyzer should canonicalize:

```text
pytest foo -q
pytest ./foo -q
pytest foo --quiet
```

into approximately:

```text
RUN_TEST(foo)
```

and separately fingerprint:

```text
FAILED: expected 12, got 0
```

Then distinguish:

```text
same action + same result        = probable loop
same action + changed result     = iteration
different action + same failure  = possibly hypothesis search
different action + new evidence  = healthy investigation
```

That's much more useful than counting commands.

---

## For the **repo-specific** prompt, I'd emphasize these 8 things

1. **User-correction episodes**
2. **Repeated semantic commands**
3. **Repeated failure signatures**
4. **File reread/edit heatmap**
5. **Edit oscillation / revert cycles**
6. **Where repo instructions were actually encountered**
7. **Repeated manually reconstructed workflows**
8. **Source-of-truth collisions**

That last one matters a lot for your repo. Community discussion around agent memory increasingly points out that the problem often becomes **staleness and orientation rather than raw retrieval**: one recent discussion describes switching toward small orientation files and timestamped/append-oriented context because stale shared knowledge gets confidently acted upon. ([Reddit][7])

So I'd explicitly ask your repo analyzer:

> **Which files, names, commands, documents, or data sources repeatedly look authoritative enough to cause premature stopping?**

That's a much sharper question than “where is documentation confusing?”

---

## For the **whole-corpus** prompt, I'd change the emphasis

Don't make the corpus agent read 400 sessions like novels.

Have it first produce aggregates:

```text
CORRECTIONS
"already told you" class          17 episodes / 6 repos
wrong source of truth             12 / 4
unrequested scope expansion        9 / 7
premature claim of absence         7 / 3

LOOPS
same semantic command + result     31
file reread >3 without edit        26
edit/revert/edit                    8
test repeated w/ same failure      19

DELEGATION
child repeats parent research      14
parent ignores child result         6
qualification lost in handoff       4

NAVIGATION
wrong canonical file              15
searching generated/fixture data   8
manual workflow despite helper     11
```

Then **retrieve representative episodes from each cluster** and ask a strong model to analyze those.

This is also where a tool such as **`cass` / coding-agent-search** is interesting rather than just as a viewer: it already normalizes local session history across Codex, Claude, Cursor, Gemini, Aider, OpenHands, Hermes, etc. into a common searchable representation and supports agent-facing JSON output. ([GitHub][8])

That is *very* close to the ingestion layer you'd eventually want for your corpus analyzer.

---

## One place I would push back on the community

There's a common pattern of:

> mistake → `/review` → write another CLAUDE.md rule.

Slagent does this, the reflection prompts do this, and Reddit users frequently recommend adding recurring mistakes to memory/instruction files. ([Hacker News][3])

**I don't think that should be the default output of your system.**

Your analyzer should instead classify:

```text
WHAT SHOULD CHANGE?

[ ] nothing — transient/recovered
[ ] code/repo structure
[ ] canonical command/helper
[ ] source-of-truth representation
[ ] search/retrieval
[ ] instruction
[ ] skill
[ ] delegation protocol
[ ] hook/runtime enforcement
[ ] model/harness selection
```

Then require evidence for the selection.

That guards against building a 4,000-line `AGENTS.md` containing the archaeological record of every stupid thing an agent has ever done.

---

### So, yes: I would revise the two prompts

The first versions I gave you had the right **scope**, but after looking at what heavy users actually build, I would make them substantially **less essay-like and more forensic**:

**raw event extraction → correction-centered windows → behavioral clustering → causal analysis → repo/harness intervention.**

And for the cross-corpus one:

**normalize events → compute mechanical patterns → sample representative traces → qualitative causal review → distinguish global vs repo-local fixes.**

That combination is much closer to what the practitioners building Squawk, Slagent, Agent Flow, `cass`, and their own transcript analyzers are converging on than the polished vendor “trace grading” material. ([Hacker News][1])

If you want, the next useful step is for me to **rewrite those two prompts around these practitioner-derived mechanics**, rather than merely bolt more sections onto the versions above.

[1]: https://news.ycombinator.com/item?id=47275717&utm_source=chatgpt.com "Show HN: Squawk – Detect and stop behavioral anti-patterns in AI coding agents | Hacker News"
[2]: https://news.ycombinator.com/item?id=47528814 "Show HN: Agent Flow: A beautiful way to visualize Claude Code actions | Hacker News"
[3]: https://news.ycombinator.com/item?id=47051517 "Slagent – a self-learning tool for AI coding agents (Claude Code, Codex) | Hacker News"
[4]: https://hanchenli.github.io/blog/posts/swe_hypo_blog/?utm_source=chatgpt.com "We Analyzed 413K AI Agent Runs. Here's What Separates the Ones That Succeed. | Hanchen's Space Bar"
[5]: https://github.com/anthropics/claude-code/issues/51735?utm_source=chatgpt.com "Agents repeat identical mistakes across sessions — no cross-session behavioral learning · Issue #51735 · anthropics/claude-code · GitHub"
[6]: https://github.com/openclaw/openclaw/issues/34574?utm_source=chatgpt.com "loopDetection does not catch repeated exec tool calls · Issue #34574 · openclaw/openclaw · GitHub"
[7]: https://es.reddit.com/r/ClaudeAI/comments/1u6w88p/how_are_people_handling_claude_memory_with_mcp/?utm_source=chatgpt.com "How are people handling Claude memory with MCP? : ClaudeAI"
[8]: https://github.com/Dicklesworthstone/coding_agent_session_search "GitHub - Dicklesworthstone/coding_agent_session_search: Unified TUI and CLI to index and search your local coding agent session history across 11+ providers (Codex, Claude, Gemini, Cursor, Aider, etc.) · GitHub"
