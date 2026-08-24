# HyperAgent capability graph

Initial probe only; paused after landing inspection.

```text
Authenticated Chrome
└── most-recent claimed tab: HyperAgent `/threads/new`
    ├── sidebar/navigation
    │   ├── New thread / Search / Inbox
    │   ├── Agents (expand) / New agent
    │   ├── Recent threads / View all
    │   └── Teams / Skills / Memories / Learning / Projects / Library / Marketplace
    ├── composer
    │   ├── Add files or context
    │   ├── Thread settings / model control
    │   │   ├── Latest model catalog (8 entries)
    │   │   ├── Anthropic (8 entries)
    │   │   ├── OpenAI (4 entries)
    │   │   ├── Other providers (9 entries)
    │   │   ├── Open weights (10 entries)
    │   │   ├── Reasoning effort (5 levels)
    │   │   ├── Tools (18 named buttons across 5 categories)
    │   │   ├── Integrations (6 entries; 4 connected status toggles plus Airtable connect)
    │   │   └── Open full settings
    │   ├── Use an agent
    │   ├── Execute
    │   ├── microphone
    │   └── Send message (disabled before input)
    ├── quick actions
    │   ├── Design a website
    │   ├── Source candidates
    │   ├── Research a topic
    │   ├── Generate images
    │   └── More...
    └── recent threads / integrations link

Full settings / Agent defaults
├── Model & compute: GPT 5.6 Luna
├── Subagents: DeepSeek V4 Flash; Manage agent delegation
├── Autonomy & safety
│   ├── Auto (selected) / Ask first
│   └── Timeout: 10m / 30m / 60m / 90m / 4h
├── Capabilities: 13 active
│   ├── Research / Browser / Data / Interactive / Media
│   └── Integration scope: Off / Selected / Open
└── Home thread delegation
    ├── Do not delegate / all agents / select agents
    ├── Ask for approval switch
    └── depth limit 1
```
