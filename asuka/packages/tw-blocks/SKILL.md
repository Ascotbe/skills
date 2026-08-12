---
name: tw-blocks
description: Semantic spacing system for Tailwind CSS v4 using block (32px) and tab
  (4px) units. Use when building UIs with consistent spacing, dashboards, admin panels,
  design tools, or any interface requiring a harmonious spacing system. Provides patterns
  for buttons, inputs, cards, toolbars, panels, and layouts.
---
# TW-Blocks Design System

## Core Principles

TW-Blocks provides semantic spacing using two fundamental units:

- **Block (2rem / 32px)**: Component sizes - buttons, inputs, headers, toolbars, avatars
- **Tab (0.25rem / 4px)**: Padding, margins, gaps - spacing between and within elements

**The 4:1 Ratio**: 4 tabs = 1 block. This creates predictable, harmonious layouts.

```
1 block = 32px = 4 tabs
████████  ████████  ████████  ████████
 tab-1     tab-2     tab-3     tab-4
  4px       8px       12px      16px
```

---

## Installation & Setup

```bash
pnpm add tw-blocks
```

```css
/* app/globals.css */
@import "tailwindcss";
@import "tw-blocks";
```

---

## Class Reference

### Tab Spacing Scale (17 values)
| Class suffix | Value | Pixels |
|--------------|-------|--------|
| `tab-0` | 0 | 0px |
| `tab-0.5` | 0.5 × tab | 2px |
| `tab-1` | 1 × tab | 4px |
| `tab-1.5` | 1.5 × tab | 6px |
| `tab-2` | 2 × tab | 8px |
| `tab-2.5` | 2.5 × tab | 10px |
| `tab-3` | 3 × tab | 12px |
| `tab-4` | 4 × tab | 16px |
| `tab-5` | 5 × tab | 20px |
| `tab-6` | 6 × tab | 24px |
| `tab-8` | 8 × tab | 32px |
| `tab-10` | 10 × tab | 40px |
| `tab-12` | 12 × tab | 48px |
| `tab-16` | 16 × tab | 64px |
| `tab-20` | 20 × tab | 80px |
| `tab-24` | 24 × tab | 96px |
| `tab-32` | 32 × tab | 128px |

### Block Spacing Scale (14 values)
| Class suffix | Value | Pixels |
|--------------|-------|--------|
| `block-0` | 0 | 0px |
| `block-0.5` | 0.5 × block | 16px |
| `block-1` | 1 × block | 32px |
| `block-1.5` | 1.5 × block | 48px |
| `block-2` | 2 × block | 64px |
| `block-2.5` | 2.5 × block | 80px |
| `block-3` | 3 × block | 96px |
| `block-4` | 4 × block | 128px |
| `block-5` | 5 × block | 160px |
| `block-6` | 6 × block | 192px |
| `block-8` | 8 × block | 256px |
| `block-10` | 10 × block | 320px |
| `block-12` | 12 × block | 384px |
| `block-16` | 16 × block | 512px |

### Border Radius Values
| Class | Value | Pixels |
|-------|-------|--------|
| `rounded-tab-1` | 1 × tab | 4px |
| `rounded-tab-2` | 2 × tab | 8px |
| `rounded-tab-3` | 3 × tab | 12px |
| `rounded-tab-4` | 4 × tab | 16px |
| `rounded-block-0.5` | 0.5 × block | 16px |
| `rounded-block-1` | 1 × block | 32px (fully round) |

### Supported Tailwind Utilities
All standard Tailwind spacing utilities work with block/tab:
- **Padding**: `p-tab-4`, `px-tab-3`, `py-tab-2`, `p-block-1`
- **Margin**: `m-tab-4`, `mx-tab-3`, `my-tab-2`, `m-block-1`
- **Gap**: `gap-tab-4`, `gap-x-tab-3`, `gap-block-1`
- **Width/Height**: `w-block-2`, `h-block-1`, `size-block-1`
- **Inset**: `top-tab-2`, `left-tab-4`, `inset-block-1`
- **Space**: `space-x-tab-2`, `space-y-tab-4`

---

## Quick Patterns

### Button
```html
<button class="h-block-1 px-tab-4 rounded-tab-2 bg-blue-500 text-white">Click me</button>
```

### Small Button
```html
<button class="h-tab-6 px-tab-3 rounded-tab-1.5 text-sm">Small</button>
```

### Icon Button
```html
<button class="size-block-1 flex items-center justify-center rounded-tab-2">
  <svg class="w-tab-4 h-tab-4" />
</button>
```

### Input Field
```html
<input type="text" class="h-block-1 px-tab-3 rounded-tab-2 border border-gray-300" />
```

### Card
```html
<div class="p-tab-4 rounded-block-0.5 bg-white shadow-sm border">
  <h3 class="text-lg font-semibold">Title</h3>
  <p class="mt-tab-2 text-gray-600">Description</p>
</div>
```

---

## Best Practices

