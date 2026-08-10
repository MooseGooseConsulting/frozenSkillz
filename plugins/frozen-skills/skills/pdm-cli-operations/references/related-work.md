# Related Proxmox control interfaces

Load this file only when evaluating whether an environment needs another durable Proxmox interface or a separate native-operations skill. It is not required for ordinary fleet work.

## Control hierarchy

`pdm-cli-operations` assumes this default hierarchy:

1. **PDM** — primary centralized fleet-management/control plane.
2. **Native PVE/PBS** — supported granular drill-down and recovery layer beneath PDM.
3. **Additional MCP/API/proxy/tooling** — only when the owning environment has deliberately adopted it or the task is specifically to evaluate/add it.

Native PVE/PBS is therefore not “competing tooling.” It is part of the Proxmox control model. The mistake to avoid is creating ad-hoc third middleware simply because one PDM command is missing or inconvenient.

## Official sources

- [Proxmox Datacenter Manager](https://github.com/proxmox/proxmox-datacenter-manager) — upstream PDM implementation.
- [PDM documentation](https://pdm.proxmox.com/docs/) — current product and client behavior.
- The current PVE/PBS documentation becomes authoritative when the routing decision selects a native remote operation.

## Adjacent agent/tooling projects

These projects may be useful when the operator is explicitly evaluating a durable additional interface. Re-check their current state before relying on them; this file does not pin stars, versions, or adoption status.

| Resource | Interface | How to think about it |
|---|---|---|
| [eddygk/proxmox-ops](https://github.com/eddygk/proxmox-ops) | PVE-oriented skill/scripts | Possible native-operation patterns; not a reason to bypass PDM for supported fleet work |
| [codeandsolder/proxmox-agent-skill](https://github.com/codeandsolder/proxmox-agent-skill) | PVE API/tooling | Compare structured native-operation patterns if an environment needs them |
| [agentify-sh/cursor-proxmox-mcp](https://github.com/agentify-sh/cursor-proxmox-mcp) | MCP over Proxmox REST | An additional interface that should be adopted deliberately, not spawned as an automatic fallback |
| [vinnie357/claude-skills](https://github.com/vinnie357/claude-skills) | broader skill pack | Possible workflow/reference material only |
| [xobotyi/cc-foundry](https://github.com/xobotyi/cc-foundry) | broader agent tooling | Possible workflow/reference material only |

## When an additional interface is justified

Do not use “PDM lacks operation X” as automatic evidence that another service is needed. First ask:

- Can the operation be performed through the environment's existing native PVE/PBS API/UI/CLI?
- Is this a repeated enough workflow that a reusable native skill or wrapper would reduce errors?
- Does the proposed interface preserve resource identity, auth boundaries, task evidence, and current-state verification?
- Is the operator actually asking for another service/control interface?

If the answer is simply “PDM is high-level and this one operation is remote-local,” use native PVE/PBS and move on.
