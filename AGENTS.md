# Nowind: agent guide

Nowind is a plain-CSS design system: theme tokens plus Prewind-style utility classes with Tailwind v4 names where they overlap. People link one file, `dist/nowind.min.css`. There is no build step for them; the scripts here are for maintaining Nowind.

Read `README.md` for what Nowind is and how people use it. This file says how to change it.

## Where things live

| Path | What it is | Edit by hand? |
|---|---|---|
| `AGENTS.md`, `CLAUDE.md` | Entry files: how to change Nowind (`CLAUDE.md` imports this file) | yes, in the same change as what they describe |
| `README.md` | How people use Nowind | yes, in the same change as what it describes |
| `CHANGELOG.md` | Releases; `## Unreleased` collects changes until a release dates it | yes, with every change people would notice |
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
| `index.html`, `site/index.html` | The root redirects to `site/`; `site/index.html` is the GitHub Pages landing page | yes, except between the `<!--nowind:top-->` and `<!--nowind:bottom-->` markers |
| `site/site.js` | The one script every page loads: ⌘K search over `site/search.json`, the display settings panel (theme light, dark or system; base size 12 to 18px on the root; tier product, content or brand on the main region and example frames, each region keeping its own until one is chosen; a fixed 14px `scope text-chrome` panel; all three saved in `localStorage` and applied before paint by a head script) and lens detection (`data-lens` on the root) | yes |
| `components.manifest.json` | Every component as data: page, group, summary, use, avoid, example ids and the classes its examples use | no, `python3 scripts/templates.py` |
| `site/search.json` | Search index: every page, block heading, component and class | no, `python3 scripts/templates.py` |
| `site/specimen.html` | Every token, the reset and every class, read live from the stylesheets | yes, except between the `<!--nowind:` markers, which `scripts/templates.py` stamps |
| `site/utilities.html` | Demo page built only from classes | yes, except between the `<!--nowind:` markers, which `scripts/templates.py` stamps |
| `site/docs/*.html` | Docs site, in the one page template every page shares (band, section row, label-column blocks; section map in `SECTIONS` in `scripts/templates.py`): home, guide, reference, regular and semantic class lists (`classes.html`, `semantic.html`, read from `classes.md` and sorted by `is_semantic` in `scripts/templates.py`), changelog and a `c-*.html` page per component | no, `python3 scripts/templates.py` |
| `scripts/component_docs.py` | Each component's snippet (rendered live and shown as code), summary, use and avoid | yes |
| `site/components.html` | Component showcase built only from classes: no `<style>`, no `style=` | yes, except between the `<!--nowind:` markers, which `scripts/templates.py` stamps |

Manifests: [`theme/theme.typography.manifest.json`](theme/theme.typography.manifest.json), [`theme/theme.space.manifest.json`](theme/theme.space.manifest.json), [`theme/theme.shadows.manifest.json`](theme/theme.shadows.manifest.json), [`nowind.manifest.json`](nowind.manifest.json) and [`components.manifest.json`](components.manifest.json) are written by their scripts; change the script, not the file. These are hand-written; update them in the same change as their CSS:

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
python3 scripts/templates.py # after a release (it reads CHANGELOG.md), a class change (it reads classes.md) or a change to the templates
node scripts/check.mjs       # before every commit
```

`scripts/check.mjs` enforces the rules below: no comments and no `color-mix()` in Nowind's CSS, every token a manifest names exists, every generated file (CSS, manifests, `classes.md`, the docs pages, `site/search.json`) matches what the scripts write, the site's controls follow the control recipe, the examples pass `python3 scripts/templates.py --lint`, and this file names every file in the repo. `node scripts/check.mjs --self-test` breaks a copy sixteen ways and confirms each is caught. `python3 scripts/templates.py --geometry-report` lists every example part whose height, padding, gap or corner breaks the geometry contract (`geometryContract` in the geometry manifest). `python3 scripts/templates.py --type-report` lists every example element whose text size breaks the size contract (`sizeContract` in the type-roles manifest), by kind. `?audit=geometry` does the same for the geometry contract's rules (nesting, insets, text edges, shared heights, squares and circles, clipping), into `window.nowindGeometryAudit`. Open any page with `?audit=type` on the dev server and `site/site.js` checks the rendered examples (the `data-example` frames, or the showcase's sections) against the contract's rules for rows, order and icons, logging the result and leaving it in `window.nowindTypeAudit`. `node scripts/serve.mjs` serves the site on port 8765.

## Keep the context current

Every change updates, in the same commit, what describes it:

- **Manifests.** A hand-written manifest changes with its CSS. A generated one (`nowind.manifest.json`, `components.manifest.json`, the typography, space, shadow, motion and materials manifests) changes through its script's text, never by hand.
- **Entry files.** `AGENTS.md` when a file, script, rule or naming pattern changes; `README.md` when how people use Nowind changes.
- **Docs.** The docs page that covers it (most read the manifests, so they follow by themselves) and `CHANGELOG.md` under `## Unreleased`.
- **Checks.** A new rule gets a check in `scripts/check.mjs` or the examples lint, and a self-test break that proves the check fires.

