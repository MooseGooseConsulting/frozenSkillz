# Prior Art: AI Conversation Organization and Codex Thread Control

Date researched: 2026-07-18
Status: initial web scan; refresh before making current-market claims

## Finding

The market contains several pieces of the idea—folders and tags, external Codex command centers, automatic knowledge graphs, project reparenting, and scheduled agent work. The initial scan suggests, but does not prove, that the exact native workflow proposed here remains uncommon: evidence-grounded semantic classification that maintains the existing Codex sidebar through a stable one-to-five-symbol language and reviewable scheduled mutations.

## Relevant systems

### Official Codex capabilities

- [Scheduled tasks](https://learn.chatgpt.com/docs/automations): recurring tasks can invoke skills, run locally against projects, and report results for review.
- [Codex app-server](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md): supports thread listing, reading, naming, archive/unarchive, and related state operations.
- [Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/): frames the app as a command center for parallel agents, projects, skills, and automations.

### Codex-specific adjacent tools

- [Codex Chat Organizer](https://tessl.io/registry/lirantal/codex-chat-organizer): moves existing threads into saved projects by safely patching local Codex state after shutdown. It solves reparenting, not automatic semantic naming.
- [Codex Monitor](https://www.codexmonitor.app/): external desktop command center with workspaces, thread control, worktrees, plans, and reviews.
- [Codex History Viewer](https://marketplace.visualstudio.com/items?itemName=hiztam.codex-history-viewer): local VS Code history browser with search, project views, tags, notes, and archived-session support.

### Cross-platform conversation organization

- [Grasppy](https://grasppy.com/): extracts decisions, artifacts, memory, plans, and entities into a local vault and visual context graph.
- [Threadback](https://threadback.dev/): fully local cross-platform conversation search with folders, tags, and export.
- [ATLAS](https://www.useatlas.space/): captures conversations and generates summaries, tasks, concepts, and per-conversation mind maps.
- [Ditto knowledge graph](https://heyditto.ai/blog/your-personal-knowledge-graph-how-ditto-maps-your-thinking/): automatically extracts subjects and co-occurrence links into an interactive graph.

## Implications for this project

1. Avoid claiming that no one has built AI-chat organization; many products have.
2. Test differentiation around native Codex actionability, stable visual language, scheduled upkeep, evidence, safety, and reversible mutations before claiming a unique market position.
3. Treat a separate knowledge graph as an optional consumer of the classification manifest, not automatically as the first product.
4. Recheck first-party Codex APIs and third-party products before implementation because these surfaces are changing rapidly.
