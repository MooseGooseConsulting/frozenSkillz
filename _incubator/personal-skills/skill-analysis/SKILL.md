---
name: skill-analysis
description: >-
  Study how an agent skill is understood and deployed in real work: where it
  entered, what it appeared to change, whether it helped or hurt, and what was
  missing, vague, overspecific, or intrusive. Use for deployment reviews,
  AgentsView skill-use research, owner-correction analysis, and evidence-backed
  skill improvement. Do not use merely to edit a skill or operate its domain.
---

# Skill Analysis

Learn from real skill deployments without asking one agent to digest an unbounded transcript pile.
Keep the entrypoint thin; load only the reference needed for the current stage.

## Core Flow

1. Resolve the recoverable activation-time skill identity and the current repository surfaces.
2. Build a complete candidate manifest before interpreting individual chats.
3. Declare the bounded analysis corpus and its coverage.
4. Send one trajectory at a time to a case reader; require one case memo per selected trajectory.
5. Send the assembled memos—not the raw chats—to a separate corpus reader.
6. Fill material gaps through additional one-case reads, then synthesize lessons and possible skill
   improvements.
7. Return only the smallest findings-supported wording, example, or handoff changes to the skill
   repository; later ordinary deployments supply the next evidence.

## Reference Router

| Need | Read |
|---|---|
| Understand what this skill should accomplish and what a good outcome looks like | `references/purpose-and-outcomes.md` |
| Inventory deployments, select a corpus, and coordinate per-case extraction | `references/corpus-assembly.md` |
| Review one deployment or understand why the debrief prompt is designed this way | `references/deployment-debrief.md` |
| Synthesize case memos, handle disagreement, and form improvement hypotheses | `references/synthesis-and-interpretation.md` |
| See the intended shape of a case memo | `examples/case-memo.md` |
| See the intended shape of a corpus synthesis | `examples/corpus-synthesis.md` |

Load `chat-history` only for bounded conversation retrieval. Keep AgentsView as the transcript
source; analysis tooling, deployment case memos, and derived corpus results belong in
`agent-control-plane`. `frozenSkillz` owns skill text, trigger and evaluation examples, and
package lifecycle or distribution state—not historical trajectory case memos.

## Non-Negotiable Boundaries

- A candidate manifest is navigation, not analysis.
- A case reader receives one bounded trajectory, not the whole corpus.
- The corpus reader receives completed case memos and coverage notes, not hundreds of raw chats.
- Separate directly observed events, reviewer interpretation, disagreement, and unknowns.
- Owner silence is not acceptance.
- Observational history can suggest help or harm; it cannot establish causation by itself.
- Do not force every deployment into a fixed contract matrix or composite score.
- Never let analysis automatically rewrite, promote, disable, or delete a skill.
