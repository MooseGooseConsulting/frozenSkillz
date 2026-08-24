# Thread model catalog — observed on `/threads/new`

Read-only inspection; models were selected only in an unsent draft to reveal model-dependent controls. No default was saved and no thread was sent.

## Thread settings menu

- Current model: GPT 5.6 Luna
- Reasoning effort: Medium
- Tools: 12 (the expanded catalog displayed 18 named tool buttons)
- Integrations: Any
- Open full settings

## Latest models

The model submenu displayed:

| Model | Provider | UI description |
|---|---|---|
| Fable 5 | Claude | Most capable model. Higher cost. |
| Opus 5 | Claude | Powerful model for complex tasks. |
| Sonnet 5 | Claude | Great for everyday tasks. Lower cost. |
| GPT 5.6 Sol | OpenAI | OpenAI's most advanced model. |
| GPT 5.6 Terra | OpenAI | Balanced OpenAI model. Lower cost. |
| Gemini 3.7 Flash | Google | Google's newest fast model. Lower cost. |
| Kimi K3 | Moonshot | Moonshot's best open model. Lower cost. |
| GLM 5.2 Fast | Z.ai | Faster GLM 5.2. Very low cost. |

## All models → Anthropic

- Fable 5 — Most capable model. Higher cost.
- Opus 5 — Powerful model for complex tasks.
- Opus 4.8 — Earlier Opus for complex tasks.
- Opus 4.7 — Earlier Opus for complex tasks.
- Opus 4.6 — Earlier Opus for complex tasks.
- Sonnet 5 — Great for everyday tasks. Lower cost.
- Sonnet 4.6 — Earlier Sonnet for everyday tasks. Lower cost.
- Haiku 4.5 — Fastest for quick, simple tasks. Very low cost.

## All models → OpenAI

- GPT 5.5 — Earlier OpenAI flagship.
- GPT 5.6 Sol — OpenAI's most advanced model.
- GPT 5.6 Terra — Balanced OpenAI model. Lower cost.
- GPT 5.6 Luna — Fast, light OpenAI model. Very low cost. (currently pressed/selected)

## All models → Other providers

- Qwen 3.7 Plus — Alibaba's model for everyday tasks. Very low cost.
- Gemini 3.7 Flash — Google's newest fast model. Lower cost.
- Gemini 3.6 Flash — Google's fast model for agentic tasks. Lower cost.
- Gemini 3.5 Flash — Google's fast model for everyday tasks. Lower cost.
- Gemini 3.5 Flash-Lite — Experimental; Google's fastest model for high-volume tasks. Lowest cost.
- Fugu Ultra — Sakana's coordinated expert agents for complex tasks.
- Grok 4.6 — xAI's frontier model for coding and agents. Very low cost.
- Grok 4.5 — xAI's conversational model. Very low cost.
- Muse Spark 1.1 — Meta's model for creative work. Very low cost.

## All models → Open weights

- Kimi K3 — Moonshot's best open model. Lower cost.
- Kimi K3 Fast — Experimental; Kimi K3 with faster output. Higher cost.
- Kimi K2.6 — Open model for everyday tasks. Very low cost.
- GLM 5.2 — Z.ai's open model for everyday tasks. Very low cost.
- GLM 5.2 Fast — Faster GLM 5.2. Very low cost.
- DeepSeek V4 Pro — Open model tuned for deep reasoning. Very low cost.
- DeepSeek V4 Flash — Open model tuned for fast, high-volume work. Lowest cost.
- MiniMax M3 — Experimental; open model for long-context, multimodal work. Very low cost.
- Inkling — Compact open model from Thinking Machines. Very low cost.
- Inkling-Small — Experimental; quarter-size Inkling that matches its quality. Very low cost.

## Reasoning effort submenu

- Low — Fast responses
- Medium — Balanced (current)
- High — Deep reasoning
- Extra high — Deeper reasoning
- Max — Maximum capacity

## Fresh model-dependent capture

The current GPT 5.6 Luna parent menu showed `Model GPT 5.6 Luna`, `Reasoning effort Medium`, `Tools 12`, and `Integrations Any`.

I then selected Gemini 3.7 Flash only in the unsent draft. Its parent menu showed `Model Gemini 3.7 Flash`, `Tools 12`, `Integrations Any`, and `Save as default`, with no `Reasoning effort` entry. GPT 5.6 Luna was then restored; no default was saved.

## Tools submenu (12 badge; 18 named buttons observed)

- Research: Search, Find Similar, Exa Answer, Exa Research, Exa Websets, Thread Search
- Browser: Browser
- Data: Tables, Documents
- Interactive: Webpages, Slides, HyperApps
- Media: Images, Video, Audio, Transcribe, Avatar, Maps

## Integrations submenu

- Airtable — Connect (not connected)
- Gmail — checked
- Google Calendar — checked
- Google Drive — checked
- Slack — checked
- GitHub — checked
- More connected integrations

## Boundary

The probe selected several models in an unsent draft and immediately inspected the resulting menu/settings branches. This did not invoke a model, send a thread, or save a default. Tool and integration controls were not toggled.

Screenshots:

- `screenshots/model-settings-parent.png` — current model/effort/tools/integrations parent menu
- `screenshots/model-settings-catalog.png` — latest model catalog
- `screenshots/model-settings-anthropic.png` — Anthropic catalog
- `screenshots/model-settings-openai.png` — OpenAI catalog
- `screenshots/model-settings-other-providers.png` — other-provider catalog
- `screenshots/model-settings-open-weights.png` — open-weights catalog
- `screenshots/reasoning-effort-levels.png` — five reasoning levels
- `screenshots/model-settings-gemini-no-reasoning.png` — Gemini branch without reasoning control
- `screenshots/model-settings-restored-luna.png` — restored GPT 5.6 Luna branch
- `screenshots/model-catalog-latest.png` — earlier catalog capture
