# Credential helper

Git authenticates pushes through credential helpers. Routing an agent's pushes through a helper that
mints its own installation token is what makes `git push` attribute to the agent with no wrapper
script and no stored long-lived credential.

## Why a helper rather than a stored token

- **Expiry.** Installation tokens last one hour. A token exported once at session start dies
  mid-session and surfaces as a confusing 401. A helper is invoked *per credential request*, so it
  mints fresh every time and session length stops mattering.
- **Concurrency.** Git spawns the helper as a fresh process inheriting the caller's environment.
  Several agents can run at once, each resolving its own identity from its own environment, with no
  shared runtime, lock, or daemon.
- **No durable secret.** Nothing long-lived is written to disk.

## Protocol contract

Git runs the helper with one argument — `get`, `store`, or `erase` — and writes `key=value` lines to
stdin, terminated by a blank line. For `get`, the helper answers on stdout with `username=` and
`password=` lines.

The behavioral rules matter more than the parsing:

- **Act only on `get`, only for the forge host, and only when the agent identity variable is set.**
- **Otherwise print nothing and exit 0.** Silence is how git moves on to the next helper. A helper
  that answers when it should not will hijack the operator's own authentication.
- **Drain stdin regardless of whether you act**, so git's pipe closes cleanly.
- **Fail loudly — nonzero, with a message on stderr — on a broken or unrecognized identity.** The
  tempting alternative, falling through silently, produces a push under whatever ambient credential
  exists. That is the misattribution this whole mechanism prevents.
- **Never write the token anywhere but stdout.**

## Helper ordering: why injection, not registration

Git consults credential helpers **in configuration order** and takes the first answer. Configuration
is layered system → global → local → command line.

On Windows, Git Credential Manager is registered in the **system** gitconfig. A helper added to the
user's global config is therefore consulted *after* GCM has already answered with the operator's
stored credentials — the agent helper never runs, and the failure looks like the helper being
broken. Resetting the helper list globally to fix that would break the operator's own
authentication.

The resolution is to inject configuration per process, which git supports natively:

```text
GIT_CONFIG_COUNT  = 2
GIT_CONFIG_KEY_0  = credential.helper
GIT_CONFIG_VALUE_0=                     # empty value resets the inherited helper list
GIT_CONFIG_KEY_1  = credential.helper
GIT_CONFIG_VALUE_1= !<absolute path to helper>
```

An empty `credential.helper` value is git's documented way to clear previously configured helpers.
Because this arrives as environment configuration, the reset applies **only** to processes carrying
these variables. The operator's shells are untouched — which is the acceptance criterion worth
testing explicitly.

The `!` prefix marks the value as an arbitrary command rather than a `git-credential-<name>` binary.

## Reference implementation (PowerShell)

```powershell
param([Parameter(Position = 0)][string]$Operation)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Drain stdin regardless of operation so git's pipe closes cleanly.
$attrs = @{}
while ($true) {
  $line = [Console]::In.ReadLine()
  if ([string]::IsNullOrEmpty($line)) { break }
  $i = $line.IndexOf('=')
  if ($i -gt 0) { $attrs[$line.Substring(0, $i)] = $line.Substring($i + 1) }
}

$identity = $env:AGENT_GITHUB_IDENTITY
if ($Operation -ne 'get' -or $attrs['host'] -ne 'github.com' -or [string]::IsNullOrEmpty($identity)) {
  exit 0   # not ours — stay silent so other helpers answer
}

try {
  $token = & (Join-Path $PSScriptRoot 'Get-AgentGitHubToken.ps1') -Agent $identity
  if (-not $token) { throw "empty token for '$identity'" }
} catch {
  [Console]::Error.WriteLine("agent credential helper: $($_.Exception.Message)")
  exit 1   # loud failure, never a silent fallback
}

Write-Output 'username=x-access-token'
Write-Output "password=$token"
```

Resolve the minting script relative to the helper (`$PSScriptRoot`, `$(dirname "$0")`) so the helper
itself stays path-independent and only the injected config value is environment-specific.

The username is the literal `x-access-token`; the installation token is the password.

## Testing the helper

Test every branch before trusting it — the dangerous branches are the ones that produce no output,
which is exactly what a silent misfire looks like:

| Operation | Host | Identity | Expected |
|---|---|---|---|
| `get` | forge | valid | `username=` + `password=`, exit 0 |
| `get` | forge | unset | no output, exit 0 (operator's helper answers) |
| `get` | forge | invalid | stderr message, exit 1 |
| `get` | other host | valid | no output, exit 0 |
| `store` / `erase` | forge | valid | no output, exit 0 |

The unset-identity row is the one that proves operator authentication is undisturbed.
