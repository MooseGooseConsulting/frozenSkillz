# Semantic Emoji Taxonomy

This taxonomy uses released Unicode Emoji v17.0 as the active set. CLDR short
names and code points are recorded so an emoji remains semantic metadata rather
than decoration. Verify rendering in the destination client; multi-code-point
sequences and font fallback can consume different visual width even when their
UTF-16 count is known.

| Emoji | CLDR short name | Code point / sequence | Organization meaning | Ambiguity / rendering note |
|---|---|---|---|---|
| 🛠️ | hammer and wrench | U+1F6E0 U+FE0F | implementation, repair, tooling | do not use for planning-only work |
| 🔍 | magnifying glass tilted left | U+1F50D | investigation, research, diagnosis | not a completion marker |
| 📝 | memo | U+1F4DD | documentation or written decision | avoid for ordinary chat-only replies |
| 🧭 | compass | U+1F9ED | planning, navigation, strategy | can be mistaken for location |
| 🧪 | test tube | U+1F9EA | experiment, validation, evaluation | distinguish from production delivery |
| 📦 | package | U+1F4E6 | packaging, release, distribution | not generic project work |
| 🔐 | locked | U+1F510 | security, identity, credentials | never signals that a secret is safe to expose |
| 🗃️ | card file box | U+1F5C3 U+FE0F | data archive, history, records | not a deletion marker |
| 🌐 | globe with meridians | U+1F310 | web, browser, external service | avoid when only a local app is involved |
| 🧩 | puzzle piece | U+1F9E9 | integration, plugin, component relation | avoid as a vague “interesting” label |
| ⚙️ | gear | U+2699 U+FE0F | configuration, automation, runtime | can overlap with implementation |
| 📊 | bar chart | U+1F4CA | analytics, report, measurement | use only when analysis is central |
| 🗂️ | card index dividers | U+1F5C2 U+FE0F | organization, taxonomy, project grouping | not a storage/back-up claim |
| 🔄 | counterclockwise arrows button | U+1F504 | synchronization, migration, refresh | do not use for a vague revisit |

## Unicode Emoji v18.0 Beta Preview — Never Apply Without Chrome Proof

These entries are preview-only. Unicode labels v18.0 as beta and lists v17.0 as
the current release. Before use, open a real Chrome page containing the exact
character, confirm the rendered glyph (not tofu/fallback), and record that
observation in proposal evidence.

| Emoji | CLDR short name | Code point | Potential organization meaning | Warning |
|---|---|---|---|---|
| 🫫 | cracking face | U+1FAEB | brittle failure or recovery review | never replace a clear failure description |
| 🫹 | leftwards thumb sign | U+1FAF9 | directional comparison only | gesture meaning varies by culture |
| 🫺 | rightwards thumb sign | U+1FAFA | directional comparison only | gesture meaning varies by culture |
| 🫌 | monarch butterfly | U+1FACC | transformation/migration workstream | do not use as a generic “nature” marker |
| 🫝 | pickle | U+1FADD | no default organizer use | high semantic ambiguity |
| 🛙 | lighthouse | U+1F6D9 | navigation/reference authority | must not imply a live safety signal |
| 🪋 | meteor | U+1FA8B | incident/event analysis | visually unsupported on older clients |
| 🪌 | eraser | U+1FA8C | correction or removal proposal | do not imply destructive action occurred |
| 🪍 | net with handle | U+1FA8D | collection/harvest pipeline | visually unsupported on older clients |

Sources: [Unicode Emoji v17.0 charts](https://unicode.org/emoji/charts/) and
[Unicode Emoji v18.0 beta charts](https://www.unicode.org/emoji/charts-18.0/).
