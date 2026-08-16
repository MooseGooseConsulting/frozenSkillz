"""Fail-closed ChatGPT history export/import primitives."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class HistorySyncError(RuntimeError):
    """Stop-the-run error; callers must not substitute a fallback acquisition path."""


@dataclass(frozen=True)
class ImportResult:
    conversations: int
    revisions: int
    tombstoned: int
    projects: int


def default_storage_root(environ: dict[str, str] | None = None, system: str | None = None) -> Path:
    environ = os.environ if environ is None else environ
    system = platform.system() if system is None else system
    if system == "Windows":
        if not environ.get("LOCALAPPDATA"):
            raise HistorySyncError("LOCALAPPDATA is required on Windows")
        return Path(environ["LOCALAPPDATA"]) / "frozenSkillz" / "chatgpt-history"
    return Path(environ["XDG_DATA_HOME"]) / "frozenSkillz" / "chatgpt-history" if environ.get("XDG_DATA_HOME") else Path.home() / ".local" / "share" / "frozenSkillz" / "chatgpt-history"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def payload_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class EndpointClient:
    """Exact endpoint client. Authentication expiry and schema drift are hard errors."""

    def __init__(self, base_url: str, session_cookie: str, timeout: float = 30.0):
        if not session_cookie:
            raise HistorySyncError("authentication is required; reauthenticate explicitly")
        self.base_url, self.session_cookie, self.timeout = base_url.rstrip("/"), session_cookie, timeout

    def get_json(self, path: str) -> Any:
        request = Request(f"{self.base_url}{path}", headers={"Cookie": self.session_cookie, "Accept": "application/json", "User-Agent": "frozenSkillz-history-sync/1"})
        try:
            with urlopen(request, timeout=self.timeout) as response:  # nosec B310: caller supplies HTTPS base URL
                if response.status != 200:
                    raise HistorySyncError(f"endpoint failure {response.status} at {path}")
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code in {401, 403}:
                raise HistorySyncError("authentication expired; reauthenticate explicitly") from exc
            raise HistorySyncError(f"endpoint drift or HTTP failure {exc.code} at {path}") from exc
        except (URLError, TimeoutError) as exc:
            raise HistorySyncError(f"request timeout or network failure at {path}") from exc
        except json.JSONDecodeError as exc:
            raise HistorySyncError(f"endpoint returned malformed JSON at {path}") from exc


def items(payload: Any, endpoint: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "conversations", "data"):
            if isinstance(payload.get(key), list):
                return payload[key]
    raise HistorySyncError(f"endpoint drift: {endpoint} did not contain a list")


def conversation_id(summary: dict[str, Any]) -> str:
    value = summary.get("id") or summary.get("conversation_id")
    if not isinstance(value, str) or not value:
        raise HistorySyncError("endpoint drift: conversation without an ID")
    return value


def export_snapshot(root: Path, client: Any, *, page_size: int = 100, max_pages: int = 1000, run_id: str | None = None) -> Path:
    """Fetch normal history, Projects, and every raw mapping into an immutable snapshot."""
    if page_size < 1 or max_pages < 1:
        raise HistorySyncError("page_size and max_pages must be positive")
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot = root / "raw" / run_id
    if snapshot.exists():
        raise HistorySyncError(f"immutable snapshot already exists: {snapshot}")
    (snapshot / "conversations").mkdir(parents=True)
    summaries: list[dict[str, Any]] = []
    for page_number in range(max_pages):
        page = items(client.get_json(f"/backend-api/conversations?offset={page_number * page_size}&limit={page_size}"), "conversations")
        summaries.extend(page)
        if len(page) < page_size:
            break
    else:
        raise HistorySyncError("incomplete export: pagination exceeded max_pages")
    if len({conversation_id(item) for item in summaries}) != len(summaries):
        raise HistorySyncError("incomplete export: duplicate conversation IDs")
    projects = items(client.get_json("/backend-api/projects"), "projects")
    entries = []
    for summary in summaries:
        ident = conversation_id(summary)
        mapping = client.get_json(f"/backend-api/conversation/{ident}")
        if not isinstance(mapping, dict) or not isinstance(mapping.get("mapping"), dict):
            raise HistorySyncError(f"endpoint drift: raw mapping missing for {ident}")
        relative = Path("conversations") / f"{ident}.json"
        raw = snapshot / relative
        raw.write_bytes(canonical_bytes(mapping))
        entries.append({"id": ident, "summary": summary, "raw_path": relative.as_posix(), "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest()})
    manifest = {"schema": 1, "run_id": run_id, "created_at": utc_now(), "complete": True, "conversation_count": len(entries), "projects": projects, "conversations": entries}
    manifest["sha256"] = payload_hash({key: value for key, value in manifest.items() if key != "sha256"})
    (snapshot / "manifest.json").write_bytes(canonical_bytes(manifest))
    return snapshot


SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS sync_runs (run_id TEXT PRIMARY KEY, imported_at TEXT NOT NULL, complete INTEGER NOT NULL, manifest_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, name TEXT, updated_at TEXT, missing INTEGER NOT NULL DEFAULT 0, last_run_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS conversations (id TEXT PRIMARY KEY, title TEXT, project_id TEXT, source_updated_at TEXT, content_hash TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0, missing INTEGER NOT NULL DEFAULT 0, last_run_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS revisions (id INTEGER PRIMARY KEY, conversation_id TEXT NOT NULL, source_updated_at TEXT, content_hash TEXT NOT NULL, raw_path TEXT NOT NULL, imported_at TEXT NOT NULL, UNIQUE(conversation_id, source_updated_at, content_hash));
CREATE TABLE IF NOT EXISTS messages (conversation_id TEXT NOT NULL, node_id TEXT NOT NULL, parent_id TEXT, author_role TEXT, content TEXT, attachment_metadata TEXT, PRIMARY KEY(conversation_id, node_id));
CREATE TABLE IF NOT EXISTS branches (conversation_id TEXT NOT NULL, node_id TEXT NOT NULL, parent_id TEXT, PRIMARY KEY(conversation_id, node_id));
CREATE TABLE IF NOT EXISTS relationships (id INTEGER PRIMARY KEY, source_id TEXT NOT NULL, target_id TEXT NOT NULL, kind TEXT NOT NULL, evidence TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS classifications (conversation_id TEXT PRIMARY KEY, classification TEXT, confidence REAL, evidence TEXT);
CREATE TABLE IF NOT EXISTS proposals (id INTEGER PRIMARY KEY, conversation_id TEXT NOT NULL, proposed_title TEXT, proposed_project_id TEXT, status TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS applied_changes (id INTEGER PRIMARY KEY, conversation_id TEXT NOT NULL, change_kind TEXT NOT NULL, before_value TEXT, after_value TEXT, applied_at TEXT NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS conversation_fts USING fts5(conversation_id UNINDEXED, content);
"""


