# Homelab / coldaine operational notes

Load this file **only** when the task involves coldaine-infra, ESO/`ClusterSecretStore`, Shipwright, or GHCR PAT wiring. Do not apply these project names or patterns to unrelated repos.

## 2026-06-29

### What Worked

- Reuse one **classic** GitHub PAT (`GHCR_BUILD_TOKEN`) for both GHCR push (`kubernetes.io/dockerconfigjson` → `ghcr-push`) and Shipwright private-repo clone (`kubernetes.io/basic-auth` → `git-clone`). No separate `GITHUB_CLONE_TOKEN` if the PAT has `repo` + `write:packages`.
- Boolean Doppler checks without printing values: `doppler secrets get KEY -p PROJECT -c CONFIG --plain 2>$null` then test `$LASTEXITCODE` and `[string]::IsNullOrWhiteSpace($v)` / `$v.Length` — never echo the value.
- `doppler secrets --only-names` across projects to reconcile manifest `remoteRef.key` names vs vault (e.g. `LLM_ARCHIVAL_DB_PASSWORD` vs `LLMARCHIVER_DB_PASSWORD`).
- Audit scripts must call seed/bootstrap helpers with **read-only** flags (`-ReadOnly`); audits that invoke writers mutate production state.

### What Failed

- Assuming credentials are missing before a Doppler names/existence audit — many keys already existed under `databases/dev` or `coldaine-k8s/dev_homelab`.
- Fine-grained GitHub PAT UI for GHCR — **no** `write:packages` under per-repo permissions; use a **classic** PAT for `ghcr.io` push.
- Treating `SOPS_AGE_KEY` as the age decrypt key when it was truncated; use `AGE_PRIVATE_KEY` when present and valid (`StartsWith('AGE-SECRET-KEY')`).

### Configuration Notes

- ESO `ClusterSecretStore` only sees secrets in the **service token's** Doppler project/config. Keys in other projects (e.g. `secrets_managment/dev` for Proxmox, `databases/dev` for legacy names) require token scope alignment or manifest key migration to the cluster project (`coldaine-k8s/dev_homelab`).
- Shipwright git clone failure (`could not read Username for 'https://github.com'`) is usually missing `spec.source.git.cloneSecret`, not a missing Doppler key — check wiring before creating new keys.
- If user pastes a token in chat: store via `doppler secrets set ... --silent`, verify ESO sync, warn about rotation — do not repeat the token in the response.
