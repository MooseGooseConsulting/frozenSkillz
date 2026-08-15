# PDM CLI operations evals

Labeled prompts for description routing. See `triggers.json`.

## How to run

1. Use a fresh agent session per prompt with no prior PDM context.
2. Record whether `$pdm-cli-operations` (or equivalent) was loaded.
3. Score: trigger rate >= 0.5 when `should_trigger` is true; < 0.5 when false.
4. Do not rewrite the skill description solely to fit the validation split.

## Behaviors the eval set should protect

Positive coverage should include:

- normal PDM fleet inventory and guest/PBS operations;
- task completion and post-state verification;
- PDM authentication/TLS troubleshooting;
- **routing an operation to native PVE/PBS when current PDM does not expose it**;
- native diagnosis when PDM localizes a failure to one remote; and
- native recovery when PDM itself is unavailable.

Negative coverage should exclude:

- generic Linux/app/cloud work unrelated to Proxmox;
- questions that are purely about one already-selected native command and do not involve fleet/PDM routing;
- installing WSL/containers merely to manufacture a PDM client environment; and
- adding a new MCP/proxy/control service when the user is not asking to evaluate or deploy one.

Do **not** mark native PVE/PBS itself as a negative. Native drill-down is part of the intended PDM-first control hierarchy; the distinction is whether the skill is needed to route/manage the fleet operation.
