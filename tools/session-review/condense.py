"""Condense AgentsView sessions into reviewer input-contract JSON.

Selects skill-firing sessions (tagged skill_name plus the codex SKILL.md-read
channel), builds one trajectory JSON per session sized for a single judge call.
Besides the conversation evidence, extracts artifact grounding: commits made in
the session's repo during its time window, verification-execution signals, and
aftermath (later commits touching the same files) so the judge can detect quiet
poor implementations, not just owner sentiment.

Usage:
  python condense.py --sessions "id1,id2"        # explicit (calibration)
  python condense.py --new --cap 12              # ungraded skill-firing sessions, newest first
"""
import argparse
import json
import re
import sqlite3
import subprocess
from pathlib import Path

import skill_versions

DB = Path.home() / ".agentsview" / "sessions.db"
HERE = Path(__file__).parent
WORK = HERE / ".work"
STATE = HERE / "state.json"

LOOP_REPROMPT = "Briefly inform the user about the task result"
CLAIM_RE = re.compile(r"\b(done|completed?|passed|merged|landed|fixed|green|success)\b", re.I)
OFFLINE_RE = re.compile(r"\boffline\b|MCP.{0,20}down|\bunavailable\b|\bquota\b|rate.?limit", re.I)
CODEX_SKILL_RE = re.compile(r"skills[\\/]([^\\/\"']+)[\\/]SKILL\.md")
VERIFY_RE = re.compile(r"\btest|pytest|runTests|npm (?:test|run)|dotnet test|cargo (?:test|check)|"
                       r"go test|tsc\b|lint|build|compile|batchmode", re.I)
EDIT_TOOLS = {"Edit", "Write", "StrReplace", "NotebookEdit", "edit_block", "apply_patch"}
AFTERMATH_FLAG_RE = re.compile(r"\brevert|\bfix|\bredo\b|rewrite|broken|hotfix", re.I)


def clip(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + " …[truncated]"


def run_git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                           timeout=20, encoding="utf-8", errors="replace")
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def skill_fires(cx, sid, agent):
    fires = {}
    for (name,) in cx.execute(
            "SELECT DISTINCT skill_name FROM tool_calls WHERE session_id=? AND skill_name IS NOT NULL", (sid,)):
        fires.setdefault(name, "tagged")
    if agent == "codex":
        for (ij,) in cx.execute(
                "SELECT input_json FROM tool_calls WHERE session_id=? AND input_json LIKE '%SKILL.md%'", (sid,)):
            for m in CODEX_SKILL_RE.finditer((ij or "").replace("\\\\", "\\")):
                fires.setdefault(m.group(1), "skillmd-read")
    return [{"name": n, "channel": ch, "version_hash": skill_versions.current_hash(n)}
            for n, ch in sorted(fires.items())]


def verification_signals(cx, sid):
    """Ordering of edits vs verification executions, from tool calls."""
    rows = cx.execute(
        "SELECT m.ordinal, tc.category, tc.tool_name, substr(COALESCE(tc.input_json,''),1,400)"
        " FROM tool_calls tc JOIN messages m ON m.id = tc.message_id"
        " WHERE tc.session_id=? ORDER BY m.ordinal", (sid,)).fetchall()
    last_edit = None
    verify_ordinals = []
    for ordn, cat, tool, inp in rows:
        if cat in EDIT_TOOLS or tool in EDIT_TOOLS:
            last_edit = ordn
        elif VERIFY_RE.search(inp):
            verify_ordinals.append(ordn)
    return {
        "edits": last_edit is not None,
        "last_edit_ordinal": last_edit,
        "verify_exec_count": len(verify_ordinals),
        "verify_exec_after_last_edit": (any(o >= last_edit for o in verify_ordinals)
                                        if last_edit is not None else None),
    }


def artifacts_and_aftermath(cwd, started, ended):
    """Commits landed in the session's repo during its window, plus what happened
    to those files afterward. Best-effort; None when cwd isn't a readable repo."""
    if not cwd:
        return None
    repo = cwd.replace("/", "\\")
    if run_git(repo, "rev-parse", "--is-inside-work-tree") != "true":
        return None
    since = (started or "")[:19]
    if not since:
        return None
    args = ["log", "--all", f"--since={since}", "--format=%h|%s"]
    if ended:
        args.insert(2, f"--until={ended[:19]}")
    log = run_git(repo, *args)
    commits = []
    for line in (log or "").splitlines()[:8]:
        sha, _, subj = line.partition("|")
        files = (run_git(repo, "show", "--name-only", "--format=", sha) or "").splitlines()
        later = run_git(repo, "log", f"{sha}..HEAD", "--format=%h|%s", "--", *files[:20]) if files else ""
        later_lines = (later or "").splitlines()[:10]
        commits.append({
            "sha": sha, "subject": clip(subj, 100),
            "files": files[:15],
            "later_commits_touching_same_files": [clip(l, 110) for l in later_lines],
            "aftermath_flags": [clip(l, 110) for l in later_lines if AFTERMATH_FLAG_RE.search(l)],
        })
    return {"repo": repo, "session_commits": commits}


