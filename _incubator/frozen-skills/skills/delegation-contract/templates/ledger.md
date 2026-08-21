# Requirements Ledger

Write to `./.workflow/LEDGER.md` before delegating. One line per item. Files survive context compaction; conversation does not.

```markdown
- [ ] 1. Every explicit requirement, one line each
- [ ] 2. Implicit expectations and constraints too
- [ ] 3. Marked done only after verification confirms it
- [~] 4. deferred: user approved postponing this
- [ ] V. fresh-eyes verification passed
```

## Rules

- `- [x]` only when addressed **and** verified. Marking your own work done is how a ledger becomes decorative.
- `- [~] deferred: <reason>` only with user approval. It is a third state, not a softer form of done.
- The **last item is always `V.`**, and only a fresh verifier closes it.
- Append discoveries as they surface; a ledger that never grows was not being used.
- Ambiguity goes to the user. A requirement you cannot resolve is not one to invent.

## Multiple concurrent tasks

Use `LEDGER-<topic>.md` beside it. Retire a finished one by renaming to `LEDGER-<topic>-archive.md` rather than deleting — the record of what was required is worth more than the tidiness.

## Honest limit

A ledger's existence proves nothing about its fidelity. A shallow ledger passes every mechanical check that could ever be written against it. Writing a faithful one stays a judgment task, which is why this is a template and not a hook.
