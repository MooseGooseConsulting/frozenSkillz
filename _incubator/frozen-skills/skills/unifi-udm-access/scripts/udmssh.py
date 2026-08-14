#!/usr/bin/env python3
"""Run commands on a UniFi console over root SSH.

Usage:
    export UDMPW="$(<secret-store fetch command>)"
    uv run --with paramiko python scripts/udmssh.py <host> "<command>" ["<command>" ...]

The password is read from the UDMPW environment variable so it never appears in
argv, process listings, or shell history. Commands themselves ARE echoed to
stdout so multi-command output can be correlated, so do not embed secrets in a
command.

This helper deliberately provides no channel for passing a secret to the remote
side: stdin is closed before the command runs, and an `env VAR=...` prefix would
only move the secret into the console's own process listing. A command that
needs a credential on the console must read it there -- from the device's
existing configuration or credential store -- not receive it through this
script. If that is not possible, the operation does not belong in this helper.

Host keys are verified against the user's known_hosts. To onboard a console for
the first time, record its key deliberately:

    ssh-keyscan -H <host> >> ~/.ssh/known_hosts

Set UDMSSH_TRUST_NEW=1 to accept and store an unknown key instead. That opt-in
exists for onboarding only; leaving it on defeats host verification and exposes
a full-root password to anything that can intercept the connection.

Runs every command even if one fails, then exits with the first non-zero status
(the most diagnostic one); a timed-out command reports 124. Set UDMUSER to
override the default 'root' login. UDMSSH_TIMEOUT sets the per-command idle
timeout in seconds (default 60, 0 disables) -- raise it for long silent
operations such as a support bundle.
"""

import os
import socket
import sys
from concurrent.futures import ThreadPoolExecutor

import paramiko


def _connect(host: str, user: str, password: str) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.load_system_host_keys()

    known_hosts = os.path.expanduser("~/.ssh/known_hosts")
    trust_new = os.environ.get("UDMSSH_TRUST_NEW") == "1"

    if trust_new:
        # AutoAddPolicy writes the accepted key back, and paramiko re-reads the
        # file to do it -- so it has to exist before we connect.
        os.makedirs(os.path.dirname(known_hosts), exist_ok=True)
        if not os.path.exists(known_hosts):
            open(known_hosts, "a").close()

    if os.path.exists(known_hosts):
        client.load_host_keys(known_hosts)

    if trust_new:
        print("UDMSSH_TRUST_NEW=1: accepting unknown host key", file=sys.stderr)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    else:
        client.set_missing_host_key_policy(paramiko.RejectPolicy())

    client.connect(
        host,
        username=user,
        password=password,
        timeout=15,
        look_for_keys=False,
        allow_agent=False,
    )
    return client


def _run(client: paramiko.SSHClient, command: str, timeout: float | None) -> tuple[str, str, int]:
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    channel = stdout.channel
    # Close stdin so a command that reads it sees EOF instead of blocking.
    stdin.close()
    channel.shutdown_write()

    # Drain both streams concurrently. Reading one to completion first can
    # deadlock when the other fills its channel window.
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            out_future = pool.submit(stdout.read)
            err_future = pool.submit(stderr.read)
            out = out_future.result().decode(errors="replace").strip()
            err = err_future.result().decode(errors="replace").strip()
    except (socket.timeout, TimeoutError):
        # Abandoning a timed-out channel leaves the remote command running and
        # leaks the channel for the rest of the session. Close it so the remote
        # side sees EOF and the next command in the batch starts clean.
        channel.close()
        raise

    return out, err, channel.recv_exit_status()


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2

    password = os.environ.get("UDMPW")
    if not password:
        print("UDMPW is not set; refusing to prompt or read from argv", file=sys.stderr)
        return 2

    host, commands = sys.argv[1], sys.argv[2:]
    user = os.environ.get("UDMUSER", "root")

    # exec_command's timeout is an idle timeout on the channel, not a wall clock
    # for the command. A long, silent operation (a support bundle, a large
    # capture) trips it and aborts the batch, so allow it to be raised or
    # disabled entirely with UDMSSH_TIMEOUT=0.
    raw_timeout = os.environ.get("UDMSSH_TIMEOUT", "60")
    try:
        timeout: float | None = float(raw_timeout) or None
    except ValueError:
        print(f"UDMSSH_TIMEOUT is not a number: {raw_timeout!r}", file=sys.stderr)
        return 2

    try:
        client = _connect(host, user, password)
    except paramiko.SSHException as exc:
        print(f"connection failed: {exc}", file=sys.stderr)
        if "not found in known_hosts" in str(exc):
            print(
                f"record the key first: ssh-keyscan -H {host} >> ~/.ssh/known_hosts",
                file=sys.stderr,
            )
        return 2
    except (OSError, socket.error) as exc:
        # gaierror / timeout / refused all land here; paramiko does not wrap them.
        print(f"cannot reach {host}: {exc}", file=sys.stderr)
        return 2

    first_failure = 0
    try:
        for command in commands:
            try:
                out, err, status = _run(client, command, timeout)
            except (socket.timeout, TimeoutError) as exc:
                print(f"$ {command}")
                print(
                    f"[timeout] no output for {timeout}s: {exc}; "
                    "raise or disable with UDMSSH_TIMEOUT",
                    file=sys.stderr,
                )
                print("-" * 50)
                first_failure = first_failure or 124
                continue

            print(f"$ {command}")
            if out:
                print(out)
            if err:
                print(f"[stderr] {err}", file=sys.stderr)
            if status:
                print(f"[exit {status}]", file=sys.stderr)
                first_failure = first_failure or status
            print("-" * 50)
    finally:
        client.close()

    return first_failure


if __name__ == "__main__":
    sys.exit(main())
