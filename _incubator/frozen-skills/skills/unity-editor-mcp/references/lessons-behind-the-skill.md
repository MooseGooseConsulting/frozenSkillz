# Lessons behind the `unity-editor-mcp` skill

This is the provenance for the `unity-editor-mcp` skill: the reasoning that produced each rule,
faithfully including **the places the authoring agent was wrong and corrected itself.** A frozen
corpus grades effectiveness, and effectiveness is easier to trust when the failures are on the
record. The self-corrections below are the highest-value lessons — read them as the point, not the
footnotes.

## Provenance

- **Source system:** ProjectBroadside — a Unity `6000.6.0b4` / HDRP `17.6.0` naval game. The skill
  was authored in-repo as `.claude/skills/unity/SKILL.md` with a `.claude/hooks/unity_lock_guard.py`
  PreToolUse hook wired in `.claude/settings.json`.
- **Authoring session:** Claude Code, 2026-07-21, `session_01LBEtdNwqYe2bstL1SMTPrq`. The first
  vision batteries ran on **Fable 5** (by accident — see Lesson 9); the grading battery and the
  skill's own review were then rerun deliberately on **Sonnet** and **Opus**.
- **Committed evidence (Broadside git):**
  - `873914d` — first cut of the skill ("dual MCP-server routing"; the burns).
  - `4d99ad2` — "verified resource inventory replaces hand-waved guidance" (Lesson 5).
  - `0193a9c` — "reviewed unity skill, lock enforcement, camera judgment": skill *rewritten from
    dual adversarial review (Sonnet defects + Opus design)*; lock hook tested; framing contract +
    prompt rule 10 added.
  - `d19d993` — the art-director loop plan + vision-prompt protocol + artlog seed.
- **Source documents cited below (Broadside `docs/`):** `evidence/watereval/artlog.md`,
  `design/vision-prompt-protocol.md`, `research/camera-judgment-prior-art.md`,
  `plans/crest-art-director-loop.md`, and the sibling `.codex/skills/unity-editor-ops/SKILL.md`.
- **Honesty note on citations:** where a lesson is documented on disk I cite the file or commit.
  Where a lesson is a conversational self-correction that left no committed artifact (Lesson 7's
  retraction, the exact token figure in Lesson 9, the two-reviewer split beyond commit `0193a9c`'s
  one-line summary), I mark it **[session account]** rather than manufacture a citation. That
  distinction is itself an instance of the spine.

---

## The spine: the top rule with all harnesses is that we have to end up testing them

Everything in this skill is a **harness** — a capture rig, a lock hook, a vision prompt, a skill
document that will steer future agents. The governing discipline is that **each one had to be
empirically run, not asserted.** In this session, every claim that skipped testing turned out
wrong; every claim that was tested either held up or was corrected by the test. Concretely, four
harnesses were run rather than trusted:

1. **The vision-grading battery** (fixtures R1–R5) — run in *fresh contexts* on **both Fable 5 and
   Sonnet**, not assumed to transfer between models (`vision-prompt-protocol.md`, results table).
2. **The lock-guard hook** — executed against foreign-live / stale / read-only / absent inputs
   before being trusted to enforce anything (commit `0193a9c`: "tested: blocks foreign live locks,
   passes stale/readonly/absent"). *(This frozenSkillz copy adds two env-var overrides and was
   re-run against nine cases — see the intake note at the end.)*
3. **The prompt protocol** — treated as versioned code with a regression battery and a change
   process ("new version + rerun battery; never rerun-until-pass"), not as prose to trust once
   written (`vision-prompt-protocol.md`).
4. **The skill itself** — subjected to **two independent adversarial reviews** with different lenses
   before it was considered done (commit `0193a9c`).

Read the spine as the reason the next three lessons exist: they are the cases where an untested
claim was caught *by* running the harness.

---

## The three assertion-vs-evidence failures that testing caught

### 2a. "Sonnet is sufficient for grading" was asserted, then had to be earned by the full battery

The cheaper Sonnet tier being "good enough" for perception/grading was adopted as policy before it
was demonstrated. It was only actually earned by **running the entire R1–R5 battery on Sonnet in
fresh contexts** — all five passed, and Sonnet additionally surfaced defects the Fable runs missed
(an LOD artifact on a hull; a horizon-glow/hull rim-light inconsistency)
(`vision-prompt-protocol.md`, "Model finding + policy" and the results table). The durable rule that
came out of it is explicitly anti-assertion: **"Rerun the battery on any new grading model before
trusting it."** A single easy pass is not a policy; the battery is.

### 2b. The editor-lock was declared "violated" — the claim was false and was retracted

The agent asserted that the `.codex/editor.lock` convention had been **violated**, reasoning from a
reviewer's *later* snapshot that showed a lock present. Checking the **timeline** falsified it: the
lock was **not present during the earlier mutations** it was supposedly protecting, so nothing had
been violated. The claim was **retracted**. The lesson is about evidence order, not locks: a
snapshot taken at time *T₂* says nothing about what was true at *T₁*; asserting a violation from the
wrong timestamp is exactly the kind of untested claim the spine exists to stop. **[session account]
— this retraction was a conversational correction and left no committed artifact; the lock
*mechanism* it concerns is documented in the hook and in the skill's burn #1.** (It also motivates
why enforcement is mechanical now: a hook reading the lock *at mutation time* cannot be fooled by a
later snapshot the way a human narrative can.)