def condense(cx, sid):
    srow = cx.execute(
        "SELECT agent, started_at, ended_at, cwd, message_count, tool_failure_signal_count,"
        " edit_churn_count, health_score, is_automated FROM sessions WHERE id=?", (sid,)).fetchone()
    if not srow:
        return None
    agent, started, ended, cwd, msgs, fails, churn, health, automated = srow

    rows = cx.execute(
        "SELECT ordinal, role, content FROM messages WHERE session_id=? AND role IN ('user','assistant')"
        " AND content IS NOT NULL AND length(content) > 0 ORDER BY ordinal", (sid,)).fetchall()

    user_msgs, claims, offline_hits, opening = [], [], 0, None
    for ordn, role, content in rows:
        if role == "user":
            if content.startswith("<"):
                continue
            if LOOP_REPROMPT in content:
                user_msgs.append({"ordinal": ordn, "text": "[loop-reprompt]"})
                continue
            entry = {"ordinal": ordn, "text": clip(content, 280)}
            if opening is None:
                opening = clip(content, 800)
            user_msgs.append(entry)
        else:
            if OFFLINE_RE.search(content):
                offline_hits += 1
            if CLAIM_RE.search(content) and len(claims) < 8:
                claims.append({"ordinal": ordn, "text": clip(content, 300)})
    if len(user_msgs) > 40:
        user_msgs = user_msgs[:20] + [{"ordinal": -1, "text": f"[…{len(user_msgs)-40} messages elided…]"}] + user_msgs[-20:]

    closing = [{"ordinal": o, "role": r, "text": clip(c, 500)} for o, r, c in rows[-10:]]
    (ncalls,) = cx.execute("SELECT COUNT(*) FROM tool_calls WHERE session_id=?", (sid,)).fetchone()

    return {
        "session_id": sid, "agent": agent, "date": (started or "")[:10], "cwd": cwd or "",
        "is_automated": bool(automated),
        "opening_ask": opening or "[no genuine user message found]",
        "user_messages": user_msgs,
        "assistant_claims": claims,
        "closing_window": closing,
        "tool_stats": {"messages": msgs, "tool_calls": ncalls, "tool_failures": fails,
                       "edit_churn": churn, "agentsview_health_thrash_score": health},
        "skills_fired": skill_fires(cx, sid, agent),
        "resource_flags": {"offline_or_quota_mentions": offline_hits},
        "verification_signals": verification_signals(cx, sid),
        "artifacts": artifacts_and_aftermath(cwd, started, ended),
    }


def pick_new(cx, cap, graded):
    ids = [r[0] for r in cx.execute(
        "SELECT DISTINCT s.id FROM sessions s JOIN tool_calls tc ON tc.session_id = s.id"
        " WHERE (tc.skill_name IS NOT NULL OR (s.agent='codex' AND tc.input_json LIKE '%SKILL.md%'))"
        " AND s.ended_at IS NOT NULL ORDER BY s.started_at DESC")]
    return [i for i in ids if i not in graded][:cap]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions")
    ap.add_argument("--new", action="store_true")
    ap.add_argument("--cap", type=int, default=12)
    args = ap.parse_args()

    state = json.loads(STATE.read_text()) if STATE.exists() else {"graded": {}}
    cx = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    ids = ([s.strip() for s in args.sessions.split(",") if s.strip()] if args.sessions
           else pick_new(cx, args.cap, state["graded"]))

    WORK.mkdir(exist_ok=True)
    out = []
    for sid in ids:
        t = condense(cx, sid)
        if t is None:
            print(f"skip (not found): {sid}")
            continue
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", sid)
        p = WORK / f"{safe}.json"
        p.write_text(json.dumps(t, indent=1), encoding="utf-8")
        out.append(str(p))
        print(p)
    if not out:
        print("nothing to grade")


if __name__ == "__main__":
    main()
