# Doppler: design intent

Human-maintainer record for `SKILL.md`. Not part of the agent-facing
instruction graph — the skill does not route here and this file is not pointed
to by anything.

## Intended response

The skill should make an agent treat Doppler as a credential-injection layer
and keep secret values out of every durable artifact: chat, logs, diffs,
committed files, and docs. It should prefer CLI-driven injection
(`doppler run -- ...`) and names-only / boolean diagnostics over value dumps,
and it should be conservative about which changes to secrets are safe to make
without owner instruction.

## Context and expected activation

Activation is deliberately gated to direct credential/injection work
(trigger narrowed 2026-08-10): retrieve, inject, set, rotate, verify, or
names-only check with the Doppler CLI. Opaque authentication through a trusted
client or launcher (PDM, `gh`, `kubectl`) is explicitly a non-trigger, so the
skill does not load on every secrets-adjacent task and dilute its own weight.
Only when diagnosis reaches the credential source, secret configuration, or
injection path does it load.

## Opinionation map

Opinionated about hygiene and authority: no value printing, no committed
secret files, service tokens only in CI/production stores, and `restricted`
visibility only on explicit owner instruction. Neutral on non-safety mechanics
such as shell syntax (POSIX vs PowerShell) and setup details, which are
reference material rather than prescribed lanes.

## Causal instruction design

- The **no-print and names-only rules** force the cheap, safe first move
  (`--only-names`, boolean env checks) instead of value dumps.
- The **default-`masked` guidance** in Adding Secrets anchors the least
  restrictive normal state; the Operating Rules guard on `restricted` is the
  hard constraint behind it.
- The **gated trigger** in the frontmatter keeps loading high-signal so the
  hygiene rules are present when a real secret operation happens, instead of
  being skimmed during speculative hygiene passes.
- The **Review Checklist** makes verification mechanical before promotion or
  commit.

## Failure modes or tempting defaults

- **`restricted` visibility is unrecoverable to a normal workflow.** A
  personal/CLI token cannot read a `restricted` value, the dashboard never
  reveals it afterward, and relaxing it to `masked`/`unmasked` requires
  simultaneously changing the value — so a mistaken restriction strands the
  value. The tempting default this guard counters is an agent reaching for
  "the most secure setting" without instruction. Recovery requires a
  service-token read plus a visibility rewrite, which is why the skill treats
  `restricted` as opt-in-only.
- **One `restricted` secret breaks whole-config reads.** A single `restricted`
  secret makes `doppler run` / `doppler secrets download` return 403 for
  personal/CLI tokens even when the secret being requested is itself masked.
  Agents have misdiagnosed this as "the target secret is restricted"
  (observed 2026-08-22); the Operating Rules wording exists so that class of
  error does not recur.
