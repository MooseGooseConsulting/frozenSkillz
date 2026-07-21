#!/usr/bin/env python3
"""PreToolUse guard: refuse Unity MCP mutations while another agent holds the Editor lock.

Enforces a single-mutating-owner convention MECHANICALLY instead of by agent etiquette.
Read-only Unity tools pass through; mutations are blocked (exit 2) while a live, unexpired
lock is held by a foreign owner. Stale (expired) locks do not block.

Provenance: distilled verbatim from ProjectBroadside's `.claude/hooks/unity_lock_guard.py`.
The only generalization from the source is that the lock path and the "self" owner-prefix are
overridable via environment variables; the DEFAULTS reproduce the source's exact behavior
(lock at `.codex/editor.lock`, self-owner prefix `claude`). See the lessons doc, Lesson 1 and
"Lesson 7 (self-correction)", for why this hook exists and how it was tested against four cases
(foreign-live / stale / read-only / absent).

Config (optional):
  UNITY_LOCK_PATH         relative path to the lock file (default: .codex/editor.lock)
  UNITY_LOCK_SELF_PREFIX  owner prefix that counts as "you" and never blocks (default: claude)
"""
import json
import os
import sys
from datetime import datetime, timezone

READONLY_PREFIXES = (
    "mcp__unityMCP__read_console",
    "mcp__unityMCP__find_gameobjects",
    "mcp__unityMCP__find_in_file",
    "mcp__unityMCP__get_",
    "mcp__unityMCP__unity_docs",
    "mcp__unityMCP__unity_reflect",
    "mcp__unityMCP__validate_script",
    "mcp__unityMCP__debug_request_context",
    "mcp__aura-unity__get_",
    "mcp__aura-unity__list_",
    "mcp__aura-unity__search_",
    "mcp__aura-unity__query_",
    "mcp__aura-unity__check_",
    "mcp__aura-unity__capture_",
    "mcp__aura-unity__grep",
    "mcp__aura-unity__read_file",
)

LOCK_PATH = os.environ.get("UNITY_LOCK_PATH", os.path.join(".codex", "editor.lock"))
SELF_PREFIX = os.environ.get("UNITY_LOCK_SELF_PREFIX", "claude")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool = payload.get("tool_name", "")
    if not (tool.startswith("mcp__unityMCP__") or tool.startswith("mcp__aura-unity__")):
        sys.exit(0)
    if any(tool.startswith(p) for p in READONLY_PREFIXES):
        sys.exit(0)
    if not os.path.exists(LOCK_PATH):
        sys.exit(0)

    try:
        with open(LOCK_PATH, "r", encoding="utf-8") as fh:
            lock = json.load(fh)
    except Exception:
        print(
            "BLOCKED: %s exists but is unreadable; treating it as held. "
            "Inspect the file before mutating Unity." % LOCK_PATH,
            file=sys.stderr,
        )
        sys.exit(2)

    owner = str(lock.get("owner", "unknown"))
    if owner.startswith(SELF_PREFIX):
        sys.exit(0)

    expires = lock.get("expiresAtUtc")
    if expires:
        try:
            exp_dt = datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
            if exp_dt < datetime.now(timezone.utc):
                sys.exit(0)  # stale lock does not block; convention says stale = deletable
        except Exception:
            pass  # unparseable expiry: fall through to block conservatively

    print(
        "BLOCKED by %s: held by '%s' (operation: %s, expires %s). "
        "Unity mutations are serialized to one owner - wait for release, coordinate, "
        "or verify the lock is stale before proceeding. Read-only Unity tools remain available."
        % (LOCK_PATH, owner, lock.get("operation"), expires),
        file=sys.stderr,
    )
    sys.exit(2)


main()
