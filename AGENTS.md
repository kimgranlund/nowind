# Nowind: agent guide

Nowind is a plain-CSS design system: theme tokens plus Prewind-style utility classes with Tailwind v4 names where they overlap. People link one file, `dist/nowind.min.css`. There is no build step for them; the scripts here are for maintaining Nowind.

Read `README.md` for what Nowind is and how people use it. This file says how to change it.

## Where things live

| Path | What it is | Edit by hand? |
|---|---|---|
| `theme.css` | Entry: imports the four `theme/theme.*.css` groups | yes |
| `theme/theme.colors.css` | Colour usage roles for every palette, Radix companions, shadows | yes |
| `theme/colors-semantic/*.css` | One file per palette: steps, alpha steps, contrast | yes |
| `theme/colors-raw/` | The radix-hct-colors library | no, copied in |
| `theme/theme.geometry.css` | `--F` geometry, radius, container, breakpoints. At the root `--F` is `var(--text-base)`, so geometry is fluid; `.scope` sets `--F: 1em` | yes |
| `theme/theme.type-roles.css` | Semantic type roles (`--heading-md`, `--heading-md--line-height`, …) | yes |
| `theme/theme.shadows.css` | Compound shadows (casts and recesses) after Massimo | no, `scripts/shadows.mjs` |
| `theme/theme.motion.css` | Spring easings (CSS `linear()`) and durations after Massimo | no, `scripts/motion.mjs` |
| `theme/theme.materials.css` | Material paint roles and glass faces after Massimo | no, `scripts/materials.mjs` |
| `theme/theme.typography.css`, `theme/theme.space.css` | Fluid Utopia scales, faces, weights, leading, tracking | no, `scripts/utopia.mjs` |
| `nowind.css` | Reset and utility classes | no, `scripts/utilities.mjs` |
| `dist/` | One-file bundle and its minified copy | no, `scripts/bundle.mjs` |
| `theme/*.manifest.json`, `nowind.manifest.json` | What each token or class is, how it is derived, what to use it for | see below |
| `classes.md` | Every class and its declarations | no, `scripts/utilities.mjs` |
| `specimen.html` | Every token, the reset and every class, read live from the stylesheets | yes |
| `utilities.html` | Demo page built only from classes | yes |
| `components.html` | Component showcase built only from classes: no `<style>`, no `style=` | yes |

Manifests: [`theme/theme.typography.manifest.json`](theme/theme.typography.manifest.json), [`theme/theme.space.manifest.json`](theme/theme.space.manifest.json), [`theme/theme.shadows.manifest.json`](theme/theme.shadows.manifest.json) and [`nowind.manifest.json`](nowind.manifest.json) are written by their scripts; change the script, not the file. These are hand-written; update them in the same change as their CSS:

- [`theme/theme.colors.manifest.json`](theme/theme.colors.manifest.json): palettes, families, contrast, roles, and each library family's `solidLabel`.
- [`theme/theme.geometry.manifest.json`](theme/theme.geometry.manifest.json): `--F` inputs, derived lengths, radius, container, breakpoints.
- [`theme/theme.type-roles.manifest.json`](theme/theme.type-roles.manifest.json): every type role, its size, line-height factor and Massimo source.

## After a change

Run the scripts in this order, as far down as the change reaches:

```bash
node scripts/utopia.mjs      # only if the type or space scale changed
node scripts/shadows.mjs     # only if the shadow constants or levels changed
node scripts/motion.mjs      # only if the springs or curves changed
node scripts/materials.mjs   # only if the paint roles or glass faces changed
node scripts/utilities.mjs   # after any token change, so classes follow
node scripts/bundle.mjs      # always last
node scripts/check.mjs       # before every commit
```

`scripts/check.mjs` enforces the rules below: no comments and no `color-mix()` in Nowind's CSS, every token a manifest names exists, and every generated file matches what the scripts write. `node scripts/check.mjs --self-test` breaks a copy four ways and confirms each is caught.

Then check the result in `specimen.html` through the dev server (`node scripts/serve.mjs`, port 8765); browsers block reading stylesheets from `file://`, and the server turns caching off so an edited stylesheet and its imports reload fresh. The `specimen` entry in `.claude/launch.json` starts it.

## Rules

- **No comments in the CSS.** Notes, reasons and formulas go in the manifests. (checked)
- **Every theme value uses a token.** Utilities read tokens; tokens read other tokens or a palette.
- **Fonts load in `theme.css`.** Its first line imports Inter, Inter Tight and IBM Plex Mono from Google Fonts; `scripts/bundle.mjs` keeps that remote import and moves it to the top of the bundle. The stacks live in the `scripts/utopia.mjs` template.
- **Colours are `light-dark()`.** Never add a separate dark theme or a `dark:` variant.
- **No `color-mix()`.** Use the alpha steps (`--{palette}-a{1..12}`) for transparency. (checked)
- **Text on a solid uses `--on-solid-{palette}`.** The library's `solidLabel` is the starting point, but Nowind overrides it where the owner chose: the accents and every status (danger, warning, success, info) take light text in both modes; only neutral follows the library (light, then dark). Each palette's choice is in `palettes[].contrast` in the colors manifest.
- **Layers:** `reset, styles, nowind`. The reset wraps every selector in `:where()`.
- **Contrast is out of scope.** Don't add contrast checks.

