---
name: agent-github-identity
description: Give each AI agent its own GitHub App bot identity so its commits, pull requests, reviews, and comments attribute to that agent, not to a shared account or the operator. Use when wiring an agent's GitHub write path or before any agent GitHub write. Not for human or CI credentials.
---

# Agent GitHub Identity

An agent that writes to GitHub under the operator's credentials produces an unauditable history: no
one can tell later which actor made a change, or whether a human reviewed it. Give each agent its
own GitHub App, installed on the owning organization, and route that agent's git and API traffic
through it.

This skill is the mechanism. The inventory — which agents exist, their App IDs, installation IDs,
bot user IDs, secret names, and script paths — belongs to the environment's canonical operational
repository. Never copy that inventory here.

## The two halves

GitHub attribution has two independent halves. An implementation that handles only one *silently
misattributes* rather than failing, which is why this is worth stating before any wiring:

1. **The installation token** identifies the agent on API-created objects — pull requests, issue
   comments, reviews — and governs what it may do.
2. **The commit author email** is what the web UI resolves for commit authorship. A commit pushed
   with a bot token but authored with the operator's email still renders as the operator.

Both must be set. See [attribution mechanics](references/attribution-mechanics.md) for how GitHub
resolves each, the bot noreply address format, and the API queries that prove attribution.

## Operating Contract

- Load the environment's secrets-management skill (`$doppler` in a Doppler-backed environment)
  before handling App credentials. App private keys are secrets; they live in the secret store and
  nowhere else.
- Resolve the agent roster, App IDs, installation IDs, bot user IDs, and helper script paths from
  the environment's canonical operational repository.
- Mint installation tokens **per credential request**, not per session. Installation tokens expire
  after one hour; minting on demand makes session length irrelevant and avoids a stale-token failure
  mode that looks like a permissions problem.
- Set the commit author *and* committer to the bot's noreply address. Setting only the author leaves
  the committer as the operator.
- Inject git configuration per process (`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n`),
  never by writing a shared gitconfig. A credential helper registered globally changes the
  operator's own authentication and, on Windows, will not even be reached — see
  [the credential helper reference](references/credential-helper.md).
- Identity must be launch-independent. Agents run as CLIs, IDE plugins, desktop apps, and services;
  a shell wrapper only covers the first. Use each product's own environment configuration surface —
  see [per-product wiring](references/per-product-wiring.md).
- `gh` does not consult git credential helpers. Every `gh` write needs an explicitly minted
  `GH_TOKEN`, and an empty `GH_TOKEN` is treated as absent — `gh` then falls back to the operator's
  stored login. Guard the mint and fail loudly.
- Never print, log, echo, or commit a token or private key. Tokens are short-lived, not harmless.
- Never unset the agent-identity variable to push as the operator. If operator attribution is
  genuinely required, stop and ask the operator to run it.
- A credential helper must stay silent for requests it does not own (other hosts, `store`/`erase`,
  no agent identity set) so other helpers still answer, and must fail **loudly** on a broken
  identity rather than degrading to anonymous or ambient auth.

## Workflow

1. Read the environment's operational repository for the agent roster and secret names.
2. Register one GitHub App per agent on the owning organization with the least permissions the
   agent's work requires — typically `contents:write`, `issues:write`, `pull_requests:write`,
   `metadata:read`. Install it, then record App ID, installation ID, and bot user ID.
3. Store the App ID, private key, installation ID, and bot user ID in the secret store.
4. Provide a token-minting command: sign an RS256 JWT with the App private key, exchange it at
   `POST /app/installations/{id}/access_tokens`, return the token.
5. Provide a git credential helper that mints per request for the forge host when the agent identity
   variable is set, and is silent otherwise.
6. Wire each agent product's environment surface with the identity variable, the `GIT_AUTHOR_*` and
   `GIT_COMMITTER_*` pair, and the `GIT_CONFIG_*` helper injection.
7. Verify per agent, **through that agent's own product** rather than a hand-built environment —
   the point is to test the product's wiring, not to simulate it. Prove a pushed commit, a pull
   request, and an issue comment each resolve to the bot.
8. Delete every test branch and close every test pull request, including on failure.

## Verification

Attribution is verified through the API, never by reading the UI or trusting the local config:

```bash
gh api repos/{owner}/{repo}/commits/{sha} --jq '{author: .author.login, email: .commit.author.email, committer: .committer.login}'
gh api repos/{owner}/{repo}/pulls/{n}    --jq '.user.login'
gh api repos/{owner}/{repo}/issues/comments/{id} --jq '.user.login'
```

Each must return the `<slug>[bot]` account. A commit whose `author.login` is null resolved against
no account — the author email is wrong. `git var GIT_AUTHOR_IDENT` shows what the current process
would write, which is the fastest local check that a product's wiring actually reached the agent.

## Failure modes

| Symptom | Cause |
|---|---|
| Objects attribute to the operator, no error | `GH_TOKEN` unset or empty; `gh` used ambient auth |
| Commit shows operator, PR shows bot | Author/committer email not set; only the token half is wired |
| Commit author has no linked account | Email is not the bot's exact noreply address |
| Push prompts for a password | Helper failed or was never reached; check helper ordering |
| Worked for an hour, then 401 | Token minted once per session instead of per request |
| Operator's own git breaks | Helper registered in a shared gitconfig instead of injected per process |

## References

- [Attribution mechanics](references/attribution-mechanics.md) — the two halves, bot email format, proving it.
- [Credential helper](references/credential-helper.md) — protocol contract, helper ordering, reference implementations.
- [Per-product wiring](references/per-product-wiring.md) — environment surfaces for CLI, IDE, desktop, and service agents.
