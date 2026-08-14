---
name: unifi-udm-access
description: >-
  Use when reading or changing configuration on a self-hosted UniFi console
  (UDM, Dream Machine, Cloud Key) — SSIDs, VLANs, firewall rules, local DNS, IPS
  settings, device and client state — or when a UniFi API call 404s and the right
  surface is unclear. Not for UniFi Protect, Access, or cloud controllers.
---

# UniFi Console Access Routing

A UniFi console exposes four access surfaces. They are **not** tiers of one API — they are disjoint,
with different base paths, different site identifiers, different response envelopes, and different
capabilities. Each owns things the others cannot reach at all.

The consequence: **a 404 tells you nothing except that this surface lacks this path.** The same fact
may be freely readable one surface over. Most time lost on UniFi automation is spent concluding a
feature doesn't exist after probing exactly one surface.

Route by which surface *owns* the fact, not by which is newest.

## Operating Contract

- Load the applicable secrets-management skill before handling authentication. The API key and the
  console SSH password are separate secrets with very different blast radius — the second is root on
  the device carrying all traffic.
- Resolve the console address, site identifier, device inventory, and credential names from the
  owning environment. Do not copy environment inventory into this skill.
- **Never assume an API key is read-only.** UniFi keys authenticate against write paths by default.
  If a document claims a key is read-only, verify it rather than trusting it.
- **Legacy `rest/*` PUT replaces the whole object.** Read, modify, send back whole. A partial PUT
  blanks the fields you omitted.
- Read pre-state, make one change, read post-state. Never chain mutations behind one unverified read.
- Prefer the surface that owns the fact over the surface that is convenient.
- Keep TLS verification on. A console serving an internally-issued certificate validates normally on
  a host that trusts the issuing CA; reach for `-k` only to prove a diagnosis, never in stored
  procedure.
- Report which surface performed the operation, and why, when it was not the obvious one.

## Start here — resolve the site

Every path below needs a site identifier, and **the two HTTP families use different ones**. Getting
this wrong is the most common cause of a spurious 404.

```bash
# Integration v1 wants the UUID from `id`:
curl -s -H "X-API-KEY: $KEY" "https://<console>/proxy/network/integration/v1/sites"
# -> {"data":[{"id":"<uuid>","internalReference":"default","name":"Default"}]}

# Legacy and v2 want the internalReference (usually, but not always, "default"):
curl -s -H "X-API-KEY: $KEY" "https://<console>/proxy/network/api/s/<internalReference>/stat/sysinfo"
```

Do not hardcode `default`. Read it once per console and carry it.

## Access-Surface Routing

| You need | Surface | Path |
|---|---|---|
| Sites, devices, clients, networks, vouchers | Integration v1 | `/proxy/network/integration/v1/sites/<uuid>/…` |
| SSIDs, networks/VLANs, firewall rules and groups, port forwards, routes, port profiles, users, RADIUS | Legacy | `/proxy/network/api/s/<site>/rest/<object>` |
| Console settings — IPS and signature suppressions, netflow, remote syslog, DPI, mDNS, NTP, SNMP | Legacy | `/proxy/network/api/s/<site>/rest/setting[/<key>]` |
| Device/client statistics, site health, sysinfo | Legacy | `/proxy/network/api/s/<site>/stat/<name>` |
| Device actions — restart, LED locate, PoE cycle, client block/kick | Legacy | `/proxy/network/api/s/<site>/cmd/<name>` |
| **Local DNS records** | **v2 only** | `/proxy/network/v2/api/site/<site>/static-dns` |
| Zone-based firewall policies, enriched LAN/WLAN config, active clients, speedtest | v2 | `/proxy/network/v2/api/site/<site>/…` |
| Console identity, model, firmware | UniFi OS | `/api/system` |
| Certificate files, config database, packet capture, IPS internals, vendor tooling | **Root SSH only** | see `references/ssh.md` |
| **Events, alarms, security log** | **No API exists** | see below |

## Reading the response

Status codes carry specific meaning here, and two of them are routinely misread:

| Code | Means | Do |
|---|---|---|
| `400` | **Authenticated.** The body was rejected | Your key works. Fix the payload — usually a missing required field from the original object |
| `401` / `403` | Authentication or scope failure | Now it is the key |
| `404` | This *surface* lacks this path | Check the other three before concluding the feature is absent |
| `200` with `[]` | Path exists, genuinely empty | Real answer — e.g. `firewall-policies` is empty on a console still using legacy `firewallrule` |

**A `400` from a write endpoint is not a permission error.** It is proof the key authenticated. This
is the single most useful signal for determining what a key can actually do.

