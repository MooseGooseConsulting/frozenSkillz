#!/usr/bin/env python3
"""Use account-owned Bright Data Scraper Studio collectors through DCA APIs.

Only runs existing collectors by default. Creating a collector and AI healing are
mutating operations; invoke them only when the user explicitly requests it.

Examples:
  python3 scraper_studio.py list
  python3 scraper_studio.py run c_example --input '[{"url":"https://target.example"}]'
  python3 scraper_studio.py realtime c_example --input '{"url":"https://target.example"}'
  python3 scraper_studio.py job j_example
  python3 scraper_studio.py jobs c_example
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import poll, print_json, request


def parse_rows(raw: str, realtime: bool = False):
    value = json.loads(raw)
    if realtime:
        if not isinstance(value, dict):
            raise SystemExit("realtime input must be one JSON object")
        return value
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list) and all(isinstance(row, dict) for row in value):
        return value
    raise SystemExit("batch input must be a JSON object or array of objects")


def ready(status: int, body: object) -> bool:
    return status == 200 and isinstance(body, list)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    run = sub.add_parser("run")
    run.add_argument("collector_id")
    run.add_argument("--input", required=True)
    run.add_argument("--timeout", type=int, default=600)
    run.add_argument("--poll", type=int, default=5)
    run.add_argument("--queue", default="1")
    rt = sub.add_parser("realtime")
    rt.add_argument("collector_id")
    rt.add_argument("--input", required=True)
    job = sub.add_parser("job")
    job.add_argument("job_id")
    jobs = sub.add_parser("jobs")
    jobs.add_argument("collector_id")
    jobs.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    if args.command == "list":
        status, _, data = request("GET", "/dca/collectors_list", timeout=60)
        print_json({"status": status, "data": data})
        return 0 if status == 200 else 1
    if args.command == "job":
        status, _, data = request("GET", f"/dca/log/{args.job_id}", timeout=60)
        print_json({"status": status, "data": data})
        return 0 if status == 200 else 1
    if args.command == "jobs":
        status, _, data = request("GET", "/dca/collector/jobs", params={"collector": args.collector_id, "limit": args.limit}, timeout=60)
        print_json({"status": status, "data": data})
        return 0 if status == 200 else 1
    if args.command == "realtime":
        status, _, data = request("POST", "/dca/trigger_immediate", params={"collector": args.collector_id}, body=parse_rows(args.input, realtime=True), timeout=180)
        print_json({"status": status, "data": data})
        return 0 if status == 200 else 1

    status, _, launched = request("POST", "/dca/trigger", params={"collector": args.collector_id, "queue_next": args.queue}, body=parse_rows(args.input), timeout=60)
    if status != 200 or not isinstance(launched, dict) or "collection_id" not in launched:
        print_json({"status": status, "data": launched})
        return 0 if status == 200 else 1
    collection_id = launched["collection_id"]
    final_status, data = poll("/dca/dataset", params={"id": collection_id}, timeout_seconds=args.timeout, interval_seconds=args.poll, ready=ready)
    print_json({"trigger_status": status, "collection_id": collection_id, "status": final_status, "data": data})
    return 0 if final_status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
