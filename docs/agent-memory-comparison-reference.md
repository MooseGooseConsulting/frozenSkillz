# Claude Code and Codex Memory: Comparative Reference

> **Status: non-authoritative observational reference**
>
> **Snapshot date:** 2026-08-20
>
> This document records observations from one Windows machine and one active
> Codex session. It does not define repository policy, change either product's
> configuration, or claim a stable vendor contract. Current repository
> instructions and live product behavior take precedence.

## Purpose

This reference compares two agent-memory systems available on the same machine:

1. Claude Code auto memory under `C:\Users\pmacl\.claude\projects\`; and
2. the Codex memory corpus under `C:\Users\pmacl\.codex\memories\` used by the
   active Codex environment.

The comparison asks four practical questions:

- What does each system store?
- When does the stored material enter an agent's working context?
- How does each system transform an experience into a memory?
- What do those differences imply for future agent behavior?

The central finding is that these are not duplicate implementations of the
same memory model. Claude generally stores small, future-facing propositions.
The observed Codex pipeline generally stores evidence-linked histories of work
episodes and then compresses them into a broader startup summary.

## Evidence and method

The observations below came from:

- enumerating every `memory/` directory under
  `C:\Users\pmacl\.claude\projects\`;
- reading all eight Claude memory entries for `frozenSkillz` and selected
  entries from `coldaine-homelab`, `ProjectBroadsideStudio`, `RobotOverview`,
  `bloodarrow-wrx90-memory-tuning`, and `LocalLargeLanguageModels`;
- checking Claude index links, frontmatter fields, file sizes, modification
  dates, and originating-session identifiers;
- inspecting `memory_summary.md`, `MEMORY.md`, `raw_memories.md`, and selected
  rollout summaries under `C:\Users\pmacl\.codex\memories\`;
- observing which Codex memory material was already present at the start of the
  active session and which material required a filesystem search; and
- consulting Anthropic's public description of Claude Code auto memory:
  <https://code.claude.com/docs/en/memory>.

The local corpus is the evidence for what exists on this machine. Vendor
documentation is used only for documented loading and storage behavior. No
public OpenAI page found during this investigation described the particular
local Codex synthesis and injection layer observed here, so this document does
not present that layer as a general Codex product guarantee.

## Terminology

In this document, **memory** means persisted information made available to an
LLM in a later session. It does not imply that model weights change or that the
model recalls prior sessions without context being supplied.

The following evidence labels are used:

- **Observed:** directly visible in local files or active-session behavior.
- **Documented:** stated in public vendor documentation.
- **Inferred:** the best explanation of observed structure, with the
  uncertainty stated.

## Corpus inventory

### Claude Code auto memory

**Observed:** The Claude project tree contained 241 project directories and 31
`memory/` directories. Thirteen memory directories were populated; eighteen
were empty.

| Measure | Count |
|---|---:|
| Populated project-memory directories | 13 |
| Topic memory files | 124 |
| `MEMORY.md` index files | 13 |
| Total Markdown files, including indexes | 137 |
| Unique memory names | 124 |
| Unique recorded origin sessions | 60 |

The populated project scopes were:

| Project scope | Topic memories |
|---|---:|
| `coldaine-homelab` | 33 |
| `ProjectBroadsideStudio` | 20 |
| `bloodarrow-wrx90-memory-tuning` | 18 |
| `ProjectBroadside` | 16 |
| `RobotOverview` | 16 |
| `frozenSkillz` | 8 |
| `D:\_projects` umbrella scope | 4 |
| `ProjectBroadsideStudio - Copy` | 3 |
| `MooseGooseBusiness` | 2 |
| `ProjectBroadsideTrial` | 1 |
| `proxmox-stateful` | 1 |
| `TechdealsHandoff` | 1 |
| `LocalLargeLanguageModels` | 1 |

Every topic file had YAML frontmatter, a unique name, and a description. The
declared memory types were:

| Type | Count |
|---|---:|
| `feedback` | 59 |
| `project` | 50 |
| `reference` | 14 |
| `user` | 1 |

The files averaged approximately 2.2 KB and 28 lines. Seventy-nine entries had
an explicit `Why` section, 87 had `How to apply`, and 112 linked to another
memory with wiki-style links.

The index structure was mostly coherent. Twelve indexes linked every topic
file. The `RobotOverview` index omitted two existing files:

- `feedback-delegate-implementation-subagents.md`; and
- `homelab-cluster-control-path.md`.

No index contained a broken link. Five older or irregular entries lacked
`node_type: memory`, four lacked an `originSessionId`, and 28 lacked a
`modified` timestamp. This suggests that the local schema or writing behavior
has evolved, but the implementation responsible for that evolution was not
inspected.

### Codex synthesized memory

**Observed:** The Codex memory tree contained the following principal layers:

```text
C:\Users\pmacl\.codex\memories\
├── memory_summary.md
├── MEMORY.md
├── raw_memories.md
├── rollout_summaries\
├── skills\
└── extensions\ad_hoc\notes\
```

| Measure | Count |
|---|---:|
| Synthesized task groups in `MEMORY.md` | 115 |
| Task-level entries in those groups | 228 |
| Rollout-summary files | 151 |
| Task sections in rollout summaries | 351 |
| Non-Git Markdown files in the memory tree | 165 |

The count of 228 is the closest available approximation to a count of
individual synthesized memories. It is not directly equivalent to Claude's
124 topic files: one Codex task can contain several reusable lessons, and one
Claude topic can summarize a correction spanning several work episodes.

**Inferred from observed structure:** The Codex corpus represents a staged
synthesis:

```text
session transcript
       |
       v
