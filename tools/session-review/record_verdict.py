"""Validate and record one reviewer verdict.

Usage: python record_verdict.py <verdict.json>

Schema-checks the verdict, appends it to grades/YYYY-MM.jsonl, marks the session
graded in state.json, and appends any mutation candidate to proposals.md.
Exits non-zero with a reason on validation failure — nothing is written then.
"""
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
ENUMS = {
    "goal_reached": {"yes", "partial", "no", "insufficient"},
    "closing_sentiment": {"accepted", "neutral", "corrected", "frustrated", "abandoned"},
}
LEVELS = {"none", "some", "severe"}
IMPL_LEVELS = {"sound", "questionable", "poor", "not_inspectable"}
AFTERMATH_LEVELS = {"survived", "churned", "reverted", "too_recent", "none"}
EFFECTS = {"shaped", "ignored", "hurt", "meta"}
REQUIRED = ["rubric_version", "session_id", "goal", "goal_reached", "owner_visible_outcome",
            "closing_sentiment", "thrash", "ceremony", "skills", "pushback",
            "implementation_quality", "aftermath", "claims_gap", "verdict", "confidence"]


def fail(msg):
    print(f"INVALID: {msg}")
    sys.exit(1)


def main(path):
    v = json.loads(Path(path).read_text(encoding="utf-8"))
    for k in REQUIRED:
        if k not in v:
            fail(f"missing key {k}")
    for k, allowed in ENUMS.items():
        if v[k] not in allowed:
            fail(f"{k}={v[k]!r} not in {sorted(allowed)}")
    for k in ("thrash", "ceremony"):
        if not isinstance(v[k], dict) or v[k].get("level") not in LEVELS:
            fail(f"{k} needs {{level: none|some|severe, evidence}}")
    if not isinstance(v["skills"], list):
        fail("skills must be a list")
    if v["implementation_quality"].get("level") not in IMPL_LEVELS:
        fail("implementation_quality.level invalid")
    if v["aftermath"].get("level") not in AFTERMATH_LEVELS:
        fail("aftermath.level invalid")
    if v["claims_gap"].get("level") not in LEVELS:
        fail("claims_gap.level invalid")
    pb = v["pushback"]
    if not isinstance(pb, dict) or not isinstance(pb.get("count"), int):
        fail('pushback needs {count: int, worst: quote|null}')
    if pb["count"] > 0 and not pb.get("worst"):
        fail("pushback count > 0 requires the worst quote")
    for s in v["skills"]:
        if s.get("effect") not in EFFECTS:
            fail(f"skill {s.get('name')} effect={s.get('effect')!r} invalid")
        if not s.get("evidence"):
            fail(f"skill {s.get('name')} has no evidence quote")

    grades_dir = HERE / "grades"
    grades_dir.mkdir(exist_ok=True)
    v["graded_at"] = date.today().isoformat()
    with (grades_dir / f"{date.today():%Y-%m}.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(v, ensure_ascii=False) + "\n")

    state_path = HERE / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {"graded": {}}
    state["graded"][v["session_id"]] = v["graded_at"]
    state_path.write_text(json.dumps(state, indent=1))

    if v.get("mutation_candidate"):
        skills = ", ".join(s["name"] for s in v["skills"]) or "none"
        with (HERE / "proposals.md").open("a", encoding="utf-8") as fh:
            fh.write(f"\n## {v['session_id']} ({v['graded_at']})\n\n"
                     f"Skills in session: {skills}\n\n{v['mutation_candidate']}\n")
    print(f"recorded {v['session_id']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: record_verdict.py <verdict.json>")
    main(sys.argv[1])
