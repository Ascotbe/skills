# Contentstack Vibe Docs

An [Agent Skill](https://agentskills.io/) that gives AI coding agents comprehensive Contentstack CMS knowledge. Works with Claude Code, Cursor, GitHub Copilot, VS Code, Gemini CLI, Roo Code, and [25+ other tools](https://agentskills.io/).

> **AI Agents: Read [`skills/contentstack-vibe-docs/SKILL.md`](skills/contentstack-vibe-docs/SKILL.md).** It contains routing rules that direct you to the 1-3 files you need. Do not read all files — this skill contains ~13,500 lines across 34 reference documents.

---

## Install

### Universal (all agents)

Install with the [skills CLI](https://skills.sh/docs/cli):

```bash
npx skills add contentstack/contentstack-vibe-docs
```

This auto-detects your installed agents (Claude Code, Cursor, Copilot, Windsurf, Cline, etc.) and installs the skill for all of them.

Install for specific agents only:

```bash
npx skills add contentstack/contentstack-vibe-docs -a claude-code
npx skills add contentstack/contentstack-vibe-docs -a cursor
npx skills add contentstack/contentstack-vibe-docs -a github-copilot
```

Install globally (available in all your projects):

```bash
npx skills add contentstack/contentstack-vibe-docs -g
```

### Claude Code

Install as a personal skill (all projects):

```bash
claude skill add contentstack/contentstack-vibe-docs
```

Or use the skills CLI:

```bash
npx skills add contentstack/contentstack-vibe-docs -a claude-code -g
```

Once installed, Claude Code discovers the skill automatically when you work on Contentstack tasks. You can also invoke it directly:

```
/contentstack-vibe-docs fetch blog posts with author references
/contentstack-vibe-docs set up live preview in Next.js
/contentstack-vibe-docs optimize images for responsive layouts
```

### Gemini CLI

```bash
gemini skills install https://github.com/contentstack/contentstack-vibe-docs.git
```

Install to workspace scope:

```bash
gemini skills install https://github.com/contentstack/contentstack-vibe-docs.git --scope workspace
```

### Manage installed skills

```bash
npx skills list              # List all installed skills
npx skills check             # Check for updates
npx skills update            # Update all skills
```

### Claude Code Plugin

This repo is also a [Claude Code plugin](https://code.claude.com/docs/en/plugins). Install it directly:

```bash
claude plugin install https://github.com/contentstack/contentstack-vibe-docs
```

Or test locally during development:

```bash
claude --plugin-dir ./contentstack-vibe-docs
```

The plugin includes:
- **Skills** — the full Contentstack documentation skill with routing and references

### Cursor Plugin

This repo is also a [Cursor plugin](https://cursor.directory/plugins/contentstack). Install it directly in Cursor:

1. Open Cursor Settings > Plugins
2. Add this repository URL: `https://github.com/contentstack/contentstack-vibe-docs`

The plugin includes:
- **Skills** — the full Contentstack documentation skill with routing and references
- **Rules** — `rules/contentstack.mdc` with routing table, decision helpers, security guardrails, and quick patterns

### Cursor (manual install)

If you prefer not to use the plugin marketplace, copy the `.mdc` rule file directly into your project:

```bash
git clone --depth 1 https://github.com/contentstack/contentstack-vibe-docs.git /tmp/cs-skills && \
  mkdir -p .cursor/rules && \
  cp /tmp/cs-skills/cursor/rules/*.mdc .cursor/rules/ && \
  rm -rf /tmp/cs-skills
```

Cursor auto-discovers `.cursor/rules/*.mdc` on project open.

### Codex CLI

Codex auto-discovers `AGENTS.md` in your project root. Copy the prebuilt `codex/` directory in:

```bash
git clone --depth 1 https://github.com/contentstack/contentstack-vibe-docs.git /tmp/cs-skills && \
  cp -r /tmp/cs-skills/codex . && \
  rm -rf /tmp/cs-skills
```

This places `codex/AGENTS.md` and `codex/skills/contentstack-vibe-docs/` in your project. Codex reads `AGENTS.md`, which routes it to the skill.

### Any other agent (manual)

Every major agent reads at least one of: `CLAUDE.md`, `AGENTS.md`, `skills/*/SKILL.md`, or `.cursor/rules/*.mdc`. Point your agent at the repo root or copy `skills/contentstack-vibe-docs/` into your project — the routing table in `SKILL.md` does the rest.

---

## How It Works

This skill uses **progressive disclosure** to keep your agent's context window clean:

1. **Discovery** (~100 tokens) — The agent loads the skill name and description. Just enough to know "this is relevant for Contentstack tasks."
2. **Activation** (~3,500 tokens) — When a Contentstack task is detected, the agent reads `SKILL.md` with its routing table, decision helpers, and inline quick-start patterns.
3. **Execution** (on-demand) — The routing table directs the agent to read only the 1-3 specific reference files it needs. It never loads all ~13,500 lines.

```
User: "Add live preview to my Next.js app"
  → Agent loads skills/contentstack-vibe-docs/SKILL.md (routing table)
  → Reads skills/contentstack-vibe-docs/references/live-preview/concepts.md
  → Reads skills/contentstack-vibe-docs/references/live-preview/ssr-mode.md
  → Reads skills/contentstack-vibe-docs/references/frameworks/nextjs.md
  → Implements with copy-paste ready code
```

---

## What's Covered

| Topic | Reference File |
|-------|---------------|
| Quick code patterns | [QUICK_REFERENCE.md](skills/contentstack-vibe-docs/references/QUICK_REFERENCE.md) |
| CMS fundamentals | [base-concepts.md](skills/contentstack-vibe-docs/references/concepts/base-concepts.md) |
| Data modeling best practices | [data-modeling-best-practices.md](skills/contentstack-vibe-docs/references/concepts/data-modeling-best-practices.md) |
| Region configuration | [regions.md](skills/contentstack-vibe-docs/references/concepts/regions.md) |
| REST Content Delivery API | [rest-api.md](skills/contentstack-vibe-docs/references/api/rest-api.md) |
| GraphQL Content Delivery API | [graphql-api.md](skills/contentstack-vibe-docs/references/api/graphql-api.md) |
| Content Management API (CRUD) | [content-management-api.md](skills/contentstack-vibe-docs/references/api/content-management-api.md) |
| Image Delivery API (transforms) | [image-delivery-api.md](skills/contentstack-vibe-docs/references/api/image-delivery-api.md) |
| TypeScript Delivery SDK | [delivery-sdk.md](skills/contentstack-vibe-docs/references/sdk/delivery-sdk.md) |
| Live Preview (concepts) | [concepts.md](skills/contentstack-vibe-docs/references/live-preview/concepts.md) |
| Live Preview (CSR mode) | [csr-mode.md](skills/contentstack-vibe-docs/references/live-preview/csr-mode.md) |
| Live Preview (SSR mode) | [ssr-mode.md](skills/contentstack-vibe-docs/references/live-preview/ssr-mode.md) |
| Next.js patterns | [nextjs.md](skills/contentstack-vibe-docs/references/frameworks/nextjs.md) |
| Nuxt patterns | [nuxt.md](skills/contentstack-vibe-docs/references/frameworks/nuxt.md) |
| Gatsby patterns | [gatsby.md](skills/contentstack-vibe-docs/references/frameworks/gatsby.md) |
| OAuth with Auth.js | [oauth.md](skills/contentstack-vibe-docs/references/authentication/oauth.md) |
| CLI plugin development | [cli-plugins/overview.md](skills/contentstack-vibe-docs/references/extensions/cli-plugins/overview.md) |
| Developer Hub apps | [devhub-apps.md](skills/contentstack-vibe-docs/references/extensions/devhub-apps.md) |
| Real-world code examples | [practical-examples.md](skills/contentstack-vibe-docs/references/examples/practical-examples.md) |
| Package version compatibility | [VERSIONS.md](skills/contentstack-vibe-docs/references/VERSIONS.md) |

All regions supported: US, EU, AU, Azure NA/EU, GCP NA/EU.

---

## Security & Guardrails

This skill includes built-in security measures and red flags that instruct agents to handle credentials safely:

- **No secret leaking** — Agents are explicitly told to never ask for, output, log, or hardcode API keys, tokens, or secrets. All code uses `process.env.*` references.
- **Credential hygiene** — If a developer accidentally pastes a real token in the conversation, the agent is instructed to warn them and suggest they rotate it.
- **Frontend protection** — Management Tokens are flagged as server-side only. Agents are told to never expose them in frontend code.
- **`.env` safety** — Agents are instructed to never commit `.env` files or credentials to version control.
- **Red flags checklist** — A dedicated "Red Flags" section in `SKILL.md` lists specific anti-patterns agents must avoid, from hardcoding secrets to mixing SDK patterns incorrectly.
- **Questions before code** — Agents are guided to ask about region, framework, and environment setup before writing any code, ensuring the right patterns are used from the start.

---

## Documentation Structure

This repo follows the [Open Plugins](https://open-plugins.com/plugin-builders) standard and the [agentskills.io](https://agentskills.io/) skill-directory convention. The skill itself is canonical — everything else is either a root-level pointer or a generated per-harness copy.

```
CLAUDE.md                    # Root pointer for Claude Code (project context)
AGENTS.md                    # Root pointer for agentskills.io / Codex / generic agents
README.md                    # This file
gemini-extension.json        # Manifest for `gemini skills install`

.plugin/plugin.json          # Open Plugins manifest
.claude-plugin/plugin.json   # Claude Code plugin manifest
.cursor-plugin/plugin.json   # Cursor plugin manifest

skills/
└── contentstack-vibe-docs/  # ★ Source of truth — the skill itself
    ├── SKILL.md             # Routing table + decision helpers
    └── references/          # 34 reference files (see tree below)

rules/
└── contentstack.mdc         # Source — Cursor rule (points at SKILL.md)

codex/                       # Generated — copy into your project for Codex CLI
├── AGENTS.md                # (hand-written, not generated)
└── skills/contentstack-vibe-docs/
    ├── SKILL.md
    └── references/

cursor/
└── rules/contentstack.mdc   # Generated — for manual `.cursor/rules/` install

scripts/
└── build.sh                 # Regenerates codex/ and cursor/ from the canonical source

skills/contentstack-vibe-docs/references/
├── QUICK_REFERENCE.md          # Condensed patterns for quick lookup
├── VERSIONS.md                 # Package version compatibility
├── concepts/
│   ├── base-concepts.md        # CMS fundamentals
│   ├── data-modeling-best-practices.md  # Schema design + taxonomy CDA operators
│   ├── localization.md         # Master language, fallback chains, non-localizable fields
│   └── regions.md              # Region configuration
├── api/
│   ├── rest-api.md             # REST Content Delivery API
│   ├── graphql-api.md          # GraphQL Content Delivery API
│   ├── content-management-api.md  # CMA (CRUD, modular block schema, headers)
│   └── image-delivery-api.md   # Image transforms + asset organization + limits
├── sdk/
│   └── delivery-sdk.md         # TypeScript SDK guide (region-aware preview)
├── live-preview/
│   ├── concepts.md             # Live Preview overview
│   ├── csr-mode.md             # ssr:false — postMessage updates
│   ├── ssr-mode.md             # ssr:true — per-request factory pattern
│   ├── visual-builder.md       # Edit tags, addEditableTags, VB_EmptyBlockParentClass
│   └── debugging.md            # Symptom-based diagnostic guide
├── authentication/
│   └── oauth.md                # OAuth login with Auth.js v5 (Next.js)
├── security/
│   ├── tokens-authentication.md  # Delivery/Preview/Management/Authtoken/OAuth decision tree
│   └── roles-permissions.md    # Built-in roles, custom roles, teams
├── workflows/
│   ├── webhooks.md             # Event channels, signature verification, release storms
│   ├── releases.md             # Atomic coordinated content deployment
│   ├── content-workflows.md    # Workflow stages, publish rules, approval gates
│   ├── branches-aliases.md     # Zero-downtime deployment via aliases
│   └── environments-publishing.md  # Publishing lifecycle, Sync API, rate limits
├── personalization/
│   └── variants-and-personalize.md  # Variants vs separate entries + Personalize SDK
├── frameworks/
│   ├── nextjs.md               # Next.js patterns + Draft Mode + revalidateTag
│   ├── nuxt.md                 # Nuxt 4 patterns
│   └── gatsby.md               # Gatsby patterns
├── extensions/
│   ├── cli-plugins/            # CLI plugin development (overview + commands + publishing)
│   │   ├── overview.md
│   │   ├── commands.md
│   │   └── publishing.md
│   ├── devhub-apps.md          # Developer Hub apps (App SDK, UI locations, API proxy)
│   └── launch.md               # Contentstack Launch deployments + env sync
└── examples/
    └── practical-examples.md   # Real-world code patterns
```

### Maintainer note

The single source of truth is **`skills/contentstack-vibe-docs/`** (SKILL.md + references/) and **`rules/contentstack.mdc`**. Everything under `codex/skills/` and `cursor/rules/` is generated — do not edit those directly. After editing a source file, run:

```bash
bash scripts/build.sh
```

Generated files are committed so GitHub / zip-download installs work without running the script locally.

---

## Support

- [Contentstack Documentation](https://www.contentstack.com/docs)
- [Discord Community](https://community.contentstack.com)
- [Contentstack Support](https://www.contentstack.com/support)
- [Agent Skills Specification](https://agentskills.io/)

---

## License

This documentation is provided as-is for use with AI coding assistants.
