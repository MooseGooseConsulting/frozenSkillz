# Corpus Synthesis and Interpretation

## Input contract

The corpus reader receives:

- the candidate-manifest coverage summary;
- the declared analysis-corpus manifest;
- one completed memo for each selected trajectory whose bounded source could be extracted;
- a separately accounted list of every selected exclusion and block, including its reason;
- skill version information; and
- source pointers for targeted challenge.

It does not receive a pile of raw transcripts. It must not invent a missing case analysis from
manifest metadata, treat an unextractable selected trajectory as memo-covered, or silently omit a
block from the corpus account.

## Corpus-reader prompt

```text
You are synthesizing individually reviewed deployments of one agent skill.

Read the corpus coverage notes and every completed case memo. Do not overwrite case-level
uncertainty or treat administrative manifest fields as evaluation labels.

First confirm that every memo maps to one selected, extractable trajectory and that every selected
trajectory without a memo is separately accounted as an exclusion or block. Do not infer findings
from those unextracted trajectories.

Explain:

1. How the case readers understood the skill's intended purpose, including meaningful disagreement.
2. Where and how the skill was deployed across the reviewed corpus.
3. Recurring ways the skill appeared helpful, harmful, unused, confusing, vague, overspecific, or
   intrusive.
4. Counterexamples that weaken each major pattern.
5. Missing guidance, trigger ambiguity, examples, or skill-to-skill handoffs that recur.
6. What the owner explicitly accepted or corrected, without treating silence as a verdict.
7. Which findings are direct observations, cross-case interpretations, or unresolved hypotheses.
8. The activation-time skill version or unknown identity supporting each theme, and whether it is
   the same as, superseded by, or not comparable to the current skill.
9. The smallest skill improvements supported by the corpus, scoped to those activation-time
   versions.
10. What should not be changed yet.
11. Which additional bounded cases would most reduce consequential uncertainty.

Use descriptive counts only when you state the reviewed denominator and selection method. Do not
produce a composite score or force a single keep/narrow/broaden verdict. Preserve minority patterns
and reviewer disagreement.
```

## Synthesis method

### Read every memo before clustering

Do not synthesize incrementally from the first few cases. First confirm that every selected
trajectory is either represented by one extractable case memo or separately accounted as blocked or
excluded; then read each memo and build provisional themes. Keep source case identifiers attached to
every theme.

### Build themes from explanations

A theme should state:

- the observed or interpreted pattern;
- supporting case identifiers;
- each supporting case's activation-time skill identity, or `unknown`;
- counterexamples;
- affected skill surface;
- confidence and uncertainty;
- the smallest plausible change; and
- a discriminating next case or comparison.

Do not collapse evidence from distinct historical versions into one statement about the current
skill. A theme can describe a superseded version as historical context, but it must name that scope.
Treat an unknown identity as unknown rather than assuming it matches the current file.

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
commission the recheck rather than performing it: dispatch a case reader against the exact source
window, or collect a discriminating case. The synthesizer does not open raw transcripts itself —
its input contract is memos, and one-trajectory extraction stays isolated from the emerging
corpus-level view precisely so a recheck cannot be steered by it. The reader returns a memo; the
synthesis updates from that.

### Distinguish observation from attribution

Examples:

- **Observed:** the skill loaded before the agent opened three authority documents.
- **Interpretation:** the skill appears to have prompted the authority lookup.
- **Unknown:** whether the agent would have opened them without the skill.
- **Owner evidence:** the owner explicitly corrected the README policy that followed.

The synthesis may describe associations. Reserve causal language for a credible controlled
comparison — one where the deployment condition was actually assigned rather than observed.

Matching deployment episodes against no-load episodes drawn from recorded history does not earn it.
Matching equalizes only the attributes that happen to be recorded; task difficulty, agent, operator
intent, and whatever drove the skill to load in the first place stay unbalanced, and that last one
is selection, not noise. Report matched historical comparisons as associations with the matched
attributes named, and say plainly what remains unmatched.

## Turning lessons into changes

Propose a change only when the case corpus explains:

- what recurrent or important problem exists;
- where in the skill the repair belongs;
- which cases demonstrate it;
- which activation-time version(s) those cases exposed and their relationship to the proposed
  current surface;
- what counterexamples constrain the repair; and
- how a real regression or later deployment would test it.

A single explicit owner correction may justify a narrow repair. A broad rewrite needs varied
supporting cases. When evidence conflicts, the correct output can be a better question and a targeted
next corpus rather than a change. Historical failure in a superseded version is not, by itself, a
current-skill defect; either tie the change to identical current guidance or describe it as a
separate current inspection or future observation.

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
