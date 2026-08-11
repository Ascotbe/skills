---
version: alpha
name: UI Skills
description: Design language for UI Skills.
colors:
  parchment-50: oklch(0.985 0 0)
  parchment-100: oklch(0.97 0 0)
  parchment-200: oklch(0.92 0 0)
  parchment-300: oklch(0.84 0 0)
  parchment-400: oklch(0.7 0 0)
  parchment-500: oklch(0.55 0 0)
  parchment-600: oklch(0.42 0 0)
  parchment-700: oklch(0.3 0 0)
  parchment-800: oklch(0.18 0 0)
  parchment-900: oklch(0.09 0 0)
  primary: oklch(0.09 0 0)
  secondary: oklch(0.42 0 0)
  tertiary: oklch(0.7 0 0)
typography:
  mono:
    fontFamily: JetBrains Mono
---

## Overview

Quiet, editorial, and code-first. UI Skills should feel like a precise developer tool, not a marketing site.

## Colors

- Use the parchment scale for text, borders, muted states, and page backgrounds.
- Use white or `parchment-100` for elevated surfaces and code blocks.
- Keep the palette neutral. Do not add decorative accents or gradients.
- Reserve the darkest values for primary text and important actions.

## Typography

- Use the project sans-serif for interface copy.
- Use JetBrains Mono for commands, code, and technical identifiers.
- Use medium-weight, tight-tracking headings.
- Keep body copy at the base size.
- Use sentence case for labels and links.

## Layout

- Use a narrow centered reading column for documentation.
- Use generous vertical spacing and light section boundaries.
- Use responsive grids for collections.
- Keep mobile padding consistent.
- Let long technical strings wrap or scroll.

## Elevation & Depth

- Use white surfaces with `shadow-2xs`.
- On larger screens, use `ring-1 ring-black/10` instead of visible borders.
- On mobile, use thin top and bottom borders for full-width surfaces.
- Keep elevation subtle.

## Shapes

- Use restrained rounded corners for cards, controls, dialogs, and code blocks.
- Keep long-form content rectangular.
- Use parchment-tinted hover states.

## Components

- Skill cards show the identifier, description, then source.
- Controls use compact neutral outlines or ghost treatments.
- Code blocks use monospace text, clear surfaces, scrolling, and copy support.
- Search uses a focused dialog with keyboard navigation and a clear empty state.

## Do's and Don'ts

- Provide visible focus states.
- Respect reduced motion.
- Give empty states one clear action.
- Do not use glow, gradients, or decorative color when neutral styling is sufficient.
