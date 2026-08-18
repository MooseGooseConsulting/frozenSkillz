# Access escalation and custom collection

## Native browser first
Use the current harness's browser for quick visual calibration and ordinary interaction. Describe the objective, not harness-specific calls, in the portable skill.

## Web Unlocker
Use for one known public URL blocked by anti-bot, CAPTCHA, geo, or rendering.

- Select an explicit live Unlocker zone; do not hardcode account-specific names.
- Direct API: `POST /request` with `zone`, `url`, and `format`; Web Unlocker `data_format` supports `markdown` or `screenshot`.
- `parsed_light` is a SERP response format, not a Web Unlocker format.
- Prefer raw HTML/JSON/Markdown.
- Request rendering/screenshot only when needed.
- Not for unknown-source discovery or clicks/forms/session flows.

## Browser API
Use when clicks, forms, login, scrolling, stateful navigation, or a Bright Data proxy/session is required and the native browser is insufficient.

Hosted MCP `scraping_browser_*` supports stateful sequences. Direct CDP is the custom-code escape hatch. Browser collection is usually less structured and more expensive than a maintained platform scraper.

## Raw proxies
Use only when an external client specifically requires HTTP/SOCKS proxy behavior. Zone credentials differ from bearer API credentials.

## Scraper Studio
Use when no maintained scraper fits and the workflow warrants a custom collector.

- Inventory existing collectors.
- Batch: `POST /dca/trigger`, then retrieve `/dca/dataset?id=<collection_id>`.
- Realtime sync: `POST /dca/crawl`; realtime async: `POST /dca/trigger_immediate`, then `/dca/get_result?response_id=...`.
- AI creation: `POST /dca/collector`, then `POST /dca/collectors/{collector_id}/automate_template`, then poll `/automate_template/progress`.
- AI healing: `POST /dca/collectors/{collector_id}/refactor_template`, then poll `/refactor_template/progress`.
- Running a published collector differs from creating/editing/healing/scheduling one.
- Collector mutations require explicit request.
- Persist collector ID, input/output schema, job ID, raw output, version/fingerprint, usage, and errors.
