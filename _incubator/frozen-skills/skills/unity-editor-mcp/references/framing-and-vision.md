# Framing contract + vision-prompt standard

Portable distillation of two ProjectBroadside research artifacts:
`docs/research/camera-judgment-prior-art.md` (framing contract, prior-art survey) and
`docs/design/vision-prompt-protocol.md` (prompt design rules + regression battery). Cited, not
copied — read the originals in the worked example for the full source list.

## Why this exists

The division of labor for any engine → vision-model QA loop is: **the engine proves
presence / size / occlusion / framing; the VLM judges aesthetics / semantics — only on frames the
engine has already certified.** This is forced by evidence that VLMs cannot self-detect bad framing:

- "Vision Language Models Are Blind" (arXiv 2407.06581, directly verified in the source survey): VLMs
  fail overlap / touching / occlusion / counting tasks trivial for humans; fine detail reads
  "blurry." Localization degrades **as the target gets smaller** — worst exactly where "subject too
  small / cut off / occluded" lives.
- VLM-judge studies report an **assert-correct bias**: models affirm regardless of visual evidence,
  amplified by leading/closed questions.
- **Absence-of-prior-art finding:** Unity MCP agent loops (IvanMurzak/Unity-MCP, Unity's official
  MCP, agent-bridge-for-unity) offer captures and even image diffing, but **none gate on
  frustum/coverage/occlusion before trusting a screenshot.** Budget to build, not adopt.

## The framing contract (minimal gate before any VLM grade)

Per tagged subject, computed engine-side per capture, logged as telemetry; a frame is **ineligible
for grading unless all hard checks pass:**

1. **In-frustum** (`GeometryUtility.CalculateFrustumPlanes` + `TestPlanesAABB`) — else subject absent.
2. **In front of camera** (projected corners z > 0) — else behind camera.
3. **On-screen containment** (≥ ~90% of projected bbox inside [0,1]²) — else cut off.
4. **Coverage floor** (bbox area ≥ ~3–8% of frame, tuned per shot intent) — else too small.
   *The "foam at 10,000 ft" failure is this check.*
5. **Coverage ceiling** (≤ ~80%, optional) — else too close.
6. **True visibility** (mask-pixel visible / total ≥ ~60%) — else occluded. The only cheap check that
   catches occlusion by waves / other objects; geometry alone misses it.
7. **Centering** (soft warn): bbox centroid within a dead-zone of frame center.
8. **Resolution / exposure sanity**: computed at capture resolution; confirm exposure is adapted /
   fixed, not the stale one-shot (pairs with the fixed-EV capture fix).

Verification techniques ranked by evidence-per-cost: (1) frustum AABB test (~5 lines, no render);
(2) 8-corner viewport projection — the single most useful cheap signal, catches *tiny* and *cut off*;
(3) ID-mask pixel count — the only cheap proof of occlusion; (4) Unity Perception Occlusion Labeler —
highest rigor, heaviest integration, #3 gets ~80% of it; (5) occlusion raycasts — noisy tie-breaker
only. Practical stack: **1+2 always-on; add 3 wherever occlusion is a live risk.**

## Vision-prompt design rules (each traced to a source in the original)

1. **Neutral, non-presupposing questions.** Never "describe the glitter lane" (presupposes one) —
   ask "what do you see," then compare to the brief. Leading tone measurably increases fabrication.
2. **Describe before judging.** Perception questions precede preference/gap questions — the standard
   chain-of-thought hallucination mitigation.
3. **Pairwise comparisons run in BOTH orders, in separate fresh contexts.** LLM judges show strong
   position bias; a verdict counts only if both orderings agree, else it's a **tie** (never
   rerun-until-it-agrees).
4. **Detail is not quality.** State explicitly that judgment is against the brief's cues, not
   richness — verbosity bias makes judges read length as quality.
5. **No provenance leakage.** The blind checker never learns which frame is newer or preferred;
   frames are "A"/"B", randomized per run.
6. **Images before text, labeled** (`Image A:` / `Image B:`), one image immediately before the
   questions that reference it.
7. **Report everything, filter downstream.** "Only mention major issues" suppresses recall — ask for
   every visible fact with confidence noted.
8. **De-prescribe.** Give a mission + constraints, not a step-by-step procedure, on frontier models.
9. **Respect the image-quality floor.** Never grade a visibly broken frame (blur, <200px features,
   recompression) — recapture. Capture native-resolution PNG.
10. **Every prompt carries the epistemic escape hatch, and no bare closed questions** (the headline
    rule — see Lesson 10 in the lessons doc):

    > Before answering: do you have enough information to answer this reliably? Is anything about the
    > image preventing you — subject too small or too distant, frame too dark, wrong vantage,
    > occlusion, artifacts? If so, say that INSTEAD of answering the question.

    Closed cue questions may only follow an open describe-what-you-see question.

## The R1–R5 regression battery (test prompts like code)

Prompts are **versioned, reviewed, and regression-tested against known-ground-truth frames** in
**fresh contexts** (a session that already knows the system's bugs is a contaminated test subject). A
failed test blocks the version; the fix is a **new version with a changelog line, not a rerun**.

| ID | Tests | Pass condition |
|---|---|---|
| R1 | label-vs-pixels | Grader reports the true lighting unprompted, contradicting a lying label |
| R2 | artifact spotting | Grader flags a debug/overlay artifact unprompted |
| R3 | pairwise, order 1 | Prefers the known-better frame, citing pixel evidence |
| R4 | pairwise, order 2 (swapped) | **Same** winner — verdict survives the order flip |
| R5 | identical-pair | Declares a tie without inventing a difference — **use two distinct paths to identical pixels** (see Lesson 2c) |

Standing rules proven in the source run: run the battery on **any new grading model before trusting
it** (Sonnet was validated separately from Fable 5); and before any run, **confirm the memory/context
index does not name the fixtures' ground truth**, or the affected test is void (the blinding caveat).
