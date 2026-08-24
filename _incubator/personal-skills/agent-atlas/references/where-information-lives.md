# Where agent-tool information lives

Use this map when the question is where a fact is recorded. The rows describe different kinds of
information; they are not a precedence order, a required sequence, or authorization to edit a
surface.

| Information kind | Location | What it can establish |
|---|---|---|
| Current runtime/configuration state | The named live CLI, config file, profile, registry key, extension setting, package directory, or diagnostic command | What is installed, configured, enabled, or emitted now. Dated Atlas observations are only discovery hints when a live check is cheap. |
| Durable workstation policy | `D:\_projects\coldaine-configurations\configurations\2026-07-07-agent-tool-configuration-policy.md` | The recorded workstation design as of that policy revision, including the deliberate Claude Code/OMC profile split. It may lag current runtime state. |
| Reviewed active skills | `D:\_projects\frozenSkillz\plugins\frozen-skills\skills` and active package/distribution metadata | Reviewed repository source for skills in the active distribution; not proof that a particular client has synchronized or loaded them. |
| Gated/personal skill review copies | `D:\_projects\frozenSkillz\_incubator\personal-skills` and `docs\skill-review\tracker.md` | Review status and durable incubator copies. `_incubator` is not an installed runtime root. |
| Live personal skills | `C:\Users\pmacl\.agents\skills` plus client-specific compatibility roots | Personal skill source/discovery material. Whether a given client reads this root is a per-client fact, not a universal contract. |
| Session learnings and reverse engineering | `D:\_projects\agent-control-plane`; detailed format notes under `capture\scratch` | Cross-project learnings and observed reconstruction notes. Despite its name, this is a reference/learnings store, not the live control plane or raw-transcript authority. |
| Current raw transcript formats | [Raw transcripts and field availability](transcripts-and-fields.md), backed by named producer/AgentsView evidence | Canonical Atlas map of raw locations and verified/unknown fields. Use `chat-history` when the task is retrieval rather than format explanation. |
| Older downstream parser catalog | `D:\_projects\llm-archiver\tools\*.yaml` | Historical normalization/parser leads for several harnesses. This catalog is stale/downstream and must not override current raw producer or AgentsView evidence. |
| Secret ownership and scoped retrieval | Doppler, using the `doppler` skill/CLI when values are actually required | Secret name, owning project/config, consuming tool, and scoped injection. Do not place secret values in this atlas, policy docs, or repository inventories. |

Useful reverse-engineering notes observed in the original Atlas include
`D:\_projects\agent-control-plane\capture\scratch\opencode-session-reconstruction.md` and
`qwen-session-reconstruction.md`. Their existence is a research pointer, not proof that the notes
still match the latest harness release.
