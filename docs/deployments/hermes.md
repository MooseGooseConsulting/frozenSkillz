# Hermes

Hermes is a standing service that consumes reviewed skills from this repository. It is a **runtime**, not a client: it has no packaging format and no plugin manifest, so it is not part of the `--consumer` enum. See [`../workflows/skill-authority-and-frozen-sync.md`](../workflows/skill-authority-and-frozen-sync.md) → **Skill Consumer Shapes**.

## How it consumes skills

The deploy script lives in `MooseGooseConsulting/coldaine-homelab` at `deployments/hermes/sync-frozen-skills.sh` and runs as root. It:

1. clones or refreshes this repository at `/srv/hermes/repos/frozenSkillz` to reviewed `origin/main`;
2. validates the current distribution;
3. materializes the `hermes-ops` deployment into `/srv/hermes/skill-sets/hermes-ops`; and
4. exposes that directory to the `hermes` container at `/opt/frozen-skills` as a read-only external skill directory.

Hermes reads bare `SKILL.md` directories from that path. Nothing renders a client package for it.

It consumes exactly `doppler` and `pdm-cli-operations`, expressed as the consumer-less `hermes-ops` deployment in `plugins/distribution.json`.

## Invocation

```sh
python3 scripts/sync_frozen_skills.py --check --deployment hermes-ops --destination /srv/hermes/skill-sets/hermes-ops --prune
python3 scripts/sync_frozen_skills.py --apply --deployment hermes-ops --destination /srv/hermes/skill-sets/hermes-ops --prune
```

`--destination` and `--prune` are mandatory for a deployment. Passing `--consumer` alongside `--deployment hermes-ops` is an error: the deployment declares no consumer because Hermes is not a client.

## Live distribution tracking

Hermes intentionally does **not** pin a frozenSkillz commit. The reviewed repository `main` branch is the deployment authority for active shared skills, and the homelab refreshes the `hermes-ops` deployment automatically. A commit SHA is recorded by each sync for traceability, but it is evidence of what was applied, not a gate that requires a second repository edit before a skill fix reaches the runtime.

The homelab-side synchronizer still fails closed on unsafe local state: it refuses a dirty or unexpected-origin checkout, validates the distribution before applying it, and treats unexpected destination content as a conflict. Those checks protect the synchronization boundary without freezing the runtime on an obsolete revision.

The standing homelab design uses a systemd timer to refresh the deployment frequently. Because Hermes reads external skills from the filesystem and loads skill content on demand, an ordinary reviewed skill-file update does not require a container rebuild. The homelab owns the exact refresh cadence, unit installation, mount checks, and operational evidence.
