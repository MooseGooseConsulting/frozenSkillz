# Plan: Skill Analysis MVP — `project-docs` Trigger Precision

Status: proposed; not started.

## Up Front

- **What:** Determine whether `project-docs` fires for the right requests and stays quiet for the
  wrong ones.
- **Why:** Unnecessary loads add context and can take over ordinary README, documentation, status,
  or operational work.
- **How:** Compare real fired sessions with similar no-fire requests, label the trigger decision and
  observed use, then make one trigger verdict.
- **Result:** Keep, narrow, or broaden the trigger—with real failure prompts added as regressions.

## How This Improves the Existing Skill

- False positive → narrow the description and add the real prompt as a negative trigger case.
- False negative → broaden the description and add the real prompt as a positive trigger case.
- Correct activation but ignored guidance → revise the skill body, not the trigger.
- Correct and useful activation → preserve the behavior as a regression.
- Ambiguous or weak evidence → make no skill change and report what evidence is missing.
- After a change → rerun the regression and inspect the next real `project-docs` opportunities
  before claiming improvement.

## Goal

Prove that `skill-analysis` can answer one useful question:

> Does `project-docs` activate for the right requests, especially authority-document work, while
> staying quiet for README edits, ordinary documentation, status checks, and operational tasks?

This MVP evaluates trigger appropriateness. It does not attempt to prove the causal value of the
whole skill, grade every skill, or build recurring automation.

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
- Deduplication to one session x skill activation.
- Separation of task use from skill editing, inspection, and meta-evaluation.
- A bounded transcript sample:
  - every explicit owner correction found for `project-docs`;
  - up to 25 fired sessions, stratified across harness and time; and
  - up to 25 comparable no-fire documentation requests.
- Five labels per reviewed session:
  - should `project-docs` have activated? yes / no / ambiguous;
  - did it activate? yes / no / uncertain;
  - did its guidance materially affect behavior? yes / no / indeterminate;
  - owner response: accepted / corrected / no verdict; and
  - failure class: false positive / false negative / ignored load / useful / unrelated.
- A trigger verdict: keep / narrow / broaden / insufficient evidence.

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

Output: a compact machine-readable activation table in `agent-control-plane` or a temporary run
directory, plus the reproducible query/tool.

### 3. Produce the opportunity sample

- Search real user requests for authority-document work and nearby negative cases.
- Match no-fire requests by harness and approximate time when possible.
- Do not classify every historical documentation request.
- Preserve `ambiguous` rather than forcing a yes/no label.

Output: at most 50 sampled session identifiers plus all discovered explicit corrections.

### 4. Label bounded trajectories

- Read only the request, activation window, materially relevant actions, observable result, and
  next substantive owner response.
- Use a second independent reviewer for at least ten mixed cases.
- Compare reviewer labels; route consequential disagreements to the owner instead of averaging.
- Treat owner silence as `no verdict`.

Output: compact labels and a disagreement list in `agent-control-plane`.

### 5. Decide only the trigger question

- Report counts and explicit sample sizes for true positives, true negatives, false positives,
  false negatives, ambiguous cases, and meta-use exclusions.
- Do not publish a percentage without its numerator, denominator, and sampling method.
- State whether the evidence supports keeping, narrowing, or broadening the trigger.
- Convert confirmed false positives and false negatives into candidate trigger cases.

Output in `agent-control-plane`:

- reproducible extraction logic;
- compact labels and coverage limitations; and
- the analysis conclusion.

Conditional output in `frozenSkillz` only if evidence supports a change:

- `project-docs` trigger wording;
- positive and negative trigger cases;
- tracker verdict; and
- one regression case tied to the real failure.

## Verification

- The extractor opens AgentsView read-only and performs no sync, import, recall, or prune action.
- Session x skill counts do not inflate repeated reads.
- Meta/evaluation sessions are excluded from task-use rates.
- At least ten mixed cases receive independent labels.
- Every reported rate includes its denominator and sampling stratum.
- Any skill change is traceable to confirmed cases, not aggregate health or sentiment proxies.
- Repository validation passes after any frozenSkillz change.

## Stop Conditions

- Stop with `insufficient evidence` if fewer than ten task-use fires or ten usable no-fire
  opportunities can be recovered.
- Stop and fix the detector if overlapping July counts cannot be reconciled within explained corpus
  or normalization differences.
- Do not assign a historical version when only the current text is known.
- Do not proceed into causal-effectiveness claims or other skills during this plan.
- Complete the MVP when the `project-docs` trigger verdict and its limitations are reviewable;
  automation is not part of completion.
