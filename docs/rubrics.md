# Skill Learning: Philosophy and Current Practice

For an existing skill, the useful question is not “what score did it get?” It is whether the
guidance helped an agent understand and complete the work it entered — and, if not, what smallest
wording change is justified.

## Principles

- Read real, bounded deployments before generalizing. Actual owner corrections and task outcomes
  are more useful than invented prompts.
- Ask open questions: what the skill was meant to do, why it entered, what it changed, whether it
  helped or hurt, and what was vague, broad, or over-specific.
- Treat the human response carefully. A correction is evidence about the misunderstanding; silence
  is not acceptance.
- Preserve counterexamples and competing explanations. A skill file read, a green test, or a
  later agent claim does not establish causation.
- Use deterministic checks for tools and packaging. Use human judgment for whether guidance was
  appropriate in a real conversation.

This draws on the useful field-evaluation distinction in Anthropic’s
[evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):
automated checks and human review answer different questions. The historical deployment method
uses the latter without turning it into a synthetic trial program or LLM-grading system.

## Process boundary

The procedure is [skill deployment learning](workflows/skill-evaluation.md). `agent-control-plane`
owns the read-only corpus, episode manifests, selection, and aggregates. `frozenSkillz` owns the
skill wording and the narrow changes supported by those findings.

There is no universal numeric rubric for historical deployment learning. If a future product needs
a genuine pass/fail operational check, define that check separately for the exact risk it protects;
do not retrofit it onto a qualitative historical study.
