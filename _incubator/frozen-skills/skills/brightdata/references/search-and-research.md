# Search, research, and answer-engine collection

> SCRATCH V3 — grouped because Discover, SERP, and AI answer-engine scraping all begin with a query/prompt but produce different evidence.

## Choose the right query surface

| Need | Surface |
|---|---|
| Unknown web sources ranked against a research purpose | Discover API |
| Exact Google/Bing/Yandex placement, ads, panels, AI Overview | SERP |
| What ChatGPT/Perplexity/Gemini/Grok/Google AI Mode says | AI answer-engine scraper |

## Discover API
Discover searches the open web and uses `intent` as a relevance rubric. It does not query ChatGPT/Perplexity/Grok.

- Sync: `POST /discover/sync` within a 60-second window.
- Async: `POST /discover` then poll by `task_id`.
- Inputs: query, intent, depth, exact filter keywords, result count, duplicate removal, content/images, country/city/language, date bounds.
- Use for primary-source discovery, supplier/source discovery, and bounded RAG seeds.
- A relevance score is not factual confidence.

## SERP
Use when the engine's presentation is evidence.

Persist engine, raw query, location/language/device, timestamp, result position, ads/widgets/panels, pagination cursor, and Google AI Overview where present. Google AI Overview is a Google SERP feature—not the same as asking ChatGPT or Gemini directly.

## AI answer engines
Bright Data exposes prompt-response scrapers for ChatGPT, Perplexity, Gemini, Google AI Mode, Copilot, and Grok when available.

Persist exact prompt, engine/scraper ID, country, web-search requested/triggered, raw answer, citations/cards, timestamp, sample/attempt number, and cost.

Appropriate uses: GEO/brand visibility, recommendation sampling, citation analysis, LLM-as-judge experiments. Inappropriate: canonical facts, canonical market prices, deterministic monitoring without repeated sampling.
