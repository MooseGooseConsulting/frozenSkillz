# Decision Log: pionxzh/chatgpt-exporter

## Decision

- Date: 2026-08-16
- Reviewer: Codex
- Artifact paths: `source/README.md`, `source/src/`
- Outcome: adapt concept only
- Affected frozenSkillz paths: `tools/chatgpt_history_sync/`,
  `deployments/chatgpt-history-sync/`, and the organizer's ChatGPT adapter reference.

## Evidence

- Inventory summary: an MIT browser userscript with raw conversation export support,
  but no organizer-specific schema, sync ledger, scheduler, or automated tests.
- Rubric score summary: raw export pattern 3.4; direct userscript implementation 2.6.
- Evaluation mode and evidence paths: forensic source review recorded in
  `evals/forensic/2026-08-16-export-completion-pattern.md`.
- Safety notes: preserve authentication boundaries; fail hard on expiry, incomplete
  snapshot, hash mismatch, and endpoint drift.
- Maintenance notes: repository-owned Python code limits browser/userscript coupling.

## Rationale

The useful idea is raw mapping acquisition with explicit per-conversation capture.
The upstream UI and endpoint behavior do not meet the required immutable snapshot,
SQLite revision, scheduling, and failure-contract requirements.

## Follow-Up

- Owner: Codex
- Due date or trigger: complete sidecar implementation and controlled live export.
- Required validation: unit suite, manifest reconciliation, scheduler rendering, and
  controlled export/import when authenticated access is available.
