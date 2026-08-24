# Full settings opened from the thread model control

URL observed: `https://hyperagent.com/settings/agent-defaults#delegation`

## New thread defaults

- Model & compute: GPT 5.6 Luna
- Subagents: configured subagent model observed as DeepSeek V4 Flash; link to `Manage agent delegation`
- Autonomy & safety:
  - Execution mode: Auto selected — “Agent runs everything end-to-end without stopping.”
  - Alternate mode: Ask first — pauses for approval before sensitive actions such as sending messages or modifying external systems.
  - Turn timeout choices: 10 min, 30 min, 60 min, 90 min, 4 hours.
- Capabilities: 13 active badge; expanded surface displayed the named capabilities and integration controls below.

## Capability controls

- Research: Search, Find Similar, Exa Answer, Exa Research, Exa Websets, Thread Search
- Browser: Browser
- Data: Tables, Documents
- Interactive: Webpages, Slides, HyperApps
- Media: Images, Video, Audio, Transcribe, Avatar, Maps
- Integration scope controls: Off, Selected, Open
- Connected/available integrations surfaced: Slack, Google Gmail, Google Tasks, Google Calendar, Google Drive, Google Docs, Google Sheets, Coldaine (GitHub), Bright Data, Notion, Context7, Firecrawl, Cloudflare
- `Connect apps` link to `/settings/integrations`
- Text: “Agent can discover and prompt for new connections”

## Home thread delegation

- Scope combobox options: Do not delegate; Delegate to all my agents; Delegate to select agents.
- Current scope observed: Delegate to all my agents.
- Ask for approval switch observed and left unchanged.
- Delegation depth limit: 1; a sub-agent invoked from a home thread cannot invoke another sub-agent.
- Reset button present and not activated.

## Mutation boundaries

No radio, timeout, capability, integration, delegation-scope, approval switch, model, or reset control was changed.

Screenshots:

- `screenshots/full-model-settings.png`
- `screenshots/delegation-settings.png`
- `screenshots/autonomy-capabilities.png`
