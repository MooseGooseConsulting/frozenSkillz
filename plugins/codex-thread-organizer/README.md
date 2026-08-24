# Codex Thread Organizer

This Codex-only package runs in **Codex Desktop**. It has two explicit,
proposal-only routes:

- **Local Codex title review** reads title-mutable Codex task bodies, compares
  their work with live coding-project context, and proposes concise titles with
  semantic **type** emoji.
- **ChatGPT web proposal** reads declared body-review cohorts from authenticated
  ChatGPT history and proposes titles plus Project creation, move, or merge
  arrangements.

Each route creates a dated report in the **Codex Desktop Chat Organization
Reports** Notion database. The report is point-in-time evidence, not current
state: it records direct conversation and artifact links, coverage, worker
roster, body-derived relationships, uncertainty, and proposed changes. It ends
with `No action executed`.

## Safety boundary

The package is not implicitly invoked and does not select a route from labels
or matching Project names. It never uses Codex title controls or ChatGPT Rename,
Move, Create Project, Merge, or Archive controls. Matching names can route a
corpus review, but the model establishes relationships only from the readable
body evidence: problems, systems, repositories, files, artifacts, decisions,
outcomes, and chronology.

## Review roles

For multiple local coding-project clusters, the local route dispatches multiple
`gpt-5.6-luna` reviewers with non-overlapping clusters and reconciles their
linked body cards against live repository context. The ChatGPT route uses the
configured `chrome_pilot` worker for browser retrieval and requires an explicitly
configured **Codex 5.3 Spark** analysis profile; it fails closed if that profile
is absent rather than silently changing models.

## Cohorts and Projects

ChatGPT histories are reviewed in declared cohorts of at most 30 body-opened
chats. Inventory labels select candidates only; they do not prove a topic or
relationship. Existing ChatGPT Projects, Codex project metadata, and Git
repositories remain different identifiers. A body-evidenced relationship may
be proposed between them, but a shared name never establishes identity.