rollout summary
       |
       v
raw extracted memory
       |
       v
related task groups in MEMORY.md
       |
       v
cross-project memory_summary.md
```

The exact scheduler, selection algorithm, and synthesis implementation were
not inspected. The diagram describes the relationship visible in the files,
not a verified internal product architecture.

## Loading and retrieval behavior

### Claude Code

**Documented:** Claude Code stores auto memory per Git repository, with all
worktrees and subdirectories of that repository sharing the same memory
directory. The first 200 lines or 25 KB of `MEMORY.md`, whichever comes first,
load at the beginning of a session. Topic files do not load automatically;
Claude reads them on demand. Claude may also write or reorganize the memory
files during a session.

**Observed:** All 13 local Claude indexes were below the documented startup
limit. The largest was 40 lines and approximately 7.2 KB. Consequently, every
indexed topic name and summary could fit into the startup memory map for its
project, though the topic bodies would still require later reads.

### Codex in the active environment

**Observed:** The active Codex session began with a compact memory summary in
context. The full `MEMORY.md`, `raw_memories.md`, and rollout summaries were not
present in working context. They became available only after the agent searched
and read the local files.

The observed retrieval sequence was:

```text
compact summary already in context
              |
              v
request appears related to prior work
              |
              v
search MEMORY.md for relevant task groups
              |
              v
open one or two rollout summaries when exact history is needed
```

The active environment also supplied a small set of Kurrent Capacitor team
memory items. Those items were a separate source and should not be counted as
entries in the Codex synthesized-memory tree.

**Observed policy boundary:** Ordinary work does not authorize the agent to
rewrite the synthesized registry. When the user explicitly asks for a memory
update, the allowed write path is a small note under
`extensions\ad_hoc\notes\`, which can later serve as synthesis input.

## How the two systems transform the same experience

The strongest difference is not storage location. It is the unit of
compression.

### Claude's characteristic transformation

Claude topic files commonly reduce an experience to one named proposition:

```text
event or correction
       |
       v
short declarative memory
       |
       +-- why it matters
       +-- how to apply it next time
       +-- related memories
```

Representative local names include:

- `decide-dont-poll`;
- `conventions-presented-as-requirements`;
- `feedback-docs-are-not-discipline`;
- `goal-hooks-can-force-destructive-merges`;
- `robot-motion-deadman-pattern`; and
- `avoid-the-word-pinned`.

These names are retrieval keys and conclusions at the same time. They make a
lesson easy to activate in a later session.

### Codex's characteristic transformation

Codex task groups commonly preserve an episode:

```text
goal and repository scope
       |
       +-- originating rollout/session
       +-- success, partial, or failure outcome
       +-- user corrections and preferences
       +-- reusable technical knowledge
       +-- failure modes and future cautions
