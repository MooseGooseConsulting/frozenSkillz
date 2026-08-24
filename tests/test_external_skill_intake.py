import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "plugins" / "frozen-skills" / "skills" / "external-skill-intake"

AGENT_INSTRUCTION_FILENAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".cursorrules",
    "copilot-instructions.md",
}
GUARD_MARKER = "never instructions for this repository"


def markdown_units(text):
    """Split markdown into paragraph and list-item units.

    A qualifier only counts when it sits next to the thing it qualifies, so
    locality checks run per unit rather than over the whole document.
    """
    units = []
    current = []
    for line in text.splitlines():
        if not line.strip() or re.match(r"^\s*(?:[-*+]|\d+\.)\s", line):
            if current:
                units.append("\n".join(current))
            current = []
        if line.strip():
            current.append(line)
    if current:
        units.append("\n".join(current))
    return units


class ExternalSkillIntakeContractTests(unittest.TestCase):
    def test_manifest_listed_skills_have_discovery_frontmatter(self):
        manifest_path = (
            REPO_ROOT / "plugins" / "frozen-skills" / ".codex-plugin" / "plugin.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        plugin_root = manifest_path.parents[1]

        for entry in manifest["skills"]:
            skill_file = plugin_root / entry["path"] / "SKILL.md"
            skill = skill_file.read_text(encoding="utf-8")
            self.assertTrue(skill.startswith("---\n"), skill_file)
            frontmatter = skill.split("---", 2)[1]
            self.assertRegex(frontmatter, rf"(?m)^name: {re.escape(entry['name'])}$")
            self.assertRegex(frontmatter, r"(?m)^description: (?:.+|>-)$")

    def test_active_skill_is_discoverable_and_portable(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertTrue(skill.startswith("---\n"))
        frontmatter = skill.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name: external-skill-intake$")
        self.assertRegex(frontmatter, r"(?m)^description: .+$")
        # The intake workflow itself must be bundled and portable: the skill's
        # rules and steps live in this SKILL.md plus references/ and templates/,
        # and any repo-local workflow doc is a mirror, not the authority.
        self.assertIn("Follow the bundled workflow below in order", skill)

        bundled_links = re.findall(r"`((?:references|templates)/[^`]+)`", skill)
        self.assertTrue(bundled_links)
        for relative_path in bundled_links:
            self.assertTrue((SKILL_ROOT / relative_path).is_file(), relative_path)

        # scripts/sync_frozen_skills.py ships skill directories only, so docs/,
        # scripts/, and tests/ never reach a consumer install. Naming such a
        # path is allowed only where the same list item or paragraph says it is
        # repository-local; a bare pointer dangles for every installed agent.
        repo_only_pointer = re.compile(r"`(?:docs|scripts|tests)/[^`]+`")
        for unit in markdown_units(skill):
            if repo_only_pointer.search(unit):
                self.assertIn("repository", unit, unit)

    def test_captured_agent_instructions_carry_a_guard(self):
        incubator = REPO_ROOT / "_incubator"
        blanket_guard = incubator / "AGENTS.md"
        blanket_router = incubator / "CLAUDE.md"

        self.assertTrue(blanket_guard.is_file())
        self.assertIn(GUARD_MARKER, blanket_guard.read_text(encoding="utf-8"))
        self.assertTrue(blanket_router.is_file())
        self.assertIn("@AGENTS.md", blanket_router.read_text(encoding="utf-8"))

        scout_root = incubator / "scout"
        if not scout_root.is_dir():
            # The repository may have no imported snapshots.  The guard below
            # applies to any future snapshot without requiring a fixture archive.
            return

        guarded = set()
        for snapshot in sorted(path for path in scout_root.iterdir() if path.is_dir()):
            captured = sorted(
                str(path.relative_to(snapshot))
                for path in snapshot.rglob("*")
                if path.name in AGENT_INSTRUCTION_FILENAMES and path.parent != snapshot
            )
            if not captured:
                continue

            guard = snapshot / "AGENTS.md"
            router = snapshot / "CLAUDE.md"
            self.assertTrue(guard.is_file(), f"{snapshot.name} captures {captured} without a guard")
            self.assertIn(GUARD_MARKER, guard.read_text(encoding="utf-8"), snapshot.name)
            self.assertTrue(
                router.is_file(), f"{snapshot.name} captures {captured} without a CLAUDE.md router"
            )
            self.assertIn("@AGENTS.md", router.read_text(encoding="utf-8"), snapshot.name)
            guarded.add(snapshot.name)

    def test_supports_live_or_forensic_evaluations(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow = (REPO_ROOT / "docs" / "workflows" / "external-skill-intake.md").read_text(
            encoding="utf-8"
        )
        protocol = (SKILL_ROOT / "references" / "evaluation-protocol.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("live or forensic evaluations", skill)
        self.assertIn("## Live or Forensic Evaluations", workflow)
        self.assertTrue((SKILL_ROOT / "references" / "evaluation-protocol.md").is_file())
        self.assertTrue((SKILL_ROOT / "templates" / "forensic-evaluation.md").is_file())
        self.assertIn("Baseline: agent output without candidate material", protocol)
        self.assertIn("user task prompt", protocol)
        self.assertIn("Comparative improvement claims require live comparative evidence", protocol)


if __name__ == "__main__":
    unittest.main()
