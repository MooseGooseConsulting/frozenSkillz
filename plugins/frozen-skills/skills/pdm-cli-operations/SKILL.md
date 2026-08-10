---
name: pdm-cli-operations
description: >-
  Inspect and operate Proxmox VE and PBS fleets through the official PDM client
  or an environment-owned wrapper. Use for inventory, guest lifecycle, tasks,
  metrics, snapshots, migration, and PDM troubleshooting; not native PVE/PBS
  break-glass work, WSL/container installs for PDM, or generic infra unrelated
  to the standing PDM API.
---

# PDM CLI Operations

Use `proxmox-datacenter-manager-client` as the shared process interface for agents and operators. An environment may expose a small launcher around that binary for credential retrieval and TLS pinning. It connects to the standing PDM API; it is not another service, database, MCP server, or source of truth.

The official client currently requires a compatible amd64 Debian environment, network access to a same-major PDM server, and a secret-safe credential command.

## Operating Contract

- Prefer the environment-owned launcher when it obtains credentials opaquely. Invoking that trusted launcher is not itself secret handling and does not require loading a separate secrets-management skill.
- Load the applicable secrets-management skill only when the task directly reads, writes, configures, rotates, or troubleshoots the credential source or secret injection. Do not load it merely because PDM authentication occurs behind the launcher.
- Resolve the PDM endpoint, TLS fingerprint, non-secret auth ID, and target names from the environment's canonical operational repository. Never copy that inventory into this skill.
- Use the identity supplied by the environment. A read-only identity is suitable for inspection or qualification, not for an authorized execution task; do not silently downgrade the requested operation.
- Verify the client and PDM share the same major version before relying on it. Re-check version-specific quirks after upgrades (see [references/commands.md](references/commands.md)).
- Prefer the environment-owned launcher when one exists. It must still invoke the official client and preserve its output and exit code.
- The raw client requires `login` before ordinary commands; persist its XDG ticket cache. Pass the password only to `login` on the operator host that runs the client, through `--password-command` or a protected short-lived `--password-file`.
- Never place a password in argv, a committed file, a prompt, durable output, or the Windows SSH bridge command line.
- Pin the expected TLS certificate and never suppress verification. Use the independently verified cache-pin procedure in the reference or a launcher that implements it when the installed client does not seed the verifier from `--fingerprint` during noninteractive login.
- Request `--output-format json` for agent work. Preserve the original output when evidence matters; some client versions emit a non-JSON terminal `TaskStatus` for mutations even when JSON was requested.
- Start with `remote list`, then select the exact remote, node, and guest. A VMID is not globally meaningful without its remote.
- Read current state immediately before a mutation. Stay within the task's authority while diagnosing and resolving proven dependencies needed to complete it.
- Treat an accepted request or returned UPID as started, not completed. Require terminal `stopped` plus `exitstatus=OK`, then read state again. Status means applied (and verified), not merely authored or accepted.
- Distinguish client/authentication failure, PDM unavailability, remote unavailability, and an unsuccessful remote task. Report the actual boundary.
- PDM is the normal fleet surface. Native PVE or PBS access remains the explicit break-glass path when PDM is unavailable; do not deploy a parallel control plane as a workaround.

## Intent → Action

| User wants to… | Do |
|---|---|
| Prove auth / list remotes | `<pdm> --output-format json remote list` |
| Inventory fleet resources | `<pdm> --output-format json resources` then narrow by remote/node |
| Inspect one guest | list/config with remote + node + VMID; use `--state active` for current config |
| Mutate (start/stop/snapshot/migrate) | pre-state → one authorized action → follow task to `stopped`/`OK` → post-state |
| Follow a task | remote-prefixed UPID via `pve`/`pbs task status`; never treat UPID alone as done |
| Windows without a local client | optional bridge `scripts/pdm.ps1` with `PDM_CLI_SSH_TARGET` + `PDM_CLI_REMOTE_PROGRAM` set; no password flags |
| PDM down / break-glass | native PVE/PBS only when explicitly required; do not invent a parallel control plane |
| “Just use MCP / qm / node SSH instead” | refuse as the default path; that recreates the typist failure mode — see [references/operator-lessons.md](references/operator-lessons.md) only if debating skill shape |

`<pdm>` means the environment launcher or the raw client plus its global connection options.

## Workflow

1. Read the owning repository's current access and fleet references.
2. Confirm the binary exists and record `--version` or package version without changing the host.
3. Select the environment launcher. If no trusted launcher exists, build the two-step raw-client login using the endpoint, user ID, TLS pin, persistent XDG state, and a secret-safe password source; load the relevant secrets skill only for that direct credential work.
4. Prove authentication with `remote list` and JSON output.
5. Read pre-state and select the exact remote, node, resource ID, and name.
6. For a mutation, confirm the supplied identity has the necessary authority, execute the exact action once, follow its task to success or failure, and verify post-state.
7. Return concise evidence: PDM endpoint identity, remote, node, guest ID and name when applicable, action, UPID or synchronous result, and final state. Redact credentials.

## References

Load these only when needed:

- [references/commands.md](references/commands.md): installation boundary, launcher contract, login, discovery, mutations, task follow-through, failure routing.
- [references/env-notes.md](references/env-notes.md): **only** when binding this skill to a specific environment's launcher name, SSH runner, or sync-install path.
- [references/related-work.md](references/related-work.md): **only** when evaluating adjacent Proxmox agent skills/MCP toolkits as future enhancement or sibling-skill candidates (not for normal PDM operations).
- [references/operator-lessons.md](references/operator-lessons.md): **only** when hardening this skill against prior Cursor/Claude/Codex k8s typist failures (maps Homelab lessons → PDM contract).

Verify live syntax with `help --verbose` before using a command that is not covered in the reference.
