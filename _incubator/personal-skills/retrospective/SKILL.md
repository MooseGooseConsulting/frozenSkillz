---
name: retrospective
description: Run a session retrospective to capture learnings, failures, and updates to relevant skills
metadata:
  author: pmacl
  version: "0.2.0"
  argument-hint: <optional session focus>
---

# Retrospective

Session retrospective for continual learning. Reviews conversation, extracts learnings, updates skills.

## When to Use

Run at end of coding sessions to capture learnings before context is lost. Invoke via `/retrospective` or when user says "let's do a retro".

## Triggering

The previous Letta Session Reviewer automation was decommissioned on 2026-08-03. This skill
is manually invocable (`/retrospective`) until an owner-configured replacement is created in
Letta. No Letta agent is currently discovery-wired through `~/.letta/skills/retrospective`.

## Process

### 0. Anchor the Target Skill — the skill that *ran the work*, found from the transcript

**Core principle.** The enhancement target is the skill that actually *executed*
the workflow you're retrospecting — **identified by reading the transcript** — not
the skill invoked to start the retro. The trigger skill (e.g. `/retrospective`)
is just the lens; it usually did none of the work. Pull the session timeline
(`scripts/session_timeline.py`), see which skill the agent actually used, and make
that your target.

**Worked example (this session, 2026-07-06).** A `/retrospective` was run on a
praised artifact hunt. Two agents in a row "improved" the `retrospective` skill
*because it was invoked* — both wrong. The transcript showed the hunt ran on
`chat-history` ("Using chat-history to search…"), so the good patterns and tooling
belonged there and went there. `/retrospective` only supplied the lens.

