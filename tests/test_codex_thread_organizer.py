import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "codex-thread-organizer"
SHARED_PLUGIN_ROOT = ROOT / "plugins" / "frozen-skills"
ORGANIZER_PLUGIN_ROOT = ROOT / "plugins" / "codex-thread-organizer"
SKILL_ROOT = ORGANIZER_PLUGIN_ROOT / "skills" / SKILL_NAME
CONVERSATION_ANALYSIS = SKILL_ROOT / "references" / "conversation-analysis.md"
EMOJI_TAXONOMY = SKILL_ROOT / "references" / "semantic-emoji-taxonomy.md"
TITLE_RULES = SKILL_ROOT / "references" / "title-rules.md"
CODEX_ADAPTER = SKILL_ROOT / "references" / "codex-sidebar-adapter.md"
CHATGPT_ADAPTER = SKILL_ROOT / "references" / "chatgpt-web-adapter.md"
PERIODIC_AUTOMATION = SKILL_ROOT / "references" / "periodic-automation.md"
TRIGGER_CASES = SKILL_ROOT / "evals" / "triggers.json"
OPENAI_METADATA = SKILL_ROOT / "agents" / "openai.yaml"
SYNC_SCRIPT = ROOT / "scripts" / "sync_frozen_skills.py"
SYNC_SPEC = importlib.util.spec_from_file_location("organizer_sync", SYNC_SCRIPT)
sync_module = importlib.util.module_from_spec(SYNC_SPEC)
assert SYNC_SPEC.loader is not None
sys.modules[SYNC_SPEC.name] = sync_module
SYNC_SPEC.loader.exec_module(sync_module)


