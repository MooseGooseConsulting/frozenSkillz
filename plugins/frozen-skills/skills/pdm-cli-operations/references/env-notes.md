# Environment binding notes

Load this file **only** when binding `pdm-cli-operations` to a specific operator environment (launcher name, SSH runner, or install path). Do not treat these names as defaults for unrelated fleets.

## Binding checklist

| Binding | Where it lives | Skill expectation |
|---|---|---|
| PDM endpoint, TLS pin, auth ID, remotes/nodes | Owning ops repository | Read from there; never copy into this skill |
| Secrets / password command | Secrets-management skill + env vault | Load that skill only for direct credential or injection work; an opaque trusted launcher is ordinary PDM operation. Never place a password on Windows bridge argv. |
| Launcher executable name | Env-owned wrapper on the Linux runner | Set `PDM_CLI_REMOTE_PROGRAM` explicitly |
| Windows → Linux hop | Operator SSH config + `PDM_CLI_SSH_TARGET` | Pre-provision `known_hosts` / keys; bridge uses `BatchMode=yes` |
| Skill files on disk | Sync destination, marketplace plugin path, or repo checkout | Invoke `scripts/pdm.ps1` relative to that skill root |

## Example shape (replace with the environment's real names)

```powershell
$env:PDM_CLI_SSH_TARGET = 'operator@pdm-client-runner'
$env:PDM_CLI_REMOTE_PROGRAM = '<env-launcher-or-absolute-client-path>'
& "<skill-root>/scripts/pdm.ps1" --output-format json remote list
```

```sh
<env-launcher> --output-format json remote list
```

If the environment documents a Homelab-specific launcher (for example a wrapper that retrieves Doppler-backed credentials and seeds the TLS pin), use that name only after confirming it still invokes `proxmox-datacenter-manager-client` and preserves exit code and output.
