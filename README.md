# Nowind

Prewind-style utility classes over a themeable token system, in plain CSS. No build step for the people using it: every class already exists, so it works in any HTML, including CMS output.

- **Colors**: Radix 12-step scales regenerated in HCT, mapped to semantic roles for a neutral, four brand accents (accent-1 to accent-4) and four statuses (danger, warning, success, info), light and dark through `light-dark()`.
- **Type and space**: fluid Utopia scales with Tailwind/Prewind names; space is a multiple of `--F`, so it also follows a `.scope`'s font size (`text-lg`, `p-md`), plus semantic type roles after Massimo (`text-heading-md`, `text-body-md`) and a kicker.
- **Geometry**: control sizes, radii, icons, shadows and container spacing built from one input, `--F`, after Affine UI. At the root `--F` is the fluid body size, so a button is 30px tall on a phone and 46px on a wide screen; an element with the `scope` class pins its own size from its `font-size`.
- **Utilities**: Prewind-style classes with Tailwind v4 names where they overlap, plus hover and breakpoint variants, in `nowind.css`. Every class is listed in [classes.md](classes.md); the counts are in [nowind.manifest.json](nowind.manifest.json).

## Setup

Link one file from the CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kimgranlund/nowind@v0.6.0/dist/nowind.min.css">
```

The link pins release `v0.6.0`, so your site won't change until you change the version. `@main` follows the latest commit, but jsDelivr caches it for up to 12 hours. Or copy `dist/nowind.min.css` into your project and link it locally. Releases are listed in [CHANGELOG.md](CHANGELOG.md).

Browse it first: [component docs](https://kimgranlund.github.io/nowind/templates/components-index.html), the [showcase](https://kimgranlund.github.io/nowind/components.html), [specimen](https://kimgranlund.github.io/nowind/specimen.html) and the [class list](https://kimgranlund.github.io/nowind/classes.html) are on GitHub Pages.

`nowind.min.css` is the whole system in one request: the theme with every import inlined, the reset and the utilities. `dist/nowind.bundle.css` is the same, unminified.

While working on Nowind itself, link the source files instead, so edits show without rebuilding:

```html
<link rel="stylesheet" href="theme.css">
<link rel="stylesheet" href="nowind.css">
```

`theme.css` loads its groups and palettes through `@import`, about 25 requests, so use the bundle in production.

`nowind.css` declares the cascade layers `reset, styles, nowind`. Put your own CSS in `@layer styles`, so a utility class always wins over it:

```css
@layer styles {
  .site-nav { display: flex; gap: var(--space-md); }
  .site-nav a { color: var(--fg-weak); }
}
```

CSS outside any layer beats every utility, so keep your rules inside `@layer styles`.

Or import the source files from one stylesheet of your own:

```css
@import "theme.css";
@import "nowind.css";

@layer styles {
  /* your global rules */
}
```

Fonts load with the theme: `theme.css` (and the bundle) imports Inter, Inter Tight and IBM Plex Mono from Google Fonts. `--font-body` is Inter, `--font-heading` is Inter Tight and `--font-mono` is IBM Plex Mono, each with a system fallback while they load. To use other faces, override those three tokens in `@layer styles`; the Google request still happens unless you remove the import from `theme.css` and rebuild.

## Using it

Work global first, as in Prewind:

1. **Global CSS** in `@layer styles` for shared looks: navigation, headings, forms.
2. **Utility classes** for one-off changes on a single element.
3. **Inline styles** for any value the scale doesn't have (there is no bracket syntax).

```html
<article class="max-w-form p-lg rounded-lg bg-bg border border-border-weak shadow-lg">
  <span class="text-kicker text-fg-accent-1-weak">Release</span>
  <h3 class="text-title mt-3xs mb-2xs">Nowind 0.1</h3>
  <p class="text-body-md text-fg-weak">Fluid type, semantic roles and a light/dark palette.</p>
  <button class="h-control px-md rounded border-0 bg-solid-accent-1 hover:bg-solid-accent-1-strong text-on-solid-accent-1">
    Read more
  </button>
