from __future__ import annotations

import argparse
import os
from pathlib import Path

from .core import EndpointClient, HistorySyncError, default_storage_root, export_snapshot, import_snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed ChatGPT history export/import for conversation organization")
    parser.add_argument("command", choices=("export", "import", "sync"))
    parser.add_argument("--storage-root", type=Path, default=default_storage_root())
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--base-url", default="https://chatgpt.com")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    try:
        if args.command == "import":
            if not args.snapshot:
                raise HistorySyncError("--snapshot is required for import")
            print(import_snapshot(args.storage_root, args.snapshot))
            return 0
        client = EndpointClient(args.base_url, os.environ.get("CHATGPT_HISTORY_SESSION_COOKIE", ""), args.timeout)
        snapshot = export_snapshot(args.storage_root, client)
        print(snapshot)
        if args.command == "sync":
            print(import_snapshot(args.storage_root, snapshot))
        return 0
    except HistorySyncError as exc:
        print(f"chatgpt-history-sync: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
