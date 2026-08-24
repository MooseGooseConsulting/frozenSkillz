# Forensic Evaluation: Brainstorming Against Real-Agent Evidence

## Claim

- Claim being evaluated: Superpowers `brainstorming` reliably establishes a safe, evidence-grounded
  design handoff across supported coding-agent harnesses.
- Candidate artifact: `source/skills/brainstorming/`
- Decision this finding informs: whether to adopt, adapt, defer, or discard the skill.

## Evidence Set

| Source | Type | Captured | Version or revision | Harness, model, and OS | Status | Result |
|---|---|---|---|---|---|---|
| [Commit `7f2ee61`](https://github.com/obra/superpowers/commit/7f2ee614b6d65af34bd6b689f48f79f742a9d43c) | maintainer commit | 2026-07-23 | `7f2ee61`; pre-4.3 behavior | Claude harness; model and OS unknown | fixed | Agents skipped or collapsed the described process; hard gates added |
| [Issue #565](https://github.com/obra/superpowers/issues/565) | reproduction + maintainer confirmation | 2026-07-23 | regression from `7f2ee61` | Claude harness; model and OS unknown | fixed | Review gate removed and plan/design paths collided |
| [Issue #1080](https://github.com/obra/superpowers/issues/1080) | source audit + one transcript summary | 2026-07-23 | Superpowers 5.0.7 | Claude Code; model and OS unknown | historical | Worktree skill was not invoked; support later rewritten |
| [Commits `cb5bb88`](https://github.com/obra/superpowers/commit/cb5bb885fd7cf00a1820f20d922df06ec02d4bed) and [`7fbae02`](https://github.com/obra/superpowers/commit/7fbae0252fe90778ce0c06fde3bf5f87aa396fc2) | code, security review, tests | 2026-07-23 | companion before Superpowers 6.1.1 | harness, model, and OS not applicable | fixed | Missing auth and six named integration defects; fixed with regression coverage |
| [Issue #939](https://github.com/obra/superpowers/issues/939) | reproduction + workaround | 2026-07-23 | Superpowers 5.0.6 | Claude Code; model and OS unknown | unresolved | Concrete default path overrode project instruction; still structurally relevant |
| [Issue #1246](https://github.com/obra/superpowers/issues/1246) | multiple independent reports | 2026-07-23 | Superpowers versions unknown | Claude Code and Codex; models and OS unknown | unresolved | Spec/plan commits on primary branch and excessive commit friction |
| [Issue #1266](https://github.com/obra/superpowers/issues/1266) | repeated-behavior report | 2026-07-23 | Superpowers version unknown | harness, model, and OS unknown | unresolved | Recommendations changed after deeper analysis; no transcripts supplied |
| [Issue #1222](https://github.com/obra/superpowers/issues/1222) | cross-harness report | 2026-07-23 | Superpowers versions unknown | Pi, Codex, and Claude Code; models and OS unknown | unresolved | Over-triggering alleged; maintainer requested unavailable transcripts |
| [Issue #1100](https://github.com/obra/superpowers/issues/1100) | screenshot + confirmations | 2026-07-23 | Superpowers 5.0.7 era | Codex app; model and OS unknown | unresolved | Output intermittently collapsed and easy to miss |
| [Issue #975](https://github.com/obra/superpowers/issues/975) | source-confirmed behavior | 2026-07-23 | Superpowers version unknown | companion runtime; model and OS not applicable | current | Persistent state placed under project `.superpowers/` |

## Assessment

- Status: unclear. The universal reliability claim spans fixed historical defects plus current,
  unresolved, and weakly evidenced concerns; no single status describes every condition.
- Corroborating evidence: current v6.1.1 source, issue reproductions, maintainer comments, fix commits,
  and in-tree companion tests.
- Contradicting evidence: successful users and the project’s continued adoption show the workflow can
  be useful, but no evidence inspected here establishes universal reliability.
- Confidence: moderate.
- Supports: B- editorial grade, selective adaptation, continued forensic review.
- Does not support: a measured improvement claim, a current failure rate, or wholesale rejection.

## Reviewer Notes

The strongest evidence concerns specific regressions corroborated by fixes. Reports without
transcripts remain labeled limited. Historical defects inform maintenance quality but are not
counted as current defects when the pinned source contains the fix.
