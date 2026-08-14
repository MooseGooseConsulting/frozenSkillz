---
name: unifi-udm-access
description: >-
  Use when reading or changing configuration on a self-hosted UniFi console
  (UDM, Dream Machine, Cloud Key) — SSIDs, VLANs, firewall rules, local DNS, IPS
  settings, device and client state — or when a UniFi API call 404s and the right
  surface is unclear. Not for UniFi Protect, Access, or cloud controllers.
---

# UniFi Console Access Routing

A UniFi console exposes four access surfaces, and they are not tiers of the same API — they are
disjoint. Each is authoritative for things the others cannot reach at all. Choosing wrong produces a
404 that looks like a missing feature rather than a wrong address.

The routing question is never "which API is newest." It is "which surface owns this fact."

1. **Integration API v1** — official, versioned, stable. Narrow.
2. **Legacy API** — the configuration surface. Undocumented and unversioned.
3. **v2 API** — newer features the other two never grew.
4. **Root SSH** — the console's own filesystem, database, and network tooling.

## Operating Contract

- Load the applicable secrets-management skill before handling authentication. API key and console
  SSH credentials are separate secrets with different blast radius.
- Resolve the console address, site identifier, device inventory, and credential names from the
  owning environment. Do not copy environment inventory into this skill.
- **Do not assume an API key is read-only.** UniFi keys authenticate against write paths by default.
  A `400` from a write endpoint means the body was rejected, not that the key lacks permission —
  auth already succeeded. Verify the scope you actually have before trusting a document that calls
  a key read-only.
- **Legacy `rest/*` PUT replaces the object.** Read the current object, modify the fields you intend,
  and send it back whole. A partial PUT silently blanks the fields you omitted.
- Read pre-state, perform one change, read post-state. Never chain mutations behind a single
  unverified read.
- Keep site identity explicit. The site path segment is a per-console identifier, not a global
  constant, and the Integration and Legacy APIs use different forms of it.
- Prefer the surface that owns the fact over the surface that is convenient. If only one surface
  exposes something, that is not a workaround.
- Never put credentials in argv, prompts, committed files, or durable output. Keep TLS verification
  enabled; the console can serve an internally-issued certificate that a trusting host validates
  normally.
- Report which surface performed the operation, and why, when it was not the obvious one.

## Access-Surface Routing

| Situation | Surface |
|---|---|
| Site list, device inventory, client list, network list, hotspot vouchers | **Integration v1** |
| SSIDs (`rest/wlanconf`), networks and VLANs (`rest/networkconf`), firewall rules and groups, port forwards, static routes, port profiles, users, RADIUS | **Legacy** |
| Console settings — IPS and its signature suppressions, netflow export, remote syslog, DPI, mDNS, NTP, SNMP (`rest/setting`, `rest/setting/<key>`) | **Legacy** |
| Device and client statistics, site health, controller sysinfo | **Legacy** (`stat/*`) or Integration v1 |
| **Local DNS records** | **v2 only** (`static-dns`) — no other surface exposes them |
| Zone-based firewall policies, enriched LAN/WLAN configuration, active/historical clients, speedtest | **v2** |
| Console TLS certificate files, configuration database, packet capture, conntrack, IPS internals, vendor `ubnt-*` tooling | **Root SSH only** |
| Console-level identity, firmware, hardware model | UniFi OS `/api/system` |
| **Controller events, alarms, or security log** | **No API.** See below |

### Two constraints worth knowing before you search

**There is no event or alarm API.** UniFi Network 9 removed the REST event log. Every path — legacy
`stat/event`, `stat/alarm`, `rest/event`, and the v2 equivalents — returns 404 on current versions,
by GET and POST alike. Controller event history exists only in the web UI and in whatever remote
syslog export the console is configured to send. If an environment claims to collect UniFi events,
verify the export actually has a remote target; a syslog setting can read "enabled" while carrying
no destination at all, which exports nothing and looks healthy.

**A consumer that pins the console certificate breaks on every re-upload.** Some clients — notably
metrics pollers — pin the certificate's digest rather than building a chain to a CA. For those,
re-uploading the console certificate is a breaking change, and trusting the issuing CA instead does
not work. Treat a console certificate swap as incomplete until every pinning consumer is re-pointed.

## Workflow

1. Identify which surface owns the fact, from the routing table above.
2. Resolve the console address, site identifier, and credential from the owning environment.
3. Prove authentication with a small read on that surface before attempting anything else.
4. For a read: fetch, and report the surface used.
5. For a write: read the current object whole → modify only the intended fields → send it back
   whole → read post-state and confirm the change and only that change.
6. If a call 404s, re-check the surface before concluding the feature is missing. A 404 on one
   surface says nothing about the others.

## Intent → Action

| User wants to… | Do |
|---|---|
| List devices or clients | Integration v1 `sites/<site>/devices` or `/clients` |
| Read or change an SSID | Legacy `rest/wlanconf` — read whole, modify, PUT whole |
| Read or change VLANs/networks | Legacy `rest/networkconf` — same read-modify-write |
| Add or change a local DNS record | v2 `static-dns` — the only surface that has them |
| Suppress an IPS signature, or change syslog/netflow export | Legacy `rest/setting/<key>` |
| Restart a device, block a client, cycle PoE | Legacy `cmd/*` endpoints |
| Find out what happened last night | UI or exported syslog — there is no event API |
| Replace the console certificate | Root SSH, then re-point every pinning consumer |
| Inspect something no API exposes | Root SSH — the configuration database holds what the APIs omit |
| Diagnose "the API doesn't have this" | Check all four surfaces before believing it |

## References

Load only what the task needs:

- [references/surfaces.md](references/surfaces.md): base paths, authentication headers, verified
  endpoint inventory per surface, and the response-shape differences between them.
- [references/ssh.md](references/ssh.md): what only root SSH reaches, the on-box tooling inventory,
  and `scripts/udmssh.py` usage.

Verify endpoint availability against the console in front of you before trusting any remembered
path. UniFi moves endpoints between surfaces across releases, and the Legacy API carries no version
contract at all.
