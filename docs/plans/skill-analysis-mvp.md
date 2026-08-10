# Plan: Skill Analysis MVP — `project-docs` Deployment Learning Pilot

Status: completed pilot; observational findings published in `agent-control-plane`.

## Up Front

- **What:** Learn whether agents understand what `project-docs` is for, where it enters real work,
  what it changes, when it helps or hurts, and what its instructions are missing.
- **Why:** Activation counts cannot tell us whether the skill was understood, useful, intrusive,
  vague, overspecific, or irrelevant to the task.
- **How:** Give an evaluator the skill, the user request, and a bounded work trajectory. Ask an
  open-ended deployment debrief, then compare examples, counterexamples, and recurring themes.
- **Result:** A short set of evidence-backed lessons and improvement hypotheses for the trigger,
  body, examples, or handoffs—not a compliance score.

## How This Improves the Existing Skill

- Agents misunderstand the purpose → rewrite the purpose, trigger description, or examples.
- The skill repeatedly enters work where it distracts or takes over → narrow or clarify its
  trigger and add those real requests as regressions.
- The skill is absent from work where its guidance would plausibly help → investigate whether the
  trigger is too narrow; do not assume a missed activation from topic similarity alone.
- Guidance helps agents make better choices → preserve the useful clause and the example that
  demonstrates it.
- Guidance is loaded but unused, harmful, too vague, or too specific → revise the body at the
  point of failure rather than treating every problem as a trigger defect.
- The skill creates an unnecessary handoff to another skill → repair that boundary directly.
- Evidence supports competing interpretations → keep both interpretations visible and identify
  what another example or controlled comparison would teach us.
- After a change → rerun the regression and inspect the next real `project-docs` opportunities
  before claiming improvement.

## Goal

Use `skill-analysis` to answer one practical set of questions:

> Do agents understand what `project-docs` is supposed to accomplish? Where has it been deployed?
> What did it appear to change? Did it help, hurt, or do nothing observable? What is missing, too
> vague, or too specific?

This MVP is a learning exercise about one skill in real use. It does not grade every skill, pretend
an evaluator has ground truth, or build recurring automation.

## Completed Pilot

- Candidate population: 291 sessions, 289 with an observed activation signal and 2 explicit
  no-load requests, across six indexed
  harnesses from 2026-02-28 through 2026-08-10.
- Declared corpus: 10 activation cases plus 3 adjacent no-load cases, selected purposively for
  authority work, operational work, README/docs work, and owner corrections.
- Extraction: one bounded trajectory per case reader; 13 case memos completed before synthesis.
- Synthesis: a separate corpus reader received the memos and coverage notes, not raw transcripts.
- Gap fill: not required for the observational conclusions; matched comparisons remain necessary
  before causal claims.
- Supported repair: preserve the narrow deliverable-based trigger and add a smallest-change stop
  rule, repository-derived topology, claim-category boundaries, and explicit handoff limits.
- Process repair: retain activation-time skill identity, evidence-source labels, bounded-window
  outcome state, interaction context, and a read-only retrieval fallback.

The pilot found recurring failure shapes, not population rates. It does not prove that
`project-docs` caused the observed help or harm, and it does not establish that the current
trigger-gated version has solved the historical cases.

## Why the Earlier Scope Was Too Large

The earlier design combined too many independent problems:

- every skill and every harness;
- full historical skill-version reconstruction;
- activation precision and recall;
- whether loaded instructions changed behavior;
- whether changed behavior caused better outcomes;
- skill-to-skill dependency graphs;
- delayed PR/runtime aftermath;
- current/prior/no-skill replay;
- generalized graders and decision thresholds; and
- scheduled monitoring and automatic review queues.

Those are possible later capabilities. Requiring all of them before answering whether
`project-docs` overtriggers would create an evaluation platform before proving the first analysis.

## Inputs

- Read-only AgentsView session and tool-call data across the complete indexed date range.
- Current `project-docs` skill text and trigger corpus.
- Recoverable historical `project-docs` trigger descriptions from git; unknown versions stay
  explicitly unknown.
- Known owner corrections involving documentation routing.
- Prior July transcript regrade as a candidate source, not accepted ground truth.

## In Scope

- One skill: `project-docs`.
- Activation detection for the channels already demonstrated in AgentsView:
  - named skill/tool events; and
  - normalized installed-`SKILL.md` reads for Codex.
- Initial deduplication to a session x skill inventory, then split clear re-entry into separate
  deployment episodes before case-level interpretation.
- Separation of task use from skill editing, inspection, and meta-evaluation.
- A complete candidate manifest followed by a declared analysis corpus. Review all task-use
  deployments when tractable; otherwise select a varied corpus across harness, time, request shape,
  owner corrections, adjacent no-deployment work, and theory-challenging examples.
- One independently extracted case memo for every selected trajectory before corpus synthesis.
- An open-ended deployment debrief for each reviewed trajectory.
- A cross-case synthesis of recurring strengths, failure shapes, counterexamples, improvement
  hypotheses, supporting evidence, and unresolved questions.
- Descriptive counts only when they illuminate the observed corpus. No score or mandatory verdict
  is required.

## Method Source

Do not duplicate the analysis manual in this plan. The pilot uses the progressively disclosed
`skill-analysis` resources:

- `references/purpose-and-outcomes.md` for the learning contract;
- `references/corpus-assembly.md` for manifest, corpus, case-reader, and gap-fill mechanics;
- `references/deployment-debrief.md` for the one-trajectory prompt and its rationale; and
- `references/synthesis-and-interpretation.md` for the separate corpus-reader pass.