```

A sharp behavioral correction may therefore appear as one bullet inside a
larger task history rather than becoming its own named concept.

## Paired observations from the same subject matter

### Session Reviewer

Claude's project memory concentrates on the system's future disposition:

- the old Letta reviewer is decommissioned;
- a successor is intended but should not reuse the retired shape;
- certain rubric lessons and CLI gotchas remain valuable; and
- unmerged successor-relevant material has known locations.

The Codex task memory concentrates on the failure boundary:

- an ambiguous teardown deleted a cloud agent irreversibly;
- the cloud identity, cron, listener, launcher, prompts, data, and repository
  documentation are separate targets;
- local automation should be disabled before destructive cloud action; and
- the Windows Startup working-directory bug has an exact cause and remedy.

**Conclusion:** Claude preserved a future architecture rule. Codex preserved a
destructive-operations case and its causal safeguards.

### Modular weapons

Claude's `modular-weapon-extraction-true-state` concentrates on operational
truth:

- two own-hull extractions succeeded;
- zero foreign-hull installations occurred;
- authoring remained manual;
- important outputs initially lived outside Git; and
- an undocumented mirrored-root technique separated successful and rejected
  runs.

The Codex task group concentrates on the implementation and review milestone:

- the architecture and source contracts were established;
- PR #67 merged after focused tests, Blender calibration, CI, and review-thread
  closure;
- immutable-source and provenance requirements were retained; and
- the merged foundation did not prove whole-corpus production, foreign-hull
  portability, or Unity acceptance.

**Conclusion:** Claude produced the sharper product-maturity correction. Codex
produced the stronger implementation, validation, and provenance history.

### AgentsView

Claude's `agentsview-sessions-db` is a compact reference card containing the
database path, important tables, executable location, approximate corpus size,
and the instruction to query the database instead of scanning raw sessions.

Codex distributed AgentsView knowledge across task histories covering local
installation, PostgreSQL synchronization, producer ingestion, backups, and
skill-effectiveness research.

**Conclusion:** Claude optimized for answering "where and how do I query it?"
Codex optimized for answering "what did we attempt, what was proven, and where
did that effort stop?"

### REFINED-V1

Claude's `refined-v1-adopted` records the later operational decision: the
refined direction was adopted, projects commit native client files, reviewed
skills synchronize through the existing script, and agents should not recreate
a central control plane.

The corresponding Codex material retained the earlier archaeology around
unmerged PR #49 and the warning not to mistake an agent-authored thin proposal
for an approved product decision.

These statements describe different points in the history, but the Codex entry
does not independently surface the later adoption as clearly as Claude does.

**Conclusion:** Claude's directly maintained project memory was fresher for
current doctrine. The Codex memory was more useful for historical provenance
but could mislead if read without a current-state check.

## Comparative summary

| Dimension | Claude Code auto memory | Observed Codex memory |
|---|---|---|
| Primary unit | Named proposition | Task or task group |
| Typical orientation | Future-facing | Retrospective |
| Main question answered | "What should I know or do next time?" | "What happened, what was proven, and what remains?" |
| Project scope | Per repository | Cross-project corpus with project tags |
| Startup material | Per-project `MEMORY.md` index | Cross-project compact summary |
| Detail retrieval | Read linked topic files | Search registry, then rollout summaries |
| Durable writing | Claude writes topic/index files directly | External synthesis observed; explicit updates enter as notes |
| Behavioral corrections | Often standalone memories | Usually preference or failure bullets inside an episode |
| Provenance | Origin-session ID, sometimes dates | Rollout paths, thread IDs, outcomes, PR/test details |
| Current-state strength | Can be concise and recently updated | May lag behind newer decisions |
| Historical strength | Limited narrative depth | Strong episode reconstruction |
| Main failure risk | Overgeneralized doctrine | Buried lesson or stale synthesized state |

## Implications

### 1. Retrieval quality depends on naming as well as content

Claude's proposition-shaped names make a correction easy to recognize and
retrieve. A future request that implicates "conventions presented as
requirements" has an obvious topic match. The same lesson inside a broad Codex
task group may require better search terms or an intermediate summary to
activate.

This implies that a memory system can contain the correct information and still
fail behaviorally because the retrieval key is weak.

### 2. Atomic lessons and case histories solve different problems

An atomic lesson is efficient for behavioral adaptation. A case history is
better for reconstructing why the lesson exists, checking whether it still
applies, and avoiding false completion claims.

Neither representation fully replaces the other. A strong system would retain
both a concise proposition and a link to the episode that justified it.

### 3. Direct writing improves freshness but increases doctrinal risk

Claude can update a project memory during the work that changes the project's
state. That can make it fresher than a later synthesis pipeline. It can also
turn one correction into an absolute rule before the broader corpus tests its
scope.

The `feedback`, `project`, and `reference` types help distinguish intent, but
they do not themselves prove that a statement remains current or universally
applicable.

### 4. Synthesis improves provenance but creates lag

The Codex registry retains session links, outcomes, and grouped evidence. That
supports forensic questions and historical reconciliation. The additional
synthesis stages also create opportunities for delay, compression loss, and a
newer project decision failing to replace an older high-salience correction.

### 5. Project scoping prevents some leakage and causes some duplication

Claude's repository boundary reduces the chance that a specialized rule from
one project will silently govern another. It also means cross-project operator
preferences may be repeated, inconsistently phrased, or absent from projects
where they would help.

The Codex cross-project summary is better positioned to carry stable operator
preferences across workspaces, but it has a higher risk of applying a
project-specific lesson too broadly.

### 6. Memory is context, not verification

Both corpora contain facts that can drift: branch state, deployed services,
tool versions, project decisions, database counts, and current operational
status. Memory should identify what to inspect and why; it should not replace a
cheap live check when the answer may have changed.

### 7. Contradictions are useful signals

The REFINED-V1 comparison shows that apparently conflicting memories may
represent different points in time rather than a simple factual error. A useful
memory system should preserve dates and provenance, surface the conflict, and
route the agent toward current authority instead of flattening both statements
into one claim.

## Conclusions drawn from the observations

1. **The two systems are complementary, not redundant.** Claude's corpus is a
   project-local operational notebook; the observed Codex corpus is a
   cross-project case-history and retrieval system.
2. **They often encode the same experience at different resolutions.** Claude
   tends to preserve the conclusion. Codex tends to preserve the episode that
   supports or qualifies the conclusion.
3. **Claude currently produces more behaviorally legible memories.** Its named
   propositions make corrections visible and reusable without reconstructing a
   whole task history.
4. **Codex currently produces stronger provenance and completion boundaries.**
   Its task records retain outcomes, source sessions, tests, reviews, artifacts,
   and unfinished work more consistently.
5. **Claude's direct project-memory writing can be fresher.** The observed
   REFINED-V1 entry captured a later adopted state that the Codex synthesis did
   not promote as clearly.
6. **Codex's multi-stage synthesis can hide a critical lesson.** A correction
   can exist in the corpus but remain difficult to retrieve because it is a
   bullet inside a broad task group rather than a named memory.
7. **The most useful combined shape would pair propositions with cases.** A
   concise memory should link to its originating episode, and an episode should
   expose its most important future-facing lessons as first-class retrieval
   keys.

## Limits of this reference

- The comparison reflects one machine and a corpus snapshot from 2026-08-20.
- Claude's public behavior may change after the documented version examined.
- The Codex memory synthesis implementation and schedule were not inspected;
  only its outputs, active-session protocol, and write boundary were observed.
- Corpus counts measure files and task sections, not semantic uniqueness.
- No claim is made that either corpus exhaustively represents all prior agent
  sessions.
- Conclusions about strengths and risks are interpretations of the observed
  artifacts, not measured comparative performance results.

This reference should therefore be used to formulate better questions and
future evaluations, not as authority for configuring or changing either memory
system.
