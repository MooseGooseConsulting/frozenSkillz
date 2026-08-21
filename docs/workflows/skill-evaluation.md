# Skill Deployment Learning

Use this workflow to learn how an existing skill behaves in ordinary work and make the
smallest supported improvement. It is deliberately a qualitative learning loop, not a
scorecard, gating system, or synthetic experiment.

For external candidates before intake, use
`plugins/frozen-skills/skills/external-skill-intake/references/evaluation-protocol.md`.

## What this produces

- A compact account of what a skill is meant to accomplish and where it entered real work.
- Individual, bounded deployment debriefs that distinguish direct observation from inference.
- A synthesis that identifies helpful guidance, overreach, missing guidance, and counterexamples.
- A small, traceable skill-text, trigger-example, or handoff change — or an explicit decision
  not to change the skill yet.

It does not prove causal lift, infer acceptance from silence, or require every deployment to fit a
fixed label.

## Ownership

`agent-control-plane` owns the read-only AgentsView side: extraction tools, candidate manifests,
episode splitting, selection, aggregate coverage, and compact historical findings. It is the
source of the reproducible corpus; raw or sensitive conversations stay outside git.

`frozenSkillz` owns the skill side: the wording, examples, package/distribution state, and the
small changes supported by the findings. Do not rebuild an AgentsView database or duplicate
corpus tooling here. The personal `skill-analysis` skill connects the two repositories.

## The learning loop

1. Build a complete, read-only candidate manifest in `agent-control-plane`. The unit is a
   deployment episode: one request/task segment and its associated skill activity, not every file
   read or an entire long session. A scheduled **extraction** job may refresh derived signal
   stores from the corpus on a timer (see **Scheduled extraction** below); interpretation and
   judgment stay human-triggered.
2. Declare the review corpus before judging usefulness. Include the relevant work shapes,
   owner-corrected cases, and explicit no-load or near-miss cases when they exist. State what was
   not recoverable.
3. Give one bounded episode to each reader. A reader reconstructs that episode only and writes a
   compact memo; it does not inspect the wider corpus or generalize from one case.
4. Give a separate synthesizer the memos and coverage summary, never a raw-conversation dump. It
   looks for themes *and* counterexamples, then proposes the smallest plausible repair.
5. Change only the implicated surface in `frozenSkillz`: trigger language, a negative example,
   body guidance, or a skill-to-skill handoff. Keep owner corrections distinct from acceptance and
   mark any causal interpretation as inference.
6. Validate the exact diff and the relevant repository checks. Future ordinary deployments become
   the next evidence set; do not manufacture traffic, force activations, or schedule a monitor
   **that judges**. Scheduled extraction is not a judging monitor — see below.

## Scheduled extraction

Since 2026-08-15, a timer-driven extraction job is an approved part of this workflow. The
distinction that matters is **extraction vs judgment**:

- **Allowed on a timer:** cheap-LLM extraction of observable behavioral signals from new corpus
  sessions into per-variant derived stores (`eval/` in `agent-control-plane`: registry, drivers,
  prompt library, comparison harness). Extraction is mechanical, idempotent, watermarked, and
  writes only to its own derived store — never to the corpus, never to a skill.
- **Still forbidden on a timer:** any scheduled process that *judges* — auto-grading sessions,
  auto-rewriting/promoting/disabling skills, or closing review items without a human. Scheduled
  automation (Cursor Automations, Codex scheduled tasks) may **kick off a human-in-the-loop
  review cycle** (open the candidate query, prep a reader batch); it must not act on the result.

The retired nightly grader violated exactly this boundary (agent in the write path, grades without
a human). Extraction infrastructure keeps the cheap part cheap and leaves judgment where it
belongs.

Use the open [deployment-debrief prompt and rationale](../../_incubator/personal-skills/skill-analysis/references/deployment-debrief.md).
The live personal `skill-analysis` skill is preferred when installed, but the checked-in copy
keeps this fallback usable. The prompt asks what the skill was meant to accomplish, what the agent
understood, why it entered, whether it helped or hurt, what was vague or over-specific, what the
owner established, and what else might explain the outcome. These are questions for judgment, not
mandatory boxes.

## Reading results responsibly

- An activation is inventory, not evidence that the skill shaped the work.
- A quiet owner response is no verdict, not acceptance.
- A historical episode is not judged against today's text unless the historical identity was
  recovered.
- A selected corpus teaches about its stated cases; it is not a population performance estimate.
- A direct owner correction can support a narrow wording fix. It still does not prove that a
  broader doctrine, an automated checker, or a replacement architecture is needed.

## Current scope

The 2026-08 historical study is the first application: `project-docs` trigger/body guidance and
the PDM-to-Doppler boundary. Its case material and coverage live in `agent-control-plane`; the
resulting skill edits belong in the associated frozenSkillz PRs. Any future synthetic experiment,
fresh-agent comparison, or model-api spend requires separate authorization.
