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

## Saved evidence

- `screenshots/landing-thread-new.png` — full-page landing screenshot
- `screenshots/model-catalog-latest.png` — expanded model catalog screenshot
- `screenshots/composer-settings-integrations.png` — integrations submenu screenshot
- `screenshots/full-model-settings.png` — full settings dialog screenshot
- `screenshots/delegation-settings.png` — agent defaults/delegation screenshot
- `screenshots/autonomy-capabilities.png` — autonomy and capability surface screenshot
- `screenshots/landing-more-options.png` — More… quick-action menu
- `screenshots/composer-add-context.png` — Add files or context root menu
- `screenshots/use-an-agent-picker.png` — Use an agent picker
- `screenshots/create-agent-identity.png` — Create-agent Identity step
- `screenshots/create-agent-model.png` — Create-agent Model step
- `screenshots/agent-integration-catalog.png` — create-agent integration catalog

Additional notes are in `model-variant-matrix.md`, `composer-options.md`, `agent-create-surface.md`, and `integration-catalog.md`.

## Stop condition for this pass

The probe remains read-only. The tab was navigated into the create-agent flow only to inspect its setup steps; no form input was entered and no agent was created. Return to `/threads/new` before handing back to the user.
