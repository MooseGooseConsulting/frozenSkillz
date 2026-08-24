# HyperAgent Wave 0.2 coverage ledger

Status: initial probe paused by user (read-only)

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
| HyperAgent landing / new thread | Sidebar navigation; composer; quick actions; recent threads; resource links | Landing screenshot and DOM snapshot captured | Send is disabled until input | Open remaining safe composer controls |
| Thread settings → Model | Latest models, provider groups, reasoning effort, tools, integrations, full settings | Model menu and all provider/effort/tool/integration submenus opened; screenshot captured | Model buttons not selected; tool/integration toggles not changed | Inspect full settings and other composer menus |
| Full settings / agent defaults | Model & compute; Subagents; Autonomy & safety; Capabilities; Home thread delegation | Opened via `Open full settings`; inspected delegation scope, execution modes, timeout buttons, named capabilities, integration scope | No radios, buttons, switches, combobox options, or reset controls changed | Return to landing and continue composer controls |

## Saved evidence

- `screenshots/landing-thread-new.png` — full-page landing screenshot
- `screenshots/model-catalog-latest.png` — expanded model catalog screenshot
- `screenshots/composer-settings-integrations.png` — integrations submenu screenshot
- `screenshots/full-model-settings.png` — full settings dialog screenshot
- `screenshots/delegation-settings.png` — agent defaults/delegation screenshot
- `screenshots/autonomy-capabilities.png` — autonomy and capability surface screenshot

## Stop condition for this pass

The user paused the probe after the landing screen was reached. Resume with the controls beneath the text box; do not infer that any model invocation or write is safe.
