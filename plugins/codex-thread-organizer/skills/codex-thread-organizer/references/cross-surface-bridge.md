# ChatGPT-to-Codex bridge

Use this only when both readable ChatGPT bodies and readable Codex task bodies
are available. It finds related work across the two surfaces; it does not rely
on either surface naming the same Project.

## Declare a bridge cohort

Do not compare unbounded ChatGPT or Codex histories by default. A bridge request
states the body-reviewed ChatGPT cohort, the Codex task cohort, and any
inventory-only candidates used to select them. Inventory-only titles or previews
cannot create, confirm, or rank a bridge.

## Compare actual work, not labels

Build the normal shared card for each body-reviewed source in the declared
bridge cohort, then compare body evidence for:

- the concrete problem or question;
- systems, repositories, files, issues, devices, services, or other artifacts;
- decisions, constraints, corrections, and requested outcomes;
- chronology that shows a decision or deliverable carried from one surface to
  the other.

A shared Project name is useful evidence but is neither required nor enough. A
matching title, sidebar preview, emoji, age, or topic word alone is not a
bridge.

## Record candidates honestly

For every candidate bridge, show both identities, the supporting body details
from each source, the common work claim, and one result:

| Result | Meaning |
| --- | --- |
| `confirmed` | Both bodies establish the same concrete work, artifact, decision, or handoff |
| `plausible` | The bodies indicate related work, but missing evidence prevents a firm claim |
| `unresolved` | The topic may overlap, but the available bodies cannot establish how |
| `no-link` | No material cross-surface relationship found |

Only `confirmed` bridges may inform a relationship or title proposal. A
`plausible` or `unresolved` bridge is presented for user judgment and causes no
rename, Project move, status marker, or lifecycle change. A bridge never
replaces the adapter-specific approval rules.

## Use in organization

Add a `Codex bridge` column to a ChatGPT evidence worksheet when Codex work is
in scope. It identifies the confirmed Codex task or reports the candidate result
and evidence. The corresponding Codex review records the ChatGPT conversation
symmetrically.

The desired outcome is retrieval: a user should be able to find the Codex task
from a ChatGPT discussion, or the ChatGPT answer from a Codex task, even where
neither originally used the Project name. Do not manufacture that connection.