**Corollaries.**
- **Don't inherit a prior retro's target-selection.** Re-derive it from the
  transcript; the earlier conclusion (even a previous retrospective's) is the
  thing most likely to be wrong.
- A retrospective *may* also improve its own method — but only when the
  retrospective *process* is what exhibited the lesson, not by default.
- Distill one sharp principle per lesson; correct in place rather than appending.

When enhancing an existing skill, edit its folder directly and validate before
reporting completion.

### 1. Session Analysis

Review the entire conversation and identify:

**Successes**
- What worked well
- Effective approaches discovered
- Useful patterns or techniques
- Tools/commands that solved problems

**Failures**
- What didn't work
- Dead ends encountered
- Errors and their root causes
- Approaches to avoid

**Discoveries**
- New insights about the codebase
- Unexpected behaviors
- Configuration quirks
- Edge cases found

Use the bundled timeline helper before synthesizing a session. The `--db` mode
reads the AgentsView archive (`~\.agentsview\sessions.db`, read-only) and covers
every harness it ingests — claude, codex, cursor, opencode, kilo, gemini, and the
rest — so start there:

```powershell
$env:PYTHONUTF8='1'
# Find sessions containing an exact phrase (lists agent / project / date / id):
python "$HOME\.agents\skills\retrospective\scripts\session_timeline.py" `
  --db --find "exact user phrase from the session"

# Emit the timeline for one of the matches:
python "$HOME\.agents\skills\retrospective\scripts\session_timeline.py" `
  --db --session-id SESSION_ID --format markdown
```

The original codex-JSONL mode still works for rollout files AgentsView has not
ingested yet, or when you need the raw event stream:

```powershell
python "$HOME\.agents\skills\retrospective\scripts\session_timeline.py" `
  --find "exact user phrase from the session" `
  --format markdown

python "$HOME\.agents\skills\retrospective\scripts\session_timeline.py" `
  --session "C:\Users\pmacl\.codex\sessions\YYYY\MM\DD\rollout-SESSION.jsonl" `
  --format jsonl
```

Keep tool outputs disabled unless the output itself is evidence; they are often
large and can obscure the actual decision sequence.

### 1.5. Parallelization And Tooling Pass

For retrospectives about a workflow, explicitly identify:

- Which work could have run in parallel.
- Which steps were dependent and should remain sequential.
- Which repeated ad hoc commands should become deterministic scripts.
- Which skill owns each improvement.
- Which external agents or non-Codex tools could collect evidence safely.

Use subagents when available and the review surfaces are independent. Assign
each subagent one perspective, such as:

- **Automation/tooling:** deterministic scripts, output formats, tests, caches,
  indexes, source pruning, validation commands.
- **Delegation/parallelism:** collector lanes, subagent prompts, merge contracts,
  and handoff boundaries.
- **Evidence/failure modes:** overclaiming, stale data, privacy leakage,
  coverage gaps, and untrusted recovered content.

Treat subagents as reviewers, not final arbiters. The main agent owns synthesis,
skill updates, validation, and the final evidence-strength labels.

**A claim about how a tool/API behaves is a hypothesis until an independent probe
reproduces it.** Don't ship n≈1 assertions as skill content. Dispatch a subagent
whose job is to *falsify* the claim by re-running the tool across several queries,
then reconcile. (This session: a probe overturned a confidently-written claim —
"an empty Pieces result means you called the wrong tool" — when the truth is the
inverse: a *non-empty* result doesn't mean a match.)

### 2. Skill Identification

Determine which skills were used or could benefit:
- Personal skills live in `~/.agents/skills/`; project skills in `.claude/skills/`.
  There is no full mirror at `~/.claude/skills/` — as of 2026-07-31 it holds only a
  couple of entries, and `~/.agents/skills/` skills appear there one at a time via
  per-skill symlinks (currently just `project-docs`). A skill Claude Code should
  discover needs its own entry there.
- The skill that *executed* the workflow — re-derived from the transcript per §0 —
  is the primary update target; the invoked/trigger skill is just the lens.
  Split the rest: process/method lessons → `retrospective`; domain helpers → the
  domain skill that will execute them.
- Scaffold a new skill only when no existing skill owns the workflow.

### 3. Learning Extraction — three documents, proposals not principles

Use the **chat-history skill** as the mandatory method: treat transcripts as evidence, search exact phrases, and **separate direct evidence from inference**. Do not answer from memory or compaction summaries. (chat-history's trigger was narrowed to forensic-only on 2026-07-30; retrospective transcript work is forensic, so the reference stays valid.)

Redact secrets and personal data from any transcript-derived quote before it lands in a durable document, whatever the source — local codex/cursor/claude session files carry the same risk as authenticated surfaces. Prefer transcript IDs or short sanitized excerpts over raw quotes.

Write to **`D:\_projects\agent-control-plane\projects\`** (flat layout, project as filename prefix; templates in `agent-control-plane/templates/`). Do **not** put session retros in project repos — only promoted product facts belong there.

**Three documents, each with a distinct job:**

- **Account** (`<project>-account-<stretch>.md`) — **per stretch** (e.g. a week or a phase). The long, readable unit of reasoning. Narrative of *what happened*, *which agent did what* (attribute every event to Codex / Claude / Cursor / a subagent / the user), and *what was observed in the code and in the chat*. High-level — transcripts remain ground truth; cite transcript IDs, finding IDs, or doc paths. Tag anything concluded-but-not-directly-observed `[inference]`. End with an agent-attributed, signal-ranked inflection spine.
- **Learnings** (`<project>-learnings.md`) — **per project, living.** Every item is a **proposal**, not a settled principle. Append only NEW conclusions; cite transcript or finding ID.
- **Meta** (`<project>-meta.md`) — **per project, living.** Honesty ledger: corpus table, confidence map (with an evidence-type column: `direct-command` / `direct-transcript` / `structural-inference`), gaps, limitations.

**Proposal format (use this, not "What Worked / What Failed" dated entries):**

```markdown
### [Short claim title]
- **Claim:** one sentence.
- **Evidence:** transcript ID / finding ID / live command — tag it `direct`
  (transcript quote or live command) vs `inference` (structural or interpreted).
- **Signal:** Champion | Promote | Flag | Drop
- **Status:** Hypothesis (1 obs) | Corroborated (>=2 independent) | Settled (user-confirmed / structural)
```

**Signal scale:**
- **Champion** — big issue, actively promote and champion.
- **Promote** — strong enough to promote to a skill/ADR now.
- **Flag** — pattern observed, needs more corroboration before action; kept so future passes accumulate evidence.
- **Drop** — noted for completeness, not actionable.

Group proposals in the Learnings doc by Signal (Champion first), not by Principle-vs-Antipattern. Not everything is a Champion — grading down to Flag/Drop is the point. If we postmortem-ed every session this way we would have thousands of items; the signal grade keeps the few that matter. Keep a short "Quick reference" table derived **only** from Champion/Promote proposals.

Before synthesizing any stretch, **name the stack** for that stretch (e.g. "Argo/KubeBlocks" vs "Talos/tofu/CNPG"). Confirm you are not conflating two systems; a full-stack pivot orphans a generation of lessons and a retrospective that treats two stacks as one is wrong from the first sentence.

### 4. Skill Update

Update skill files with extracted learnings:
- **A skill is a directory, not just `SKILL.md`.** Audit the whole thing — read
  and *run* its scripts before citing them; prose edits alone are not a skill
  improvement. (This session a helper script was cited approvingly for two turns
  before anyone opened it.)
- Add to existing `## Learnings` / `## Known Issues` sections (create if absent);
  keep entries dated, concise, and non-destructive to existing content.
- Distill one sharp principle per lesson. If a lesson already appears, sharpen it
  in place — do not restate it across sections.
- Add deterministic scripts to `retrospective` only when they support
  retrospectives generally (e.g. transcript timeline extraction); domain-specific
  scripts go in the domain skill.
- Validate before reporting: frontmatter parses, headings nest, and any script
  the skill references actually exists and runs. (The old
  `skill-creator/scripts/quick_validate.py` path is not present on this machine —
  check structurally.)

### 5. Summary Output

Report to user:
- Skills updated (with paths)
- Key learnings captured
- Suggested new skills (if patterns emerged)

## Output Format

```
## Session Retrospective

### Skills Updated
- `~/.agents/skills/[name]/SKILL.md` — added [X] learnings

### Key Takeaways
1. [Most important learning]
2. [Second learning]

### Failures Documented
- [Failure 1]: [brief reason]

### Suggested Actions
- [ ] Create new skill for [pattern]
- [ ] Update AGENTS.md with [insight]
```

## Guidelines

- **Be specific**: "Use `--no-cache` flag" not "caching can cause issues"
- **Include context**: When/why something works or fails
- **Date entries**: Learnings should have dates for tracking
- **Don't over-document**: Only capture genuinely useful insights
- **Failures are valuable**: Non-deterministic LLM behavior means documenting anti-patterns prevents repeating mistakes

## Example Skill Update

Adding to `~/.agents/skills/pdf-generation/SKILL.md`:

```markdown
## Known Issues

### 2025-01-01
- Eisvogel template fails with emoji in headers — escape or remove
- Russian text needs `babel-lang: russian` in YAML frontmatter

## What Works

### 2025-01-01
- `--pdf-engine=xelatex` required for non-Latin scripts
- Pre-flight check: `pandoc --version` to verify filters installed
```

## Integration

Can be combined with:
- Git commit hooks (auto-retro before commit)
- AGENTS.md instructions (remind to run retro)
- CI/CD (capture learnings from failed builds)

## Tools

- Read: Access skill files and conversation history
- Edit: Update existing skills
- Write: Create new skill files if needed
- Glob: Find skill directories

## Learnings

### 2026-06-10

#### What Worked
- For retrospectives about a recent session, find the actual transcript first and search it with exact user phrases before evaluating. In Codex this is usually `~/.codex/sessions/**/rollout-*.jsonl`.
- The strongest session analysis came from reconstructing the workflow loop: user correction, live evidence, plan, narrow implementation, tests, visual verification, PR review comments, and CI.
- Treat user complaints like "you didn't think long enough" as a pressure test. Re-run the analysis from source artifacts instead of defending the earlier answer.

#### What Failed
- Answering a "why did this go well" question from compacted recollection produced a plausible but shallow evaluation. The missing step was transcript inspection.
- The `chat-history` directory had extraction scripts but no `SKILL.md`, so the workflow was not discoverable as a skill even though the tooling existed.

#### Configuration Notes
- On Windows, transcript extractor commands may need `PYTHONUTF8=1` to avoid console encoding failures from Unicode output.

### 2026-06-29

#### What Worked
- Cursor agent transcripts at `~/.cursor/projects/<workspace>/agent-transcripts/**/*.jsonl` reconstruct multi-turn sessions (PR #4 secrets cutover, template debate, Doppler audit) when the `/retrospective` turn has no prior in-chat history.
- User corrections ("how do you know?", "creds are in Doppler", "CI green doesn't mean much") are triggers to re-run from **artifacts** (transcript → `doppler secrets --only-names` → `kubectl` → `gh pr diff`) instead of defending the prior answer.
- PR review bar: triage each bot separately — Kilo line reviews can find real bugs; CodeRabbit Free may be rate-limited walkthrough only; manifest-policy CI catches allowlist gaps bots miss.
- Shipping velocity advice: separate **capture lane** (tofu/talhelper) from **platform lane** (helmfile waves) — don't gate Longhorn/KubeBlocks on substrate capture when cluster is already live.

#### What Failed
- Broad `.gitignore` rule `secrets.yaml` silently blocked `apps/secrets.yaml` (ExternalSecret refs only) — commit needed `!apps/secrets.yaml` or `git add -f`.
- Inferring "credentials missing" or "KubeBlocks broken" from docs without cluster/Doppler verification in the same session.

#### Configuration Notes
- PR review canvas SDK: `Table` uses `rowTone` (not `rowTones`); `DiffStats` does not accept `~900` — use `Text` for approximate counts.
- Post-review uncommitted work noted in review comments (e.g. gitleaks workflows) may exist on disk but outside the PR branch — call out explicitly in merge verdict.
- **Session learnings home:** `D:\_projects\agent-control-plane\` — three docs per project: `<project>-account-<stretch>.md` (narrative, per stretch), `<project>-learnings.md` (proposals with Claim/Evidence/Signal/Status, per project), `<project>-meta.md` (corpus/confidence/gaps, per project). Templates in `agent-control-plane/templates/`. Wave-1 granular files archived under `archive/wave1-granular/`. See `agent-control-plane/AGENTS.md`.

### 2026-07-04

#### What Worked
- A strong workflow retrospective should include an explicit parallelization and tooling pass: identify independent evidence lanes, deterministic scripts to extract first-pass evidence, and subagent perspectives that challenge the main agent's synthesis.
- Subagent review is useful after the first skill update, especially with separate prompts for tooling, delegation strategy, and evidence/failure modes.
- A reusable retrospective helper belongs in this skill when it supports retrospectives broadly. `scripts/session_timeline.py` extracts message/tool-call timelines from Codex JSONL so future retros can cite a compact timeline without hand-writing parsers.

#### What Failed
- Updating only the domain skill (`chat-history`) missed the directly invoked `retrospective` skill. When a user invokes a skill and asks to improve the workflow just used, enhance that skill first unless the improvement is clearly domain-specific.
- Treating a strong metadata lead as effectively recovered source can overstate evidence. Retrospectives should preserve evidence-strength labels and note coverage limits.

#### Configuration Notes
- For collector lanes, require a stable schema: `surface`, `timestamp`, `location`, `direct_evidence`, `inference`, `confidence`, and `needs_followup`.
- Use redacted or no-snippet outputs for durable retrospective docs when evidence comes from authenticated browser, Drive, Gmail, or Pieces surfaces.

### 2026-07-06

#### Corrections to 2026-07-04
- **The target-skill rule was reversed.** 2026-07-04 said "enhance the invoked (`retrospective`) skill first." Wrong — the target is the skill that *executed* the workflow, found from the transcript (here `chat-history`). See §0; the old note stands only as a record of the wrong turn.

#### What worked
- **Probe-to-falsify beats assert-then-defend.** A `chat-history` write-up of Pieces' quirks was authored from one session (n≈1); a subagent dispatched to *falsify* it via 9 real calls overturned two claims. Reproduce tool-behavior claims before shipping them.
- **Frame Pieces' risk as derailment, not security.** Its real hazard to an agent is a flood of confident-looking irrelevant hits (self-reference, recent-activity fallback, out-of-window leaks, junk entities) that pull it off-task — not secret leakage. Center the noise problem.

#### What failed
- **"Improved the skill" that was only prose.** Edited `SKILL.md` and rubber-stamped a script (`session_timeline.py`) unread for two turns. A skill is a directory — audit and run the scripts.
- **Over-built the method on n=1.** Wrote a 5-lane hunt architecture for a hunt one Pieces call actually cracked, and added net length while claiming "shorter." Match the method's weight to what solves the task.
