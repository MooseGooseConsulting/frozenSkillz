import importlib.util
import json
import re
import sys
from pathlib import Path


def _load_skill_validation():
    """Load skill_validation from this script's directory.

    Anchoring to ``__file__`` guarantees the sibling module wins even when a
    third-party ``skill_validation`` package is installed in site-packages or
    this script is imported from an arbitrary working directory.
    """

    module_name = "frozenskillz_skill_validation"
    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached
    module_path = Path(__file__).resolve().parent / "skill_validation.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load skill_validation from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_skill_validation = _load_skill_validation()
SkillMetadataError = _skill_validation.SkillMetadataError
validate_skill_metadata = _skill_validation.validate_skill_metadata


PLUGIN_MANIFESTS = [
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
]
FROZEN_CONSUMER_MANIFESTS = {
    "claude": Path("plugins/frozen-skills/.claude-plugin/plugin.json"),
    "codex": Path("plugins/frozen-skills/.codex-plugin/plugin.json"),
    "cursor": Path("plugins/frozen-skills/.cursor-plugin/plugin.json"),
    "gemini": Path("plugins/frozen-skills/gemini-extension.json"),
}
CONSUMER_PACKAGE_MANIFESTS = {
    "claude": Path(".claude-plugin/plugin.json"),
    "codex": Path(".codex-plugin/plugin.json"),
    "cursor": Path(".cursor-plugin/plugin.json"),
    "gemini": Path("gemini-extension.json"),
}
FROZEN_MARKETPLACE_MANIFESTS = {
    "claude": Path(".claude-plugin/marketplace.json"),
    "codex": Path(".codex-plugin/marketplace.json"),
    "cursor": Path(".cursor-plugin/marketplace.json"),
    "gemini": Path("gemini-marketplace.json"),
}
FROZEN_DISTRIBUTION = Path("plugins/distribution.json")
SAFE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REPO_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$"
)


def load_json(filepath):
    with filepath.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_inside(plugin_root, relative_path):
    candidate_path = Path(relative_path)
    if candidate_path.is_absolute():
        raise ValueError(f"Path must be relative: {relative_path}")
    resolved_plugin_root = plugin_root.resolve()
    resolved_path = (plugin_root / candidate_path).resolve()
    try:
        resolved_path.relative_to(resolved_plugin_root)
    except ValueError as exc:
        raise ValueError(f"Path escapes plugin root: {relative_path}") from exc
    return resolved_path


def validate_skill_entry(plugin_root, skill, seen_names):
    skill_name = skill.get("name") if isinstance(skill, dict) else None
    if not isinstance(skill_name, str) or not skill_name:
        raise ValueError("Skill entry missing name")
    if skill_name in seen_names:
        raise ValueError(f"Duplicate skill name {skill_name}")
    seen_names.add(skill_name)
    skill_path = skill.get("path")
    if not isinstance(skill_path, str) or not skill_path:
        raise ValueError(f"Skill {skill_name} missing path")
    resolved_skill_path = resolve_inside(plugin_root, skill_path)
    if resolved_skill_path.name != skill_name:
        raise ValueError(
            f"Skill {skill_name} must use a same-name directory: {skill_path}"
        )
    if not (resolved_skill_path / "SKILL.md").is_file():
        raise ValueError(f"Skill {skill_name} has no SKILL.md")
    try:
        validate_skill_metadata(resolved_skill_path / "SKILL.md", skill_name)
    except SkillMetadataError as exc:
        raise ValueError(f"Skill {skill_name} has invalid metadata: {exc}") from exc


