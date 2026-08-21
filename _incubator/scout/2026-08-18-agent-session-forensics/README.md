# Scout: Agent Session Forensics — Prompts for Reasoning Over Agents

- **Source:** Research notes, synthesized from practitioner discussions (r/ClaudeCode, r/ClaudeAI, Hacker News, GitHub issues), captured 2026-08-18 in `NEWINGESTHTHIS/Promps for reasinng over agents.txt` (filename verbatim from the capture location, including its typos — not an error in this repo).
- **References cited in notes:** Squawk (behavioral anti-pattern detector), Slagent (self-learning coding agent tool), Agent Flow (Claude Code action visualizer), `cass`/coding_agent_session_search (unified session search across 11+ providers), 413K-trajectory empirical analysis (Hanchen Li), OpenClaw loop-detection issue, Claude Code cross-session learning issue #51735.
- **License:** Original synthesis — no upstream license to track.
- **Why captured:** The notes articulate a practitioner-grounded forensic analysis methodology for AI agent sessions that is directly relevant to the `skill-analysis` and session-review lanes in this repo. Key insight: **separate mechanical extraction from causal interpretation**, and treat user corrections as labeled failure events.
- **Core methodology extracted:**
  1. **Raw event extraction** — commands, failures, file touches (heatmap), edit oscillations, user interventions, subagent duplication, rule-encounter events.
  2. **Correction-centered windows** — look 10–20 events backward from each user correction.
  3. **Behavioral clustering** — same-command+same-result (loop), same-command+changed-result (iteration), different-command+same-failure (hypothesis search), different-command+new-evidence (healthy investigation).
  4. **Causal analysis** — RULE MISSING vs RULE PRESENT BUT NOT APPLIED; source-of-truth collisions; instruction-encounter-to-violation gap.
  5. **Intervention classification** — 10 change-type buckets (nothing, code/repo, canonical command, source-of-truth, search/retrieval, instruction, skill, delegation, hook, model/harness). Not defaulting to "add another AGENTS.md rule."
  6. **Cross-corpus aggregation** — normalize events first, compute mechanical patterns, sample representative traces, then do qualitative causal review.
- **What to take for skill-analysis lane:** The SESSION MECHANICS structured-extraction template; the 8-item repo-analyzer checklist; the corpus-level aggregate-first workflow; the 10-bucket intervention taxonomy.
- **What to strip:** The vendor "evaluation framework" framing; the "write another CLAUDE.md rule" reflex.
- **Status:** Raw seed material for the skill-analysis lane; not yet a promotion candidate.
