"""Shared direct HTTP helpers for the Bright Data skill.

Run through Hyperagent RunWithCredentials so BRIGHTDATA_API_KEY is injected.
Never print or persist the credential.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

API_BASE = "https://api.brightdata.com"


def token() -> str:
    value = os.environ.get("BRIGHTDATA_API_KEY") or os.environ.get("BRIGHTDATA_API_TOKEN")
    if not value:
        raise SystemExit("BRIGHTDATA_API_KEY is missing. Run this through RunWithCredentials for the brightdata skill.")
    return value


def api_url(path: str, params: dict[str, Any] | None = None) -> str:
    suffix = ""
    if params:
        suffix = "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return f"{API_BASE}{path}{suffix}"


def request(
    method: str,
    path: str,
    body: Any | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 180,
    raw: bool = False,
) -> tuple[int, dict[str, str], Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Authorization": f"Bearer {token()}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(api_url(path, params), data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = response.read()
            headers_out = dict(response.headers)
            if raw:
                return response.status, headers_out, payload
            text = payload.decode("utf-8", errors="replace")
            try:
                return response.status, headers_out, json.loads(text)
            except json.JSONDecodeError:
                return response.status, headers_out, text
    except urllib.error.HTTPError as error:
        payload = error.read()
        headers_out = dict(error.headers)
        if raw:
            return error.code, headers_out, payload
        text = payload.decode("utf-8", errors="replace")
        try:
            return error.code, headers_out, json.loads(text)
        except json.JSONDecodeError:
            return error.code, headers_out, text


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def poll(
    path: str,
    params: dict[str, Any],
    timeout_seconds: int = 600,
    interval_seconds: int = 5,
    ready: callable | None = None,
) -> tuple[int, Any]:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status, _, body = request("GET", path, params=params, timeout=60)
        if ready and ready(status, body):
            return status, body
        if not ready and status == 200:
            return status, body
        if status not in (200, 202):
            return status, body
        time.sleep(interval_seconds)
    return 408, {"error": "Timed out while waiting for Bright Data result", "path": path, "params": params}
