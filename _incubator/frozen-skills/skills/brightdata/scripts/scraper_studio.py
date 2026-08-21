#!/usr/bin/env python3
"""Use account-owned Bright Data Scraper Studio collectors through DCA APIs.

Running existing collectors is read/execute behavior. Creating or AI-healing a
collector mutates account-owned scraper state; use those subcommands only when
explicitly requested.

Examples:
  python3 scraper_studio.py list
  python3 scraper_studio.py run c_example --input '[{"url":"https://target.example"}]'
  python3 scraper_studio.py realtime c_example --input '{"url":"https://target.example"}'
  python3 scraper_studio.py realtime-async c_example --input '{"url":"https://target.example"}'
  python3 scraper_studio.py create --name example --deliver deliver.json --description 'Extract product fields' --url https://target.example/product/1
  python3 scraper_studio.py heal c_example --prompt 'Fix the broken product selectors' --input '{"url":"https://target.example/product/1"}'
  python3 scraper_studio.py job j_example
  python3 scraper_studio.py jobs c_example
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import poll, print_json, request


def parse_json_or_file(raw: str):
    path = Path(raw)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else json.loads(raw)


def parse_rows(raw: str, realtime: bool = False):
    value = parse_json_or_file(raw)
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


def ai_ready(status: int, body: object) -> bool:
    return status == 200 and isinstance(body, dict) and body.get("status") in {"done", "failed"}


def ai_ok(status: int, body: object) -> bool:
    return status == 200 and isinstance(body, dict) and body.get("status") == "done"


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
    rt.add_argument("--request-timeout", type=int, default=50, choices=range(25, 51), metavar="25..50")

    rta = sub.add_parser("realtime-async")
    rta.add_argument("collector_id")
    rta.add_argument("--input", required=True)
    rta.add_argument("--timeout", type=int, default=180)
    rta.add_argument("--poll", type=int, default=2)

    create = sub.add_parser("create")
    create.add_argument("--name", required=True)
    create.add_argument("--deliver", required=True, help="Delivery JSON object or path; prefer a file if it contains credentials")
    create.add_argument("--description", required=True)
    create.add_argument("--url", required=True, help="One representative URL for AI generation")
    create.add_argument("--timeout", type=int, default=900)
    create.add_argument("--poll", type=int, default=5)

    heal = sub.add_parser("heal")
    heal.add_argument("collector_id")
    heal.add_argument("--prompt", required=True)
    heal.add_argument("--input", help="Optional JSON object/array or path for custom_input")
    heal.add_argument("--timeout", type=int, default=900)
    heal.add_argument("--poll", type=int, default=5)

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

    if args.command == "create":
        deliver = parse_json_or_file(args.deliver)
        if not isinstance(deliver, dict):
            parser.error("--deliver must resolve to one JSON object")
        status, _, created = request("POST", "/dca/collector", body={"name": args.name, "deliver": deliver}, timeout=60)
        collector_id = created.get("id") if isinstance(created, dict) else None
        if status != 200 or not collector_id:
            print_json({"status": status, "data": created})
            return 1
        flow_status, _, flow = request(
            "POST",
            f"/dca/collectors/{collector_id}/automate_template",
            body={"description": args.description, "urls": [args.url]},
            timeout=60,
        )
        if flow_status != 200:
            print_json({"status": flow_status, "collector_id": collector_id, "create": created, "data": flow})
            return 1
        final_status, progress = poll(
            f"/dca/collectors/{collector_id}/automate_template/progress",
            params={},
            timeout_seconds=args.timeout,
            interval_seconds=args.poll,
            ready=ai_ready,
        )
        print_json({"status": final_status, "collector_id": collector_id, "create": created, "ai_job": flow, "progress": progress})
        return 0 if ai_ok(final_status, progress) else 1

    if args.command == "heal":
        body = {"prompt": args.prompt}
        if args.input:
            body["custom_input"] = parse_rows(args.input)
        status, _, started = request("POST", f"/dca/collectors/{args.collector_id}/refactor_template", body=body, timeout=60)
        if status != 200:
            print_json({"status": status, "collector_id": args.collector_id, "data": started})
            return 1
        final_status, progress = poll(
            f"/dca/collectors/{args.collector_id}/refactor_template/progress",
            params={},
            timeout_seconds=args.timeout,
            interval_seconds=args.poll,
            ready=ai_ready,
        )
        print_json({"status": final_status, "collector_id": args.collector_id, "ai_job": started, "progress": progress})
        return 0 if ai_ok(final_status, progress) else 1

    if args.command == "realtime":
        status, _, data = request(
            "POST",
            "/dca/crawl",
            params={"collector": args.collector_id, "timeout": f"{args.request_timeout}s"},
            body=parse_rows(args.input, realtime=True),
            timeout=args.request_timeout + 10,
        )
        print_json({"status": status, "data": data})
        return 0 if status in (200, 202) else 1
    if args.command == "realtime-async":
        status, _, launched = request("POST", "/dca/trigger_immediate", params={"collector": args.collector_id}, body=parse_rows(args.input, realtime=True), timeout=60)
        response_id = launched.get("response_id") if isinstance(launched, dict) else None
        if status != 200 or not response_id:
            print_json({"status": status, "data": launched})
            return 1
        final_status, data = poll(
            "/dca/get_result",
            params={"response_id": response_id},
            timeout_seconds=args.timeout,
            interval_seconds=args.poll,
            ready=lambda s, b: s == 200 and not (isinstance(b, dict) and b.get("status") in {"pending", "running"}),
        )
        print_json({"trigger_status": status, "response_id": response_id, "status": final_status, "data": data})
        return 0 if final_status == 200 else 1

    status, _, launched = request("POST", "/dca/trigger", params={"collector": args.collector_id, "queue_next": args.queue}, body=parse_rows(args.input), timeout=60)
    if status != 200 or not isinstance(launched, dict) or "collection_id" not in launched:
        print_json({"status": status, "data": launched})
        return 1
    collection_id = launched["collection_id"]
    final_status, data = poll("/dca/dataset", params={"id": collection_id}, timeout_seconds=args.timeout, interval_seconds=args.poll, ready=ready)
    print_json({"trigger_status": status, "collection_id": collection_id, "status": final_status, "data": data})
    return 0 if final_status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
