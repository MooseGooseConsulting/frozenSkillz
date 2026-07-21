---
name: unity-editor-mcp
description: >-
  Drive a live Unity Editor over MCP (unityMCP / aura-unity) safely and reproducibly:
  serialize Editor mutation behind a lock, prefer resources/dedicated tools over ad-hoc
  execute_code, capture evidence that is fresh and correctly framed, and dispatch vision
  subagents that can decline bad frames. Use before any Unity Editor MCP work — scene
  mutation, captures for visual QA, test runs, or driving an art/rendering loop. NOT for
  editing Unity C# on disk (use normal file tools) or for pure in-repo asset math.
metadata:
  author: distilled by an authoring agent from the ProjectBroadside "unity" skill
  version: "0.1.0"
  provenance: _incubator/frozen-skills/skills/unity-editor-mcp/references/lessons-behind-the-skill.md
---

# Unity Editor over MCP — portable core

Reusable rules for any agent driving a live Unity Editor through an MCP bridge (CoplayDev
`unityMCP`, `aura-unity`, or a similar server), especially when the Editor is a shared
resource and captures feed a vision-model QA loop. Every rule below was earned by a real
failure and is documented in **`references/lessons-behind-the-skill.md`** (the provenance
doc — read it to understand *why* each rule exists). The concrete system it was distilled
from is preserved in **`references/worked-example-broadside.md`** (an HDRP naval game); that
appendix is the evidence base, not a dependency.

> **The spine — test every harness, never assert it.** A capture rig, a lock hook, a vision
> prompt, and the skill itself are all *harnesses*. The single highest-value discipline in
> this skill is: **empirically run each one before trusting it.** In the session that produced
> this skill, every claim that skipped testing turned out wrong (three of them are catalogued
> in the lessons doc). "It should work" is not a result; a run is.

## 1. The Editor is a single-owner, mutating resource — serialize it, and enforce it

Scene mutation, compilation, scene regeneration, asset writes, and test runs share **one live
Editor**. Fan out read-only work freely; **never fan out Editor mutation**.

- Adopt a lock convention: a small JSON file (`{owner, operation, jobId, acquiredAtUtc,
  expiresAtUtc}`). Before any mutation or repo write, read it. Unexpired and not yours → wait
  or coordinate. Past expiry → stale, deletable. Doing a mutation yourself → write your own
  lock, delete it when done.
- **Etiquette is not enough — enforce mechanically.** Convention alone was violated in
  practice. A `PreToolUse` hook that reads the lock and blocks foreign-held mutations is
  shipped here: `hooks/unity_lock_guard.py`, wired via `hooks/settings.snippet.json`. It lets
  read-only Unity tools through and blocks mutations while a live, unexpired, foreign lock
  exists. The hook itself was tested against four cases (foreign-live / stale / read-only /
  absent) — see the lessons doc. The hook covers one agent client only; still check the file
  when work spans other agents.

## 2. One server mutates; the others are read-only auxiliaries

If two MCP servers can both mutate the Editor, pick **one sole mutating controller** and route
every mutation through it. Never mutate through the secondary server while the primary is
operational — even for authoring tools it happens to expose. Use the secondary only for its
read-only uniques (perf triage, quick-look inline captures, inventory). Edit C# on disk with
your own file tools, never either server's file tools.

## 3. Tool preference ladder — resources and dedicated tools before `execute_code`

Ad-hoc code is the *last* resort, not the reflex. Ladder:

1. **Resource read** for state queries. URIs are exact — read them from `resources/list`, never
   derive a URI by swapping separators in a resource's *name* (names use `_`, URIs use `/`).
   Payloads wrap under `data.*`. Enumerate what exists before hand-writing code: a session here
   defaulted straight to `execute_code` C# and had never listed the ~18 resources sitting right
   there — one of which half-covered the exact scene introspection it had written by hand.
2. **Dedicated tool** — legible in the permission UI, no compiler dependency.
3. **`execute_code`** only for compound (read-modify-measure in one tick) or genuinely
   uncovered operations. If the server compiles via CodeDom, assume **C# 6** — no local
   functions, pattern matching, out-vars, or tuples (a silent Roslyn→CodeDom fallback surfaces
   as C#6 syntax errors, not fallback warnings). Leave the scene clean and *prove it* (return
   `scene.isDirty` after any mutating diagnostic); keep calls idempotent — the bridge can drop
   mid-sequence.

## 4. Concrete MCP burns (Unity-general, verify against your server)

- **Deferred tools must be batch-loaded before use** — load everything you'll need in ONE
  selection call, not one call per tool.
- **Domain reloads drop the bridge** — on play-mode transitions *and* on script recompiles (a
  refresh triggers one too). "Could not connect" right after either is expected turbulence:
  retry once, then **verify state** (`isPlaying`, editor-ready flag) instead of assuming your
  last call landed.
- **Screenshot tools default-write into a tracked project folder** (e.g. `Assets/Screenshots`).
  Always pass an explicit output folder to captures; never let evidence land in a tracked path.
