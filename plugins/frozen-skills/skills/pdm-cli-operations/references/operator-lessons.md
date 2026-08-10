# Control-surface lessons for PDM-first operations

Load this file only when changing the skill, writing routing evals, or explaining why the skill prefers PDM without forbidding native PVE/PBS.

## The corrected lesson

The useful lesson from prior agent failures is **not** “never use another control surface.” It is:

> Use one obvious primary fleet surface, change surfaces for an explicit technical reason, and preserve enough evidence to know what actually happened.

For Proxmox, PDM is the primary fleet-management plane. Native PVE/PBS is the expected granular layer beneath it. Proxmox itself describes PDM as a high-level control plane with a transition/escape hatch to native remote interfaces for granular configuration.

That yields a capability ladder rather than a prohibition:

```text
requested Proxmox operation
  -> can current PDM perform it?
       yes -> PDM
       no  -> is it a documented native PVE/PBS operation?
                yes -> native surface
                no  -> identify the real missing capability; do not invent middleware by default
```

PDM unavailability is another ordinary reason to use native PVE/PBS. It is a recovery condition, but native PVE/PBS use is **not limited** to recovery conditions.

## What agents should centralize through PDM

PDM earns its position as the normal surface because it gives one fleet-wide context for:

- remotes, nodes, guests, storages, and PBS resources;
- fleet-oriented guest lifecycle operations;
- task evidence;
- supported snapshots and migrations;
- PDM-side identity/trust and remote management; and
- a consistent operator/automation entrypoint across the fleet.

If PDM already supports the operation, choosing a direct node command merely because it is familiar throws away that central context for no benefit.

## What agents should use natively

Native PVE/PBS is appropriate when:

- the current PDM version does not expose the requested operation;
- the operation is inherently host-local or granular remote configuration;
- deeper logs/configuration are needed to diagnose one remote;
- PDM reports the remote as unavailable and the remote itself must be inspected;
- PDM is unavailable or the PDM guest needs recovery; or
- the operator/owning repository explicitly directs a documented native workflow.

A native handoff should be explicit in the result: name the surface and why it was selected. That is enough. Do not wrap ordinary native drill-down in invented approval ceremony.

## Authentication ownership

An environment-owned launcher that obtains credentials opaquely remains part of the PDM workflow. Its ordinary use does not require a secrets-management handoff. Route to the applicable secrets skill only when the task directly reads, writes, configures, rotates, or troubleshoots the credential source or injection path.

## Failure modes to avoid

| Failure mode | Better behavior |
|---|---|
| Bypass PDM for every operation because `qm`/API is familiar | Check PDM first and use it when it already owns the fleet-level operation |
| Refuse a valid task because PDM lacks a command | Confirm the capability gap, then use the documented native PVE/PBS path |
| Treat every native command as “break-glass” | Distinguish normal capability drill-down from outage/recovery work |
| Silently hop surfaces after an auth/syntax failure | Diagnose the actual failure boundary before changing surfaces |
| Install a new MCP/proxy/control service because the existing CLI is inconvenient | Prefer the two control surfaces already owned by the environment unless a new interface is an explicit design task |
| Treat a returned UPID as completion | Follow the task and verify post-state |
| Add unrelated invariants, non-goals, hardening, or policy | Execute the requested operation within the owning environment's actual rules |
| Treat repository intent as live state | Read PDM/PVE/PBS state before and after the operation |

## No invented non-goals

This skill must not manufacture architecture from absence. Examples of bad invented rules:

- “Native PVE must never be used.”
- “PDM must be bypassed for host-local work even if PDM supports it.”
- “Every mutation requires a new approval gate.”
- “MCP/direct API is always forbidden.”
- “A recovery path must also be the normal operating path.”

Only the owning environment can establish those constraints. The portable skill supplies routing and evidence discipline, not policy that was never requested.

## Minimal workflow worth preserving

```text
identify target
  -> choose surface by current capability
  -> use the trusted environment launcher when credentials remain opaque
  -> read pre-state
  -> execute requested action
  -> follow task if any
  -> verify post-state
  -> report surface + result
```

That is the useful residue. Everything else belongs in the environment's architecture, access, or recovery documentation.
