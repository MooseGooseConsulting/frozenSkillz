# Writing a Skill Intent README

The adjacent `README.md` is a human-maintainer record of the skill's
**response-shaping rationale**. It should let a future maintainer understand why
the instructions are designed to evoke a particular model response before they
change that design. It is not an installation guide, a restatement of the
skill's business purpose, or a hidden runtime instruction file.

## Required content

Explain the following in the level of detail the skill actually needs:

1. **Intended response.** Describe the decisions, behavior, or output the
   instruction design is meant to evoke from the model.
2. **Context and expected activation.** Give the larger context when it helps
   explain the design. In particular, describe the situations, request shapes,
   or workflow states in which you expect the skill to activate. Mention a
   non-activation boundary when it materially distinguishes this skill from a
   nearby capability.
3. **Opinionation map.** State whether the skill is intended to be opinionated.
   Identify which material lanes deliberately prescribe a preferred workflow
   and which lanes are intended to provide a neutral or unbiased reference that
   supports the model's judgment. Treat hard safety, authority, or correctness
   constraints as constraints rather than disguising them as stylistic
   opinions.
4. **Causal instruction design.** Explain how the important wording, ordering,
   boundaries, evidence gates, examples, and routed resources are expected to
   produce the intended response. Focus on design choices whose removal or
   alteration could change model behavior.

## Optional failure-mode context

When a particular design choice deliberately counters an observed failure or a
tempting model default, consider recording that relationship. Describe the
demonstrated failure mode or likely default and how the design choice is meant
to steer the response away from it. This is optional: do not invent a failure
mode, require one for every choice, or turn one past incident into a universal
rule without evidence.

## Authority and maintenance

- Runtime requirements belong in `SKILL.md` or a resource it explicitly routes
  to, never only in the README.
- The target skill should not route agents to its own intent README. The
  `skill-authoring` skill routes agents to this writing guide when they are
  creating or revising that human record.
- Update the README when the response-shaping design materially changes. A typo,
  formatting cleanup, or implementation-neutral example correction does not by
  itself require a rationale rewrite.
- If the README and agent-facing instructions disagree about runtime behavior,
  the agent-facing instructions control. Repair the stale rationale in the same
  change so future maintainers are not misled.

## Suggested shape

Use whatever structure makes the rationale easiest to maintain. A useful
starting point is:

```markdown
# <Skill name>: design intent

## Intended response
## Context and expected activation
## Opinionation map
## Causal design rationale
## Failure modes or tempting defaults (optional)
```

The headings are a suggestion, not a required template. Completeness means the
maintainer can recover the intended response and the reasons for the meaningful
design choices; it does not mean filling every section with ceremonial text.