</article>
```

### Class names

Classes follow `property-value`. Color classes take the token name without `--`, and each property takes only its own roles: `text-` the `fg-*` and `on-solid-*` tokens, `bg-` the `bg-*`, `component-*` and `solid-*` tokens, `border-` the `border-*` tokens. Raw palette steps (`bg-accent-1-3`) and alpha steps (`bg-neutral-a4`) are background-only; text and borders always use a role. `border-border-page` draws a border in the page color, for overlapping avatars. The table shows examples; [classes.md](classes.md) lists every class with its declarations.

| Group | Examples |
|---|---|
| Spacing | `p-md`, `px-lg`, `mt-xs`, `-mt-sm`, `mx-auto`, `gap-sm` (sizes `0`, `3xs` … `4xl`) |
| Type scale | `text-xs` … `text-6xl` (size and line height), `text-kicker-sm/md/lg` |
| Type roles | `text-display`, `text-heading-md`, `text-title`, `text-body-md`, `text-caption`, `text-label`, `text-kicker`, `text-figure`, `text-mono`, … |
| Text color | `text-fg`, `text-fg-weak`, `text-fg-subtle`, `text-fg-accent-1`, `text-on-solid`, `text-fg-inverse` |
| Background | `bg-bg`, `bg-bg-strong`, `bg-component`, `bg-solid-accent-1`, `bg-accent-1-3`, `bg-neutral-a4`, `bg-bg-inverse` (toasts, tooltips), `bg-scrim` |
| Border | `border`, `border-2`, `border-t`, `border-border`, `border-border-accent-1-weak`, `rounded`, `rounded-lg` |
| Shadow | `shadow-xs` … `shadow-xl`, `inset-shadow-xs`, `inset-shadow-sm`, `shadow-none` (a cast and a recess on one element combine) |
| Typography | `font-semibold`, `font-sans`, `font-heading`, `font-mono`, `leading-tight`, `tracking-wide`, `uppercase`, `tabular-nums`, `text-balance`, `truncate` |
| Layout | `container`, `flex`, `flex-col`, `items-center`, `justify-between`, `grid`, `grid-cols-1` … `grid-cols-12`, `col-span-2`, `col-span-full`, `basis-1/2`, `hidden`, `relative`, `z-10` |
| Sizing | `w-full`, `w-fit`, `w-1/2`, `w-1/3`, `w-2/3`, `w-1/4`, `w-3/4`, fifths, `h-control`, `max-w-text` (or `max-w-prose`), `max-w-form`, `min-h-screen`, `min-h-dvh` |

### Container levels and tiers

Affine pads by what a box is, not by a size. These classes read the geometry tokens, so they grow with the type and follow a `.scope`:

| Class | Use | At 16px |
|---|---|---|
| `p-surface` | Card or panel (slot − border) | 23px |
| `p-dialog` | Dialog (control height − border) | 37px |
| `p-region` | Sidebar | 24px |
| `p-page` | Page content area (tier × control height) | 38px |
| `gap-field` | Label to control, control to help | 7px |
| `gap-row` | Controls side by side | 14px |
| `gap-group` | Field to field | 19px |
| `gap-section`, `mt-section`, `mb-section` | Before a new section (tier × slot) | 24px |

Each padding class also has `px-` and `py-` versions.

Tiers change the rhythm of a whole region. `tier-content` raises the font size by 2px and multiplies page and section spacing by 1.5; `tier-brand` adds 4px and 2×. `tier-product` is the default. Every size inside a tier recomputes, as inside a `.scope`, and the whole type scale grows with it: body text is 18px at the root, 20px in `tier-content` and 22px in `tier-brand` on a wide screen, with larger steps growing in proportion.

```html
<article class="tier-content">…</article>
```

### Buttons and icons

Nowind has no button component; a button is a stack of utilities. The geometry follows Affine UI: one control height tall, text padded by the text edge, and a side that holds an icon padded one margin less, so the icon's box sits one margin from the edge. An icon alone makes a square.

Icons use [Phosphor](https://phosphoricons.com)'s web font. Link the weights you use:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/regular/style.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/bold/style.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/light/style.css">
```

```html
<button class="inline-flex items-center justify-center h-control px-control gap-gutter rounded-sm
               border border-border bg-component-weak hover:bg-component text-title-sm">
  <i class="icon ph ph-floppy-disk"></i><span>Save</span>
</button>

<button class="inline-flex items-center justify-center h-control px-control rounded-sm border border-border" aria-label="Add">
  <i class="icon ph ph-plus"></i>
</button>

<button class="inline-flex items-center justify-center h-nested px-nested gap-gutter-half rounded-xs border border-border text-label">
  <i class="icon icon-sm ph-bold ph-funnel"></i><span>Filter</span>
</button>
```

