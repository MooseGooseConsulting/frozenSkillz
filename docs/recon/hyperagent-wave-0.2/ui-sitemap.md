# HyperAgent UI sitemap

Initial probe only; traversal is paused by the user.

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
    - Thread settings → Reasoning effort → Low / Medium / High / Extra high / Max
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
  - Recent threads list with View all
  - Connect your integrations link

## Not yet opened

- Composer `+` / Add files or context menu
- Thread settings/model picker (catalog inspected; model selection intentionally not activated)
- Use an agent picker
- Execute menu
- More... quick-action menu
- Agents expand/new-agent surfaces
