# Example Case Memo

This example demonstrates source traceability plus open-ended reasoning. It is not a mandatory form.

## Source

- Session: `example-session-17`
- Relevant window: user request through the next substantive owner response
- Harness/date: example only
- Activation evidence: full skill read before authority inspection; recoverable hash recorded by
  the run
- Exposed subject guidance: full read is recoverable; partial reads would instead cite only their
  exact excerpt and byte/range locator, or `unknown`
- Relevant co-active guidance: repository instructions and their timing were checked; any material
  excerpt that shaped the same action is included in the source packet
- User goal: update one repository README with a deployment note

## Activation evidence

The skill loaded before the agent inspected the repository's documentation. Its exposed
authority-document guidance was available before the agent proposed changing adjacent files.

For a no-load case, this section would instead identify the bounded evidence that the skill did not
load and would not claim that it should have done so.

## Observed trajectory

The agent opened the README, AGENTS.md, and architecture document. It then proposed a new README
policy and changed AGENTS.md even though the user had requested only a README update. The owner
rejected the invented policy and the expansion into AGENTS.md.

## Debrief

The skill appears intended to help agents author and reconcile authority-bearing documentation.
That purpose is understandable, but this request concerned a bounded explanatory README edit.

The skill may have encouraged the agent to inspect authority relationships, which could have been a
useful precaution. In this trajectory, however, the agent converted that context into an invented
policy and expanded the requested scope. The problem may be the trigger, the procedural body, the
agent's independent overreach, or a combination.

The directly observed harm is the unnecessary adjacent edit and explicit owner correction. It is
not possible to establish from this trajectory alone whether the skill caused the overreach.

Potential learning, conditional on later confirming the historical skill version and exposed text:
retain permission to inspect relevant authority when needed, but make clearer that inspection does
not authorize rewriting neighboring documents or assigning a purpose to a README.

## Competing interpretation and unknowns

The agent might have made the same scope expansion without the skill. The exact historical skill
version, exposed text, and relevant active repository instructions must be checked before
attributing the behavior or proposing a guidance change.

A useful next case would be another README-only request where the skill loaded but the agent kept the
scope bounded, or a comparable request where the skill did not load.

## Follow-up pointers

- inspect the exact skill version;
- find adjacent README-only deployments;
- include the owner's correction in the corpus synthesis; and
- do not convert this one case into a global trigger verdict.
