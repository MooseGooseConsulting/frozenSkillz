# Corpus Synthesis and Interpretation

## Input contract

The corpus reader receives:

- the candidate-manifest coverage summary;
- the declared analysis-corpus manifest;
- one completed memo per selected trajectory;
- explicit exclusions and blocks;
- skill version information; and
- source pointers for targeted challenge.

It does not receive a pile of raw transcripts. It must not invent a missing case analysis from
manifest metadata.

## Corpus-reader prompt

```text
You are synthesizing individually reviewed deployments of one agent skill.

Read the corpus coverage notes and every completed case memo. Do not overwrite case-level
uncertainty or treat administrative manifest fields as evaluation labels.

Explain:

1. How the case readers understood the skill's intended purpose, including meaningful disagreement.
2. Where and how the skill was deployed across the reviewed corpus.
3. Recurring ways the skill appeared helpful, harmful, unused, confusing, vague, overspecific, or
   intrusive.
4. Counterexamples that weaken each major pattern.
5. Missing guidance, trigger ambiguity, examples, or skill-to-skill handoffs that recur.
6. What the owner explicitly accepted or corrected, without treating silence as a verdict.
7. Which findings are direct observations, cross-case interpretations, or unresolved hypotheses.
8. The smallest skill improvements supported by the corpus.
9. What should not be changed yet.
10. Which additional bounded cases would most reduce consequential uncertainty.

Use descriptive counts only when you state the reviewed denominator and selection method. Do not
produce a composite score or force a single keep/narrow/broaden verdict. Preserve minority patterns
and reviewer disagreement.
```

## Synthesis method

### Read every memo before clustering

Do not synthesize incrementally from the first few cases. First confirm corpus completeness, then
read each memo and build provisional themes. Keep source case identifiers attached to every theme.

### Build themes from explanations

A theme should state:

- the observed or interpreted pattern;
- supporting case identifiers;
- counterexamples;
- affected skill surface;
- confidence and uncertainty;
- the smallest plausible change; and
- a discriminating next case or comparison.

Useful repair surfaces include:

- purpose/description;
- trigger examples;
- procedural body;
- focused reference material;
- examples;
- handoff or dependency guidance;
- tool/runtime assumptions; and
- no demonstrated skill defect.

### Preserve disagreement

Reader disagreement may mean:

- the skill purpose is ambiguous;
- the source window is incomplete;
- the behavior supports multiple explanations;
- owner intent is not recoverable; or
- one reviewer overreached.

Do not average these into a middle score. Explain the competing readings and, when consequential,
return to the exact source window or collect a discriminating case.

### Distinguish observation from attribution

Examples:

- **Observed:** the skill loaded before the agent opened three authority documents.
- **Interpretation:** the skill appears to have prompted the authority lookup.
- **Unknown:** whether the agent would have opened them without the skill.
- **Owner evidence:** the owner explicitly corrected the README policy that followed.

The synthesis may describe associations. Use causal language only after a credible controlled or
matched comparison.

## Turning lessons into changes

Propose a change only when the case corpus explains:

- what recurrent or important problem exists;
- where in the skill the repair belongs;
- which cases demonstrate it;
- what counterexamples constrain the repair; and
- how a real regression or later deployment would test it.

A single explicit owner correction may justify a narrow repair. A broad rewrite needs varied
supporting cases. When evidence conflicts, the correct output can be a better question and a targeted
next corpus rather than a change.

## Final product

The corpus synthesis should be readable as a learning report:

- corpus and coverage;
- purpose comprehension;
- deployment patterns;
- apparent help and harm;
- missing/vague/overspecific guidance;
- owner responses;
- counterexamples and disagreements;
- improvement hypotheses;
- proposed next cases; and
- limits on the conclusions.

The findings, not the structure, are the deliverable.
