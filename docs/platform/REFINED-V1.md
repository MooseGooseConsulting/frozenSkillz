# Refined v1: Persist and Manage Agent Configurations

> **Status:** adopted 2026-07-31 (operator direction). RV1-01…07 are the standing
> decisions; reversing one requires an explicit edit here, not incremental drift.
> **Authority:** governs the agent-config direction. Tracker, manifests, and
> active skills remain governed by their own sources per `AGENTS.md`.
> **Date:** 2026-07-21; adopted 2026-07-31

## What this is for

Answer one operator need:

> How do we persist and manage agent configuration (skills, rules, MCP selection)
> across machines and GitHub projects without agents inventing a second control plane?

Not: build Obot, a managed MCP proxy, a Renovator GitHub App, or a five-client
conformance pilot.

---

## Challenge of the July 16 pack

The evidence pack and three phase plans are valuable as **traceability**. As an
**implementation roadmap** they overfit a ChatGPT/Codex design spiral.

| Claim in the pack | Challenge |
|---|---|
| Need a new public CLI (`frozen` / `frozenctl`) with sync/validate/mcp-exec/scan | `scripts/sync_frozen_skills.py` already syncs reviewed skills to `~/.agents/skills`. A second CLI before any project-intent convention is duplication. |
| Need `.agents/config.yaml` (or `frozen.yaml`) as project desired state | Operator pushback on 2026-07-16: commit the real files to each GitHub project. Native client files **are** the intent surface. A meta-manifest is optional sugar, not a v1 gate. |
| Need `~/.frozen/machine.yaml` as execution registry | Unproven. Host MCP launch today is client JSON + PATH. Inventing a machine registry before measuring launcher pain is speculative architecture. |
| Four/five pillars including Observation (Obot) in the same program | Observation is a later *optional* sink. Folding it into the same plan bloated Phase 3 and invited false “we adopted Obot” readings. |
| Close every DR/GAP before writing code | Correct for a full control plane; wrong for v1. Ship the thin convention on top of the live sync lane; leave MCP-proxy/session/root security as explicit **non-goals** until a real managed-proxy need appears. |
| Pilot two repos × two OS × five clients | Pilot of an unbuilt system. v1 proof is: one personal machine sync stays green + two real projects commit native configs without a central renderer. |
| Treat transcript architecture as nearly-spec | Register already says nothing is approved. The phase plans still read like a product build sequence. Reframe them as **evidence + deferred backlog**, not the critical path. |

**Core failure mode the pack risked:** designing a universal reconciler for a
workflow the operator already described as “commit those files to each project.”

---

## What is already true (do not redesign)

On `main` today:

1. **Reviewed reusable skills** live under `plugins/frozen-skills/skills/` + four
   manifests (`docs/workflows/skill-authority-and-frozen-sync.md`).
2. **`scripts/sync_frozen_skills.py`** materializes that allowlist into
   `~/.agents/skills` with check/apply/prune and conflict refusal.
3. **Personal/gated skills** are authored live under `~/.agents/skills` and mirrored
   into `_incubator/` for review — opposite authority direction from active skills.
4. **Tracker** gates promotion. No platform doc may silently change that.

v1 **extends** this. It does not replace it.

---

## Refined authority model (v1)

Three surfaces. Full stop.

```text
frozenSkillz Git          project Git                 each machine
─────────────────         ──────────────────          ──────────────────
reviewed reusable         committed native            runtime / secrets
skills + manifests        agent config for            + managed skill copies
+ incubator mirrors       THAT repo                   from sync script
```

| Surface | Owns | Does not own |
|---|---|---|
| **frozenSkillz** | Reusable skill definitions, publication allowlist, intake/review | Per-project MCP menus, project rules, machine credentials |
| **Each project repo** | Native files agents actually read: `AGENTS.md`, `.cursor/`, `.claude/`, `.codex/`, project `.agents/skills/` (local/fork), committed MCP config the team chose | Global skill distribution; other repos’ configs |
| **Each machine** | `~/.agents/skills` managed copies via sync script; client trust/approval; secrets (Doppler/env); host tools on PATH | Project capability selection |

### Explicit v1 decisions (adopted 2026-07-31)

