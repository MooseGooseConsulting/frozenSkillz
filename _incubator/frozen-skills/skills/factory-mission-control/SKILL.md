---
name: factory-mission-control
description: >-
  Route an explicitly selected Codex or ChatGPT conversation through a
  Notion-controlled Factory mission lifecycle: shape a bounded packet, launch
  only with explicit authority, return execution evidence and independent
  review, then capture evidence-backed improvements. Do not use for ordinary
  coding, generic planning, or unattended automation.
---

# Factory Mission Control

This is one gated router, not a scheduler or a separate preflight skill. Its
job is to turn a selected conversation into a bounded mission, preserve the
return path to that conversation, and make outcomes improve the next mission
without silently changing the skill.

The live control surface is [Factory Mission Control](https://app.notion.com/p/3cbc4d261ef8817f9495e137c359e72f?pvs=204). Read it before creating, launching, resuming, or closing a mission. If it is unavailable, do not create a dispatch or launch work; report that the control plane is unavailable.

## Invariants

- A conversation is source material, not launch authority. Read the relevant message bodies before deriving a mission.
- Keep one Mission row per durable outcome and one Dispatch row per external action or handoff. Record links and concise evidence, not credentials or raw secret-bearing logs.
- Do not install this skill, add it to a distribution, alter Factory/Codex hooks, start a daemon, or schedule background work. This incubator copy is intentionally inactive.
- A user saying **launch** (or an equally explicit instruction) for the named mission authorizes that one headless run. No other phrasing does. A run must use high autonomy and must never use an unsafe permission-bypass flag.
- A Factory or Codex hook is local lifecycle telemetry, not a cross-system mission callback. Do not represent hooks as the return channel until an explicit observer/adapter exists and has been separately approved.

## Decision tree 1 — route the request

| Request | Route |
|---|---|
| Ordinary coding, research, or conversation with no Factory handoff | Do that work normally; do not create a Mission. |
| Shape work for later execution | Create or update a Mission in **Intake** or **Prepared**; read [the packet reference](references/mission-packet.md). No Dispatch is created. |
| Explicitly launch a named prepared mission | Continue to tree 2, then create the Dispatch before the external launch. |
| Resume, inspect, review, or close a mission | Read the Mission plus its Dispatches and continue to tree 3. Do not infer completion from a sidebar label, a plan, or a local checkout. |

## Decision tree 2 — establish a dispatchable packet

Read [the mission-packet reference](references/mission-packet.md). Choose exactly one branch:

| Packet state | Route |
|---|---|
| A required field is missing or contradictory | Mark the Mission **Blocked** or keep it **Intake** and resolve it from the source conversation. Do not launch. |
| A preflight is requested or useful | Perform the bounded preflight inside this skill. It may inspect the base revision, target readiness, dependencies, and validation command; it does not mutate the target, broaden scope, or become a separate skill. Record the finding in the Mission. |
| Packet is ready | Record the target, immutable source/base, validation, return path, and stop conditions. Set launch authority only when the user has explicitly granted it. |
| The user explicitly skips optional preflight and explicitly launches | Run the mandatory minimum packet checks, record that preflight was skipped, then use the ready route. A skip never waives source, scope, target, validation, or stop-condition checks. |

For an authorized launch, create a **Factory mission** Dispatch first with the Mission relation, selected registered Droid computer, correlation/session identifier when available, and expected return evidence. Use the Factory Mission surface or its supported headless Mission Mode against that selected computer. Do not use an unsafe permission bypass. Update the Dispatch as it starts, waits, succeeds, needs repair, or blocks.

## Decision tree 3 — return, review, and learn

Read [return-and-learning.md](references/return-and-learning.md). Choose exactly one branch:

| Outcome | Route |
|---|---|
| Acceptance evidence is present | Create result-collection and independent-review Dispatches as needed. Send a concise, evidence-linked review request to a distinct existing Codex or ChatGPT conversation; record its link and verdict. Close only when the approved acceptance path is satisfied. |
| Failure is inside the approved packet | One bounded repair is allowed. Record why it is in scope, create a new Dispatch, and return through this tree after its evidence is collected. |
| The repair needs a new target, broader scope, changed autonomy, deployment/data action, or policy change | Mark the Mission **Waiting** or **Blocked** and ask the user for that specific decision. Do not convert it into an in-run repair. |
| A recurring failure or review disagreement is evidenced | Add or update a Learning row. It is a candidate, not an instruction change: promotion requires three independent matching cases, a regression fixture, a passing holdout, and human signoff. |

## References

- [Mission packet](references/mission-packet.md) — fields and minimum checks before a dispatch.
- [Notion control plane](references/notion-control-plane.md) — register schemas and state semantics.
- [Return and learning](references/return-and-learning.md) — evidence, cross-dispatch, repair, and improvement rules.
