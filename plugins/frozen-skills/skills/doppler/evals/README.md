# Trigger evals for `doppler`

Labeled prompts live in [`triggers.json`](triggers.json).

## How to run (Cursor)

1. Confirm the skill appears under Customize → Skills / Agent Decides.
2. Explicit smoke: `/doppler` once — proves body quality independent of description.
3. For each query in `train`, then `validation`, open a **fresh** Agent chat (no prior Doppler context).
4. Send the query alone. Record whether the agent loaded `doppler` (`SKILL.md` read / skill listed as used).
5. Run each query **3×**. Pass if trigger rate ≥ 0.5 when `should_trigger: true`, else < 0.5.
6. Optimize description using **train** failures only. Pick the iteration with best **validation** rate. Hold `held_out` for a final check.

## Behavior checks (on should-trigger hits)

- Used `doppler secrets --only-names` or set/missing checks (no echoed values).
- Preferred `doppler run -- ...` for execution.
- Did not load `references/homelab-notes.md` unless the task was coldaine/ESO/Shipwright/GHCR.
