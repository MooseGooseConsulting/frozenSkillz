# Codex Thread Organizer: design intent

## Intended response

This skill is designed to make an agent organize the conversation surface Codex
actually exposes, using conversation bodies rather than sidebar titles as its
evidence. When a user needs detailed cross-chat analysis, the agent should
first capture the accessible body data durably, then summarize or classify it
from that evidence.

## Context and expected activation

It activates for recent-chat organization, current-work review, cross-chat
summaries, and durable exports of the chats exposed by Codex. It does not claim
to retrieve a user's entire ChatGPT account history when the native inventory is
bounded, and it is not a general personal-knowledge-management workflow.

## Opinionation map

Native inventory/body retrieval, cursor exhaustion, coverage reporting, and
private handling of saved transcripts are correctness constraints. The title
grammar and workstream clustering rules are intentionally opinionated so the
sidebar stays concise and useful. Project routing remains evidence-led: a
working directory is a clue, not proof of common ownership.

## Causal design rationale

Inventorying every exposed kind before filtering prevents ChatGPT chats from
being silently dropped. Reading the actual bodies counters misleading titles.
The durable-export lane explicitly chooses Codex's native list/read operations
over browser rendering, pages each conversation to exhaustion, and stores the
raw returned turns with an evidence ledger. This makes later detailed summaries
auditable and distinguishes an app-imposed bounded inventory from missing work.
