# Mission packet

Use this reference only when a conversation is being prepared for Factory execution or re-scoped after a pause.

## Required packet fields

| Field | What it resolves |
|---|---|
| Desired outcome | The observable result, not a proposed implementation. |
| Source threads | The specific Codex/ChatGPT conversation links and messages that support the mission. |
| Scope and exclusions | What the worker may do, and what it must not change. |
| Repository and base revision | The repository/ref plus an immutable starting revision or equivalent source snapshot. |
| Target | The selected registered Droid computer or other named execution surface. |
| Validation | The commands, checks, or observable behavior that decide whether the outcome is met. |
| Return path | Where execution evidence, PR/artifact links, and independent review will be recorded. |
| Stop conditions | Which changes require a pause: target, scope, autonomy, deployment/data actions, policy, or unavailable control plane. |

Store the durable fields in the Mission row and its page body. Use a packet version when a paused mission is intentionally revised; do not overwrite the old scope without saying what changed and why.

## Mandatory minimum before an explicit headless launch

1. The Mission is linked to its actual source conversation(s), has a clear outcome, and has no unresolved contradiction.
2. Its scope, exclusions, selected target, base revision, and validation are stated.
3. The Mission records **Explicit headless launch** authority for the current run.
4. A Factory-mission Dispatch exists before starting the run and names the expected return evidence.
5. The run is bounded by the packet and uses high autonomy only; unsafe permission-bypass mode is forbidden.

## Preflight branch

Preflight is optional, but when selected it is confined to facts that determine whether the packet is actionable:

- source/base still exists and is the intended work surface;
- selected target is available and has the necessary runtime/dependency shape;
- named validation can actually be run or the limitation is recorded;
- the proposed work does not cross a stop condition.

Preflight reports **ready**, **blocked**, or **needs packet change**. It does not launch a mission, mutate a runtime, or approve an exception.
