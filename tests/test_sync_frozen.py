import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/sync_frozen.py"
SCRIPTS = str(SCRIPT.parent)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
SPEC = importlib.util.spec_from_file_location("sync_frozen", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load synchronization module from {SCRIPT}")
sync_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_module)


class SyncFrozenTests(unittest.TestCase):
    @mock.patch.object(sync_module.sync_codex_global_config, "main", side_effect=[0, 0])
    @mock.patch.object(sync_module.sync_frozen_skills, "main", side_effect=[0, 0])
    def test_apply_runs_preflight_then_applies_skills_and_config(
        self, skills_main, config_main
    ):
        alternate = Path("alternate-codex-home")

        # Attach both mocks to one manager so we can assert the *combined*
        # call order across collaborators, not just each mock's own order.
        # Per-mock call_args_list assertions alone would still pass for an
        # implementation that ran skills.check, skills.apply, config.check,
        # config.apply -- which violates the "both preflights precede either
        # apply" contract this test is named for.
        manager = mock.Mock()
        manager.attach_mock(skills_main, "skills_main")
        manager.attach_mock(config_main, "config_main")

        result = sync_module.main(
            ["--consumer", "codex", "--apply", "--codex-home", str(alternate)]
        )

        self.assertEqual(0, result)
        self.assertEqual(
            [
                mock.call.skills_main(
                    [
                        "--check",
                        "--consumer",
                        "codex",
                        "--destination",
                        str(alternate / "skills"),
                    ]
                ),
                mock.call.config_main(["--check", "--codex-home", str(alternate)]),
                mock.call.skills_main(
                    [
                        "--apply",
                        "--consumer",
                        "codex",
                        "--destination",
                        str(alternate / "skills"),
                    ]
                ),
                mock.call.config_main(["--apply", "--codex-home", str(alternate)]),
            ],
            manager.mock_calls,
        )

    @mock.patch.object(sync_module.sync_codex_global_config, "main", return_value=0)
    @mock.patch.object(sync_module.sync_frozen_skills, "main", side_effect=[0, 2])
    def test_config_apply_is_skipped_when_skill_apply_fails(self, skills_main, config_main):
        result = sync_module.main(["--consumer", "codex", "--apply"])

        self.assertEqual(2, result)
        config_main.assert_called_once_with(
            ["--check", "--codex-home", str(Path.home() / ".codex")]
        )

    @mock.patch.object(sync_module.sync_codex_global_config, "main", return_value=0)
    @mock.patch.object(sync_module.sync_frozen_skills, "main", return_value=0)
    def test_alternate_codex_home_routes_skills_to_that_home(self, skills_main, _config_main):
        alternate = Path("alternate-codex-home")
        result = sync_module.main(
            ["--consumer", "codex", "--check", "--codex-home", str(alternate)]
        )

        self.assertEqual(0, result)
        skills_main.assert_called_once_with(
            ["--check", "--consumer", "codex", "--destination", str(alternate / "skills")]
        )


if __name__ == "__main__":
    unittest.main()