def validate_repo_targets(distribution, plugin_root, lane_names, seen_names):
    """Validate the optional repository axis.

    A repo-targeted skill is routed only into the repositories that own the
    environment it operates. Skills already in a shared/consumer lane inherit
    their lane path; a repo-only skill declares a ``path`` in a dedicated
    package outside the shared auto-discovery tree.
    """

    repo_targets = distribution.get("repo_targets", {})
    if not isinstance(repo_targets, dict):
        raise ValueError("distribution repo_targets field must be an object")
    repo_root = plugin_root.parent
    for skill_name, entry in repo_targets.items():
        if not isinstance(skill_name, str) or not SAFE_NAME_PATTERN.fullmatch(skill_name):
            raise ValueError(f"Unsafe repo_targets skill name {skill_name!r}")
        if not isinstance(entry, dict):
            raise ValueError(f"repo_targets entry for {skill_name} must be an object")
        description = entry.get("description")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"repo_targets entry for {skill_name} has no description")

        relative_path = entry.get("path")
        if skill_name in lane_names:
            if relative_path is not None:
                raise ValueError(
                    f"repo_targets entry for {skill_name} must not carry a path; "
                    "it inherits its shared/consumer lane path"
                )
        else:
            if not isinstance(relative_path, str) or not relative_path:
                raise ValueError(
                    f"repo_targets skill {skill_name} is not in any shared/consumer "
                    "lane, so it must declare a path in a dedicated repo-only package"
                )
            parts = Path(relative_path).parts
            if (
                len(parts) < 3
                or parts[0] == "frozen-skills"
                or parts[1] != "skills"
                or ".." in parts
            ):
                raise ValueError(
                    f"repo_targets skill {skill_name} must live in a dedicated "
                    f"repo-only package (<package>/skills/{skill_name}), not in the "
                    "shared auto-discovery tree"
                )
            validate_skill_entry(
                plugin_root, {"name": skill_name, "path": relative_path}, seen_names
            )

        repos = entry.get("repos")
        if not isinstance(repos, list) or not repos:
            raise ValueError(f"repo_targets entry for {skill_name} has no repos")
        if len(repos) != len(set(repos)):
            raise ValueError(f"repo_targets entry for {skill_name} duplicates a repo")
        for repo in repos:
            if not isinstance(repo, str) or not REPO_ID_PATTERN.fullmatch(repo):
                raise ValueError(
                    f"repo_targets entry for {skill_name} has an unsafe repository "
                    f"identifier {repo!r}; expected 'owner/repo'"
                )

        mcp = entry.get("mcp", [])
        if not isinstance(mcp, list):
            raise ValueError(f"repo_targets entry for {skill_name} mcp must be a list")
        if len(mcp) != len(set(mcp)):
            raise ValueError(
                f"repo_targets entry for {skill_name} duplicates an MCP template"
            )
        for template in mcp:
            if not isinstance(template, str) or not SAFE_NAME_PATTERN.fullmatch(template):
                raise ValueError(
                    f"repo_targets entry for {skill_name} has an unsafe MCP template "
                    f"name {template!r}"
                )
            template_path = repo_root / "mcp" / f"{template}.json"
            if not template_path.is_file():
                raise ValueError(
                    f"repo_targets entry for {skill_name} names MCP template "
                    f"{template} but {template_path} does not exist"
                )
            load_json(template_path)
    return set(repo_targets)


