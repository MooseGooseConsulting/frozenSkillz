# HyperAgent UI sitemap

Wave 0.2 probe; read-only traversal captured in screenshots and companion notes.

## Confirmed starting surface

- Chrome authenticated session
  - Current most-recent tab: ChatGPT conversation `Prompting failure analysis`
  - HyperAgent tab was not present in the first open-tab listing

## Pending

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
