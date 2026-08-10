# Plan: Historical Skill-Deployment Learning MVP

Status: executed 2026-08-10; resulting skill changes are under review.

## Up front

- **What:** Learn from real deployments whether a skill helped, distracted, or lacked useful
  guidance.
- **Why:** Activation counts do not tell us whether an agent understood the skill or whether the
  skill made the task better.
- **How:** Build a read-only episode census, read declared cases one at a time, then synthesize
  only the compact memos.
- **How it improves skills:** Change only the implicated trigger, example, body instruction, or
  handoff; leave unsupported theories alone.

## Outcome we want

For each subject skill, produce a short, traceable answer:

- What was it supposed to accomplish?
- Where did it enter and what did the agent appear to understand?
- Did it appear helpful, harmful, neutral, or unknowable in this episode?
- What was missing, vague, too broad, or too specific?
- What did the owner actually establish, and what remains inference?
- What is the smallest change worth making now?

This is a guide for learning, not a required/permitted/prohibited checklist and not a numerical
grade. It does not claim causal improvement.

## Execution and boundaries

1. `agent-control-plane` builds the full, read-only candidate census and records episode windows,
   activation evidence, recoverable skill identity, co-loaded skills, and owner/outcome signals.
2. A deterministic declared sample is selected before usefulness is judged. The 2026-08 study used
   24 stratified `project-docs` episodes plus every PDM-centered episode.
3. One reader receives one bounded episode and writes an open deployment debrief. The corpus
   reader receives case memos and coverage only, not hundreds of raw chats.
4. `frozenSkillz` consumes the synthesis and applies only the supported language changes. It does
   not own AgentsView extraction, manifests, or aggregates.
5. Validate the extractor with deterministic tests and the skill edits with focused repository
   checks and exact-diff review. Do not manufacture new prompts or call external models.

## 2026-08 study result

- Census: 545 `project-docs` candidate episodes in 291 sessions; 543 observed activation episodes
  and two explicit no-load cases. The declared sample contained 24 episodes; one source was
  unrecoverable and is recorded as a gap.
- PDM: all 18 PDM-centered episodes were read. Eleven also showed Doppler in the same bounded
  episode; that correlation was not treated as evidence that Doppler was needed.
- `project-docs`: keep a deliverable-based trigger, exclude operational/README/incidental-doc
  proximity, map existing authority before proposing topology, and distinguish proposal, applied
  change, PR state, and owner acceptance.
- PDM/Doppler: ordinary trusted PDM launchers are self-sufficient. Doppler is for direct secret or
  injection work, not a routine prerequisite to fleet operations; preserve native PVE/PBS for
  named gaps or recovery.

## Immutable 2026-08 study record

The totals and findings above refer to the committed `agent-control-plane` study record at
[`30b1d12d19d4ba208de1a9d453e594ece5e7509a`](https://github.com/MooseGooseConsulting/agent-control-plane/tree/30b1d12d19d4ba208de1a9d453e594ece5e7509a),
not to a mutable local database or later regeneration. Its exact committed artifacts are:

- `projects/project-docs-skill-analysis-account-2026-08.md`,
  `projects/project-docs-skill-analysis-learnings.md`, and
  `projects/project-docs-skill-analysis-meta.md` for the compact study account, findings, and
  method metadata;
- `projects/project-docs-skill-analysis-manifest.csv`,
  `projects/project-docs-skill-analysis-coverage.json`,
  `projects/project-docs-skill-analysis-corpus.csv`,
  `projects/project-docs-skill-analysis-corpus-coverage.json`, and
  `projects/project-docs-skill-analysis-review-status.json` for the project-docs census and
  declared-corpus accounting; and
- `projects/pdm-cli-operations-skill-analysis-account-2026-08.md`,
  `projects/pdm-cli-operations-skill-analysis-manifest.csv`,
  `projects/pdm-cli-operations-skill-analysis-coverage.json`,
  `projects/pdm-cli-operations-skill-analysis-corpus.csv`,
  `projects/pdm-cli-operations-skill-analysis-corpus-coverage.json`, and
  `projects/pdm-cli-operations-skill-analysis-review-status.json` for the PDM-centered study.

Raw transcripts and temporary case memos deliberately remain outside git. This document is the
frozenSkillz-side plan and boundary, not a second corpus database.
