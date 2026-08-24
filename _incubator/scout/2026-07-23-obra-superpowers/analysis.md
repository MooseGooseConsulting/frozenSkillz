# Analysis: obra/superpowers v6.1.1

## Scope

- Selected artifacts: `skills/brainstorming/` and `skills/dispatching-parallel-agents/`.
- Reason: the operator requested a one-at-a-time doctree, intent, evidence, and letter-grade review.
- Out of scope for this pass: grades for the remaining 12 skills and any repo-wide adoption claim.

## Grade Meaning

Letter grades are evidence-backed editorial assessments, not unpublished benchmark results. Each
grade combines the frozenSkillz rubric, current source, documented real-agent behavior, maintenance
response, and unresolved risk. Confidence describes the evidence base supporting the grade.

## Review Status

| Artifact | Type | Rubric average | Letter grade | Confidence | Recommendation |
|---|---|---:|---:|---|---|
| `skills/brainstorming/` | skill | 4.0/5 | B- | moderate | Incubate; mine patterns only after the full review |
| `skills/dispatching-parallel-agents/` | skill | 3.6/5 | B- | strong for observed Codex behavior; moderate cross-harness | Prioritize adaptation; retain the independence gate and add explicit preflight, isolation, and lifecycle contracts |

## `brainstorming`

### Intent and Doctree

The skill turns an idea into an approved design and written specification before planning or
implementation. Its required flow is context inspection, one-at-a-time clarification, alternative
comparison, incremental design approval, spec creation, self-review, written-spec review, and
handoff to `writing-plans`.

```text
brainstorming/
├── SKILL.md
├── spec-document-reviewer-prompt.md
├── visual-companion.md
└── scripts/
    ├── frame-template.html
    ├── helper.js
    ├── server.cjs
    ├── start-server.sh
    └── stop-server.sh
```

The support tree is not passive documentation. It includes an optional authenticated local
HTTP/WebSocket companion for diagrams and comparisons. It should start only after explicit consent
and only when a visual question would benefit from it.

### Rubric Scores

| Dimension | Score | Rationale |
|---|---:|---|
| Purpose clarity | 5 | Explicit design-before-implementation purpose |
| Activation or invocation clarity | 4 | Strong trigger, but its universal scope risks over-triggering |
| Output contract | 5 | Defines conversation, spec, review, and handoff artifacts |
| Reuse value | 4 | Broadly useful for substantial design work; heavy for bounded changes |
| Progressive disclosure or structure | 5 | Core workflow routes companion and review detail to support files |
| Safety/security risk | 4 | Companion is opt-in and hardened, but still adds a local service surface |
| Portability | 3 | Cross-harness prose exists; companion and helpers retain shell/runtime assumptions |
| Testability/evaluability | 4 | Server and trigger tests exist; behavior eval corpus is external to the release |
| Maintenance burden | 3 | Eight-file companion and cross-harness behavior require active maintenance |
| Fit with frozenSkillz scope | 4 | Directly relevant methodology, but not suitable for wholesale adoption yet |
| Trigger clarity | 4 | Creative-work trigger is unmistakable |
| Negative triggers | 2 | It explicitly rejects a small-task exemption instead of defining exclusions |
| Reference and template routing | 5 | Supporting material has clear entrypoints and conditional loading |
| Gate quality before action | 4 | Strong approval gates; branch/output-location ordering remains problematic |

Average: **4.0/5**. The letter grade is **B-**, rather than mapping mechanically to the numeric
average, because unresolved operational problems affect normal use in Codex and Git repositories.

### Forensic Findings

