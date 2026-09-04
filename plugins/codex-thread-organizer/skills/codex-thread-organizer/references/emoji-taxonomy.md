# Semantic emoji taxonomy

Applied titles use three to five leading emoji, normally three or four. Each
emoji must supply a different retrievable signal: a domain, a work type, and a
state, relationship, retention role, or second precise domain. Do not add
decorative duplicates just to reach the count.

## Domain signals

| Emoji | Meaning |
| --- | --- |
| `🤖` | AI agents, LLMs, evaluations, or automation |
| `☁️` | Cloud, remote compute, or hosted services |
| `🖥️` | Hardware, GPUs, workstations, or local infrastructure |
| `🏠` | Homelab, property, or home systems |
| `🛰️` | Robotics, sensors, networking, or autonomy |
| `💾` | Storage, data retention, or databases |
| `🔐` | Identity, security, secrets, or access control |
| `🌐` | Websites, browsers, domains, or web integrations |
| `🎨` | Design, media, visual production, or creative tools |
| `🧾` | Personal administration, billing, orders, or records |

Use two domain signals only when both identify the work more precisely, such as
`☁️ 🖥️` for cloud GPU serving or `🏠 🛰️` for a home-network sensor system.

## Work-type signals

| Emoji | Meaning |
| --- | --- |
| `🛠️` | Implementation, repair, or configuration change |
| `🔍` | Research, review, diagnosis, or investigation |
| `🧪` | Test, experiment, evaluation, or verification |
| `🧭` | Planning, architecture, or decision framing |
| `📝` | Documentation or writing as the primary deliverable |
| `🧹` | Cleanup, consolidation, or retirement |
| `📦` | Delivery, integration, packaging, or release work |

## State, relationship, and retention signals

| Emoji | Meaning |
| --- | --- |
| `✅` | The bounded task is complete |
| `🟡` | A concrete action remains with the current owner |
| `🔴` | The clearest highest-priority unfinished task; use sparingly |
| `⏸️` | A named user or external response is next |
| `🚧` | A specific obstacle blocks required work |
| `📌` | Canonical task or durable reference |
| `↪️` | Work continued or was superseded elsewhere |
| `🗄️` | Archive candidate |

Codex-sidebar titles may use these markers after the lifecycle review. ChatGPT
web titles use them only when the user explicitly asks for a status-oriented
view; otherwise use a second domain signal or a documented retrieval role.

## Combination seeds

| Prefix | Suitable use |
| --- | --- |
| `🤖 🧪 🔍` | Agent or model evaluation research |
| `☁️ 🖥️ 🛠️` | Cloud GPU or model-serving implementation |
| `🏠 🛰️ 🛠️` | Homelab sensor, network, or automation work |
| `💾 🖥️ 🔍` | Storage or hardware investigation |
| `🔐 🌐 🛠️` | OAuth, identity, or web-access implementation |
| `🎨 🌐 🛠️` | Creative or web-interface implementation |
| `🧾 🔍 ✅` | Completed billing, order, or records investigation |

These are seeds, not a closed ontology. Choose familiar emoji that visibly
render in the selected client; replace an uncertain symbol with a clear existing
one rather than guessing at a newly released emoji.
