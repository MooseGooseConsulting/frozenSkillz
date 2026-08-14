#!/usr/bin/env python3
"""Run commands on a UniFi console over root SSH.

Usage:
    export UDMPW="$(<secret-store fetch command>)"
    uv run --with paramiko python udmssh.py <host> "<command>" ["<command>" ...]

The password is read from the UDMPW environment variable so it never appears in
argv, process listings, or shell history. Exits non-zero if any command does.
"""

import os
import sys

import paramiko


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

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        host,
        username=user,
        password=password,
        timeout=15,
        look_for_keys=False,
        allow_agent=False,
    )

    worst = 0
    try:
        for command in commands:
            _, stdout, stderr = client.exec_command(command, timeout=60)
            out = stdout.read().decode(errors="replace").strip()
            err = stderr.read().decode(errors="replace").strip()
            status = stdout.channel.recv_exit_status()

            print(f"$ {command}")
            if out:
                print(out)
            if err:
                print(f"[stderr] {err}", file=sys.stderr)
            if status:
                print(f"[exit {status}]", file=sys.stderr)
                worst = worst or status
            print("-" * 50)
    finally:
        client.close()

    return worst


if __name__ == "__main__":
    sys.exit(main())
