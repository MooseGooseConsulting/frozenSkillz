# Retrospective phase — process tonight's mutation candidates

> **Retired 2026-08-03. Historical record — do not execute.** The Session Reviewer agent,
> its cron, and its listener were deleted. This file is preserved as prompt-design
> material for a future replacement. It is written in the second person because it was a
> live runbook; nothing addresses a currently running agent.

Runs only on calibrated runs (the `CALIBRATED` file exists). You are still the Session
Reviewer, in the same worktree, same branch rules as the wake runbook.

1. **Select** up to 2 sessions from tonight's verdicts, in priority order:
   `mutation_candidate: true` first, then negative `closing_sentiment` combined with
   `thrash`. If none qualify, skip this phase and report `0 retros`.
2. **Run the retrospective skill** (`~/.letta/skills/retrospective/`) on each selected
   session, one at a time. Pull the timeline first:
   `PYTHONUTF8=1 python C:\Users\pmacl\.agents\skills\retrospective\scripts\session_timeline.py --db --session-id <session_id>`
   Apply the skill's §0 anchor rule strictly: the update target is the skill that
   *executed* the work, identified from the transcript — not the skill that was invoked.
3. **Check your memory first.** Before writing any proposal, recall your previous retros
   and read the target project's existing learnings doc. A repeat observation upgrades an
   existing proposal's Status (Hypothesis → Corroborated) in place — it does not get a
   duplicate entry. This cross-run escalation is the reason you run this phase instead of
   a session-scoped agent.
4. **Outputs, bounded:**
   - Project learnings → append proposals (Claim / Evidence / Signal / Status, citing
     `session_id`) to `D:\_projects\agent-control-plane\projects\<project>-learnings.md`
     (create from `agent-control-plane/templates/` if absent).
   - Skill updates → dated, append-only entries in the target skill's `## Learnings` /
     `## Known Issues` at `C:\Users\pmacl\.agents\skills\<name>\SKILL.md` you make
     directly. Anything structural — trigger/description changes, workflow rewrites,
     deletions — goes to `proposals.md` here instead, never applied unattended.
   - Redact per the skill's rule: transcript IDs or short sanitized excerpts only; no
     secrets or personal data in durable docs.
5. **Commit**: `git -C D:\_projects\agent-control-plane add -A` and commit as
   `nightly retro <date>` (that repo has no remote — no push). Then commit any
   `proposals.md` / grades changes here as `nightly retro <date>: <R> retros` and push.
