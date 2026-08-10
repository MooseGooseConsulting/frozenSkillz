# Per-product wiring

Identity must be **launch-independent**. A shell wrapper (`AGENT_ID=x claude ...`) covers only agents
started from a terminal, and most are not: IDE plugins are started by the IDE, desktop apps by the
OS launcher, service agents by the init system. An agent launched from an application menu must
carry the same identity as one launched from a shell.

Every serious agent product exposes some static environment surface in its own configuration, and
child processes (`git`, `gh`) inherit it. That surface is the wiring point.

## The block

Each product sets the same values, differing only in agent key and bot identity:

```text
AGENT_GITHUB_IDENTITY = <agent key>
GIT_AUTHOR_NAME       = <slug>[bot]
GIT_AUTHOR_EMAIL      = <bot-user-id>+<slug>[bot]@users.noreply.github.com
GIT_COMMITTER_NAME    = <slug>[bot]
GIT_COMMITTER_EMAIL   = <bot-user-id>+<slug>[bot]@users.noreply.github.com
GIT_CONFIG_COUNT      = 2
GIT_CONFIG_KEY_0      = credential.helper
GIT_CONFIG_VALUE_0    =
GIT_CONFIG_KEY_1      = credential.helper
GIT_CONFIG_VALUE_1    = !<absolute path to the credential helper>
```

`GIT_CONFIG_VALUE_1` is an absolute path and names an interpreter, so it is **host-specific**. A
checkout at another location, or on another OS, needs its own value. Keep the helper script itself
path-independent so only this one value varies.

## Verified surfaces

**Claude Code** — the `env` map in `settings.json`. Project scope (`.claude/settings.json`) is
usually right: it scopes bot attribution to repositories where the fleet works, rather than to
everything the operator does on that machine.

```json
{ "env": { "AGENT_GITHUB_IDENTITY": "...", "GIT_AUTHOR_NAME": "..." } }
```

**Codex CLI** — the `[shell_environment_policy.set]` table in `~/.codex/config.toml`. Codex filters
the environment it passes to spawned shells, so variables must be declared here rather than merely
exported; this is exactly the case a shell wrapper fails to cover.

```toml
[shell_environment_policy.set]
AGENT_GITHUB_IDENTITY = "..."
GIT_AUTHOR_NAME = "..."
```

## Determining an unverified surface

Do not guess configuration keys. For any product not listed above, establish the surface before
wiring, then record what was verified:

1. Search the product's configuration reference for an environment map, an env allow/deny policy, or
   a terminal-environment setting. Editor-derived agents (VS Code forks and similar) commonly expose
   a `terminal.integrated.env.<platform>` map; desktop apps commonly expose a per-MCP-server `env`
   object; JetBrains plugins expose a tool environment.
2. Note whether the product **filters** the environment it passes to child processes. A product that
   passes the parent environment through inherits the block from however it was launched — which is
   convenient from a terminal and absent from a desktop launcher, so it still needs explicit
   configuration to be launch-independent.
3. Confirm with the product itself, not the config file: run `git var GIT_AUTHOR_IDENT` through the
   agent and check that it reports the bot.
4. Then run the full proof — commit, pull request, comment — through that product.

A product with no environment surface at all cannot be wired this way. Options are a wrapper on the
launcher itself, a per-repository local git config (which does not cover `gh`), or accepting that
the agent does not write to the forge directly.

## Service runtimes

For an agent running as a service, set the block in the unit's environment, sourced from the secret
store at start rather than written into a unit file. The identity variable and the git author values
are not secrets; the App private key is, and it should be reachable only through the secret store
that the minting command already uses.

## Verification status

Track which surfaces are proved. "Configured" is not "verified" — the failure mode is silent, so an
unverified row should be read as unknown, not as working.

| Product | Surface | Status |
|---|---|---|
| Claude Code | `settings.json` `env` | verified |
| Codex CLI | `config.toml` `[shell_environment_policy.set]` | verified |
| others | determine per the procedure above | record when proved |
