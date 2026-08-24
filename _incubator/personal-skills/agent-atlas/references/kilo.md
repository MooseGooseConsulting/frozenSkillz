# Kilo Code

Configuration and CLI checked locally 2026-08-24 with Kilo `7.4.23`. Verify live state for later
versions.

## Identity

Kilo Code is the client/harness. `@kilocode/plugin` is its plugin SDK/package, not the client,
provider, or model. Provider and model selection are separate configuration/session metadata.

- CLI: `kilo` -> `C:\Users\pmacl\AppData\Roaming\npm\kilo.ps1`, version `7.4.23`.
- `kilo debug paths` reports config root `C:\Users\pmacl\.config\kilo` and live config file
  `kilo.json` exists there.
- The older `C:\Users\pmacl\.kilo` and `C:\Users\pmacl\.kilocode` roots are not the config root
  reported by current Kilo.

In the 2026-07-07 snapshot, both older roots existed with `skills\` directories and identical
`package.json` files depending on `@kilocode/plugin@7.2.20`. That historical duplication explains
the older canonical-root question, but it does not establish that Kilo `7.4.23` reads either root.
Whether their skill directories are still discovered or are vestigial remains unknown.

## Config surface

Names-only inspection of `kilo.json` found top-level configuration for schema, model/provider,
agents, permissions, defaults, experimental features, compaction, MCP, and related client behavior.
The local file contained no top-level `plugin` key at inspection time. `kilo config check` returned
no warnings.

The config root also contains `agent\`, `node_modules\`, and `package.json`. Names-only package
inspection found `@kilocode/plugin` as the dependency.

## Plugin and hook surface

`kilo plugin <module>` installs an npm module and updates configuration; `--global` selects the
global config and `--pure` starts Kilo without external plugins. The installed
`@kilocode/plugin` types define an optional config `plugin` array whose entries are module names or
module/options pairs.

Plugins return a `Hooks` object. The current SDK type surface includes general event/config/tool,
auth, and provider hooks plus named callbacks such as `chat.message`, `chat.params`,
`chat.headers`, `permission.ask`, `command.execute.before`, `tool.execute.before`,
`tool.execute.after`, and `shell.env`.

No standalone hook config key or hook-named path outside dependencies was present in the inspected
config root. Hook implementations therefore belong to configured plugin modules, but the active
module/implementation location is unknown when the `plugin` key is absent. Do not promise a fixed
`hooks\` directory.

For names-only diagnosis without resolving or printing configuration values:

```powershell
kilo debug paths
kilo config check
kilo plugin --help
Get-ChildItem "$env:USERPROFILE\.config\kilo" -Recurse -Force |
  Where-Object { $_.FullName -notmatch '\\node_modules\\' -and $_.Name -match 'hook' } |
  Select-Object FullName
```

`kilo debug config` prints resolved configuration values and is not a names-only diagnostic.

## Diagnostics

```powershell
kilo --version
kilo debug paths
kilo config check
kilo debug skill
```

The canonical current/legacy transcript locations and raw fields are in
[Raw transcripts and field availability](transcripts-and-fields.md). Use `chat-history` for
retrieval.
