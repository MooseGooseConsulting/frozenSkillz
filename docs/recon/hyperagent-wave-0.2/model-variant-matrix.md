# Model-dependent control matrix

Observed on authenticated `/threads/new` in an unsent draft. Each sample was selected only long enough to inspect its menus and full-settings branch; no prompt was entered, no thread was sent, and `Save as default` was never activated.

| Sampled model | Reasoning-effort control | Parent menu after selection | Tools surface | Integrations surface | Notes |
|---|---|---|---|---|---|
| GPT 5.6 Luna | Present: Low / Medium / High / Extra high / Max | GPT 5.6 Luna; no `Save as default` because it is the current default | Tools 12 badge; 18 named buttons | Integrations Any; same provider menu | Baseline/current model |
| GPT 5.6 Sol | Present: five levels | `Save as default` appeared | Tools 12; same named catalog | Integrations Any | OpenAI advanced model |
| GPT 5.6 Terra | Present: five levels | `Save as default` appeared | Tools 12; same named catalog | Integrations Any | OpenAI balanced model |
| GPT 5.5 | Present: five levels | `Save as default` appeared | Tools 12; same named catalog | Integrations Any | Earlier OpenAI flagship |
| Fable 5 | Present: five levels | `Save as default` appeared | Tools 12; same named catalog | Integrations Any | Anthropic capable model |
| Gemini 3.7 Flash | Not shown | No reasoning submenu | Tools 12; same named catalog | Integrations Any | Full settings also omitted reasoning control |
| Kimi K3 | Not shown | No reasoning submenu | Tools 12; same named catalog | Integrations Any | Open-weight catalog entry |
| GLM 5.2 Fast | Not shown | No reasoning submenu | Tools 12; same named catalog | Integrations Any | Open-weight fast entry |
| Haiku 4.5 | Not shown | No reasoning submenu | Tools 12; same named catalog | Integrations Any | Full settings also omitted reasoning control |

## What changed by model

- The clearest observed model-dependent change is the presence or absence of the reasoning-effort branch. GPT/OpenAI samples and Fable exposed five levels; Gemini, Kimi, GLM Fast, and Haiku did not.
- Non-default model selections exposed `Save as default`; the current GPT 5.6 Luna did not.
- Across these samples, the visible tools badge/catalog and integration chooser did not change. This is an observation of the current UI, not proof that every model has identical backend permissions.
- Full settings reflected the selected model family and exposed no reasoning control for the non-reasoning samples.