`node scripts/check.mjs` fails when this file stops naming a repo file, or names a path that doesn't exist.

Then check the result in `site/specimen.html` through the dev server (`node scripts/serve.mjs`, port 8765); browsers block reading stylesheets from `file://`, and the server turns caching off so an edited stylesheet and its imports reload fresh. The `specimen` entry in `.claude/launch.json` starts it.

## Rules

- **No comments in the CSS.** Notes, reasons and formulas go in the manifests. (checked)
- **Every theme value uses a token.** Utilities read tokens; tokens read other tokens or a palette.
- **Fonts load in `theme.css`.** Its first line imports Inter, Inter Tight and IBM Plex Mono from Google Fonts; `scripts/bundle.mjs` keeps that remote import and moves it to the top of the bundle. The stacks live in the `scripts/utopia.mjs` template.
- **Colours are `light-dark()`.** Never add a separate dark theme or a `dark:` variant.
- **No `color-mix()`.** Use the alpha steps (`--{palette}-a{1..12}`) for transparency. (checked)
- **Text on a solid uses `--on-solid-{palette}`.** The library's `solidLabel` is the starting point, but Nowind overrides it where the owner chose: the accents and every status (danger, warning, success, info) take light text in both modes; only neutral follows the library (light, then dark). Each palette's choice is in `palettes[].contrast` in the colors manifest.
- **Layers:** `reset, styles, nowind`. The reset wraps every selector in `:where()`. Its heading roles apply only to headings without a `text-{size}` class; a sized heading reads as text at that size.
- **Contrast is out of scope.** Don't add contrast checks.
- **Radii nest.** A container that holds items against its padding pairs by name: `rounded-md p-inset border` holds `rounded-sm`, `rounded-sm p-inset` holds `rounded-xs`, one step per margin after Affine. Any other padding uses `rounded-inner` on the item. The scale and the rule live in `theme/theme.geometry.css` and its manifest (`nesting`).
- **Logical sides.** Examples and the site say start and end, not left and right: `ps-`, `pe-`, `ms-`, `me-`, `start-`, `end-`, `text-start`, `text-end`, `border-s`, `border-e`, `rounded-s-*`, `rounded-e-*`. The physical classes exist for authors who need them; the examples lint rejects them. (checked)
- **Examples use regular classes only.** Component snippets and the showcase's blocks are written in primitives: palette steps (`bg-neutral-3`, `fg-accent-1-contrast`), the space scale, `p-inset`, the radius steps, the icon sizes (`icon`, `icon-sm`, `icon-lg`: every Phosphor icon sits in an `icon` box), and the control lengths (`h-control px-control`, `h-nested px-nested`, `size-control`, `size-nested`: Affine's control height, 4n − 26 at base size n, so every button, field, select and menu item is one height; `gap-gutter` and `gap-gutter-half` space a control's icon and label, one margin), type sizes and weights. Raw steps of neutral, accent-1 to accent-4 and danger take hover and state variants for this. Showcase blocks that demonstrate a semantic feature carry `data-semantic-demo`. (checked by `scripts/templates.py --lint`) An example's state indicators move with state (a caret takes `icon icon-sm transition group-open:rotate-180` inside a `group`), and any non-interactive element with a state or hover variant carries a `transition` class (interactive elements get one from the reset). `px-control` and `px-nested` drop to the icon padding at a leading or trailing icon by themselves; anything else padded `px-sm` with an icon at its edge pads that edge at its block padding (`ps-xs pe-sm`). The small size (`h-nested`, `size-nested`, `rounded-xs`) sits only inside an inset container (`p-inset rounded-sm`: a toolbar, field or segmented control), never beside full-size controls. No element carries two classes that set the same property (which wins would depend on stylesheet order; `icon` with its `icon-sm`/`icon-lg` modifier is the exception). A round marker holding text or initials is sized (`size-nested`, `size-control`, with `shrink-0`), never padded into an oval. Every part's height, padding, gap and corner follows the geometry contract (`geometryContract` in `theme/theme.geometry.manifest.json`): controls `h-control px-control gap-gutter rounded-sm`, small controls `h-nested px-nested gap-gutter-half rounded-inner`, badges `h-nested px-nested rounded-full`, cards `p-md rounded-md`, and so on. (checked; `?audit=geometry` measures the rendered rules) Every text size follows the size contract (`sizeContract` in `theme/theme.type-roles.manifest.json`): controls, cells and body `text-base`; labels, table headers, supporting lines and badges `text-sm`; titles `text-base font-semibold`, `text-lg` in a dialog; an icon takes the step of its text. (checked; `?audit=type` checks the rendered rules) Hover and press tints use `state`, not `hover:`/`active:` bg variants; those stay only on an element whose selected, pressed, current or open state changes its surface.
- **The site's own controls share one recipe.** In the band, bar and other chrome, every control sized `h-control` or `size-control` has `px-control` (unless `size-control` or `w-full`), a border width (`border`, plus `border-transparent` on a fill), a radius and a control type role. A field with slots is a box around a bare input; its slots run leading icon, prefix, input, suffix, trailing. (checked)

