# Durable collection architecture

> SCRATCH V3 — grouped architecture reference. Only load when persistence, schema variation, webhooks, adapters, or downstream promotion matters.

## Goal
Explorer agents can run bounded probes and preserve arbitrary Bright Data output without first designing a TechDeals table or universal flat schema.

## Stage 1: immutable permissive receipt
Persist:
- provider, account/workspace, scraper/tool/collector ID;
- endpoint, mode, discovery type, exact query parameters and inputs;
- purpose, agent/harness/thread/workflow;
- snapshot/job ID and idempotency key;
- trigger/completion/receipt timestamps, status, errors;
- raw payload/object URI, hash, row index/order, source ID/URL;
- observed fields, primitive types, presence rates, schema fingerprint;
- pre/post usage and cost;
- delivery attempts.

Unknown fields never block receipt. Webhook acknowledgement occurs only after raw artifact and manifest are durable.

## Stage 2: adapters and promotion
A versioned adapter keyed by provider + scraper ID + schema fingerprint normalizes money, dates, URLs, conditions, identities and variants. Unknown fields remain raw. Breaking drift stops promotion, not receipt.

Flow:
`raw receipt -> normalized neutral records -> explicit destination promotion`

## Storage
Use object storage for complete large payloads and PostgreSQL for manifests, row indexes, schema registry, adapter versions, normalized rows, promotions, and operational state.

## Webhook
Provider-generic, idempotent on provider + job ID, accepts completion/failure/partial notifications, fetches result if metadata-only, persists raw first, queues normalization separately, records every delivery attempt, and can recover from provider snapshot retention.

## Agent roles
- Explorer: calibrates, probes, persists raw; no canonical writes.
- Schema/adapter: compares fingerprints, builds fixture-tested mappings, classifies drift.
- Domain: applies meaning/evidence rules and promotes explicitly.
- Operations: reconciles cost, monitors webhook/failures/drift, cancels runaway jobs, routes alerts.

## Automation
Manual trigger is default. A saved recurring recipe is not a schedule. Automation requires approved purpose, bounded spend, durable delivery, idempotency, recovery, and a monitored operational destination.
