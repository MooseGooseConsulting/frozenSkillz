#!/usr/bin/env python3
"""Synchronize one consumer or deployment's frozen-skills into a local skill root."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


MANIFEST_PATHS = {
    "claude": Path(".claude-plugin/plugin.json"),
    "codex": Path(".codex-plugin/plugin.json"),
    "cursor": Path(".cursor-plugin/plugin.json"),
    "gemini": Path("gemini-extension.json"),
}
DISTRIBUTION_PATH = Path("distribution.json")
DEFAULT_DESTINATIONS = {"codex": "~/.codex/skills"}
STATE_FILE = ".frozen-skills-sync.json"
STATE_SCHEMA = 2
IGNORED_NAMES = {".DS_Store", "Thumbs.db", "__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
SKILL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
REPO_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$"
)
MCP_TEMPLATES_ROOT = "mcp"
MCP_ARTIFACT_NAME = ".frozen-skills-mcp.json"


class SyncError(RuntimeError):
    """Raised when the distribution or destination cannot be synchronized safely."""


class TargetChangedError(SyncError):
    """Raised when a destination changes after its synchronization plan."""

    def __init__(self, target: Path, current_digest: str | None):
        """Record the target and newly observed digest for conflict reporting."""

        super().__init__(f"Destination changed after planning: {target}")
        self.target = target
        self.current_digest = current_digest


@dataclass(frozen=True)
class SkillSource:
    """A validated active skill and the digest of its reviewed source tree."""

    name: str
    path: Path
    digest: str


@dataclass(frozen=True)
class Action:
    """One planned synchronization action and the target state it observed."""

    kind: str
    name: str
    detail: str
    observed_digest: str | None = None


@dataclass(frozen=True)
class SyncResult:
    """The complete synchronization plan or apply result."""

    actions: tuple[Action, ...]

    @property
    def conflicts(self) -> tuple[Action, ...]:
        """Return actions that require human conflict resolution."""

        return tuple(action for action in self.actions if action.kind == "conflict")

    @property
    def changes(self) -> tuple[Action, ...]:
        """Return actions that make or record a distribution change."""

        return tuple(
            action
            for action in self.actions
            if action.kind in {"install", "update", "adopt", "remove", "forget", "state"}
        )


def _load_json(path: Path) -> dict:
    """Load a JSON object or raise a synchronization-specific error."""

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"Cannot read JSON from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SyncError(f"Expected a JSON object in {path}")
    return data


def _validate_safe_name(name: str, kind: str, source: Path) -> None:
    """Reject names that could escape a destination root."""

    if (
        not isinstance(name, str)
        or not SKILL_NAME_PATTERN.fullmatch(name)
        or name in {".", ".."}
    ):
        raise SyncError(f"Unsafe {kind} name {name!r} in {source}")


def _validate_repo_id(repo: str, source: Path) -> None:
    """Reject repository identifiers that are not an exact ``owner/repo`` pair."""

    if not isinstance(repo, str) or not REPO_ID_PATTERN.fullmatch(repo):
        raise SyncError(
            f"Unsafe repository identifier {repo!r} in {source}; expected 'owner/repo'"
        )


def _validate_skill_name(name: str, source: Path) -> None:
    """Reject skill names that could escape a destination root."""

    _validate_safe_name(name, "skill", source)


def _skill_entry_set(data: dict, source: Path) -> tuple[tuple[str, str], ...]:
    """Return a validated ordered name/path tuple from one distribution section."""

    entries = data.get("skills")
    if not isinstance(entries, list):
        raise SyncError(f"Distribution section has no skills list: {source}")

    normalized: list[tuple[str, str]] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise SyncError(f"Invalid skill entry in {source}: {entry!r}")
        name = entry.get("name")
        relative_path = entry.get("path")
        if not isinstance(name, str) or not name:
            raise SyncError(f"Skill entry has no name in {source}")
        _validate_skill_name(name, source)
        if not isinstance(relative_path, str) or not relative_path:
            raise SyncError(f"Skill {name!r} has no path in {source}")
        if name in seen:
            raise SyncError(f"Duplicate skill {name!r} in {source}")
        seen.add(name)
        normalized.append((name, Path(relative_path).as_posix()))
    return tuple(normalized)


def _iter_skill_files(root: Path) -> Iterable[Path]:
    """Yield deterministic source files while rejecting symbolic links."""

    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative_parts = path.relative_to(root).parts
        if any(part in IGNORED_NAMES for part in relative_parts):
            continue
        if path.is_symlink():
            raise SyncError(f"Skill source must not contain symbolic links: {path}")
        if path.is_file() and path.suffix not in IGNORED_SUFFIXES:
            yield path


def digest_directory(root: Path) -> str:
    """Hash a skill tree with explicit path and per-file content framing."""

    if not root.is_dir():
        raise SyncError(f"Skill path is not a directory: {root}")

    digest = hashlib.sha256()
    found_file = False
    for path in _iter_skill_files(root):
        found_file = True
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        file_digest = hashlib.sha256()
        content_length = 0
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                content_length += len(chunk)
                file_digest.update(chunk)
        digest.update(content_length.to_bytes(8, "big"))
        digest.update(file_digest.digest())
    if not found_file:
        raise SyncError(f"Skill directory is empty: {root}")
    return digest.hexdigest()


def _resolve_distribution_skill(source_root: Path, name: str, relative_path: str) -> Path:
    """Resolve and validate one distribution-listed skill source directory."""

    candidate = (source_root / relative_path).resolve()
    try:
        candidate.relative_to(source_root)
    except ValueError as exc:
        raise SyncError(
            f"Skill path escapes plugins source root: {relative_path}"
        ) from exc
    if candidate.name != name:
        raise SyncError(
            f"Skill {name!r} must use a same-name directory, found {relative_path!r}"
        )
    if not (candidate / "SKILL.md").is_file():
        raise SyncError(f"Skill {name!r} has no SKILL.md: {candidate}")
    return candidate


def validate_repo_targets(
    distribution: dict,
    source: Path,
    source_root: Path,
    repo_root: Path,
    lane_names: set[str],
) -> dict[str, dict]:
    """Validate the optional ``repo_targets`` repository axis.

    The repo axis routes a skill (and any MCP templates it needs) only into the
    repositories that own the environment the skill operates, instead of
    broadcasting it to every consumer. A skill listed here may either inherit
    its path from the shared/consumer lanes or declare its own ``path`` in a
    dedicated repo-only package outside the shared auto-discovery tree.

    Returns a map of skill name to ``{"path": str | None, "repos": tuple,
    "mcp": tuple}``. A ``None`` path means the skill inherits its lane path.
    """

    repo_targets = distribution.get("repo_targets", {})
    if not isinstance(repo_targets, dict):
        raise SyncError(f"Distribution repo_targets must be an object: {source}")

    validated: dict[str, dict] = {}
    for skill_name, entry in repo_targets.items():
        _validate_skill_name(skill_name, source)
        if not isinstance(entry, dict):
            raise SyncError(f"repo_targets entry for {skill_name!r} must be an object: {source}")
        description = entry.get("description")
        if not isinstance(description, str) or not description.strip():
            raise SyncError(f"repo_targets entry for {skill_name!r} has no description: {source}")

        relative_path = entry.get("path")
        if skill_name in lane_names:
            if relative_path is not None:
                raise SyncError(
                    f"repo_targets entry for {skill_name!r} must not carry a path; "
                    f"it inherits its shared/consumer lane path: {source}"
                )
        else:
            if not isinstance(relative_path, str) or not relative_path:
                raise SyncError(
                    f"repo_targets entry for {skill_name!r} is not in any "
                    f"shared/consumer lane, so it must declare a path in a dedicated "
                    f"repo-only package: {source}"
                )
            parts = Path(relative_path).parts
            if (
                len(parts) < 3
                or parts[0] == "frozen-skills"
                or parts[1] != "skills"
                or ".." in parts
            ):
                raise SyncError(
                    f"repo_targets skill {skill_name!r} must live in a dedicated "
                    f"repo-only package (<package>/skills/{skill_name}), not in the "
                    f"shared auto-discovery tree: {source}"
                )
            _resolve_distribution_skill(source_root, skill_name, Path(relative_path).as_posix())

        repos = entry.get("repos")
        if not isinstance(repos, list) or not repos:
            raise SyncError(f"repo_targets entry for {skill_name!r} has no repos: {source}")
        seen_repos: set[str] = set()
        for repo in repos:
            _validate_repo_id(repo, source)
            if repo in seen_repos:
                raise SyncError(
                    f"repo_targets entry for {skill_name!r} duplicates repo {repo!r}: {source}"
                )
            seen_repos.add(repo)

        mcp = entry.get("mcp", [])
        if not isinstance(mcp, list):
            raise SyncError(f"repo_targets entry for {skill_name!r} mcp must be a list: {source}")
        seen_mcp: set[str] = set()
        for template in mcp:
            _validate_safe_name(template, "MCP template", source)
            if template in seen_mcp:
                raise SyncError(
                    f"repo_targets entry for {skill_name!r} duplicates MCP template "
                    f"{template!r}: {source}"
                )
            seen_mcp.add(template)
            template_path = repo_root / MCP_TEMPLATES_ROOT / f"{template}.json"
            if not template_path.is_file():
                raise SyncError(
                    f"repo_targets entry for {skill_name!r} names MCP template "
                    f"{template!r} but {template_path} does not exist"
                )
            _load_json(template_path)

        validated[skill_name] = {
            "description": description,
            "path": Path(relative_path).as_posix() if relative_path else None,
            "repos": tuple(repos),
            "mcp": tuple(mcp),
        }
    return validated


def validate_deployments(
    distribution: dict,
    source: Path,
    shared_names: set[str],
    available_by_consumer: dict[str, set[str]],
    repo_targets: dict[str, dict] | None = None,
) -> dict[str, dict]:
    """Validate the optional deployment subsets against the active distribution.

    A deployment is one of two kinds. A client-scoped deployment names its
    consumer and may select from that consumer's shared-plus-restricted set. A
    runtime deployment omits ``consumer`` because it is not a Claude/Codex/
    Cursor/Gemini client at all, and may therefore select only shared skills:
    it has no client packaging format to render a restricted package into.

    A runtime deployment may additionally name the ``repo`` whose environment it
    operates (for example the homelab repository for a homelab runtime); it may
    then also select repo-targeted skills aimed at that repository.
    """

    repo_targets = repo_targets or {}
    deployments = distribution.get("deployments", {})
    if not isinstance(deployments, dict):
        raise SyncError(f"Distribution deployments must be an object: {source}")

    validated: dict[str, dict] = {}
    for name, entry in deployments.items():
        _validate_safe_name(name, "deployment", source)
        if not isinstance(entry, dict):
            raise SyncError(f"Deployment {name!r} must be an object: {source}")
        description = entry.get("description")
        if not isinstance(description, str) or not description.strip():
            raise SyncError(f"Deployment {name!r} has no description: {source}")
        deployment_consumer = entry.get("consumer")
        if deployment_consumer is not None and deployment_consumer not in available_by_consumer:
            raise SyncError(
                f"Deployment {name!r} must name one consumer of "
                f"{sorted(available_by_consumer)}, or omit 'consumer' entirely for "
                f"a non-client runtime that receives only shared skills: {source}"
            )
        deployment_repo = entry.get("repo")
        if deployment_repo is not None:
            _validate_repo_id(deployment_repo, source)
        names = entry.get("skills")
        if not isinstance(names, list) or not names:
            raise SyncError(f"Deployment {name!r} has no skills: {source}")
        available = (
            shared_names
            if deployment_consumer is None
            else available_by_consumer[deployment_consumer]
        )
        if deployment_repo is not None:
            repo_selectable = {
                skill
                for skill, target in repo_targets.items()
                if deployment_repo in target["repos"]
            }
            available = available | repo_selectable
        selected: list[str] = []
        for skill_name in names:
            _validate_safe_name(skill_name, "skill", source)
            if skill_name in selected:
                raise SyncError(
                    f"Deployment {name!r} contains duplicate skill {skill_name!r}: {source}"
                )
            if skill_name not in available:
                if deployment_consumer is None:
                    raise SyncError(
                        f"Deployment {name!r} declares no consumer, so it may only "
                        f"select shared skills; {skill_name!r} is a consumer-restricted "
                        f"package, a repo-targeted skill this deployment's repo does "
                        f"not operate, or is not in the distribution: {source}"
                    )
                raise SyncError(
                    f"Deployment {name!r} skill {skill_name!r} is not active for "
                    f"consumer {deployment_consumer!r}"
                )
            selected.append(skill_name)
        validated[name] = {
            "description": description,
            "consumer": deployment_consumer,
            "repo": deployment_repo,
            "skills": tuple(selected),
        }
    return validated


def load_distribution(
    repo_root: Path,
    consumer: str | None = None,
    *,
    deployment: str | None = None,
    repo: str | None = None,
) -> tuple[Path, str, str | None, str | None, tuple[SkillSource, ...], tuple[str, ...]]:
    """Validate all manifests and load one consumer, deployment, or repo distribution.

    The returned consumer is the one actually selected. It is ``None`` only for
    a runtime deployment, which declares no consumer and receives shared skills
    (plus repo-targeted skills when the deployment declares the repo it operates).

    The returned repo is the selected repository target for a ``--repo`` run.
    The final tuple is the merged MCP template names the selection requires.
    """

    if consumer is not None and consumer not in MANIFEST_PATHS:
        raise SyncError(f"Unknown skill consumer: {consumer!r}")
    if repo is not None and (consumer is not None or deployment is not None):
        raise SyncError(
            "--repo selects a repository's targeted skills on its own; do not "
            "combine it with --consumer or --deployment"
        )

    source_root = (repo_root / "plugins").resolve()
    plugin_root = source_root / "frozen-skills"
    manifests: dict[str, tuple[Path, dict]] = {}
    for manifest_consumer, relative_manifest in MANIFEST_PATHS.items():
        manifest = plugin_root / relative_manifest
        if not manifest.is_file():
            raise SyncError(f"Required manifest is missing: {manifest}")
        data = _load_json(manifest)
        manifests[manifest_consumer] = (manifest, data)

    baseline_manifest, baseline_data = manifests["claude"]
    plugin_name = baseline_data.get("name")
    version = baseline_data.get("version")
    if plugin_name != "frozen-skills" or not isinstance(version, str) or not version:
        raise SyncError(f"Invalid plugin identity or version in {baseline_manifest}")

    for manifest_consumer, (manifest, data) in manifests.items():
        if manifest_consumer == "claude":
            continue
        if data.get("name") != plugin_name:
            raise SyncError(f"Plugin name differs in {manifest}")
        if data.get("version") != version:
            raise SyncError(f"Plugin version differs in {manifest}")

    distribution_path = source_root / DISTRIBUTION_PATH
    distribution = _load_json(distribution_path)
    if (
        distribution.get("schema") != 1
        or distribution.get("plugin") != plugin_name
        or distribution.get("version") != version
    ):
        raise SyncError(
            f"Distribution identity, schema, or version differs in {distribution_path}"
        )
    consumers = distribution.get("consumers")
    if not isinstance(consumers, dict) or set(consumers) != set(MANIFEST_PATHS):
        raise SyncError(
            f"Distribution consumers must be exactly {sorted(MANIFEST_PATHS)}"
        )
    consumer_packages = distribution.get("consumer_packages")
    if (
        not isinstance(consumer_packages, dict)
        or set(consumer_packages) != set(MANIFEST_PATHS)
        or any(not isinstance(packages, list) for packages in consumer_packages.values())
        or any(
            not isinstance(package, str)
            or not SKILL_NAME_PATTERN.fullmatch(package)
            or package == "frozen-skills"
            for packages in consumer_packages.values()
            for package in packages
        )
        or any(
            len(packages) != len(set(packages))
            for packages in consumer_packages.values()
        )
    ):
        raise SyncError(
            "Distribution consumer_packages must map exactly "
            f"{sorted(MANIFEST_PATHS)} to unique safe package-name lists; "
            "'frozen-skills' is reserved for shared skills"
        )

    shared_skills = _skill_entry_set(
        {"skills": distribution.get("shared")}, distribution_path
    )
    for name, relative_path in shared_skills:
        parts = Path(relative_path).parts
        if (
            len(parts) < 3
            or parts[:2] != ("frozen-skills", "skills")
            or ".." in parts
        ):
            raise SyncError(f"Shared skill {name!r} is outside frozen-skills/skills")
    consumer_skills = {
        manifest_consumer: _skill_entry_set(
            {"skills": entries}, distribution_path
        )
        for manifest_consumer, entries in consumers.items()
    }
    for manifest_consumer, entries in consumer_skills.items():
        shared_names = {name for name, _path in shared_skills}
        duplicated = shared_names & {name for name, _path in entries}
        if duplicated:
            raise SyncError(
                f"Consumer {manifest_consumer!r} duplicates shared skills: "
                f"{sorted(duplicated)}"
            )
        allowed_packages = set(consumer_packages[manifest_consumer])
        for name, relative_path in entries:
            parts = Path(relative_path).parts
            if (
                len(parts) < 3
                or parts[0] not in allowed_packages
                or parts[1] != "skills"
                or ".." in parts
            ):
                raise SyncError(
                    f"Consumer {manifest_consumer!r} skill {name!r} is outside its "
                    "declared consumer packages"
                )

    all_distribution_entries = list(shared_skills)
    for entries in consumer_skills.values():
        all_distribution_entries.extend(entries)
    for name, relative_path in all_distribution_entries:
        _resolve_distribution_skill(source_root, name, relative_path)

    shared_names = {name for name, _path in shared_skills}
    lane_names = shared_names | {
        name for entries in consumer_skills.values() for name, _path in entries
    }
    repo_targets = validate_repo_targets(
        distribution, distribution_path, source_root, repo_root, lane_names
    )
    deployments = validate_deployments(
        distribution,
        distribution_path,
        shared_names,
        {
            manifest_consumer: shared_names | {name for name, _path in entries}
            for manifest_consumer, entries in consumer_skills.items()
        },
        repo_targets,
    )

    if deployment is not None:
        selected_deployment = deployments.get(deployment)
        if selected_deployment is None:
            raise SyncError(f"Unknown deployment {deployment!r} in {distribution_path}")
        deployment_consumer = selected_deployment["consumer"]
        if consumer is not None and deployment_consumer is None:
            raise SyncError(
                f"Deployment {deployment!r} declares no consumer because it is not a "
                f"client runtime; do not pass --consumer {consumer!r} with it"
            )
        if consumer is not None and consumer != deployment_consumer:
            raise SyncError(
                f"Deployment {deployment!r} targets consumer "
                f"{deployment_consumer!r}, not the requested {consumer!r}; "
                "a deployment already selects its own consumer"
            )
        consumer = deployment_consumer
    elif consumer is None and repo is None:
        raise SyncError("A consumer, a deployment, or a repo must be selected")

    if repo is not None:
        _validate_repo_id(repo, distribution_path)
        selected_names = [
            name for name, target in repo_targets.items() if repo in target["repos"]
        ]
        if not selected_names:
            raise SyncError(
                f"No repo_targets skills name repository {repo!r} in "
                f"{distribution_path}; nothing to synchronize"
            )
        lane_paths = dict(all_distribution_entries)
        selected_skills = tuple(
            (name, repo_targets[name]["path"] or lane_paths[name])
            for name in selected_names
        )
    elif deployment is not None:
        available_skills = (
            shared_skills if consumer is None else shared_skills + consumer_skills[consumer]
        )
        path_by_name = dict(all_distribution_entries) | dict(available_skills)
        for name, target in repo_targets.items():
            if target["path"] is not None:
                path_by_name.setdefault(name, target["path"])
        selected_skills = tuple(
            (name, path_by_name[name]) for name in deployments[deployment]["skills"]
        )
    else:
        selected_skills = shared_skills + consumer_skills[consumer]

    sources: list[SkillSource] = []
    for name, relative_path in selected_skills:
        candidate = _resolve_distribution_skill(source_root, name, relative_path)
        sources.append(SkillSource(name, candidate, digest_directory(candidate)))

    selected_mcp: tuple[str, ...] = ()
    if repo is not None:
        selected_mcp = tuple(
            dict.fromkeys(
                template
                for name in selected_names
                for template in repo_targets[name]["mcp"]
            )
        )
    elif deployment is not None:
        deployment_repo = deployments[deployment].get("repo")
        if deployment_repo is not None:
            selected_mcp = tuple(
                dict.fromkeys(
                    template
                    for name in deployments[deployment]["skills"]
                    if name in repo_targets
                    for template in repo_targets[name]["mcp"]
                )
            )

    return source_root, version, consumer, repo, tuple(sources), selected_mcp


def _empty_state(
    consumer: str | None, deployment: str | None = None, repo: str | None = None
) -> dict:
    """Return a new empty synchronization management record."""

    state = {
        "schema": STATE_SCHEMA,
        "plugin": "frozen-skills",
        "skills": {},
    }
    if consumer is not None:
        state["consumer"] = consumer
    if deployment is not None:
        state["deployment"] = deployment
    if repo is not None:
        state["repo"] = repo
    return state


def _owner_label(deployment: str | None, repo: str | None = None) -> str:
    """Describe which distribution scope owns a destination."""

    if repo is not None:
        return f"repo {repo!r}"
    if deployment is None:
        return "the full consumer distribution"
    return f"deployment {deployment!r}"


def load_state(
    destination: Path,
    consumer: str | None,
    deployment: str | None = None,
    repo: str | None = None,
) -> dict:
    """Load and validate the destination's management record."""

    path = destination / STATE_FILE
    if not path.exists():
        return _empty_state(consumer, deployment, repo)
    data = _load_json(path)
    if data.get("schema") != STATE_SCHEMA or data.get("plugin") != "frozen-skills":
        raise SyncError(
            f"Unsupported or unrelated sync state: {path}; use a fresh consumer-specific "
            "destination or migrate the state deliberately"
        )
    state_repo = data.get("repo")
    if state_repo is not None:
        _validate_repo_id(state_repo, path)
    state_consumer = data.get("consumer")
    if repo is not None:
        if state_repo != repo or state_consumer is not None:
            raise SyncError(
                f"Destination is managed for {_owner_label(None, state_repo) if state_repo else f'consumer {state_consumer!r}'}, "
                f"not repo {repo!r}: {path}"
            )
    elif state_repo is not None:
        raise SyncError(
            f"Destination is managed for repo {state_repo!r}, not "
            f"{_owner_label(deployment)}: {path}"
        )
    elif state_consumer != consumer:
        raise SyncError(
            f"Destination is managed for consumer {state_consumer!r}, not "
            f"{consumer!r}: {path}"
        )
    state_deployment = data.get("deployment")
    if state_deployment is not None:
        _validate_safe_name(state_deployment, "deployment", path)
    if state_deployment != deployment:
        raise SyncError(
            f"Destination is managed by {_owner_label(state_deployment)}, not "
            f"{_owner_label(deployment)}: {path}; use a separate destination or "
            "deliberately remove the existing managed state"
        )
    if not isinstance(data.get("skills"), dict):
        raise SyncError(f"Invalid skills state in {path}")
    for name, entry in data["skills"].items():
        if not isinstance(name, str):
            raise SyncError(f"Invalid skill name in {path}")
        _validate_skill_name(name, path)
        if not isinstance(entry, dict) or not DIGEST_PATTERN.fullmatch(
            str(entry.get("digest", ""))
        ):
            raise SyncError(f"Invalid digest for skill {name!r} in {path}")
    state_mcp = data.get("mcp")
    if state_mcp is not None and (
        not isinstance(state_mcp, dict)
        or not DIGEST_PATTERN.fullmatch(str(state_mcp.get("digest", "")))
    ):
        raise SyncError(f"Invalid mcp state in {path}")
    return data


