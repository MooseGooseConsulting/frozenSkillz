# Forensic Evaluation: export-completion-pattern

## Claim

- Claim being evaluated: upstream supports fetching raw conversation content that can
  inform a complete organizer export.
- Candidate artifact: `source/README.md`
- Decision this finding informs: adapt raw capture only, not the userscript itself.

## Evidence

| Source URL or path | Type | Captured | Version or revision | Harness, model, and OS | Status | Observed behavior and reproduction details |
|---|---|---|---|---|---|---|
| `source/README.md` | documentation | 2026-08-16 | `45aca51` | browser userscript, unknown, unknown | current | Documents raw conversation endpoint content and export of official `conversations.json`. |
| `source/package.json` | config | 2026-08-16 | `45aca51` | TypeScript/Vite userscript | current | Confirms a browser-extension/userscript delivery shape rather than a local sync service. |

## Assessment

- Status: current for the captured upstream revision; endpoint behavior itself is unresolved.
- Corroborating evidence: README and source layout agree on browser-oriented acquisition.
- Contradicting evidence: no upstream automated test proves snapshot completeness or current endpoint stability.
- Confidence: moderate.
- Supports: raw mappings and official export archives are useful source inputs.
- Does not support: endpoint stability, unattended authentication, or direct active import.
