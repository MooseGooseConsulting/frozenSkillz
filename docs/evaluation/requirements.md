# Evaluation Requirements

Every requirement this system serves, traced to the layer that satisfies it. Sources:
the 2026-08-15 planning brief and the Letta transcript corpus (28 transcripts, 3
agents, mined 2026-08-15).

| # | Requirement | Source | Satisfied by |
|---|---|---|---|
| R1 | Evaluate any and all skills on an ongoing, recurring basis | brief | Extraction timer + human-triggered review cycles (runbook §1–3) |
| R2 | Multiple prompts, extractors, rubrics, methods — persisted, never collapsed | brief | `eval/library/` + `CATALOG.md`; comparison harness; retirement = `reference`, never deletion |
| R3 | Separate extraction from interpretation — never free-form "analyze performance" | method file (NEWINGESTHTHIS) | Two LLM tiers; extractor emits signal JSON only; interpretation consumes signals |
| R4 | Review at two scales: per-project and whole-corpus | brief | `repo-forensic-miner` + `doc-use-investigator` (project); `corpus-behavioral-miner` (fleet) |
| R5 | Per-project review answers: what would help these agents, what are they failing at, did they have the information they needed | brief | repo-forensic-miner required analyses (correction windows, RULE MISSING vs PRESENT-BUT-NOT-APPLIED, source-of-truth collisions) |
| R6 | Fleet review answers: is anything going wrong across all projects | brief | corpus-behavioral-miner aggregates + representative episodes |
| R7 | Reason over everything — AgentsView AND KCap | brief | AgentsView source (driver) + KCap in-session recall (interpretation) |
| R8 | Timer-driven "little agents" via Cursor Automation and/or Codex scheduled task | brief | `eval/automation/`: Cursor draft + Register-EvalTasks.ps1 (Codex via Task Scheduler; verified no built-in scheduler in CLI 0.147.0) |
| R9 | Workshop prompts safely | brief | Versioned variants + `CALIBRATION.md` golden-set gate (v4-lesson) |
| R10 | Skills and MCP servers route through frozenSkillz into the right tooling | brief | `plugins/distribution.json` lanes + `sync_frozen_skills.py` |
| R11 | Domain skills (k8s, PDM, python) land only in the repos they pertain to | brief | `repo_targets` axis; PDM migrated 2026-08-15; UniFi targeted at promotion |
| R12 | MCP servers follow the same routing | brief | `repo_targets[].mcp` + merged `.frozen-skills-mcp.json` artifact |
| R13 | AGENTS.md prompting so agents actually use routed skills/MCP | brief | Project AGENTS.md thin routes (authority doc → Repository-Targeted Skills; project-owned content per project-agent-config.md) |
| R14 | Distill via BYOK, never Letta-tier `model: auto` | transcripts (quota burn) | Ollama backend, configured not hardcoded; cost recorded per run |
| R15 | Cross-project memory, not per-repo burial | transcripts | Fleet store is corpus-wide; repo axis is about *distribution*, not learnings |
| R16 | Separate mechanical facts from interpretive conclusions, with provenance | transcripts | Signal rows carry extractor + version + model + coverage gaps; interpretation labels Observed/Association/Hypothesis/Unknown |
| R17 | Never route to an empty store | transcripts | Phase gate: manual batch + human spot-check before any scheduled consumer |
| R18 | Promote session-derived facts into tools | transcripts | "WHAT SHOULD CHANGE" classification includes command/helper/hook targets |
| R19 | Corpus reasoning is a subagent returning summaries by default | transcripts | Reader variants are bounded one-episode subagents; synthesizer reads memos |
| R20 | Scheduled process never rewrites/promotes/deletes skills | 12-step method + retired-reviewer lesson | The extraction/judgment boundary (skill-evaluation.md → Scheduled extraction); kickoffs stop for a human |
| R21 | Every confirmed defect becomes a regression | 12-step method | Trigger corpus + regression cases in frozenSkillz (method step 9) |
| R22 | Persist the whole design as detailed, diagrammed documentation | brief | This directory |

## Explicitly not requirements

- Numeric pass/fail scores on historical sessions.
- Auto-grading, fleet auto-disable, or any agent in the extraction write path.
- KCap analytics (`v_an_*`) — paywalled (verified 403, 2026-08-15).
- Unvetted ingest normalizers (e.g. coding-agent-search) — AgentsView + KCap are the
  two sanctioned surfaces.