## Naming

- **Palettes:** `accent-1` (blue), `accent-2` (violet), `accent-3` (plum), `accent-4` (crimson), `neutral` (slate), `danger` (red), `warning` (amber), `success` (green), `info` (indigo). Steps: `--accent-1-9`, `--neutral-a4`.
- **Colour roles:** `--{group}[-{palette}][-weak|-strong]`, where the bare name is the middle of its group. Groups: `bg` (1–2), `component` (3–5), `border` (6–8), `solid` (9–10), `fg` (8, 11, 12 and a strong value). No palette name means neutral.
- **Type:** `--text-{xs…6xl}` and `--text-{size}--line-height` (Tailwind v4). Roles are `--{role}` with `--{role}--{property}` companions, outside `--text-*`, so they never clash with sizes.
- **Space:** `--space-{3xs…4xl}` (Prewind names), each `multiplier × var(--F)`, declared on `:root, .scope`. At the root that equals a Utopia space scale, because `--F` is the fluid `--text-base`.
- **Classes:** `property-value`; colour classes take the token name without `--` (`bg-solid-accent-1`, `text-fg-weak`). Tailwind v4 names where Tailwind has the same thing: `rounded-xs/sm`, `shadow-xs/sm`, `h-dvh`, `2xl:`.
- **Shadows:** `--shadow-{xs…xl}` and `--inset-shadow-{xs,sm}` (Tailwind v4 names) for Massimo's levels, each a stack of 4–6 generated layers in multiples of `--q`. Change the constants in `scripts/shadows.mjs`, never a layer by hand.
- **Levels and tiers:** `p-surface`, `p-dialog`, `p-region`, `p-page`, `gap-field`, `gap-row`, `gap-group`, `gap-section` after Affine's container levels; `tier-product`, `tier-content`, `tier-brand` are scopes, listed beside `.scope` in the selectors of `theme.geometry.css`, `scripts/utopia.mjs` and `scripts/shadows.mjs`. A new scope-like class goes in all three.
- **Materials:** `material-*` on a region, `relief-*` on a part. The paint lives in `scripts/materials.mjs`; how each material paints each relief lives in `scripts/utilities.mjs` as `@scope` blocks, so the nearest material wins.
- **Controls and icons:** utilities only (`h-control`, `px-control`, `gap-gutter`, `icon`, …), after Affine UI's button and icon geometry. The icon-edge padding is a `:has(> .icon:first-child)` rule in the generator, so labels must be wrapped in a `<span>`. Glyphs come from Phosphor's web font, linked by the page, not bundled.
- **Variants:** `hover:` for role-token text, background and border colours, opacity and cursor, inside `@media (hover: hover)`; `sm:` to `2xl:` for layout only (display, grid, flex, basis, alignment, widths, gaps). No other variants.

## Adding a palette

1. Copy a file in `theme/colors-semantic/`, rename the prefix and the family, and set `--{name}-contrast` from the family's `solidLabel`, recorded under `library.solidLabel.families` in [`theme/theme.colors.manifest.json`](theme/theme.colors.manifest.json): light in both modes → `var(--{name}-contrast-white)`, dark in both → `var(--{name}-contrast-black)`, light then dark → `light-dark(var(--{name}-contrast-white), var(--{name}-contrast-black))`.
2. Import it in `theme/theme.colors.css` and copy one palette's companion and role block with the new name.
3. Add it to `palettes` in `theme/theme.colors.manifest.json`.
4. Run `node scripts/utilities.mjs`, `node scripts/bundle.mjs` and `node scripts/check.mjs`. The specimen finds it by itself.

## Adding a type role

1. In `theme/theme.type-roles.css`, add `--{role}` pointing at a size (`var(--text-lg)`), and its companions: `--{role}--line-height`, `--{role}--font-weight`, `--{role}--font-family`, plus `--{role}--letter-spacing`, `--font-variant-numeric`, `--text-transform` or `--font-style` when the role needs them. Line height follows `calc(var(--{role}) * (1 + k/2) - 3k px)`; the manifest lists each k.
2. Add the role to `roles` in [`theme/theme.type-roles.manifest.json`](theme/theme.type-roles.manifest.json).
3. Run `node scripts/utilities.mjs`, `node scripts/bundle.mjs` and `node scripts/check.mjs`. The generator finds any `--{role}--font-family` and writes `text-{role}`.

## Changing faces, weights, tracking or leading

These live in the CSS template inside `scripts/utopia.mjs`, not in `theme/theme.typography.css`, which that script overwrites. Edit the template, then run all four scripts in order.

## Git

The repository is `github.com/kimgranlund/nowind`, branch `main`. Commit generated files (`nowind.css`, `classes.md`, `dist/`, the generated manifests) with the change that produced them, after `node scripts/check.mjs` passes.
