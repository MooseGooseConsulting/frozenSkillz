# Notion control plane

The authoritative control surface is [Factory Mission Control](https://app.notion.com/p/3cbc4d261ef8817f9495e137c359e72f?pvs=204). It is the durable resume point for the controller; raw execution artifacts remain in Factory, Codex, GitHub, and the repository that produced them.

## Registers

| Register | One row means | Key fields |
|---|---|---|
| [Missions](https://app.notion.com/p/11d6b85a42e24987bd2f5e55f377c1fb) | One durable user outcome | Status, launch authority, desired outcome, scope/exclusions, source threads, repository/base, target, packet version, Factory mission link. |
| [Dispatches](https://app.notion.com/p/355f1110ea8b4cd6b9706115609304f6) | One external run, continuation, collection, review, or human handoff | Related Mission, kind, status, target, correlation, Factory session, review thread, PR/artifact, return summary, timestamps. |
| [Learning](https://app.notion.com/p/a1c97cc1d5ed47b2872834cf5143fbac) | One evidence-backed improvement candidate | Related Mission and Dispatches, failure class, status, evidence count, proposed change, regression fixture, holdout result, human decision. |

The database relationships are deliberate: a Mission has many Dispatches and Learning records, and Learning cites the Dispatches that support it. Do not replace those links with a prose-only narrative.

## State meaning

- **Intake / Prepared:** the mission exists but has not begun a Factory run.
- **Running / Waiting / Review:** live lifecycle states; link the relevant Dispatch and explain the reason for a wait.
- **Closed:** the requested acceptance path is satisfied and the return evidence is recorded.
- **Blocked:** the packet cannot advance without missing evidence or a human decision.
- **Not authorized / Explicit headless launch / Paused / Closed:** launch authority is distinct from Mission status. An explicit launch authorizes the named run, not future work.

Create a Dispatch before the action it represents. Update it with durable links and a concise return summary when the action changes state. Never put credentials, full secret-bearing logs, or transient terminal output into Notion.
