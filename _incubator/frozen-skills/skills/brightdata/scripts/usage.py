#!/usr/bin/env python3
"""Read Bright Data account balance, active zones, and usage/cost data.

Run after a paid Bright Data task so the agent reports current account spend
rather than silently consuming credits. This is observation only.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import print_json, request


def month_range() -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(year=start.year + 1, month=1) if start.month == 12 else start.replace(month=start.month + 1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def main() -> int:
    start, end = month_range()
    balance_status, _, balance = request("GET", "/customer/balance", timeout=60)
    zones_status, _, zones = request("GET", "/zone/get_active_zones", timeout=60)
    bw_status, _, bandwidth = request("GET", "/customer/bw", params={"from": start, "to": end}, timeout=60)
    costs = {}
    if isinstance(zones, list):
        for zone in zones:
            name = zone.get("name") if isinstance(zone, dict) else None
            if name:
                status, _, cost = request("GET", "/zone/cost", params={"zone": name, "from": start, "to": end}, timeout=60)
                costs[name] = {"status": status, "data": cost}
    print_json({"window": {"from": start, "to_exclusive": end}, "balance": {"status": balance_status, "data": balance}, "zones": {"status": zones_status, "data": zones}, "bandwidth": {"status": bw_status, "data": bandwidth}, "zone_costs": costs})
    required_ok = balance_status == 200 and zones_status == 200 and bw_status == 200
    zone_costs_ok = all(row.get("status") == 200 for row in costs.values())
    return 0 if required_ok and zone_costs_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
