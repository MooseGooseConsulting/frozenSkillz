# Environment binding notes

Load this file **only** when binding `pdm-cli-operations` to a specific operator environment (direct adapter, launcher name, SSH runner, or install path). Do not treat these names as defaults for unrelated fleets.

## Binding checklist

| Binding | Where it lives | Skill expectation |
|---|---|---|
| PDM endpoint, TLS pin, auth ID, remotes/nodes | Owning ops repository | Read from there; never copy into this skill |
| Secrets / password command | Secrets-management skill + env vault | Load that skill; no password on Windows bridge argv |
| Direct PDM adapter | Env-owned workstation/agent wrapper | Use its documented read/mutation surface and independently pinned TLS; it need not invoke the official CLI |
| Launcher executable name | Env-owned wrapper on a Linux runner | Set `PDM_CLI_REMOTE_PROGRAM` explicitly only when this route is selected |
| Windows → Linux hop | Operator SSH config + `PDM_CLI_SSH_TARGET` | Optional legacy/CLI bridge only; do not add it when a documented direct adapter exists |
| Optional Windows CLI bridge files | Sync destination, marketplace plugin path, or repo checkout | Invoke `scripts/pdm.ps1` relative to that skill root only when the official-client bridge route is selected |

## Official-client bridge shape (replace with the environment's real names)

```powershell
$env:PDM_CLI_SSH_TARGET = 'operator@pdm-client-runner'
$env:PDM_CLI_REMOTE_PROGRAM = '<env-launcher-or-absolute-client-path>'
& "<skill-root>/scripts/pdm.ps1" --output-format json remote list
```

```sh
<env-launcher> --output-format json remote list
```

If the environment documents a direct Homelab PDM reader (for example a wrapper that retrieves Doppler-backed credentials and verifies a PDM TLS pin), use that reader directly for its declared operations. It is a supported PDM entrypoint, not an invitation to rebuild an SSH runner or to widen the adapter beyond its documented capability.
