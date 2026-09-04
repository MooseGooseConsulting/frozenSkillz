import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "plugins" / "codex-thread-organizer"
SKILL_ROOT = PACKAGE_ROOT / "skills" / "codex-thread-organizer"


class CodexThreadOrganizerContractTests(unittest.TestCase):
    def test_router_exposes_real_routes_and_references(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        expected_references = (
            "shared-conversation-model.md",
            "emoji-taxonomy.md",
            "codex-sidebar-adapter.md",
            "chatgpt-web-adapter.md",
            "cross-surface-bridge.md",
            "title-grammar.md",
            "cross-task-review.md",
            "periodic-automation.md",
        )

        self.assertIn("Codex sidebar", skill)
        self.assertIn("ChatGPT web", skill)
        self.assertIn("ask which one", skill)
        self.assertIn("not a proposal-only", skill)
        self.assertIn("different resources", skill)
        for name in expected_references:
            self.assertTrue((SKILL_ROOT / "references" / name).is_file(), name)
            self.assertIn(name, skill)

    def test_adapters_preserve_coverage_and_mutation_boundaries(self):
        codex = (
            SKILL_ROOT / "references" / "codex-sidebar-adapter.md"
        ).read_text(encoding="utf-8")
        chatgpt = (
            SKILL_ROOT / "references" / "chatgpt-web-adapter.md"
        ).read_text(encoding="utf-8")
        grammar = (SKILL_ROOT / "references" / "title-grammar.md").read_text(
            encoding="utf-8"
        )
        taxonomy = (SKILL_ROOT / "references" / "emoji-taxonomy.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("list_threads` with `limit: 50`", codex)
        self.assertIn("fewer than 50 non-pinned rows", codex)
        self.assertIn("title-mutable", codex)
        self.assertIn("names the container action", codex)
        self.assertIn("controllable `chatgpt.com` browser surface", chatgpt)
        self.assertIn("direct-execution route", chatgpt)
        self.assertIn("explicitly asks to move chats to Projects", chatgpt)
        self.assertIn("three to five meaningful emoji", grammar)
        self.assertIn("attention remains leftmost", grammar.lower())
        self.assertIn("lifecycle marker last", grammar)
        self.assertIn("Combination seeds", taxonomy)

    def test_human_design_document_is_not_runtime_instruction(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("do not load it as runtime instructions", skill)
        self.assertIn("does not load this README", readme)
        self.assertIn("direct-execution tool", readme)

    def test_manifest_and_trigger_metadata_match_the_contract(self):
        manifest = json.loads(
            (PACKAGE_ROOT / ".codex-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        trigger_cases = json.loads(
            (SKILL_ROOT / "evals" / "triggers.json").read_text(encoding="utf-8")
        )

        self.assertEqual(manifest["version"], "2.8.0")
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"][0]), 128)
        queries = [
            case["query"]
            for split in ("train", "validation", "held_out")
            for case in trigger_cases[split]
            if case["should_trigger"]
        ]
        self.assertTrue(any("ChatGPT web" in query for query in queries))


if __name__ == "__main__":
    unittest.main()
