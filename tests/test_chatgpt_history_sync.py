import hashlib
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.chatgpt_history_sync.core import (  # noqa: E402
    HistorySyncError,
    canonical_bytes,
    default_storage_root,
    export_snapshot,
    import_snapshot,
    payload_hash,
)


def mapping(text, attachment=False):
    return {
        "mapping": {
            "root": {"parent": None, "message": None},
            "user": {"parent": "root", "message": {"author": {"role": "user"}, "content": {"parts": [text]}, "metadata": {"attachments": [{"name": "image.png"}] if attachment else []}}},
            "assistant-a": {"parent": "user", "message": {"author": {"role": "assistant"}, "content": {"parts": ["answer"]}}},
            "assistant-b": {"parent": "user", "message": {"author": {"role": "assistant"}, "content": {"parts": ["alternate answer"]}}},
        }
    }


class FakeClient:
    def __init__(self, conversations, projects, raw):
        self.conversations, self.projects, self.raw = conversations, projects, raw
        self.calls = []

    def get_json(self, path):
        self.calls.append(path)
        if path == "/backend-api/projects":
            return {"items": self.projects}
        if path.startswith("/backend-api/conversations?"):
            from urllib.parse import parse_qs, urlparse
            query = parse_qs(urlparse(path).query)
            offset, limit = int(query["offset"][0]), int(query["limit"][0])
            return {"items": self.conversations[offset : offset + limit]}
        prefix = "/backend-api/conversation/"
        if path.startswith(prefix):
            return self.raw[path[len(prefix) :]]
        raise AssertionError(path)


class ChatGPTHistorySyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "store"
        self.conversations = [
            {"id": "a", "title": "Alpha", "update_time": "1", "project_id": "p1"},
            {"id": "b", "title": "Beta", "update_time": "2", "project_id": "p2", "is_archived": True},
        ]
        self.projects = [{"id": "p1", "name": "One"}, {"id": "p2", "name": "Two"}]
        self.raw = {"a": mapping("alpha searchable", True), "b": mapping("beta searchable")}

    def tearDown(self):
        self.temporary.cleanup()

    def export(self, run="run-one"):
        return export_snapshot(self.root, FakeClient(self.conversations, self.projects, self.raw), page_size=1, run_id=run)

    def test_export_completion_pagination_projects_and_raw_branches(self):
        snapshot = self.export()
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["complete"])
        self.assertEqual(manifest["conversation_count"], 2)
        self.assertEqual([p["id"] for p in manifest["projects"]], ["p1", "p2"])
        self.assertTrue((snapshot / "conversations" / "a.json").is_file())
        result = import_snapshot(self.root, snapshot)
        self.assertEqual((result.conversations, result.projects), (2, 2))
        db = sqlite3.connect(self.root / "history.sqlite3")
        self.assertEqual(db.execute("select count(*) from branches where conversation_id='a'").fetchone()[0], 4)
        self.assertIn("image.png", db.execute("select attachment_metadata from messages where conversation_id='a' and node_id='user'").fetchone()[0])
        self.assertEqual(db.execute("select count(*) from conversation_fts where conversation_fts match 'searchable'").fetchone()[0], 2)
        db.close()

    def test_import_is_idempotent_and_revisions_when_content_changes(self):
        first = self.export("one")
        self.assertEqual(import_snapshot(self.root, first).revisions, 2)
        self.assertEqual(import_snapshot(self.root, first).revisions, 0)
        self.raw["a"] = mapping("alpha changed", True)
        self.conversations[0]["update_time"] = "3"
        second = self.export("two")
        self.assertEqual(import_snapshot(self.root, second).revisions, 1)

    def test_project_move_and_archive_reconcile(self):
        import_snapshot(self.root, self.export("one"))
        self.conversations[0]["project_id"] = "p2"
        self.conversations[0]["is_archived"] = True
        import_snapshot(self.root, self.export("two"))
        db = sqlite3.connect(self.root / "history.sqlite3")
        self.assertEqual(db.execute("select project_id, archived from conversations where id='a'").fetchone(), ("p2", 1))
        db.close()

    def test_complete_snapshot_tombstones_missing_but_incomplete_does_not(self):
        import_snapshot(self.root, self.export("one"))
        self.conversations = [self.conversations[0]]
        self.raw.pop("b")
        second = self.export("two")
        self.assertEqual(import_snapshot(self.root, second).tombstoned, 1)
        db = sqlite3.connect(self.root / "history.sqlite3")
        db.execute("update conversations set missing=0 where id='b'")
        db.commit(); db.close()
        manifest_path = second / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["complete"] = False
        manifest["sha256"] = payload_hash({key: value for key, value in manifest.items() if key != "sha256"})
        manifest_path.write_bytes(canonical_bytes(manifest))
        self.assertEqual(import_snapshot(self.root, second).tombstoned, 0)

    def test_malformed_manifest_and_hash_mismatch_fail_hard(self):
        snapshot = self.export()
        (snapshot / "manifest.json").write_text("not json", encoding="utf-8")
        with self.assertRaisesRegex(HistorySyncError, "malformed manifest"):
            import_snapshot(self.root, snapshot)
        snapshot = self.export("two")
        raw = snapshot / "conversations" / "a.json"
        raw.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(HistorySyncError, "hash mismatch"):
            import_snapshot(self.root, snapshot)

    def test_endpoint_drift_auth_expiry_timeout_and_incomplete_pagination_fail_hard(self):
        class FailingClient:
            def get_json(self, path):
                raise HistorySyncError("authentication expired; reauthenticate explicitly")
        with self.assertRaisesRegex(HistorySyncError, "authentication expired"):
            export_snapshot(self.root, FailingClient(), run_id="auth")
        class DriftClient:
            def get_json(self, path): return {"unexpected": []}
        with self.assertRaisesRegex(HistorySyncError, "endpoint drift"):
            export_snapshot(self.root, DriftClient(), run_id="drift")
        client = FakeClient(self.conversations, self.projects, self.raw)
        with self.assertRaisesRegex(HistorySyncError, "incomplete export"):
            export_snapshot(self.root, client, page_size=1, max_pages=1, run_id="pages")

    def test_windows_and_linux_storage_paths(self):
        self.assertEqual(default_storage_root({"LOCALAPPDATA": "C:/Local"}, "Windows"), Path("C:/Local/frozenSkillz/chatgpt-history"))
        self.assertEqual(default_storage_root({"XDG_DATA_HOME": "/data"}, "Linux"), Path("/data/frozenSkillz/chatgpt-history"))
        self.assertEqual(default_storage_root({}, "Linux").parts[-3:], ("share", "frozenSkillz", "chatgpt-history"))

    def test_immutable_export_and_duplicate_ids_fail(self):
        self.export("one")
        with self.assertRaisesRegex(HistorySyncError, "already exists"):
            self.export("one")
        self.conversations.append(dict(self.conversations[0]))
        with self.assertRaisesRegex(HistorySyncError, "duplicate conversation IDs"):
            self.export("two")

    def test_systemd_scheduler_uses_user_scope_and_xdg_data_home(self):
        deployment = ROOT / "deployments" / "chatgpt-history-sync"
        service = (deployment / "chatgpt-history-sync.service").read_text(encoding="utf-8")
        timer = (deployment / "chatgpt-history-sync.timer").read_text(encoding="utf-8")
        self.assertIn("Type=oneshot", service)
        self.assertIn("chatgpt-history-sync sync", service)
        self.assertIn("XDG_DATA_HOME=%h/.local/share", service)
        self.assertIn("OnCalendar=daily", timer)
        self.assertIn("Persistent=true", timer)


if __name__ == "__main__":
    unittest.main()
