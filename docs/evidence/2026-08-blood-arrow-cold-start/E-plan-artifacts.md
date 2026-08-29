# Blood Arrow Cold-Start Proof — Plan Artifact Search Report

**Question:** Was a PLAN ARTIFACT for the "Blood Arrow cold-start proof" work (2026-08-26 → 2026-08-29) ever written to disk anywhere, or did every version of the plan exist only as chat text?

## VERDICT

**NO — every version of the plan existed only as chat text.** No durable, machine-readable plan artifact for "Blood Arrow Baked-Appliance Cold-Start Proof" (or its predecessor "Qwen benchmark plan" / "## Proof" drafts) was ever written to disk, in any repo, on Windows, in Codex's own state, or on the remote host, within the 2026-08-26 → 2026-08-29 window. Confidence: **high**. Supporting evidence and residual gaps are itemized below.

---

## 1. Codex's own structured plan mechanism (`C:\Users\pmacl\.codex\plans\`)

Codex has a real, structured, on-disk plan store: `plans\<session-id>\<turn-id>\PLAN.md`. It contains **exactly four** PLAN.md files, all pre-dating or unrelated to this work:

| Path | mtime | Topic |
|---|---|---|
| `plans\01a00ab8-...\01a00d86-...\PLAN.md` | Aug 16 | ChatGPT Conversation Organizer fork |
| `plans\01a03961-...\01a03973-...\PLAN.md` | Aug 25 10:20 | Durable GPU Observability / Q5 qualification |
| `plans\01a03a91-...\_r_2b7_\PLAN.md` | Aug 25 15:30 | One-off Infatoshi Marlin C1 qualification on Blood Arrow/Vast (Blood-Arrow-adjacent but a *different* workstream, and predates the window) |
| `plans\01a03bf2-...\01a03cfc-...\PLAN.md` | **Aug 26 03:57** | "Finish and Correct the Context7 Key Rotator" — session `01a03cfc-5926...` ("Find Context7 key rotation prototype"), started 02:32 on 08-26. Unrelated topic. |

