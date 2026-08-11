# Skills

Agent Skills for AI coding assistants. These skills follow the [Agent Skills Standard](https://github.com/anthropics/agent-skills-standard) and work with Claude Code, Cursor, Gemini Code Assist, GitHub Copilot, and other compatible tools.

## Installation

```bash
npx skills add Shpigford/skills
```

Or manually:

```bash
git clone https://github.com/Shpigford/skills.git ~/.skills/shpigford
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [build](#build) | Feature development pipeline with research, planning, and phased implementation |
| [but-for-real](#but-for-real) | Skeptical self-review that forces verification before declaring victory |
| [chat-widget](#chat-widget) | Real-time support chat system with user widget and admin dashboard |
| [conductor-setup](#conductor-setup) | Configure a Rails project for Conductor parallel coding agents |
| [favicon](#favicon) | Generate a complete favicon set from a source image |
| [feature-image](#feature-image) | Generate branded social media images for feature announcements |
| [issues](#issues) | Create, list, and view GitHub issues via the gh CLI |
| [learnings](#learnings) | Pre-commit sweep for session insights worth codifying in CLAUDE.md or README.md |
| [new-rails-project](#new-rails-project) | Scaffold a new Rails 8 project with Inertia, React, and Vite |
| [research](#research) | Deep research before planning — parallel agents search docs, web, and codebase |
| [readme](#readme) | Generate absurdly thorough README documentation for any project |
| [screenshots](#screenshots) | Capture retina-quality marketing screenshots with Playwright |

---

### build

A 4-phase feature development pipeline that walks you through research, implementation planning, progress tracking, and phased execution. Each phase produces documented artifacts (RESEARCH.md, IMPLEMENTATION.md, PROGRESS.md) and uses deep research including web search, documentation lookup, and codebase exploration before writing code.

- Subcommands: `research`, `implementation`, `progress`, `phase`, `status`

```bash
/build research chat-interface
/build implementation chat-interface
/build phase 1 chat-interface
```

---

### but-for-real

Forces a ruthless self-review of your own work. Reads the git diff, checks every changed line, hunts for forgotten tests, missed edge cases, dead code, and logic errors. Then actually runs the code to verify it works instead of pattern-matching to "looks correct."

```bash
/but-for-real
```

---

### chat-widget

Builds a complete real-time support chat system: a floating widget for end users and an admin dashboard for support staff. Covers data models, WebSocket channels, REST APIs, frontend components (React, Vue, Rails), email notifications, and message deduplication. Includes framework-specific guidance for Rails, React, Next.js, Laravel, and Vue.

```bash
/chat-widget
```

---

### conductor-setup

Configures a Rails project to work with Conductor, the Mac app for parallel coding agents. Creates `conductor.json`, setup scripts, and a port-aware server script. Updates Redis configuration across Sidekiq, ActionCable, caching, and Rack::Attack to use environment variables for workspace isolation.

```bash
/conductor-setup
```

---

### favicon

Generates a complete set of favicons (ICO, PNG, Apple Touch Icon, web manifest icons) from a single source image using ImageMagick. Auto-detects the project framework to place files in the correct static directory and updates the HTML layout with proper link tags.

Requires: ImageMagick v7+

```bash
/favicon path/to/logo.svg
```

---

### feature-image

Generates branded social media announcement images by analyzing your git history to detect what changed, extracting your brand's colors/fonts/visual patterns from the codebase, building a styled HTML page, and screenshotting it with Playwright. Supports stylized mockup, screenshot+overlay, and abstract styles.

Requires: Playwright

```bash
/feature-image dark mode support
```

---

### issues

Interactive GitHub issue management. Create issues with guided title/body/label prompts, list issues with filters (assignee, author, label), or view issue details. Enforces short, scannable titles and detailed bodies.

Requires: `gh` CLI

```bash
/issues
```

---

### learnings

Pre-commit sweep that reviews the current session's code changes, user corrections, and discoveries to identify anything worth codifying in CLAUDE.md or README.md. Applies a high bar — most sessions produce nothing worth adding, and that's a valid outcome. Proposes edits but never writes to load-bearing files without approval.

Triggers: "anything learned?", "anything to note?", "should we update CLAUDE.md?"

```bash
/learnings
```

---

### new-rails-project

Scaffolds a new Rails 8 project with a full modern stack: Inertia.js + React + Vite + Tailwind CSS + Sidekiq + Redis. Configures UUID primary keys, timestamptz columns, minitest, and RuboCop. Verifies the boilerplate runs via Playwright.

```bash
/new-rails-project my-app
```

---

### research

Deep research skill that runs before planning or implementation. Clarifies ambiguities with the user first, then launches parallel sub-agents to search the codebase, official docs (via Context7), and the web. Synthesizes findings into a structured output with evidence, sources, downsides, and a recommendation — then flows into Plan mode.

- Agents: codebase, docs, web, dependencies, UI, UX, delight (matched to problem complexity)

```bash
/research how should we handle webhook retries
/research why is the dashboard slow on mobile
```

---

### readme

Generates comprehensive README documentation by deeply exploring the codebase first. Covers local setup, architecture (directory structure, request lifecycle, data flow), environment variables, available scripts, testing, deployment (auto-detected platform), and troubleshooting. Writes directly to README.md.

```bash
/readme
```

---

### screenshots

Captures retina-quality (2x) marketing screenshots using Playwright. Analyzes routes and components to discover screenshottable features, handles authentication with smart form detection, and produces consistently sized HiDPI images ready for Product Hunt, social media, or landing pages.

Requires: Playwright

```bash
/screenshots http://localhost:3000
```

---

## Compatibility

These skills work with any Agent Skills Standard-compatible tool:

- Claude Code (Anthropic)
- Cursor
- Gemini Code Assist (Google)
- GitHub Copilot (Microsoft)

## License

MIT
