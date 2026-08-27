You are performing an end-to-end spike to repair the titles of my existing Codex app chat threads.

The current titles are often useless because Codex derived them from:
- the first sentence I typed;
- pasted instructions;
- attachment paths;
- generic requests such as “review this” or “make a plan”;
- inherited text from another agent.

I already cannot reliably find these threads from their existing titles, so do not be overly conservative about changing them. The objective is to make the Codex app’s Chats sidebar substantially more descriptive and useful.

## Hard precondition

Before modifying anything, verify that the Codex app and any other Codex client that may write to the same local thread metadata are fully closed.

If Codex is still running, stop and tell me exactly which process must be closed. Do not modify the thread store concurrently with Codex.

## Scope

Operate on the actual persisted Codex app threads shown in the Codex Chats sidebar.

This is not about:
- ChatGPT web conversations;
- browser-tab titles;
- Tampermonkey;
- browser extensions;
- local display-only aliases.

The resulting names must be the names that Codex itself displays after it is reopened.

## Objective

For every accessible Codex thread:

1. Briefly inspect enough of the conversation to understand what the thread was actually about.
2. Determine the primary work performed or intended in the thread.
3. Generate a substantially more descriptive title.
4. Review and improve the proposed title.
5. Rename the persisted Codex thread.
6. Record the old and new titles in an audit report.

Complete the spike end to end. Do not stop after analyzing the threads or proposing names.

## How to understand each thread

Do not name a thread solely from its first message.

For each thread, inspect at minimum:

- the opening request;
- enough subsequent discussion to identify the real objective;
- the most recent substantive messages;
- any visible outcome, decision, artifact, diagnosis, or unresolved problem.

For long threads, do not read every token sequentially unless necessary. Use targeted inspection, search, summaries, or representative messages to determine:

- the principal subject;
- the actual work undertaken;
- the relevant project or technology;
- the most distinguishing decision, problem, or deliverable.

A thread may evolve. Prefer the title that best represents the dominant or final substantive purpose, not necessarily the first request.

## Naming standard

Prefer titles that are:

- specific;
- concrete;
- recognizable several months later;
- approximately 5–12 words;
- centered on the project, system, problem, or deliverable;
- distinguishable from adjacent threads.

Good title patterns include:

- `Codex Thread Renaming and Session Organization`
- `Unity Remote Agent Harness Architecture`
- `N5 MAX Worker Evacuation and Cold Start Plan`
- `Mach.2 SAS HBA Compatibility Review`
- `Hermes Vanilla Deployment and Expansion Plan`
- `Critique of Agent Documentation Governance Work`
- `Google Drive Reorganization Execution Plan`

Avoid titles such as:

- `Can you review this`
- `Pasted text file`
- `A previous agent produced`
- `Check project status`
- `New chat`
- `Planning`
- `Research`
- `Help with Codex`
- raw filesystem paths;
- titles copied from the opening sentence;
- vague verbs without an object;
- excessively clever titles that conceal the subject.

It is acceptable to use longer titles when that materially improves recognition.

## Two-pass title refinement

Use two passes before applying each rename.

### Pass 1: descriptive candidate

Generate a title that identifies:

- the subject or project;
- the type of work;
- the key distinction from similar threads.

### Pass 2: critique and revision

Ask:

- Would this title let me recognize the thread six months from now?
- Does it describe the actual conversation rather than its opening prompt?
- Is it distinguishable from other threads on the same project?
- Is any important noun missing?
- Is it vague, generic, or unnecessarily truncated?
- Could it be made more concrete without becoming unwieldy?

Then produce the final title.

Do not request individual approval from me. Apply the improved title.

## Execution method

First determine the supported and safest available mechanism for changing the actual Codex thread title.

Preferred methods, in order:

1. A Codex-provided thread-title operation such as:
   - `codex_app.set_thread_title`;
   - `thread/name/set`;
   - another current equivalent exposed by the installed Codex version.

2. If no callable title operation is available, inspect the local Codex thread metadata and determine how the installed version persists titles.

When modifying local metadata directly:

- identify all stores that participate in title persistence;
- avoid updating only a display cache if another authoritative store exists;
- preserve thread IDs, messages, timestamps, project associations, and all unrelated metadata;
- make an automatic timestamped backup before the first write;
- write changes atomically where practical;
- do not edit conversation content;
- do not delete, archive, merge, or reorder threads.

The backup is not an approval gate. Create it automatically and continue.

## Batch process

Perform the work in this sequence:

1. Discover the Codex thread inventory.
2. Record each thread ID, current title, dates, and available metadata.
3. Briefly inspect every accessible thread.
4. Draft a proposed title for every thread.
5. Perform the second-pass critique across the entire set.
6. Detect confusing duplicates or near-duplicates.
7. Revise titles so related threads remain distinguishable.
8. Apply all renames.
9. Re-read the persisted metadata and verify each rename.
10. Produce the final audit report.

Do not rename only the obviously bad entries. Review the entire accessible inventory.

## Handling ambiguous threads

When a thread contains several unrelated topics:

- choose the dominant or most consequential topic;
- include a second topic only when necessary for recognition;
- do not use a vague umbrella title merely to cover everything.

When the content is too sparse to infer the purpose:

- use the most concrete available evidence;
- mark the result as low confidence in the audit report;
- still give it a better title where possible.

When multiple threads concern the same project:

- distinguish them by phase, problem, decision, or deliverable.

Examples:

- `Unity MCP Candidate Research`
- `Unity MCP Remote Transport Validation`
- `Unity MCP Agent Harness Architecture`
- `Unity MCP Implementation Failure Analysis`

## Audit report

Create a report containing:

| Thread ID | Old title | Final title | Confidence | Brief rationale | Rename verified |
|---|---|---|---|---|---|

Also include:

- number of threads discovered;
- number inspected;
- number renamed;
- number left unchanged;
- any inaccessible or malformed threads;
- the title mutation method used;
- backup location;
- metadata files or APIs changed;
- any issues that should be addressed before turning this into a recurring workflow.

## Success criteria

The spike is complete only when:

- every accessible thread has been reviewed;
- the proposed names have undergone a second refinement pass;
- the actual persisted Codex titles have been changed;
- the changes have been verified by reading them back;
- a complete old-to-new mapping has been produced;
- Codex can be reopened without corrupting or losing the threads.

Favor meaningful improvement over excessive caution. This is an exploratory cleanup spike, not a production migration. Do the full run and report what actually happened.