def _target_digest(target: Path) -> str | None:
    """Return a destination tree digest, or None when it is absent."""

    is_junction = getattr(os.path, "isjunction", lambda _path: False)
    if target.is_symlink() or is_junction(target):
        raise SyncError(f"Skill destination must be a real directory, not a link: {target}")
    if not target.exists():
        return None
    if not target.is_dir():
        raise SyncError(f"Skill destination is not a directory: {target}")
    return digest_directory(target)


def _validate_direction(repo_root: Path, destination: Path) -> None:
    """Require an outward destination disjoint from the source repository."""

    if destination == repo_root or repo_root in destination.parents:
        raise SyncError("Destination must be outside the frozenSkillz repository")
    if destination in repo_root.parents:
        raise SyncError("Destination must not contain the frozenSkillz repository")
    if destination.exists() and not destination.is_dir():
        raise SyncError(f"Destination must be a directory: {destination}")


def plan_sync(
    sources: tuple[SkillSource, ...],
    destination: Path,
    state: dict,
    *,
    prune: bool,
    force: bool,
    exact: bool = False,
) -> tuple[Action, ...]:
    """Plan safe distribution changes from one observed destination snapshot."""

    actions: list[Action] = []
    recorded = state["skills"]
    active_names = {source.name for source in sources}

    for source in sources:
        target = destination / source.name
        current_digest = _target_digest(target)
        prior_entry = recorded.get(source.name)
        prior_digest = prior_entry.get("digest") if isinstance(prior_entry, dict) else None

        if current_digest == source.digest:
            kind = "current" if prior_digest == source.digest else "adopt"
            detail = "already matches reviewed source"
        elif current_digest is None:
            kind = "install"
            detail = "destination skill is missing"
        elif prior_digest and current_digest == prior_digest:
            kind = "update"
            detail = "managed copy differs from reviewed source"
        elif force:
            kind = "update"
            detail = "overwrite locally modified or unmanaged copy (--force)"
        else:
            kind = "conflict"
            detail = "destination has locally modified or unmanaged content"
        actions.append(Action(kind, source.name, detail, current_digest))

    if prune:
        for name in sorted(set(recorded) - active_names):
            target = destination / name
            current_digest = _target_digest(target)
            prior_entry = recorded.get(name)
            prior_digest = prior_entry.get("digest") if isinstance(prior_entry, dict) else None
            if current_digest is None:
                actions.append(
                    Action("forget", name, "managed skill is already absent", current_digest)
                )
            elif prior_digest and current_digest == prior_digest:
                actions.append(
                    Action(
                        "remove",
                        name,
                        "no longer listed in the selected distribution",
                        current_digest,
                    )
                )
            elif force:
                actions.append(
                    Action(
                        "remove",
                        name,
                        "remove locally modified retired skill (--force)",
                        current_digest,
                    )
                )
            else:
                actions.append(
                    Action(
                        "conflict",
                        name,
                        "retired managed skill has local modifications",
                        current_digest,
                    )
                )

    if exact and destination.is_dir():
        known_names = active_names | set(recorded) | {STATE_FILE, MCP_ARTIFACT_NAME}
        for entry in sorted(destination.iterdir(), key=lambda item: item.name):
            if entry.name not in known_names:
                actions.append(
                    Action(
                        "conflict",
                        entry.name,
                        "deployment destination contains unmanaged content",
                    )
                )

    return tuple(actions)


