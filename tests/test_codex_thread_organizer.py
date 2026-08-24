import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "codex-thread-organizer"
PLUGIN_ROOT = ROOT / "plugins" / SKILL_NAME
SKILL_ROOT = PLUGIN_ROOT / "skills" / SKILL_NAME
SYNC_SCRIPT = ROOT / "scripts" / "sync_frozen_skills.py"
SYNC_SPEC = importlib.util.spec_from_file_location("organizer_sync", SYNC_SCRIPT)
sync_module = importlib.util.module_from_spec(SYNC_SPEC)
assert SYNC_SPEC.loader is not None
sys.modules[SYNC_SPEC.name] = sync_module
SYNC_SPEC.loader.exec_module(sync_module)


class CodexThreadOrganizerContractTests(unittest.TestCase):
    def test_router_is_explicit_and_proposal_only(self):
        router = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        notion = (SKILL_ROOT / "references" / "notion-proposal-report.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("in Codex Desktop only", router)
        self.assertIn("Local Codex title review", router)
        self.assertIn("ChatGPT web proposal", router)
        self.assertIn("allow_implicit_invocation` is off", router)
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("Do **not** invoke a native Codex title operation", router)
        self.assertIn("not an approval queue", router)
        self.assertIn("Codex Desktop Chat Organization Reports", notion)
        self.assertIn("No action executed", notion)
        self.assertIn("Chats Renamed` | `0`", notion)

    def test_local_route_requires_luna_corpus_review_and_linked_proposals(self):
        adapter = (SKILL_ROOT / "references" / "codex-sidebar-adapter.md").read_text(
            encoding="utf-8"
        )
        grammar = (SKILL_ROOT / "references" / "title-grammar.md").read_text(
            encoding="utf-8"
        )
        review = (SKILL_ROOT / "references" / "cross-task-review.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("title-mutable", adapter)
        self.assertIn("not title-mutable", adapter)
        self.assertIn("page, cursor, or load-more", adapter)
        self.assertIn("multiple `gpt-5.6-luna` subagents", adapter)
        self.assertIn("live coding-project/repository", adapter)
        self.assertIn("direct Codex task link", adapter)
        self.assertIn("Set the report's `Chats Renamed` property to `0`", adapter)
        self.assertIn("semantic **type** emoji", adapter)
        self.assertIn("does not rename a task", adapter.replace("\n", " "))
        self.assertIn("type of work", grammar)
        self.assertIn("Do not add `✅`", grammar)
        self.assertIn("does not rename a task", review)

    def test_chatgpt_route_requires_declared_cohort_spark_and_notion_links(self):
        adapter = (SKILL_ROOT / "references" / "chatgpt-web-adapter.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("`chrome_pilot`", adapter)
        self.assertIn("Codex 5.3 Spark", adapter)
        self.assertIn("do not silently replace", adapter)
        self.assertIn("at most 30 conversations", adapter)
        self.assertIn("next deferred cohort", adapter)
        self.assertIn("inventory-only", adapter)
        self.assertIn("direct `chatgpt.com` link", adapter)
        self.assertIn("exactly one row per body-reviewed chat", adapter)
        self.assertIn("Every cited repository, artifact, Codex task, and ChatGPT chat has a direct", adapter)
        self.assertIn("No action executed", adapter)
        for forbidden_heading in ("Apply only approval", "user approves", "post-mutation"):
            self.assertNotIn(forbidden_heading, adapter)

    def test_corpus_bridge_uses_bodies_not_matching_labels(self):
        router = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        shared = (SKILL_ROOT / "references" / "shared-conversation-model.md").read_text(
            encoding="utf-8"
        )
        bridge = (SKILL_ROOT / "references" / "cross-surface-bridge.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("reason over its concrete", router)
        self.assertIn("Matching labels are not prohibited evidence", router)
        self.assertIn("direct source link", shared)
        self.assertIn(
            "language-model reasoning must compare the actual body",
            shared.replace("\n", " "),
        )
        self.assertIn("Project name is useful evidence but is neither required nor enough", bridge)
        self.assertIn("direct links to both sources", bridge)
        self.assertIn("never authorizes a rename", bridge)

    def test_skill_is_packaged_for_codex_only(self):
        tracker = (ROOT / "docs" / "skill-review" / "tracker.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("| `codex-thread-organizer` | active | Codex-only, explicit-route", tracker)

        plugin = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(plugin["name"], SKILL_NAME)
        self.assertEqual(plugin["version"], "2.7.2")
        self.assertEqual(plugin["skills"], "./skills/")

        distribution = json.loads(
            (ROOT / "plugins" / "distribution.json").read_text(encoding="utf-8")
        )
        self.assertNotIn(SKILL_NAME, {entry["name"] for entry in distribution["shared"]})
        for consumer, entries in distribution["consumers"].items():
            names = {entry["name"] for entry in entries}
            (self.assertIn if consumer == "codex" else self.assertNotIn)(
                SKILL_NAME, names, consumer
            )

    def test_only_explicit_evals_trigger_the_skill(self):
        evals = json.loads(
            (SKILL_ROOT / "evals" / "triggers.json").read_text(encoding="utf-8")
        )
        positives = [
            item["query"]
            for split in ("train", "validation", "held_out")
            for item in evals[split]
            if item["should_trigger"]
        ]
        self.assertTrue(positives)
        self.assertTrue(all("$codex-thread-organizer" in query for query in positives))

        negatives = {
            item["query"]
            for split in ("train", "validation", "held_out")
            for item in evals[split]
            if not item["should_trigger"]
        }
        self.assertIn("Organize my ChatGPT web conversation history", negatives)

    def test_real_distribution_smoke_installs_organizer_only_for_codex(self):
        shared = {
            "agent-github-identity",
            "delegation-contract",
            "doppler",
            "external-skill-intake",
            "omc-reference",
            "pdm-cli-operations",
        }
        with tempfile.TemporaryDirectory() as temporary:
            smoke_root = Path(temporary)
            for consumer in ("claude", "codex", "cursor", "gemini"):
                destination = smoke_root / consumer
                applied = sync_module.sync(
                    ROOT,
                    destination,
                    consumer=consumer,
                    apply=True,
                    prune=False,
                    force=False,
                )
                self.assertFalse(applied.conflicts, consumer)
                installed = {
                    path.name
                    for path in destination.iterdir()
                    if (path / "SKILL.md").is_file()
                }
                expected = shared | ({SKILL_NAME} if consumer == "codex" else set())
                self.assertEqual(installed, expected, consumer)


if __name__ == "__main__":
    unittest.main()