- **Wrap the label in a `<span>`.** `px-control` and `px-nested` find an icon edge with `:has(> .icon:first-child)` and `:last-child`, and CSS cannot see bare text.
- **Icon sizes** follow Affine's weights: `icon icon-sm` with `ph-bold`, `icon` with `ph` (regular), `icon icon-lg` with `ph-light`. The box is always one slot square.
- An inline `<svg>` inside `.icon` also works; it takes the glyph size and `currentColor`.
- Classes: `h-control`, `h-nested`, `size-control`, `size-nested`, `min-w-control`, `px-control`, `px-nested`, `gap-gutter`, `gap-gutter-half`, `icon`, `icon-sm`, `icon-md`, `icon-lg`.

### Materials

After Massimo, a region picks a material and each part says what it is. The material decides how parts are lit, lined or made of glass; it never changes a size or a fill color.

| Class | Effect |
|---|---|
| `material-flat` | No paint (the default) |
| `material-physical` | Lit faces, a bevel, a cast shadow; pressed buttons sink |
| `material-frosted` | Cards, buttons and overlays become frosted glass: blurred backdrop, sheen, lit rim |
| `material-glass` | The same as clear glass: a thinner face and a sharper sheen |
| `material-outline` | No fills: every part draws one line |

Parts: `relief-raised` (buttons), `relief-raised-solid` (primary buttons), `relief-field` (inputs), `relief-recessed` (tracks, wells), `relief-etched`, `relief-ground` (cards), `relief-overlay` (popovers, dialogs). The nearest material wins, so regions nest.

```html
<div class="material-frosted relief-ground p-surface rounded-lg bg-bg">
  <input class="relief-field …">
  <button class="relief-raised-solid …">Invite</button>
</div>
```

### Form marks

The reset draws checkboxes, radios, switches and sliders with the theme, at Affine's mark size (between the body size and a slot), filled with `accent-1` when on. A switch is a checkbox with `role="switch"`; its thumb moves on the snappy spring. `mark-sm` and `mark-lg` pick another size.

```html
<label><input type="checkbox" role="switch" checked> Email me about mentions</label>
<input type="checkbox" class="mark-lg" checked>
<input type="range" value="60">
```

### Page grid and app shell

After Affine: `gap-grid` is the column gutter (2M), `p-grid-inset` pads a placed element by half a gutter, and `px-grid` / `px-grid-compact` are the page's edge padding. For an app frame, `w-sidebar` (16F + 16), `w-rail` (collapsed), `h-header` and `max-w-measure` (a 44-character reading column) all grow with the type. `top-header` and `max-h-below-header` make a sidebar stick just under a sticky header: `lg:sticky top-header max-h-below-header lg:overflow-y-auto`.

### Motion

Hover states animate when an element has a transition class. `transition-colors` (and `transition`, `transition-opacity`, `transition-shadow`, `transition-transform`) use Affine's single state change: 160ms on Apple's standard ease. Swap in one of Massimo's springs for movement: `duration-snappy ease-snappy` for a toggle, `duration-smooth ease-smooth` for a sliding sheet, `ease-bouncy` for playful moments. The springs are real spring curves sampled into CSS `linear()`. The reset turns all motion off for people who ask for reduced motion.

### Popovers, select and animation

- `anchor-bottom`, `anchor-top`, `anchor-start`, `anchor-end` and `anchor-center` place a popover against the button that opens it (`popovertarget`), with CSS anchor positioning that flips at the screen edge. No script.
- `select-base` turns a `<select>` into the customizable select: its picker and options take the theme.
- `animate-spin` and `animate-pulse` for spinners and skeletons; the reset stops them for people who ask for reduced motion.

```html
<button popovertarget="menu">Sort</button>
<div id="menu" popover class="anchor-bottom p-3xs rounded-lg bg-bg border border-border-weak shadow-lg">…</div>
```

### Variants