def _remove_path(path: Path) -> None:
    """Remove one explicitly selected file, link, or directory tree."""

    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def _replace_directory(
    source: Path,
    target: Path,
    expected_source_digest: str,
    observed_target_digest: str | None,
) -> None:
    """Stage and replace one skill while preserving a failed rollback backup."""

    target.parent.mkdir(parents=True, exist_ok=True)
    nonce = uuid.uuid4().hex
    staged = target.parent / f".{target.name}.frozen-skills-stage-{nonce}"
    backup = target.parent / f".{target.name}.frozen-skills-backup-{nonce}"
    try:
        shutil.copytree(
            source,
            staged,
            ignore=shutil.ignore_patterns(".DS_Store", "Thumbs.db", "__pycache__", "*.pyc", "*.pyo"),
        )
        staged_digest = digest_directory(staged)
        if staged_digest != expected_source_digest:
            raise SyncError(
                f"Reviewed source changed while staging {source}; rerun synchronization"
            )
        current_target_digest = _target_digest(target)
        if current_target_digest != observed_target_digest:
            raise TargetChangedError(target, current_target_digest)
        if target.exists():
            os.replace(target, backup)
        os.replace(staged, target)
        _remove_path(backup)
    except Exception:
        if backup.exists() and not target.exists():
            try:
                os.replace(backup, target)
            except Exception as restore_error:
                raise SyncError(
                    f"Replacing {target} failed and rollback also failed; "
                    f"the original copy is preserved at {backup}"
                ) from restore_error
        raise
    finally:
        _remove_path(staged)