Response envelopes differ per surface, so a client written against one mis-parses another:

```
Integration v1  {"offset":0,"limit":25,"count":7,"totalCount":7,"data":[…]}   paginated
Legacy          {"meta":{"rc":"ok"},"data":[…]}
v2              […]                                                          bare, no envelope
```

Integration v1 paginates — check `totalCount` against `count` before treating a page as the set.

## Changing configuration safely

Legacy `rest/*` is a **replace**, not a merge. Send a partial object and every omitted field is
cleared. Always round-trip:

```bash
BASE="https://<console>/proxy/network/api/s/<site>"

# 1. Read the whole object and keep it — this is also your rollback copy.
curl -s -H "X-API-KEY: $KEY" "$BASE/rest/wlanconf" | jq '.data[] | select(.name=="<ssid>")' > before.json

# 2. Modify only the intended field, preserving everything else.
jq '.<field> = <value>' before.json > after.json

# 3. PUT the complete object back to its own _id.
ID=$(jq -r '._id' after.json)
curl -s -X PUT -H "X-API-KEY: $KEY" -H 'Content-Type: application/json' \
     --data @after.json "$BASE/rest/wlanconf/$ID"

# 4. Verify only the intended field changed.
curl -s -H "X-API-KEY: $KEY" "$BASE/rest/wlanconf" \
  | jq '.data[] | select(._id=="'"$ID"'")' > check.json
diff <(jq -S . before.json) <(jq -S . check.json)
```

Step 4 is the point of the recipe. A diff showing one changed line is proof; a successful `200` is
not. Keep `before.json` until verified — it is the rollback payload.

## Common mistakes

| Mistake | Symptom | Correction |
|---|---|---|
| Probing one surface, concluding the feature is missing | "UniFi has no DNS API" | Local DNS is v2-only; check all four |
| Using the Integration UUID on Legacy, or vice versa | 404 on a path that exists | Two identifier forms — see *Start here* |
| Reading `400` as "the key is read-only" | Believing a key is scoped when it is not | `400` = authenticated, body rejected |
| Partial PUT to `rest/*` | Unrelated settings silently blank | Read-modify-write the whole object |
| Trusting a settings document's `enabled` flag | Export "enabled" but nothing arrives | A settings object can read `enabled: true` while carrying **no destination fields**. Diff it field-by-field against a working one |
| Parsing v2 with a Legacy client | Empty results, no error | v2 returns bare JSON, no `meta`/`data` |
| Swapping the console certificate | A metrics collector silently stops | Consumers that pin the leaf digest break on every re-upload, and CA trust does not fix them. See `references/ssh.md` |
| Assuming `default` is the site | 404 everywhere on a multi-site console | Read `internalReference` |

### There is no event or alarm API

UniFi Network 9 removed the REST event log. `stat/event`, `stat/alarm`, `rest/event` and the v2
equivalents all return 404, by GET and POST alike. Controller event history exists **only** in the
web UI and in whatever remote syslog export the console sends.

If an environment claims to collect UniFi events, verify the export has a destination before
believing it. A remote-syslog setting reading `enabled: true` with no `server` field exports nothing
and looks healthy — compare it against the netflow setting, which does carry `server` and `port`.

## Intent → Action

| User wants to… | Do |
|---|---|
| List devices or clients | Integration v1 `sites/<uuid>/devices` or `/clients`; mind pagination |
| Change an SSID | Legacy `rest/wlanconf` — round-trip recipe above |
| Change a VLAN or network | Legacy `rest/networkconf` — same recipe |
| Add a local DNS record | v2 `static-dns` — POST the record; nothing else exposes these |
| Suppress an IPS signature | Legacy `rest/setting/ips_suppression` — read whole, append, PUT whole |
| Check whether an export actually exports | Legacy `rest/setting/<key>`; look for destination fields, not `enabled` |
| Restart a device or cycle PoE | Legacy `cmd/devmgr` |
| Find out what happened last night | UI or exported syslog — there is no event API |
| Replace the console certificate | Root SSH, then re-point every pinning consumer |
| Determine what a key can actually do | Send a deliberately malformed write; `400` means authenticated |
| Reach something no API exposes | Root SSH — the config database holds what the APIs omit |

## References

Load only what the task needs:

- [references/surfaces.md](references/surfaces.md): per-surface base paths, auth header, verified
  endpoint inventory, and settings-document keys.
- [references/ssh.md](references/ssh.md): what only root SSH reaches, on-box tooling, certificate
  replacement, and `scripts/udmssh.py`.

Verify endpoints against the console in front of you before trusting a remembered path. The Legacy
API carries no version contract and UniFi moves capabilities between surfaces across releases.
