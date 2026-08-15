# Evaluation Architecture

The system in one diagram, then the ownership boundaries.

```mermaid
flowchart TD
    subgraph ingest["Source corpora — read-only, never mutated"]
        AV["AgentsView<br/>~/.agentsview/sessions.db (7.07 GB)<br/>+ central Postgres (agentsview-db)"]
        KC["KCap (Kurrent Capacitor)<br/>sessions / turns / PR-linked review<br/><i>analytics views paywalled — unused</i>"]
    end

    subgraph lib["Variant library — agent-control-plane eval/library/"]
        P["prompts/<br/>forensic-extractor<br/>repo-forensic-miner<br/>corpus-behavioral-miner<br/>doc-use-investigator"]
        X["extractors/<br/>forensic-signals spec"]
        R["rubrics/"]
        M["methods/<br/>trigger-effectiveness (12-step)<br/>ceremony-gate-lexicon"]
        GS["golden-set/ + CALIBRATION.md"]
    end

    subgraph extract["Extraction harness — cheap LLM, Windows Task Scheduler, every 2 days"]
        DRV["eval/extractors/driver.py<br/>registry -> source window -> backend -> validate -> upsert"]
        ST[("per-variant stores<br/>jsonl today; homelab Postgres after phase gate")]
    end

    subgraph interpret["Interpretation harness — strong LLM, human-triggered"]
        PER["per-project review<br/>(repo-forensic-miner, doc-use-investigator, deployment-debrief)"]
        FLT["fleet review<br/>(corpus-behavioral-miner)"]
    end

    subgraph compare["Comparison harness — eval/comparison/"]
        CMP["agreement / divergence per facet<br/>per session, per variant"]
    end

    subgraph act["Act — frozenSkillz"]
        SK["skill wording / trigger change"]
        TK["docs/skill-review/tracker.md"]
        PR["commit + push + PR"]
    end

    subgraph route["Distribution — plugins/distribution.json"]
        DS["shared + consumer lanes<br/>+ repo_targets axis"]
        SY["sync_frozen_skills.py<br/>--consumer / --deployment / --repo"]
        PRJ["project repo<br/>.agents/skills + .frozen-skills-mcp.json<br/>+ AGENTS.md route"]
    end

    AV --> DRV
    KC -.->|"in-session recall<br/>grounds specific cases"| PER
    P --> DRV
    DRV --> ST
    ST --> PER
    ST --> FLT
    M --> PER
    M --> FLT
    PER --> CMP
    FLT --> CMP
    CMP --> SK
    SK --> TK
    SK --> PR
    TK --> PR
    SK -.-> DS
    DS --> SY
    SY --> PRJ
```

## Ownership

| Surface | Owns | Never does |
|---|---|---|
| AgentsView | Raw cross-harness session corpus (SQLite per machine + central Postgres) | Is never written by this system |
| KCap | Structured sessions/turns, PR-linked transcripts, durable team memory | Analytics SQL is paywalled (403) — not a dependency |
| `agent-control-plane` | The variant library, extractor drivers, comparison harness, run tooling, derived stores | Skill wording decisions |
| homelab Postgres | Per-variant derived stores (`extracted_signals__<variant>`, `extraction_runs`, watermarks) | Disposable — rebuildable from the corpora at any time |
| frozenSkillz (this repo) | Skill text, trigger examples, packaging, lifecycle, tracker, this doc set | Raw transcript storage |

## Layer 1 — extraction

```mermaid
sequenceDiagram
    participant TS as Task Scheduler (2d)
    participant DRV as extractors/driver.py
    participant AV as AgentsView (read-only)
    participant LLM as Cheap LLM (Ollama, BYOK)
    participant DB as Derived store

    TS->>DRV: run --all --batch N
    DRV->>DB: load watermark (per variant)
    DRV->>AV: new sessions since watermark
    loop per session
        DRV->>AV: bounded event window
        DRV->>LLM: forensic-extractor prompt + window
        LLM-->>DRV: signal JSON
        DRV->>DRV: validate schema (one retry, then skip-and-count)
        DRV->>DB: upsert (session_id, extractor_version)
    end
    DRV->>DB: save watermark + run audit
```

Failure contract: store unreachable → abort before any work, watermark kept; one
session fails → recorded, batch continues; backend down → fast pre-check abort (~1s).

## Layer 2 — interpretation

Human-triggered. A kickoff (Cursor Automation or `codex exec` on Task Scheduler)
assembles a review batch from the derived stores and **stops**. A human then
dispatches reader variants over the batch. Two scales: per-project (friction, rule
application, doc use) and fleet (aggregate clusters, then representative episodes).
The synthesizer reads memos, never raw dumps. Output guardrail on every variant: the
"WHAT SHOULD CHANGE" classification with required evidence — nothing / code / command
/ source-of-truth / retrieval / instruction / skill / delegation / hook / model.

## Act + distribute

A supported finding becomes the smallest change in frozenSkillz: trigger language, a
negative example, body guidance, or a handoff — plus tracker update, commit, PR.
Distribution routes it: `shared` (all consumers), a consumer lane (one client), or
`repo_targets` (only the owning repos, with MCP templates and an AGENTS.md route).
