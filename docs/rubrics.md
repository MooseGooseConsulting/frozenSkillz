# Rubrics: Philosophy, Sources, and Current Practice

How frozenSkillz thinks about scoring agent behavior. This is the philosophy doc; the procedure
lives in `docs/workflows/skill-evaluation.md` (existing skills) and
`plugins/frozen-skills/skills/external-skill-intake/references/evaluation-protocol.md` (external
candidates).

## Philosophy

A rubric's value is not the number. The real instrument is: run the skill, watch the behavior it
evokes, then reason backward — was that the appropriate behavior for the situation, where did it
drift, what should it have done instead? Scores are bookkeeping that keeps reviewers consistent;
the observations are the deliverable. A rubric reduced to countable metrics misses the point.

Corollaries we hold:

- **Scenarios come from real history, not imagination.** Fabricated "the user might say X" prompts
  test the wrong thing. We derive eval scenarios from actual past conversations (via the
  `chat-history` skill), preferably episodes with verified ground truth so correctness is
  checkable.
- **Never let a model grade its own misunderstanding.** Self-grading repeats the same blind spot.
  Every rubric is paired with known ground truth, deterministic checks where possible, and human
  review. (Observed in our own history: a compaction summary confidently blamed "the other
  session" for files the session itself created.)
- **Grade the outcome, not the transcript.** The agent claiming success is not evidence; the final
  state checked against ground truth is.
- **Owner silence is unknown, not acceptance.** Explicit corrections and explicit acceptance are
  strong labels. A conversation ending without either is `no verdict`, even when the agent claimed
  completion.
- **Separate trigger quality from instruction quality.** A useful skill that fires on the wrong
  tasks needs a narrower trigger; a correctly triggered skill that adds no useful behavior needs a
  body revision or removal. One combined grade hides the repair.
- **Historical correlation is not causal evidence.** Pair the full-history field review with
  controlled current/prior/no-skill replay before claiming the skill caused the outcome.
- **Multiple trials, always.** Agents are non-deterministic. At least 3 trials per scenario per
  scoring event, recorded individually. A single passing run is an anecdote, not a measurement.
- **Don't grade against one imagined path.** A deviation that solves the task better is a finding
  about the rubric or the skill's prescribed route, not a failure.
- **Hard gates are the exception, not the structure.** A gate is a failure that should veto the
  whole trial regardless of other strengths (e.g. a retrieval skill contradicting known ground
  truth). Most criteria are quality gradients; many evaluations have no gates. Do not manufacture
  gates to make a rubric look rigorous.
- **Capability evals graduate into regression evals.** New cases start at a low pass rate — a hill
  to climb. Once the skill passes consistently, the case becomes part of that skill's permanent
  regression suite and must keep passing on every future edit.

## Sources and inspiration

- **HyperAgent (Airtable)** — practitioner model closest to ours: a rubric is a persistent
  "definition of quality" stored alongside skills and memories, applied via LLM-as-judge. Their
  rules we adopted: rubrics are for behavior that must stay consistent across runs, not one-off
  tasks; self-grading is a checkpoint, not proof, and must be paired with source links,
  deterministic checks, and sampled human review.
  ([walkthrough](https://www.ai.joaoqueiros.com/blog/hyperagent-no-code-ai-agent-team-three-builds))
- **Anthropic, "Demystifying evals for AI agents"** — the grader taxonomy (code-based,
  model-based, human — each checks what it's good at); outcome-over-transcript; binary scoring
  (the gate structure); pass@k / pass^k trial metrics; capability vs. regression lifecycle; and
  the research-agent rubric pattern (groundedness, coverage, source-quality checks) that maps
  one-to-one onto chat-history evaluation.
  ([anthropic.com](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents))
- **Twine, "How to Write an LLM Evaluation Rubric"** — the term "hard gates" and the gates vs.
  quality-preferences split; giving each criterion a passing, borderline, and failing example so
  two reviewers score alike.
  ([twine.net](https://www.twine.net/blog/how-to-write-an-llm-evaluation-rubric/))
- **OpenAI / RUBINLAKE radar caution** — blind LLM-as-judge scoring as a shipping signal is an
  anti-pattern: judges are non-deterministic, length-biased, and need calibration against human
  graders. Single model scores are not objective quality measures.
  ([rubinlake.com](https://rubinlake.com/en/technology-radar/developer-ai-and-delivery/blind-llm-as-judge))
- **Our own chat history** — the strongest evidence. Real episodes showed the failure modes any
  rubric here must catch: source-trust vetoes (raw transcripts > summaries > archive DBs),
  confident-but-wrong self-reports after compaction, recap handoffs that transfer facts but not
  intent, and lexical false positives. (`evals/cases/2026-08-03-chat-history.md`)

## What we're trying for the moment

The two-layer rubric, first applied in `evals/cases/2026-08-03-chat-history.md`:

1. **Hard gates (optional, crisp, countable)** — only genuine non-negotiables. In the current
   case: the final answer must match known ground truth, and every substantive claim must cite
   the session it came from. Where a gate can be made code-checkable (string match, state check),
   prefer code over a judge.
2. **Behavioral assertions (pass / partial / fail)** — derived from the skill's own contract,
   judged against the observed trajectory: staged delegation, artifact discipline, brief-only
   worker returns, routing that follows the skill's decision tree, honestly recorded coverage
   gaps, caught false positives.
3. **Qualitative review (the actual deliverable)** — what behavior was evoked; was each routing
   decision appropriate; what went wrong; what should it have done instead; were any deviations
   better than the prescribed route; what specific change to the skill text does that imply.

Open questions we're deliberately leaving open:

- Whether judge-evaluated gates (vs. code-only gates) earn their place long-term.
- How many trials is enough in practice — 3 is the floor, not a proven optimum.
- Whether the repo's existing 1–5 scalar rubrics (`artifact-rubrics.md`, `eval-case.md`) should
  adopt the gates-plus-assertions shape or stay scalar for intake triage.
