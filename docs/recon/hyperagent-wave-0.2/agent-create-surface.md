# Create-agent surface

Reached safely from `Use an agent → Create from scratch`; no text was entered and the disabled `Create Agent` control was never activated.

## Step flow

`Identity → Model → Tools & Integrations → Invocations → Knowledge`, with `Back`, `Previous`, and `Next` controls.

## Identity

- Prompt: “What should this agent do?” with a triage-inbox placeholder.
- Links: `Fill these in manually`, `Cast a personified agent`, `Draft identity`, `Edit agent avatar`.
- Right summary initially showed Model `Latest (Opus)`, Invocations `1 → Thread`, Integrations `0`, Tools `18`, Skills `0`, Memory `0`, Library `0`.

## Model

- Agent model default: `Opus 5 (Latest)`.
- Subagent model default: `Default (Sonnet 4.6)`; description says the agent may choose a different tier for a task.
- Subagent choices include `Default (Sonnet 4.6)`, `Parent model (Opus 5)`, and recommended Sonnet 4.6, Haiku 4.5, Opus 5, Fable 5; all Anthropic catalog entries are also available.
- Switches (all initially off): `Extended thinking`, `Fast mode` (2x token cost), `Budget limit per query`.

## Tools & Integrations

- `Integrations 0 active`; `Add Integrations`; empty-state says tools such as Airtable, Slack, or a custom MCP server can be added.
- `Tools 18 active`; `All` and `None` controls; same Research, Browser, Data, Interactive, and Media tool catalog as the thread composer.
- `Global tables across threads` checkbox was checked under Data Tables.
- Integration catalog was opened read-only; exact observed catalog is recorded in `integration-catalog.md`.

## Unexpanded steps

Invocations and Knowledge were not opened, because doing so was not needed to answer the model/tools/integration question and the form had no user input to preserve.

