# Forensic Evaluation: Live-Only Intake Bias

## Claim

- Claim being evaluated: frozenSkillz’s external-intake instructions incorrectly made a sandboxed
  live evaluation the only acceptable evidence before recommending a large pattern.
- Candidate artifact: `plugins/frozen-skills/skills/external-skill-intake/`
- Decision this finding informs: update the intake contract to accept live or forensic evaluations.

## Evidence

| Field | Value |
|---|---|
| Source | Pre-change active `SKILL.md` and `docs/workflows/external-skill-intake.md` |
| Source type | instruction source plus real Codex interaction |
| Captured | 2026-07-23 |
| Version or revision | frozenSkillz `origin/main` at `6f9b10f` |
| Harness | Codex CLI 0.145.0 |
| Observed behavior | The reviewing agent repeatedly reframed a requested forensic investigation as needing live evaluations or unpublished metrics. |
| Operator correction | The operator clarified that evidence gathering was sufficient and that the work was forensic. |
| Reproduction details | The source required “at least one sandboxed live eval” and offered no forensic evidence mode. |

## Assessment

- Status: fixed on `docs/superpowers-forensic-evaluation`.
- Corroborating evidence: direct source wording and the agent’s repeated behavior in the review session.
- Contradicting evidence: none found in the pre-change contract.
- Confidence: strong.
- Supports: adding an explicit forensic mode and claim boundary.
- Does not support: eliminating live comparisons when claiming measured improvement.

## Reviewer Notes

The correction changes the positive recipe: choose the evidence mode that matches the question.
Comparative improvement remains a live-evaluation claim; real-agent behavior can be reconstructed
forensically without manufacturing another run.
