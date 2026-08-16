import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "plugins" / "codex-thread-organizer" / "tools" / "proposal_contract.py"
FIXTURE_PATH = (
    ROOT
    / "plugins"
    / "codex-thread-organizer"
    / "skills"
    / "codex-thread-organizer"
    / "evals"
    / "fixtures"
    / "chatgpt-forward-30.json"
)
SPEC = importlib.util.spec_from_file_location("organizer_proposal_contract", MODULE_PATH)
contract = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = contract
SPEC.loader.exec_module(contract)


class ChatGPTOrganizerForwardFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.records = {record["id"]: record for record in cls.batch["records"]}

    def test_thirty_chat_forward_proposal_preserves_required_evidence(self):
        result = contract.validate_read_only_batch(self.batch)
        self.assertEqual(result["records"], 30)
        self.assertEqual(result["unreadable"], 1)
        self.assertGreaterEqual(result["relationships"], 20)
        self.assertGreaterEqual(result["changed_titles"], 28)

    def test_fixture_covers_generic_titles_projects_and_relationship_shapes(self):
        generic = {"New chat", "Followup", "Part 2", "Chat", "Plan", "Error"}
        self.assertTrue(any(r["current_title"] in generic for r in self.records.values()))
        self.assertTrue(any(r["current_project"] == "none" for r in self.records.values()))
        self.assertEqual(self.records["c08"]["proposed_project"], "Personal")
        self.assertEqual(self.records["c08"]["relationships"][0]["kind"], "duplicates")
        self.assertEqual(self.records["c04"]["relationships"][0]["kind"], "corrects")
        self.assertEqual(self.records["c09"]["relationships"][0]["kind"], "continues")
        self.assertEqual(self.records["c10"]["relationships"][0]["kind"], "supersedes")

    def test_unreadable_preview_and_self_correction_fail_closed(self):
        self.assertEqual(self.records["c11"]["acquisition"], "unreadable")
        self.assertIsNone(self.records["c11"]["proposed_title"])
        self.assertTrue(self.records["c23"]["preview_emoji"]["chrome_rendering_confirmed"])
        revision = self.records["c24"]["proposal_revision"]
        self.assertEqual(revision["failure"], "generic title")
        self.assertNotEqual(revision["initial_title"], revision["final_title"])

    def test_visible_rubric_grades_are_complete_and_titles_fit_utf16_target(self):
        grades = contract.grade(self.batch)
        self.assertEqual(set(grades), {
            "body_coverage", "title_specificity", "cluster_cohesion", "emoji_fit",
            "relationship_confidence", "collision_risk",
        })
        self.assertGreaterEqual(grades["body_coverage"], 0.95)
        self.assertGreaterEqual(grades["relationship_confidence"], 0.85)
        for record in self.records.values():
            if record.get("acquisition") != "unreadable":
                self.assertLessEqual(contract.utf16_units(record["proposed_title"]), 60)


if __name__ == "__main__":
    unittest.main()