def validate_deployment_subsets(distribution, shared_names, available_by_consumer, repo_targets=None):
    """Check every deployment subset against the aligned active distribution.

    A deployment comes in two kinds. A client-scoped deployment names the
    consumer whose client format it receives plus the exact subset of that
    consumer's active skills. A runtime deployment omits ``consumer`` because it
    is not one of the four clients — it may select only shared skills, since it
    has no client packaging format to render a restricted package into. A
    runtime deployment that names the ``repo`` whose environment it operates may
    additionally select repo-targeted skills aimed at that repository.

    Neither kind may select a skill the distribution does not already carry.
    """

    repo_targets = repo_targets or {}
    deployments = distribution.get("deployments", {})
    if not isinstance(deployments, dict):
        raise ValueError("distribution deployments field must be an object")
    for name, entry in deployments.items():
        if not isinstance(name, str) or not SAFE_NAME_PATTERN.fullmatch(name):
            raise ValueError(f"Unsafe deployment name {name!r}")
        if not isinstance(entry, dict):
            raise ValueError(f"Deployment {name} must be an object")
        description = entry.get("description")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"Deployment {name} has no description")
        consumer = entry.get("consumer")
        if consumer is not None and consumer not in available_by_consumer:
            raise ValueError(
                f"Deployment {name} must name one consumer of "
                f"{sorted(available_by_consumer)}, or omit consumer entirely for a "
                "non-client runtime that receives only shared skills"
            )
        deployment_repo = entry.get("repo")
        if deployment_repo is not None and (
            not isinstance(deployment_repo, str)
            or not REPO_ID_PATTERN.fullmatch(deployment_repo)
        ):
            raise ValueError(
                f"Deployment {name} has an unsafe repo identifier {deployment_repo!r}"
            )
        skills = entry.get("skills")
        if not isinstance(skills, list) or not skills:
            raise ValueError(f"Deployment {name} has no skills")
        available = (
            shared_names if consumer is None else available_by_consumer[consumer]
        )
        if deployment_repo is not None:
            available = available | {
                skill
                for skill in repo_targets
                if deployment_repo in distribution["repo_targets"][skill].get("repos", [])
            }
        seen = set()
        for skill_name in skills:
            if not isinstance(skill_name, str) or not SAFE_NAME_PATTERN.fullmatch(
                skill_name
            ):
                raise ValueError(f"Deployment {name} has an unsafe skill {skill_name!r}")
            if skill_name in seen:
                raise ValueError(f"Deployment {name} duplicates skill {skill_name}")
            seen.add(skill_name)
            if skill_name not in available:
                if consumer is None:
                    raise ValueError(
                        f"Deployment {name} declares no consumer, so it may only "
                        f"select shared skills; {skill_name} is a consumer-restricted "
                        "package, a repo-targeted skill this deployment's repo does "
                        "not operate, or is not in the distribution"
                    )
                raise ValueError(
                    f"Deployment {name} skill {skill_name} is not active for "
                    f"consumer {consumer}"
                )
    return len(deployments)


