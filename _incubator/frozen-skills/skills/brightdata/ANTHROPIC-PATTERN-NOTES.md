# Anthropic official-skill pattern notes

Repository cloned locally: `/agent/workspace/anthropic-official-skills`
Source: https://github.com/anthropics/skills
Audit date: 2026-08-16

## Measured examples

| Official skill | Markdown | Python | Other | Pattern |
|---|---:|---:|---:|---|
| `mcp-builder` | 5 | 2 | 3 | Substantial process in SKILL.md; refs only for deep best-practice/evaluation/language branches. |
| `pdf` | 3 | 8 | 1 | Core operations in SKILL.md; one advanced reference and one deep forms workflow. |
| `webapp-testing` | 1 | 4 | 1 | All procedural guidance in SKILL.md; scripts treated as black boxes via `--help`. |
| `internal-comms` | 5 | 0 | 1 | One SKILL.md plus one example/template per genuinely distinct deliverable. |
| `web-artifacts-builder` | 1 | 0 | 4 | Small cohesive skill: one Markdown + helper assets/scripts. |
| `claude-api` | 66 | 0 | 1 | Exceptional giant reference skill split by deep language/feature retrieval units. Not a normal target for Bright Data. |

## Practical split rule
Create a separate Markdown reference only when the topic is:
1. deep enough to justify its own retrieval unit;
2. disjoint enough that most invocations do not need it;
3. non-core—shared routing/safety/workflow belongs in SKILL.md.

Do not create a file for every endpoint, gate, target, or policy sentence.

## Applied to Bright Data v3

- `SKILL.md`: target recognition, job routing, standard workflow, evidence boundaries, cost/automation, escalation, verification, script inventory.
- `structured-scrapers.md`: eBay/Amazon/Reddit/Google Shopping and other maintained platform schemas.
- `search-and-research.md`: Discover, SERP, AI answer-engine scrapers.
- `access-and-custom.md`: Unlocker, Browser API, proxies, Scraper Studio.
- `collection-architecture.md`: neutral webhook, raw receipt, schema registry, adapters, agent roles, promotion.

Target: 5 operational Markdown files plus this audit note; eight scripts remain executable assets. This matches the medium Anthropic patterns instead of the rejected 33-Markdown v2 tree.
