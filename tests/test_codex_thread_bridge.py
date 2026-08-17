import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "plugins" / "codex-thread-organizer" / "skills" / "codex-thread-organizer"
FIXTURE = ROOT / "tests" / "fixtures" / "chatgpt-large-history-cohort.json"


class CrossSurfaceBridgeContractTests(unittest.TestCase):
    def test_bridge_requires_actual_bodies_and_cannot_authorize_mutation(self):
        router = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        shared = (SKILL_ROOT / "references" / "shared-conversation-model.md").read_text(
            encoding="utf-8"
        )
        bridge = (SKILL_ROOT / "references" / "cross-surface-bridge.md").read_text(
            encoding="utf-8"
        )
        chatgpt = (SKILL_ROOT / "references" / "chatgpt-web-adapter.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("cross-surface bridge", router)
        self.assertIn("visible title, sidebar preview", shared)
        self.assertIn("both readable ChatGPT bodies and readable Codex task bodies", bridge)
        self.assertIn("Project name is useful evidence but is neither required nor enough", bridge)
        self.assertIn("confirmed", bridge)
        self.assertIn("plausible", bridge)
        self.assertIn("unresolved", bridge)
        self.assertIn("no-link", bridge)
        self.assertIn("never by itself authority to mutate", router.replace("\n", " "))
        self.assertIn("Codex bridge", chatgpt)
        self.assertIn("only confirmed bridges inform proposals", chatgpt)
        self.assertIn("each body-reviewed source in the declared", bridge)

    def test_large_history_contract_and_fixture_prevent_unbounded_claims(self):
        chatgpt = (SKILL_ROOT / "references" / "chatgpt-web-adapter.md").read_text(
            encoding="utf-8"
        )
        bridge = (SKILL_ROOT / "references" / "cross-surface-bridge.md").read_text(
            encoding="utf-8"
        )
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cohort = fixture["scope"]["body_review_cohort"]
        by_id = {item["id"]: item for item in fixture["conversations"]}

        self.assertIn("Never default to a full-history body review", chatgpt)
        self.assertIn("at most 30 conversations", chatgpt)
        self.assertIn("next deferred cohort", chatgpt)
        self.assertIn("inventory-only", chatgpt)
        self.assertIn("canonical-reference` **within the declared cohort**", chatgpt)
        self.assertIn("new-project-candidate", chatgpt)
        self.assertIn("project-merge-candidate", chatgpt)
        self.assertIn("was body-reviewed and is in the declared", chatgpt.replace("\n", " "))
        self.assertIn("canonical-reference`/`duplicate-or-superseded", chatgpt)
        self.assertIn("Do not compare unbounded ChatGPT or Codex histories", bridge)
        self.assertIn("Inventory-only titles or previews cannot", bridge.replace("\n", " "))

        self.assertGreater(fixture["history_total_estimate"], 30)
        self.assertLessEqual(len(cohort), fixture["scope"]["body_review_cohort_maximum"])
        self.assertEqual(fixture["scope"]["body_review_cohort_maximum"], 30)
        self.assertTrue(fixture["scope"]["deferred_set"]["next_cohort"])
        requested = set(fixture["scope"]["requested_chat_ids"])
        deferred = set(fixture["scope"]["deferred_set"]["conversation_ids"])
        self.assertEqual(requested, set(cohort) | deferred)
        self.assertTrue(set(cohort).isdisjoint(deferred))
        self.assertEqual(by_id["chat-101"]["canonical_scope"], "within this declared cohort")
        self.assertEqual(by_id["chat-103"]["proposed_mutation"], "none")
        self.assertEqual(by_id["chat-104"]["project_action"], "none")
        self.assertEqual(by_id["chat-104"]["proposed_mutation"], "flag-for-archive-approval")
        self.assertEqual(by_id["chat-105"]["project_action"], "move-existing")
        self.assertTrue(set(fixture["inventory_only_candidates"]).isdisjoint(cohort))


if __name__ == "__main__":
    unittest.main()