| Finding | Status | Confidence | Evidence |
|---|---|---|---|
| Models skipped design or collapsed it into one response before hard gates were added | fixed | moderate | [`7f2ee61`](https://github.com/obra/superpowers/commit/7f2ee614b6d65af34bd6b689f48f79f742a9d43c) describes three tested variants but publishes no result table |
| Written-spec review was skipped and planning could overwrite the design | fixed | strong | [#565](https://github.com/obra/superpowers/issues/565), maintainer confirmation, and [`ec3f7f1`](https://github.com/obra/superpowers/commit/ec3f7f1027a61629fc67270a9a5ccb21a432a194) |
| Brainstorming-to-worktree handoff was structurally inconsistent | historical | moderate | [#1080](https://github.com/obra/superpowers/issues/1080) includes a real session; maintainer says worktree support was rewritten in 5.1 |
| Companion initially exposed content/events without authentication and later integration contained real defects | fixed | strong | [`cb5bb88`](https://github.com/obra/superpowers/commit/cb5bb885fd7cf00a1820f20d922df06ec02d4bed) and [`7fbae02`](https://github.com/obra/superpowers/commit/7fbae0252fe90778ce0c06fde3bf5f87aa396fc2) with named regressions and test counts |
| Concrete default spec path can win over repository output-path instructions | unresolved | moderate | [#939](https://github.com/obra/superpowers/issues/939) has reproduction and workaround; v6.1.1 still places the concrete default before its override note |
| Spec commit can happen before a feature branch/worktree decision | unresolved | strong | Current flow says write and commit before handoff; [#1246](https://github.com/obra/superpowers/issues/1246) contains multiple independent reports |
| Recommendations may be shallow until challenged | unresolved | limited | [#1266](https://github.com/obra/superpowers/issues/1266) reports repeated flips but provides no transcripts |
| Skill may trigger too broadly | unresolved | limited | [#1222](https://github.com/obra/superpowers/issues/1222) names several harnesses but reporter could not provide transcripts |
| Codex can collapse outputs under `Worked for...` | unresolved | moderate | [#1100](https://github.com/obra/superpowers/issues/1100) includes screenshot evidence and multiple Codex confirmations |
| Persistent companion state defaults inside the project when `--project-dir` is used | current | strong | Current script and [#975](https://github.com/obra/superpowers/issues/975) agree on `.superpowers/brainstorm/` behavior |

### Assessment

The skill has a clear, valuable intent and a maintainership history that responds to concrete
failures. Its strongest elements are explicit approval gates, one-question-at-a-time clarification,
alternative comparison, and a written decision artifact.

It does not earn an A-range grade because the current contract remains overbroad, orders spec
commits before isolation decisions, gives a concrete output path more salience than repository
authority, and does not require an evidence basis before recommending an option. The optional
companion is substantially hardened but materially raises complexity and maintenance cost.

## `dispatching-parallel-agents`

### Intent and Doctree

The skill teaches a controller to identify genuinely independent problem domains, give each worker
a narrow and self-contained brief, launch the workers concurrently, and integrate their results
under a full-suite verification gate. It is intentionally a fan-out/fan-in pattern, not a
coordinated agent-team workflow.

```text
dispatching-parallel-agents/
└── SKILL.md
```

There are no bundled references, templates, scripts, or tests. Platform behavior is expected to
come from the separate `using-superpowers` harness references.

### Rubric Scores

| Dimension | Score | Rationale |
|---|---:|---|
| Purpose clarity | 5 | The independent-domain fan-out/fan-in purpose is explicit |
| Activation or invocation clarity | 3 | Frontmatter says 2+ tasks while the body says 3+ failing files |
| Output contract | 4 | Requires a root-cause/change summary and integration checks, but no lifecycle/status record |
| Reuse value | 5 | Independent investigation and research fan-out are broadly reusable |
| Progressive disclosure or structure | 3 | Self-contained, but 185 lines repeat negative triggers, benefits, and the same example |
| Safety/security risk | 3 | Rejects shared state, but lacks capability, authorization, resource-isolation, and cleanup gates |
| Portability | 2 | Harness-neutral prose depends on adapters whose Codex discovery, isolation, dispatch-grouping, and lifecycle mappings remain incomplete or version-sensitive |
| Testability/evaluability | 3 | External transcript tooling makes the behavior manually inspectable, but the candidate ships no linked, repeatable behavior-eval result |
| Maintenance burden | 3 | One file is simple, but tool semantics and per-harness lifecycle behavior drift underneath it |
| Fit with frozenSkillz scope | 5 | Directly addresses reusable multi-agent coordination |
| Trigger clarity | 3 | Independence is clear; the 2-versus-3 threshold is not |
| Negative triggers | 5 | Related failures, exploration, full-context work, and shared state are explicitly excluded |
| Reference and template routing | 2 | No local routing points to harness capability, isolation, or cleanup guidance |
| Gate quality before action | 4 | Independence and interference gates are strong, but capability and operating-surface checks are absent |

Average: **3.6/5**. The revised letter grade is **B-**. Direct Codex transcripts show that the core
pattern produces real concurrent work and useful synthesis, while also exposing missing preflight,
context, dispatch-grouping, and lifecycle contracts. This is an editorial grade, not a measured
comparison with sequential work. The workflow's importance in this environment is higher than the
artifact-only rubric average: observed utility raises the editorial grade without crediting the
candidate for evaluator infrastructure that it does not ship.

### Forensic Findings

| Finding | Status | Confidence | Evidence |
|---|---|---|---|
| The 2+ frontmatter trigger conflicts with the 3+ body threshold | unresolved | strong | Current v6.1.1 source and open [#948](https://github.com/obra/superpowers/pull/948) agree on the one-line defect |
| The skill omitted the same-response mechanic needed for parallel tool dispatch | unresolved | strong for Codex | [#1470](https://github.com/obra/superpowers/pull/1470) records a sequential session and v6.1.1 adds the instruction; a current local Codex v6.1.1 transcript still serialized three spawns across separate call results, although the children genuinely overlapped |
| An older direct Codex use produced successful two-agent and four-agent fan-outs | historical | strong | AgentsView session `codex:019d800f-ad35-79f1-9fcf-c458d77fa2d0`: the skill was read at ordinal 309; two children overlapped for 63.768 seconds and four later children overlapped for 53.059 seconds; the parent synthesized both batches into concrete outputs |
| A current v6.1.1 Codex use achieved concurrency but dispatched before a shared authority preflight | current | strong | AgentsView session `codex:019f8eb1-4e84-7652-a5ae-c4262784973b`: three `fork_turns: none` workers overlapped for 30.828 seconds, then all were interrupted after the parent discovered a repository governance gate that should have been checked before fan-out |
| High-value Codex workflows repeatedly succeed with the same pattern even without attributable skill invocation | current | strong for behavior; limited for causality | AgentsView session `codex:019f8cf4-aab6-7693-9ecb-7ded9e04b1c1` used independent research, allowlisted implementation, and reviewer lanes; the reviewer found a high-severity state-machine defect, the parent corrected it, expanded passing tests, performed live verification, and published PR #93 |
| Context isolation is required but not operationally mapped for Codex history/fork controls | current | strong | Current skill and Codex adapter contain the guarantee but no history-control mapping |
| Codex capability discovery guidance can falsely conclude that subagents are unavailable | unresolved | moderate | [#1633](https://github.com/obra/superpowers/issues/1633) was closed after ambiguity, while open [#1662](https://github.com/obra/superpowers/pull/1662) records deferred discovery in Codex Desktop |
| Completed Codex agents can retain concurrency slots after result consumption on some runtime versions | unresolved | strong | [#1927](https://github.com/obra/superpowers/issues/1927) cites Codex v1 source and open [#1982](https://github.com/obra/superpowers/pull/1982) adds a neutral release step; Codex v2 may expose no close operation |
| Parallel work can collide on worktree-local ports, databases, or files | current | moderate | [#597](https://github.com/obra/superpowers/issues/597) confirms the collision class; maintainers assign environment isolation to project instructions |
| Development workers sometimes stopped to ask permission despite being dispatched to implement | unclear | limited | [#473](https://github.com/obra/superpowers/issues/473) reports one paired real-world example; maintainer attributes it to harness behavior and no transcript is preserved |
| The dated “time of one” and zero-conflict success story is not auditable in the release | current | strong | v6.1.1 and current `main` contain no linked transcript or run artifact; merged-to-`dev` [#1934](https://github.com/obra/superpowers/pull/1934) removes the social-proof recap but is not yet released |

### Codex Fit and Settings

The v6.1.1 Codex reference explicitly recommends:

```toml
[features]
multi_agent = true
```

That setting is already enabled on the reviewed Codex installation, so this skill review recommends
**no additional Codex setting change**. Do not treat the setting alone as proof that dispatch is
available: newer Codex surfaces may expose agents by default or through deferred tool discovery,
and the current session's actual tool surface remains authoritative.

The more important adaptation is behavioral: request explicit subagent authority, choose a
history/fork policy instead of assuming isolation, preserve file and resource boundaries, consume
results, and release workers only when the active harness provides and requires that lifecycle.

### Assessment

The strongest reusable idea is the pre-dispatch independence test. The focused prompt structure and
post-integration full-suite check are also worth retaining. Those elements make the skill materially
better than an undisciplined “spawn several agents” instruction.

The combined transcript evidence moves the editorial grade into the B range. Direct attributable
runs demonstrate concurrent child work and useful synthesis. Separately, an implicit behavioral
match demonstrates reviewer value and successful integration for the broader pattern, but is not
credited causally to this skill. The current file stays at B- because it contradicts itself on
activation, asserts isolation without a portable mechanism, omits a shared authority/capability
preflight, relies on version-sensitive discovery and lifecycle behavior, and presents an unlinked
upstream recap as evidence of speed and conflict-free integration. Agent Teams are not counted
against it: peer coordination is a different workflow, tracked separately upstream.

## Summary Recommendation

- Recommended outcome: prioritize an adapted Codex-oriented version after the suite review; do not import wholesale.
- Potential concepts to adapt: evidence-aware design gates, incremental user approval, explicit
  separation between design and implementation planning, independent-domain fan-out, focused
  worker briefs, controller-owned synthesis, and integrated verification.
- Open questions: review the remaining 12 skills and determine whether the methodology works better as
  selected independent skills or as a tightly coupled suite.
