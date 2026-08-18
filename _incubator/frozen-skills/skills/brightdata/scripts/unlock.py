#!/usr/bin/env python3
"""Direct Web Unlocker and SERP API access.

Use direct REST only when a known active zone supports it. Discover zones with
`catalog.py zones`; pass the intended product zone explicitly or set the
product-specific environment default.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import print_json, request


def zone_for(mode: str, explicit: str | None) -> str | None:
    if explicit:
        return explicit
    env_name = "BRIGHTDATA_UNLOCKER_ZONE" if mode == "unlock" else "BRIGHTDATA_SERP_ZONE"
    return os.environ.get(env_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["unlock", "serp"])
    parser.add_argument("url")
    parser.add_argument("--zone", help="Active product zone; otherwise use BRIGHTDATA_UNLOCKER_ZONE or BRIGHTDATA_SERP_ZONE")
    parser.add_argument("--format", choices=["raw", "json"], default="raw")
    parser.add_argument("--data-format", choices=["markdown", "screenshot", "parsed_light"])
    parser.add_argument("--country")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--output", help="Required for screenshot output; writes the PNG bytes here")
    args = parser.parse_args()

    zone = zone_for(args.mode, args.zone)
    if not zone:
        env_name = "BRIGHTDATA_UNLOCKER_ZONE" if args.mode == "unlock" else "BRIGHTDATA_SERP_ZONE"
        parser.error(f"--zone or {env_name} is required")
    if args.mode == "unlock" and args.data_format == "parsed_light":
        parser.error("parsed_light is a SERP data format, not a Web Unlocker data format")
    if args.data_format == "screenshot" and not args.output:
        parser.error("--output is required with --data-format screenshot")

    body = {"zone": zone, "url": args.url, "format": args.format, "method": "GET", "debug": args.debug}
    if args.data_format:
        body["data_format"] = args.data_format
    if args.country:
        body["country"] = args.country
    if args.render:
        body["render"] = "true"

    screenshot = args.data_format == "screenshot"
    status, headers, data = request("POST", "/request", body=body, timeout=180, raw=screenshot)
    brd_headers = {k: v for k, v in headers.items() if k.lower().startswith("x-brd")}
    if screenshot and status == 200:
        assert isinstance(data, (bytes, bytearray))
        Path(args.output).write_bytes(bytes(data))
        print_json({"status": status, "zone": zone, "headers": brd_headers, "output": args.output})
    else:
        print_json({"status": status, "zone": zone, "headers": brd_headers, "data": data})
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
