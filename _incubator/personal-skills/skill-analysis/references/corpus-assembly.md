# Corpus Assembly

## Why corpus assembly is a separate stage

A deployment analysis fails before interpretation if the corpus is incomplete, silently biased, or
too large for one agent to read carefully. Build the corpus in two levels:

- the **candidate manifest** inventories everything detectable in scope;
- the **analysis corpus** is the explicitly selected set that receives individual case extraction.

These carry two different completeness claims, and conflating them is how a bounded study starts
reading as a census:

- **Corpus accounting** — every trajectory in the declared analysis corpus has a case memo or a
  recorded block. This is what the corpus completeness check verifies, and a bounded corpus can
  pass it.
- **Population coverage** — the analysis corpus contains every in-scope candidate in the manifest.
  Only claim this when the numbers actually match.

Deliberately bounding the corpus below the candidate population is expected when the population is
too large to read carefully. State the bound and its selection rule; never report an accounted
corpus as though it covered the population.

Do not turn transcript discovery into an infrastructure repair project. If semantic search is
unavailable, startup synchronization is incomplete, or a configured store has an incompatible
schema, record the limitation and continue with the best bounded read-only indexed fallback.

## Pipeline

```text
AgentsView detection
  -> deduplicated candidate manifest
  -> declared analysis corpus
  -> one trajectory per case reader
  -> one case memo per selected trajectory
  -> corpus completeness check
  -> separate corpus synthesis
  -> targeted gap fill, if needed
```

## 1. Build the candidate manifest

Declare the source scope first: coverage dates, indexed harnesses, machines, providers, projects,
and known blind spots. Inventory the subject skill's detectable activation channels before running
the census, including canonical and distributed paths, named invocation events, injected skill text,
and harness-specific load records when available.

Use read-only AgentsView extraction. Normalize path variants and deduplicate repeated reads within
one deployment episode while retaining repetition as a possible signal. A deployment episode is one
substantive use of the skill for one request or task segment. Split two uses inside the same session
when a new user request, continuation boundary, or clear re-entry creates a separate task context;
record unresolved splits rather than hiding them inside a session-level count.

The manifest carries administrative provenance, not evaluative conclusions:

- session identifier;
- harness, project, machine, and date when available;
- detected activation channel and neutral turn neighborhood: named invocation, full or partial
  read, assistant announcement, references loaded, and the first post-activation action or turn
  boundary when each is recoverable;
- activation-time subject-skill identity: full text or bytes when recoverable, content hash,
  repository commit/package version, and path; for a partial read or injection, the exact exposed
  excerpt and its byte/range locator; or `unknown` when the exposed material cannot be recovered.
  Never substitute the current file or an unexposed full copy for historical guidance;
- likely task-use, editing/inspection, meta-evaluation, or unresolved context;
- candidate source or search neighborhood;
- continuation or parent/child pointers;
- other active skills, repository instructions, or explicit owner language plausibly shaping the
  same behavior;
- extraction state; and
- exclusion or blocking reason when applicable.

Record coverage dates, indexed harnesses, missing providers, and detector limitations alongside the
manifest.

## 2. Declare the analysis corpus

When the candidate set is tractable, extract every task-use deployment plus relevant adjacent
no-deployment cases. When it is not tractable, declare a bounded corpus and explain how it was
selected.

Useful neighborhoods include:

- explicit owner corrections;
- direct skill invocation;
- common activation request shapes;
- unusual or high-cost deployments;
- multiple harnesses and time periods;
- requests before and after a skill version change;
- adjacent tasks where the skill did not appear;
- requests that challenge the current theory; and
- a small random slice to expose blind spots.

Select neighborhoods before deciding whether individual cases were good or bad. Do not search only
for examples that support an overtriggering, usefulness, or failure theory.

For adjacent no-deployment cases, declare the matching rule before interpretation. Useful matching
dimensions include harness, time period, project, request shape, task stakes, and named document or
tool. The rule may vary by neighborhood, but it must be visible enough to expose cherry-picking.

## 3. Maintain a case queue

Every selected manifest row must end in one administrative state:

- `pending`;
- `extracted`;
- `excluded`, with reason; or
- `blocked`, with the missing surface.

These states prove corpus accounting only. They do not grade the skill.

Process the queue in independent bounded assignments. Parallel execution is allowed for throughput,
but each case reader receives one trajectory and produces one memo without seeing other cases or the
emerging corpus conclusion.

Routine extractable cases receive one reader. Assign an independent second read when a case's
interpretation would drive a consequential skill change, when the first reader reports substantial
ambiguity, or when the corpus reader identifies it as a key counterexample. Do not double-read an
arbitrary quota merely to calculate agreement.

## 4. Give each case reader a bounded source packet

Include only:

- the activation-time subject-skill material actually exposed to the agent: the full text when a
  full load is recoverable, or the exact excerpt plus byte/range locator for a partial activation.
  If that material cannot be recovered, label it `unknown`; do not give the reader a current or
  full skill copy as a stand-in. For a no-load episode, record that the agent saw no subject text;
  when the installed-at-time version is recoverable, include it separately as evaluator-only
  reference, never as agent exposure;
- relevant co-active guidance that could plausibly explain the same behavior: the other skill,
  repository instruction, or explicit owner direction's identity and timing, plus the relevant
  text or a stable excerpt locator. State `unknown` or `not recovered` rather than supplying
  unrelated instructions or guessing their content;
- the user request;
- the skill activation neighborhood;
- actions and tool results relevant to the skill;
- the owner-visible result;
- the next substantive owner response; and
- stable source identifiers.

Also record where the bounded window ends: before or after implementation, validation,
commit/push, and owner reply. Include one continuation pointer when a consequential conclusion
depends on material outside the window.

Do not provide the leading theory, expected label, other case memos, or desired skill change. If the
trajectory is too large, localize the relevant turn window first rather than asking the reader to
skim the whole session.

Use the prompt and rationale in [deployment-debrief.md](deployment-debrief.md).

## 5. Assemble before synthesis

Do not synthesize while selected cases remain silently unread. Before corpus review:

- reconcile the analysis-corpus list against the case-memo set;
- account for every exclusion and block;
- confirm no case memo accidentally covers multiple deployments;
- preserve source pointers for later challenge;
- keep raw or sensitive transcript material outside git; and
- publish only compact derived material appropriate for the repository.

## 6. Let synthesis request gap filling

The corpus reader may identify a missing harness, request shape, counterexample, version, or owner
response. Convert that request into new manifest rows or select existing ones, then send each through
the same one-case extraction path. Do not let the corpus reader improvise a case interpretation from
manifest metadata alone.

## Scaling guidance

For dozens or hundreds of candidates:

- batch queue administration, not human reasoning;
- keep one-trajectory isolation for each case reader;
- keep one primary reader for routine cases; use an independent second reader only for a
  consequential proposed skill change, substantial ambiguity, or a key counterexample;
- checkpoint completed memos and coverage after each batch;
- let a separate agent synthesize the assembled memos;
- resynthesize after material gap filling; and
- distinguish population counts from findings in the reviewed corpus.

The purpose of the structure is not ceremony. It prevents context overload, uneven skimming, theory
leakage, and the loss of individual deployments inside an aggregate narrative.
