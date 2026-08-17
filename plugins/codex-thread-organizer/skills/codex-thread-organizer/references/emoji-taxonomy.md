# Semantic emoji taxonomy

Use one to three semantic emoji only when they improve retrieval. Their order
should express a meaningful compound, not decoration. The title words still
name the system and work.

| Emoji | Meaning and suitable use |
| --- | --- |
| `🤖🧪` | Agent research, evaluation, or experiment work |
| `☁️🖥️` | Cloud compute, GPU capacity, or model-serving work |
| `🛰️🤖` | Robotics, sensing, or autonomy work |
| `🛰️🔌` | Sensor power, network, or device bring-up |
| `🏠💧` | Home, property, irrigation, or water-system work |
| `💾💸` | Storage capacity, cost, pricing, or retention tradeoffs |
| `🧭🏗️` | Architecture, topology, or system-design decisions |
| `🎨🏭` | Generative-media or creative-production pipeline work |

These are combination seeds, not a closed ontology. Reuse a combination only
when both parts describe the conversation. Avoid a string of loosely related
emoji.

## Version-aware choices

Unicode Emoji v17 is the released newer set. Unicode Emoji v18 is a preview
reference, not a default title vocabulary. A preview emoji must not be used in
an applied title until the target client is known to render it.

When the needed category is absent, an emoji is newly released or preview-only,
or its rendering in the target client is uncertain, dispatch one focused emoji
research subagent. It returns the Unicode version and status, code point
sequence, target-client rendering result, and a concise semantic recommendation.
Do not invent a taxonomy entry from model memory.

## Adapter boundary

For ChatGPT web titles, use semantic category emoji only. Do not add Codex
completion, owner, blocked, canonical, supersession, or archive markers as
default ChatGPT metadata. Codex lifecycle markers remain defined by the Codex
adapter's title grammar.

## Curated newer and rare candidates

These are suggestions, not default labels. The agent must still check rendering in
the target client before proposing one.

| Version | Candidate | Use only when it is semantically exact |
| --- | --- | --- |
| Unicode Emoji v17, released | `U+1FA8E` treasure chest | A durable trove of useful references, retained assets, or a high-value source collection |
| Unicode Emoji v17, released | `U+1F6D8` landslide | A genuinely overwhelming backlog, clutter triage, or a disruptive incident; never ordinary unfinished work |
| Unicode Emoji v18 beta | `U+1F6D9` lighthouse | Wayfinding to a canonical answer, reference, or decision that prevents re-asking the same question |
| Unicode Emoji v18 beta | `U+1FA8C` eraser | A correction, rewrite, duplicate cleanup, or removal decision |
| Unicode Emoji v18 beta | `U+1FA8D` net with handle | Intentional collection, capture, or intake work |

The official [Unicode Emoji v17 charts](https://www.unicode.org/emoji/charts-17.0/)
identify v17 as released and list its newly added emoji. The official [Unicode
Emoji v18 beta charts](https://www.unicode.org/emoji/charts-18.0/) identify v18
as beta; their candidates remain preview-only until the target client renders
them.