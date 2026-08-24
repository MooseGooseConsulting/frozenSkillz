# Forensic Evaluation: Dispatching Parallel Agents Against Real-Agent Evidence

## Claim

- Claim being evaluated: Superpowers `dispatching-parallel-agents` reliably turns independent work
  into safe, portable, genuinely concurrent agent execution and integration.
- Candidate artifact: `source/skills/dispatching-parallel-agents/`
- Decision this finding informs: whether to adopt, adapt, defer, or discard the skill.

## Evidence Set

| Source | Type | Captured | Version or revision | Harness, model, and OS | Status | Result |
|---|---|---|---|---|---|---|
| [Pinned v6.1.1 skill](../../source/skills/dispatching-parallel-agents/SKILL.md) | direct source | 2026-07-23 | Superpowers 6.1.1; commit `d884ae0` | harness-neutral prose; model and OS not applicable | current | Strong independence, prompt-scope, and integration gates; contradictory 2+/3+ trigger; no lifecycle or isolation mechanism |
| [PR #948](https://github.com/obra/superpowers/pull/948) | source audit + proposed fix | 2026-07-23 | Superpowers v5-v6 source; PR head `bdf41c9` | Claude Code 1.0.33; Claude Opus 4.6; OS unknown | unresolved | Confirms the frontmatter says 2+ while the body says 3+; the one-line fix remains open |
| [PR #1470](https://github.com/obra/superpowers/pull/1470) and commit [`f0e5117`](https://github.com/obra/superpowers/commit/f0e5117fa6bdd2645485d2a8df8d7a107c4bf2af) | real-session report + code history | 2026-07-23 | pre-v5.1 report; instruction present by `f0e5117` and v6.1.1 | Claude API and Claude Code; model and OS unknown | unresolved | A controller launched two agents in separate turns but called them parallel. The missing instruction was added; the local v6.1.1 Codex transcript below now supplies a post-change run and shows that Codex still serialized three spawn results despite achieving real child overlap |
| AgentsView session `codex:019d800f-ad35-79f1-9fcf-c458d77fa2d0`; raw source `C:\Users\pmacl\.codex\sessions\2026\04\12\rollout-2026-04-12T00-00-04-019d800f-ad35-79f1-9fcf-c458d77fa2d0.jsonl` | direct local transcript + child lineage | 2026-07-23 | unpinned Superpowers snapshot read on 2026-04-12 | Codex; GPT-5.3-Codex and GPT-5.4; Windows | historical | Skill read at ordinal 309; a two-agent batch overlapped for 63.768 seconds and a later four-agent batch overlapped for 53.059 seconds; all workers completed and the parent synthesized useful results. Workers used inherited context, and stale completed agents caused one initial slot failure before cleanup and retry |
| AgentsView session `codex:019f8eb1-4e84-7652-a5ae-c4262784973b`; raw source `C:\Users\pmacl\.codex\sessions\2026\07\23\rollout-2026-07-23T06-16-52-019f8eb1-4e84-7652-a5ae-c4262784973b.jsonl` | direct local transcript + child lineage | 2026-07-23 | installed Superpowers 6.1.1 | Codex; GPT-5.6-Terra; Windows | current | Exact v6.1.1 skill read at ordinal 3; three `fork_turns: none` children overlapped for 30.828 seconds. Codex serialized spawn results rather than issuing all calls in one response, and the parent interrupted every worker after discovering a shared repository-authority gate that should have been checked before fan-out |
| AgentsView session `codex:019f8cf4-aab6-7693-9ecb-7ded9e04b1c1`; raw source `C:\Users\pmacl\.codex\sessions\2026\07\22\rollout-2026-07-22T22-11-12-019f8cf4-aab6-7693-9ecb-7ded9e04b1c1.jsonl` | implicit behavioral match; no direct skill attribution | 2026-07-23 | Codex workflow on 2026-07-22/23 | Codex; model unknown; Windows | current | Independent research, allowlisted implementation, and reviewer lanes completed. A reviewer found a high-severity state-machine defect missed by passing component tests; the parent corrected it, expanded passing tests, performed live verification, and published PR #93. This supports workflow utility but cannot prove the skill caused the behavior |
| Commits [`9ccce3b`](https://github.com/obra/superpowers/commit/9ccce3bf07a40e45259004a330409ba00970eff7) and [`1c53f5d`](https://github.com/obra/superpowers/commit/1c53f5deb62efeadaf1e9c924662b8f01c342692), plus [issue #350](https://github.com/obra/superpowers/issues/350) | code history + real-agent report | 2026-07-23 | Superpowers v5 context-isolation/SUBAGENT-STOP changes | Codex 0.89 report; model and OS unknown | fixed | Added the isolated-context principle and SUBAGENT-STOP behavior to address skill leakage; no transcript was preserved for the Codex report |
| [Pinned Codex adapter](../../source/skills/using-superpowers/references/codex-tools.md) | direct source + current tool-contract inspection | 2026-07-23 | Superpowers 6.1.1; commit `d884ae0` | Codex CLI 0.145.0; model identifier unknown; Windows | current | Adapter enables agent tools but contains no history/fork control that enforces the skill's “never inherit” guarantee |
| [Issue #1633](https://github.com/obra/superpowers/issues/1633) and [PR #1662](https://github.com/obra/superpowers/pull/1662) | conflicting investigation + direct Codex session | 2026-07-23 | Superpowers 5.1.0-v6.1.1; PR head `85e3215` | Codex CLI 0.133.0 on macOS and Codex Desktop 0.115.0-era surface; GPT-5.5; Desktop OS unknown | unresolved | One report was closed as a runtime ambiguity; the open PR records deferred tool discovery after an initial false “unavailable” conclusion |
| [Issue #1927](https://github.com/obra/superpowers/issues/1927) and [PR #1982](https://github.com/obra/superpowers/pull/1982) | source-backed lifecycle report + proposed fix | 2026-07-23 | Superpowers 5.1.3-v6.1.1; PR head `35769a1` | Codex CLI 0.142.5 with GPT-5.5 on Linux; Codex v2 source has no model or OS context | unresolved | Codex v1 retained finished workers until close; v2 may expose no close operation; the skill has no neutral release step |
| [Issue #597](https://github.com/obra/superpowers/issues/597) | real-user environment report + maintainer triage | 2026-07-23 | Superpowers version unknown | parallel worktrees; harness, model, and OS unknown | current | Parallel sessions can collide on shared ports and databases; maintainer assigns the isolation recipe to project instructions rather than core |
| [Issue #473](https://github.com/obra/superpowers/issues/473) | paired real-agent report | 2026-07-23 | Superpowers version unknown | Claude Code; harness version, model, and OS unknown | unclear | A verification worker proceeded while a development worker paused for permission; maintainer classified autonomy as platform behavior and no transcript is linked |
| [PR #1934](https://github.com/obra/superpowers/pull/1934) | source critique + merged deletion on `dev` | 2026-07-23 | Superpowers 6.1.1/current `main`; merged `dev` head `67714e0` | source-only critique; harness, model, and OS not applicable | current | Removes the “time of one,” benefits recap, and dated success story as social proof on `dev`; v6.1.1 and current `main` still share the old blob and retain the unaudited claims |
| [Issue #429](https://github.com/obra/superpowers/issues/429) | feature request + maintainer/community discussion | 2026-07-23 | Superpowers version unknown | Claude Code Agent Teams; models and OS unknown | current | Confirms coordinated teams are a separate, unresolved workflow; this does not invalidate the skill's narrower independent fan-out scope |

## AgentsView Measurement Method

AgentsView is a local-first index over the machine's agent transcripts, not a public transcript
corpus. The local v0.38.1 archive was queried read-only using exact-content search, session metadata,
chronological tool calls, messages, and parent/child session lineage. Its documented
[session API](https://www.agentsview.io/session-api/) exposes the fields used here, and the
[usage guide](https://www.agentsview.io/usage/) documents direct session links and subagent trees.

Attribution, fidelity, and outcome were evaluated separately:

- **Direct use:** the exact skill was loaded before an episode containing at least two child-spawn
  attempts.
- **Implicit match:** the same fan-out/fan-in pattern occurred without evidence that this skill
  caused it.
- **False positive:** the name appeared only in inherited context, search output, review material,
  or another workflow.

| Episode | Spawn grouping | Measured overlap | Context policy | Fan-in outcome |
|---|---|---:|---|---|
| 2026-04-12 two-domain direct use | two spawn calls in one recorded parent response before child output | 63.768 seconds; peak 2 | inherited (`fork_context: true`) | both completed; parent synthesized both reports |
| 2026-04-12 four-domain direct use | four intended before completion; one slot failure required cleanup and retry | 53.059 seconds with all four active; peak 4 | inherited (`fork_context: true`) | all completed; parent synthesized cross-agent findings |
| 2026-07-23 v6.1.1 direct use | three spawn calls serialized across call results | 30.828 seconds; peak 3 | isolated (`fork_turns: none`) | all interrupted after late shared-gate discovery; no integrated child result |
| 2026-07-22/23 Wi-Fi workflow | repeated three-lane research and implementation batches plus reviewer | overlap confirmed from child lineage; exact aggregate not used for a speed claim | mixed inherited/partial forks | implementation, reviewer-found defect, correction, tests, live verification, and PR; implicit match only |

The evaluation does not infer speedup from overlap alone. It records concurrency, prompt and context
policy, parent review, conflicts, integrated verification, lifecycle handling, and outcome as
separate observations.

The search and lineage inspection can be repeated with the documented CLI surface:

On the reviewed Windows installation, replace `agentsview` below with
`C:\Users\pmacl\AppData\Local\AgentsView\agentsview.exe` because the executable is not on `PATH`.

```powershell
agentsview session search 'dispatching-parallel-agents' --agent codex `
  --include-children --include-automated --include-one-shot --limit 500 --json
agentsview session get <session-id> --json
agentsview session tool-calls <session-id> --json
agentsview session messages <session-id> --from 0 --limit 500 --json
```

## Assessment

- Status: unresolved. Direct attributable Codex transcripts prove that the independence pattern can
  create real overlap and useful synthesis. A separately labeled implicit match corroborates defect
  discovery and successful integration for the broader pattern, but does not establish that this
  skill caused those outcomes. Activation, pre-dispatch authority checks, context isolation,
  dispatch grouping, resource isolation, and worker lifecycle remain inconsistent or
  harness-dependent.
- Corroborating evidence: pinned source, code history, open fixes, direct Codex transcripts with
  AgentsView child lineage and timestamps, real-agent issue reports, and maintainer triage.
- Contradicting evidence: successful local fan-outs show the workflow has substantial practical
  value. A current v6.1.1 run also shows serialized dispatch and wasted worker time when a shared
  authority gate is discovered only after fan-out.
- Confidence: strong for observed Codex behavior; moderate for cross-harness portability.
- Supports: B- editorial grade, prioritizing an adapted Codex-oriented form, retaining the
  independence/prompt/integration gates, and adding explicit preflight, context, and lifecycle rules.
- Does not support: a measured speedup, universal context isolation, a current failure rate, or
  wholesale rejection of parallel agents.

## Reviewer Notes

The transcript search began with 26 Codex sessions containing the exact skill name. Only two had both
direct skill provenance and a multi-child dispatch episode. Most hits were inherited skill text,
search output, reviews, or behavioral matches attributable to another workflow. Attribution,
fidelity, and outcome were therefore classified separately so failed uses were not discarded and
implicit matches were not credited causally.

Current source defects receive more weight than closed platform reports. Agent Teams are treated as
a different coordination model, not a missing requirement for independent fan-out. The local Codex
setting enables multi-agent support today, but actual tool discovery and lifecycle semantics remain
version-sensitive and must be inspected rather than inferred from configuration alone.
