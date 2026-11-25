# Changelog

## Unreleased

- **Inverse colors:** `--bg-inverse`, `--fg-inverse`, `--fg-inverse-weak` and their classes, for toasts and tooltips.
- **Hover borders:** `hover:border-*` for the border roles (`hover:border-border-strong`).
- **Grid:** `grid-cols-1` … `grid-cols-12`, `grid-cols-none`, `col-span-1` … `col-span-12`, `col-span-full`.
- **Fractions:** `w-1/2`, `w-1/3`, `w-2/3`, `w-1/4`, `w-3/4`, fifths, and matching `basis-*`.
- **Breakpoints** now also cover grid columns and spans, basis, widths and gaps.

## 0.1.0 (2026-11-25)

First release.

### Theme

- **Colors:** nine palettes on the radix-hct-colors scales: `accent-1` (blue), `accent-2` (violet), `accent-3` (plum), `accent-4` (crimson), `neutral` (slate), `danger` (red), `warning` (amber), `success` (green), `info` (indigo). Each has steps 1–12, alpha steps a1–a12 and a contrast color, all in `light-dark()`.
- **Color roles:** `bg`, `component`, `border`, `solid`, `on-solid` and `fg` for every palette, with `-weak` and `-strong` steps; Radix companions `surface`, `indicator`, `track`; `--scrim` for backdrops.
- **Type:** a fluid Utopia scale `--text-xs` … `--text-6xl` with Tailwind v4 line-height companions; 29 semantic roles after Massimo (`--heading-md`, `--body-md`, `--figure`, …); a kicker at three sizes.
- **Geometry:** every length from one base size `--F`, after Affine UI: slot, margin, inset, control height, radii, icon sizes, container levels and tiers. At the root `--F` follows the fluid body size; a `.scope` or tier sets its own.
- **Space:** `--space-3xs` … `--space-4xl` as multiples of `--F`.
- **Shadows:** compound casts and recesses after Massimo, `--shadow-xs` … `--shadow-xl` and `--inset-shadow-xs`, `--inset-shadow-sm`.

### Utilities

- About 1,200 Prewind-style classes with Tailwind v4 names where they overlap; `hover:` for role colors, opacity and cursor; `sm:` … `2xl:` for layout.
- Affine container levels (`p-surface`, `p-dialog`, `gap-field`, `gap-group`, …), tiers (`tier-content`, `tier-brand`), control and icon utilities for Phosphor icons.
- A 2026 reset in `@layer reset`, every selector in `:where()`.

### Tooling

- `dist/nowind.min.css`: the whole system in one file.
- Generators for the type and space scales, shadows, utilities and bundle; `scripts/check.mjs` with a self-test.
- `specimen.html`, `components.html`, `utilities.html` and `classes.md`.
