# Return, independent review, and learning

Use this reference after a Factory run is launched, resumed, blocked, or presented for review.

## Return evidence

For each completed or interrupted Dispatch, capture the smallest durable evidence that lets the originating conversation decide what happened:

- Factory mission/session link and correlation identifier, when available;
- base revision and resulting commit, PR, artifact, or explicit no-change result;
- validation command/output summary or a precise reason it could not run;
- whether the packet was followed, repaired once in scope, paused, or blocked;
- the next decision and who owns it.

Do not call a run successful because planning completed, a process exited, or a worker claims success. The Mission closes only against the packet's acceptance evidence.

## Cross-dispatch for review

An independent review is another Dispatch, not an informal afterthought. Before sending it:

1. choose a distinct existing Codex or ChatGPT conversation whose role can independently assess the work;
2. provide the desired outcome, scope, base/result links, validation evidence, and the precise review question;
3. ask for a concrete verdict: accepted, findings, missing evidence, or needs human decision;
4. link the review thread and return summary to the Dispatch and Mission.

The reviewer does not become an execution authority. A disagreement is evidence to record and resolve, not a reason to silently relaunch work.

## Repair boundary

One repair Dispatch is permitted only when it fixes a failure inside the approved outcome, scope, target, authority, and validation plan. It must name the failing evidence and the narrow correction. A second repair, changed target, broader scope, changed permission/autonomy, deployment/data action, policy issue, or unavailable Notion control plane pauses for the user.

## Learning policy

Classify failures as one of: packet ambiguity, stale source/base, target/environment, worker execution, validation/observability, review disagreement, or policy/hook failure.

- One reproducible outcome creates an **Observed** Learning row.
- Three independent comparable cases can move it to **Candidate** with the cited Dispatches and a proposed narrow change.
- A candidate needs a regression fixture and a passing holdout before **Awaiting approval**.
- Only human signoff may promote a change into the frozen skill or an execution adapter.
- A safety/data breach requires human review and disables the relevant future adapter path until that decision is made.

No learning row edits the skill, changes a hook, launches a run, or schedules background work by itself.
