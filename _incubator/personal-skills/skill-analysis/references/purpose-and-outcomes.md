# Purpose and Outcomes

## What this skill is for

`skill-analysis` helps an agent learn how another skill behaves in real work. It connects three
questions that activation counts cannot answer:

1. Did the agent understand what the skill was trying to accomplish?
2. Where did the skill enter the work, and what did it appear to change?
3. What should be retained, clarified, narrowed, expanded, removed, or tested next?

The method is exploratory before it is evaluative. It should surface unexpected uses, harms,
strengths, missing guidance, and conflicting interpretations—not merely confirm the evaluator's
initial theory.

## What a good outcome looks like

A good analysis leaves the owner with:

- a map of where the skill was actually deployed;
- individually reasoned case memos for the declared corpus;
- recurring patterns plus examples that contradict those patterns;
- a clear separation between observed events, interpretation, and unknowns;
- concrete improvement hypotheses tied to real deployments;
- an explanation of what additional observation would resolve important uncertainty; and
- no change recommendation when the corpus does not support one.

The output is useful when it changes how the skill is understood or identifies a small, testable
improvement. A score, fire count, or tidy verdict is not inherently useful.

## Questions the analysis should be able to answer

- What does the skill tell an agent it is supposed to accomplish?
- Do agents appear to understand that purpose consistently?
- Where is the skill installed or available, and in what harnesses, projects, request types, and
  task moments does it actually appear?
- At what point in the task does it enter?
- Which parts of its guidance appear to shape decisions or actions?
- When does it help, distract, expand scope, create ceremony, or do nothing visible?
- What is missing?
- What is too vague to guide action?
- What is too specific or rigid for the situations where it appears?
- What interactions with other skills help or hurt?
- How does the owner respond?
- Which findings repeat, which are counterexamples, and which remain unresolved?

## How this improves existing skills

Route each supported learning to the smallest repair surface:

- misunderstood purpose -> description, opening explanation, or examples;
- deployment in unrelated work -> trigger wording or negative examples;
- plausible absence from useful work -> trigger wording or positive examples;
- helpful guidance -> preserve it and add a regression example;
- vague guidance -> add decision support, examples, or a focused reference;
- overspecific guidance -> restore agent judgment or split variant-specific material;
- harmful or distracting guidance -> narrow, rewrite, or remove the clause;
- unnecessary skill handoff -> repair the dependency boundary;
- conflicting evidence -> do not change the skill yet; collect the discriminating case.

## What it is not

This skill is not:

- a universal grader;
- a mandatory precision/recall exercise;
- a contract-compliance checklist;
- a model self-report accepted as truth;
- proof that a skill caused an outcome;
- a reason to load every historical transcript into one context;
- an automatic lifecycle controller; or
- a substitute for checking an owner-visible result.

Counts and structured fields may support navigation and corpus accounting. They do not replace
case-level reasoning or cross-case interpretation.
