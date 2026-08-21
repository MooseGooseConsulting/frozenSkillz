#!/usr/bin/env python3
"""Direct client for Bright Data's hosted Pro MCP API.

Use for:
- scraping_browser_* browser automation without local Playwright credentials
- web_data_* tools not covered by the direct dataset runner
- search_engine, discover, scrape_as_html, scrape_batch, and session_stats

Examples:
  python3 mcp.py --list
  python3 mcp.py --tool web_data_npm_package --arguments '{"package_name":"@brightdata/mcp"}'
  python3 mcp.py --tool scraping_browser_navigate --arguments '{"url":"https://example.com"}'

Each process is one MCP session. For multi-step browser sequences, use the
--sequence file format so all calls share a browser session:
  [{"name":"scraping_browser_navigate","arguments":{"url":"https://example.com"}},
   {"name":"scraping_browser_get_text","arguments":{}}]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE = "https://mcp.brightdata.com/mcp"


def token() -> str:
    value = os.environ.get("BRIGHTDATA_API_KEY") or os.environ.get("BRIGHTDATA_API_TOKEN")
    if not value:
        raise SystemExit("BRIGHTDATA_API_KEY or BRIGHTDATA_API_TOKEN is required.")
    return value


def parse_sse(body: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in body.splitlines():
        if line.startswith("data: ") and line[6:].strip():
            try:
                records.append(json.loads(line[6:]))
            except json.JSONDecodeError:
                pass
    return records


def parse_response(body: str) -> list[dict[str, Any]]:
    stripped = body.strip()
    if not stripped:
        return []
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        return parse_sse(body)
    return [value] if isinstance(value, dict) else []


class Client:
    def __init__(self, groups: str | None = None, tools: str | None = None) -> None:
        query = {"token": token()}
        if groups:
            query["groups"] = groups
        if tools:
            query["tools"] = tools
        if not groups and not tools:
            query["pro"] = "1"
        self.url = f"{BASE}?{urllib.parse.urlencode(query)}"
        self.session_id: str | None = None
        self.next_id = 1

    def call(self, method: str, params: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
        return self.post(method, params, timeout)

    def post(self, method: str, params: dict[str, Any], timeout: int) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode(), method="POST", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                self.session_id = response.headers.get("Mcp-Session-Id", self.session_id)
                messages = parse_response(response.read().decode(errors="replace"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            return {"error": {"type": "transport_error", "message": str(exc)}, "id": request_id}
        for message in messages:
            if message.get("id") == request_id:
                return message
        return {"responses": messages}

    def initialize(self) -> dict[str, Any]:
        response = self.post("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "frozen-skills-brightdata", "version": "1.0"}}, 60)
        if response.get("error"):
            return response
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        payload = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode(), method="POST", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60):
                pass
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            return {"error": {"type": "transport_error", "message": str(exc)}}
        return response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--tool")
    parser.add_argument("--arguments", default="{}")
    parser.add_argument("--sequence", help="JSON array or path to JSON array of {name, arguments} calls sharing one MCP session")
    parser.add_argument("--groups")
    parser.add_argument("--tools")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    if not args.list and not args.tool and not args.sequence:
        parser.error("pass --list, --tool, or --sequence")
    try:
        tool_args = json.loads(args.arguments)
    except json.JSONDecodeError as exc:
        parser.error(f"invalid --arguments JSON: {exc}")
    client = Client(args.groups, args.tools)
    initialized = client.initialize()
    if initialized.get("error"):
        print(json.dumps(initialized, indent=2))
        return 1
    if args.list:
        result = client.post("tools/list", {}, 60)
        if result.get("error"):
            print(json.dumps(result, indent=2))
            return 1
        tool_list = result.get("result", {}).get("tools", [])
        print(json.dumps({"tool_count": len(tool_list), "tools": tool_list}, indent=2))
    elif args.sequence:
        source = args.sequence
        try:
            if source.lstrip().startswith("["):
                sequence = json.loads(source)
            else:
                with open(source, encoding="utf-8") as handle:
                    sequence = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"invalid --sequence: {exc}")
        if not isinstance(sequence, list):
            parser.error("--sequence must be a JSON array")
        results = []
        failed = False
        for item in sequence:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                parser.error("each sequence item must contain a string name")
            arguments = item.get("arguments", {})
            if not isinstance(arguments, dict):
                parser.error("each sequence arguments value must be an object")
            response = client.post("tools/call", {"name": item["name"], "arguments": arguments}, args.timeout)
            failed = failed or bool(response.get("error"))
            results.append({"name": item["name"], "response": response})
        print(json.dumps({"results": results}, indent=2))
        return 1 if failed else 0
    else:
        response = client.post("tools/call", {"name": args.tool, "arguments": tool_args}, args.timeout)
        print(json.dumps(response, indent=2))
        return 1 if response.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
