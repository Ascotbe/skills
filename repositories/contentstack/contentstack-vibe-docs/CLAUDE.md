# Contentstack Vibe Docs

This repository is an [Agent Skill](https://agentskills.io/) providing comprehensive Contentstack CMS documentation for AI coding agents.

**Read [skills/contentstack-vibe-docs/SKILL.md](skills/contentstack-vibe-docs/SKILL.md) first.** It contains the routing table that maps your current task to the 1–3 reference files you need. The full skill spans ~13,500 lines across 32 reference documents — do not read them all.

## How to use this repo

1. Open [skills/contentstack-vibe-docs/SKILL.md](skills/contentstack-vibe-docs/SKILL.md) and match the user's task to the routing table.
2. Read only the referenced file(s) from `skills/contentstack-vibe-docs/references/`.
3. For multi-step tasks (e.g. "new Next.js project"), follow the **Common task combinations** section in `SKILL.md`.

## What's covered

Contentstack REST API, GraphQL API, Content Management API, Image Delivery API, TypeScript Delivery SDK, Live Preview (CSR + SSR modes), OAuth authentication, data modeling, region configuration, CLI plugins, Developer Hub apps, and framework integrations for Next.js, Nuxt, and Gatsby.

## Security

Never ask for, log, or hardcode API keys or tokens. Use `process.env.*`. Management Tokens are server-side only — never expose them in frontend code. See the **Red flags** section in `skills/contentstack-vibe-docs/SKILL.md` and the decision tree in `skills/contentstack-vibe-docs/references/security/tokens-authentication.md`.
