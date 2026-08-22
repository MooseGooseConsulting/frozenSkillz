# Skill Authoring: design intent

## Intended response

This skill should make an agent treat skill creation as response design. The
agent should put behavior-changing instructions on the runtime path while also
leaving a separate human record that explains why those instructions should
evoke the intended response.

## Context and expected activation

The skill is expected to activate when a frozenSkillz-owned skill is created or
materially redesigned, including changes to triggering, workflow lanes,
boundaries, evidence gates, or routed resources. It should not activate merely
because an agent is using an existing skill, and third-party intake belongs to
the separate external-skill-intake workflow.

The repository root routes here so the detailed convention has one agent-read
home. A target skill's own README remains human-only and is not part of that
target skill's runtime instruction graph.

## Opinionation map

This skill is intentionally opinionated about instruction authority and
maintainability: runtime behavior belongs in `SKILL.md` or routed resources, new
skills remain gated until reviewed, and material response-design choices get a
human rationale record.

It is deliberately less opinionated about the exact internal structure of a
skill and the prose or headings used in its README. Those lanes should preserve
the author's judgment unless a concrete trigger, safety, correctness, or
maintenance need justifies a stronger prescription.

## Causal design rationale

The `SKILL.md` stays short so an author first receives the authority split and
the routing decision. The substantial README-writing guidance lives in one
routed reference because it is needed specifically when that human record is
created or updated. The target README itself is not routed, preventing human
maintenance rationale from silently becoming runtime behavior.

The guide asks for intended response, activation context, an opinionation map,
and causal instruction design because together they explain how the prompt is
supposed to work. Merely describing the skill's business purpose would not tell
a future maintainer which wording or boundaries can safely change.

## Failure modes or tempting defaults

This design counters two demonstrated maintenance failures: placing behavior in
a README that agents never read, and writing a README that only says why the
skill exists without explaining how its instructions shape the response. The
failure-mode section remains optional in the general guide so one observed case
does not become mandatory ceremony for every skill.
