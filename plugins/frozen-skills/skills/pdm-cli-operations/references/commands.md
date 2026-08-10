# Official PDM client commands

Primary upstream references:

- [PDM introduction](https://pdm.proxmox.com/docs/introduction.html) — PDM is the high-level control plane and native remote UIs are the granular escape hatch.
- [PDM client description](https://pdm.proxmox.com/docs/sysadmin.html#proxmox-datacenter-manager-client)
- [PDM command syntax](https://pdm.proxmox.com/docs/command-syntax.html#proxmox-datacenter-manager-client)
- [PDM package repositories](https://pdm.proxmox.com/docs/installation.html#debian-package-repositories)

The upstream documentation is currently 1.1.7 (2026-07-15). Environments may legitimately run an earlier 1.1.x release. Always inspect the installed client and server before relying on examples below; version-specific notes are evidence, not permanent product limits.

## Contents

- [Installation boundary](#installation-boundary)
- [Environment launcher](#environment-launcher)
- [Raw client login](#raw-client-login)
- [Authority](#authority)
- [Capability check and surface routing](#capability-check-and-surface-routing)
- [Discovery and evidence](#discovery-and-evidence)
- [Guest lifecycle and snapshots](#guest-lifecycle-and-snapshots)
- [Migration](#migration)
- [Task completion](#task-completion)
- [Failure routing](#failure-routing)

## Installation boundary

The executable is `proxmox-datacenter-manager-client`. First inspect what is already installed:

```sh
command -v proxmox-datacenter-manager-client
dpkg-query -W -f='${Package} ${Version}\n' proxmox-datacenter-manager-client
```

Install it only on a compatible Debian amd64 operator host from an official Proxmox PDM repository selected by the owning environment. Do not silently enable a test repository. Install the client package, not a PDM server, when all that is needed is the process interface.

Proxmox does not publish a native Windows build. If the environment selected the official client route on Windows, use an environment-owned Linux runner or the bundled bridge if it has qualified one. A documented pinned direct adapter is an independent supported Windows route; do not detour through Linux/SSH. Do not create WSL or a container solely to satisfy this skill unless the operator explicitly chooses that architecture.

## Environment launcher

Prefer an environment-owned PDM entrypoint when the owning repository provides one. Keep concrete adapter, launcher, and SSH-runner names in [env-notes.md](env-notes.md); they are not part of the portable skill contract.

For an official-client-compatible launcher:

```sh
<launcher> --output-format json remote list
<launcher> --output-format json resources
```

For a constrained direct adapter, invoke its documented named operations; it is not required to implement the official CLI's arguments or command grammar.

A good official-client launcher should:

- retrieve the environment-selected identity without printing its credential;
- retain the official client's ticket cache separately from unrelated identities;
- preserve TLS verification;
- invoke `proxmox-datacenter-manager-client` for the requested PDM command; and
- preserve stdout, stderr, and exit status.

An environment-owned direct PDM API adapter is also valid when it pins TLS,
contains only reviewed operations, protects credentials, and reports its
supported boundary clearly. Use it directly on Windows or an agent when the
repository declares it; do not force a Linux/SSH bridge merely to reach the
official CLI. Neither entrypoint may impose an invented read-only policy on an
identity whose owning environment authorizes mutation.

### Optional Windows SSH bridge

The bundled adapter `scripts/pdm.ps1` forwards PDM commands over SSH to an authorized Linux runner. It is optional and is not another management plane.

Required environment:

| Variable | Meaning |
|---|---|
| `PDM_CLI_SSH_TARGET` | `user@host` for the authorized runner; put non-default ports in SSH config |
| `PDM_CLI_REMOTE_PROGRAM` | Bare launcher/client name on PATH, or an absolute POSIX path |

```powershell
$env:PDM_CLI_SSH_TARGET = 'operator@pdm-client-runner'
$env:PDM_CLI_REMOTE_PROGRAM = 'proxmox-datacenter-manager-client'
& "<skill-root>/scripts/pdm.ps1" --output-format json remote list
```

The bridge rejects password flags and uses noninteractive SSH. Authentication that requires secrets happens on the Linux runner, not in the Windows SSH argv.

## Raw client login

Global connection options precede the subcommand. Ordinary commands use a cached session; login is explicit.

```sh
export XDG_CONFIG_HOME='<protected-state>/config'
export XDG_CACHE_HOME='<protected-state>/cache'
install -d -m 0700 "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME/proxmox-datacenter-client"

proxmox-datacenter-manager-client \
  --host '<pdm-host>' \
  --port 8443 \
  --user '<user-id>' \
  --fingerprint '<independently-verified-sha256-fingerprint>' \
  --password-command '<secret-manager command that writes only the password>' \
  login

proxmox-datacenter-manager-client \
  --host '<pdm-host>' \
  --port 8443 \
  --user '<user-id>' \
  --output-format json \
  remote list
```

A live-qualified 1.1.6 environment observed that noninteractive login parsed `--fingerprint` but did not seed the verifier cache. That environment worked around the behavior by writing the independently verified fingerprint to the client's cache before login. Do not generalize that quirk to newer clients; first test the installed version.

Do not put a password directly in argv. Use a protected password command or a short-lived mode-0600 password file created and removed by the owning environment.

## Authority

PDM authorization and the backing remote's authorization both matter. The environment owns those identities and ACLs; this skill does not substitute a safer-looking but insufficient identity after an execution task was authorized.

A successful read does not prove mutation authority. An authorization failure during a requested mutation means diagnose the assigned PDM/backing-remote permissions; it does not mean silently redefine the task as read-only.

## Capability check and surface routing

PDM is the default surface, but it is intentionally high-level. **For an
official-client-compatible launcher only**, inspect current help before assuming
PDM can or cannot do something:

```sh
<pdm> help --verbose
<pdm> help pve --verbose
<pdm> help pbs --verbose
<pdm> help pve qemu --verbose
<pdm> help pve lxc --verbose
```

Use current official command syntax when the installed help is ambiguous.

For a constrained direct adapter, use its documented operation list as the
capability boundary. Do not send it `help --verbose` or any other official CLI
syntax that the owning environment has not declared it to support. If the
adapter does not expose the requested PDM operation, route through that
environment's documented PDM/native boundary rather than guessing an endpoint.

Choose the surface this way:

| Evidence | Surface |
|---|---|
| PDM exposes the requested fleet/guest/PBS operation | **PDM** |
| PDM does not expose the required operation in the installed version | **Native PVE/PBS** for that operation |
| Operation is inherently host-local or granular remote configuration | **Native PVE/PBS** |
| PDM localizes a problem to one remote and deeper diagnosis is needed | **Native PVE/PBS** for diagnosis |
| PDM itself is unreachable or needs repair | **Native PVE/PBS** for continued/recovery operation |

Do not call a normal capability handoff “break-glass” merely because it uses `qm`, `pct`, `pvesh`, the PVE API, the PBS API, or a native web interface. Conversely, do not bypass a working PDM operation solely because the native command is familiar.

This reference intentionally does not teach every native PVE/PBS command. Once routing selects a native surface, use the owning environment's native Proxmox runbook/skill and current PVE/PBS documentation.

## Discovery and evidence

The following commands are **official-client-compatible launcher only**.
`<pdm>` means that launcher or the raw client plus its global connection
options; it is not a placeholder for a constrained direct adapter. For such an
adapter, use its documented named discovery operations instead.

```sh
<pdm> --output-format json remote list
<pdm> --output-format json resources
<pdm> --output-format json pve node list <remote>
<pdm> --output-format json pve resources <remote> [vm|storage|node|sdn]
<pdm> --output-format json pve qemu list <remote> [--node <node>]
<pdm> --output-format json pve lxc list <remote> [--node <node>]
<pdm> --output-format json pve qemu config <remote> <vmid> --node <node> --state active
<pdm> --output-format json pve lxc config <remote> <vmid> --node <node> --state active
<pdm> --output-format json pve task list <remote>
<pdm> --output-format json pbs datastore list <remote>
<pdm> --output-format json pbs snapshot list <remote> <datastore>
<pdm> --output-format json pbs task list <remote>
```

The fleet command is `resources`, not `resources list`, in the 1.1.x client family. Guest configuration may default to pending state, so request `--state active` when current configuration is the evidence you need. Runtime state comes from the guest/resource listing rather than the configuration response.

## Guest lifecycle and snapshots

Read current guest state and active configuration immediately before execution. Confirm remote, node, VMID, kind, and guest name together. Prefer graceful shutdown unless the task specifically needs an abrupt stop.

```sh
# QEMU lifecycle
<pdm> --output-format json pve qemu start <remote> <vmid> --node <node>
<pdm> --output-format json pve qemu shutdown <remote> <vmid> --node <node>
<pdm> --output-format json pve qemu stop <remote> <vmid> --node <node>

# LXC lifecycle
<pdm> --output-format json pve lxc start <remote> <vmid> --node <node>
<pdm> --output-format json pve lxc shutdown <remote> <vmid> --node <node>
<pdm> --output-format json pve lxc stop <remote> <vmid> --node <node>

# QEMU snapshots
<pdm> --output-format json pve qemu snapshot list <remote> <vmid> --node <node>
<pdm> --output-format json pve qemu snapshot create <remote> <vmid> <snapname> --node <node> [--description <text>] [--vmstate <boolean>]
<pdm> --output-format json pve qemu snapshot delete <remote> <vmid> <snapname> --node <node>
<pdm> --output-format json pve qemu snapshot rollback <remote> <vmid> <snapname> --node <node> [--start <boolean>]

# LXC snapshots
<pdm> --output-format json pve lxc snapshot list <remote> <vmid> --node <node>
<pdm> --output-format json pve lxc snapshot create <remote> <vmid> <snapname> --node <node> [--description <text>]
<pdm> --output-format json pve lxc snapshot delete <remote> <vmid> <snapname> --node <node>
<pdm> --output-format json pve lxc snapshot rollback <remote> <vmid> <snapname> --node <node> [--start <boolean>]
```

Rollback is destructive. Verify the target snapshot and current guest identity before executing it. Do not add unrelated preconditions that the owning environment has not established.

## Migration

Same-remote migration uses a target node:

```sh
# QEMU, same remote
<pdm> --output-format json pve qemu migrate <remote> <vmid> <target-node> \
  --node <source-node> [--online <boolean>] [--force <boolean>] \
  [--with-local-disks <boolean>] [--map-storage FROM:TO,...] \
  [--bwlimit <KiB/s>] [--migration-network <CIDR>] \
  [--migration-type secure|insecure]

# LXC, same remote
<pdm> --output-format json pve lxc migrate <remote> <vmid> <target-node> \
  --node <source-node> [--online <boolean>] [--restart <boolean>] \
  [--timeout <seconds>] [--map-storage FROM:TO,...] [--bwlimit <KiB/s>]
```

Cross-remote migration requires explicit bridge and storage mappings:

```sh
# QEMU, cross remote
<pdm> --output-format json pve qemu remote-migrate \
  <source-remote> <vmid> <target-remote> \
  --map-bridge FROM:TO,... --map-storage FROM:TO,... \
  [--node <source-node>] [--target-vmid <vmid>] \
  [--online <boolean>] [--delete <boolean>] [--bwlimit <KiB/s>]

# LXC, cross remote
<pdm> --output-format json pve lxc remote-migrate \
  <source-remote> <vmid> <target-remote> \
  --map-bridge FROM:TO,... --map-storage FROM:TO,... \
  [--node <source-node>] [--target-vmid <vmid>] \
  [--online <boolean>] [--restart <boolean>] [--timeout <seconds>] \
  [--delete <boolean>] [--bwlimit <KiB/s>]
```

Capture source, target, storage, network, and deletion semantics before submission. Use the operation requested by the task; do not automatically turn a migration into a broader topology-hardening exercise.

## Task completion

A mutation may return synchronously or through a UPID/task. An accepted request is not evidence of completion.

A live-qualified 1.1.6 client automatically waited for snapshot create/delete and emitted a wrapped UPID followed by a non-JSON terminal `TaskStatus` even when JSON output was requested. Preserve the original output when evidence matters.

When a UPID is returned, use the complete remote-prefixed identifier if required by the installed client:

```sh
<pdm> --output-format json pve task status <remote> '<pve:remote!UPID:...>'
<pdm> --output-format json pbs task status <remote> '<pbs:remote!UPID:...>'
```

Poll at a bounded interval while the task is running. Success requires terminal stopped state plus an OK exit status when the API provides those fields. A timeout, transport loss, missing task, or malformed response is an unknown outcome: re-read the same task and resource state before considering a retry.

After success, verify the intended resource state. Do not infer completion from the request being accepted.

## Failure routing

| Evidence | Meaning | Next action |
|---|---|---|
| Client missing/incompatible | Operator-runner problem | Correct the client environment; do not modify PDM/PVE merely to satisfy the tool |
| TLS mismatch | Trust/identity problem | Stop and independently verify the certificate |
| PDM authentication rejected | PDM identity problem | Repair the selected identity/credential |
| Reads work but mutation is unauthorized | ACL/remote credential problem | Correct the authorized execution identity; do not silently downgrade the task |
| Command/subcommand absent in current PDM help/docs | **PDM capability gap** | Route that operation to documented native PVE/PBS if the task requires it |
| PDM endpoint unreachable | **PDM unavailable** | Use native PVE/PBS for operations that can proceed; diagnose/restore PDM separately |
| PDM reachable but one remote unavailable | **Remote-specific failure** | Diagnose that remote natively; PDM itself may be healthy |
| PDM operation returns remote error | Target operation failure | Preserve task/error evidence; use native diagnosis if it adds needed detail |
| Task stops non-OK | Target operation failed | Report failure; inspect task/resource state before retrying |
| Task outcome unknown after transport loss | Indeterminate | Re-query task and resource state; do not blindly resubmit |

The important boundary is **why** the surface changes. PDM-first centralization and native drill-down are complementary, not competing doctrines.