- **"Tool not found" may mean an inactive tool group, not wrong routing.** Servers activate
  groups (testing, profiling, ui, vfx, …) on demand — check the tool-groups resource and
  activate before concluding a tool is missing.

## 5. Capture: fresh, correctly framed, validated *before* anyone grades it

- **Return numbers, not pixels.** Compute statistics in-engine (band-mean RGB, coverage %, luma
  percentiles) and return short strings. In the source session, **three RGB triplets settled a
  rendering bug that screenshots plus a vision model would have cost ~100× the tokens to settle.**
- **Presented-frame capture is a trap headless.** APIs that photograph the last *presented*
  frame (`ScreenCapture.CaptureScreenshotAsTexture`, no-camera screenshots) return null with no
  presentation, capture whatever camera the game presents, and carry **stale lighting** when
  presentation lags a scene change. That last mode is exactly how "midday-labeled frames contain
  dusk pixels" happens — and it was proven to be the capture path, not the renderer, by
  in-engine measurement, not by eyeballing (lessons doc, Lesson 3).
- **Direct-render** (camera specified → RT) is fresh and correctly aimed but bypasses adapted
  auto-exposure. The correct pattern: override Exposure to **Fixed** for the capture, render to
  RT, restore, then **validate the written frame** (sample it; recapture-once-then-fail on
  mismatch). Read live exposure/volume settings live — never trust remembered values.
- **Framing contract (novel; the strongest defense).** Prove framing *engine-side before any
  vision model looks*: subject in-frustum (`TestPlanesAABB`), in front of camera, on-screen
  containment, a coverage floor (bbox ≥ a few % of frame), and — because occlusion is the one
  thing geometry misses — a mask-pixel visibility check. A VLM must **never** be the thing that
  discovers the camera wasn't aimed at the subject; the literature is consistently negative on
  VLMs self-detecting small/occluded/absent subjects. See `references/framing-and-vision.md`.

## 6. Dispatching vision subagents — let them decline, and look yourself

- **No bare closed questions.** A caged closed question on an inadequate frame yields a confident
  *wrong* answer, not a complaint (real case: "is there any foam?" → "no", on a frame shot from
  ~10,000 ft where foam cannot resolve). Every delegated vision prompt carries the **epistemic
  escape hatch** verbatim, before the task questions:

  > Before answering: do you have enough information to answer this reliably? Is anything about
  > the image preventing you — subject too small or too distant, frame too dark, wrong vantage,
  > occlusion, artifacts? If so, say that INSTEAD of answering the question.

  And order questions **open-before-closed**: "describe what you actually see" precedes any
  specific cue question.
- **The orchestrator looks too.** Read at least one image (or source doc) per delegated batch.
  Delegation failures — wrong file passed, wrong altitude, stale/broken frame, prompt
  misunderstood — are invisible in a subagent's text summary and obvious in one direct look.
- **Model-tier discipline.** Use a cheap/mechanical tier (e.g. `sonnet`) for perception/grading,
  a strong tier for judgment/research/adversarial review. **Never omit the model by accident** —
  subagents silently inherit the top session tier (one early batch did this and burned ~325k
  top-tier tokens). Re-validate any grading model on a known-ground-truth battery before trusting
  it. Full prompt standards and the battery pattern: `references/framing-and-vision.md`.

## 7. Author against what already exists — discover siblings first

Before writing an Editor skill, search the repo for one that already exists. The source session
wrote a Unity skill without finding the pre-existing ops skill holding the repo's richest Editor
knowledge (test-run truth, crash-evidence harvesting, HDRP persistence, checkpoint mechanics).
Cross-link the deeper skill; do not duplicate it. Likewise, run any script a skill references
before claiming it works — existence ≠ correctness.

## 8. Session rituals

- **Start:** batch-load deferred tools; read the editor-state resource to confirm the bridge is
  up and ready (in a subagent, resource-reading tools may be absent — fall back to dedicated
  status tools); pin the instance if several are connected; check the lock.
- **Tests / crashes / commits:** treat MCP job status as advisory — the Test Runner XML is truth.
  Run heavy PlayMode suites in **batch mode**, not the GUI, if GUI scene loads crash. Harvest
  crash evidence *before* any recovery (relaunch rotates logs). Checkpoint with explicit staging
  and `.meta` pairs; never `git add -A`. Depth lives in the sibling ops skill (worked example).
- **End:** stop play mode → scene not dirty (or intentionally saved) → console clean → your lock
  deleted → evidence committed (an end-of-run audit must replay the session from git alone).

## References

- `references/lessons-behind-the-skill.md` — the faithful provenance: the spine, the 13 lessons,
  and the three assertion-vs-evidence failures that testing caught (including where the authoring
  agent was wrong and retracted).
- `references/framing-and-vision.md` — the engine-side framing contract, the vision-prompt design
  rules with sources, and the R1–R5 regression battery.
- `references/worked-example-broadside.md` — the original Broadside-specific skill preserved as
  evidence (BattleSandbox, the watereval harness, `.codex/editor.lock`, the sibling
  `unity-editor-ops` skill, exact server topology).
- `hooks/unity_lock_guard.py` + `hooks/settings.snippet.json` — the enforcement mechanism.
