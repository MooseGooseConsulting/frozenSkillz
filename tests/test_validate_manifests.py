import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_manifests.py"
SPEC = importlib.util.spec_from_file_location("validate_manifests", SCRIPT)
validate_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validate_module
SPEC.loader.exec_module(validate_module)


class ValidateManifestsTests(unittest.TestCase):
    def test_contract_reports_missing_or_invalid_json_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifests = {}
            for consumer in validate_module.FROZEN_CONSUMER_MANIFESTS:
                manifest = root / f"{consumer}.json"
                manifest.write_text(
                    json.dumps(
                        {
                            "name": "frozen-skills",
                            "version": "1.0.0",
                            "description": "test",
                            "skills": [],
                        }
                    ),
                    encoding="utf-8",
                )
                manifests[consumer] = manifest

            invalid = root / "invalid.json"
            invalid.write_text("{", encoding="utf-8")
            for broken_distribution in (root / "missing.json", invalid):
                with self.subTest(distribution=broken_distribution.name):
                    output = io.StringIO()
                    with (
                        mock.patch.object(
                            validate_module,
                            "FROZEN_CONSUMER_MANIFESTS",
                            manifests,
                        ),
                        mock.patch.object(
                            validate_module,
                            "FROZEN_DISTRIBUTION",
                            broken_distribution,
                        ),
                        redirect_stdout(output),
                    ):
                        self.assertFalse(
                            validate_module.validate_frozen_consumer_contract()
                        )
                    self.assertIn("FAILED", output.getvalue())

    def test_contract_rejects_the_shared_package_in_a_consumer_lane(self):
        distribution = validate_module.load_json(
            validate_module.FROZEN_DISTRIBUTION
        )
        distribution["consumer_packages"]["codex"] = ["frozen-skills"]
        real_load_json = validate_module.load_json

        def load_with_invalid_distribution(path):
            if path == validate_module.FROZEN_DISTRIBUTION:
                return distribution
            return real_load_json(path)

        output = io.StringIO()
        with (
            mock.patch.object(
                validate_module,
                "load_json",
                side_effect=load_with_invalid_distribution,
            ),
            redirect_stdout(output),
        ):
            self.assertFalse(validate_module.validate_frozen_consumer_contract())
        self.assertIn("reserved for shared skills", output.getvalue())

    def _contract_with_deployments(self, deployments):
        distribution = validate_module.load_json(validate_module.FROZEN_DISTRIBUTION)
        distribution["deployments"] = deployments
        real_load_json = validate_module.load_json

        def load_with_patched_distribution(path):
            if path == validate_module.FROZEN_DISTRIBUTION:
                return distribution
            return real_load_json(path)

        output = io.StringIO()
        with (
            mock.patch.object(
                validate_module,
                "load_json",
                side_effect=load_with_patched_distribution,
            ),
            redirect_stdout(output),
        ):
            valid = validate_module.validate_frozen_consumer_contract()
        return valid, output.getvalue()

    def test_contract_rejects_a_deployment_skill_the_consumer_does_not_carry(self):
        valid, output = self._contract_with_deployments(
            {
                "hermes-ops": {
                    "description": "test",
                    "consumer": "claude",
                    "skills": ["codex-thread-organizer"],
                }
            }
        )
        self.assertFalse(valid)
        self.assertIn("is not active for consumer claude", output)

    def test_contract_rejects_a_malformed_deployment_entry(self):
        for deployments, expected in (
            ({"hermes-ops": {"consumer": "codex", "skills": ["doppler"]}}, "no description"),
            (
                {
                    "hermes-ops": {
                        "description": "t",
                        "consumer": "not-a-client",
                        "skills": ["doppler"],
                    }
                },
                "must name one consumer",
            ),
            ({"hermes-ops": {"description": "t", "consumer": "codex", "skills": []}}, "has no skills"),
            (
                {
                    "hermes-ops": {
                        "description": "t",
                        "consumer": "codex",
                        "skills": ["doppler", "doppler"],
                    }
                },
                "duplicates skill",
            ),
            (
                {"../outside": {"description": "t", "consumer": "codex", "skills": ["doppler"]}},
                "Unsafe deployment name",
            ),
        ):
            with self.subTest(expected=expected):
                valid, output = self._contract_with_deployments(deployments)
                self.assertFalse(valid)
                self.assertIn(expected, output)

    def test_contract_accepts_a_consumer_less_runtime_deployment(self):
        valid, output = self._contract_with_deployments(
            {
                "hermes-ops": {
                    "description": "bare-SKILL.md service runtime, not a client",
                    "skills": ["doppler", "pdm-cli-operations"],
                }
            }
        )
        self.assertTrue(valid, output)
        self.assertIn("1 deployment subset(s) are aligned", output)

    def test_contract_rejects_a_restricted_package_in_a_consumer_less_deployment(self):
        valid, output = self._contract_with_deployments(
            {
                "hermes-ops": {
                    "description": "bare-SKILL.md service runtime, not a client",
                    "skills": ["doppler", "codex-thread-organizer"],
                }
            }
        )
        self.assertFalse(valid)
        self.assertIn(
            "declares no consumer, so it may only select shared skills", output
        )
        self.assertIn("codex-thread-organizer", output)

    def test_contract_accepts_a_valid_deployment(self):
        valid, output = self._contract_with_deployments(
            {
                "hermes-ops": {
                    "description": "test",
                    "consumer": "codex",
                    "skills": ["doppler", "codex-thread-organizer"],
                }
            }
        )
        self.assertTrue(valid, output)
        self.assertIn("1 deployment subset(s) are aligned", output)


class SkillMetadataValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.plugin = Path(self.temporary.name) / "plugin"
        self.skill = self.plugin / "skills/alpha"
        self.skill.mkdir(parents=True)
        self.manifest = self.plugin / ".codex-plugin/plugin.json"
        self.manifest.parent.mkdir()
        self.manifest.write_text(
            json.dumps(
                {
                    "name": "frozen-skills",
                    "version": "1.0.0",
                    "description": "test",
                    "skills": [{"name": "alpha", "path": "skills/alpha"}],
                }
            ),
            encoding="utf-8",
        )

    def validate(self):
        with redirect_stdout(io.StringIO()) as output:
            result = validate_module.validate_manifest(self.manifest)
        return result, output.getvalue()

    def test_valid_skill_metadata_passes(self):
        (self.skill / "SKILL.md").write_text(
            "---\nname: alpha\ndescription: Test skill.\n---\n\n# Alpha\n",
            encoding="utf-8",
        )

        result, _ = self.validate()
        self.assertTrue(result)

    def test_folded_block_scalar_description_passes(self):
        (self.skill / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "description: >-\n"
            "  Use when testing folded block scalars\n"
            "  across multiple frontmatter lines.\n"
            "---\n\n# Alpha\n",
            encoding="utf-8",
        )

        result, _ = self.validate()
        self.assertTrue(result)

    def test_block_scalar_with_indentation_indicator_passes(self):
        for header in (">2-", "|2", ">-2", "|+1"):
            with self.subTest(header=header):
                (self.skill / "SKILL.md").write_text(
                    "---\n"
                    "name: alpha\n"
                    f"description: {header}\n"
                    "  Use when testing block scalar headers\n"
                    "  with explicit indentation indicators.\n"
                    "---\n\n# Alpha\n",
                    encoding="utf-8",
                )

                result, output = self.validate()
                self.assertTrue(result, output)

    def test_indented_continuation_of_plain_scalar_passes(self):
        """An indented line after a plain scalar is a legal multi-line scalar.

        The hand-rolled parser used to reject this as an "unexpected indented
        line"; PyYAML folds it into the description, and so does every real
        client, so the validator must agree.
        """

        (self.skill / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "description: Test skill.\n"
            "  stray continuation line\n"
            "---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertTrue(result, output)

    def test_indented_mapping_key_fails(self):
        (self.skill / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "  description: Test skill.\n"
            "---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("invalid YAML frontmatter", output)

    def test_empty_description_fails(self):
        (self.skill / "SKILL.md").write_text(
            "---\nname: alpha\ndescription:\n---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("'description'", output)

    def test_unexpected_frontmatter_field_fails(self):
        (self.skill / "SKILL.md").write_text(
            "---\nname: alpha\ndescription: Test skill.\nauthor: someone\n---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("unexpected frontmatter field", output)

    def test_missing_frontmatter_fails_manifest_validation(self):
        (self.skill / "SKILL.md").write_text("# Alpha\n", encoding="utf-8")

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("missing YAML frontmatter", output)

    def test_frontmatter_name_must_match_manifest_name(self):
        (self.skill / "SKILL.md").write_text(
            "---\nname: beta\ndescription: Test skill.\n---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("does not match manifest name", output)

    def test_directory_name_must_match_manifest_name(self):
        other_skill = self.plugin / "skills/beta"
        other_skill.mkdir()
        (other_skill / "SKILL.md").write_text(
            "---\nname: alpha\ndescription: Test skill.\n---\n",
            encoding="utf-8",
        )
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        data["skills"][0]["path"] = "skills/beta"
        self.manifest.write_text(json.dumps(data), encoding="utf-8")

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("same-name directory", output)

    def test_missing_bundled_reference_fails(self):
        (self.skill / "SKILL.md").write_text(
            "---\nname: alpha\ndescription: Test skill.\n---\n\n"
            "Read `references/missing.md` first.\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("does not exist", output)

    def test_invalid_yaml_frontmatter_fails(self):
        """Frontmatter that PyYAML refuses to load must fail validation.

        Every case here passed the hand-rolled parser while raising in PyYAML,
        so the skill would have shipped and then failed to load in a client.
        """

        cases = {
            "unquoted colon in value": "description: does x: then y\n",
            "tab indented block body": "description: >-\n\tUse when tabs sneak in.\n",
            "unterminated double quote": 'description: "unterminated\n',
            "reserved indicator": "description: @reserved\n",
            "unclosed flow sequence": (
                "description: Test skill.\nallowed-tools: [Read, Write\n"
            ),
        }
        for label, frontmatter in cases.items():
            with self.subTest(case=label):
                (self.skill / "SKILL.md").write_text(
                    f"---\nname: alpha\n{frontmatter}---\n",
                    encoding="utf-8",
                )

                result, output = self.validate()
                self.assertFalse(result, output)
                self.assertIn("invalid YAML frontmatter", output)

    def test_optional_fields_accept_block_and_flow_styles(self):
        """``metadata`` and ``allowed-tools`` are allowed, so both YAML styles work.

        Block style used to trip the "unexpected indented line" rule, making
        ALLOWED_FIELDS advertise shapes the parser rejected.
        """

        cases = {
            "metadata block": "metadata:\n  version: 1\n",
            "metadata flow": "metadata: {version: 1}\n",
            "allowed-tools block": "allowed-tools:\n  - Read\n  - Write\n",
            "allowed-tools flow": "allowed-tools: [Read, Write]\n",
        }
        for label, frontmatter in cases.items():
            with self.subTest(case=label):
                (self.skill / "SKILL.md").write_text(
                    f"---\nname: alpha\ndescription: Test skill.\n{frontmatter}"
                    "---\n\n# Alpha\n",
                    encoding="utf-8",
                )

                result, output = self.validate()
                self.assertTrue(result, output)

    def test_duplicate_frontmatter_field_fails(self):
        (self.skill / "SKILL.md").write_text(
            "---\nname: alpha\nname: beta\ndescription: Test skill.\n---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("duplicate 'name' frontmatter field", output)

    def test_non_mapping_frontmatter_fails(self):
        (self.skill / "SKILL.md").write_text(
            "---\n- alpha\n- beta\n---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("must be a mapping", output)

    def test_non_string_name_fails(self):
        (self.skill / "SKILL.md").write_text(
            "---\nname: 123\ndescription: Test skill.\n---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("must be a string", output)

    def test_yaml_error_reports_the_skill_md_line_number(self):
        (self.skill / "SKILL.md").write_text(
            "---\nname: alpha\ndescription: does x: then y\n---\n",
            encoding="utf-8",
        )

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("line 3", output)

    def test_skill_root_string_validates_discovered_skill_metadata(self):
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        data["skills"] = "./skills/"
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        (self.skill / "SKILL.md").write_text("# Alpha\n", encoding="utf-8")

        result, output = self.validate()
        self.assertFalse(result)
        self.assertIn("missing YAML frontmatter", output)


class DopplerReferenceHygieneTests(unittest.TestCase):
    BANNED_CONFIGURE_PATTERN = re.compile(
        r"doppler configure(?!\s+(?:get|unset)\b)"
    )

    def test_doppler_docs_avoid_token_revealing_configure_commands(self):
        doppler_root = (
            Path(__file__).resolve().parents[1]
            / "plugins/frozen-skills/skills/doppler"
        )
        offenders = []
        for markdown in sorted(doppler_root.rglob("*.md")):
            for line_number, line in enumerate(
                markdown.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if self.BANNED_CONFIGURE_PATTERN.search(line):
                    offenders.append(f"{markdown}:{line_number}: {line.strip()}")
        self.assertEqual(
            [],
            offenders,
            "bare/debug/--all configure display commands can reveal the saved "
            "CLI token; query non-secret options explicitly",
        )


if __name__ == "__main__":
    unittest.main()