## Naming

- **Palettes:** `accent-1` (blue), `accent-2` (violet), `accent-3` (plum), `accent-4` (crimson), `neutral` (slate), `danger` (red), `warning` (amber), `success` (green), `info` (indigo). Steps: `--accent-1-9`, `--neutral-a4`.
- **Colour roles:** `--{group}[-{palette}][-weak|-strong]`, where the bare name is the middle of its group. Groups: `bg` (1–2), `component` (3–5), `border` (6–8), `solid` (9–10), `fg` (8, 11, 12 and a strong value). No palette name means neutral.
- **Type:** `--text-{xs…6xl}` and `--text-{size}--line-height` (Tailwind v4). Roles are `--{role}` with `--{role}--{property}` companions, outside `--text-*`, so they never clash with sizes.
- **Space:** `--space-{3xs…4xl}` (Prewind names), each `multiplier × var(--F)`, declared on `:root, .scope`. At the root that equals a Utopia space scale, because `--F` is the fluid `--text-base`.
- **Classes:** `property-value`; colour classes are the prefix plus the token name without `--`, dropping the role group when it matches the prefix (`fg-weak`, `bg-accent-1`, `border-weak`, `bg-solid-accent-1`); `--border` is `border-default`, since `border` is the width class. Tailwind v4 names where Tailwind has the same thing: `rounded-xs/sm`, `shadow-xs/sm`, `h-dvh`, `2xl:`.
- **Shadows:** `--shadow-{xs…xl}` and `--inset-shadow-{xs,sm}` (Tailwind v4 names) for Massimo's levels, each a stack of 4–6 generated layers in multiples of `--q`. Change the constants in `scripts/shadows.mjs`, never a layer by hand.
- **Levels and tiers:** `p-surface`, `p-dialog`, `p-region`, `p-page`, `gap-field`, `gap-row`, `gap-group`, `gap-section` after Affine's container levels; `tier-product`, `tier-content`, `tier-brand` are scopes, listed beside `.scope` in the selectors of `theme.geometry.css`, `scripts/utopia.mjs` and `scripts/shadows.mjs`. A new scope-like class goes in all three.
- **Materials:** `material-*` on a region, `relief-*` on a part. The paint lives in `scripts/materials.mjs`; how each material paints each relief lives in `scripts/utilities.mjs` as `@scope` blocks, so the nearest material wins.
- **Controls and icons:** utilities only (`h-control`, `px-control`, `gap-gutter`, `icon`, …), after Affine UI's button and icon geometry. The icon-edge padding is a `:has(> .icon:first-child)` rule in the generator, so labels must be wrapped in a `<span>`. Glyphs come from Phosphor's web font, linked by the page, not bundled.
- **Variants:** `hover:` (inside `@media (hover: hover)`) and the state variants `active:`, `focus-visible:`, `focus-within:`, `selected:`, `current:`, `pressed:`, `expanded:`, `open:`, `invalid:`, `has-invalid:`, `disabled:` change colors only (plus opacity and cursor for disabled, and `shadow-xs`, `shadow-sm`, `shadow-none` for `selected:`, `current:`, `pressed:`, `open:` and `has-checked:`, so a chosen segment can lift) for the neutral and accent roles and the raw steps of neutral, accent-1 to accent-4 and danger; `sm:` to `2xl:` (viewport) and `@sm:` to `@2xl:` (the nearest `@container`, widths from `--container-*`) for layout only. Group variants (`group-hover:`, `group-focus-within:`, `group-open:`) cover opacity, visibility, rotation and `fg-*` only. `state` is the alternative to colour variants: one class, a currentColor wash at the `--state-*` opacities (in `theme/theme.colors.css`). No `dark:`.

