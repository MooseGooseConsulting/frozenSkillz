# Plan: Skill-Deployment Learning Follow-through

Status: active only for evidence-supported wording changes from the 2026-08 historical study.

## Up front

- **What:** Apply the historical study’s narrow findings to `project-docs` and the PDM/Doppler
  handoff, then learn from later ordinary deployments.
- **Why:** The point is better guidance in real work, not an evaluation platform.
- **How:** Keep corpus tooling in `agent-control-plane`, edit only the demonstrated failure surface
  in `frozenSkillz`, and leave deferred research actually deferred.
- **Result:** A clean, reviewable skill change with a clear reason and no invented proof of lift.

## Current sequence

1. Preserve the pre-change historical baseline while the census and debriefs are assembled.
2. Update `project-docs` only where the study found overreach: deliverable-based entry, no
   README/operational/incidental-doc inference, topology grounded in existing authority, and clear
   proposed-versus-applied reporting.
3. Update PDM/Doppler only where the study found a boundary problem: trusted opaque PDM launchers
   need no Doppler load; direct credential, secret-store, or injection work does. Native PVE/PBS
   remains a deliberate capability/recovery route.
4. Validate the read-only manifest and selection tooling in `agent-control-plane`; validate the
   frozen skill text, trigger examples, manifests, and exact diff here.
5. Reconcile the existing routing PR after the study: keep the supported narrow changes, remove or
   revise unsupported doctrine, and do not merge an unreviewed or stale conclusion.
6. Let later ordinary deployments supply the next corpus. Revisit only when enough relevant cases
   exist or an owner correction exposes a new question.

## Explicitly deferred

- Current/prior/no-skill comparisons, fresh-agent A/B tests, and third-party model calls.
- A composite skill score, universal grading rubric, hard trigger gates, or automatic promotion.
- Scheduled monitoring, listeners, automatic mutations, and corpus-wide raw-chat processing.

If a future question genuinely requires a controlled experiment, it needs a separate user-approved
proposal: exact decision, cost, model/provider, corpus, safety boundary, and stop condition. It is
not a hidden next step of this plan.
