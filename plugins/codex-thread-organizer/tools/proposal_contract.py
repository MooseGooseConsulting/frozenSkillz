"""Deterministic contract checks for organizer fixture proposals.

This deliberately does not pretend to summarize conversations with heuristics.
The skill requires agents to read bodies.  The helper verifies that a proposed
read-only batch preserves the required evidence and cannot silently emit titles
outside the cross-client conservative limit.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


REQUIRED_RECORD_FIELDS = {
    "id",
    "current_title",
    "current_project",
    "updated_at",
    "subject_summary",
    "decisions_outcomes",
    "important_artifacts",
    "unresolved_questions",
    "related_ids",
    "proposed_title",
    "proposed_project",
    "confidence",
    "evidence",
    "relationships",
}
RELATIONSHIPS = {
    "continues",
    "supersedes",
    "duplicates",
    "corrects",
    "related",
    "independent",
}
MAX_UTF16_UNITS = 60
PREVIEW_EMOJI = {"🫫", "🫹", "🫺", "🫌", "🫝", "🛙", "🪋", "🪌", "🪍"}


def utf16_units(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def validate_read_only_batch(batch: dict[str, Any]) -> dict[str, int]:
    """Validate a fully analyzed organizer proposal fixture.

    Raises ValueError with the exact invalid record rather than coercing or
    guessing.  This mirrors the skill's fail-closed treatment of unreadable
    bodies and unconfirmed preview emoji.
    """

    records = batch["records"]
    ids = {record["id"] for record in records}
    if len(ids) != len(records):
        raise ValueError("conversation IDs must be unique")
    relationship_count = 0
    changed_titles = 0
    unreadable = 0
    for record in records:
        missing = REQUIRED_RECORD_FIELDS - set(record)
        if missing:
            raise ValueError(f"{record.get('id', '<missing>')}: missing {sorted(missing)}")
        if not 0 <= record["confidence"] <= 1:
            raise ValueError(f"{record['id']}: confidence must be between zero and one")
        if record.get("acquisition") == "unreadable":
            unreadable += 1
            forbidden = ("proposed_title", "proposed_project", "preview_emoji", "emoji_reason", "collision_checked", "proposal_revision")
            if record["relationships"] or any(record.get(key) is not None for key in forbidden):
                raise ValueError(f"{record['id']}: unreadable body must not receive body-derived proposals or relationships")
            continue
        if not record["subject_summary"] or not record["evidence"]:
            raise ValueError(f"{record['id']}: body-derived summary and evidence are required")
        title = record["proposed_title"]
        if not title or utf16_units(title) > MAX_UTF16_UNITS:
            raise ValueError(f"{record['id']}: title is missing or exceeds {MAX_UTF16_UNITS} UTF-16 units")
        if title != record["current_title"]:
            changed_titles += 1
        preview_characters = PREVIEW_EMOJI.intersection(title)
        preview = record.get("preview_emoji")
        if preview_characters:
            if not isinstance(preview, dict) or preview.get("value") not in preview_characters or not preview.get("chrome_rendering_confirmed"):
                raise ValueError(f"{record['id']}: preview emoji lacks matching Chrome rendering proof")
        elif preview is not None:
            raise ValueError(f"{record['id']}: preview emoji metadata does not match the proposed title")
        relationships = record["relationships"]
        if not isinstance(relationships, list):
            raise ValueError(f"{record['id']}: relationships must be a list")
        for relation in relationships:
            if not isinstance(relation, dict):
                raise ValueError(f"{record['id']}: relationship must be an object")
            relationship_count += 1
            if relation.get("kind") not in RELATIONSHIPS:
                raise ValueError(f"{record['id']}: unsupported relationship")
            if relation.get("target_id") not in ids:
                raise ValueError(f"{record['id']}: relationship target is absent")
            if not relation.get("evidence"):
                raise ValueError(f"{record['id']}: relationship lacks evidence")
    return {
        "records": len(records),
        "relationships": relationship_count,
        "changed_titles": changed_titles,
        "unreadable": unreadable,
    }


def grade(batch: dict[str, Any]) -> dict[str, float]:
    """Return visible proposal-rubric scores, not hidden reasoning."""

    validate_read_only_batch(batch)
    records = batch["records"]
    readable = [item for item in records if item.get("acquisition") != "unreadable"]
    if not readable:
        return {"body_coverage": 0.0, "title_specificity": 0.0, "cluster_cohesion": 0.0, "emoji_fit": 0.0, "relationship_confidence": 0.0, "collision_risk": 0.0}
    relation_kinds = Counter(
        relation["kind"] for item in readable for relation in item["relationships"]
    )
    return {
        "body_coverage": len(readable) / len(records),
        "title_specificity": sum(bool(item["proposed_title"]) for item in readable) / len(readable),
        "cluster_cohesion": 1.0 if relation_kinds["related"] else 0.0,
        "emoji_fit": 1.0 if all("emoji_reason" in item for item in readable) else 0.0,
        "relationship_confidence": sum(item["confidence"] for item in readable) / len(readable),
        "collision_risk": sum(bool(item.get("collision_checked")) for item in readable) / len(readable),
    }
