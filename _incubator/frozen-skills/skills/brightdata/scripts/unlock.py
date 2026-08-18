#!/usr/bin/env python3
"""Direct Web Unlocker and SERP API access.

Use direct REST only when a known active zone supports it. Discover zones with
brightdata_catalog.py zones. mcp_unlocker is an active Web Unlocker zone in the
current account. No active dedicated SERP zone has been verified.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import print_json, request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["unlock", "serp"])
    parser.add_argument("url")
    parser.add_argument("--zone", help="Active Bright Data zone; default mcp_unlocker for unlock")
    parser.add_argument("--format", choices=["raw", "json"], default="raw")
    parser.add_argument("--data-format", choices=["markdown", "screenshot", "parsed_light"])
    parser.add_argument("--country")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    zone = args.zone
    body = {"zone": zone, "url": args.url, "format": args.format, "method": "GET", "debug": args.debug}
    if args.data_format:
        body["data_format"] = args.data_format
    if args.country:
        body["country"] = args.country
    if args.render:
        body["render"] = "true"
    status, headers, data = request("POST", "/request", body=body, timeout=180)
    print_json({"status": status, "zone": zone, "headers": {k: v for k, v in headers.items() if k.lower().startswith("x-brd")}, "data": data})
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
