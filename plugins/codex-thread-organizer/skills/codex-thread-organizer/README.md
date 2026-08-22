# Codex Thread Organizer: Maintainer Intent

## Intended outcome

Make the Codex app's accessible conversation sidebar understandable without
inventing coverage, capability, or ownership that the app has not exposed.
Operators should be able to find current work, see which older work was
superseded, and recognize unfinished work from concise, evidence-based titles.

## Problem addressed

The sidebar can mix Codex tasks and ChatGPT conversations. The native listing
can expose a bounded recent page plus pinned conversations, while title mutation
and body reading can have different per-kind or per-entry capabilities. Treating
that as a Codex-only list, or calling a bounded page the complete history, makes
the organization result misleading.

## Design intent and non-goals

- Keep inventory coverage, body readability, and title mutability separate so a
  limitation in one does not erase the other two.
- Prefer accurate, bounded reporting to a false claim that all history was
  organized.
- Do not turn this into a cross-client history manager, a background daemon, or
  an internal title-state database.
- Do not treat a title as proof that a broader project is complete; it records
  the state of the individual conversation after reviewing its body.

## Deliberate boundary

This is a human-maintainer record, not agent instruction. The active behavior is
defined only by `SKILL.md` and references that `SKILL.md` explicitly routes to.
