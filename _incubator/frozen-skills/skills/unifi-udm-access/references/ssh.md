# Root SSH to a UniFi console

Root SSH is enabled in the console UI and uses a password set there, held in the environment's
secret store. It is a different credential from the Network API key, with a much larger blast
radius: it is full root on the gateway that carries all household traffic.

## What only SSH reaches

| Target | Why the APIs cannot |
|---|---|
| Console TLS files under `/data/unifi-core/config/` | Certificate replacement is a file operation plus a service restart |
| The configuration database (`mongo --port 27117`) | Holds objects no REST surface projects |
| `tcpdump`, `conntrack`, routing and firewall state | No packet or flow inspection exists in any API |
| IPS/IDS internals, geo-IP data, vendor diagnostics | Vendor `ubnt-*` tooling only |
| Support bundle generation | `ubnt-make-support-file` |

Consoles run a BusyBox-style aarch64 Linux with systemd. Expect `mongo`, `jq`, `curl`, `tcpdump`,
`iperf3`, `conntrack`, `iptables`, and roughly three dozen `ubnt-*` utilities — among them
`ubnt-device-info`, `ubnt-make-support-file`, `ubnt-config-restore`, `ubnt-syslog-agent`, and
`ubnt-idsips-daemon`.

## Certificate replacement

Replacing the console certificate is a file swap plus a service restart, and the UI accepts
**RSA keys only** on many versions — an ECDSA leaf is rejected. Back up the existing pair before
overwriting.

The step operators forget: **any consumer pinning the old certificate breaks at the moment of the
swap.** Metrics pollers commonly pin the leaf digest rather than chaining to a CA, so pointing them
at the issuing CA does not fix them — each must receive the new leaf and re-pin. A console OS
upgrade can also revert the certificate to self-signed, which breaks the same consumers again.
Treat the swap as incomplete until every pinning consumer is re-pointed and verified.

## scripts/udmssh.py

Runs one or more commands over SSH and prints stdout, stderr, and a separator per command. Reads the
password from the `UDMPW` environment variable — never from argv, where it would land in process
listings and shell history.

```bash
export UDMPW="$(<secret-store fetch command>)"
uv run --with paramiko python scripts/udmssh.py \
  "<host>" "ubnt-device-info summary" "uptime"
```

Host is the first argument; every argument after it is a command. `uv run --with paramiko` avoids
installing anything permanently. On Windows there is generally no `sshpass`, which is why this
exists rather than a shell one-liner.

**Host keys are verified.** The console's key must already be in `known_hosts`, because this session
sends a full-root password — a console that is not who it claims to be gets that password. Onboard a
new console deliberately:

```bash
ssh-keyscan -H <host> >> ~/.ssh/known_hosts
```

`UDMSSH_TRUST_NEW=1` accepts and stores an unknown key instead, for onboarding when `ssh-keyscan` is
inconvenient. It prints a warning, and leaving it set defeats the verification entirely. An
unrecognised host fails with exit 2 and the `ssh-keyscan` line to run.

Other behaviour worth knowing:

- Commands are echoed to stdout so multi-command output can be correlated. Do not embed secrets in a
  command — pass them through the remote environment.
- stdin is closed per command, so a command that reads stdin sees EOF rather than hanging.
- stdout and stderr are drained concurrently; reading one to completion first can deadlock when the
  other fills its channel window.
- Every command runs even if an earlier one fails. The exit status is the **first** non-zero one.
- `UDMUSER` overrides the default `root` login.

Use it for reads and deliberate single changes. It is not a configuration management tool — no
idempotence, no dry run, no rollback.
