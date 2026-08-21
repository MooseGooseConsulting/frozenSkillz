import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sync_frozen_skills.py"
SPEC = importlib.util.spec_from_file_location("sync_frozen_skills", SCRIPT)
sync_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = sync_module
SPEC.loader.exec_module(sync_module)


class SyncFrozenSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.destination = self.root / "skills"
        self.plugin = self.repo / "plugins/frozen-skills"
        self._write_skill("alpha", "alpha v1")
        self._write_manifests({consumer: ["alpha"] for consumer in sync_module.MANIFEST_PATHS})

    def tearDown(self):
        self.temporary.cleanup()

    def _write_skill(self, name, body):
        skill = self.plugin / "skills" / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(body, encoding="utf-8")

    def _write_manifests(self, skills_by_consumer, *, version="1.0.0"):
        shared_names = set.intersection(
            *(set(names) for names in skills_by_consumer.values())
        )
        for consumer, relative in sync_module.MANIFEST_PATHS.items():
            data = {
                "name": "frozen-skills",
                "version": version,
                "description": "test",
                "skills": [
                    {"name": name, "path": f"skills/{name}"}
                    for name in sorted(shared_names)
                ],
            }
            path = self.plugin / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data), encoding="utf-8")

        consumer_packages = {}
        consumer_skills = {}
        for consumer, names in skills_by_consumer.items():
            restricted_names = sorted(set(names) - shared_names)
            package = f"test-{consumer}"
            consumer_packages[consumer] = [package] if restricted_names else []
            consumer_skills[consumer] = [
                {
                    "name": name,
                    "path": f"{package}/skills/{name}",
                }
                for name in restricted_names
            ]
            for name in restricted_names:
                source = self.plugin / "skills" / name
                if source.is_dir():
                    shutil.copytree(
                        source,
                        self.repo / "plugins" / package / "skills" / name,
                        dirs_exist_ok=True,
                    )

        distribution = {
            "schema": 1,
            "plugin": "frozen-skills",
            "version": version,
            "shared": [
                {"name": name, "path": f"frozen-skills/skills/{name}"}
                for name in sorted(shared_names)
            ],
            "consumer_packages": consumer_packages,
            "consumers": consumer_skills,
        }
        (self.repo / "plugins" / sync_module.DISTRIBUTION_PATH).write_text(
            json.dumps(distribution), encoding="utf-8"
        )

    def _write_deployment(
        self,
        name,
        skills,
        *,
        consumer="codex",
        description="test deployment subset",
    ):
        path = self.repo / "plugins" / sync_module.DISTRIBUTION_PATH
        distribution = json.loads(path.read_text(encoding="utf-8"))
        entry = {"description": description, "skills": skills}
        if consumer is not None:
            entry["consumer"] = consumer
        distribution.setdefault("deployments", {})[name] = entry
        path.write_text(json.dumps(distribution), encoding="utf-8")

    def _sync(
        self,
        *,
        consumer="codex",
        apply=False,
        prune=False,
        force=False,
        deployment=None,
        destination=None,
        repo=None,
    ):
        if repo is not None:
            consumer = None
        return sync_module.sync(
            self.repo,
            destination or self.destination,
            consumer=consumer,
            apply=apply,
            prune=prune,
            force=force,
            deployment=deployment,
            repo=repo,
        )

    def test_fresh_install_then_check_is_current(self):
        planned = self._sync()
        self.assertEqual([action.kind for action in planned.actions], ["install"])

        applied = self._sync(apply=True)
        self.assertFalse(applied.conflicts)
        self.assertEqual(
            (self.destination / "alpha/SKILL.md").read_text(encoding="utf-8"),
            "alpha v1",
        )
        self.assertTrue((self.destination / sync_module.STATE_FILE).is_file())

        checked = self._sync()
        self.assertEqual([action.kind for action in checked.actions], ["current"])
        self.assertFalse(checked.changes)

    def test_managed_copy_updates_when_source_changes(self):
        self._sync(apply=True)
        self._write_skill("alpha", "alpha v2")

        planned = self._sync()
        self.assertEqual([action.kind for action in planned.actions], ["update"])
        self._sync(apply=True)
        self.assertEqual(
            (self.destination / "alpha/SKILL.md").read_text(encoding="utf-8"),
            "alpha v2",
        )

    def test_local_modification_is_a_conflict_unless_forced(self):
        self._sync(apply=True)
        (self.destination / "alpha/SKILL.md").write_text("local edit", encoding="utf-8")

        refused = self._sync(apply=True)
        self.assertEqual([action.kind for action in refused.actions], ["conflict"])
        self.assertEqual(
            (self.destination / "alpha/SKILL.md").read_text(encoding="utf-8"),
            "local edit",
        )

        forced = self._sync(apply=True, force=True)
        self.assertEqual([action.kind for action in forced.actions], ["update"])
        self.assertEqual(
            (self.destination / "alpha/SKILL.md").read_text(encoding="utf-8"),
            "alpha v1",
        )

    def test_unmanaged_matching_copy_is_adopted(self):
        self.destination.mkdir(parents=True)
        target = self.destination / "alpha"
        target.mkdir()
        (target / "SKILL.md").write_text("alpha v1", encoding="utf-8")

        result = self._sync(apply=True)
        self.assertEqual([action.kind for action in result.actions], ["adopt"])
        state = json.loads(
            (self.destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
        )
        self.assertIn("alpha", state["skills"])

    def test_prune_only_removes_unchanged_managed_skills(self):
        self._write_skill("beta", "beta v1")
        self._write_manifests(
            {consumer: ["alpha", "beta"] for consumer in sync_module.MANIFEST_PATHS}
        )
        self._sync(apply=True)

        self._write_manifests(
            {consumer: ["alpha"] for consumer in sync_module.MANIFEST_PATHS}
        )
        without_prune = self._sync(apply=True)
        self.assertTrue((self.destination / "beta").is_dir())
        self.assertNotIn("remove", [action.kind for action in without_prune.actions])

        with_prune = self._sync(apply=True, prune=True)
        self.assertIn("remove", [action.kind for action in with_prune.actions])
        self.assertFalse((self.destination / "beta").exists())

    def test_consumer_specific_distributions_are_selected_independently(self):
        self._write_skill("different", "different")
        self._write_manifests(
            {
                "claude": ["alpha"],
                "codex": ["alpha"],
                "cursor": ["different"],
                "gemini": ["alpha"],
            }
        )

        codex = self._sync(consumer="codex")
        cursor = self._sync(consumer="cursor")

        self.assertEqual([action.name for action in codex.actions], ["alpha"])
        self.assertEqual([action.name for action in cursor.actions], ["different"])

    def test_unselected_consumer_distribution_still_requires_valid_skill_paths(self):
        self._write_manifests(
            {
                "claude": ["missing"],
                "codex": ["alpha"],
                "cursor": ["alpha"],
                "gemini": ["alpha"],
            }
        )

        with self.assertRaisesRegex(sync_module.SyncError, "missing"):
            self._sync(consumer="codex")

    def test_invalid_consumer_packages_error_describes_the_full_contract(self):
        distribution_path = self.repo / "plugins" / sync_module.DISTRIBUTION_PATH
        distribution = json.loads(distribution_path.read_text(encoding="utf-8"))
        distribution["consumer_packages"]["codex"] = ["../unsafe"]
        distribution_path.write_text(json.dumps(distribution), encoding="utf-8")

        with self.assertRaisesRegex(
            sync_module.SyncError,
            "unique safe package-name lists",
        ):
            self._sync(consumer="codex")

    def test_consumer_packages_cannot_claim_the_shared_package(self):
        distribution_path = self.repo / "plugins" / sync_module.DISTRIBUTION_PATH
        distribution = json.loads(distribution_path.read_text(encoding="utf-8"))
        distribution["consumer_packages"]["codex"] = ["frozen-skills"]
        distribution_path.write_text(json.dumps(distribution), encoding="utf-8")

        with self.assertRaisesRegex(sync_module.SyncError, "reserved for shared skills"):
            self._sync(consumer="codex")

    def test_distribution_escape_names_the_plugins_source_boundary(self):
        source_root = self.repo / "plugins"
        with self.assertRaisesRegex(
            sync_module.SyncError,
            "escapes plugins source root",
        ):
            sync_module._resolve_distribution_skill(
                source_root,
                "outside",
                "../outside",
            )

    def test_cli_exit_codes_distinguish_drift_current_and_conflict(self):
        common = [
            "--consumer",
            "codex",
            "--repo-root",
            str(self.repo),
            "--destination",
            str(self.destination),
        ]
        self.assertEqual(sync_module.main(["--check", *common]), 1)
        self.assertEqual(sync_module.main(["--apply", *common]), 0)
        self.assertEqual(sync_module.main(["--check", *common]), 0)

        (self.destination / "alpha/SKILL.md").write_text("local edit", encoding="utf-8")
        self.assertEqual(sync_module.main(["--check", *common]), 2)

    def test_unsafe_managed_skill_name_is_rejected(self):
        self.destination.mkdir(parents=True)
        state = {
            "schema": sync_module.STATE_SCHEMA,
            "plugin": "frozen-skills",
            "consumer": "codex",
            "skills": {"../outside": {"digest": "0" * 64}},
        }
        (self.destination / sync_module.STATE_FILE).write_text(
            json.dumps(state), encoding="utf-8"
        )
        with self.assertRaises(sync_module.SyncError):
            self._sync(prune=True)

    def test_digest_frames_each_file_content(self):
        first = self.root / "first"
        second = self.root / "second"
        first.mkdir()
        second.mkdir()
        (first / "SKILL.md").write_bytes(b"common")
        (second / "SKILL.md").write_bytes(b"common")
        (first / "a").write_bytes((1).to_bytes(8, "big") + b"b" + b"payload")
        (second / "a").write_bytes(b"")
        (second / "b").write_bytes(b"payload")

        self.assertNotEqual(
            sync_module.digest_directory(first),
            sync_module.digest_directory(second),
        )

    def test_target_change_after_plan_is_not_overwritten(self):
        original_target_digest = sync_module._target_digest
        target_calls = 0

        def racing_target_digest(target):
            nonlocal target_calls
            if target.name == "alpha":
                target_calls += 1
                if target_calls == 1:
                    return None
                if target_calls == 2:
                    target.mkdir(parents=True)
                    (target / "SKILL.md").write_text("racing local edit", encoding="utf-8")
            return original_target_digest(target)

        with mock.patch.object(
            sync_module, "_target_digest", side_effect=racing_target_digest
        ):
            result = self._sync(apply=True)

        self.assertTrue(result.conflicts)
        self.assertEqual(
            (self.destination / "alpha/SKILL.md").read_text(encoding="utf-8"),
            "racing local edit",
        )
        self.assertFalse((self.destination / sync_module.STATE_FILE).exists())

    def test_failed_rollback_preserves_the_original_backup(self):
        source = self.root / "replacement"
        target = self.root / "managed"
        source.mkdir()
        target.mkdir()
        (source / "SKILL.md").write_text("new", encoding="utf-8")
        (target / "SKILL.md").write_text("original", encoding="utf-8")
        real_replace = sync_module.os.replace
        replace_calls = 0

        def failing_replace(source_path, target_path):
            nonlocal replace_calls
            replace_calls += 1
            if replace_calls == 1:
                return real_replace(source_path, target_path)
            if replace_calls == 3:
                competing_target = Path(target_path)
                competing_target.mkdir(parents=True)
                (competing_target / "SKILL.md").write_text(
                    "competing edit", encoding="utf-8"
                )
            raise OSError("simulated replace failure")

        with mock.patch.object(sync_module.os, "replace", side_effect=failing_replace):
            with self.assertRaises(sync_module.SyncError):
                sync_module._replace_directory(
                    source,
                    target,
                    sync_module.digest_directory(source),
                    sync_module.digest_directory(target),
                )

        backups = list(self.root.glob(".managed.frozen-skills-backup-*"))
        self.assertEqual(
            (target / "SKILL.md").read_text(encoding="utf-8"), "competing edit"
        )
        self.assertEqual(len(backups), 1)
        self.assertEqual(
            (backups[0] / "SKILL.md").read_text(encoding="utf-8"), "original"
        )

    def test_plugin_version_drift_requires_state_refresh(self):
        self._sync(apply=True)
        self._write_manifests(
            {consumer: ["alpha"] for consumer in sync_module.MANIFEST_PATHS},
            version="2.0.0",
        )

        checked = self._sync()
        self.assertIn("state", [action.kind for action in checked.actions])
        self.assertTrue(checked.changes)

        self._sync(apply=True)
        state = json.loads(
            (self.destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
        )
        self.assertEqual(state["plugin_version"], "2.0.0")

    def test_destination_must_be_disjoint_from_repository(self):
        with self.assertRaises(sync_module.SyncError):
            sync_module.sync(
                self.repo,
                self.repo / "runtime-skills",
                consumer="codex",
                apply=False,
                prune=False,
                force=False,
            )
        with self.assertRaises(sync_module.SyncError):
            sync_module.sync(
                self.repo,
                self.root,
                consumer="codex",
                apply=False,
                prune=False,
                force=False,
            )

    def test_source_change_during_staging_leaves_target_untouched(self):
        source = self.root / "changing-source"
        target = self.root / "untouched-target"
        source.mkdir()
        target.mkdir()
        (source / "SKILL.md").write_text("changed", encoding="utf-8")
        (target / "SKILL.md").write_text("original", encoding="utf-8")

        with self.assertRaises(sync_module.SyncError):
            sync_module._replace_directory(
                source,
                target,
                "0" * 64,
                sync_module.digest_directory(target),
            )

        self.assertEqual(
            (target / "SKILL.md").read_text(encoding="utf-8"), "original"
        )

    def test_target_created_during_staging_is_not_overwritten(self):
        original_copytree = sync_module.shutil.copytree

        def racing_copytree(source, staged, **kwargs):
            result = original_copytree(source, staged, **kwargs)
            target = self.destination / "alpha"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("late local edit", encoding="utf-8")
            return result

        with mock.patch.object(
            sync_module.shutil, "copytree", side_effect=racing_copytree
        ):
            result = self._sync(apply=True)

        self.assertTrue(result.conflicts)
        self.assertEqual(
            (self.destination / "alpha/SKILL.md").read_text(encoding="utf-8"),
            "late local edit",
        )

    def test_destination_skill_link_is_rejected(self):
        self.destination.mkdir(parents=True)
        target = self.destination / "alpha"
        missing = self.root / "missing-skill"
        try:
            target.symlink_to(missing, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symbolic links unavailable: {exc}")

        with self.assertRaises(sync_module.SyncError):
            self._sync()

    def test_state_is_bound_to_one_consumer(self):
        self._sync(consumer="codex", apply=True)
        state = json.loads(
            (self.destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
        )
        self.assertEqual(state["consumer"], "codex")

        with self.assertRaisesRegex(sync_module.SyncError, "managed for consumer 'codex'"):
            self._sync(consumer="claude")

    def test_cli_requires_a_consumer_or_a_deployment(self):
        self.assertEqual(
            sync_module.main(
                [
                    "--check",
                    "--repo-root",
                    str(self.repo),
                    "--destination",
                    str(self.destination),
                ]
            ),
            2,
        )

    def test_codex_has_private_default_and_other_consumers_require_destination(self):
        self.assertEqual(
            sync_module.resolve_destination("codex", None),
            sync_module._expanded_path("~/.codex/skills"),
        )
        with self.assertRaisesRegex(sync_module.SyncError, "--destination is required"):
            sync_module.resolve_destination("claude", None)

        explicit = self.root / "claude-skills"
        self.assertEqual(
            sync_module.resolve_destination("claude", explicit),
            explicit,
        )

    def test_deployment_installs_only_its_selected_skills(self):
        self._write_skill("beta", "beta v1")
        self._write_manifests(
            {consumer: ["alpha", "beta"] for consumer in sync_module.MANIFEST_PATHS}
        )
        self._write_deployment("hermes-ops", ["beta"])

        result = self._sync(
            consumer=None, apply=True, prune=True, deployment="hermes-ops"
        )

        self.assertFalse(result.conflicts)
        self.assertFalse((self.destination / "alpha").exists())
        self.assertTrue((self.destination / "beta/SKILL.md").is_file())
        state = json.loads(
            (self.destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
        )
        self.assertEqual(state["deployment"], "hermes-ops")
        self.assertEqual(state["consumer"], "codex")
        self.assertEqual(set(state["skills"]), {"beta"})

    def test_deployment_supplies_its_own_consumer(self):
        self._write_skill("only-cursor", "only cursor")
        self._write_manifests(
            {
                "claude": ["alpha"],
                "codex": ["alpha"],
                "cursor": ["alpha", "only-cursor"],
                "gemini": ["alpha"],
            }
        )
        self._write_deployment("cursor-ops", ["only-cursor"], consumer="cursor")

        result = self._sync(
            consumer=None, apply=True, prune=True, deployment="cursor-ops"
        )

        self.assertFalse(result.conflicts)
        self.assertTrue((self.destination / "only-cursor/SKILL.md").is_file())
        state = json.loads(
            (self.destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
        )
        self.assertEqual(state["consumer"], "cursor")

    def test_deployment_rejects_an_inconsistent_explicit_consumer(self):
        self._write_deployment("hermes-ops", ["alpha"], consumer="codex")

        with self.assertRaisesRegex(
            sync_module.SyncError, "already selects its own consumer"
        ):
            self._sync(consumer="claude", prune=True, deployment="hermes-ops")

        self.assertFalse(
            self._sync(
                consumer="codex", prune=True, deployment="hermes-ops"
            ).conflicts
        )

    def test_deployment_cannot_select_a_skill_the_consumer_lacks(self):
        self._write_skill("only-cursor", "only cursor")
        self._write_manifests(
            {
                "claude": ["alpha"],
                "codex": ["alpha"],
                "cursor": ["alpha", "only-cursor"],
                "gemini": ["alpha"],
            }
        )
        self._write_deployment("hermes-ops", ["only-cursor"], consumer="codex")

        with self.assertRaisesRegex(
            sync_module.SyncError, "is not active for consumer 'codex'"
        ):
            self._sync(consumer=None, prune=True, deployment="hermes-ops")

    def test_runtime_deployment_without_a_consumer_installs_shared_skills(self):
        self._write_skill("beta", "beta v1")
        self._write_manifests(
            {consumer: ["alpha", "beta"] for consumer in sync_module.MANIFEST_PATHS}
        )
        self._write_deployment("hermes-ops", ["alpha", "beta"], consumer=None)

        result = self._sync(
            consumer=None, apply=True, prune=True, deployment="hermes-ops"
        )

        self.assertFalse(result.conflicts)
        self.assertTrue((self.destination / "alpha/SKILL.md").is_file())
        self.assertTrue((self.destination / "beta/SKILL.md").is_file())
        state = json.loads(
            (self.destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
        )
        self.assertNotIn("consumer", state)
        self.assertEqual(state["deployment"], "hermes-ops")

        checked = self._sync(consumer=None, prune=True, deployment="hermes-ops")
        self.assertEqual([action.kind for action in checked.actions], ["current"] * 2)

    def test_runtime_deployment_cannot_select_a_restricted_package(self):
        self._write_skill("only-codex", "only codex")
        self._write_manifests(
            {
                "claude": ["alpha"],
                "codex": ["alpha", "only-codex"],
                "cursor": ["alpha"],
                "gemini": ["alpha"],
            }
        )
        self._write_deployment("hermes-ops", ["alpha", "only-codex"], consumer=None)

        with self.assertRaisesRegex(
            sync_module.SyncError,
            "declares no consumer, so it may only select shared skills",
        ):
            self._sync(consumer=None, prune=True, deployment="hermes-ops")

    def test_runtime_deployment_refuses_an_explicit_consumer(self):
        self._write_deployment("hermes-ops", ["alpha"], consumer=None)

        with self.assertRaisesRegex(
            sync_module.SyncError, "declares no consumer because it is not a client"
        ):
            self._sync(consumer="codex", prune=True, deployment="hermes-ops")

    def test_runtime_and_client_deployment_states_are_distinguishable(self):
        self._write_deployment("hermes-ops", ["alpha"], consumer=None)
        self._sync(consumer=None, apply=True, prune=True, deployment="hermes-ops")

        self._write_deployment("hermes-ops", ["alpha"], consumer="codex")
        with self.assertRaisesRegex(
            sync_module.SyncError, "managed for consumer None, not 'codex'"
        ):
            self._sync(consumer=None, prune=True, deployment="hermes-ops")

    def test_file_destination_is_a_clean_error_not_a_traceback(self):
        self._write_deployment("hermes-ops", ["alpha"], consumer=None)
        destination = self.root / "not-a-directory"
        destination.write_text("i am a file", encoding="utf-8")

        for deployment in ("hermes-ops", None):
            with self.subTest(deployment=deployment):
                with self.assertRaisesRegex(
                    sync_module.SyncError, "Destination must be a directory"
                ):
                    self._sync(
                        consumer=None if deployment else "codex",
                        prune=True,
                        deployment=deployment,
                        destination=destination,
                    )

    def test_deployment_rejects_unpromoted_and_duplicate_skills(self):
        self._write_deployment("subset", ["alpha", "not-active"])
        with self.assertRaisesRegex(sync_module.SyncError, "is not active for consumer"):
            self._sync(consumer=None, prune=True, deployment="subset")

        self._write_deployment("subset", ["alpha", "alpha"])
        with self.assertRaisesRegex(sync_module.SyncError, "duplicate skill"):
            self._sync(consumer=None, prune=True, deployment="subset")

    def test_deployment_entry_shape_is_validated(self):
        self._write_deployment("subset", ["alpha"], description="  ")
        with self.assertRaisesRegex(sync_module.SyncError, "has no description"):
            self._sync(consumer=None, prune=True, deployment="subset")

        self._write_deployment("subset", ["alpha"], consumer="not-a-client")
        with self.assertRaisesRegex(sync_module.SyncError, "must name one consumer"):
            self._sync(consumer=None, prune=True, deployment="subset")

        self._write_deployment("subset", [])
        with self.assertRaisesRegex(sync_module.SyncError, "has no skills"):
            self._sync(consumer=None, prune=True, deployment="subset")

    def test_unsafe_or_unknown_deployment_names_are_rejected(self):
        with self.assertRaisesRegex(sync_module.SyncError, "Unknown deployment"):
            self._sync(consumer=None, prune=True, deployment="missing")

        self._write_deployment("../outside", ["alpha"])
        with self.assertRaisesRegex(sync_module.SyncError, "Unsafe deployment name"):
            self._sync(consumer=None, prune=True, deployment="../outside")

    def test_malformed_deployments_block_fails_an_ordinary_consumer_sync(self):
        path = self.repo / "plugins" / sync_module.DISTRIBUTION_PATH
        distribution = json.loads(path.read_text(encoding="utf-8"))
        distribution["deployments"] = {"broken": {"consumer": "codex"}}
        path.write_text(json.dumps(distribution), encoding="utf-8")

        with self.assertRaisesRegex(sync_module.SyncError, "has no description"):
            self._sync(consumer="codex")

    def test_managed_destination_refuses_a_different_deployment(self):
        self._write_deployment("first", ["alpha"])
        self._write_deployment("second", ["alpha"])
        self._sync(consumer=None, apply=True, prune=True, deployment="first")

        with self.assertRaisesRegex(
            sync_module.SyncError, "managed by deployment 'first'"
        ):
            self._sync(consumer=None, prune=True, deployment="second")

    def test_deployment_requires_prune_for_check_and_apply(self):
        self._write_skill("beta", "beta v1")
        self._write_manifests(
            {consumer: ["alpha", "beta"] for consumer in sync_module.MANIFEST_PATHS}
        )
        self._write_deployment("hermes-ops", ["alpha", "beta"])
        self._sync(consumer=None, apply=True, prune=True, deployment="hermes-ops")
        self._write_deployment("hermes-ops", ["alpha"])

        for apply in (False, True):
            with self.subTest(apply=apply):
                with self.assertRaisesRegex(sync_module.SyncError, "requires --prune"):
                    self._sync(consumer=None, apply=apply, deployment="hermes-ops")

        self.assertTrue((self.destination / "beta").is_dir())

    def test_deployment_prune_preserves_modified_retired_skill_as_conflict(self):
        self._write_skill("beta", "beta v1")
        self._write_manifests(
            {consumer: ["alpha", "beta"] for consumer in sync_module.MANIFEST_PATHS}
        )
        self._write_deployment("hermes-ops", ["alpha", "beta"])
        self._sync(consumer=None, apply=True, prune=True, deployment="hermes-ops")
        (self.destination / "beta/SKILL.md").write_text(
            "local beta edit", encoding="utf-8"
        )
        self._write_deployment("hermes-ops", ["alpha"])

        result = self._sync(
            consumer=None, apply=True, prune=True, deployment="hermes-ops"
        )

        self.assertEqual(
            [action.kind for action in result.actions], ["current", "conflict"]
        )
        self.assertEqual(
            (self.destination / "beta/SKILL.md").read_text(encoding="utf-8"),
            "local beta edit",
        )

    def test_empty_deployment_state_refuses_a_different_deployment(self):
        self._write_deployment("first", ["alpha"])
        self._write_deployment("second", ["alpha"])
        self.destination.mkdir(parents=True)
        (self.destination / sync_module.STATE_FILE).write_text(
            json.dumps(
                {
                    "schema": sync_module.STATE_SCHEMA,
                    "plugin": "frozen-skills",
                    "consumer": "codex",
                    "plugin_version": "1.0.0",
                    "deployment": "first",
                    "skills": {},
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaises(sync_module.SyncError):
            self._sync(consumer=None, prune=True, deployment="second")

    def test_full_and_deployment_destinations_cannot_be_reused(self):
        self._write_deployment("hermes-ops", ["alpha"])
        self._sync(apply=True)

        with self.assertRaisesRegex(
            sync_module.SyncError, "managed by the full consumer distribution"
        ):
            self._sync(consumer=None, prune=True, deployment="hermes-ops")

        deployment_destination = self.root / "deployment-skills"
        self._sync(
            consumer=None,
            apply=True,
            prune=True,
            deployment="hermes-ops",
            destination=deployment_destination,
        )
        with self.assertRaisesRegex(
            sync_module.SyncError, "managed by deployment 'hermes-ops'"
        ):
            self._sync(destination=deployment_destination)

    def test_deployment_reports_unmanaged_destination_content(self):
        self._write_skill("beta", "beta v1")
        self._write_manifests(
            {consumer: ["alpha", "beta"] for consumer in sync_module.MANIFEST_PATHS}
        )
        self._write_deployment("hermes-ops", ["alpha", "beta"])
        self._sync(consumer=None, apply=True, prune=True, deployment="hermes-ops")
        unrelated = self.destination / "local-hermes-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("local", encoding="utf-8")

        self._write_deployment("hermes-ops", ["alpha"])
        result = self._sync(
            consumer=None,
            apply=True,
            prune=True,
            force=True,
            deployment="hermes-ops",
        )

        self.assertEqual(
            [action.kind for action in result.actions],
            ["current", "remove", "conflict"],
        )
        self.assertTrue((self.destination / "beta").is_dir())
        self.assertTrue(unrelated.is_dir())

    def test_deployment_cli_requires_explicit_destination_and_prune(self):
        self._write_deployment("hermes-ops", ["alpha"])
        self.assertEqual(
            sync_module.main(
                ["--check", "--repo-root", str(self.repo), "--deployment", "hermes-ops"]
            ),
            2,
        )
        self.assertEqual(
            sync_module.main(
                [
                    "--check",
                    "--repo-root",
                    str(self.repo),
                    "--destination",
                    str(self.destination),
                    "--deployment",
                    "hermes-ops",
                ]
            ),
            2,
        )

    def test_deployment_cli_exit_codes_distinguish_drift_and_current(self):
        self._write_deployment("hermes-ops", ["alpha"])
        common = [
            "--repo-root",
            str(self.repo),
            "--destination",
            str(self.destination),
            "--deployment",
            "hermes-ops",
            "--prune",
        ]
        self.assertEqual(sync_module.main(["--check", *common]), 1)
        self.assertEqual(sync_module.main(["--apply", *common]), 0)
        self.assertEqual(sync_module.main(["--check", *common]), 0)

    def _write_repo_targets(self, targets):
        path = self.repo / "plugins" / sync_module.DISTRIBUTION_PATH
        distribution = json.loads(path.read_text(encoding="utf-8"))
        distribution["repo_targets"] = targets
        path.write_text(json.dumps(distribution), encoding="utf-8")

    def _write_repo_only_skill(self, package, name, body):
        skill = self.repo / "plugins" / package / "skills" / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(body, encoding="utf-8")

    def _write_mcp_template(self, name, server):
        template_dir = self.repo / sync_module.MCP_TEMPLATES_ROOT
        template_dir.mkdir(parents=True, exist_ok=True)
        (template_dir / f"{name}.json").write_text(
            json.dumps({"mcpServers": {name: server}}), encoding="utf-8"
        )

    def test_repo_sync_installs_repo_only_skill_and_mcp_artifact(self):
        self._write_repo_only_skill("beta-ops", "beta", "beta v1")
        self._write_mcp_template("beta", {"command": "npx", "args": ["-y", "beta-mcp"]})
        self._write_repo_targets(
            {
                "beta": {
                    "description": "repo-only skill with an MCP template",
                    "path": "beta-ops/skills/beta",
                    "repos": ["owner/project"],
                    "mcp": ["beta"],
                }
            }
        )
        result = self._sync(repo="owner/project", apply=True)
        self.assertFalse(result.conflicts)
        self.assertTrue((self.destination / "beta" / "SKILL.md").is_file())

        artifact = self.destination / sync_module.MCP_ARTIFACT_NAME
        document = json.loads(artifact.read_text(encoding="utf-8"))
        self.assertEqual(
            document["mcpServers"]["beta"]["args"], ["-y", "beta-mcp"]
        )

        state = json.loads(
            (self.destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
        )
        self.assertEqual(state["repo"], "owner/project")
        self.assertNotIn("consumer", state)
        self.assertIn("mcp", state)

        checked = self._sync(repo="owner/project", apply=False)
        self.assertFalse(checked.changes)

    def test_repo_sync_targets_a_lane_skill_without_a_path(self):
        self._write_repo_targets(
            {
                "alpha": {
                    "description": "shared skill also routed to one repo",
                    "repos": ["owner/project"],
                }
            }
        )
        result = self._sync(repo="owner/project", apply=True)
        self.assertFalse(result.conflicts)
        self.assertTrue((self.destination / "alpha" / "SKILL.md").is_file())
        # A consumer destination stays uninvolved with repo state.
        self.assertIsNone(
            json.loads(
                (self.destination / sync_module.STATE_FILE).read_text(encoding="utf-8")
            ).get("consumer")
        )

    def test_repo_sync_rejects_a_consumer_managed_destination(self):
        self._sync(consumer="codex", apply=True)
        self._write_repo_targets(
            {
                "alpha": {
                    "description": "shared skill also routed to one repo",
                    "repos": ["owner/project"],
                }
            }
        )
        with self.assertRaisesRegex(sync_module.SyncError, "consumer 'codex'"):
            self._sync(repo="owner/project", apply=True)

    def test_repo_sync_rejects_an_untargeted_repo(self):
        self._write_repo_targets(
            {
                "alpha": {
                    "description": "shared skill routed elsewhere",
                    "repos": ["owner/other"],
                }
            }
        )
        with self.assertRaisesRegex(sync_module.SyncError, "owner/project"):
            self._sync(repo="owner/project", apply=False)

    def test_repo_cli_requires_destination_and_refuses_combinations(self):
        self._write_repo_targets(
            {
                "alpha": {
                    "description": "shared skill also routed to one repo",
                    "repos": ["owner/project"],
                }
            }
        )
        self.assertEqual(
            sync_module.main(["--check", "--repo-root", str(self.repo), "--repo", "owner/project"]),
            2,
        )
        self.assertEqual(
            sync_module.main(
                [
                    "--check",
                    "--repo-root",
                    str(self.repo),
                    "--repo",
                    "owner/project",
                    "--consumer",
                    "codex",
                    "--destination",
                    str(self.destination),
                ]
            ),
            2,
        )

    def test_runtime_deployment_with_repo_selects_repo_targeted_skill(self):
        self._write_repo_only_skill("beta-ops", "beta", "beta v1")
        self._write_repo_targets(
            {
                "beta": {
                    "description": "repo-only skill for the runtime's environment",
                    "path": "beta-ops/skills/beta",
                    "repos": ["owner/project"],
                    "mcp": [],
                }
            }
        )
        path = self.repo / "plugins" / sync_module.DISTRIBUTION_PATH
        distribution = json.loads(path.read_text(encoding="utf-8"))
        distribution["deployments"] = {
            "ops-runtime": {
                "description": "runtime operating the owner/project environment",
                "repo": "owner/project",
                "skills": ["alpha", "beta"],
            }
        }
        path.write_text(json.dumps(distribution), encoding="utf-8")

        result = self._sync(consumer=None, deployment="ops-runtime", apply=True, prune=True)
        self.assertFalse(result.conflicts)
        installed = {
            path.name
            for path in self.destination.iterdir()
            if (path / "SKILL.md").is_file()
        }
        self.assertEqual(installed, {"alpha", "beta"})

    def test_runtime_deployment_without_repo_cannot_select_repo_only_skill(self):
        self._write_repo_only_skill("beta-ops", "beta", "beta v1")
        self._write_repo_targets(
            {
                "beta": {
                    "description": "repo-only skill",
                    "path": "beta-ops/skills/beta",
                    "repos": ["owner/project"],
                    "mcp": [],
                }
            }
        )
        self._write_deployment("ops-runtime", ["alpha", "beta"], consumer=None)
        with self.assertRaisesRegex(sync_module.SyncError, "repo-targeted skill"):
            self._sync(consumer=None, deployment="ops-runtime", apply=False, prune=True)

    def test_mcp_artifact_local_modification_is_a_conflict_unless_forced(self):
        self._write_repo_only_skill("beta-ops", "beta", "beta v1")
        self._write_mcp_template("beta", {"command": "npx", "args": ["-y", "beta-mcp"]})
        self._write_repo_targets(
            {
                "beta": {
                    "description": "repo-only skill with an MCP template",
                    "path": "beta-ops/skills/beta",
                    "repos": ["owner/project"],
                    "mcp": ["beta"],
                }
            }
        )
        self._sync(repo="owner/project", apply=True)
        artifact = self.destination / sync_module.MCP_ARTIFACT_NAME
        artifact.write_text('{"mcpServers": {"local": {}}}\n', encoding="utf-8")

        conflicted = self._sync(repo="owner/project", apply=True)
        self.assertTrue(conflicted.conflicts)
        self.assertEqual(
            json.loads(artifact.read_text(encoding="utf-8"))["mcpServers"].keys(),
            {"local"},
        )

        forced = self._sync(repo="owner/project", apply=True, force=True)
        self.assertFalse(forced.conflicts)
        self.assertEqual(
            json.loads(artifact.read_text(encoding="utf-8"))["mcpServers"].keys(),
            {"beta"},
        )


if __name__ == "__main__":
    unittest.main()
