import importlib.util
import io
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sync_codex_global_config.py"
REVIEWED_CHAT_HISTORY_AGENT = (
    SCRIPT.parents[1]
    / "config/codex/global/agents/chat-history-researcher.toml"
)
SPEC = importlib.util.spec_from_file_location("sync_codex_global_config", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load synchronization module from {SCRIPT}")
sync_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sync_module
SPEC.loader.exec_module(sync_module)


class SyncCodexGlobalConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        (self.source / "agents").mkdir(parents=True)
        self.fragment = "## Required\n\nAlways delegate browser work.\n"
        (self.source / "AGENTS.browser-delegation.md").write_text(
            self.fragment, encoding="utf-8"
        )
        (self.source / "agents/chrome-pilot.toml").write_text(
            'name = "chrome_pilot"\n'
            'description = "Browser worker"\n'
            'developer_instructions = "Use Chrome."\n',
            encoding="utf-8",
        )
        self.chat_history_agent = (
            'name = "chat_history_researcher"\n'
            'description = "Chat history worker"\n'
            'model = "gpt-5.6-luna"\n'
            'model_reasoning_effort = "high"\n'
            'service_tier = "fast"\n'
            'developer_instructions = "Analyze bounded history corpora."\n'
        )
        (self.source / "agents/chat-history-researcher.toml").write_text(
            self.chat_history_agent,
            encoding="utf-8",
        )
        self.codex_home = self.root / ".codex"
        self.codex_home.mkdir()
        self.skills_root = self.root / ".agents" / "skills"
        self.chat_history_skill = self._write_installed_skill(self.skills_root)
        self.predecessor_agent = (
            'name = "history_researcher"\n'
            'description = "Predecessor history worker"\n'
            'developer_instructions = "Localize, then analyze."\n'
        )

    def _write_installed_skill(self, skills_root, name="chat-history"):
        skill_file = skills_root / "chat-history" / "SKILL.md"
        skill_file.parent.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(
            "---\n"
            f"name: {name}\n"
            "description: Test fixture for the installed gated router.\n"
            "---\n\n"
            "# Chat History\n",
            encoding="utf-8",
        )
        return skill_file

    def _apply(self):
        changes, conflicts, state = sync_module.plan(self.source, self.codex_home)
        self.assertEqual([], conflicts)
        transaction = sync_module.apply_changes(self.codex_home, changes, state)
        return changes, transaction

    def _state_path(self, codex_home=None):
        home = codex_home or self.codex_home
        return home / sync_module.MANAGEMENT_ROOT / sync_module.STATE_FILE

    def _seed_predecessor(self):
        self._apply()
        new_target = self.codex_home / "agents/chat-history-researcher.toml"
        old_target = self.codex_home / "agents/history-researcher.toml"
        new_target.unlink()
        old_target.write_text(self.predecessor_agent, encoding="utf-8")
        state_path = self._state_path()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["managed"].pop("agents/chat-history-researcher.toml")
        state["managed"]["agents/history-researcher.toml"] = sync_module._digest(
            self.predecessor_agent
        )
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return old_target, new_target, state_path

    def test_reviewed_chat_history_agent_contract(self):
        profile = tomllib.loads(
            REVIEWED_CHAT_HISTORY_AGENT.read_text(encoding="utf-8")
        )

        self.assertEqual("chat_history_researcher", profile["name"])
        self.assertEqual(
            "Fast optional chat-history worker for bounded research across large "
            "conversation corpora or long transcripts.",
            profile["description"],
        )
        self.assertEqual("gpt-5.6-luna", profile["model"])
        self.assertEqual("high", profile["model_reasoning_effort"])
        self.assertEqual("fast", profile["service_tier"])
        self.assertIn("chat-history-researcher.toml", sync_module.AGENT_FILES)
        self.assertNotIn("history-researcher.toml", sync_module.AGENT_FILES)
        instructions = profile["developer_instructions"]
        required_instruction_anchors = (
            "optional delegated chat-history researcher for large conversation corpora",
            "Load and follow the installed chat-history skill",
            "coordinator's question, bounded scope, and requested deliverable",
            "Preserve source identifiers and bounded turn, event, or time references",
            "Distinguish direct records from assistant claims and your own inference",
            "Never mutate source conversations, transcripts, indexes, the project or "
            "repository, or global configuration",
        )
        for anchor in required_instruction_anchors:
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, instructions)

        duplicated_workflow_anchors = (
            "Every assignment must specify LOCALIZE or ANALYZE mode",
            "LOCALIZE mode:",
            "ANALYZE mode:",
            "Kurrent Capacitor",
            "AgentsView",
            "Pieces",
            "exact temporary run directory",
            "Route by the requested field",
            "raw transcripts from the recording harness as authority",
            "Prefer indexed search",
            "ambient working directory",
        )
        for anchor in duplicated_workflow_anchors:
            with self.subTest(anchor=anchor):
                self.assertNotIn(anchor, instructions)

    def test_apply_preserves_unmanaged_prompt_content_and_records_state(self):
        target = self.codex_home / "AGENTS.md"
        target.write_text("# Existing policy\n", encoding="utf-8")

        changes, transaction = self._apply()

        self.assertEqual(3, len(changes))
        self.assertIsNotNone(transaction)
        result = target.read_text(encoding="utf-8")
        self.assertIn("# Existing policy", result)
        self.assertIn(sync_module.START_MARKER, result)
        state = sync_module._load_state(self.codex_home)
        self.assertIn("AGENTS.md#browser-delegation", state["managed"])
        self.assertEqual(
            sync_module._digest(self.chat_history_agent),
            state["managed"]["agents/chat-history-researcher.toml"],
        )
        self.assertEqual(
            self.chat_history_agent,
            (self.codex_home / "agents/chat-history-researcher.toml").read_text(
                encoding="utf-8"
            ),
        )

    def test_apply_adopts_matching_unmarked_fragment_without_duplication(self):
        target = self.codex_home / "AGENTS.md"
        target.write_text(f"# Existing\n\n{self.fragment}", encoding="utf-8")

        self._apply()

        result = target.read_text(encoding="utf-8")
        self.assertEqual(1, result.count("Always delegate browser work."))
        self.assertEqual(1, result.count(sync_module.START_MARKER))

    def test_locally_modified_managed_block_is_a_conflict(self):
        self._apply()
        target = self.codex_home / "AGENTS.md"
        target.write_text(
            target.read_text(encoding="utf-8").replace(
                "Always delegate browser work.", "locally changed"
            ),
            encoding="utf-8",
        )
        self.fragment = "## Required\n\nUpdated reviewed rule.\n"
        (self.source / "AGENTS.browser-delegation.md").write_text(
            self.fragment, encoding="utf-8"
        )

        _changes, conflicts, _state = sync_module.plan(self.source, self.codex_home)

        self.assertEqual(
            ["managed browser-delegation block was modified locally"], conflicts
        )

    def test_unmanaged_different_agent_file_is_a_conflict(self):
        target = self.codex_home / "agents/chrome-pilot.toml"
        target.parent.mkdir()
        target.write_text('name = "somebody_elses_agent"\n', encoding="utf-8")

        _changes, conflicts, _state = sync_module.plan(self.source, self.codex_home)

        self.assertEqual(1, len(conflicts))
        self.assertIn("unmanaged or locally modified agent file", conflicts[0])

    def test_check_plan_does_not_write(self):
        target = self.codex_home / "AGENTS.md"
        target.write_text("unchanged\n", encoding="utf-8")

        changes, conflicts, _state = sync_module.plan(self.source, self.codex_home)

        self.assertEqual([], conflicts)
        self.assertEqual(3, len(changes))
        self.assertEqual("unchanged\n", target.read_text(encoding="utf-8"))

    def test_missing_required_chat_history_skill_blocks_apply_without_mutation(self):
        agents_target = self.codex_home / "AGENTS.md"
        agents_target.write_text("unchanged\n", encoding="utf-8")
        self.chat_history_skill.unlink()
        stderr = io.StringIO()

        with (
            mock.patch("sys.stdout", new=io.StringIO()),
            mock.patch("sys.stderr", new=stderr),
        ):
            result = sync_module.main(
                [
                    "--apply",
                    "--source",
                    str(self.source),
                    "--codex-home",
                    str(self.codex_home),
                ]
            )

        self.assertEqual(2, result)
        self.assertIn("Required installed skill is missing", stderr.getvalue())
        self.assertEqual("unchanged\n", agents_target.read_text(encoding="utf-8"))
        self.assertFalse((self.codex_home / "agents").exists())
        self.assertFalse(self._state_path().exists())

    def test_wrong_installed_chat_history_skill_identity_blocks_apply(self):
        agents_target = self.codex_home / "AGENTS.md"
        agents_target.write_text("unchanged\n", encoding="utf-8")
        self._write_installed_skill(self.skills_root, name="not-chat-history")
        stderr = io.StringIO()

        with (
            mock.patch("sys.stdout", new=io.StringIO()),
            mock.patch("sys.stderr", new=stderr),
        ):
            result = sync_module.main(
                [
                    "--apply",
                    "--source",
                    str(self.source),
                    "--codex-home",
                    str(self.codex_home),
                ]
            )

        self.assertEqual(2, result)
        self.assertIn("Required installed skill has the wrong identity", stderr.getvalue())
        self.assertEqual("unchanged\n", agents_target.read_text(encoding="utf-8"))
        self.assertFalse((self.codex_home / "agents").exists())
        self.assertFalse(self._state_path().exists())

    def test_explicit_valid_agents_skills_root_applies_and_converges(self):
        self.chat_history_skill.unlink()
        alternate_skills_root = self.root / "alternate-agents-skills"
        self._write_installed_skill(alternate_skills_root)
        common = [
            "--source",
            str(self.source),
            "--codex-home",
            str(self.codex_home),
            "--agents-skills-root",
            str(alternate_skills_root),
        ]

        with mock.patch("sys.stdout", new=io.StringIO()):
            apply_result = sync_module.main(["--apply", *common])

        self.assertEqual(0, apply_result)
        installed_agent = self.codex_home / "agents/chat-history-researcher.toml"
        self.assertEqual(
            self.chat_history_agent, installed_agent.read_text(encoding="utf-8")
        )
        state = sync_module._load_state(self.codex_home)
        self.assertEqual(
            sync_module._digest(self.chat_history_agent),
            state["managed"]["agents/chat-history-researcher.toml"],
        )
        with mock.patch("sys.stdout", new=io.StringIO()):
            self.assertEqual(0, sync_module.main(["--check", *common]))

    def test_predecessor_rename_plans_diffs_applies_and_converges(self):
        old_target, new_target, state_path = self._seed_predecessor()
        state_before = state_path.read_text(encoding="utf-8")

        changes, conflicts, _state = sync_module.plan(self.source, self.codex_home)

        self.assertEqual([], conflicts)
        changes_by_key = {change.key: change for change in changes}
        self.assertEqual(
            {
                "agents/chat-history-researcher.toml",
                "agents/history-researcher.toml",
            },
            set(changes_by_key),
        )
        self.assertEqual(
            self.chat_history_agent,
            changes_by_key["agents/chat-history-researcher.toml"].desired,
        )
        self.assertIsNone(
            changes_by_key["agents/history-researcher.toml"].desired
        )

        stdout = io.StringIO()
        with mock.patch("sys.stdout", stdout):
            diff_result = sync_module.main(
                [
                    "--diff",
                    "--source",
                    str(self.source),
                    "--codex-home",
                    str(self.codex_home),
                ]
            )

        self.assertEqual(1, diff_result)
        rendered_diff = stdout.getvalue()
        self.assertIn("live/agents/chat-history-researcher.toml", rendered_diff)
        self.assertIn("reviewed/agents/chat-history-researcher.toml", rendered_diff)
        self.assertIn("live/agents/history-researcher.toml", rendered_diff)
        self.assertIn("reviewed/agents/history-researcher.toml", rendered_diff)
        self.assertIn('+name = "chat_history_researcher"', rendered_diff)
        self.assertIn('-name = "history_researcher"', rendered_diff)
        self.assertEqual(self.predecessor_agent, old_target.read_text(encoding="utf-8"))
        self.assertFalse(new_target.exists())
        self.assertEqual(state_before, state_path.read_text(encoding="utf-8"))

        with mock.patch("sys.stdout", new=io.StringIO()):
            apply_result = sync_module.main(
                [
                    "--apply",
                    "--source",
                    str(self.source),
                    "--codex-home",
                    str(self.codex_home),
                ]
            )

        self.assertEqual(0, apply_result)
        self.assertFalse(old_target.exists())
        self.assertEqual(
            (self.source / "agents/chat-history-researcher.toml").read_text(
                encoding="utf-8"
            ),
            new_target.read_text(encoding="utf-8"),
        )
        applied_state = sync_module._load_state(self.codex_home)
        self.assertNotIn("agents/history-researcher.toml", applied_state["managed"])
        self.assertEqual(
            sync_module._digest(self.chat_history_agent),
            applied_state["managed"]["agents/chat-history-researcher.toml"],
        )
        with mock.patch("sys.stdout", new=io.StringIO()):
            self.assertEqual(
                0,
                sync_module.main(
                    [
                        "--check",
                        "--source",
                        str(self.source),
                        "--codex-home",
                        str(self.codex_home),
                    ]
                ),
            )

    def test_modified_retired_agent_blocks_rename_without_mutation(self):
        old_target, new_target, state_path = self._seed_predecessor()
        local_content = self.predecessor_agent + "# local owner edit\n"
        old_target.write_text(local_content, encoding="utf-8")
        state_before = state_path.read_text(encoding="utf-8")

        _changes, conflicts, _state = sync_module.plan(self.source, self.codex_home)

        self.assertEqual(1, len(conflicts))
        self.assertIn("locally modified retired agent file", conflicts[0])
        with (
            mock.patch("sys.stdout", new=io.StringIO()),
            mock.patch("sys.stderr", new=io.StringIO()),
        ):
            result = sync_module.main(
                [
                    "--apply",
                    "--source",
                    str(self.source),
                    "--codex-home",
                    str(self.codex_home),
                ]
            )

        self.assertEqual(2, result)
        self.assertEqual(local_content, old_target.read_text(encoding="utf-8"))
        self.assertFalse(new_target.exists())
        self.assertEqual(state_before, state_path.read_text(encoding="utf-8"))

    def test_retired_agent_changed_after_plan_is_preserved_and_apply_rolls_back(self):
        old_target, new_target, state_path = self._seed_predecessor()
        state_before = state_path.read_text(encoding="utf-8")
        changes, conflicts, state = sync_module.plan(self.source, self.codex_home)
        self.assertEqual([], conflicts)
        racing_content = self.predecessor_agent + "# raced after plan\n"
        old_target.write_text(racing_content, encoding="utf-8")

        with self.assertRaisesRegex(sync_module.ConfigError, "changed after planning"):
            sync_module.apply_changes(self.codex_home, changes, state)

        self.assertEqual(racing_content, old_target.read_text(encoding="utf-8"))
        self.assertFalse(new_target.exists())
        self.assertEqual(state_before, state_path.read_text(encoding="utf-8"))

    def test_rename_rollback_restores_predecessor_file_and_state(self):
        old_target, new_target, state_path = self._seed_predecessor()
        state_before = state_path.read_text(encoding="utf-8")
        changes, conflicts, state = sync_module.plan(self.source, self.codex_home)
        self.assertEqual([], conflicts)
        transaction = sync_module.apply_changes(self.codex_home, changes, state)
        self.assertIsNotNone(transaction)

        sync_module.rollback(self.codex_home, transaction)

        self.assertEqual(self.predecessor_agent, old_target.read_text(encoding="utf-8"))
        self.assertFalse(new_target.exists())
        self.assertEqual(state_before, state_path.read_text(encoding="utf-8"))

    def test_rename_rollback_refuses_a_recreated_retired_target(self):
        old_target, new_target, state_path = self._seed_predecessor()
        changes, conflicts, state = sync_module.plan(self.source, self.codex_home)
        self.assertEqual([], conflicts)
        transaction = sync_module.apply_changes(self.codex_home, changes, state)
        self.assertIsNotNone(transaction)
        state_after_apply = state_path.read_text(encoding="utf-8")
        recreated_content = "recreated by another owner\n"
        old_target.write_text(recreated_content, encoding="utf-8")

        with self.assertRaisesRegex(
            sync_module.ConfigError, "retired target was recreated"
        ):
            sync_module.rollback(self.codex_home, transaction)

        self.assertEqual(recreated_content, old_target.read_text(encoding="utf-8"))
        self.assertEqual(self.chat_history_agent, new_target.read_text(encoding="utf-8"))
        self.assertEqual(state_after_apply, state_path.read_text(encoding="utf-8"))

    def test_invalid_retired_agent_keys_fail_before_touching_outside_content(self):
        old_target, new_target, state_path = self._seed_predecessor()
        baseline_state = json.loads(state_path.read_text(encoding="utf-8"))
        victim = self.root / "outside-victim.toml"
        victim_content = "outside owner\n"
        victim.write_text(victim_content, encoding="utf-8")
        invalid_keys = (
            str(victim.resolve()),
            "agents/../../outside-victim.toml",
            "agents/nested/retired.toml",
            "agents/retired.txt",
        )

        for key in invalid_keys:
            with self.subTest(key=key):
                state = json.loads(json.dumps(baseline_state))
                state["managed"][key] = sync_module._digest(victim_content)
                state_path.write_text(
                    json.dumps(state, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

                with self.assertRaisesRegex(
                    sync_module.ConfigError, "Invalid retired managed agent key"
                ):
                    sync_module.plan(self.source, self.codex_home)

                self.assertEqual(victim_content, victim.read_text(encoding="utf-8"))
                self.assertEqual(
                    self.predecessor_agent, old_target.read_text(encoding="utf-8")
                )
                self.assertFalse(new_target.exists())

    def test_rollback_restores_shared_file_and_removes_created_agent(self):
        target = self.codex_home / "AGENTS.md"
        target.write_text("original\n", encoding="utf-8")
        _changes, transaction = self._apply()
        self.assertIsNotNone(transaction)

        sync_module.rollback(self.codex_home, transaction)

        self.assertEqual("original\n", target.read_text(encoding="utf-8"))
        self.assertFalse((self.codex_home / "agents/chrome-pilot.toml").exists())
        self.assertFalse(
            (self.codex_home / "agents/chat-history-researcher.toml").exists()
        )
        self.assertFalse(
            (self.codex_home / sync_module.MANAGEMENT_ROOT / sync_module.STATE_FILE).exists()
        )

    def test_rollback_rejects_a_non_current_transaction(self):
        _changes, first = self._apply()
        self.assertIsNotNone(first)
        (self.source / "AGENTS.browser-delegation.md").write_text(
            "## Required\n\nUpdated reviewed rule.\n", encoding="utf-8"
        )
        _changes, second = self._apply()
        self.assertIsNotNone(second)

        with self.assertRaises(sync_module.ConfigError):
            sync_module.rollback(self.codex_home, first)

    def test_rollback_rejects_unrelated_post_apply_edit(self):
        target = self.codex_home / "AGENTS.md"
        target.write_text("original\n", encoding="utf-8")
        _changes, transaction = self._apply()
        target.write_text(target.read_text(encoding="utf-8") + "later\n", encoding="utf-8")

        with self.assertRaises(sync_module.ConfigError):
            sync_module.rollback(self.codex_home, transaction)

        self.assertIn("later", target.read_text(encoding="utf-8"))

    def test_matching_files_without_state_are_not_current(self):
        self._apply()
        state_path = self.codex_home / sync_module.MANAGEMENT_ROOT / sync_module.STATE_FILE
        state_path.unlink()

        self.assertEqual(
            1,
            sync_module.main(
                ["--check", "--source", str(self.source), "--codex-home", str(self.codex_home)]
            ),
        )

    def test_invalid_agent_toml_fails_hard(self):
        (self.source / "agents/chrome-pilot.toml").write_text("name = [\n", encoding="utf-8")
        with self.assertRaises(sync_module.ConfigError):
            sync_module.plan(self.source, self.codex_home)

    def test_agent_toml_requires_codex_agent_fields(self):
        (self.source / "agents/chrome-pilot.toml").write_text(
            'name = "chrome_pilot"\n', encoding="utf-8"
        )
        with self.assertRaises(sync_module.ConfigError):
            sync_module.plan(self.source, self.codex_home)

    def test_malformed_markers_fail_hard(self):
        (self.codex_home / "AGENTS.md").write_text(
            f"{sync_module.START_MARKER}\n", encoding="utf-8"
        )

        with self.assertRaises(sync_module.ConfigError):
            sync_module.plan(self.source, self.codex_home)

    def test_reversed_markers_fail_with_config_error(self):
        (self.codex_home / "AGENTS.md").write_text(
            f"{sync_module.END_MARKER}\n{sync_module.START_MARKER}\n",
            encoding="utf-8",
        )

        with self.assertRaises(sync_module.ConfigError):
            sync_module.plan(self.source, self.codex_home)

    def test_symlinked_agents_file_is_rejected(self):
        real = self.root / "real-agents.md"
        real.write_text("outside\n", encoding="utf-8")
        target = self.codex_home / "AGENTS.md"
        try:
            target.symlink_to(real)
        except OSError:
            self.skipTest("symlink creation is unavailable")

        with self.assertRaises(sync_module.ConfigError):
            sync_module.plan(self.source, self.codex_home)

    def test_symlinked_agents_directory_is_rejected(self):
        real = self.root / "outside-agents"
        real.mkdir()
        target = self.codex_home / "agents"
        try:
            target.symlink_to(real, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation is unavailable")

        with self.assertRaises(sync_module.ConfigError):
            sync_module.plan(self.source, self.codex_home)

    def test_failed_second_target_rolls_back_first_target(self):
        agents_target = self.codex_home / "AGENTS.md"
        agents_target.write_text("original\n", encoding="utf-8")
        changes, conflicts, state = sync_module.plan(self.source, self.codex_home)
        self.assertEqual([], conflicts)
        real_atomic_write = sync_module._atomic_write
        agent_target = self.codex_home / "agents/chrome-pilot.toml"

        def fail_agent_write(path, content):
            if path == agent_target:
                raise OSError("simulated agent write failure")
            return real_atomic_write(path, content)

        with (
            mock.patch.object(sync_module, "_atomic_write", side_effect=fail_agent_write),
            self.assertRaises(sync_module.ConfigError),
        ):
            sync_module.apply_changes(self.codex_home, changes, state)

        self.assertEqual("original\n", agents_target.read_text(encoding="utf-8"))
        self.assertFalse(agent_target.exists())

    def test_concurrent_later_target_is_preserved_during_failure_rollback(self):
        agents_target = self.codex_home / "AGENTS.md"
        agents_target.write_text("original\n", encoding="utf-8")
        changes, conflicts, state = sync_module.plan(self.source, self.codex_home)
        self.assertEqual([], conflicts)
        real_atomic_write = sync_module._atomic_write
        agent_target = self.codex_home / "agents/chrome-pilot.toml"

        def create_concurrent_target(path, content):
            result = real_atomic_write(path, content)
            if path == agents_target:
                agent_target.parent.mkdir(exist_ok=True)
                agent_target.write_text("concurrent owner\n", encoding="utf-8")
            return result

        with (
            mock.patch.object(
                sync_module, "_atomic_write", side_effect=create_concurrent_target
            ),
            self.assertRaises(sync_module.ConfigError),
        ):
            sync_module.apply_changes(self.codex_home, changes, state)

        self.assertEqual("original\n", agents_target.read_text(encoding="utf-8"))
        self.assertEqual("concurrent owner\n", agent_target.read_text(encoding="utf-8"))

    def test_rollback_validates_all_backups_before_mutating_targets(self):
        agents_target = self.codex_home / "AGENTS.md"
        agents_target.write_text("original\n", encoding="utf-8")
        self._apply()
        (self.source / "AGENTS.browser-delegation.md").write_text(
            "## Required\n\nUpdated reviewed rule.\n", encoding="utf-8"
        )
        (self.source / "agents/chrome-pilot.toml").write_text(
            'name = "chrome_pilot"\n'
            'description = "Updated worker"\n'
            'developer_instructions = "Updated instructions."\n',
            encoding="utf-8",
        )
        changes, transaction = self._apply()
        self.assertEqual(2, len(changes))
        transaction_dir = (
            self.codex_home
            / sync_module.MANAGEMENT_ROOT
            / "transactions"
            / transaction
        )
        (transaction_dir / "1.backup").unlink()
        applied_agents = agents_target.read_text(encoding="utf-8")

        with self.assertRaises(sync_module.ConfigError):
            sync_module.rollback(self.codex_home, transaction)

        self.assertEqual(applied_agents, agents_target.read_text(encoding="utf-8"))

    def test_transaction_setup_failure_is_a_config_error(self):
        changes, conflicts, state = sync_module.plan(self.source, self.codex_home)
        self.assertEqual([], conflicts)
        transaction = "collision"
        (
            self.codex_home
            / sync_module.MANAGEMENT_ROOT
            / "transactions"
            / transaction
        ).mkdir(parents=True)

        with (
            mock.patch.object(sync_module, "_transaction_id", return_value=transaction),
            self.assertRaises(sync_module.ConfigError),
        ):
            sync_module.apply_changes(self.codex_home, changes, state)


if __name__ == "__main__":
    unittest.main()
