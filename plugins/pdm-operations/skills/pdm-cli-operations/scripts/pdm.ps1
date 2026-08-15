[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $CommandArgs
)

# Optional Windows adapter: forwards argv to an environment-owned Linux runner.
# Login/secrets stay on the runner - this script must never carry password flags.

$target = $env:PDM_CLI_SSH_TARGET
if ([string]::IsNullOrWhiteSpace($target)) {
    throw 'Set PDM_CLI_SSH_TARGET to the authorized SSH runner for the official PDM client.'
}
if ($target.StartsWith('-') -or $target -notmatch '^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+$') {
    throw 'PDM_CLI_SSH_TARGET must be user@host (DNS or IPv4). Set SSH port via ~/.ssh/config, not user@host:port.'
}

$remoteProgram = $env:PDM_CLI_REMOTE_PROGRAM
if ([string]::IsNullOrWhiteSpace($remoteProgram)) {
    throw 'Set PDM_CLI_REMOTE_PROGRAM to the environment launcher or absolute path of proxmox-datacenter-manager-client on the runner.'
}
# Bare executable name, or absolute POSIX path. Reject relative paths, ., .., and option-like names.
if (
    $remoteProgram.StartsWith('-') -or
    $remoteProgram -eq '.' -or
    $remoteProgram -eq '..' -or
    $remoteProgram -match '(^|/)\.\.(/|$)' -or
    $remoteProgram -notmatch '^([A-Za-z0-9_-]+|/([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*))$'
) {
    throw 'PDM_CLI_REMOTE_PROGRAM must be one bare executable name or an absolute POSIX path (no relative segments).'
}

function ConvertTo-PosixSingleQuoted {
    param([Parameter(Mandatory = $true)][string] $Value)
    $apostrophe = [string][char]39
    $doubleQuote = [string][char]34
    $replacement = $apostrophe + $doubleQuote + $apostrophe + $doubleQuote + $apostrophe
    return $apostrophe + $Value.Replace($apostrophe, $replacement) + $apostrophe
}

if (-not $CommandArgs -or $CommandArgs.Count -eq 0) {
    $CommandArgs = @('help')
}

# Credentials belong on the runner. Forwarding these would expose them on the Windows ssh argv.
$blockedPasswordFlags = @('--password', '--password-file', '--password-command')
foreach ($arg in $CommandArgs) {
    $flag = ($arg -split '=', 2)[0]
    if ($flag -in $blockedPasswordFlags) {
        throw 'Refuse password-related flags on the Windows bridge. Perform login with secrets only on the SSH runner (environment launcher or raw client there).'
    }
}

$remoteCommand = @(
    (ConvertTo-PosixSingleQuoted $remoteProgram)
    $CommandArgs | ForEach-Object { ConvertTo-PosixSingleQuoted $_ }
) -join ' '

# BatchMode fails closed instead of hanging on host-key or password prompts.
& ssh -o BatchMode=yes $target $remoteCommand
if ($null -eq $LASTEXITCODE) {
    exit 1
}
exit $LASTEXITCODE