| ID | Decision | Rationale |
|---|---|---|
| RV1-01 | **Project intent = committed native files.** No required `.agents/config.yaml` in v1. | Matches operator intent; avoids parallel source of truth. |
| RV1-02 | **Reusable skills = frozenSkillz + `sync_frozen_skills.py`.** Keep current dual-lane authority. | Already implemented and documented. |
| RV1-03 | **No machine.yaml in v1.** Document launcher expectations as “client config + PATH”; revisit only after a concrete multi-client launcher failure. | YAGNI. |
| RV1-04 | **No observation sink / Obot in v1.** Local `skill-audit` / future scan stay optional diagnostics. | Prevents false adoption; unblocks config persistence work. |
| RV1-05 | **No managed MCP proxy, Docker gateway wrapper, or cross-repo Renovator in v1.** | Security/session design is real but not on the critical path for “persist configs.” |
| RV1-06 | **No new `frozenctl` product surface in v1.** Extend or document the existing Python sync script; add small helpers only when a repeated pain is measured. | One sync tool, not two. |
| RV1-07 | **Rules stay project-owned.** frozenSkillz may scaffold/reference; it does not overwrite project rules from a central pack. | Already the strongest repeated correction in the evidence pack. |

Open items **deferred with no v1 dependency:** DR-019/043/044/045 (roots, tool
policy, session sharing), DR-025–027 (Docker gateway), DR-029–030 (Obot/scan
transport), DR-031–032 (cross-repo PRs), filename bikeshed `config.yaml` vs
`frozen.yaml` (DR-009) — **parked**; native files win for now.

---

## v1 deliverables (what “implemented” would mean)

### D1 — Doctrine (done)

- This file is **adopted** for the agent-config direction (2026-07-31). It does
  not transfer skill-lifecycle authority: tracker, workflows, manifests, and
  active skills remain governed by their own sources per `AGENTS.md`.
- This file is the critical path; the July 16 phase plans are archived in git history.

### D2 — Project config convention (docs in this PR; examples may follow)

A short workflow, `docs/workflows/project-agent-config.md` (included in this PR),
that says:

1. Commit the native files your clients actually load for this repo.
2. Prefer project-local or vendored skills under the project when the skill is
   project-specific; use frozenSkillz sync for shared reviewed skills.
3. Do not invent a second manifest that agents must reconcile against native files.
4. Secrets never committed; reference Doppler/env only.

Optional later: a checked-in **example** fixture repo or `examples/project-agent-config/`
showing one Cursor + one Claude layout — not a renderer.

### D3 — Harden the existing sync lane (code, separate PR)

Only if gaps hurt operators:

- Document Windows/macOS/Linux one-liners in README pointing at skill-authority doc.
- Add `--json` summary for check/apply if agents need machine-readable status.
- Do **not** expand into project vendoring until D2 is in use on ≥2 real projects.

### D4 — Explicit non-goals checklist (keep visible)

v1 is **done** without: Obot, machine.yaml, frozenctl, managed proxy, five-client
fixture matrix, cross-repo update automation, GHCR skill catalog, Project Skill MCP.

---

## Mapping: old phases → refined path

| Old phase plan | Refined treatment |
|---|---|
| Plan 1 design closure | **Shrink:** RV1-01…07 adopted; evidence pack archived. Full DR closure not required. |
| Plan 2 local control plane | **Replace critical path** with D2+D3. Full Plan 2 becomes backlog `BL-platform-later`. |
| Plan 3 conformance/integrations/pilot | **Defer entire plan** until a real multi-machine drift problem appears. |

July 16 `PHASE-0` evidence work is **done enough** to stop expanding the pack.
Further evidence churn is not progress.

---

## Risks of this refinement

| Risk | Mitigation |
|---|---|
| Native files diverge across clients with no schema | Accept in v1; document “commit what your clients read.” Add schema only after painful drift. |
| Projects forget to commit MCP/skills | Convention + review checklist in the project's agent-authority docs; not a central renderer. |
| Agents still invent `config.yaml` | This doc + router: meta-manifest is non-goal unless RV1-01 is explicitly reversed. |
| Losing useful July 16 security thinking | Evidence pack archived in git history ([PR #49](https://github.com/Coldaine/frozenSkillz/pull/49), last on `main` at `069aeea`); recover it only if a deferred decision genuinely reopens. |

---

## Adoption record

Adopted 2026-07-31 by operator direction: RV1-01 through RV1-07 stand as
written. D1 (doctrine) and D2 (`project-agent-config` workflow) are landed;
D3 (sync-lane hardening) triggers only on measured operator friction; D4
(non-goals) is enforced by this file and `docs/platform/README.md`.
The July 16 evidence pack and phase plans are archived in git history
([PR #49](https://github.com/Coldaine/frozenSkillz/pull/49)).
