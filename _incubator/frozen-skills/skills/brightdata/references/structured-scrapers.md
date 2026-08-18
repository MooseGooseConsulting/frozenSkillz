# Structured platform scrapers

> SCRATCH V3 — grouped target family. This file earns separation because platform schemas and discovery inputs are deep and needed only for structured-target tasks.

## Shared collection pattern
- Inventory `/datasets/v3/scrapers` live.
- Known URLs: synchronous `/datasets/v3/scrape` for quick inputs.
- Discovery/multi-page: asynchronous `/datasets/v3/trigger` with `type=discover_new`.
- Set `limit_per_input` and total result limit.
- Store exact scraper ID, input schema, output fields, snapshot, errors, and raw output.

## eBay
- Supports product URL enrichment plus keyword, category URL, and shop URL discovery.
- Proven keyword mode uses `discover_by=keywords` and input field `keywords` (plural).
- Category/shop modes use `url`.
- First measured keyword probe returned 1,236 rows and showed variant/capacity contamination; always cap and calibrate.
- Preserve item/group/variant IDs, listing format, condition, price/sale price, shipping, seller/location, timestamp, categories, specifications, aggregate sold count.
- `sold_count` is not a dated completed-sale comp.

## Amazon
- Families: product by URL/ASIN, product search, reviews, sellers, global products.
- Product search observed shape: `keyword`, domain `url`, `pages_to_search`.
- Preserve ASIN, seller/offer, variant, shipping, coupon, Prime/subscription, ZIP/country, timestamp.
- One current scrape is not price history.

## Reddit
- Families: posts, comments, profiles.
- Preserve subreddit, post/comment ID, author, body/title, score, flair, timestamps, permalink, parent/thread links, edit/deletion state.
- Public data only.
- A marketplace post or “sold” marker does not prove final negotiated price.

## Google Shopping
- Structured merchant/product offer discovery, distinct from SERP capture.
- Observed keyword input is `keyword` (singular), not eBay's plural field.
- Preserve product/group identity, merchant, price, shipping, condition, rating, destination URL, position, country, query, timestamp, variants.
- Verify destination page before treating an offer as actionable.

## Other maintained targets
Search the live catalog. Promote a target to a named section only after repeated use or meaningful target-specific semantics. Do not maintain a stale exhaustive list.
