# HyperAgent Wave 0.2 coverage ledger

Status: read-only probe in progress; findings saved incrementally

## Session

- Browser: authenticated Chrome extension session
- Starting user tab observed: `https://chatgpt.com/c/6a8bb822-9160-83ea-96c2-a9bb5194d8b1` (title: `Prompting failure analysis`)
- HyperAgent landing screen reached at `https://hyperagent.com/threads/new`
- Safety boundary: no prompts, messages, runs, model invocation, schedule/eval/live-mode start, OAuth, billing change, or save/confirm

## Initial coverage

| Surface | Visible controls / observations | Opened | Mutation boundary | Remaining |
|---|---|---|---|---|
| Current Chrome tab | ChatGPT conversation; sidebar, composer, `Add files and more`, model/effort button, voice controls | Read-only DOM snapshot | Composer send and model actions intentionally not activated | Superseded by HyperAgent navigation |
| Browser session | 12 user tabs listed; most-recent tab claimed and navigated to Hyperagent | `chrome.user.openTabs`, claim of most-recent tab | No tab creation or external writes | User may need to foreground the tab manually |
| HyperAgent landing / new thread | Sidebar navigation; composer; quick actions; recent threads; resource links | Landing screenshot and DOM snapshot captured | Send is disabled until input | None for current landing pass |
| Thread settings → Model | Latest models, provider groups, reasoning effort, tools, integrations, full settings | Model menu and all provider/effort/tool/integration submenus opened; model-variant comparison captured | Models were selected only in an unsent draft to expose branches; no default saved; tool/integration toggles not changed | None for sampled variants |
| Full settings / agent defaults | Model & compute; Subagents; Autonomy & safety; Capabilities; Home thread delegation | Opened via `Open full settings`; inspected delegation scope, execution modes, timeout buttons, named capabilities, integration scope | No radios, buttons, switches, combobox options, or reset controls changed | Return to landing and continue composer controls |
| Composer quick-action menus | More…, Add files or context, Use an agent, Execute | All opened; screenshots captured; submenu branches inspected | No upload, output generation, project mutation, agent save, or execution | None for current landing pass |
| Create-agent flow | Identity → Model → Tools & Integrations → Invocations → Knowledge | Entered without input; model/subagent switches and integration catalog inspected | Create disabled; no identity, model default, tool, integration, invocation, or knowledge mutation | Invocations and Knowledge remain unexpanded |
| Sidebar control plane | Search, Inbox, Agents/Command Center, Teams, Skills, Memories, Learning, Projects, Library, Marketplace | Opened each safe navigation surface; screenshots and notes captured | Approval/denial, create/join, add/install, marketplace, and memory mutations intentionally untouched | No remaining safe top-level surface required for this pass |

## Saved evidence

- `screenshots/landing-thread-new.png` — full-page landing screenshot
- `screenshots/model-catalog-latest.png` — expanded model catalog screenshot
- `screenshots/composer-settings-integrations.png` — integrations submenu screenshot
- `screenshots/full-model-settings.png` — full settings dialog screenshot
- `screenshots/delegation-settings.png` — agent defaults/delegation screenshot
- `screenshots/autonomy-capabilities.png` — autonomy and capability surface screenshot
- `screenshots/model-settings-parent.png` — current model/effort/tools/integrations parent menu
- `screenshots/model-settings-catalog.png` — latest model catalog
- `screenshots/model-settings-anthropic.png` — Anthropic model catalog
- `screenshots/model-settings-openai.png` — OpenAI model catalog
- `screenshots/model-settings-other-providers.png` — other-provider catalog
- `screenshots/model-settings-open-weights.png` — open-weights catalog
- `screenshots/reasoning-effort-levels.png` — five reasoning levels
- `screenshots/model-settings-gemini-no-reasoning.png` — Gemini branch without reasoning control
- `screenshots/model-settings-full-current.png` — full current model settings
- `screenshots/model-settings-subagents.png` — subagent model settings
- `screenshots/model-settings-autonomy.png` — autonomy and timeout settings
- `screenshots/model-settings-capabilities.png` — capability settings
- `screenshots/model-settings-full-reasoning-open.png` — full-settings reasoning options
- `screenshots/model-settings-restored-luna.png` — restored GPT 5.6 Luna branch
- `screenshots/landing-more-options.png` — More… quick-action menu
- `screenshots/composer-add-context.png` — Add files or context root menu
- `screenshots/use-an-agent-picker.png` — Use an agent picker
- `screenshots/create-agent-identity.png` — Create-agent Identity step
- `screenshots/create-agent-model.png` — Create-agent Model step
- `screenshots/agent-integration-catalog.png` — create-agent integration catalog
- `screenshots/sidebar-skills.png` — Skills inventory surface
- `screenshots/sidebar-projects.png` — Projects surface
- `screenshots/sidebar-library.png` — Library filters/search surface
- `screenshots/sidebar-marketplace.png` — Marketplace cards/search surface
- `screenshots/sidebar-teams.png` — Teams surface
- `screenshots/sidebar-memories.png` — Memories controls and count
- `screenshots/sidebar-learning.png` — Improvements/Learning surface
- `screenshots/sidebar-rubrics.png` — Rubrics loading surface
- `screenshots/sidebar-inbox.png` — Inbox approval items
- `screenshots/command-center.png` — Command Center dashboard
- `screenshots/global-search.png` — Global search palette

Additional notes are in `model-variant-matrix.md`, `composer-options.md`, `agent-create-surface.md`, `integration-catalog.md`, and `sidebar-surfaces.md`.

## Stop condition for this pass

The probe remains read-only. The tab was navigated into the create-agent flow only to inspect its setup steps; no form input was entered and no agent was created. Return to `/threads/new` before handing back to the user.
