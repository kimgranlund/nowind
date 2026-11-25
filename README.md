# Nowind

Prewind-style utility classes over a themeable token system, in plain CSS. No build step for the people using it: every class already exists, so it works in any HTML, including CMS output.

- **Colors**: Radix 12-step scales regenerated in HCT, mapped to semantic roles for a neutral, four brand accents (accent-1 to accent-4) and four statuses (danger, warning, success, info), light and dark through `light-dark()`.
- **Type and space**: fluid Utopia scales with Tailwind/Prewind names (`text-lg`, `p-md`), plus semantic type roles after Massimo (`text-heading-md`, `text-body-md`) and a kicker.
- **Geometry**: control sizes, radii and container spacing built from one input, the scope's font size, after Affine UI.
- **Utilities**: about 800 classes, with hover and breakpoint variants, in `nowind.css`.

## Setup

Link one file:

```html
<link rel="stylesheet" href="dist/nowind.min.css">
```

`dist/nowind.min.css` is the whole system in one request: the theme with every import inlined, the reset and the utilities (184 KiB, 29 KiB gzipped). `dist/nowind.bundle.css` is the same, unminified.

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

Nowind sets no font files. `--font-body` asks for Inter and falls back to the system UI face; link a font yourself if you want it.

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

Classes follow `property-value`. Color classes take the token name without `--`.

| Group | Examples |
|---|---|
| Spacing | `p-md`, `px-lg`, `mt-xs`, `-mt-sm`, `mx-auto`, `gap-sm` (sizes `0`, `3xs` … `4xl`) |
| Type scale | `text-xs` … `text-6xl` (size and line height), `text-kicker-sm/md/lg` |
| Type roles | `text-display`, `text-heading-md`, `text-title`, `text-body-md`, `text-caption`, `text-label`, `text-kicker`, `text-figure`, `text-mono`, … |
| Text color | `text-fg`, `text-fg-weak`, `text-fg-subtle`, `text-fg-accent-1`, `text-on-solid` |
| Background | `bg-bg`, `bg-bg-strong`, `bg-component`, `bg-solid-accent-1`, `bg-accent-1-3`, `bg-neutral-a4` |
| Border | `border`, `border-2`, `border-t`, `border-border`, `border-border-accent-1-weak`, `rounded`, `rounded-lg`, `shadow` |
| Typography | `font-semibold`, `font-sans`, `font-heading`, `font-mono`, `leading-tight`, `tracking-wide`, `uppercase`, `tabular-nums`, `text-balance`, `truncate` |
| Layout | `container`, `flex`, `flex-col`, `items-center`, `justify-between`, `grid`, `hidden`, `relative`, `z-10` |
| Sizing | `w-full`, `w-fit`, `h-control`, `max-w-text` (or `max-w-prose`), `max-w-form`, `min-h-screen`, `min-h-dvh` |

### Variants

- **Hover**: only on devices that can hover, as Tailwind v4. Text and background colors of the role tokens (not raw palette steps), opacity and cursor only: `hover:bg-component`, `hover:text-fg`, `hover:opacity-100`.
- **Breakpoints**: `sm:` 640px, `md:` 768px, `lg:` 1024px, `xl:` 1280px, `2xl:` 1536px (the `--breakpoint-*` tokens), for layout only: display, flex direction and wrap, justify, align and text alignment.

```html
<div class="flex flex-col md:flex-row gap-sm">
  <div class="flex-1">…</div>
  <div class="flex-1 hidden lg:block">…</div>
</div>
```

There are no `focus:`, `active:`, `group-` or `dark:` variants. Write those states in `@layer styles`. Dark mode needs no variant: every color token switches by itself.

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
theme.css                      imports the theme groups below
nowind.css                     reset and utility classes (generated)
nowind.manifest.json           class counts, groups, variants, changes from Prewind
dist/
  nowind.bundle.css            theme + reset + utilities in one file (generated)
  nowind.min.css               the same, minified (generated)
theme/
  theme.colors.css             color roles, Radix companions, shadows
  theme.geometry.css           --F geometry: slot, margin, control height, radius, container
  theme.space.css              fluid --space-* (generated)
  theme.typography.css         fluid --text-*, kicker, faces, weights, leading, tracking (generated)
  theme.type-roles.css         semantic roles: --heading-md, --heading-md--line-height, …
  theme.*.manifest.json        what every token is and how it's derived
  colors-semantic/             accent-1 (indigo), accent-2 (violet), accent-3 (plum), accent-4 (crimson), neutral (slate),
                               danger (red), warning (amber), success (green), info (blue): one file each
  colors-raw/                  the radix-hct-colors library (31 families)
scripts/
  utopia.mjs                   generates the fluid type and space scales
  utilities.mjs                generates nowind.css from the theme tokens
  bundle.mjs                   inlines theme.css's imports and nowind.css into dist/
specimen.html                  every token, the reset and every class, live
utilities.html                 a demo built only from classes
```

## Changing the theme

**Colors.** Each palette is one file in `theme/colors-semantic/`. To switch an accent to another family, change its `@import` and every `--colors-<family>-*` reference in its file. Then set its `--accent-N-contrast` from the family's `solidLabel` in the radix-hct-colors `manifest.json`: indigo, violet, plum and crimson take light text on their solid in both modes; amber, yellow and lime take dark text in both; most others take light text in light mode and dark in dark mode. To add a palette (danger, success), copy a palette file, rename the prefix and import it in `theme/theme.colors.css`.

**Type and space.** Regenerate the fluid scales with your own viewport range, base sizes and ratios:

```bash
node scripts/utopia.mjs --min-vw 360 --max-vw 1240 --min-base 14 --max-base 18 --min-ratio 1.2 --max-ratio 1.25
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

`specimen.html` reads the tokens, reset rules and classes straight from the stylesheets, so it stays current. It needs a local server, because browsers block reading stylesheets from `file://`:

```bash
python3 -m http.server 8765
```

Then open http://localhost:8765/specimen.html.

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
