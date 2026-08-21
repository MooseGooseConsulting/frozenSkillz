# Structured platform scrapers

## Shared collection pattern
- Inventory `/datasets/v3/scrapers` live.
- Known URLs: synchronous `/datasets/v3/scrape` for quick inputs.
- Discovery/multi-page: asynchronous `/datasets/v3/trigger` with `type=discover_new`.
- Set `limit_per_input` and total result limit.
- Store exact scraper ID, input schema, output fields, snapshot, errors, and raw output.

## eBay

### Observed behavior
- Supports product URL enrichment plus keyword, category URL, and shop URL discovery.
- Proven keyword mode uses `discover_by=keywords` and input field `keywords` (plural).
- Category/shop modes use `url`.
- First measured keyword probe returned 1,236 rows and showed variant/capacity contamination; always cap and calibrate.

### Evidence semantics
- Preserve item/group/variant IDs, listing format, condition, price/sale price, shipping, seller/location, timestamp, categories, specifications, aggregate sold count.
- `sold_count` is not a dated completed-sale comp.

## Amazon
- Families: product by URL/ASIN, product search, reviews, sellers, global products.

### Current documented contracts (checked 2026-08-18)
- Amazon products keyword discovery uses dataset `gd_l7q7dkf244hwjntr0`, `discover_by=keyword`, and input `keyword` with optional `zipcode`.
- Amazon global-products keyword discovery uses dataset `gd_lwhideng15g8jg63s7` and input `keyword`, Amazon-domain `url`, and optional `pages_to_search`.
- Amazon Products Search uses dataset `gd_lwdb4vjm1ehb499uxs` with required `keyword` and Amazon-domain `url`, plus optional `pages_to_search`.

### Observed behavior
- Preserve ASIN, seller/offer, variant, shipping, coupon, Prime/subscription, ZIP/country, timestamp.
- One current scrape is not price history.

## Reddit
- Families: posts, comments, profiles.

### Current documented contracts (checked 2026-08-18)
- Reddit posts use dataset `gd_lvz8ah06191smkebj4`; keyword discovery uses `discover_by=keyword` with `keyword`, required `date`, and optional `num_of_posts`.
- Subreddit discovery uses the same dataset with `discover_by=subreddit_url`, input `url`, and optional `sort_by`.
- Preserve subreddit, post/comment ID, author, body/title, score, flair, timestamps, permalink, parent/thread links, edit/deletion state.
- Public data only.
- A marketplace post or “sold” marker does not prove final negotiated price.

## Google Shopping
- Structured merchant/product offer discovery, distinct from SERP capture.

### Current documented contract (checked 2026-08-18)
- Google Shopping uses dataset `gd_ltppk50q18kdw67omz`; keyword discovery uses `discover_by=keyword` with input `keyword` and optional `country`.

### Observed behavior
- Observed keyword input is `keyword` (singular), not eBay's plural field.
- Preserve product/group identity, merchant, price, shipping, condition, rating, destination URL, position, country, query, timestamp, variants.
- Verify destination page before treating an offer as actionable.

## Other maintained targets
Search the live catalog. Promote a target to a named section only after repeated use or meaningful target-specific semantics. Do not maintain a stale exhaustive list.