The last entry (Aug 26 03:57) is the **most recent plan ever written via this mechanism** — nothing has been added to `plans\` since, through the moment of this investigation (2026-08-29 01:16). The main Blood Arrow thread (session `01a03ed4-d36a-7333-9548-7b7d8fc6ee32`, started 2026-08-26T16:08:50Z) has **no corresponding entry**, nor does any of its ~100 sub-agent/delegate rollout files.

### Direct, first-person confirmation from the transcript

At **2026-08-28T05:28:17Z** (main thread, line 2248), the assistant said, unprompted:

> "The recorded KCap session has no machine-readable plan, so validation cannot certify completeness automatically."

The user then asked at **2026-08-28T05:29:01Z**: *"can you tell me, why is there no machien readbale plan?"*

The assistant's reply (immediately following, same thread) is the single most decisive piece of evidence in this investigation:

> "Because I never recorded one through the mechanism KCap recognizes. `kcap validate-plan` does not parse arbitrary planning prose, Mermaid diagrams, or assistant messages. It only recognizes: Plan content attached when a session starts or continues, or an in-session plan event captured through the supported planning hooks. In this session, I discussed and presented several plans conversationally, but I never emitted a recognized plan event... That does not mean there was no planning content in the chat. It means none of it was stored in the session's machine-readable plan field... We are currently in Plan Mode, where I am not permitted to use the normal plan-update checklist mechanism. The appropriate next output is one decision-complete `<proposed_plan>` for the reusable appliance pattern."

Ten minutes later (05:39Z) the "Blood Arrow Baked-Appliance Cold-Start Proof" plan (~11.9k chars) was delivered — by the assistant's own account, as a `<proposed_plan>` chat block, explicitly *not* through the plan-persistence mechanism, because Plan Mode disallows it. This matches the empty state of `plans\` exactly: the mechanism that would have produced a file was never invoked for this plan or its predecessors (the 16:44Z Qwen benchmark plan, the 05:14Z "## Proof" draft).

## 2. Corpus-wide file-write scan (Codex rollout transcripts)

Scanned **113 rollout `.jsonl` files** (`sessions\2026\08\{26,27,28}\*.jsonl` — 102 files, 462 MB — plus 11 `archived_sessions\rollout-2026-08-2[6-9]*.jsonl` files), covering the main thread and every subagent/delegate thread visible in that window (86,654 JSONL lines total). Method: parsed every `custom_tool_call`/`function_call` payload; extracted every `apply_patch` "Add/Update/Delete File" target path (JSON-unescaped); separately ran bounded regex sweeps for any filename token anywhere in any transcript (not just patch operations — also plain prose, shell one-liners, tool arguments) matching `*cold*start*`, `*appliance*`, `*proof*.md`, `*plan*.md` patterns.

Results:
- **803** total `apply_patch` Add/Update/Delete File operations across the whole corpus.
- **35** of those targeted a path containing plan/proof/runbook/spec/appliance/cold-start keywords. None was a cold-start-proof document. The real hits, all verified individually:
  - `D:\_projects\bloodarrow-wrx90-memory-tuning\docs\vast-ubuntu-vm-qualification-plan.md` (session `01a03f18`, cwd `D:\LocalLargeLanguageModels`) — VM qualification, not cold-start proof.
  - `docs/activation-runbook.md` and `docs/plans/bloodarrow-operating-model-and-cost-plan.md` (session `01a0469a`, thread name "Find last renter and peer percentile", cwd `D:\_projects\bloodarrow-wrx90-memory-tuning`) — operating-model/cost plan, not cold-start proof.
  - Same `bloodarrow-operating-model-and-cost-plan.md`, edited again from a since-deleted worktree `D:/_projects/.tmp-bloodarrow-edit/` (session `01a04a5f-bf95`, 08-28 21:56 UTC, cwd `D:\LocalLargeLanguageModels`).
  - `D:\_projects\TechdealsHandoff\_artifacts\...\docs\plans\gen5-ssd-atlas-integration.md` / `planning-index.md` — entirely different project (SSD/Atlas integration), unrelated.
  - `D:\LocalLargeLanguageModels\tools\serving\vast_ds4_flash_0731\inspect_capacity.py` — false-positive keyword match (`inspect_capacity` contains the substring "spec"); not a plan document.
  - `D:\LocalLargeLanguageModels\docs\plans\2026-08-22-escha-qwen38-w2-rtx5090-qualification.md` — a **pre-existing** file (dated 2026-08-22), edited at 02:45 on 08-26 from an unrelated session (cwd `D:\_projects\frozenSkillz`, thread unrelated to Blood Arrow), hours before the 16:44Z "Qwen benchmark plan" chat message. Different repo, different topic (RTX 5090 qualification), not the chat-only Qwen benchmark plan referenced in the main thread.
- **Zero** `apply_patch` operations, anywhere in the 113-file corpus, targeted a filename combining "cold-start"/"coldstart" with any extension.
- Bounded regex sweep for `*cold*start*.md` filename tokens **anywhere at all** in any of the 113 transcripts (prose, shell commands, tool args — not just patch targets): **zero matches**.
- Bounded regex sweep for `*appliance*.md`: the only match anywhere in the corpus is a single unrelated, pre-existing memory-summary filename, `2026-08-24T17-58-56-fue5-deepseek_v4_flash_r18_vast_appliance_qualification.md` (dated 2026-08-24, before the window; referenced repeatedly only because Codex's memory system re-surfaces it as context in many later sessions).
- 32 files in the corpus mention "baked-appliance" or "cold-start" as prose/keywords (up to 560 times in the main thread alone) — this is the conversation and live operational work itself (SSH commands, curl calls, measurement-directory paths like `/srv/ai-models/runtime-state/serving/cold-start/...`), not file-write evidence.

## 3. Other Codex state (per task item 2)

- `automations\`, `attachments\`, `ambient-suggestions\` — inspected; nothing plan/proof/cold-start related to this topic.
- `.codex-global-state.json` (1.8 MB): exactly one plaintext occurrence of "cold-start" — an embedded task/prompt string, *"Continue the current Blood Arrow r21 cold-start proof from this task..."* — this is queued task/session text, not a structured plan object. The two `"plan"` key occurrences in the file are unrelated JSON-schema fields (subscription tier `plan`, workspace `plan` field).
- `memories\rollout_summaries\` (Codex's auto-generated end-of-session summaries): 14 files dated 2026-08-26/08-28 exist, e.g. `2026-08-26T16-08-50-ffWO-qwen38_dflash2_bloodarrow_handoff_host_correction.md` and `2026-08-28T04-21-33-EqcB-bloodarrow_renter_peer_percentile_and_practitioner_image_sec.md`. These are Codex's own auto-summaries of *past* sessions surfaced as context — not the user-facing plan, not a machine-structured plan object, and none is titled/dated to match the 05:14Z or 05:39Z proof documents (the long-running main thread never triggered a rollout-summary write for those later turns, consistent with it still being one continuous open session as of this investigation).
- No `.codex-global-state.json`-style structured "todo/plan" store other than `plans\` was found.

## 4. Windows filesystem sweep (per task item 3)

Walked all 8 requested roots — `D:\LocalLargeLanguageModels`, `D:\_projects`, `D:\_worktrees`, `D:\CLAUDEWORKTREES`, `D:\_codex_worktrees`, `D:\_scratch`, `D:\scratch`, `D:\docs` (all exist) — **166,824 files scanned**, excluding `node_modules`, `.git`, `SteamLibrary`, `Samsung 2TB backup`, venvs, model-weight/cache dirs, for `*plan*.md/json/yaml`, `*proof*.md/json`, `*cold-start*`, `*coldstart*`, `*cold_start*`, `*appliance*`, `docs/plans/**`, `*runbook*.md` modified 2026-08-26→2026-08-29.

**88 files matched**, all inspected. Zero matched any cold-start/coldstart/cold_start/appliance pattern. The plan-shaped hits fall into three groups, none of which is the target document:

1. **Bulk worktree checkouts of the `bloodarrow-wrx90-memory-tuning` repo's existing docs** — identical file sets, identical mtimes-per-checkout (i.e., a `git clone`/checkout moment, not an edit):
   - `D:\_scratch\bloodarrow-ops-provenance-fix-20260826\docs\{activation-runbook.md, bloodarrow-bios-operator-runbook.md, memory-qualification-plan.md, plans\bloodarrow-operating-model-and-cost-plan.md, plans\vast-owner-storage-marlin-c1-plan.md, vast-marlin-c1-operator-runbook.md, vast-ubuntu-vm-qualification-plan.md}` — 2026-08-26 02:50:47
   - `D:\_projects\bloodarrow-aw-collector-repair\docs\{...same set...}` — 2026-08-26 03:22:21
   - These are pre-existing repo documents about hardware/BIOS/VM-qualification/cost, checked out for unrelated maintenance tasks ("provenance fix", "collector repair"). Not the cold-start proof.
2. **Entirely unrelated projects** running in parallel during the same window: TechdealsHandoff (`gen5-ssd-atlas-integration.md`, ingestion plans), MooseGooseWebsite (`pivot-plan.md`, `observatory-product-plan.md`), RobotOverview (`beast-command-deck-plan.md`, robot-architecture pivot plans), wispr-word-corpus (`knowledge-recovery-plan.md`), NanoBrowserReborn (`specs/.../plan.md`). None mentions Blood Arrow or cold-start.
3. The one surviving real file: `D:\_projects\bloodarrow-wrx90-memory-tuning\docs\activation-runbook.md` (2026-08-28 16:46) — a genuine, current, committed doc, but it's an *activation runbook*, not the cold-start proof plan.

## 5. Git history

### `D:\LocalLargeLanguageModels` (the serving repo; cwd of the main Codex thread)
- Working tree is currently dirty (unrelated mid-refactor changes; branch `codex/qwen38-speedbench-8k-32k`).
- `git log --all` (90 good refs; 2 corrupt `refs/codex/turn-diffs/*` objects excluded and reported below) for 2026-08-26→2026-08-30: only `tools/serving/qwen38_dflash2_pro6000/*` and `docs/{configuration-investigations.md,serving-benchmarking.md}` commits. **No `docs/plans/*cold-start*` or proof file was ever committed, on any branch, in this window.**
- A branch `origin/plan/manifest-first-experiment-architecture` exists but is dated 2026-08-19 and is about experiment-manifest architecture — unrelated. `origin/cursor/laguna-s21-serve-plan-cf82` is from July, also unrelated. Neither touches cold-start/appliance content.

### `D:\_projects\bloodarrow-wrx90-memory-tuning` (the hardware/ops "Blood Arrow" repo)
- Very active, clean git history in-window (BIOS/BMC/memory tuning, Vast market analysis, incident postmortems, `docs/plans/bloodarrow-operating-model-and-cost-plan.md` added then "retired in favour of Notion", `docs/vast-ubuntu-vm-qualification-plan.md` renamed then retired as "completed").
- These are **real, durable, committed plan documents** — but about VM qualification and cost/operating-model topics, not "Baked-Appliance Cold-Start Proof." No commit in the window touches any cold-start/appliance-named file.

## 6. Remote host `bloodarrow` (read-only, via `ssh bloodarrow`; container `C.49031045` untouched, no writes/restarts issued)

- **`/srv/ai-models/runtime-state/serving/cold-start/`** — confirmed reachable. Contains exactly the 18 measurement files in `20260829T040311Z-r21-cold1/` (create-response.json, cold-measurements.json, preflight.json, timestamps.tsv, container.log, cache-*, docker-diff-*, first-inference-response.json, post-inference-host-state.txt, registry.log, container-inspect-sanitized.json, warm-cache-publication.json) as described, **plus** a second, shorter cycle `20260829T043908Z-r21-warm-cold2/` (5 files: monitor.tsv, timestamps.tsv, preflight.json, instance-latest-sanitized.json, create-response-sanitized.json), **plus** top-level `native-codex-{prompt,last-message,events,pull-*,relist-*,resume-*,release-*}.{txt,jsonl}` files. **None of these is a plan document.**
- `native-codex-prompt.txt` (the briefing that launched the native Codex agent running directly on the host on 2026-08-28, per task note) was read in full. It is a **condensed, re-derived operational directive** ("Continue and complete the Blood Arrow baked-appliance cold-start proof... Required sequence: 1. Verify live state... 2. Native docker push... 9. Only after success, update correct Git docs... create one Notion Investigation..."). It is materially different text from, and shorter than, the 05:39Z chat plan — it is a task briefing generated for/by a different (native, host-side) agent invocation, not a saved copy of the chat-authored plan, and it is not named or shaped like a plan artifact.
- A sibling directory, **`/srv/ai-models/runtime-state/bloodarrow-baked-cold-start-20260828T063810Z/`** (an earlier attempt, referenced inside the main Codex transcript), was also checked: 16 files, all measurement/log artifacts (`cycle1-create.json`, `cycle1-rejected-*`, `host-registry-*`, `guest-local-registry-cleanup.log`) — no plan document there either.
- **`/home/coldaine/Projects/bloodarrow-ops`** — a second, Linux-side checkout of the same `bloodarrow-wrx90-memory-tuning` repo (explicitly referenced by `native-codex-prompt.txt` as "the bloodarrow-ops checkout"). Bounded `find` for plan/proof/coldstart/appliance/runbook names found only the same `docs/activation-runbook.md` — no cold-start-proof file.
- **`/home/coldaine/Projects/LocalLargeLanguageModels`** exists on the host too; bounded `find` there found only its own `.git/refs/remotes/origin/plan/manifest-first-experiment-architecture` ref (same unrelated branch noted above).
- A broader sweep, `find /home/coldaine /srv/ai-models -newermt 2026-08-26 ! -newermt 2026-08-30 -iname '*plan*'` (bounded with `timeout 120`), returned mostly noise from an rclone Google Drive cache mount under `/home/coldaine/.cache/rclone/...` (historical naval "deck plan" reference images, an unrelated Notion "Weekly Planning" export) — nothing Blood-Arrow/cold-start related beyond what's listed above.

## 7. What was NOT / could not be searched — explicit caveats

- **Remote host scope was bounded, not exhaustive.** I ran targeted `find` queries scoped to `/home/coldaine`, `/home/coldaine/Projects`, and `/srv/ai-models` (each bounded with `timeout`, per the read-only/no-state-change constraint). I did **not** enumerate all of `/root`, `/tmp`, `/var`, other users' home directories, or filesystem mounts outside those trees. A plan file dropped somewhere far outside those paths would not have been found.
- **`apply_patch` diff *bodies* were not opened**, only their target file *paths* (extracted from 803 patch operations). I cannot with certainty rule out that cold-start-proof prose was pasted as a comment inside some unrelated file's diff — I consider this very unlikely given the exhaustive filename/keyword sweep across all 113 transcripts turned up zero cold-start-named files anywhere, but it is not literally provable without reading every diff.
- **Codex's internal SQLite stores** (`state_5.sqlite`, `thread_history_1.sqlite` [734 MB], `queue_1.sqlite`, `goals_1.sqlite`, `memories_1.sqlite`, `logs_2.sqlite` [1.57 GB]) were **not queried directly with SQL**. I relied on the rollout JSONL transcripts (the authoritative, human-readable record of the same conversations, which these SQLite files index/cache) plus the confirmed-empty `plans\` directory and the assistant's own explanation of exactly where a recognized plan event would be persisted. If Codex silently persists a distinct plan object *only* inside one of these SQLite DBs and *never* mirrors it to `plans\` or the rollout log, I would have missed it — but this contradicts the transcript's own description of the mechanism, so I judge this gap low-risk.
- **`D:\_projects\.tmp-bloodarrow-edit\`** no longer exists on disk (confirmed via direct `ls` — "No such file or directory"). Its only trace is one `apply_patch` Update-File operation (session `01a04a5f-bf95`, 2026-08-28 21:56 UTC) targeting `bloodarrow-operating-model-and-cost-plan.md`. I could not inspect its final on-disk state before deletion — only the patch-target path, which is not cold-start-proof-shaped.
- Two corrupted git refs (`refs/codex/turn-diffs/captures/...` and `refs/codex/turn-diffs/checkpoints/...`) in `D:\LocalLargeLanguageModels` were excluded from `git log --all` after `git for-each-ref` filtered them out; they are Codex's own turn-diff bookkeeping refs, not user-facing branches, so this exclusion should not hide a plan commit, but is noted for completeness.

## Bottom line

Across Codex's structured plan store, 113 rollout transcripts (462+ MB, every subagent/delegate thread in the window), Codex's global state/automations/memories, a 166,824-file Windows sweep of every plausible project root, full git history (`--all`) in both the `LocalLargeLanguageModels` and `bloodarrow-wrx90-memory-tuning` repos, and a bounded but substantial read-only sweep of the remote host including the cold-start measurement directories themselves — **no file named or shaped like the "Blood Arrow Baked-Appliance Cold-Start Proof" plan (or its "Qwen benchmark plan" / "## Proof" predecessors) exists anywhere.** The assistant's own transcript at 2026-08-28T05:28–05:39Z explains why: Plan Mode's plan-persistence hook was never invoked for this work, and the final plan was delivered as a `<proposed_plan>` chat block by design, not saved to disk — which is exactly what the empty `plans\` directory and the corpus-wide filename sweep confirm independently.