## Adding a palette

1. Copy a file in `theme/colors-semantic/`, rename the prefix and the family, and set `--{name}-contrast` from the family's `solidLabel`, recorded under `library.solidLabel.families` in [`theme/theme.colors.manifest.json`](theme/theme.colors.manifest.json): light in both modes → `var(--{name}-contrast-white)`, dark in both → `var(--{name}-contrast-black)`, light then dark → `light-dark(var(--{name}-contrast-white), var(--{name}-contrast-black))`.
2. Import it in `theme/theme.colors.css` and copy one palette's companion and role block with the new name.
3. Add it to `palettes` in `theme/theme.colors.manifest.json`.
4. Run `node scripts/utilities.mjs`, `node scripts/bundle.mjs` and `node scripts/check.mjs`. The specimen finds it by itself.

## Adding a component page

Add an entry to `COMPONENTS` in `scripts/component_docs.py`: a `slug`, `name`, Phosphor `icon`, `group`, `summary`, one `html` snippet using utility classes only, and `use` and `avoid` lists. Then run `python3 scripts/templates.py` and `node scripts/check.mjs`. The page, its sidebar entry, its index card and its class list are generated.

## Adding a type role

1. In `theme/theme.type-roles.css`, add `--{role}` pointing at a size (`var(--text-lg)`), and its companions: `--{role}--line-height`, `--{role}--font-weight`, `--{role}--font-family`, plus `--{role}--letter-spacing`, `--font-variant-numeric`, `--text-transform` or `--font-style` when the role needs them. Line height follows `calc(var(--{role}) * (1 + k/2) - 3k px)`; the manifest lists each k.
2. Add the role to `roles` in [`theme/theme.type-roles.manifest.json`](theme/theme.type-roles.manifest.json).
3. Run `node scripts/utilities.mjs`, `node scripts/bundle.mjs` and `node scripts/check.mjs`. The generator finds any `--{role}--font-family` and writes `text-{role}`.

## Changing faces, weights, tracking or leading

These live in the CSS template inside `scripts/utopia.mjs`, not in `theme/theme.typography.css`, which that script overwrites. Edit the template, then run all four scripts in order.

## Git

The repository is `github.com/kimgranlund/nowind`, branch `main`. Commit generated files (`nowind.css`, `classes.md`, `dist/`, the generated manifests) with the change that produced them, after `node scripts/check.mjs` passes.
