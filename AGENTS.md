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
| `theme/theme.geometry.css` | `--F` geometry, radius, container, breakpoints | yes |
| `theme/theme.type-roles.css` | Semantic type roles (`--heading-md`, `--heading-md--line-height`, …) | yes |
| `theme/theme.typography.css`, `theme/theme.space.css` | Fluid Utopia scales, faces, weights, leading, tracking | no, `scripts/utopia.mjs` |
| `nowind.css` | Reset and utility classes | no, `scripts/utilities.mjs` |
| `dist/` | One-file bundle and its minified copy | no, `scripts/bundle.mjs` |
| `theme/*.manifest.json`, `nowind.manifest.json` | What each token or class is, how it is derived, what to use it for | see below |
| `specimen.html` | Every token, the reset and every class, read live from the stylesheets | yes |
| `utilities.html` | Demo page built only from classes | yes |

Manifests: `theme.typography.manifest.json`, `theme.space.manifest.json` and `nowind.manifest.json` are written by their scripts; change the script, not the file. The colour, geometry and type-roles manifests are hand-written; update them in the same change as their CSS.

## After a change

Run the scripts in this order, as far down as the change reaches:

```bash
node scripts/utopia.mjs      # only if the type or space scale changed
node scripts/utilities.mjs   # after any token change, so classes follow
node scripts/bundle.mjs      # always last
```

Then check the result in `specimen.html` through a local server (`python3 -m http.server 8765`); browsers block reading stylesheets from `file://`. The `specimen` entry in `.claude/launch.json` starts it.

## Rules

- **No comments in the CSS.** Notes, reasons and formulas go in the manifests.
- **Every theme value uses a token.** Utilities read tokens; tokens read other tokens or a palette.
- **Colours are `light-dark()`.** Never add a separate dark theme or a `dark:` variant.
- **No `color-mix()`.** Use the alpha steps (`--{palette}-a{1..12}`) for transparency.
- **Text on a solid uses `--on-solid-{palette}`**, set per palette from the library's `solidLabel`; amber takes dark text in both modes, the accents take light text in both.
- **Layers:** `reset, styles, nowind`. The reset wraps every selector in `:where()`.
- **Contrast is out of scope.** Don't add contrast checks.

## Naming

- **Palettes:** `accent-1` (indigo), `accent-2` (violet), `accent-3` (plum), `accent-4` (crimson), `neutral` (slate), `danger` (red), `warning` (amber), `success` (green), `info` (blue). Steps: `--accent-1-9`, `--neutral-a4`.
- **Colour roles:** `--{group}[-{palette}][-weak|-strong]`, where the bare name is the middle of its group. Groups: `bg` (1–2), `component` (3–5), `border` (6–8), `solid` (9–10), `fg` (8, 11, 12 and a strong value). No palette name means neutral.
- **Type:** `--text-{xs…6xl}` and `--text-{size}--line-height` (Tailwind v4). Roles are `--{role}` with `--{role}--{property}` companions, outside `--text-*`, so they never clash with sizes.
- **Space:** `--space-{3xs…4xl}` (Prewind).
- **Classes:** `property-value`; colour classes take the token name without `--` (`bg-solid-accent-1`, `text-fg-weak`). Tailwind v4 names where Tailwind has the same thing: `rounded-xs/sm`, `shadow-xs/sm`, `h-dvh`, `2xl:`.
- **Variants:** `hover:` for role-token colours, opacity and cursor, inside `@media (hover: hover)`; `sm:` to `2xl:` for layout only. No other variants.

## Adding a palette

1. Copy a file in `theme/colors-semantic/`, rename the prefix and the family, and set `--{name}-contrast` from the family's `solidLabel` in the radix-hct-colors `manifest.json`.
2. Import it in `theme/theme.colors.css` and copy one palette's companion and role block with the new name.
3. Add it to `palettes` in `theme/theme.colors.manifest.json`.
4. Run `node scripts/utilities.mjs` and `node scripts/bundle.mjs`. The specimen finds it by itself.

## Git

The repository is `github.com/kimgranlund/nowind`, branch `main`. Commit generated files (`nowind.css`, `dist/`, the generated manifests) with the change that produced them.
