# Inventory: obra/superpowers tooling reference

## Provenance

- Source URL: <https://github.com/obra/superpowers>
- Reference point: `v6.1.1` / `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Import date: 2026-07-23
- License: MIT
- Scout path: `_incubator/scout/2026-07-23-obra-superpowers/`

## Retained reference surface

This is a deliberately reduced reference bundle. It does not contain upstream skill bodies or
`SKILL.md` files.

| Type | Retained material |
|---|---|
| Plugin metadata | `.agents/plugins/marketplace.json`, `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.kimi-plugin/`, `gemini-extension.json` |
| Harness adapters | `.opencode/` and `.pi/` extensions; harness README and porting documentation |
| Hooks | `hooks/hooks.json`, `hooks/hooks-cursor.json`, `hooks/session-start`, `hooks/run-hook.cmd` |
| Packaging/tooling | `package.json`, version/lint/package/sync scripts, pre-commit configuration |
| Tests | Cross-harness, plugin-sync, brainstorm-server, explicit-request, and shell-lint tests |
| Reference docs | upstream README, release notes, plans/specs, license, and captured project policy files |

The upstream skill payload was intentionally excluded because this repository is retaining the
plugin and tooling reference, not adopting or staging the skills themselves.
