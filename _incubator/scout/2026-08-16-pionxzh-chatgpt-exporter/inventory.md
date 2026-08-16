# Inventory: pionxzh/chatgpt-exporter

## Provenance

- Source URL: https://github.com/pionxzh/chatgpt-exporter
- Commit: `45aca51d8783ae460c1a18611fce12a87841a76b`
- Import date: 2026-08-16
- License: MIT
- Reviewer: Codex
- Scout path: `_incubator/scout/2026-08-16-pionxzh-chatgpt-exporter/`

## Artifact Counts

| Type | Count | Notable paths |
|---|---:|---|
| userscript/export UI | 1 | `source/src/` |
| config/package | 6 | `source/package.json`, Vite/TypeScript configuration |
| template/formatters | 1+ | `source/src/` export format modules |
| documentation pattern | 1 | `source/README.md` |
| automated tests | 0 observed | no dedicated test directory in snapshot |

## Risks

- Secret surfaces: browser-session authentication and private conversation content.
- Tool assumptions: a GreasyFork/browser userscript and undocumented ChatGPT backend
  endpoint shape.
- External dependencies: browser DOM, session cookies, endpoint stability, pnpm/Vite.
- Provenance: MIT source snapshot; upstream is a general export UI, not an organizer
  synchronization service.
- Generated/low-quality material: built `dist/` content is not a design authority.

## Initial Scope Recommendation

- Evaluate: full raw-conversation acquisition and visible export-completion ideas.
- Defer: browser UI, deletion/archive controls, and format renderers.
- Discard: direct userscript packaging and its endpoint assumptions.
- Needs more evidence: whether current ChatGPT endpoints and authentication can support
  the required controlled live export.