- **Hover**: only on devices that can hover, as Tailwind v4. Text, background and border colors of the role tokens (not raw palette steps), opacity and cursor: `hover:bg-component`, `hover:text-fg`, `hover:border-border-strong`, `hover:opacity-100`.
- **Breakpoints**: `sm:` 640px, `md:` 768px, `lg:` 1024px, `xl:` 1280px, `2xl:` 1536px (the `--breakpoint-*` tokens), for layout: display, grid columns and spans, flex direction, wrap and basis, alignment, text alignment, widths (`md:w-1/3`) and gaps (`md:gap-lg`). Margins, color and type have no breakpoint variants; padding, position, `top-*`, overflow and heights do.

```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-sm md:gap-lg">
  <div class="md:col-span-2">…</div>
  <div class="hidden lg:block">…</div>
</div>
```

- **States** (Tailwind v4 names), colors only: `active:`, `focus-visible:` (borders), `aria-selected:`, `aria-current:`, `aria-pressed:`, `aria-expanded:`, `open:` (details and popovers), `aria-invalid:` (also `:user-invalid`) and `disabled:` (also `aria-disabled`, with opacity and cursor). They cover the neutral and accent roles; `aria-invalid:` covers neutral and danger. Markup drives the look:

```html
<button role="tab" aria-selected="true"
        class="border-b-2 border-transparent aria-selected:border-border-accent-1-strong text-fg-weak aria-selected:text-fg">Profile</button>
```

There are no `group-` or `dark:` variants. Dark mode needs no variant: every color token switches by itself.

### Light and dark

The page follows the OS setting. Force a mode on any element and everything inside it follows:

```html
<html data-color-mode="dark">
<section class="light">…</section>
```

### Tokens in your own CSS

Every class reads a token, and your CSS can read the same ones:

```css
@layer styles {
  .callout {
    padding: var(--space-md);
    background: var(--component-accent-1-weak);
    border: var(--border-width) solid var(--border-accent-1-weak);
    border-radius: var(--radius-surface);
    color: var(--fg-accent-1);
    font-size: var(--body-md);
    line-height: var(--body-md--line-height);
  }
}
```

The color roles, named by contrast against the page in both modes:

| Group | Tokens (neutral; add `-accent-1` … `-accent-4`, `-danger`, `-warning`, `-success` or `-info` after the group for that palette) |
|---|---|
| Background | `--bg`, `--bg-strong` |
| Component fill | `--component-weak` (rest), `--component` (hover), `--component-strong` (pressed) |
| Border | `--border-weak` (dividers), `--border` (controls), `--border-strong` (hover) |
| Solid | `--solid`, `--solid-strong` (hover), `--on-solid` (text on it) |
| Text | `--fg-subtle`, `--fg-weak`, `--fg`, `--fg-strong` |

So a field in error is `border-border-danger`, its message `text-fg-danger-weak`, and a destructive button `bg-solid-danger hover:bg-solid-danger-strong text-on-solid-danger`.

The full list, with what each token is for, is in the manifests in `theme/`.

## Files

```
CHANGELOG.md                   releases
index.html                     GitHub Pages landing page
AGENTS.md                      how to change Nowind: generated files, script order, rules, naming
theme.css                      imports the theme groups below
nowind.css                     reset and utility classes (generated)
nowind.manifest.json           class counts, groups, variants, changes from Prewind
classes.md                     every class and its declarations (generated)
dist/
  nowind.bundle.css            theme + reset + utilities in one file (generated)
  nowind.min.css               the same, minified (generated)
theme/
  theme.colors.css             color roles, Radix companions, shadows
  theme.geometry.css           --F geometry: slot, margin, control height, radius, container
  theme.shadows.css            compound shadows after Massimo (generated)
  theme.motion.css             spring easings and durations after Massimo (generated)
  theme.materials.css          material paint and glass faces after Massimo (generated)
  theme.space.css              fluid --space-* (generated)
  theme.typography.css         fluid --text-*, kicker, faces, weights, leading, tracking (generated)
  theme.type-roles.css         semantic roles: --heading-md, --heading-md--line-height, …
  theme.*.manifest.json        what every token is and how it's derived
  colors-semantic/             accent-1 (blue), accent-2 (violet), accent-3 (plum), accent-4 (crimson), neutral (slate),
                               danger (red), warning (amber), success (green), info (indigo): one file each
  colors-raw/                  the radix-hct-colors library (31 families)
scripts/
  utopia.mjs                   generates the fluid type and space scales
  shadows.mjs                  generates the compound shadows
  motion.mjs                   generates the spring easings and durations
  materials.mjs                generates the material paint tokens
  utilities.mjs                generates nowind.css from the theme tokens
  bundle.mjs                   inlines theme.css's imports and nowind.css into dist/
  check.mjs                    checks the rules in AGENTS.md; --self-test proves it catches breaks
  serve.mjs                    dev server on port 8765 with caching off
  templates.py                 generates the docs-site templates and component pages
  component_docs.py            the component pages' content: snippet, summary, use and avoid
specimen.html                  every token, the reset and every class, live
utilities.html                 a demo built only from classes
templates/                     docs site: home, guide, reference, changelog and a page per component (generated by scripts/templates.py)
components.html                buttons, badges, alerts, forms, cards, tables, navigation and a dialog, built only from classes
```

