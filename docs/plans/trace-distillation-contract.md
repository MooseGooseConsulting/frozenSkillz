# Contract: Trace Distillation Pipeline

Status: proposed contract; not implemented.

## Up Front

- **What:** A scheduled job that distills new agent sessions into compact structured records and
  persists them to a Postgres database on `coldaine-homelab`.
- **Why:** Skill evaluation, ongoing behavior review, and fleet questions all re-derive the same
  facts from raw transcripts. Distill once, consult forever; raw transcripts stay ground truth but
  stop being the first read.
- **How:** Every other day, read new sessions from AgentsView (read-only). Produce two products:
  lossy navigation condensation for candidate selection, and complete evidence packets (full
  tool-call chains + following message spans) for any session selected for examination. A cheap
  LLM with a versioned prompt extracts structured rows from the packets, never from condensation.
- **Result:** A queryable, rebuildable derived store that `skill-analysis`, review queues, and
  future recurring reviewers consult instead of re-reading the corpus.

## Ownership

| Surface | Owns |
|---|---|
| AgentsView (`~/.agentsview/sessions.db`) | Source corpus. Read-only. Never mutated, never replaced. |
| `agent-control-plane` | Distiller code, distillation prompt versions, run tooling. |
| `coldaine-homelab` | Postgres instance, schema migrations, backup/retention. |
| `frozenSkillz` | This contract, skill decisions that consume the data, tracker. |

The database is **derived and disposable**: it must be rebuildable from AgentsView at any time.
No raw transcript dumps land in it — compact distillations only.

## Architecture Decisions (defaults — confirm or override)

1. **Plain scheduled job, not an agent.** Distillation is mechanical: condense, prompt, insert.
   Reliability matters more than reasoning at this layer. The prior Letta nightly reviewer was
   decommissioned without proving a production run; do not put an agent in the write path.
   Learning-over-time lives in the accumulating database, not in agent memory. A Letta/memory
   agent may later be a **consumer** of this store, never its writer.
2. **Runs on HEPHASTUS** (where the AgentsView DB lives), writes to homelab Postgres over the
   LAN/Tailscale. No DB sync dependency in the read path.
3. **Cadence: every other day**, via Windows Task Scheduler. A run must be safe to re-run and safe
   to skip (machine offline → next run catches up via watermark).
4. **Cheap model, configured not hardcoded.** Model name, endpoint, and cost cap live in config.
   The distillation prompt is versioned; every row records model + prompt version. Rows from
   different prompt versions are never silently compared.
5. **Idempotent.** Upsert by `(session_id, prompt_version)`. Bumping the prompt version
   re-distills; same version never double-writes.

## Data Contract

### Table: `distilled_sessions`

One row per session per prompt version.

| Field | Content |
|---|---|
| `session_id` | AgentsView session identifier (PK with `prompt_version`) |
| `prompt_version` | Distillation prompt version (PK with `session_id`) |
| `model` | Model that produced the row |
| `harness` / `project` / `started_at` | From AgentsView metadata |
| `user_goal` | One sentence: what the owner actually asked for |
| `skills_fired` | JSONB: skill, version/hash if known, channel, task-use vs meta-use |
| `skill_influence` | Per fired skill: shaped behavior / loaded-then-ignored / contradicted / indeterminate, with a one-line basis |
| `outcome` | achieved / partial / failed / unknown, with owner-visible evidence pointer |
| `owner_reaction` | explicit acceptance / explicit correction / no verdict; correction quote when present |
| `harm_cost` | none / ceremony / delay / scope drift / wrong tool / unnecessary handoff, plus note |
| `summary` | One short paragraph |
| `evidence_quotes` | JSONB: minimal verbatim quotes backing outcome and owner_reaction |
| `distilled_at` | Run timestamp |

Abstention is a first-class value: `unknown` / `indeterminate` / `no verdict` are valid and must
not be coerced into confidence.

### Table: `distiller_runs`

One row per run: started/finished, watermark (last processed session), sessions attempted /
written / skipped / failed, model and prompt version, cost. This is the operational audit trail.

### Watermark

