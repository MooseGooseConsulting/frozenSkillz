# Inventory: obra/superpowers v6.1.1

## Provenance

- Source URL: <https://github.com/obra/superpowers>
- Commit or version: `v6.1.1` / `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Import date: 2026-07-23
- License: MIT
- Reviewer: Codex with operator review
- Scout path: `_incubator/scout/2026-07-23-obra-superpowers/`

## Artifact Counts

The snapshot contains 172 files. Counts below classify primary artifacts; support files are not
double-counted merely because they could fit more than one category.

| Type | Count | Notable paths |
|---|---:|---|
| skill | 14 | `skills/*/SKILL.md` |
| agent | 0 | No standalone agent definitions |
| command | 0 | Legacy slash commands are absent in v6.1.1 |
| hook | 4 | `hooks/hooks.json`, `hooks/hooks-cursor.json`, `hooks/session-start`, `hooks/run-hook.cmd` |
| config | 7 | Six marketplace/plugin JSON manifests plus `gemini-extension.json` |
| template/prompt | 6 | Brainstorm/spec, plan, code-review, SDD, and visual-frame support |
| eval-case | 13 | Nine explicit-skill prompts plus four systematic-debugging pressure/academic cases |
| documentation-pattern | 1 | The cross-skill development methodology and handoff chain |

Additional file counts: 82 Markdown, 37 shell, 13 JSON, 10 JavaScript, and one CommonJS file.

## Skill Doctree

| Skill | Files | Supporting intent |
|---|---:|---|
| `brainstorming` | 8 | Spec-review prompt and optional browser companion server/scripts |
| `dispatching-parallel-agents` | 1 | Standalone parallel-dispatch guidance |
| `executing-plans` | 1 | Standalone plan-execution workflow |
| `finishing-a-development-branch` | 1 | Standalone finish/merge/cleanup workflow |
| `receiving-code-review` | 1 | Standalone review-response discipline |
| `requesting-code-review` | 2 | Skill plus reviewer prompt |
| `subagent-driven-development` | 6 | Implementer/reviewer prompts and three workspace/review scripts |
| `systematic-debugging` | 11 | Root-cause, defense, waiting, polluter helper, and pressure cases |
| `test-driven-development` | 2 | Skill plus testing anti-patterns reference |
| `using-git-worktrees` | 1 | Standalone isolation workflow |
| `using-superpowers` | 4 | Entrypoint plus Codex, Pi, and Antigravity tool mappings |
| `verification-before-completion` | 1 | Standalone completion-evidence gate |
| `writing-plans` | 2 | Skill plus plan-review prompt |
| `writing-skills` | 7 | Authoring/testing references, graph tooling, and examples |

## Risks and Assumptions

- The methodology uses strong mandatory language that can conflict with higher-priority repository
  or harness instructions if agents fail to honor instruction precedence.
- Some skills dispatch subagents and require harness-specific multi-agent support.
- The brainstorming companion starts a local Node service only when invoked; it has a broader attack
  and maintenance surface than the Markdown-only skills.
- Several helpers are POSIX shell scripts. Platform references adapt concepts but do not make every
  bundled executable natively PowerShell-compatible.
- Skill-behavior evaluations moved to a separate upstream repository and are not present in this
  snapshot. In-tree tests primarily cover plugin code, scripts, packaging, and selected triggers.

## Initial Scope Recommendation

- Evaluate: all 14 skills, one at a time, starting with `brainstorming`.
- Defer: repo-wide adoption or promotion decisions until the individual reviews are complete.
- Discard: nothing at intake time.
- Needs more evidence: current real-agent behavior for each unreviewed skill and any claim of
  comparative improvement.