## Changing the theme

**Colors.** Each palette is one file in `theme/colors-semantic/`. To switch an accent to another family, change its `@import` and every `--colors-<family>-*` reference in its file. Then set its `--accent-N-contrast` from the family's `solidLabel` in the radix-hct-colors `manifest.json`: indigo, violet, plum and crimson take light text on their solid in both modes; amber, yellow and lime take dark text in both; most others take light text in light mode and dark in dark mode. To add a palette (danger, success), copy a palette file, rename the prefix and import it in `theme/theme.colors.css`.

**Type and space.** Regenerate the fluid scales with your own viewport range, base sizes and ratios:

```bash
node scripts/utopia.mjs --min-vw 360 --max-vw 1240 --min-base 14 --max-base 18 --min-ratio 1.2 --max-ratio 1.25
```

**Shadows.** Every shadow is a stack of 4–6 layers generated from a few constants after Massimo: a tight contact layer where the element meets its ground, then key layers that double in offset and blur while their opacity falls to a fixed total. Lengths are multiples of `--q`, so a `.scope` with a smaller font size casts smaller shadows. Change the constants or levels in `scripts/shadows.mjs`, then:

```bash
node scripts/shadows.mjs
```

**Utilities.** After changing or adding tokens, regenerate `nowind.css` so the classes follow:

```bash
node scripts/utilities.mjs
```

**Bundle.** Rebuild `dist/` last, after any change to the theme or the utilities:

```bash
node scripts/bundle.mjs
```

The scripts need Node 18 or later and have no dependencies. People who use Nowind never run them.

## Specimen

`specimen.html` reads the tokens, reset rules and classes straight from the stylesheets, so it stays current. It needs a local server, because browsers block reading stylesheets from `file://`. The dev server turns caching off, so an edited stylesheet and everything it imports reload fresh:

```bash
node scripts/serve.mjs
```

Then open http://localhost:8765/specimen.html, or http://localhost:8765/components.html for common interface parts built only from utility classes.

## Differences from Prewind

- `container` is `min(100%, max)`, so it never overflows a narrow screen.
- No `bg-opacity-*`. Use the alpha steps instead: `bg-accent-1-a3`, `bg-neutral-a5`.
- No `m-full` or `p-full`.
- `text-{size}` also sets the line height, as Tailwind v4 does.
- The reset keeps link underlines and adds a focus ring, `:where()` selectors, headings sized from the type roles and reduced-motion handling.
- Dark mode is built in through `light-dark()`.
- Tailwind v4 names where v4 renamed v3 ones: `rounded-xs`/`rounded-sm`, `shadow-xs`/`shadow-sm`, `backdrop-blur-xs`/`-sm`. `h-screen` is `100vh`, with `h-dvh`, `h-svh` and `h-lvh` separate. Aliases `max-w-prose` and `font-sans`.
- Added: semantic type roles, kicker classes, grid display, `tabular-nums`, `text-balance`, `text-pretty`, `w-fit`, `h-control`.

## Browser support

Nowind uses `light-dark()`, `@layer`, `@property`, `clamp()` and `:where()`, which every current browser supports. A few reset properties (`interpolate-size`, `field-sizing`, `text-wrap: pretty`) are progressive: browsers without them ignore them.

## Credits

Built on ideas and values from Prewind, [Tailwind CSS](https://tailwindcss.com), [Utopia](https://utopia.fyi) and [Radix Colors](https://www.radix-ui.com/colors), plus the Affine UI and Massimo kits.
