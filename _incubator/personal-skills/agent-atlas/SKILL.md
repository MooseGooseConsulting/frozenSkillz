---
name: agent-atlas
description: "Factual router for explicit questions about an agent client or harness itself: installation, launch commands, configuration, hooks, skills, raw transcript storage or format, provider/model metadata, and diagnostics. Use for Claude Code or OMC, Codex, Cursor, Copilot CLI, Gemini CLI or Antigravity, OpenCode, Kilo, Kimi, Goose, Qwen Code, and OpenRouter routing. Do not use for ordinary coding performed inside those tools or for locating, retrieving, or analyzing prior conversations; use chat-history for cross-session retrieval."
---

# Agent Atlas

Route a question about an agent tool to the smallest relevant reference. This skill records
workstation-specific facts and known unknowns; it is not a configuration workflow or an authority
hierarchy.

Keep these identities separate:

- A **client or harness** is the application that launches the agent and owns configuration or
  session data, such as Codex, Claude Code, or OpenCode.
- An **extension or orchestration layer** modifies a harness, such as OMC for Claude Code or
  oh-my-openagent for OpenCode.
- A **provider** supplies model inference, such as Anthropic, OpenAI, Google, or OpenRouter.
- A **model** is the selected model identifier. A harness name, provider name, and model name are
  not interchangeable, and many raw transcript formats do not expose all three.

Use the dated facts as discovery hints. For a question about what is installed or active now,
inspect the named live surface or run the reference's diagnostic command. Treat auth files as
sensitive: locations and field names are useful; secret values are not.

## References

- [Workstation map](references/workstation-agent-config-map.md) — client/harness classification,
  launch/config roots, and shared skill surfaces.
- [Claude Code and OMC](references/claude-omc.md)
- [Codex](references/codex.md)
- [Cursor](references/cursor.md)
- [GitHub Copilot CLI](references/copilot-cli.md)
- [Gemini CLI and Antigravity](references/gemini-antigravity.md)
- [OpenCode and oh-my-openagent](references/opencode.md)
- [Kilo Code](references/kilo.md)
- [Goose](references/goose.md)
- [Qwen Code](references/qwen.md)
- [OpenRouter](references/openrouter.md) — provider routing, not a standalone agent client.
- [Raw transcripts and field availability](references/transcripts-and-fields.md) — canonical raw
  locations, formats, and verified/unknown fields, including Kimi CLI and Kimi Code.

If the actual goal is to find or analyze a previous conversation, stop at identifying the likely
client/harness and hand the task to `chat-history`. Do not reproduce its search, fallback, or raw
recovery procedures here.
