# Analysis: pionxzh/chatgpt-exporter

## Scope

- Selected artifacts: `source/README.md` raw-conversation export description and the
  source tree's export acquisition shape.
- Reason this scope is narrow enough: the sidecar needs only complete raw data and
  explicit failure behavior, not a browser UI or file-format product.
- Out-of-scope artifacts: all userscript UI, delete/archive actions, markdown/PDF
  rendering, and bundled `dist/` output.

## Rubric Scores

| Artifact | Type | Average | Recommendation |
|---|---|---:|---|
| Raw conversation export pattern | documentation-pattern | 3.4 | Adapt concept only |
| Browser userscript implementation | command/config | 2.6 | Discard for active use |

## Detailed Notes

### Raw conversation export pattern

| Dimension | Score | Rationale |
|---|---:|---|
| Purpose clarity | 5 | Explicitly exports conversation content. |
| Output contract | 3 | Raw mapping is useful, but completion integrity is not defined. |
| Reuse value | 4 | Full mapping acquisition is directly useful to organizer analysis. |
| Progressive disclosure | 3 | Readme and source are separated, but UI concerns dominate. |
| Safety/security risk | 2 | Browser-session and private-history access need stricter controls. |
| Portability | 2 | Userscript/browser-specific. |
| Testability/evaluability | 2 | No dedicated tests observed. |
| Maintenance burden | 2 | Undocumented endpoint drift risk. |
| Fit with frozenSkillz scope | 4 | Organizer history acquisition is in scope. |
| Authority flow | 4 | Raw mapping supports durable, inspectable source truth. |

## Summary Recommendation

- Recommended outcome: adapt concept only.
- Evidence: the snapshot documents per-conversation raw mapping acquisition but does
  not supply a safe, complete, authenticated synchronization contract.
- Open questions: live endpoint schema and authentication remain current-state checks.
