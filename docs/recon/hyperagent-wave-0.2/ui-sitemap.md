# HyperAgent UI sitemap

Wave 0.2 probe; read-only traversal captured in screenshots and companion notes.

## Confirmed starting surface

- Chrome authenticated session
  - Initial most-recent tab was a ChatGPT conversation (`Prompting failure analysis`); it was safely claimed and navigated to HyperAgent for the probe
  - Current handoff tab is authenticated HyperAgent `/threads/new`

## Confirmed landing and thread settings

- HyperAgent authenticated landing / new thread (`/threads/new`)
  - Sidebar: New thread, Search, Inbox, Agents (expand), New agent, Recent threads, Teams, Skills, Memories, Learning, Projects, Library, Marketplace
  - Composer controls: Add files or context, Thread settings/model control, Use an agent, Execute, microphone, Send message
    - Thread settings → Model → Latest models
    - Thread settings → Model → All models → Anthropic / OpenAI / Other providers / Open weights
    - Thread settings → Reasoning effort → Low / Medium / High / Extra high / Max (model-dependent; absent on sampled Gemini/Kimi/GLM Fast/Haiku)
    - Thread settings → Tools → Research / Browser / Data / Interactive / Media tool buttons
    - Thread settings → Integrations → Airtable / Gmail / Google Calendar / Google Drive / Slack / GitHub / More connected integrations
    - Thread settings → Open full settings
  - Full settings / Agent defaults (`/settings/agent-defaults#delegation`)
    - Model & compute
    - Subagents
    - Autonomy & safety
      - Auto / Ask first
      - Turn timeout: 10 min / 30 min / 60 min / 90 min / 4 hours
    - Capabilities (13 active)
      - named research/browser/data/interactive/media capabilities
      - integration scope: Off / Selected / Open
      - connected integration buttons
      - Connect apps
    - Home thread delegation
      - Do not delegate / Delegate to all my agents / Delegate to select agents
      - Ask for approval switch
      - delegation depth limit 1
  - Quick actions: Design a website, Source candidates, Research a topic, Generate images, More...
    - More… → Video / Audio / Slides / Map / Doc
  - Add files or context
    - Upload files…
    - Skills / Memories / Assets
    - Output as… → Image / Video / Audio / Webpage / Slides / Table / Map / Doc
    - Integrations → Gmail / Calendar / Drive / Slack / GitHub / Sheets / Docs / Tasks / Cloudflare / Firecrawl / Context7 / Notion / Bright Data / Add other
    - Add to a project → existing projects / Create new project…
  - Use an agent
    - Search / six user agents / one team agent / Create from scratch
  - Execute
    - Plan first / Execute
  - Recent threads list with View all
  - Connect your integrations link

## Create-agent flow reached from Use an agent → Create from scratch

- `/agents/new`: Identity → Model → Tools & Integrations → Invocations → Knowledge
- Model: agent model Opus 5; subagent Default (Sonnet 4.6); switches Extended thinking / Fast mode / Budget limit per query
- Tools & Integrations: 18 active tools; Add Integrations opens the full catalog
- Invocations and Knowledge were not expanded

## Sidebar control plane

- Search → global palette over threads, agents, projects, messages, documents, and tables
- Inbox → approval/denial items
- Agents → Command Center, visible agents, View all
- Teams → Join a team / Create team / existing teams
- Skills → Your / Team / Shared with you, create/discover, search, filters, grid/list
- Memories → add/search/filter/list/grid, personal-memory count
- Learning → Improvements / Rubrics
- Projects → new and existing projects plus linked threads
- Library → search, type/visibility/source filters
- Marketplace → searchable agent/skill cards
