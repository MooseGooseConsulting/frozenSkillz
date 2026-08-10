# Attribution mechanics

How GitHub decides which account an object belongs to, and why two separate mechanisms must both be
wired before an agent's work attributes correctly.

## Half one: the installation token

Objects created through the API — pull requests, issue comments, reviews, releases, API-created
commits — are attributed to whoever the request's credential belongs to. A GitHub App installation
token resolves to that App's bot account, `<app-slug>[bot]`.

Installation tokens are minted, not stored:

1. Build an RS256 JWT signed with the App's private key: `iss` is the App ID, `iat` slightly in the
   past to absorb clock skew, `exp` at most ten minutes out.
2. `POST https://api.github.com/app/installations/{installation_id}/access_tokens` with
   `Authorization: Bearer <jwt>`.
3. The response `token` is valid for one hour and carries the installation's permissions.

The App ID is not the installation ID and neither is the bot user ID. All three are distinct
identifiers and all three are needed.

## Half two: the commit author email

Git commits are created locally, not by the API, so no credential is attached to them. GitHub
attributes a commit by matching its author email against emails registered to accounts. Push a
commit with a bot token but the operator's author email and the web UI shows the operator — the
push succeeded, nothing errored, and the history is wrong.

A bot's only usable address is:

```text
<bot-user-id>+<app-slug>[bot]@users.noreply.github.com
```

The bot user ID comes from the bot account, not the App:

```bash
gh api /users/<app-slug>%5Bbot%5D --jq '.id'
```

`%5B` and `%5D` are the escaped brackets; the literal `[bot]` suffix is part of the login.

Set both the author and the committer. Git treats them separately, and a commit created by
`git commit` with only `GIT_AUTHOR_*` set records the operator as committer:

```text
GIT_AUTHOR_NAME     = <app-slug>[bot]
GIT_AUTHOR_EMAIL    = <bot-user-id>+<app-slug>[bot]@users.noreply.github.com
GIT_COMMITTER_NAME  = <app-slug>[bot]
GIT_COMMITTER_EMAIL = <bot-user-id>+<app-slug>[bot]@users.noreply.github.com
```

## Verified badges and API-created commits

Commits created through the contents API (rather than `git commit` + push) are signed server-side by
GitHub and carry the "Verified" badge. Locally created commits are not signed unless the agent has a
signing key. Both attribute to the bot when the email is right; only the signature differs. Do not
treat the absent badge as an attribution failure.

## Proving it

Attribution is a server-side fact. Read it from the API, never from local config or the rendered
page:

```bash
gh api repos/{owner}/{repo}/commits/{sha} \
  --jq '{author: .author.login, author_email: .commit.author.email, committer: .committer.login}'
```

- `author.login` = `<slug>[bot]` — the email resolved to the bot account.
- `author.login` = `null` — the email matched no account at all. Almost always a malformed noreply
  address: wrong user ID, missing `[bot]`, or the App ID used in place of the bot user ID.
- `author.login` = the operator — the author email was never overridden.

For API-created objects:

```bash
gh api repos/{owner}/{repo}/pulls/{n} --jq '.user.login'
gh api repos/{owner}/{repo}/issues/comments/{id} --jq '.user.login'
```

A bot login appears as `app/<slug>` in some `gh` output shapes and `<slug>[bot]` in others. Both
denote the same account.

## Cleaning up proofs

Verification creates real objects. Delete test branches and close test pull requests as part of the
verification step, including when the test fails — a half-finished proof left on the default branch
is worse than no proof.