def _write_state(destination: Path, state: dict) -> None:
    """Atomically write the synchronization management record."""

    destination.mkdir(parents=True, exist_ok=True)
    target = destination / STATE_FILE
    staged = destination / f".{STATE_FILE}.{uuid.uuid4().hex}.tmp"
    try:
        with staged.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(state, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(staged, target)
    finally:
        if staged.exists():
            staged.unlink()


def _write_json_atomic(path: Path, document: dict) -> None:
    """Atomically write one JSON document with deterministic formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    staged = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    try:
        with staged.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(document, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(staged, path)
    finally:
        if staged.exists():
            staged.unlink()


def _mcp_document(repo_root: Path, template_names: tuple[str, ...]) -> dict:
    """Merge named mcp/<name>.json templates into one mcpServers document."""

    servers: dict = {}
    for name in template_names:
        template = _load_json(repo_root / MCP_TEMPLATES_ROOT / f"{name}.json")
        servers.update(template.get("mcpServers", {}))
    return {"mcpServers": servers}


def _canonical_digest(document: dict) -> str:
    """Digest a JSON document in canonical form for drift comparison."""

    canonical = json.dumps(document, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _mcp_artifact_digest(path: Path) -> str | None:
    """Digest an existing MCP artifact's parsed content, or None when absent."""

    if not path.exists():
        return None
    if not path.is_file():
        raise SyncError(f"MCP artifact destination is not a file: {path}")
    try:
        document = _load_json(path)
    except SyncError:
        # Unparseable project content is a conflict, not a digest.
        return "unparseable"
    return _canonical_digest(document)


def sync(
    repo_root: Path,
    destination: Path,
    *,
    consumer: str | None = None,
    apply: bool,
    prune: bool,
    force: bool,
    deployment: str | None = None,
    repo: str | None = None,
) -> SyncResult:
    """Check or apply one consumer, deployment, or repo distribution to one skill root."""

    repo_root = repo_root.resolve()
    destination = destination.resolve()
    _validate_direction(repo_root, destination)
    if deployment is not None and not prune:
        raise SyncError(
            "Deployment synchronization requires --prune so the destination "
            "converges to the exact deployment"
        )
    source_root, version, consumer, repo, sources, mcp_templates = load_distribution(
        repo_root, consumer, deployment=deployment, repo=repo
    )
    state = load_state(destination, consumer, deployment, repo)
    actions = list(
        plan_sync(
            sources,
            destination,
            state,
            prune=prune,
            force=force,
            exact=deployment is not None,
        )
    )
    if state["skills"] and state.get("plugin_version") != version:
        actions.append(
            Action(
                "state",
                "frozen-skills",
                "management record plugin version differs",
            )
        )

    mcp_document = (
        _mcp_document(repo_root, mcp_templates) if mcp_templates else None
    )
    mcp_target = destination / MCP_ARTIFACT_NAME
    mcp_digest = _canonical_digest(mcp_document) if mcp_document is not None else None
    recorded_mcp = state.get("mcp")
    recorded_mcp_digest = (
        recorded_mcp.get("digest") if isinstance(recorded_mcp, dict) else None
    )
    current_mcp_digest = _mcp_artifact_digest(mcp_target)
    if mcp_digest is not None:
        if current_mcp_digest == mcp_digest:
            mcp_kind = "current" if recorded_mcp_digest == mcp_digest else "adopt"
            mcp_detail = "MCP artifact already matches reviewed templates"
        elif current_mcp_digest is None:
            mcp_kind = "install"
            mcp_detail = "MCP artifact is missing"
        elif recorded_mcp_digest and current_mcp_digest == recorded_mcp_digest:
            mcp_kind = "update"
            mcp_detail = "managed MCP artifact differs from reviewed templates"
        elif force:
            mcp_kind = "update"
            mcp_detail = "overwrite locally modified MCP artifact (--force)"
        else:
            mcp_kind = "conflict"
            mcp_detail = "MCP artifact has locally modified or unmanaged content"
        actions.append(Action(mcp_kind, MCP_ARTIFACT_NAME, mcp_detail, current_mcp_digest))
    elif recorded_mcp_digest and prune:
        if current_mcp_digest is None:
            actions.append(
                Action("forget", MCP_ARTIFACT_NAME, "managed MCP artifact is already absent", None)
            )
        elif current_mcp_digest == recorded_mcp_digest or force:
            actions.append(
                Action(
                    "remove",
                    MCP_ARTIFACT_NAME,
                    "no MCP templates are targeted at this selection",
                    current_mcp_digest,
                )
            )
        else:
            actions.append(
                Action(
                    "conflict",
                    MCP_ARTIFACT_NAME,
                    "retired managed MCP artifact has local modifications",
                    current_mcp_digest,
                )
            )

    result = SyncResult(tuple(actions))

    if not apply or result.conflicts:
        return result

    source_by_name = {source.name: source for source in sources}
    for action in actions:
        if action.kind == "state":
            continue
        if action.name == MCP_ARTIFACT_NAME:
            if action.kind in {"install", "update", "adopt"}:
                if mcp_document is not None and action.kind != "adopt":
                    _write_json_atomic(mcp_target, mcp_document)
            elif action.kind == "remove":
                _remove_path(mcp_target)
            continue
        target = destination / action.name
        if action.kind in {"install", "update"}:
            source = source_by_name[action.name]
            try:
                _replace_directory(
                    source.path,
                    target,
                    source.digest,
                    action.observed_digest,
                )
            except TargetChangedError as exc:
                return SyncResult(
                    tuple(actions)
                    + (
                        Action(
                            "conflict",
                            action.name,
                            "destination changed after the synchronization plan was created; rerun",
                            exc.current_digest,
                        ),
                    )
                )
        elif action.kind == "remove":
            current_digest = _target_digest(target)
            if current_digest != action.observed_digest:
                return SyncResult(
                    tuple(actions)
                    + (
                        Action(
                            "conflict",
                            action.name,
                            "destination changed after the synchronization plan was created; rerun",
                            current_digest,
                        ),
                    )
                )
            _remove_path(target)
        else:
            current_digest = _target_digest(target)
            if current_digest != action.observed_digest:
                return SyncResult(
                    tuple(actions)
                    + (
                        Action(
                            "conflict",
                            action.name,
                            "destination changed after the synchronization plan was created; rerun",
                            current_digest,
                        ),
                    )
                )

    for source in sources:
        current_digest = _target_digest(destination / source.name)
        if current_digest != source.digest:
            return SyncResult(
                tuple(actions)
                + (
                    Action(
                        "conflict",
                        source.name,
                        "destination changed before synchronization state was recorded; rerun",
                        current_digest,
                    ),
                )
            )
    if prune:
        for action in actions:
            if action.kind not in {"remove", "forget"}:
                continue
            current_digest = _target_digest(destination / action.name)
            if current_digest is not None:
                return SyncResult(
                    tuple(actions)
                    + (
                        Action(
                            "conflict",
                            action.name,
                            "retired destination reappeared before state was recorded; rerun",
                            current_digest,
                        ),
                    )
                )

    next_skills = dict(state["skills"])
    for source in sources:
        next_skills[source.name] = {
            "digest": source.digest,
            "source": source.path.relative_to(source_root).as_posix(),
        }
    if prune:
        for name in set(next_skills) - set(source_by_name):
            del next_skills[name]

    next_state = {
        "schema": STATE_SCHEMA,
        "plugin": "frozen-skills",
        "plugin_version": version,
        "skills": next_skills,
    }
    if consumer is not None:
        next_state["consumer"] = consumer
    if deployment is not None:
        next_state["deployment"] = deployment
    if repo is not None:
        next_state["repo"] = repo
    if mcp_digest is not None:
        next_state["mcp"] = {"digest": mcp_digest}
    _write_state(destination, next_state)
    return result


def _expanded_path(value: str) -> Path:
    """Expand user and environment markers in a command-line path."""

    return Path(os.path.expandvars(os.path.expanduser(value)))


def resolve_destination(consumer: str, destination: Path | None) -> Path:
    """Resolve an explicit destination or one verified consumer-private default."""

    if destination is not None:
        return destination
    default = DEFAULT_DESTINATIONS.get(consumer)
    if default is None:
        raise SyncError(
            f"--destination is required for consumer {consumer!r}; no private default "
            "has been qualified"
        )
    return _expanded_path(default)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Synchronize one consumer's frozen-skills distribution, or one named "
            "deployment subset of it, into a local skill root. The command refuses "
            "to overwrite local changes unless --force is supplied."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="report drift without writing")
    mode.add_argument("--apply", action="store_true", help="apply the synchronization plan")
    parser.add_argument(
        "--consumer",
        choices=tuple(MANIFEST_PATHS),
        help="consumer whose exact shared-plus-restricted distribution should be synchronized",
    )
    parser.add_argument(
        "--deployment",
        help=(
            "named deployment subset from plugins/distribution.json:deployments; "
            "supplies its own consumer (or none, for a shared-only runtime) and "
            "requires explicit --destination and --prune"
        ),
    )
    parser.add_argument(
        "--repo",
        help=(
            "repository identifier (owner/repo) whose repo_targets skills and MCP "
            "templates should be synchronized into a project skill root; requires "
            "explicit --destination and does not combine with --consumer/--deployment"
        ),
    )
    parser.add_argument(
        "--destination",
        type=_expanded_path,
        help=(
            "local skill root (Codex default: ~/.codex/skills; required otherwise "
            "and always required with --deployment)"
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=_expanded_path,
        default=Path(__file__).resolve().parent.parent,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help=(
            "remove previously managed skills no longer listed in the selected "
            "distribution or deployment"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite conflicting local content (use only after reviewing the plan)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the synchronizer and return its documented process status."""

    args = build_parser().parse_args(argv)
    try:
        if args.repo is not None:
            if args.consumer is not None or args.deployment is not None:
                raise SyncError(
                    "--repo does not combine with --consumer or --deployment; a "
                    "repository sync selects its own targeted skill set"
                )
            if args.destination is None:
                raise SyncError(
                    "--repo requires an explicit --destination (the project's skill "
                    "root); there is no default repository destination"
                )
            destination = args.destination
        elif args.deployment is not None:
            if args.destination is None:
                raise SyncError(
                    "--deployment requires an explicit --destination; there is no "
                    "default deployment destination"
                )
            if not args.prune:
                raise SyncError(
                    "--deployment requires --prune so the destination converges to "
                    "the exact deployment"
                )
            destination = args.destination
        elif args.consumer is None:
            raise SyncError("One of --consumer, --deployment, or --repo is required")
        else:
            destination = resolve_destination(args.consumer, args.destination)
        result = sync(
            args.repo_root,
            destination,
            consumer=args.consumer,
            apply=args.apply,
            prune=args.prune,
            force=args.force,
            deployment=args.deployment,
            repo=args.repo,
        )
    except SyncError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for action in result.actions:
        print(f"{action.kind.upper():8} {action.name}: {action.detail}")

    if result.conflicts:
        print("Synchronization refused because conflicts require review.", file=sys.stderr)
        return 2
    if args.check and result.changes:
        print("Local skills differ from the reviewed frozen-skills distribution.")
        return 1
    if args.apply:
        selection = (
            f"deployment {args.deployment}"
            if args.deployment is not None
            else f"repo {args.repo} skills"
            if args.repo is not None
            else f"{args.consumer} skills"
        )
        print(f"Synchronized {selection} into {destination.resolve()}")
    else:
        print("Local skills match the reviewed frozen-skills distribution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
