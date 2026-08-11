# Vercel Plugin for Cursor

Vercel development toolkit for Cursor — React/Next.js best practices from Vercel Engineering and deploy to Vercel.

## What's Included

### Skills

**vercel-react-best-practices** — 57 performance optimization rules across 8 categories for React and Next.js, prioritized by impact. The skill dynamically fetches the latest rules from [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) on GitHub, so you always get up-to-date guidance without needing to update the plugin.

Categories (by priority):
1. Eliminating Waterfalls (CRITICAL)
2. Bundle Size Optimization (CRITICAL)
3. Server-Side Performance (HIGH)
4. Client-Side Data Fetching (MEDIUM-HIGH)
5. Re-render Optimization (MEDIUM)
6. Rendering Performance (MEDIUM)
7. JavaScript Performance (LOW-MEDIUM)
8. Advanced Patterns (LOW)

### Commands

**vercel-deploy** — Deploy your project to Vercel using the official Vercel CLI. Handles CLI installation, authentication, and both preview and production deployments.

## Usage

After installing the plugin in Cursor:

- The **react best practices skill** activates automatically when writing, reviewing, or refactoring React/Next.js code. It fetches detailed rule guidance from GitHub as needed.
- Use the **`/vercel-deploy`** command to deploy your project. The agent will walk through CLI setup, authentication, and deployment.

## License

MIT
