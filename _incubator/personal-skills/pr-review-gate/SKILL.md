---
name: pr-review-gate
description: >-
  After the final push to a PR, wait five minutes for bot reviews before
  merging. Use when you are about to merge a PR you just pushed to. Do not
  load for opening PRs, reading review feedback, or ordinary git work; this
  is only the wait-between-final-push-and-merge moment.
whenToUse: About to merge a PR whose last commit you just pushed
metadata:
  author: pmacl
  version: "0.3.0"
---

# PR Review Gate

The failure that birthed this: merging minutes after the final push, before
review bots had time to respond to that commit. The fix is a time buffer,
nothing else.

## The rule

After your last push to a PR:

1. **Wait five minutes.** Do not merge during this window and do not start the
   next step of the plan that assumes the merge.

2. **At the five-minute mark, check the PR for anything new** — reviews,
   comments, threads, failed checks.
   - Nothing new: **merge.**
   - Something new: read it. If it requests changes, make them, push, and
     restart the five-minute wait. If it's trivial or already addressed,
     merge.

3. Merge autonomously after the wait. No owner approval step — the merge was
   already authorized by the work you were asked to do.

If you have other work to do, the wait can run in the background; it is still
mandatory.

That's the whole skill. Do not expand it into a review-compliance framework —
the point is a five-minute buffer for bots to respond, and then you land it.
