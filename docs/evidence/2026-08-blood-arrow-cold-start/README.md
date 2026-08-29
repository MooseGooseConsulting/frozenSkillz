# Blood Arrow cold-start proof — investigation evidence

Primary-source investigation reports backing two analyses:

- **MooseGooseConsulting/bloodarrow-ops#66** — single-queue virtio-net capping host↔guest transfer
- **MooseGooseConsulting/bloodarrow-ops#67** — artifact transfer emulating a network between a host and its own guest

Subject: a DeepSeek V4 Flash cold-start proof run on the Blood Arrow host and its `vast-ubuntu` guest, 2026-08-26 → 2026-08-29 (Codex session `01a03ed4-d36a-7333-9548-7b7d8fc6ee32`).

These are **reference documents, not instructions.** Nothing here should be treated as guidance to an agent. They exist so the conclusions in the linked issues can be checked against primary evidence rather than taken on trust.

## Contents

| File | Question it answers | Headline |
|---|---|---|
| `A-transfer-limiter.md` | What limited the registry pull to ~1.35 GB/s? | One `vhost-net` kernel thread on a single-queue virtio NIC, at 88.9% of its demonstrated ceiling. No physical NIC in the path. |
| `B-unpack-limiter.md` | Why did extraction take 577 s on a 64-core machine? | One single-threaded gzip stream at a time; ~1.2 of 64 cores busy. zstd would be 2.5–2.7× faster *and* marginally smaller on the wire. |
| `C-bakeable-state.md` | Why can pre-baking recover so little? | CUDA graphs are unserialisable by CUDA itself; ceiling for any filesystem-only bake is 17–19 s of a 1,124 s start. Also finds 101.74 s of measurement artifact. |
| `D-telemetry.md` | Was the run clean, and what telemetry exists? | Zero errors, tracebacks, retries or fallbacks. Full container logs existed on disk the whole time and were never surfaced. |
| `E-plan-artifacts.md` | Did a plan ever exist as a file? | No. Codex Plan Mode disallows the persistence mechanism, so every plan lived only as chat text and was destroyed by ten compactions. |
| `F-flowcharts.md` | What diagramming was requested, and what came back? | ~20 diagrams across 4 episodes. "Local transfer" was rendered as an SSH-tunnelled registry push. One diagram of ~20 was ever persisted. |

## Method and limits

Reports A, B and D were produced by read-only inspection of the live host and guest plus the session transcript. C combines transcript reconstruction with external research. E and F are transcript analyses.

Each report carries its own "could not determine" section. Notable unresolved items:

- Whether gzip is also a co-limiter of the transfer phase — the decisive test needed credentials the investigation declined to escalate for.
- Whether Vast's control plane validates layer media types, which gates the zstd recommendation.
- Whether a Vast owner instance can receive a host-backed bind mount, which gates all of #67.

Figures quoted in the issues trace to these reports. Where a number is derived rather than measured, the report says so.
