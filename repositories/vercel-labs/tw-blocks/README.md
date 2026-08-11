# TW-Blocks

A semantic spacing system for Tailwind CSS v4, providing consistent layouts with block and tab units.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

TW-Blocks is a Tailwind CSS v4 plugin that introduces a two-unit spacing system:

- **Block units** - Component sizes (inputs, buttons, toolbars) - Default: 32px
- **Tab units** - Padding and spacing - Default: 4px
- **Ratio** - 4 tabs = 1 block for predictable layouts

## Installation

### For AI Coding Assistants (Recommended)

Add the TW-Blocks skill to your AI assistant (Cursor, Windsurf, etc.):

```bash
npx skills add vercel-labs/tw-blocks
```

This enables your AI to use TW-Blocks patterns automatically when building UIs.

### Manual Installation

```bash
pnpm add tw-blocks
```

## Setup

Add to your CSS file:

```css
@import "tailwindcss";
@import "tw-blocks";
```

That's it! No configuration file needed.

## Usage

```html
<!-- Button: 32px height, 16px horizontal padding -->
<button class="h-block-1 px-tab-4 rounded-tab-2">
  Click me
</button>

<!-- Input: 48px height -->
<input class="h-block-1.5 px-tab-4 rounded-tab-2" placeholder="Enter text">

<!-- Card: 24px padding, 12px border radius -->
<div class="p-tab-6 rounded-tab-3 bg-white shadow-md">
  Card content
</div>

<!-- Sidebar: 256px width -->
<aside class="w-block-8 h-screen bg-gray-900">
  Navigation
</aside>
```

## Available Classes

### Spacing (padding, margin, gap)
```
p-tab-{0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32}
p-block-{0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16}
```

### Sizing (width, height)
```
h-block-{0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16}
w-block-{0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16}
```

### Border Radius
```
rounded-block-{0.5, 1}
rounded-tab-{1, 2, 3, 4}
```

## Customization

Override the base sizes in your CSS:

```css
@layer theme {
  :root {
    --spacing-block: 2.5rem;  /* 40px instead of 32px */
    --spacing-tab: 0.5rem;    /* 8px instead of 4px */
  }
}
```

## Examples

View production-ready examples:
- [Dashboard](https://github.com/vercel-labs/tw-blocks/tree/main/examples/dashboard) - Enterprise dashboard with sidebar
- [Design Tool](https://github.com/vercel-labs/tw-blocks/tree/main/examples/design-tool) - Design tool interface
- [3D Editor](https://github.com/vercel-labs/tw-blocks/tree/main/examples/editor-3d) - 3D editor UI

## Documentation

Full documentation available in the docs app. Deploy to Vercel or run locally:

```bash
pnpm --filter docs dev
```

## LLM Integration

This library is LLM-ready:
- **llms.txt** - AI crawler discovery
- **Skill file** - Complete guide at `SKILLS/tw-blocks/SKILL.md`
- **Markdown API** - Request with `Accept: text/markdown` header

Use the skill file with ChatGPT/Claude to generate UI components automatically.

## Monorepo Structure

```
tw-blocks/
├── packages/design-system/   # The tw-blocks plugin
├── apps/
│   ├── docs/                 # Documentation site
│   └── ui-analyzer/          # Screenshot comparison tool
└── examples/                 # Production examples
    ├── dashboard/
    ├── design-tool/
    └── editor-3d/
```

## Development

```bash
# Install dependencies
pnpm install

# Start docs
pnpm --filter docs dev

# Start an example
pnpm --filter dashboard dev

# Build everything
pnpm build

# Run tests
pnpm test
```

## Requirements

- Node.js 18+
- pnpm 8+
- Tailwind CSS v4+

## Tech Stack

- Tailwind CSS v4.2.0
- Next.js 14.2.35
- React 18.2.0
- TypeScript
- Turbo (monorepo build system)

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

This is a Vercel Labs project. Contributions welcome!

## Links

- **Repository:** [vercel-labs/tw-blocks](https://github.com/vercel-labs/tw-blocks)
- **Documentation:** Deploy docs to see full guide
- **Examples:** See `/examples` directory

---

**Built by Vercel Labs**