Persisted last-successful-session marker (in the DB, not local files) so any machine with
credentials can resume and re-runs are cheap.

## Distillation Prompt Contract

The prompt must:

- extract only the fields above; no global verdicts, no scores;
- require an evidence quote for `outcome` and `owner_reaction`, else mark `unknown` / `no verdict`;
- separate task use from skill editing/inspection/meta-evaluation in `skills_fired`;
- treat owner silence as `no verdict`, never acceptance;
- never infer tool-use effectiveness from call sequence. `skill_influence` judgments require the
  full evidence packet (below); if the packet is unavailable, the value is `indeterminate`.

## Evidence Packets vs Navigation Condensation

Two different products, not one:

1. **Navigation condensation** (lossy, cheap): opening ask, user-message list, fire inventory,
   closing window. Used for candidate selection and corpus accounting only. A row judged from
   condensation alone is invalid.
2. **Evidence packet** (complete): for every session selected for examination, the full chain for
   the skill under review — complete tool-call inputs, complete results *where the archive
   retained them*, and the complete subsequent message span showing what the agent did with them.
   No truncation of the examined chain.

The evaluation question is skill-specific (for `context7-mcp`: "were the inquiries effective and
were results put to use?", not "did the MCP fire?"). The distiller cannot pre-judge that; it must
preserve the complete chain so the examination can.

Known archive limitation (found in pilot, 2026-08-10): AgentsView `tool_calls.result_content` is
empty for kilo/opencode MCP calls — what a tool returned is not always recoverable. Rows must
record this as a coverage gap.

Prompt changes bump `prompt_version` and are recorded in `agent-control-plane` with a one-line
rationale, same discipline as the old reviewer rubric.

## Consumers

- **`skill-analysis` ongoing mode:** census and review-queue candidates come from SQL over this
  store (fire rates, ignored loads, corrections since version change), not from re-scanning
  AgentsView.
- **Worth-keeping deep dives:** the store selects the candidate corpus; final verdicts still read
  raw bounded trajectories. Distillations are navigation and triage, not verdict evidence.
- **Tracker / review queue:** correction rows and repeated-harm patterns surface automatically.

## Failure Rules

- Homelab DB unreachable → abort the run, keep watermark, log; next run catches up.
- One session fails distillation → record in `distiller_runs`, continue; never block the batch.
- Model output fails schema validation → one retry, then skip-and-count.
- Never write to AgentsView. Never write to frozenSkillz. Never mutate a skill.

## Explicitly Deferred (recorded, not dropped)

- `skill-analysis` contract, reframed 2026-08-10: **one assembly pipeline, two examinations.**
  Evidence assembly (distill → candidate corpus → bounded case review) is identical regardless of
  why the skill is being examined; there is no "field track vs study track." What differs is the
  examination applied to the same assembled evidence:
  - *Ongoing examination:* is current behavior acceptable? Output: behavior call, smallest fix or
    temporary disable, recheck condition. May pause a skill immediately on strong evidence.
  - *Worth-keeping examination:* does this skill earn its place? Output: full decision package
    (trigger / behavior / outcome / failure taxonomy / recommended change / regressions /
    uncertainty / post-change plan) and lifecycle disposition.
  - Paired replay is not a separate assembly track; it is an optional evidence *generator* invoked
    only when the examination question is causal.
- Fleet-wide disable/enable tooling across consumer discovery roots.
- Letta/memory recurring reviewer as a **consumer** of this store (revive only after one manual
  ongoing-mode cycle proves the loop; the old schedule never proved a production nightly).
- First MVP target: ongoing behavior review of `context7-mcp` (not `project-docs`).

## Stop Conditions

- Do not build a second transcript database: fields above only, no raw dumps.
- Do not add scoring, grading, or verdict logic to the distiller — it extracts, it does not judge.
- Do not schedule consumers (auto-review, auto-disable) before the store has accumulated and a
  human has spot-checked distillations against raw transcripts.
- Complete this phase when the schema exists on the homelab, one manual run distills a bounded
  batch end-to-end, and spot-check confirms rows match their source sessions.