The plan defines this pilot's scope and stop conditions. The skill references define the reusable
method.

## Explicitly Out of Scope

- Evaluating PDM, Doppler, Context7, chat-history, or the rest of the skill estate.
- Claiming that `project-docs` caused better task outcomes.
- Current-versus-prior-versus-no-skill replay.
- A universal LLM grader or composite effectiveness score.
- Complete historical content hashes for every activation.
- PR, file-churn, or runtime aftermath tracking.
- A general skill dependency graph.
- Monthly scheduling, Letta, background listeners, or automatic skill mutation.
- Promotion of the new `skill-analysis` skill.

## Execution

### 1. Freeze the question and subject

- Record the current live and incubator `project-docs` hashes.
- Extract the current trigger description separately from the skill body.
- Identify only historical trigger versions that git can recover confidently.
- Record AgentsView coverage dates and missing harness/provider surfaces.

Output: a short run header with subject identity and corpus coverage.

### 2. Produce the activation population

- Add or adapt one read-only extractor under `agent-control-plane/tools/`.
- Query only `project-docs` activation candidates.
- Normalize Codex path escaping and remove repeated page reads.
- Mark editing/inspection/meta sessions separately from task use.
- Reconcile counts against known July results where the corpus overlaps.

Output: a complete candidate manifest with one row per detected session x skill inventory item,
plus an explicit deployment-episode split where a long session contains distinct task uses, and the
reproducible query/tool. The manifest is an inventory and navigation surface, not a set of
conclusions.

### 3. Produce a comparison sample

- Retrieve request neighborhoods before interpretation:
  1. explicit authority-document terminology;
  2. README/docs edits;
  3. status or information requests;
  4. operational tasks involving docs incidentally;
  5. requests near known owner corrections; and
  6. a small random documentation-oriented sample.
- Match no-fire requests by harness and approximate time when possible, but do not construct the
  sample from requests the evaluator already assumes represent a failure.
- Do not classify every historical documentation request.
- Keep requests whose relevance is unclear; boundary uncertainty is itself useful evidence.

Output: the declared analysis-corpus identifiers, selection rationale, and all discovered explicit
corrections relevant to the pilot.

Every selected row is tracked as `pending`, `extracted`, `excluded` with a reason, or `blocked`.
The sample is the declared analysis corpus; reports must distinguish it from the complete candidate
manifest.

### 4. Extract and debrief one trajectory at a time

- Give each case reader exactly one selected session and its bounded request-to-response window.
- Include the recoverable skill version, but no other case memos or cross-case theory.
- Ask the deployment-debrief questions as a coherent review, not a form to complete mechanically.
- Require one compact memo containing source identifiers, user goal, deployment point, directly
  observed actions/result/owner response, the open-ended debrief, competing interpretations,
  unknowns, and follow-up pointers.
- Complete or explicitly exclude every selected row before synthesis. Do not ask one agent to read
  or remember the whole raw corpus.
- Treat owner silence as unknown, not acceptance.

Output: one case memo per selected trajectory in a temporary run directory; only compact,
non-sensitive derived memos are candidates for `agent-control-plane`.

### 5. Give the assembled corpus to a separate synthesis agent

- Give the synthesis agent the candidate-manifest summary, completed case memos, and coverage notes;
  do not give it hundreds of raw transcripts.
- Group recurring themes without erasing counterexamples.
- Explain what agents understood about the skill, where it was deployed, how it appeared to affect
  the work, and what seems missing, vague, overspecific, helpful, or harmful.
- Use counts only as descriptions of the reviewed sample and always state how the sample was built.
- Propose the smallest trigger, body, example, or handoff changes supported by the trajectories.
- Convert strong real examples into candidate regressions, including examples that should continue
  to work and examples that expose a problem.
- State what remains unknown and what next observation would be most informative.
- If a coverage gap matters, send the requested session back through the one-trajectory case-reader
  step and then resynthesize.
- Give a second reviewer only the memos and source windows behind consequential proposed changes.
  Treat disagreement as another interpretation to investigate rather than a grading error.

Output in `agent-control-plane`:

- reproducible extraction logic;
- compact deployment debriefs and coverage limitations; and
- the cross-case lessons and improvement hypotheses.

Conditional output in `frozenSkillz` only if evidence supports a change:

- `project-docs` trigger wording;
- positive and negative trigger cases;
- tracker learning/status update; and
- one regression case tied to the real failure.

## Verification

- The extractor opens AgentsView read-only and performs no sync, import, recall, or prune action.
- Session x skill counts do not inflate repeated reads.
- Meta/evaluation sessions are excluded from task-use rates.
- A second reviewer challenges the examples most likely to drive a change, when such examples exist.
- Every important finding is traceable to reviewed trajectories rather than aggregate health or
  sentiment proxies.
- The synthesis preserves counterexamples, unknowns, and reviewer disagreement.
- Any reported rate includes its denominator and sampling stratum.
- Repository validation passes after any frozenSkillz change.

## Stop Conditions

- Do not force a skill change when the trajectories support competing explanations or too little
  variation. Report what was learned and what remains unresolved.
- Stop and fix the detector if overlapping July counts cannot be reconciled within explained corpus
  or normalization differences.
- Do not assign a historical version when only the current text is known.
- Do not proceed into causal-effectiveness claims or other skills during this plan.
- Complete the MVP when the deployment debriefs and cross-case lessons answer the core questions
  and any proposed skill change is grounded in real examples; automation is not part of completion.
