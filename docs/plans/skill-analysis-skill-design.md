# Plan: Build the `skill-analysis` Skill

Status: construction complete; first `project-docs` pilot executed.

## Up Front

- **What:** Build a progressively disclosed skill that assembles real deployment corpora, reviews
  one trajectory at a time, and learns across completed case memos.
- **Why:** Fire counts do not explain whether a skill was understood or useful, while asking one
  agent to read hundreds of chats produces shallow, untraceable conclusions.
- **How:** Keep `SKILL.md` as a thin router; put purpose, corpus assembly, the one-case prompt and its
  rationale, synthesis guidance, and examples in focused references.
- **Outcome:** Another agent can use the skill to build a complete candidate manifest, extract every
  selected case independently, synthesize the assembled corpus, and propose bounded improvements
  without turning the process into a checklist or score.

## Product Contract

The skill should help answer:

- Do agents understand what the evaluated skill is supposed to accomplish?
- Where was it deployed, and when did it enter the work?
- What did it appear to change?
- Did it appear helpful, harmful, neutral, or impossible to assess?
- What was missing, too vague, too specific, intrusive, or in conflict?
- What patterns and counterexamples exist across deployments?
- What small improvement is supported, and what should remain unchanged?

The skill must not ask one agent to ingest an unbounded raw corpus. It must not treat reviewer
judgment as ground truth, reduce findings to a composite score, infer acceptance from silence, or
claim causal effect from observational sequence.

## Skill Shape

```text
skill-analysis/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── evals/
│   └── triggers.json
├── references/
│   ├── purpose-and-outcomes.md
│   ├── corpus-assembly.md
│   ├── deployment-debrief.md
│   └── synthesis-and-interpretation.md
└── examples/
    ├── case-memo.md
    └── corpus-synthesis.md
```

### `SKILL.md`

Keep only:

- the concise trigger description;
- the end-to-end flow in a few steps;
- a reference router;
- repository ownership boundaries; and
- non-negotiable context and attribution safeguards.

It should not contain the full prompt, corpus mechanics, interpretation doctrine, or examples.

### `references/purpose-and-outcomes.md`

Explain what the skill is intended to accomplish, what a good learning outcome looks like, what it
can teach about existing skills, and what it explicitly is not.

### `references/corpus-assembly.md`

Define the complete candidate manifest, declared analysis corpus, one-trajectory case queue,
per-case source packet, completeness reconciliation, scaling strategy, and targeted gap filling.

### `references/deployment-debrief.md`

Contain the exact one-case prompt and a section-by-section rationale. Explain why it begins with
purpose comprehension, why it asks open-ended help/harm questions, why missing/vague/overspecific
are separate, why it requires competing explanations, and why one reader sees one trajectory.

Document rejected prompt designs so future revisions do not reintroduce binary trigger judgment,
mandatory contract labels, causal language, whole-corpus prompts, or mutually exclusive failure
classes.

### `references/synthesis-and-interpretation.md`

Define what the corpus reader receives, the synthesis prompt, theme construction, counterexample
handling, disagreement, observation-versus-attribution language, and the route from lessons to
small skill changes.

### Examples

Show a traceable but open-ended case memo and a corpus synthesis shape. They demonstrate useful
outputs without becoming mandatory templates.

## Build Sequence

1. Capture the product contract and non-goals.
2. Write the one-deployment prompt and explain every design choice.
3. Write corpus assembly before any AgentsView pilot so extraction can scale beyond one context.
4. Write the separate corpus-synthesis method.
5. Reduce `SKILL.md` to a router over those references.
6. Align `agents/openai.yaml` and trigger cases with the product contract.
7. Validate the live personal skill.
8. Mirror the complete live tree into the incubator path and verify exact equality.
9. Run the `project-docs` pilot in `agent-control-plane` using one case reader per trajectory and a
   separate corpus reader.
10. Revise the skill from the pilot's observed problems before considering promotion.

The first clean-room routing test confirmed that a fresh agent found the thin router and loaded the
purpose, corpus, debrief, synthesis, and example resources for a large-corpus request. It also
identified details that must be explicit before the real pilot: subject-specific activation-channel
inventory, multi-deployment sessions, declared indexed scope, adjacent-case matching, and targeted
double reading. Those refinements belong in `references/corpus-assembly.md`, not `SKILL.md`.

The first real pilot then completed a 291-session candidate census, declared a 13-case corpus,
produced one independent memo per bounded trajectory, and used a separate corpus reader for
synthesis. It exposed two additional method needs now captured in the references: preserve the
activation-time skill identity rather than substituting today's file, and record evidence source,
bounded-window outcome state, interacting instructions, and retrieval limitations consistently.

## Why This Prompt

The prompt must produce both attention and later composability:

- Purpose restatement reveals whether the evaluated skill explains itself.
- Deployment reconstruction prevents a file read from becoming a claim of influence.
- Open-ended help/harm inquiry leaves room for unanticipated behavior.
- Separate missing/vague/overspecific questions identify different repair surfaces.
- Owner-visible response grounds the review without treating silence as approval.
- Competing explanations preserve observational uncertainty.
- Stable source pointers make corpus-level themes traceable.
- One-case isolation prevents context overload and theory leakage.

The prompt intentionally does not ask for a global verdict, score, or required answer to every
question. The corpus reader, not the case reader, performs cross-case comparison.

## Validation

- Run the skill-creator structural validator against the live and incubator roots.
- Parse `evals/triggers.json` in both roots.
- Compare all relative file paths and SHA-256 hashes between live and incubator copies.
- Run repository validation.
- Forward-test corpus assembly with a candidate manifest larger than one reader can reasonably hold.
- Confirm each selected deployment produces one memo before corpus synthesis begins.
- Confirm the corpus reader receives memos and coverage notes, not raw transcripts.
- Confirm a consequential finding remains traceable to its source case and preserves a
  counterexample or uncertainty where one exists.

## Stop Conditions

- Do not run the pilot while `SKILL.md` still contains the full manual.
- Do not synthesize an analysis corpus with silently pending cases.
- Do not describe a selected corpus as the complete population.
- Do not promote the skill from structural validation alone.
- Complete this construction phase when the thin router, references, examples, metadata, and trigger
  cases validate and the live/incubator trees match. The real `project-docs` pilot is the next
  phase, not evidence that construction was unnecessary.
