---
name: pdm-cli-operations
description: >-
  Operate Proxmox VE and PBS fleets with Proxmox Datacenter Manager as the
  primary centralized control plane. Use for fleet inventory, guest lifecycle,
  tasks, snapshots, migrations, PDM auth/trust, and deciding when to drill down
  to native PVE/PBS because PDM does not expose an operation or is unavailable.
---

# PDM-First Proxmox Fleet Operations

Treat Proxmox Datacenter Manager (PDM) as the normal fleet-management surface for Proxmox VE (PVE) and Proxmox Backup Server (PBS). PDM is a high-level control plane over the remotes; the native PVE/PBS interfaces remain the underlying granular control surfaces and recovery path.

The hierarchy is simple:

1. **Use PDM first** for operations PDM exposes.
2. **Use the existing native PVE/PBS surface deliberately** when the required operation is not exposed by the current PDM version, when remote-local diagnosis/configuration is inherently native, or when PDM itself is unavailable.
3. **Do not invent another control service just to avoid either surface.** If the environment has already adopted another supported interface, follow the owning repository rather than this generic preference.

Using native PVE/PBS for a capability gap is not a PDM failure and is not automatically “break-glass.” PDM remains the primary fleet plane even when a specific operation drills down to a remote.

## Operating Contract

- Prefer the environment-owned PDM launcher when it obtains credentials opaquely; using that trusted launcher is ordinary PDM operation, not direct secret handling.
- Load the applicable secrets-management skill only when the task directly reads, writes, configures, rotates, or troubleshoots the credential source or injection path. Do not load it merely because PDM authenticates behind the launcher.
- Resolve the PDM endpoint, TLS trust, identity, remotes, nodes, and native access paths from the owning environment. Do not copy environment inventory into this skill.
- The environment-owned launcher should still invoke the official `proxmox-datacenter-manager-client` and preserve output and exit status.
- Verify the installed client/server versions and inspect `help --verbose` before assuming a command exists. PDM is evolving quickly; do not turn an old capability gap into permanent architecture.
- **Route by capability, not ideology.** If PDM supports the requested operation, use PDM. If it does not, say so and use the documented native PVE/PBS path if the task still requires the operation.
- Do not silently pivot because a command failed. First distinguish: wrong syntax/version, auth/trust failure, PDM outage, remote outage, or an operation PDM simply does not expose.
- Keep resource identity explicit: remote + node + guest kind + VMID + name when applicable. VMID alone is not fleet identity.
- Read current state immediately before a mutation. Execute the requested mutation once; do not add unrelated hardening, invariants, or policy that the task/environment did not ask for.
- A returned UPID or accepted request means **started**, not completed. Require terminal task success when the surface provides a task, then verify the resulting resource state.
- Never put passwords or tokens in argv, prompts, committed files, or durable output. Keep TLS verification enabled.
- Report which surface performed the operation: **PDM**, **native PVE**, or **native PBS**, plus the reason when it was not PDM.

## Control-Surface Routing

| Situation | Preferred surface |
|---|---|
| Fleet inventory, remote/node/resource overview | **PDM** |
| Guest power/lifecycle supported by PDM | **PDM** |
| Guest snapshots supported by PDM | **PDM** |
| Same-remote or cross-remote migration supported by PDM | **PDM** |
| PBS inventory/tasks exposed by PDM | **PDM** |
| PDM authentication, TLS, remote registration, or PDM task troubleshooting | **PDM** |
| Requested operation absent from current PDM client/API after checking current help/docs | **Native PVE/PBS** for that operation |
| Granular host/cluster configuration PDM intentionally leaves to a remote | **Native PVE/PBS** |
| Deep diagnosis of one PVE/PBS remote after PDM localizes the problem | **Native PVE/PBS** |
| PDM unreachable, broken, or the PDM guest itself needs recovery | **Native PVE/PBS** |
| User explicitly requests an existing documented native PVE/PBS workflow | Use that native workflow; do not force an unnecessary PDM detour |

The routing rule is not “never use `qm`, `pvesh`, the PVE API, or PBS-native tools.” It is “do not bypass a working centralized operation without a reason, and do not pretend PDM implements something it does not.”

## PDM Workflow

1. Read the owning environment’s fleet/access references.
2. Confirm the PDM client/launcher and current version.
3. If a trusted environment launcher exists, use it. Otherwise use the raw official
   `proxmox-datacenter-manager-client` with the environment's documented connection options. If
   direct credential or injection work is actually required, load the applicable secrets-management
   skill before proving connectivity with a small read such as `remote list`.
4. Identify the exact remote, node, resource ID, kind, and name.
5. Confirm the requested operation exists in the installed PDM surface.
6. Read pre-state, execute the requested action, follow any returned task to terminal success, and read post-state.
7. Return concise evidence: surface used, target identity, action, task/result, and final state.

## Native Drill-Down Workflow

Use this only after the routing decision selects native PVE/PBS.

1. State the reason for drill-down: **PDM capability gap**, **remote-local diagnosis/configuration**, or **PDM unavailable/recovery**.
2. Use the environment’s already-documented native access/API/CLI path. This skill does not invent node credentials or a parallel native inventory.
3. Re-read the same target’s native pre-state.
4. Perform only the operation needed for the task.
5. Verify native post-state and, when relevant, confirm the resulting resource is visible correctly from PDM afterward.

Native drill-down should be boring and explicit. It is a supported layer boundary, not an architectural exception that needs ceremony.

## Intent → Action

| User wants to… | Do |
|---|---|
| List remotes / prove PDM auth | `<pdm> --output-format json remote list` |
| Inventory fleet resources | `<pdm> --output-format json resources`, then narrow by remote/node |
| Inspect a guest | PDM list/config with remote + node + VMID; use active state where required |
| Start/stop/shutdown/snapshot/migrate through PDM | pre-state → one action → terminal task/result → post-state |
| Follow a PDM task | use the remote-prefixed UPID and PDM task status |
| Perform something PDM does not expose | verify the gap with current help/docs, then use the documented native PVE/PBS surface |
| Diagnose a remote that PDM says is unavailable | inspect that remote natively; keep PDM failure and remote failure distinct |
| Recover when PDM is down | use native PVE/PBS; repair PDM separately rather than blocking unrelated fleet recovery |

`<pdm>` means the environment launcher or the raw official client plus its connection options.

## References

Load only what the task needs:

- [references/commands.md](references/commands.md): PDM client setup, command examples, task completion, capability checks, and failure routing.
- [references/env-notes.md](references/env-notes.md): environment binding only — launcher names, SSH runners, and sync/install shape.
- [references/operator-lessons.md](references/operator-lessons.md): rationale for PDM-first **without** turning native PVE/PBS into a forbidden surface.
- [references/related-work.md](references/related-work.md): adjacent Proxmox interfaces when evaluating a durable additional interface, not ordinary operations.

For commands not covered here, trust the installed client’s `help --verbose` and current official PDM documentation over remembered syntax.
