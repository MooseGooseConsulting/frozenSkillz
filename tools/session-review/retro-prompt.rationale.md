# Why retro-prompt.md is shaped this way

**Provenance.** Owner decision 2026-07-31: "why don't we just have letta agent run it,
especially because it can reason over the whole history of the project." The
`retrospective` skill's failure mode was never content — it was that the owner forgets to
invoke it, so learnings died with sessions. Human-nudge designs (hooks, flags) only
soften that failure; giving the duty to the already-scheduled stateful agent removes it.

**Why this agent.** The Session Reviewer already reads every skill-firing session
nightly, already emits `mutation_candidate` flags that nothing consumed until now, and —
unlike any session-scoped agent — carries memory across runs. That memory is what turns
one-off observations into corroborated proposals (step 3's Hypothesis → Corroborated
escalation is the whole point of the design).

**Why the trigger is `mutation_candidate`.** It is the rubric's existing "this session
should change a skill" judgment; reusing it means the retro phase inherits the
calibration contract instead of needing its own.

**Tuning knobs.**
- *Cap (2/night):* bounds gpt-5.6-luna cost and keeps each retro attentive; raise it if
  candidates routinely queue up, lower to 1 if nightly runs get slow.
- *Secondary trigger (negative sentiment + thrash):* catches sessions the rubric didn't
  flag but the owner visibly fought with; drop it if it produces noise retros.
- *The write boundary:* append-only dated entries to live skills are allowed unattended
  because they are non-destructive by construction; structural edits route to
  `proposals.md` for the owner. This is blast-radius control, not an approval gate — do
  not add further ceremony here.

**Maintenance contract.** Owner overturns of retro conclusions belong in the same
calibration table as grade overturns (`reviewer-prompt.md`). If retro proposals are
repeatedly overturned, fix this prompt or the skill's §0 rule — do not argue in the
proposals file.
