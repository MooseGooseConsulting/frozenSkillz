# How to Write a North Star

A North Star is the most authoritative document in a project. It states what the project is, where it is going, and what it refuses to be. Agents and contributors read it first and weigh everything else against it.

Because of that authority, every word matters. A wrong sentence in a North Star is enforced as if the owner chose it. This guide exists to prevent that — and to keep the document small enough that every agent actually reads it every session.

> This guide reflects the settled 2026-06-25 redesign. The North Star has at most five sections — **Opener, Goals, In/Out (conditional), Anti-Goals (default zero), Pillars (conditional)**. There is **no Requirements section**, and **Shape/Caller live in `architecture.md`**, not here.

---

## Resulting Shape

| Section | Include when | Default |
|---|---|---|
| Opener | Always. | Required — one or two lines. |
| Goals | Always. | Required — one or two guiding-light lines. |
| In / Out | The project has a clear *caller* and a clear delivered *Out*. | Omit unless both are concrete. |
| Anti-Goals | You can point to a real, observed, recurring "mistaken-for X" case. | **Zero.** Absence is healthy. |
| Pillars | The owner has made a real tradeoff ("accept cost X for benefit Y"). | Omit. |

Deleted from the old pattern: **Requirements** (goals-as-validation) and **Shape/Caller** as North Star sections (they belong to architecture). No goal backlog. No fabricated anti-goals.

**Minimum viable North Star: Opener + Goals.** Everything else is earned, not filled in. The document stays small enough to read every session through content discipline, not a line count.

Open or unresolved questions are **current work**, not a North Star section — route them to Issues or `docs/plans/` (see `current-work-and-lifecycle.md`). A sixth "Open Questions" section is exactly the drift this pattern removes.

---

## The Opener

At most two lines: state the problem, name the thing. Pick one shape; the default is Problem → Solution.

| Shape | Rank | Form |
|---|---|---|
| **Problem → Solution** | default | "I have problem Y. This is X to solve Y." |
| **Why This Exists** | gap-closer | "No good X exists for Y. This fills that gap." Use when the pain is an absence in the world, not personal. |
| **The Hypothesis** (was "The Bet") | spike-only | "We suspect X produces Y without Z. This tests that." Renamed to drop the commercial-wager reading; restricted to speculative/experimental repos, never the default. |

### Rules

- **State the problem explicitly.** The problem is the most load-bearing piece of identity — it makes the side-quest gate answerable ("does this serve solving problem Y?"). If the problem is only implied, the gate gets answered by inference.
- **Name the thing.** Two lines, both earning their place. No hedging — "We believe that maybe…" is a committee trying not to commit.
- **Do not reach for "The Bet" by default.** Agents glom onto it because it sounds dramatic and misread it as get-rich-quick framing. That is why it is renamed and restricted to spikes.

### Example (MooseGoose)

"Patrick's technical life is scattered across home-app, refs, and half-finished tools, none reachable in one place. MooseGoose Studio is a single-owner private console that consolidates it behind one gate."

---

## Goals

Goals are a compass bearing, not a destination. They shape every decision an agent makes; they are never a test suite.

### What goals are NOT

- **Not requirements.** No "how you'll recognize progress." That is validation — deleted from the pattern.
- **Not a backlog.** A goal that needs more than a sentence is a plan; plans live in `docs/plans/`.
- **Not implementation.** "Use Postgres" is architecture, not a goal.
- **Not a checklist item.** If you can tick it off, it was a task.

### Goal shapes

| Shape | Example |
|---|---|
| Direction | "Make MooseGoose the one place Patrick's technical life lives." A compass bearing, never done. Most common. |
| Problem-echo | "Consolidate scattered tools behind one owner gate." Restates the opener's problem as the standing thing to solve. |
| Quality-bar | "Every owner-only route is reachable, or has a documented reason it's hidden." A bar to clear on every piece of work. |
| User-outcome | "Patrick can run his day from one authenticated surface." Names the caller and what they get. |

### Rules

- **How many? The test is not a count.** Does each goal shape a real decision an agent would otherwise get wrong? Five can be fine if each earns its place and none duplicate without intent. Seven is usually a backlog wearing a goal suit.
- **Start with a verb that implies direction, not completion.** "Surface," "separate," "reduce," "consolidate" — not "implement," "build," "deliver."
- **Refusal goals live in Anti-Goals.** "Not X" is an anti-goal shape; do not duplicate it as both a goal and an anti-goal.
- Number them (G1, G2) if the project cites them, but keep the list short enough to read at a glance.

---

## In / Out — conditional; Shape and Caller live in architecture

In/Out are scope filters — "In: the owner's work + tools. Out: a thin public portfolio, nothing else." They answer one question: *does this belong here?*

### Include In/Out only when the shape is earned

Include In/Out **only** when the project has a clear *caller* and a clear delivered *Out*. For platforms, infrastructure, languages, umbrella repos, or abstract-caller systems, In/Out degrade into tautology — omit rather than force filler.

The pattern was stress-tested against real software to find where it holds:

| Software | Verdict |
|---|---|
| Git, Postgres | **HOLDS** — clear caller, crisp data-model In/Out, concrete delivered Out. |
| VS Code | **THINS** — In/Out add little; Shape carries the identity. |
| Linux kernel | **DEGRADES** — caller is "every process," so In is barely a filter. |
| Python (the language) | **COLLAPSES** — the spec deliberately refuses to prescribe delivery. |

If you cannot fill In/Out concretely, that is the signal: the thing isn't a product with a caller — it's a platform/spec/layer that needs a different identity shape, not a forced one.

### Shape and Caller belong in `architecture.md`

Shape ("Next.js pod on K8s behind Cloudflare Tunnel") and Caller are **delivery mechanism**, not identity. If delivery changes, only architecture should change — the North Star is the slowest-moving doc. Keeping Shape here also invites the agent to infer implementation ("K8s → reach for Helm"): the prescription-creep failure. Demote both to architecture.

> As a full four-liner (In/Out/Shape/Caller), this is a **plan/epic-scoping tool**, not a universal identity section: being unable to fill it out concretely tells you an epic isn't well-defined. That is where the four-liner earns its keep — in `docs/plans/`, not the North Star.

---

## Anti-Goals — default is ZERO

Anti-goals define identity through exclusion: "What will agents assume we are building, because it looks similar, that we are NOT building?"

### The inverted rule

- **Default is zero.** Absence is the healthy state, not a gap to fill.
- **An anti-goal is earned, not invented.** Write one only when you can point to a specific, observed, recurring case of the project being mistaken for X. No evidence, no anti-goal.
- **The guard is against fabrication, not absence.** Agents fabricate anti-goals to feel thorough ("must not become a framework," "must not depend on cloud") — constraints the owner never chose. If you cannot point to a real time this project was actually mistaken for X, do not write one.

### Identity-level only — the minor-rule-explosion guard

"Not a marketing site. Not a multi-user SaaS." — identity drift, good. "Must not use Redis" is a prescription hiding in an anti-goal; it belongs in `architecture.md` → Constraints and Conventions — as a convention with its alternative named, or as a constraint with its source — where it can change without touching identity.

Fabricated anti-goals are the **primary way a minor rule becomes a major one** — it gets written into the highest-authority doc on a hunch and then enforced everywhere. Keep every anti-goal identity-level ("not a SaaS"), never implementation-level ("must not use Redis"), and keep the default at zero.

### When you do write one

Name the attractor. "This is not a note-taking app" names the specific thing agents drift toward — LLMs are especially susceptible: put "text," "corpus," and "user" in a description and every model tries to add a text editor. Ban the *intent*, not the mechanism: "the user does not compose ideas into this system," not "no text input fields."

---

## Pillars — keep, conditional

Pillars are how the project prefers to make tradeoff decisions. Each has a name, a statement, and a "Why" that names the cost. This is the **one place prescription-adjacent content is allowed**, and only as a tradeoff.

### Rules

- **Every pillar names its tradeoff.** "We accept slower velocity in exchange for never shipping demo-only features" is a pillar. "We value quality" is a platitude. No cost, no pillar.
- **The "reasonable opposite" test.** Would someone reasonably argue the opposite? "Corpus-first vs. synthetic-first" is a real tradeoff. "Don't ship broken software" is not.
- **Pillars are defaults, not mandates.** A PR that departs from one is a signal that a tradeoff is being made, to be made conscious — not blocked.
- **Every pillar comes from the owner's mouth.** This is the section most contaminated by agent assumptions ("local and self-contained" sounds reasonable for any desktop app). Two real pillars from the owner beat four plausible ones from the agent.
- **Zero pillars is a valid state.** The section appears when the owner makes a real choice about what to sacrifice for what — not before.

---

## Common Failure Modes

- **Agent fabrication.** An agent filling this out will confidently invent constraints the owner never chose; they sound reasonable, reviewers praise them, and they get enforced until they block something the owner wanted. Every line must trace to something the owner said. This is why the North Star is authored by interview, not by filling in a template.
- **Reaching for "The Bet."** It is spike-only. Default to Problem → Solution.
- **Requirements creeping back.** "How we'll recognize progress" is validation; it turns the North Star into a test suite. It lives nowhere here — if it is testable and load-bearing, it is a plan (`docs/plans/`) or an architecture invariant.
- **Fabricated anti-goals.** The minor-rule-explosion vector. Default zero; earn each one.
- **Shape smuggled in as identity.** Delivery belongs in architecture; if it is in the North Star, the North Star churns every time delivery changes.
- **Pillars without costs.** A "Why" that names no sacrifice is a platitude.

---

## The Guardian

Enforcement is out of scope for this skill, and the Guardian runtime does not exist yet — author and review as if it never will. If it later ships, it reasons over these sections (opener for context, goals for direction, anti-goals as identity boundaries, pillars as tradeoffs to surface). See `guardian-relationship.md`; do not add Guardian ceremony to the North Star itself.