### 2c. The R5 fixture was broken — same file passed twice — and had to be fixed to two distinct paths

R5 tests that a fresh grader, shown two *identical* frames, declares them equal without inventing a
difference. The first R5 attempt was **invalidated by a fixture error: both paths pointed at the
same file**, so the agent deduced identity from the *paths* rather than the pixels — testing
identity-detection-from-filenames, not the intended perceptual tie. It was rerun with **two distinct
paths to identical pixels**; the grader then described both independently and declared a tie with no
invented differences. The fixture definition was corrected permanently: **"always two distinct file
paths"** (`vision-prompt-protocol.md`, "2026-07-21 battery run details" → R5). A test that passes for
the wrong reason is a failed test.

---

## The rest of the lessons

### 3. The capture-path root cause was proven by measurement, not eyeballing

The visible bug was "`midday`-labeled frames contain **dusk** pixels." The tempting culprit was the
renderer or the time-of-day definition. Both were **falsified in-engine**:

- The condition was defined correctly — `WaterEvalConditions.cs:92` sets `calm_midday` sun elevation
  to **58°**, and `WaterEvalHarness.cs:353` applies it (`artlog.md` Entry 0.5).
- The renderer responds to sun elevation correctly — a manual HDRP render at **58°** gives sky-band
  mean RGB **(0.066, 0.109, 0.155)** (blue-dominant, midday); at **5°** it gives **(0.102, 0.121,
  0.083)** (warm/olive, dusk) (`artlog.md` Entry 1, H2 FALSIFIED).

The actual cause: `WaterEvalCapture.RenderToPng` **does not render the passed camera at all** — it
calls `ScreenCapture.CaptureScreenshotAsTexture`, photographing the **Game View's last *presented*
frame** (deliberately, to inherit adapted auto-exposure). Three consequences, all observed live: it
returns **null** with no presentation; it captures whatever camera the game presents; and when the
Game View repaint **lags** a condition change, the PNG carries the **previous** condition's lighting
— a systematic one-condition presentation lag is exactly how every midday tile ends up wearing dusk
pixels (`artlog.md` Entry 1, H3/H4 CONFIRMED). **The fix (fixed-EV manual RT render + in-engine
post-capture validation) is speced, not yet shipped** — `artlog.md` "Fix design" and
`crest-art-director-loop.md` Phase B. The lesson: when a harness produces a suspicious artifact,
*measure the pipeline stage by stage*; the obvious suspect (the renderer) was innocent.

### 4. Telemetry beats screenshots — by roughly two orders of magnitude in tokens

