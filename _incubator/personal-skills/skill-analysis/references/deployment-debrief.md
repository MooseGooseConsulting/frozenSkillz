# Deployment Debrief Prompt and Rationale

## Design goal

The case reader should reason about one real deployment without being forced into a binary trigger
judgment or a fixed score. The prompt must still produce enough provenance and clarity for a later
agent to synthesize many case memos.

It therefore separates:

- purpose comprehension;
- deployment facts;
- apparent influence;
- help, harm, and friction;
- missing, vague, and overspecific guidance;
- owner-visible response;
- competing interpretations; and
- uncertainty.

The questions are invitations to investigate. They are not boxes that must each contain a value.

## Prompt for one historical deployment

```text
You are reviewing one deployment of an agent skill.

Inputs:
- the exact skill text or recoverable version;
- one user request;
- the bounded trajectory relevant to the skill;
- stable source identifiers.

First, explain in your own words what this skill is trying to help an agent accomplish. If the
purpose is unclear or internally conflicting, say so.

Then explain this deployment as a coherent case:

- Where did the skill enter the work, and did it arrive when it could still inform the task?
- What did the agent do that appears connected to identifiable skill guidance?
- Did the skill appear to help, hurt, add no visible value, or remain impossible to assess? Why?
- Did it add useful structure, confusion, context load, scope expansion, ceremony, or an unrelated
  handoff?
- What guidance was missing?
- What was too vague to guide action?
- What was too specific or rigid for this situation?
- Did the skill conflict with the request, repository authority, another skill, or available tools?
- What happened in the owner-visible result and the next substantive owner response?
- What should be retained, changed, removed, or illustrated with a better example?

Separate directly observed events from your interpretation. Identify unknowns and at least one
competing explanation where a plausible alternative exists. Say what additional example or source
would most improve the conclusion.

Use clear evidence labels where they help: `Observed`, `Assistant claim`, `User-reported history`,
`Owner response`, `Interpretation`, and `Unknown`. Do not create empty sections merely to satisfy
the labels. State whether the bounded window reaches implementation, validation, commit/push, and
an owner reply, and note other active instructions or skills that may explain the same behavior.

Write one compact case memo. Include the session and turn-window identifiers, user goal, deployment
point, observed actions/result/owner response, your open-ended analysis, competing interpretations,
unknowns, and useful follow-up pointers.

Do not compare this case with other deployments. Do not assign a global skill verdict. Do not infer
acceptance from silence or causation from temporal sequence.
```

## Why the prompt begins with purpose comprehension

An evaluator cannot decide whether guidance was helpful without first showing that it understands
the intended job. Asking for a restatement exposes ambiguity in the skill itself and prevents the
reviewer from silently substituting its own preferred purpose.

This is not a quiz with one exact answer. Divergent reasonable restatements are evidence that the
skill may communicate its purpose inconsistently.

## Why deployment is reconstructed before judging value

A skill loaded after the relevant decision cannot have informed that decision. A skill may also be
loaded for inspection, editing, or a transitive handoff rather than task use. Locating when and how
it entered prevents a read event from being treated as impact.

## Why help and harm remain open-ended

The analysis should notice dimensions that the author did not predict. Fixed labels such as
`useful`, `ignored`, or `false positive` compress several independent effects into one box. The
prompt instead asks the reader to explain useful structure, confusion, context load, scope
expansion, ceremony, and handoffs while permitting other findings.

A later corpus synthesis may group recurring descriptions. The groups should emerge from case
memos, not be imposed before reading.

## Why missing, vague, and overspecific are separate questions

A skill can fail in different directions:

- missing guidance leaves the agent without needed support;
- vague guidance states an aspiration without helping a decision;
- overspecific guidance displaces judgment or applies one context's solution everywhere.

Combining these into a generic `body problem` hides the repair surface.

## Why owner response is included but not treated as ground truth

Explicit owner correction or acceptance is important evidence about owner-visible value. Silence,
topic change, or session end is not a verdict. An owner reaction can also address only part of the
work, so the memo should say exactly what the response supports.

## Why the prompt requires competing explanations

Historical trajectories are observational. A skill may appear in difficult tasks because the task
was difficult; the skill may not have caused the difficulty. Requiring a plausible alternative
reduces premature causal stories without pretending uncertainty makes learning impossible.

## Why one case reader receives one trajectory

A reader given dozens of chats will skim unevenly, forget early cases, anchor on dramatic examples,
and blur sources. One-case isolation preserves attention and prevents the emerging corpus theory
from contaminating extraction.

The later corpus agent performs comparison using completed memos. It does not redo raw extraction.

## Adaptation for forward tests

When reviewing a fresh agent run, the same debrief questions apply, but the packet may also include
a deterministic final-state check. Do not tell the performing agent the expected diagnosis or
desired skill change. The case reader remains separate from the task-performing agent when possible.

## Rejected prompt shapes

Do not default to:

- `Should the skill have fired: yes/no?` — it converts reviewer preference into ground truth.
- `Required/permitted/prohibited` for every case — most skill descriptions are guidance, not law.
- a mandatory confusion matrix — useful only for a genuinely adjudicated narrow classifier.
- `Did the skill materially cause the outcome?` — historical sequence rarely establishes this.
- one prompt containing the entire corpus — it produces uneven, untraceable synthesis.
- one mutually exclusive failure class — a deployment can be optional, unused, costly, and still
  complete successfully.
- a long checklist with required answers — it narrows attention to anticipated failure modes.

Use narrower structured judgments only when a specific decision genuinely requires them and the
source of truth is explicit.
