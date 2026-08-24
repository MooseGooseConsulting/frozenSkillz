# architecture.md

## Architecture Thesis

homelab-gitops is a layered, reconciled Kubernetes homelab. OpenTofu provisions
the VM substrate on Proxmox; Talos Linux turns those VMs into a Kubernetes
cluster; a platform layer installs the shared services (ingress, secrets,
storage, database operator); apps run on top. A GitOps controller reconciles the
repo into the cluster, so the repo is the desired state and the cluster is the
observed state.

## Status Legend

- **Current** — applied to the live cluster (reconciled / present in cluster or remote state).
- **Planned** — decided direction, manifest may exist, not yet applied.
- **Candidate** — plausible option, not decided.
- **Deferred** — intentionally not being built now.

Note: status is about *applied*, not *authored*. A manifest committed to the
tree but not yet reconciled is **Planned**, not Current.

## System Shape

| Area | Status | Approach |
|---|---|---|
| Substrate (`tofu/`) | Current | OpenTofu provisions Proxmox VMs and the Talos boot media |
| Kubernetes (`talos/`) | Current | Talos Linux, declarative machine config, 1 control plane + 2 workers |
| GitOps controller (`platform/`) | Current | Reconciles `platform/` and `apps/` from this repo |
| Ingress + TLS (`platform/`) | Current | Gateway controller with automatic certificates |
| Secrets (`platform/`) | Current | External secrets operator backed by an out-of-cluster store |
| In-cluster S3 (`platform/`) | Planned | Object store for backups and app blobs; manifest drafted, not applied |
| Postgres operator (`platform/`) | Planned | Operator-managed Postgres for stateful apps |
| Offsite backup target | Candidate | Replicate object store to a remote bucket; not decided |
| Service mesh | Deferred | No app needs mTLS or traffic-splitting yet |

## Major Components

| Component | Status | Responsibility | Detail |
|---|---|---|---|
| `tofu/` | Current | VM substrate and boot media | `docs/components/substrate.md` |
| `talos/` | Current | Cluster machine config and bootstrap | `docs/components/talos.md` |
| `platform/` | Current | Shared cluster services | `docs/components/platform.md` |
| `apps/` | Current | Workloads | `docs/components/apps.md` |

## Constraints and Conventions

**Constraints** (required; source named):

- Worker VMs carry a single boot disk in the cluster manifest — required: the machine-provisioning provider's storage schema exposes one boot-volume field and no additional-volume field (provider docs, pinned version linked in `docs/components/substrate.md`).
- Talos machine config is the only path to node OS state — required: Talos has no shell and no package manager; there is nothing else to edit.
- All hosts present the same CPU model to guests — required: live migration across the heterogeneous hosts fails otherwise (incident 2026-05, `docs/decisions/0004-uniform-cpu-baseline.md`).

**Conventions** (chosen; alternative named):

- Nodes that need a data disk get it from a per-host VM template with the disk baked in — chosen; alternative: clone boot-only and attach the disk after clone with one host command; not evaluated when the storage nodes were built (owner asked 2026-08-15; no recorded reason). *This is a choice a later node class may make differently.*
- One control plane, not three — chosen; alternative: an HA control plane; because this is a homelab and the recovery procedure in `docs/workflows/` is rehearsed.
- Secrets never live in the repo, even encrypted — chosen; alternative: sealed/encrypted secrets in-tree; because the out-of-cluster store already exists for other systems.

## Architectural Invariants

- **Manifests only in implementation directories.** `tofu/`, `talos/`, `platform/`, and `apps/` hold IaC and manifests, never prose docs. Prevents the tree from accreting stale READMEs that drift from the manifests. Documentation lives in the doc homes; a one-line pointer is the only allowed doc file in an implementation directory.
- **No hand-edited live state.** Changes land as commits and are reconciled. Prevents the cluster from diverging into a snowflake the repo can no longer rebuild.
- **Layer order holds.** A layer depends only on the layers below it (`apps` may assume `platform`, never the reverse). Prevents bootstrap cycles.

## ADR Index

| ADR | Status | Summary |
|---|---|---|
| `docs/decisions/0001-talos-over-kubeadm.md` | accepted | Talos for immutable, declarative nodes |
| `docs/decisions/0002-gitops-reconciler.md` | accepted | Reconcile the repo in-cluster rather than push from CI |
| `docs/decisions/0003-in-cluster-s3.md` | proposed | Object store choice for backups and app blobs |
| `docs/decisions/0004-uniform-cpu-baseline.md` | accepted | Mask guests to a common CPU baseline after the 2026-05 live-migration failure |

## Open Architecture Questions

- Do we replicate the object store offsite once total stored data exceeds a set threshold, or accept local-only backups?
- Does the Postgres operator own backups, or does the object store layer?

## Links

- Intent and anti-goals: `NORTH_STAR.md`
- Current work: GitHub Issues and/or `docs/plans/`
- Decisions: `docs/decisions/`