The bug above was settled by a handful of **in-engine RGB measurements** (the skill's phrasing:
"three RGB triplets settled a bug"), not by shipping screenshots to a vision model. The skill
estimates the vision route would have cost **~100×** the tokens (`SKILL.md`, burn #4). Standing rule:
compute statistics in-engine (band-mean RGB, coverage %, luma percentiles) and return short strings;
reserve pixels for the questions only a model can answer.

### 5. Reach for resources and dedicated tools before writing `execute_code`

The agent's reflex was `execute_code` C#. It had **never enumerated the resources sitting right
there.** When it finally did (commit `4d99ad2`): **18 unityMCP resources** exist (aura-unity exposes
none), and **`mcpforunity://scene/volumes` half-covered the exact volume introspection the agent had
already hand-written via `execute_code`**; `editor/windows` exposed the Game-View focus state
relevant to the capture-staleness triage above. The tool preference ladder (resource → dedicated
tool → `execute_code`) is a direct consequence: ad-hoc code is the last resort, and enumerating what
the server already offers is a five-minute step that retires whole classes of hand-written code.

### 6. Concrete Unity-MCP burns, each from a real stumble

From commit `873914d` and the skill body: **deferred tools must be batch-loaded** in one selection
call before use; **domain reloads drop the bridge** on both play-mode transitions *and* recompiles
(a refresh triggers one), so "could not connect" right after is expected — retry once then verify
state; **`execute_code` is CodeDom C# 6** (no local functions / pattern matching / out-vars /
tuples; the Roslyn→CodeDom fallback surfaces as C#6 syntax errors, not warnings); **`manage_camera
screenshot` default-writes into the tracked `Assets/Screenshots`** — always pass an explicit output
folder; and **"tool not found" often means an inactive tool group**, not wrong routing — check the
tool-groups resource and activate before concluding a tool is missing.

### 7. Serialize the one Editor — and enforce it mechanically, because etiquette failed

Scene mutation, compilation, regeneration, asset writes, and test runs share one live Editor and
must be serialized to a single owner (`unity-editor-ops` §1). The convention was a lock file
(`.codex/editor.lock`). **Etiquette alone did not hold** — which is why the lock is now backed by a
`PreToolUse` hook (`unity_lock_guard.py`) that reads the lock *at mutation time* and blocks
foreign-held mutations while passing read-only tools, stale locks, and self-owned locks (commit
`0193a9c`; Lesson 2b explains why *mutation-time* enforcement matters). The hook was tested before it
was trusted — the spine again.

### 8. Discover sibling skills before authoring — cross-link, don't duplicate

The Unity skill was written before the agent found the pre-existing **`.codex/skills/unity-editor-ops`**
skill, which already held the repo's richest Editor knowledge: test-run *result truth* (MCP job
status is advisory, the Test Runner XML is truth — a run reported failed by MCP had actually passed
in 89 s), batch-vs-GUI crash recipes, crash-evidence harvesting *before* recovery, HDRP asset
persistence, and the git checkpoint flow. The corrected skill **cross-links** the sibling for that
depth instead of restating it (`SKILL.md` header + "Tests, crashes, commits" section). Lesson:
search for prior art *inside your own repo* before writing a guide; the best documentation of a
subsystem is often already there under a different name.

### 9. Subagent model-tier discipline — never inherit the top tier by accident

Subagents **silently inherit the session model** when no `model` is set. The first vision battery ran
on **Fable 5 by accident** for exactly this reason (`vision-prompt-protocol.md`, "Model finding +
policy") — **burning ~325k top-tier tokens [session account]** before the tier mistake was noticed.
The policy: `sonnet` (or the cheapest capable tier) for perception/mechanical/grading work; a strong
tier for judgment, research, and adversarial review; inherit the top tier only for genuine frontier
reasoning — and **never omit `model` by accident**.

### 10. The epistemic escape hatch — no bare closed questions

A grader was asked only **"is there any foam on the ocean?"** and answered **"no"** — on a frame shot
from **~10,000 ft** where foam physically cannot resolve. The narrow closed question left it no way
to object; VLM-judge research documents the mechanism (an assert-an-answer bias amplified by closed
questions). The fix is a rule, now `vision-prompt-protocol.md` rule 10 and commit `0193a9c`: **every**
delegated vision prompt opens with the escape hatch — *"do you have enough information to answer this
reliably? … If so, say that INSTEAD of answering"* — and **closed cue questions may only follow an
open "describe what you see."** A caged closed question on an inadequate frame yields a confident
*wrong* answer, not a complaint.

### 11. Prove framing engine-side before any model looks — the novel part

VLMs are **documented as unable to self-detect** small / occluded / absent / mis-framed subjects
(`camera-judgment-prior-art.md`: "Vision Language Models Are Blind", arXiv 2407.06581, directly
verified; localization degrades as the target shrinks — worst exactly where the failure lives). So
subject **presence / coverage / occlusion / framing must be proven in-engine before any grade** — a
"framing contract" of cheap checks (frustum AABB, 8-corner viewport projection for coverage %, an
ID-mask pixel count for true occlusion). The survey's absence-of-prior-art finding: **no existing
Unity MCP / agent loop validates captures before trusting them** — "budget to build, not adopt."
This engine-proves-then-VLM-judges division of labor is the skill's most transferable and most novel
idea. (The "foam at 10,000 ft" case is a *coverage-floor* failure — check #4 in the contract.)

### 12. The orchestrator must look too

Delegation failures — wrong file passed, wrong altitude, a stale or broken frame, a misunderstood
prompt — are **invisible in a subagent's text summary and obvious in one direct look**. Rule
(`SKILL.md`, "Dispatching vision subagents"): the main thread itself **Reads at least one image or
source document per delegated batch** — a spot-check, not a full regrade. Delegation scales the loop
*and* is where it silently fails; the cheap defense is one direct look per round.

### 13. Adversarial *and diverse* review — different lenses catch disjoint defects

The skill was finalized only after **two independent adversarial reviews with different lenses**: one
hunting factual / cold-start defects (**Sonnet**), one judging design (**Opus**) — commit `0193a9c`:
"rewritten from dual adversarial review (Sonnet defects + Opus design)." They caught **disjoint**
problems, and the review also surfaced **the author's own rule violations** (rot-prone live values
that the skill itself told authors to strip). Lesson: a single reviewer, however careful, shares a
lens with the author; two reviewers chosen for *different* lenses find non-overlapping defects, and
one of the most valuable things a review finds is the author breaking their own stated rules.
**[session account for the two-reviewer split beyond the commit's one-line summary.]**

---

## Intake note (this frozenSkillz copy)

Per the spine, the one thing changed on intake was re-tested. `hooks/unity_lock_guard.py` here is the
source hook plus two env-var overrides (`UNITY_LOCK_PATH`, `UNITY_LOCK_SELF_PREFIX`) whose **defaults
reproduce the source's exact behavior** (`.codex/editor.lock`, self-prefix `claude`). It was run
against nine cases — foreign-live/mutate → block(2); foreign-live/read-only (three tools) → pass(0);
stale → pass(0); self-owned → pass(0); absent → pass(0); unreadable → block(2); non-Unity tool
passthrough → pass(0); and the two overrides (re-point self-prefix, re-point lock path) → expected
block/pass. All nine matched. The generalization was adopted only because it was tested, not because
it "should" work.