### Component Height Guidelines
| Component | Height | Class |
|-----------|--------|-------|
| Standard button | 32px | `h-block-1` |
| Small button | 24px | `h-tab-6` |
| Large button | 48px | `h-block-1.5` |
| Input field | 32px | `h-block-1` |
| Small input | 24px | `h-tab-6` |
| Toolbar | 48px | `h-block-1.5` |
| Header (main) | 64px | `h-block-2` |
| Status bar | 24px | `h-tab-6` |
| Avatar (small) | 32px | `size-block-1` |
| Avatar (large) | 48px | `size-block-1.5` |

### Horizontal Padding Standards
| Container | Padding |
|-----------|---------|
| Page content | `px-tab-6` |
| Card | `p-tab-4` |
| Button | `px-tab-4` |
| Input | `px-tab-3` |
| Panel section | `p-tab-2` or `p-tab-3` |
| Header | `px-tab-4` |

### Border Radius Guidelines
| Element | Radius |
|---------|--------|
| Button | `rounded-tab-2` (8px) |
| Card | `rounded-block-0.5` (16px) |
| Input | `rounded-tab-2` (8px) |
| Small badge | `rounded-tab-1` (4px) |
| Avatar | `rounded-full` |

### UI Density Patterns

**Compact UI** (Code editors, IDEs, tools):
- Toolbar: `h-block-1` (32px)
- List items: `h-tab-5` or `h-tab-6` (20-24px)
- Padding: `p-tab-2`, `px-tab-3`
- Gaps: `gap-tab-1`, `gap-tab-2`

**Normal UI** (Dashboards, apps):
- Header: `h-block-2` (64px)
- Buttons: `h-block-1` (32px)
- Cards: `p-tab-4` or `p-tab-6`
- Gaps: `gap-tab-4`, `gap-tab-6`

**Spacious UI** (Marketing, content):
- Headers: `h-block-2.5` or `h-block-3`
- Cards: `p-tab-8`, `p-tab-12`
- Gaps: `gap-tab-8`, `gap-tab-12`

---

## Combining with Standard Tailwind

TW-Blocks focuses on **spacing and sizing**. Use standard Tailwind for everything else:

### ✅ Use Standard Tailwind For:
- Colors: `bg-blue-500`, `text-gray-700`, `border-gray-200`
- Typography: `text-sm`, `font-bold`
- Flexbox/Grid: `flex`, `grid`, `items-center`
- Borders: `border`, `border-t`
- Effects: `shadow-md`, `hover:bg-gray-100`

### ❌ Avoid Standard Tailwind For:
- Spacing: Use `p-tab-4` not `p-4`
- Component sizing: Use `h-block-1` not `h-8`
- Block-aligned radius: Use `rounded-tab-2` not `rounded-md`

---

## Detailed Patterns

For complete component patterns, see **[references/patterns.md](references/patterns.md)**:

- Dashboard layouts (sidebar, stat cards)
- Toolbars & headers (dashboard, design tool, status bar)
- Panels & sidebars (tool palette, property panels, layers)
- Forms & inputs (buttons, inputs, cards)
- Tables & lists (dense lists, email lists)
- Status indicators (badges, progress bars, selected states)
- Chat & messages (chat bubbles, message lists)
- Charts & data viz (containers, recommended heights)
- Timeline & animation panels
- Code editor interface (full IDE layout)

**Read patterns.md when you need specific implementation examples.**

---

## Common Mistakes to Avoid

### ❌ Don't mix spacing systems
```html
<!-- Bad -->
<div class="p-4 mt-tab-2 mb-8">

<!-- Good -->
<div class="p-tab-4 mt-tab-2 mb-tab-8">
```

### ❌ Don't use blocks for small padding
```html
<!-- Bad -->
<button class="p-block-1">

<!-- Good -->
<button class="px-tab-4 py-tab-2">
```

### ❌ Don't use tabs for component sizing
```html
<!-- Bad -->
<button class="h-tab-8">

<!-- Good -->
<button class="h-block-1">
```

### ✅ Do use fractional values
```html
<div class="p-tab-1.5">  <!-- 6px -->
<div class="h-block-1.5"> <!-- 48px -->
<div class="gap-tab-2.5"> <!-- 10px -->
```

---

## Debugging Tips

### Inspect CSS Variables
```javascript
getComputedStyle(document.documentElement).getPropertyValue('--spacing-block') // "2rem"
getComputedStyle(document.documentElement).getPropertyValue('--spacing-tab')   // "0.25rem"
```

### Test with Visible Borders
```html
<div class="p-tab-4 border-2 border-red-500">
  <div class="h-block-1 border-2 border-blue-500">Button height</div>
</div>
```

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│ BLOCKS (Component Sizing)                                │
│ block-1 = 32px | block-1.5 = 48px | block-2 = 64px      │
├─────────────────────────────────────────────────────────┤
│ TABS (Spacing/Padding)                                   │
│ tab-1 = 4px | tab-2 = 8px | tab-3 = 12px | tab-4 = 16px │
├─────────────────────────────────────────────────────────┤
│ HEIGHT: Button h-block-1 | Header h-block-2 | Toolbar h-block-1.5 │
├─────────────────────────────────────────────────────────┤
│ PADDING: Button px-tab-4 | Card p-tab-4 | Input px-tab-3 │
├─────────────────────────────────────────────────────────┤
│ RADIUS: Button rounded-tab-2 | Card rounded-block-0.5    │
└─────────────────────────────────────────────────────────┘
```