def read_manifest(snapshot: Path) -> dict[str, Any]:
    try:
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HistorySyncError("malformed manifest") from exc
    expected = manifest.get("sha256")
    actual = payload_hash({key: value for key, value in manifest.items() if key != "sha256"})
    if manifest.get("schema") != 1 or expected != actual or not isinstance(manifest.get("conversations"), list) or not isinstance(manifest.get("projects"), list):
        raise HistorySyncError("malformed manifest or hash mismatch")
    return manifest


def _content(node: dict[str, Any]) -> str:
    content = ((node.get("message") or {}).get("content") or {})
    parts = content.get("parts") if isinstance(content, dict) else None
    return "\n".join(part for part in parts if isinstance(part, str)) if isinstance(parts, list) else content if isinstance(content, str) else ""


def import_snapshot(root: Path, snapshot: Path) -> ImportResult:
    manifest = read_manifest(snapshot)
    root.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(root / "history.sqlite3")
    db.executescript(SCHEMA)
    revisions = tombstoned = 0
    seen: set[str] = set()
    try:
        with db:
            db.execute("INSERT OR REPLACE INTO sync_runs VALUES (?, ?, ?, ?)", (manifest["run_id"], utc_now(), int(bool(manifest["complete"])), manifest["sha256"]))
            for project in manifest["projects"]:
                if not isinstance(project.get("id"), str):
                    raise HistorySyncError("malformed project")
                db.execute("INSERT INTO projects VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,updated_at=excluded.updated_at,missing=0,last_run_id=excluded.last_run_id", (project["id"], project.get("name") or project.get("title"), project.get("updated_at"), 0, manifest["run_id"]))
            for entry in manifest["conversations"]:
                ident, relative, summary = entry.get("id"), entry.get("raw_path"), entry.get("summary")
                if not isinstance(ident, str) or not isinstance(relative, str) or not isinstance(summary, dict):
                    raise HistorySyncError("malformed conversation manifest entry")
                raw = (snapshot / relative).read_bytes()
                if hashlib.sha256(raw).hexdigest() != entry.get("raw_sha256"):
                    raise HistorySyncError(f"raw export hash mismatch for {ident}")
                mapping = json.loads(raw)
                if not isinstance(mapping.get("mapping"), dict):
                    raise HistorySyncError(f"malformed raw mapping for {ident}")
                content_hash = payload_hash(mapping)
                updated = summary.get("update_time", summary.get("updated_at"))
                db.execute("INSERT INTO conversations VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,project_id=excluded.project_id,source_updated_at=excluded.source_updated_at,content_hash=excluded.content_hash,archived=excluded.archived,missing=0,last_run_id=excluded.last_run_id", (ident, summary.get("title"), summary.get("project_id", summary.get("project")), updated, content_hash, int(bool(summary.get("is_archived", summary.get("archived", False)))), 0, manifest["run_id"]))
                cursor = db.execute("INSERT OR IGNORE INTO revisions(conversation_id,source_updated_at,content_hash,raw_path,imported_at) VALUES(?,?,?,?,?)", (ident, str(updated), content_hash, relative, utc_now()))
                if cursor.rowcount:
                    revisions += 1
                    db.execute("DELETE FROM messages WHERE conversation_id=?", (ident,)); db.execute("DELETE FROM branches WHERE conversation_id=?", (ident,)); db.execute("DELETE FROM conversation_fts WHERE conversation_id=?", (ident,))
                    content = []
                    for node_id, node in mapping["mapping"].items():
                        if not isinstance(node, dict): raise HistorySyncError(f"malformed mapping node for {ident}")
                        message = node.get("message") or {}; metadata = message.get("metadata") or {}; text = _content(node); attachments = metadata.get("attachments") or message.get("attachments") or []
                        db.execute("INSERT INTO messages VALUES(?,?,?,?,?,?)", (ident, node_id, node.get("parent"), (message.get("author") or {}).get("role"), text, json.dumps(attachments, sort_keys=True)))
                        db.execute("INSERT INTO branches VALUES(?,?,?)", (ident, node_id, node.get("parent")))
                        if text: content.append(text)
                    db.execute("INSERT INTO conversation_fts VALUES(?,?)", (ident, "\n".join(content)))
                seen.add(ident)
            if manifest["complete"]:
                placeholders = ",".join("?" for _ in seen) or "''"
                tombstoned = db.execute(f"UPDATE conversations SET missing=1 WHERE id NOT IN ({placeholders}) AND missing=0", tuple(seen)).rowcount
    finally:
        db.close()
    return ImportResult(len(seen), revisions, tombstoned, len(manifest["projects"]))
