# Worked example: ProjectBroadside

The portable core in `../SKILL.md` was distilled from one concrete system. This appendix preserves
the **Broadside-specific detail as the evidence base** — deliberately not stripped, so a grader can
see the reusable rules were abstracted from real particulars rather than invented. Paths, doc names,
and server topology below are **Broadside's**, not portable claims; treat them as "here is exactly
what the rule looked like in situ." The Broadside `docs/` paths named here live in that repo, not in
frozenSkillz.

## The system

Unity `6000.6.0b4`, HDRP `17.6.0`. A deterministic 20 Hz simulation owns combat truth; all
presentation (water, cameras, VFX) is expressive but non-authoritative. The skill served an
**art-director loop** for ocean rendering (`docs/plans/crest-art-director-loop.md`): perception →
hypothesis → parameter change → recapture → observation, with vision subagents grading captures
against art-direction briefs.

## The four burns, in Broadside terms

1. **The Editor is a locked, single-owner resource.** Before any Editor mutation or repo write, read
   `.codex/editor.lock` — JSON `{owner, operation, jobId, acquiredAtUtc, expiresAtUtc}`. Unexpired and
   not yours → don't mutate. Past `expiresAtUtc` → stale, deletable. Lock mechanics are canonical in
   **AGENTS.md § "Write freeze during Unity jobs"**. Mechanically enforced by the PreToolUse hook
   (`.claude/hooks/unity_lock_guard.py`, wired in `.claude/settings.json`) — the same guard shipped in
   this skill's `hooks/`.
2. **Screenshot tools default-write into `Assets/Screenshots` — which is tracked.** Always pass
   `output_folder` to `manage_camera screenshot`. Curated evidence → `docs/evidence/watereval/`
   (tracked); scratch → `Captures/watereval/<run>/` (gitignored); never `Assets/`.
3. **Domain reloads drop the MCP bridge** — on play-mode transitions AND recompiles (`refresh_unity`
   triggers one). Retry once, then verify state (`Application.isPlaying`, or `editor/state` →
   `data.advice.ready_for_tools`).
4. **Return numbers, not pixels.** Three RGB triplets settled the midday/dusk bug that screenshots
   plus a vision model would have cost ~100× the tokens to settle.

## Server topology (single-mutating-controller)

Per `docs/UNITY_MCP_SERVERS.md`: **CoplayDev `unityMCP` (pinned `mcpforunityserver==10.1.0`,
project-scoped) is the SOLE mutating controller.** Never mutate through `aura-unity` while unityMCP is
operational — including its animator/input-asset/GameObject authoring tools; route such mutations
through unityMCP's `execute_code` or `manage_*` suite instead. `aura-unity` is for its read-only
uniques: performance triage (`get_worst_cpu_frames`, `get_worst_gc_frames`), quick-look inline
captures (`capture_scene_object`, `capture_editor_screenshot` — return inline images, write no files,
unusable as durable evidence), and inventory (`list_objects_with_high_polygon_count`,
`list_all_prefabs_with_bounding_boxes`). Repo files on disk are edited with Claude Code's own
Read/Edit/Grep — never either server's file tools.

## The resource inventory (Lesson 5, in situ)

Enumerated live (commit `4d99ad2`): **18 unityMCP resources; aura-unity exposes none.** URIs are exact
(read `resources/list`; `editor_state` lives at `mcpforunity://editor/state`, payloads wrap under
`data.*`). High-value ones: `editor/state` (readiness), `instances`, `scene/volumes` (profiles +
which params are overridden + asset paths — override *values* still need code), `scene/cameras`,
`editor/windows` (does a Game View exist to present frames — capture triage), `tests`, `menu-items`,
`rendering/stats`. `scene/volumes` half-covered volume introspection the agent had hand-written via
`execute_code` before enumerating.

## The capture bug (Lesson 3, in situ)

**Status as of authoring:** `WaterEvalCapture.RenderToPng` still uses presented-frame capture
(`ScreenCapture.CaptureScreenshotAsTexture`) — the diagnosed root cause of the midday-label bug
(`docs/evidence/watereval/artlog.md` Entry 1). The fix (fixed-EV manual RT render + in-engine
validation) is **speced but not yet implemented** (Phase B of `docs/plans/crest-art-director-loop.md`).
Discriminating measurement: sun-band mean RGB at 58° = (0.066, 0.109, 0.155) blue/midday vs at 5° =
(0.102, 0.121, 0.083) warm/dusk — the renderer was innocent; the capture path was stale. Exposure is
`AutomaticHistogram` (limits 2–14 EV) — the adaptation dependency that motivated presented-frame
capture and that the fixed-EV fix must override per condition (midday ≈ 13–14 EV, dusk ≈ 8–9 EV).

## The sibling skill (Lesson 8)

The deeper ops truth lives in **`.codex/skills/unity-editor-ops/SKILL.md`** — test-run *result truth*
(MCP job status advisory, Test Runner XML is truth; a run reported failed by MCP passed in 89 s),
batch-vs-GUI crash recipes (GUI HDRP scene loads crash the 6000.6 beta 3/3; batch runs green;
`-batchmode … -runTests -testPlatform PlayMode -testResults <abs>.xml`), watcher requirements
(cover process death, not just outputs), crash-evidence harvesting *before* recovery
(`%LOCALAPPDATA%\Temp\Unity\Editor\Crashes\`, relaunch rotates `Editor.log`), HDRP asset persistence
(add volume components to the *serialized* profile asset, verify non-null), and the git checkpoint
flow (save Project first; explicit staging with `.meta` pairs; never `git add -A`). The Unity skill
**cross-links** this rather than restating it.

## Quick reference — Broadside stable locations (read live values live)

| Thing | Where |
|---|---|
| Battle scene | `Assets/Broadside/Scenes/Stage1/BattleSandbox.unity` — **generated**; never hand-edit or reference scene-local YAML file IDs |
| Sky/exposure/water volumes | read `mcpforunity://scene/volumes` (profile asset paths included) |
| Cameras | read `mcpforunity://scene/cameras` |
| Watereval harness | `Assets/Broadside/Editor/Evaluation/WaterEval*.cs` |
| Capture output / curated evidence | `Captures/watereval/<run>/` (gitignored) / `docs/evidence/watereval/` (tracked) |
| Loop plan · prompts · evidence log | `docs/plans/crest-art-director-loop.md` · `docs/design/vision-prompt-protocol.md` · `docs/evidence/watereval/artlog.md` |
| Framing prior-art | `docs/research/camera-judgment-prior-art.md` |
| MCP topology + tool groups | `docs/UNITY_MCP_SERVERS.md` |
| Deep ops (tests/crashes/commits/locks) | `.codex/skills/unity-editor-ops/SKILL.md` + AGENTS.md § write freeze |

## Generalization call (recorded for the grader)

This skill was ingested as a **project-scoped candidate presented as portable-core + worked-example**,
not silently genericized. The transferable rules (harness-testing discipline, single-mutating-controller
+ mechanical lock, telemetry-over-pixels, resource-first ladder, the framing contract, the vision-prompt
standard, model-tier discipline, orchestrator-looks-too, discover-siblings) are lifted to
engine/Unity-MCP-general phrasing in `../SKILL.md`. The Broadside specifics above are preserved as
evidence. The one code change on intake — two env-var overrides on the lock hook, defaults reproducing
Broadside's behavior — was re-tested (see the lessons doc's intake note). What is **not** yet proven is
portability itself: every rule here is validated *in Broadside*; whether it transfers to another Unity
project or another engine is exactly what the corpus grading should evaluate.