class CodexThreadOrganizerPackagingTests(unittest.TestCase):
    def test_shared_semantics_and_adapter_boundaries(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        analysis_text = CONVERSATION_ANALYSIS.read_text(encoding="utf-8")
        taxonomy_text = EMOJI_TAXONOMY.read_text(encoding="utf-8")
        title_text = TITLE_RULES.read_text(encoding="utf-8")
        codex_text = CODEX_ADAPTER.read_text(encoding="utf-8")
        chatgpt_text = CHATGPT_ADAPTER.read_text(encoding="utf-8")
        automation_text = PERIODIC_AUTOMATION.read_text(encoding="utf-8")
        openai_text = OPENAI_METADATA.read_text(encoding="utf-8")
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        trigger_data = json.loads(TRIGGER_CASES.read_text(encoding="utf-8"))

        for marker in ("\U0001F534", "\U0001F7E1", "\u2705", "\u23F8\uFE0F", "\U0001F6A7", "\U0001F4CC", "\u21AA\uFE0F", "\U0001F5C4\uFE0F"):
            self.assertIn(marker, codex_text)

        for classification in (
            "continues",
            "supersedes",
            "duplicates",
            "corrects",
            "related",
            "independent",
        ):
            self.assertIn(classification, analysis_text.lower())

        combined = "\n".join((skill_text, analysis_text, taxonomy_text, title_text, codex_text, chatgpt_text, automation_text))
        combined_lower = combined.lower()
        self.assertIn("source id", analysis_text.lower())
        self.assertIn("detailed subject summary", analysis_text.lower())
        self.assertIn("project", analysis_text.lower())
        self.assertIn("subagent", combined_lower)
        self.assertIn("wait for explicit approval", chatgpt_text.lower())
        self.assertIn("do not infer codex completion state", chatgpt_text.lower())
        self.assertIn("60", title_text)
        self.assertIn("unicode emoji v18.0 beta preview", taxonomy_text.lower())
        self.assertIn("chrome proof", taxonomy_text.lower())
        self.assertIn("rename", openai_text.lower())
        self.assertIn("chatgpt-web adapter", readme_text.lower())
        self.assertIn("proposal-first", chatgpt_text.lower())

        for classification in (
            "done",
            "active-remaining",
            "continued-elsewhere",
            "parked-unclear",
        ):
            self.assertIn(classification, automation_text.lower())

        positive_queries = [
            case["query"]
            for split in ("train", "validation", "held_out")
            for case in trigger_data[split]
            if case["should_trigger"]
        ]
        self.assertTrue(any("rename" in query.lower() for query in positive_queries))
        self.assertTrue(
            any("recent relevant" in query.lower() for query in positive_queries)
        )

        for obsolete in (
            "proposal-only",
            "authorized title batch",
            "coupled transition",
            "roll back the new red",
            "fresh manifest before retrying",
        ):
            self.assertNotIn(obsolete, combined_lower)
            self.assertNotIn(obsolete, openai_text.lower())

        self.assertNotIn("proposes sparse semantic titles", readme_text.lower())

    def test_skill_is_packaged_for_codex_only(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        openai_metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        tracker_text = (ROOT / "docs" / "skill-review" / "tracker.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Packaging is Codex-only", skill_text)
        self.assertIn("$codex-thread-organizer", openai_metadata)
        self.assertIn(
            "| `codex-thread-organizer` | active | Codex-only dedicated package with shared conversation semantics",
            tracker_text,
        )

        manifests = {
            "claude": ROOT / "plugins" / "frozen-skills" / ".claude-plugin" / "plugin.json",
            "codex": ROOT / "plugins" / "frozen-skills" / ".codex-plugin" / "plugin.json",
            "cursor": ROOT / "plugins" / "frozen-skills" / ".cursor-plugin" / "plugin.json",
            "gemini": ROOT / "plugins" / "frozen-skills" / "gemini-extension.json",
        }
        for manifest in manifests.values():
            data = json.loads(manifest.read_text(encoding="utf-8"))
            active_names = {entry["name"] for entry in data.get("skills", [])}
            self.assertNotIn(SKILL_NAME, active_names, manifest.as_posix())

        self.assertFalse(
            (ROOT / "_incubator" / "frozen-skills" / "skills" / SKILL_NAME).exists()
        )
        self.assertFalse((SHARED_PLUGIN_ROOT / "skills" / SKILL_NAME).exists())

        organizer_plugin = json.loads(
            (ORGANIZER_PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(organizer_plugin["name"], SKILL_NAME)
        self.assertEqual(organizer_plugin["skills"], "./skills/")

        distribution = json.loads(
            (ROOT / "plugins" / "distribution.json").read_text(encoding="utf-8")
        )
        shared_names = {entry["name"] for entry in distribution["shared"]}
        self.assertNotIn(SKILL_NAME, shared_names)
        for consumer, entries in distribution["consumers"].items():
            names = {entry["name"] for entry in entries}
            assertion = self.assertIn if consumer == "codex" else self.assertNotIn
            assertion(SKILL_NAME, names, consumer)

        selected = {}
        for consumer in manifests:
            _plugin_root, _version, _consumer, sources = sync_module.load_distribution(
                ROOT, consumer
            )
            selected[consumer] = {source.name for source in sources}

        self.assertIn(SKILL_NAME, selected["codex"])
        for consumer in ("claude", "cursor", "gemini"):
            self.assertNotIn(SKILL_NAME, selected[consumer])

    def test_skill_inventories_all_accessible_sidebar_conversations(self):
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        evals = json.loads(
            (SKILL_ROOT / "evals" / "triggers.json").read_text(encoding="utf-8")
        )

        adapter_text = CODEX_ADAPTER.read_text(encoding="utf-8")
        chatgpt_text = CHATGPT_ADAPTER.read_text(encoding="utf-8")
        self.assertIn("title-mutable", adapter_text)
        self.assertIn("not title-mutable", adapter_text)
        self.assertNotIn("not-title-mutable", adapter_text)
        self.assertIn("bounded", adapter_text)
        self.assertIn("partial coverage", adapter_text)
        # A bounded listing must never be reported as a complete one: the
        # coverage status travels with the total.
        self.assertIn("coverage", adapter_text)
        self.assertNotIn("full inventory total", adapter_text)
        self.assertNotIn("do not use for ChatGPT", skill_text.lower())
        self.assertIn("approval", chatgpt_text.lower())

        # The 60 UTF-16 ceiling keeps its provenance; it is the only evidence
        # for the number, and it is verified for Codex targets specifically.
        self.assertIn("60 UTF-16", adapter_text)
        self.assertIn("conservative ChatGPT target", TITLE_RULES.read_text(encoding="utf-8"))

        chatgpt_queries = {
            item["query"]: item["should_trigger"]
            for split in ("train", "validation", "held_out")
            for item in evals[split]
            if "chatgpt" in item["query"].lower()
        }
        for query in (
            "Organize my ChatGPT web conversation history",
            "Organize my ChatGPT web conversation history that appears in the Codex sidebar",
        ):
            self.assertIn(query, chatgpt_queries)
            self.assertTrue(chatgpt_queries[query], query)

        other_client_negatives = {
            item["query"]: item["should_trigger"]
            for split in ("train", "validation", "held_out")
            for item in evals[split]
            if not item["should_trigger"]
        }
        self.assertIn("Add emoji names to my Claude Code sessions", other_client_negatives)
        self.assertIn("Rename this Git branch and clean up stale files", other_client_negatives)
        self.assertIn("Build a browser extension that renames chat tabs", other_client_negatives)

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

                checked = sync_module.sync(
                    ROOT,
                    destination,
                    consumer=consumer,
                    apply=False,
                    prune=False,
                    force=False,
                )
                self.assertFalse(checked.changes, consumer)
                installed = {
                    path.name
                    for path in destination.iterdir()
                    if (path / "SKILL.md").is_file()
                }
                expected = shared | ({SKILL_NAME} if consumer == "codex" else set())
                self.assertEqual(installed, expected, consumer)

                state = json.loads(
                    (destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
                )
                self.assertEqual(state["consumer"], consumer)


if __name__ == "__main__":
    unittest.main()
