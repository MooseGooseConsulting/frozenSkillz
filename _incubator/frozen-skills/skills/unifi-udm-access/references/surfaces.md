# UniFi console surfaces

Base paths below are relative to the console root. `<site>` differs by surface: the Integration API
uses a UUID from its own `sites` endpoint; the Legacy and v2 APIs use the site's internal reference
name (commonly `default`). They are not interchangeable.

Authentication for all three HTTP surfaces is the same header:

```
X-API-KEY: <key>
```

Keys are generated in the console UI under Control Plane → Integrations. **A key authenticates
against write paths unless the console scopes it otherwise** — a `400` from a write endpoint means
the request body was rejected after successful authentication, not that the key is read-only.
Distinguish `400` (auth passed, body wrong) from `401`/`403` (auth failed) before concluding
anything about permissions.

The console may serve an internally-issued certificate. Prefer trusting the issuing CA on the client
host over disabling verification. Note that some clients pin the leaf digest instead of chaining to
a CA — for those, CA trust does not work and the leaf itself must be re-pinned after every swap.

## Integration API v1

```
/proxy/network/integration/v1/
```

Official and versioned. Deliberately narrow — verified to expose only:

| Path | Returns |
|---|---|
| `info` | Application version |
| `sites` | Site list with UUID and internal reference |
| `sites/<site>/devices` | Adopted devices: name, model, MAC, IP, state, firmware |
| `sites/<site>/clients` | Connected clients, paginated |
| `sites/<site>/networks` | Configured networks |
| `sites/<site>/hotspot/vouchers` | Guest vouchers |

Responses are envelope-shaped: `{offset, limit, count, totalCount, data:[...]}`. No OpenAPI document
is served locally.

Everything else 404s here — WLANs, firewall rules, port forwards, traffic rules, DNS records, device
statistics, events, alarms. Their absence on this surface says nothing about the others.

## Legacy API

```
/proxy/network/api/s/<site>/
```

Undocumented, unversioned, and the broadest configuration surface. Responses are
`{meta:{rc:"ok"}, data:[...]}`.

**Configuration (`rest/*`)** — read with GET, change with PUT of the *complete* object:

`wlanconf` · `networkconf` · `firewallrule` · `firewallgroup` · `portforward` · `routing` ·
`portconf` · `user` · `usergroup` · `account` · `radiusprofile` · `dynamicdns` · `setting`

`rest/setting` returns every settings document at once; `rest/setting/<key>` addresses one. Keys
observed on a current console include `ips` and `ips_suppression`, `netflow`, `rsyslogd`, `dpi`,
`doh`, `mdns`, `ntp`, `snmp`, `guest_access`, `mgmt`, `global_switch`, `global_nat`,
`network_optimization`, `connectivity`, `country`, `locale`, `auto_speedtest`, `usg`, `ugw`.

A settings document can read `enabled: true` while lacking the destination fields that make it do
anything — compare a working exporter's document against a suspect one field by field rather than
trusting the enabled flag.

**Reads (`stat/*`)**: `device` · `sta` · `health` · `sysinfo` · `ccode` · `rogueap` · `sdn` ·
`current-channel`

**Actions (`cmd/*`)**: device restart, LED locate, PoE cycle, client block/unblock/kick.

**Absent**: `stat/event` and `stat/alarm` return 404 on current versions.

## v2 API

```
/proxy/network/v2/api/site/<site>/
```

Where newer features landed. Responses are bare JSON arrays or objects — no `meta`/`data` envelope,
so a client written against the Legacy shape will mis-parse them.

| Path | Owns |
|---|---|
| `static-dns` | **Local DNS records — no other surface exposes these** |
| `firewall-policies` | Zone-based firewall model (empty when still on legacy `firewallrule`) |
| `clients/active`, `clients/history` | Client state |
| `lan/enriched-configuration`, `wlan/enriched-configuration` | Combined configuration views |
| `aggregated-dashboard` | Dashboard rollups |
| `speedtest` | Speedtest results |
| `device` | Device list |

## UniFi OS

```
/api/system
```

Console-level identity: hardware model, name, MAC, firmware. Separate from the Network application.
A Network API key does **not** authorize other UniFi OS paths — console user and firmware endpoints
return `401` with it.

## Optional read helper

`uvx unifi-cli` provides read commands and a JSON schema dump for agent introspection without
installing anything. Two caveats before relying on it: it ships its own certificate root store, so
it cannot validate an internally-issued console certificate and must be run with verification
disabled; and it echoes credentials passed by environment variable into its `--help` output. It
covers device, client, network, port, and system reads — not the configuration surfaces above.
