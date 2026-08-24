# Harness coverage and known gaps

This is an informational completeness map. The dimensions and gaps help answer “what do we know?”
and “what remains unverified?” They are not a required research procedure, promotion gate, or
instruction to change any live surface.

## Coverage dimensions

A well-characterized harness may have evidence for these independent dimensions:

1. **Identity and installation** — install channel, package/binary identity, installed version,
   update mechanism, and release notes.
2. **Launch surface** — commands/aliases, interactive and headless/CI modes, permission flags, and
   config-root environment overrides.
3. **Configuration precedence** — global/project files, environment overrides, formats, and which
   layer wins.
4. **Instruction/context files** — auto-read files, discovery order, and size limits.
5. **Skills** — discovery roots, supported format, shared-root support, and install/update behavior.
6. **Plugins/extensions** — plugin mechanism, marketplace/package source, and installed set.
7. **MCP** — global/project configuration, transports, and configured servers.
8. **Subagents/orchestration** — availability, definition, invocation, and parent/child identity.
9. **Hooks/automation** — lifecycle callbacks, event system, and scheduled/background behavior.
10. **Models and providers** — supported backends, selection rules, OpenRouter/local-model support,
    and whether raw sessions record provider/model identity.
11. **Authentication and secrets** — auth flow, sensitive stores, secret ownership, and scoped
    Doppler use.
12. **Session/data stores** — raw location and format, retention, identity stability, and downstream
    parser coverage. Raw facts live in [the transcript catalog](transcripts-and-fields.md).
13. **Sandboxing and permissions** — default capabilities and restriction/expansion controls.
14. **Web capabilities** — built-in search/fetch tools and their configuration.
15. **Known workstation issues** — observed warnings or ambiguity, dated and separated from upstream
    product behavior.
16. **Diagnostics** — commands that identify the active version, paths, and resolved surface without
    exposing credentials.

## Per-harness ledger

States below combine the recovered 2026-06/07 Atlas snapshot with corrections made through
2026-08-24. “Open” means not established by the evidence currently cited here.

### Claude Code and OMC

- Known: launcher/profile split, two config roots, dated version checks, current raw transcript
  metadata, and OMC package name.
- Open: full config precedence; hooks and MCP locations/semantics; headless/CI behavior; OMC upstream
  release/update contract and the exact surface it modifies.

### Codex

- Known: dated CLI/config snapshot, top-level settings, plugin/session/auth locations, and current raw
  rollout fields.
- Open: full current `config.toml` schema; the writer/meaning of the `.omc` marker seen under sessions;
  rules, hooks, automations, and memories semantics; complete headless/MCP behavior; root cause or
  suppression of the dated `morph-mcp` mismatch warning.

### Cursor

- Known: dated global MCP/config snapshot, global-first workstation report, raw transcript family,
  and separate IDE/`cursor-agent` identities.
- Open: complete `cursor-agent` capabilities/version; `skills` versus `skills-cursor`; project rule
  format/layout; worktree behavior; whether the setup report's installed-but-unused surface remains.

### Gemini CLI and Antigravity

- Known: shared `.gemini` configuration root, settings/context/extension/trust surfaces, distinct
  client identities, and current raw-format families.
- Open: why the dated scripted `gemini --version` returned no text; exact Gemini/Antigravity
  responsibility split; extension and trusted-hook/policy semantics; current configured MCP server
  set.

### OpenCode and oh-my-openagent

- Known: dated CLI/config roots, profile/provider/agent/skill/LSP surfaces, OpenCode-family raw store,
  and provider/model fields.
- Open: oh-my-openagent upstream/update contract; profile semantics; which listed providers are
  active; whether timestamped backup files are still relevant; current behavior of each
  orchestration setting.

### Kilo Code

- Known: Kilo `7.4.23` CLI/config root, config shape, plugin SDK and hook callback surface, current
  OpenCode-family raw store, and legacy-extension boundary.
- Open: active configured plugin module/implementation location when `plugin` is absent; exact skill
  discovery contract; current provider/model selection behavior; whether older `.kilo` and
  `.kilocode` skill roots are read or vestigial.

### GitHub Copilot CLI

- Known: dated CLI/config snapshot, agents/hooks/skills directories, raw event family, and GitHub CLI
  auth relationship.
- Open: semantics of the agents/hooks directories; MCP support; model/provider selection and raw
  identity fields; exact relationship between CLI and VS Code Copilot session/config surfaces.

### Goose

- Known: dated CLI/version and candidate config root.
- Open: current Windows config file, provider setup, extensions/MCP, skills/hooks, raw session store,
  and model/provider/usage fields.

### Qwen Code

- Known: `.qwen` root existed in the dated survey, current producer/parser format is documented, and
  no CLI or chats were found in the older workstation survey.
- Open: whether Qwen Code is currently installed/in use, active configuration precedence,
  hooks/skills/MCP, and current local session presence.

### OpenRouter

- Known: provider/router rather than harness; dated OpenCode availability and secret-store
  boundaries.
- Open: which installed harnesses can use it, which currently do, and the owning Doppler
  project/config and secret name (names only).

### Additional inventory not yet characterized

- `C:\Users\pmacl\.continue\skills` exists and currently contains `gws-gmail`, `gws-gmail-read`,
  `gws-gmail-send`, and `gws-shared`; whether Continue is installed or this is vestigial remains
  unknown.
- Kimi CLI/Kimi Code raw `wire.jsonl` is characterized, including provider/model field paths, but
  installation, launch, config precedence, hooks, skills, MCP, and current provider selection are
  not covered.
- VS Code as an agent host for Copilot Chat/extensions is not independently characterized.
- Client-by-client support for `C:\Users\pmacl\.agents\skills` remains only partially verified; the
  existence of the shared root does not prove discovery by every harness.