def validate_manifest(filepath):
    print(f"Validating {filepath}...")
    try:
        data = load_json(filepath)
        required_fields = ["name", "version", "description"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            print(f"  FAILED: Missing fields {missing}")
            return False

        plugin_root = filepath.parent.parent if filepath.name == "plugin.json" else filepath.parent
        skills = data.get("skills", [])
        if isinstance(skills, str):
            skill_root = resolve_inside(plugin_root, skills)
            if not skill_root.is_dir():
                raise ValueError(f"Missing skill root {skill_root}")
            discovered = [
                path for path in skill_root.iterdir() if (path / "SKILL.md").is_file()
            ]
            if not discovered:
                raise ValueError(f"Skill root contains no skills: {skill_root}")
            for skill_dir in discovered:
                try:
                    validate_skill_metadata(skill_dir / "SKILL.md", skill_dir.name)
                except SkillMetadataError as exc:
                    raise ValueError(
                        f"Skill {skill_dir.name} has invalid metadata: {exc}"
                    ) from exc
        elif isinstance(skills, list):
            seen_names = set()
            for skill in skills:
                validate_skill_entry(plugin_root, skill, seen_names)
        else:
            raise ValueError("skills must be a path string or entry list")

        print("  PASSED")
        return True
    except Exception as exc:
        print(f"  FAILED: {exc}")
        return False


def discover_manifests():
    manifests = []
    for plugin_root in sorted(Path("plugins").iterdir()):
        if not plugin_root.is_dir():
            continue
        for relative_manifest in PLUGIN_MANIFESTS:
            manifest = plugin_root / relative_manifest
            if manifest.exists():
                manifests.append(manifest)
    return manifests


def validate_frozen_consumer_contract():
    print("Validating frozen-skills consumer contract...")
    try:
        return _validate_frozen_consumer_contract()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  FAILED: cannot read consumer contract JSON: {exc}")
        return False


def _validate_frozen_consumer_contract():
    loaded = {
        consumer: load_json(path)
        for consumer, path in FROZEN_CONSUMER_MANIFESTS.items()
    }
    identities = {(data.get("name"), data.get("version")) for data in loaded.values()}
    if len(identities) != 1 or next(iter(identities))[0] != "frozen-skills":
        print("  FAILED: Consumer manifests must share frozen-skills name and version")
        return False
    plugin_version = next(iter(identities))[1]
    distribution = load_json(FROZEN_DISTRIBUTION)
    if (
        distribution.get("schema") != 1
        or distribution.get("plugin") != "frozen-skills"
        or distribution.get("version") != plugin_version
    ):
        print("  FAILED: distribution identity, schema, or version is not aligned")
        return False
    consumers = distribution.get("consumers")
    if not isinstance(consumers, dict) or set(consumers) != set(loaded):
        print("  FAILED: distribution must name exactly the four supported consumers")
        return False
    consumer_packages = distribution.get("consumer_packages")
    if (
        not isinstance(consumer_packages, dict)
        or set(consumer_packages) != set(loaded)
        or any(not isinstance(packages, list) for packages in consumer_packages.values())
        or any(
            not isinstance(package, str)
            or not package
            or "/" in package
            or "\\" in package
            or package in {".", ".."}
            or package == "frozen-skills"
            for packages in consumer_packages.values()
            for package in packages
        )
        or any(
            len(packages) != len(set(packages))
            for packages in consumer_packages.values()
        )
    ):
        print(
            "  FAILED: consumer_packages must name exactly the four consumers with "
            "unique safe package lists; frozen-skills is reserved for shared skills"
        )
        return False

    plugin_root = FROZEN_DISTRIBUTION.parent
    try:
        shared = distribution.get("shared")
        if not isinstance(shared, list):
            raise ValueError("distribution shared field must be a list")
        shared_names = set()
        for entry in shared:
            validate_skill_entry(plugin_root, entry, shared_names)
            parts = Path(entry["path"]).parts
            if (
                len(parts) < 3
                or parts[:2] != ("frozen-skills", "skills")
                or ".." in parts
            ):
                raise ValueError(
                    f"Shared skill is outside frozen-skills/skills/: {entry['path']}"
                )
        available_by_consumer = {}
        for consumer, entries in consumers.items():
            if not isinstance(entries, list):
                raise ValueError(f"Consumer {consumer} entries must be a list")
            consumer_names = set(shared_names)
            available_by_consumer[consumer] = consumer_names
            for entry in entries:
                validate_skill_entry(plugin_root, entry, consumer_names)
                parts = Path(entry["path"]).parts
                if (
                    len(parts) < 3
                    or parts[0] not in set(consumer_packages[consumer])
                    or parts[1] != "skills"
                    or ".." in parts
                ):
                    raise ValueError(
                        f"Consumer {consumer} skill is outside its declared packages: "
                        f"{entry['path']}"
                    )

        discovered_shared = {
            path.name
            for path in (plugin_root / "frozen-skills" / "skills").iterdir()
            if (path / "SKILL.md").is_file()
        }
        if discovered_shared != shared_names:
            raise ValueError(
                "Shared physical skill tree differs from distribution: "
                f"tree={sorted(discovered_shared)}, distribution={sorted(shared_names)}"
            )
        for consumer, entries in consumers.items():
            for package in consumer_packages[consumer]:
                expected_names = {
                    entry["name"]
                    for entry in entries
                    if Path(entry["path"]).parts[0] == package
                }
                package_root = plugin_root / package / "skills"
                discovered_names = (
                    {
                        path.name
                        for path in package_root.iterdir()
                        if (path / "SKILL.md").is_file()
                    }
                    if package_root.is_dir()
                    else set()
                )
                if discovered_names != expected_names:
                    raise ValueError(
                        f"{consumer} package {package} differs from distribution: "
                        f"tree={sorted(discovered_names)}, "
                        f"distribution={sorted(expected_names)}"
                    )

        lane_names = set(shared_names)
        for entries in consumers.values():
            lane_names |= {entry["name"] for entry in entries}
        seen_names = set(lane_names)
        repo_target_names = validate_repo_targets(
            distribution, plugin_root, lane_names, seen_names
        )

        deployment_count = validate_deployment_subsets(
            distribution, shared_names, available_by_consumer, repo_target_names
        )
    except ValueError as exc:
        print(f"  FAILED: {exc}")
        return False

    shared_pairs = [(entry["name"], entry["path"]) for entry in shared]
    native_shared_pairs = [
        (name, path.replace("frozen-skills/", "", 1))
        for name, path in shared_pairs
    ]
    for consumer in ("claude", "codex", "cursor", "gemini"):
        native_pairs = [
            (entry.get("name"), entry.get("path"))
            for entry in loaded[consumer].get("skills", [])
        ]
        if native_pairs != native_shared_pairs:
            print(
                f"  FAILED: {consumer} native manifest must expose exactly the shared lane"
            )
            return False

    for consumer, marketplace_path in FROZEN_MARKETPLACE_MANIFESTS.items():
        marketplace = load_json(marketplace_path)
        entries = [
            entry
            for entry in marketplace.get("plugins", [])
            if entry.get("name") == "frozen-skills"
        ]
        if len(entries) != 1 or entries[0].get("version") != plugin_version:
            print(
                f"  FAILED: {consumer} marketplace frozen-skills version must be "
                f"{plugin_version}"
            )
            return False

    organizer_consumers = {
        consumer
        for consumer, entries in consumers.items()
        if "codex-thread-organizer" in {entry.get("name") for entry in entries}
    }
    if organizer_consumers != {"codex"}:
        print(
            "  FAILED: codex-thread-organizer must be listed only for Codex, found "
            f"{sorted(organizer_consumers)}"
        )
        return False

    declared_packages = {
        package
        for packages in consumer_packages.values()
        for package in packages
    }
    for package in declared_packages:
        for consumer in loaded:
            approved = package in consumer_packages[consumer]
            marketplace = load_json(FROZEN_MARKETPLACE_MANIFESTS[consumer])
            marketplace_entries = [
                entry
                for entry in marketplace.get("plugins", [])
                if entry.get("name") == package
            ]
            expected_count = 1 if approved else 0
            if len(marketplace_entries) != expected_count:
                print(
                    f"  FAILED: package {package} marketplace approval for {consumer} "
                    "differs from consumer_packages"
                )
                return False
            if not approved:
                continue
            if marketplace_entries[0].get("version") != plugin_version:
                print(
                    f"  FAILED: package {package} marketplace version for {consumer} "
                    "is not aligned"
                )
                return False
            package_manifest_path = (
                Path("plugins") / package / CONSUMER_PACKAGE_MANIFESTS[consumer]
            )
            if not package_manifest_path.is_file():
                print(
                    f"  FAILED: package {package} is approved for {consumer} but lacks "
                    f"{CONSUMER_PACKAGE_MANIFESTS[consumer]}"
                )
                return False
            package_manifest = load_json(package_manifest_path)
            if (
                package_manifest.get("name") != package
                or package_manifest.get("version") != plugin_version
            ):
                print(
                    f"  FAILED: package {package} manifest for {consumer} is not aligned"
                )
                return False

    print(
        "  PASSED: shared/consumer packages, identity/version, "
        f"{len(repo_target_names)} repo-targeted skill(s), and "
        f"{deployment_count} deployment subset(s) are aligned"
    )
    return True


def main():
    manifests = discover_manifests()
    results = [validate_manifest(manifest) for manifest in manifests]

    contract_valid = validate_frozen_consumer_contract()

    if manifests and all(results) and contract_valid:
        print(f"\nAll {len(manifests)} manifests validated successfully.")
        return

    print(f"\nValidation failed. Found {len(manifests)} manifests.")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
