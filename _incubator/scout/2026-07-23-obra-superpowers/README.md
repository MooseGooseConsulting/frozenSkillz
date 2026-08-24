# obra/superpowers Forensic Evaluation

This scout preserves and reviews Superpowers as an external agent-skill framework. The source tree
is evidence only; do not edit or promote files directly from `source/`.

## Provenance

- Source: <https://github.com/obra/superpowers>
- Release: `v6.1.1`
- Commit: `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Release date: 2026-07-02
- Snapshot date: 2026-07-23
- License: MIT
- Reviewer: Codex with operator review
- Installed Codex used for local inspection: `codex-cli 0.145.0`

The snapshot was produced from `v6.1.1` with `git archive`; the two paths excluded by upstream
archive rules (`.opencode/INSTALL.md` and `.opencode/plugins/superpowers.js`) were restored from
the same tag. All 172 path modes and blob IDs were then compared with the tag, so local
plugin-cache changes and `.git` metadata are excluded. `source-tree.tsv` persists the expected Git
mode and blob ID for every source path and is checked by the repository test suite.

## Evaluation Mode

This is a **forensic evaluation**. It inspects current source, repository history, real-agent issue
reports, reproductions, maintainer responses, fix commits, tests, and release notes. No synthetic
baseline comparison has been run, and this dossier does not claim measured improvement over an
agent without Superpowers.

Findings distinguish current behavior from fixed or historical behavior. A report without a
transcript or corroborating artifact remains useful but receives lower confidence.

## Review Progress

| Skill | Status | Grade |
|---|---|---|
| `brainstorming` | reviewed 2026-07-23 | B- (moderate confidence) |
| `dispatching-parallel-agents` | reviewed 2026-07-23 | B- (strong confidence for observed Codex behavior; moderate cross-harness) |
| Remaining 12 skills | pending one-at-a-time review | not graded |

See `inventory.md` for the complete doctree, `analysis.md` for grades and rationale,
`evals/forensic/` for source-level findings, and `decisions.md` for packaging status.
