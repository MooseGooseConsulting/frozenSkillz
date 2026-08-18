---
name: brightdata
description: Use this skill whenever a task needs Bright Data or structured public-web collection from eBay, Amazon, Reddit, Google Shopping, Google/Bing/Yandex, ChatGPT/Perplexity/Gemini/Grok/Google AI Mode, a protected or CAPTCHA-blocked website, or a custom scraper. Covers live scraper inventory, known-URL collection, keyword/category discovery, Discover API source finding, SERP capture, Web Unlocker, Browser API escalation, AI answer-engine scraping, Scraper Studio, usage/cost, snapshots, cancellation, and durable collection. Use even when the user names the target site but not Bright Data.
---

# Bright Data

> SCRATCH V3 — grouped from Anthropic official-skill patterns. Shared routing, workflow, safety, and target recognition stay here. Only deep/disjoint capability families move to references.

## Supported targets

This skill explicitly covers:
- **eBay**: product URLs; keyword, category, and shop discovery.
- **Amazon**: products, product search, reviews, sellers, and global domains.
- **Reddit**: posts, comments, and profiles.
- **Google Shopping**: product/merchant offer discovery.
- **Search engines**: Google, Bing, Yandex results, ranks, ads, panels, AI Overview.
- **AI answer engines**: ChatGPT, Perplexity, Gemini, Grok, Google AI Mode, Copilot.
- **Protected websites**: anti-bot, CAPTCHA, geo, rendering.
- **Other targets**: anything found in the live catalog or requiring Scraper Studio.

## Route by job

| Job | Primary path | Read next only when needed |
|---|---|---|
| Inspect keywords/categories/filters | Current harness native browser | none |
| Collect known supported URLs | `scripts/web_scraper.py scrape` | `references/structured-scrapers.md` for target schema |
| Discover many records on eBay/Amazon/Reddit/Shopping | `scripts/web_scraper.py discover` | `references/structured-scrapers.md` |
| Find unknown web sources by research intent | `scripts/discover.py` | `references/search-and-research.md` |
| Capture actual Google/Bing/Yandex result evidence | hosted MCP/direct SERP | `references/search-and-research.md` |
| Query ChatGPT/Perplexity/Gemini/Grok | hosted MCP or live scraper | `references/search-and-research.md` |
| Unlock one known page | `scripts/unlock.py` | `references/access-and-custom.md` |
| Run stateful interactive browser | native browser first; Bright Browser escalation | `references/access-and-custom.md` |
| Build/run custom collector | `scripts/scraper_studio.py` | `references/access-and-custom.md` |
| Check balance/usage/zones | `scripts/usage.py`, `scripts/catalog.py` | none |
| Persist arbitrary async output | neutral raw receipt → adapter → explicit promotion | `references/collection-architecture.md` |

## Standard workflow

1. State what evidence is needed and what target/source is named.
2. Use the current harness native browser for quick manual calibration if query/category semantics are unproven.
3. Inventory live zones, scraper IDs, collectors, or MCP schemas. Never trust stale IDs as authoritative.
4. Select the smallest maintained surface that returns the needed evidence.
5. Choose mode:
   - known quick URLs: synchronous;
   - discovery, broad, multi-page, or long: explicit asynchronous trigger.
6. Every discovery must set hard per-input and total result limits.
7. Record pre-run balance/pending cost and estimated maximum exposure.
8. Trigger once. Do not silently rerun, expand, or schedule.
9. Persist raw output plus exact inputs/config, provider job ID, timestamps, errors, schema fingerprint, and usage.
10. Normalize with a versioned target adapter; preserve unknown fields.
11. Report returned/usable rows, cost per returned/usable row, remaining balance, and what was not established.

## Evidence boundaries

- Active ask ≠ sold/cleared price.
- `sold_count` ≠ dated completed sale.
- One scrape ≠ price history.
- Sold-out page ≠ confirmed transaction.
- Discover result ≠ canonical fact or price ledger.
- LLM/answer-engine response ≠ canonical fact.
- Google Shopping feed ≠ verified destination-page offer.
- Database-wide counts ≠ target-specific evidence counts.

## Cost and automation

- Manual/on-demand by default.
- A recurring search is a saved recipe, not a schedule.
- No auto-rerun or auto-expansion.
- Automation requires explicit purpose, bounded spend, durable webhook, idempotency, recovery, and monitored operational alerts.
- Use `scripts/usage.py` before and after paid runs; billing can post late, so unchanged immediate balance is not proof of zero cost.
- Preserve snapshot IDs immediately so long-running jobs can be monitored or canceled.

## Escalation

1. Official/public feed or JSON.
2. Direct HTTP.
3. Current harness native browser.
4. Maintained structured scraper.
5. Web Unlocker.
6. Bright Data Browser API.
7. Scraper Studio custom collector.

This is not a universal cost ranking. A ready-made structured scraper can be the best path even when a browser can open the page.

## Progressive references

Read only the deep family that matches the current task:
- `references/structured-scrapers.md` — eBay, Amazon, Reddit, Google Shopping schemas and collection patterns.
- `references/search-and-research.md` — Discover, SERP, and AI answer-engine scraping.
- `references/access-and-custom.md` — Unlocker, Browser API, raw proxies, Scraper Studio.
- `references/collection-architecture.md` — neutral webhook, raw receipt, schema registry, adapters, agent roles, promotion.

## Script usage

Treat scripts as black boxes first. Run `--help`; do not read source unless customization or debugging is genuinely required.

- `scripts/catalog.py`
- `scripts/usage.py`
- `scripts/web_scraper.py`
- `scripts/discover.py`
- `scripts/mcp.py`
- `scripts/unlock.py`
- `scripts/scraper_studio.py`
- `scripts/common.py` (shared runtime; normally not invoked directly)

## Verification report

Name the selected surface and dataset/tool ID, exact inputs and caps, snapshot/job ID, result/error counts, raw artifact location, observed schema, adapter version if any, pre/post usage, and unproven claims.
