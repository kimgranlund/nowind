# Nowind

A runtime CSS foundation with no build step and no dependencies. Link one file and every class already exists: no purging, no compiler, no config. Nowind gives HTML a small, closed set of style tags over a token layer you can retune, so whoever writes the markup, a person, a CMS or an agent, never has to author a stylesheet or reach for inline styles.

If you know Tailwind, you already know Nowind. The classes you type every day, `flex`, `p-md`, `gap-sm`, `rounded-md`, `shadow-sm`, `hover:`, `md:`, have the same names. The differences: sizes are t-shirt steps (`p-md`, `text-lg`) that scale fluidly, colors are Radix-style 12-step palettes, and lengths come from one geometric system instead of arbitrary numbers.

Nowind is directly derived from four systems, and brings its own math to tie them together:

- **[Prewind](https://github.com/codepilotsf/prewind)**: the no-build utility library Nowind grew from. Its shape (one CSS file, `@layer reset, styles, prewind`, t-shirt sizes, a theme file of CSS variables, global first) is Nowind's shape.
- **[Tailwind CSS](https://tailwindcss.com)**: the class vocabulary and the runtime tag system: `property-value` names, v4 names where they differ (`rounded-xs`, `shadow-xs`, `h-dvh`), `hover:`, state and breakpoint variants, `group-*`, `@container` queries.
- **[Radix Colors](https://www.radix-ui.com/colors)**: 12-step scales with alpha steps, regenerated in HCT, mapped to roles by contrast, light and dark through `light-dark()`.
- **[Utopia](https://utopia.fyi)**: fluid type and space scales that grow with the viewport between two sizes, with no media queries.
- **Nowind's own scaling**: one input, `--F` (the body size), drives every length after Affine UI's geometry: control heights (4n − 26 at base size n: 38px at 16), insets, gutters, icon boxes and a radius scale that nests concentrically. The fluid scale follows the root font size too, and three tiers (product, content, brand) re-run the whole system at a larger rhythm for a region.

## Why Nowind

**It is a runtime system.** Every class is in the file before the page loads, so it works with HTML that arrives at runtime: streamed responses, CMS output, server-rendered fragments and UI generated on the fly. There is nothing to compile and nothing to purge.

**It is built for agents and generative UI.** A model writing interface markup does best with a vocabulary it already knows, a small set of choices and defaults that look right without help. Nowind gives it exactly that: Tailwind names, a constrained scale, and no need to write CSS or `style=""`. Every class, token and component is also described as data, so an agent can look things up instead of guessing:

- [`nowind.manifest.json`](nowind.manifest.json): every class group, variant and count
- [`components.manifest.json`](components.manifest.json): every component's purpose, use, avoid and the classes its example uses
- `theme/*.manifest.json`: every token, what it is for and how it is derived

**The defaults are the product.** Unstyled HTML already looks considered: the reset themes headings, links, fields, selects, checkboxes, radios, switches, sliders, file inputs, `progress`, `meter` and the dialog backdrop, with focus rings, transitions and reduced-motion handling built in. A button is one control tall and a card pads to nest its children's corners without anyone choosing a number. Smaller and larger sizes are there when a design asks for them (nested controls, tiers, `icon-sm`, `icon-lg`), but the default is always the sensible one.

**The tokens are yours.** Every class reads a CSS variable. Change a palette, the type scale, the viewport range or the corner curvature in the token layer and every class follows.

## Philosophy: classes first

Prewind works global first. Nowind keeps that order for people, and adds a rule for machines:

1. **Tokens and global CSS** for what should look the same everywhere: retune the theme, or put site-wide rules in `@layer styles`.
2. **Utility classes** for everything else. Markup carries its own look, so generated UI needs no stylesheet.
3. **No inline styles.** The scale has a step for every common case; if a value isn't on it, it belongs in the token layer.

Markup drives state, too: set `aria-pressed`, `aria-selected`, `aria-current`, `open` or `aria-invalid` and the `pressed:`, `selected:`, `current:`, `open:` and `invalid:` variants follow. No script swaps classes.

## Getting started

Link one file:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kimgranlund/nowind@v0.10.0/dist/nowind.min.css">
```

The link pins release `v0.10.0`. Or copy `dist/nowind.min.css` into your project. Releases are in [CHANGELOG.md](CHANGELOG.md). Browse the [component docs](https://kimgranlund.github.io/nowind/site/docs/components-index.html), the [showcase](https://kimgranlund.github.io/nowind/site/components.html), the [specimen](https://kimgranlund.github.io/nowind/site/specimen.html) and the [class list](https://kimgranlund.github.io/nowind/site/docs/classes.html) on GitHub Pages.

```html
<article class="max-w-form p-md rounded-md bg-neutral-1 border border-neutral-6 shadow-sm">
  <span class="text-xs font-mono uppercase tracking-widest fg-accent-1-11">Release</span>
  <h3 class="text-base font-semibold">Nowind 0.10</h3>
  <p class="fg-neutral-11">Fluid type, Radix palettes and one geometric system.</p>
  <button class="inline-flex items-center h-control px-control gap-gutter rounded-sm state border border-transparent bg-accent-1-9 fg-accent-1-contrast font-medium">
    <i class="icon ph ph-arrow-right"></i><span>Read more</span>
  </button>
</article>
```

Nowind declares the layers `reset, styles, nowind`. Put your own CSS in `@layer styles` and a utility class always wins over it:

```css
@layer styles {
  .site-nav { display: flex; gap: var(--space-md); }
}
```

### The theme

`theme.css` holds the token layer: colors, type, space, geometry, radii, shadows, motion and materials, each a group of CSS variables in `theme/`. The bundle inlines it. To retune, override tokens in `@layer styles`, or edit the theme files and rebuild (see [Changing the theme](#changing-the-theme)).

Fonts load with the theme: Inter (`--font-body`), Inter Tight (`--font-heading`, `--font-display`) and IBM Plex Mono (`--font-mono`) from Google Fonts, each with a system fallback.

### The included reset

The reset, in the `reset` layer with every selector in `:where()`, sets `box-sizing`, zero-width solid borders (so `border` sets only a width), sizes unsized headings from the type roles, keeps link underlines, gives buttons and links a focus ring and text fields an accent border, themes native form controls, transitions every interactive element and turns motion off for people who ask for less.

## Theming

### Colors

After Radix, each palette is twelve steps plus twelve alpha steps, regenerated in HCT so the steps are even in perceived lightness, and each step switches for dark mode by itself through `light-dark()`. There is no `dark:` variant.

Palettes: `neutral` (slate), `accent-1` (blue), `accent-2` (violet), `accent-3` (plum), `accent-4` (crimson), `danger`, `warning`, `success`, `info`.

- **Steps** for direct use: `bg-neutral-3`, `fg-accent-1-11`, `border-danger-7`, `bg-neutral-a4`, `fg-accent-1-contrast` (text on step 9).
- **Roles** by contrast, for your own CSS and semantic classes: `--bg`, `--component-weak` / `--component` / `--component-strong` (rest, hover, pressed), `--border-weak` / `--border` / `--border-strong`, `--solid` / `--solid-strong`, `--fg-subtle` / `--fg-weak` / `--fg` / `--fg-strong`, each with a palette suffix (`--border-danger`, `--fg-accent-1-weak`).

A page follows the OS setting; `data-color-mode="dark"` (or `light`) on any element forces a mode inside it.

### Tokens in your own CSS

```css
@layer styles {
  .callout {
    padding: var(--space-md);
    background: var(--component-accent-1-weak);
    border: var(--border-width) solid var(--border-accent-1-weak);
    border-radius: var(--radius-md);
    color: var(--fg-accent-1);
  }
}
```

The full list, with what each token is for, is in the manifests in `theme/`.

## Fluid sizing

Nowind starts from Tailwind's scales and then runs them through its own systems.

**Tailwind's steps.** Type is Tailwind v4's scale as fractions of the base, with Tailwind's line heights: `text-xs` 0.75, `sm` 0.875, `base` 1, `lg` 1.125, `xl` 1.25, `2xl` 1.5, `3xl` 1.875, `4xl` 2.25, `5xl` 3, `6xl` 3.75. Space is Tailwind's spacing unit in t-shirt names: `3xs` 1, `2xs` 2, `xs` 3, `sm` 4, `md` 6, `lg` 8, `xl` 12, `2xl` 16, `3xl` 24, `4xl` 32 (× 0.25 of the base). Breakpoints and container widths are Tailwind's. At a 16px base every step is Tailwind's exactly.

**Utopia's base.** The base itself is fluid, as in Prewind: a CSS `clamp()` from 14px on a phone to 18px on a wide screen, so every step grows with the viewport and keeps its ratio to the base.

Nowind's own systems act on that base:

- **One input.** Space steps are multiples of `--F`, the body size, and so is every control length. At the root `--F` is the fluid body size; inside a `.scope` or a tier it is that element's own font size, so a region with smaller type spaces itself to match.
- **Affine's geometry.** From `--F` (n) come the slot (2n − 8, the icon box and small control), the margin (n − 9), the control height (slot + 2 margins, 4n − 26), the inset (margin − border) and the gutter. Controls, fields, segmented controls, toolbars, table rows and menu items share one height.
- **The root scales everything.** The vw term of every clamp is scaled by the root font size (CSS typed arithmetic), so `html { font-size: 14px }` resizes type, space, radii and controls by 14/16 at any width. Breakpoints stay in px.

| Base size n | 12 | 14 | 16 | 18 |
|---|---|---|---|---|
| Control height (4n − 26) | 22 | 30 | 38 | 46 |
| Slot, small control (2n − 8) | 16 | 20 | 24 | 28 |

### Radius and nesting

One unit runs the radius scale: each step is one margin from the next (`rounded-xs` control − M, `rounded-sm` the control, `rounded-md` + M for cards and popovers, `rounded-lg` + 2M for dialogs, `rounded-xl` + 3M). The padding between two levels is the inset, `p-inset`, so a container holds the next step down with parallel curves; for any other padding, `rounded-inner` takes the parent's radius minus its padding and border.

```html
<div popover class="p-inset rounded-md border">
  <a class="h-control px-control rounded-sm">Rename</a>
</div>
```

### Sizes

A smaller or larger component is a region with a smaller or larger base: wrap it in `scope text-sm` or `scope text-lg` and every length inside recomputes from that size. Inside a scope, leave `text-base` off so the component's text follows too.

```html
<div class="scope text-sm">
  <button class="inline-flex items-center h-control px-control gap-gutter rounded-sm border border-transparent bg-neutral-a2 font-medium">
    <i class="icon ph ph-download-simple"></i><span>Export</span>
  </button>
</div>
```

### Tiers

A tier re-runs the whole system for a region at a different rhythm, as product, editorial and marketing surfaces need:

| Class | Body size | Spacing |
|---|---|---|
| `tier-product` | the base | 1× |
| `tier-content` | + 2px | 1.5× |
| `tier-brand` | + 4px | 2× |

Every length inside a tier recomputes: type, space, controls, radii and shadows. Tiers nest without stacking: a `tier-product` frame inside a `tier-content` page is product-sized again.

## Nowind, Prewind and Tailwind

**Choose Nowind when:**

- You want one runtime file, no build, no dependencies
- Markup is written or generated at runtime, by people, a CMS or a model
- You want defaults that look right and a constrained scale over arbitrary values
- You want Radix-style palettes, fluid sizing and dark mode without configuration

**Choose Tailwind when:** you want arbitrary values (`w-[347px]`), a build step's tree-shaking, or a plugin ecosystem.

### What Nowind adds to Prewind

- Grid (`grid-cols-1` … `12`, `col-span-*`), container queries (`@container`, `@md:`) and a `2xl:` breakpoint
- State variants driven by ARIA (`pressed:`, `selected:`, `current:`, `expanded:`, `open:`, `invalid:`, `has-checked:`, `disabled:`) and group variants (`group-hover:`, `group-open:`)
- A state layer: `state` washes the text color over any element on hover, focus, press and selection, in any palette
- Transitions on by default, spring easings, `animate-spin`, `animate-pulse`
- Control geometry (`h-control`, `px-control`, `size-control`, the `-nested` forms, `gap-gutter`), icon boxes (`icon`, `icon-sm`, `icon-lg`) and nesting radii
- Radix palettes with alpha steps and roles; `text-{size}` sets the line height, as in Tailwind v4
- Tiers, materials (`material-frosted`, `material-glass` with a refracting `lens`) and a themed reset for native controls
- Logical sides (`ps-`, `me-`, `start-`, `border-s`, `rounded-e-*`) for right-to-left languages

### What Nowind leaves out

- **Arbitrary values.** No bracket syntax. A value the scale lacks belongs in the token layer.
- **A `dark:` variant.** Every color switches by itself.
- **`bg-opacity-*`.** Use the alpha steps: `bg-accent-1-a3`.
- **Margins and colors at breakpoints.** Breakpoint and container variants cover layout only.

## Reference

Every class and its declarations: [classes.md](classes.md), or browse them as [regular](https://kimgranlund.github.io/nowind/site/docs/classes.html) and [semantic](https://kimgranlund.github.io/nowind/site/docs/semantic.html) classes. Regular classes name a step or a value (`p-md`, `text-lg`, `bg-neutral-3`); semantic classes name a role (`p-surface`, `fg-weak`, `text-heading-md`). Your markup may use either. The examples here and in the docs use regular classes, so every step they choose is visible.

| Group | Examples |
|---|---|
| Spacing | `p-md`, `px-lg`, `mt-xs`, `-mt-sm`, `mx-auto`, `gap-sm`, `p-inset` |
| Type | `text-xs` … `text-6xl`, `font-medium` … `font-extrabold`, `font-display`, `font-mono`, `tracking-tight`, `uppercase`, `tabular-nums`, `truncate` |
| Color | `fg-neutral-11`, `bg-accent-1-9`, `fg-accent-1-contrast`, `border-neutral-6`, `bg-neutral-a4` |
| Borders and radius | `border`, `border-2`, `border-b`, `border-dashed`, `rounded-xs` … `rounded-xl`, `rounded-full`, `rounded-inner` |
| Shadow | `shadow-xs` … `shadow-xl`, `inset-shadow-xs`, `inset-shadow-sm` |
| Controls and icons | `h-control`, `px-control`, `size-control`, `h-nested`, `size-nested`, `gap-gutter`, `icon`, `icon-sm`, `icon-lg` |
| Layout | `flex`, `grid`, `grid-cols-3`, `col-span-2`, `basis-1/3`, `items-center`, `justify-between`, `container`, `@container` |
| Sizing | `w-full`, `w-fit`, `w-1/3`, `max-w-text`, `max-w-form`, `min-h-dvh`, `aspect-video`, `aspect-square` |

### Text sizes in practice

Every example follows one size contract, enforced by the examples lint: controls, table cells and body copy are `text-base`; labels, table headers, supporting lines and badges `text-sm`; titles `text-base font-semibold` (`text-lg` in a dialog); and an icon takes the step of the text beside it. The [Type and space](https://kimgranlund.github.io/nowind/site/docs/type-space.html) page has the table.

### Buttons, fields and icons

There is no button or field component: each is a stack of classes, and the docs show every pattern. Wrap a label in a `<span>`, so `px-control` can find an icon at either edge and pad it one margin less.

```html
<button class="inline-flex items-center h-control px-control gap-gutter rounded-sm state border border-transparent bg-neutral-a2 fg-neutral-12 font-medium">
  <i class="icon ph ph-floppy-disk"></i><span>Save</span>
</button>

<div class="flex items-center gap-gutter h-control px-control rounded-sm border bg-neutral-1 cursor-text">
  <i class="icon ph ph-scales fg-neutral-11"></i>
  <input inputmode="decimal" class="grow min-w-0 self-stretch p-0 border-0 bg-transparent" value="72.5">
  <span class="fg-neutral-11">kg</span>
</div>
```

Icons use [Phosphor](https://phosphoricons.com)'s web font; link the weights you use (`ph` regular, `ph-bold`):

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/regular/style.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/bold/style.css">
```

Every glyph sits in an `icon` box, one slot square.

### Patterns

Each pattern is a stack of classes; the [component docs](https://kimgranlund.github.io/nowind/site/docs/components-index.html) show each one live with its code. The ones people reach for first:

| Pattern | Classes |
|---|---|
| Card | `p-md rounded-md border border-neutral-6 bg-neutral-1`; children with corners take `rounded-inner` |
| Segmented control | Group `inline-flex h-control rounded-sm border-2 border-transparent bg-neutral-a2 role="group"`; each `<button aria-pressed>` is `h-full px-nested rounded-inner border-0 bg-transparent hover:bg-neutral-4 pressed:bg-white fg-neutral-11 pressed:fg-black font-medium`. Small controls (`h-nested`, `px-nested`, `size-nested`) sit only inside an inset group like this one, never beside full-size controls |
| Badge | `inline-flex items-center h-nested px-nested rounded-full border bg-success-3 border-success-6 fg-success-11 text-sm font-medium`; an icon in it is `icon icon-sm` |
| Alert | One line: `flex items-center gap-gutter py-xs ps-xs pe-sm rounded-md border border-info-6 bg-info-3`, icon `fg-info-11`, text `fg-info-12`. With a title: `flex flex-col gap-3xs p-xs`, the detail `text-sm fg-info-11` |
| Select | `<select class="select-base h-control px-control rounded-sm border border-neutral-5 hover:border-neutral-7 bg-neutral-1 w-full">`; `select-base` opts in to the styled picker, with its caret and check |
| Switch | `<input type="checkbox" role="switch">`; the reset draws it |
| Dialog | `<dialog class="m-auto p-lg rounded-lg bg-neutral-1 border-0 shadow-xl max-w-form w-full">`, title `text-lg font-semibold`, actions `flex justify-end gap-xs`. Open it with `commandfor` and `command="show-modal"` |
| Table | Wrapper `rounded-md border border-neutral-6 overflow-x-auto`; cells `h-control px-control`, headers add `text-sm font-medium fg-neutral-11`, rows `border-b border-neutral-6`, numbers `text-end tabular-nums` |

Status colours follow one pattern across every palette: step 3 fills, 6 draws the border, 11 is text and icons, 12 is strong text, and 9 is the solid fill with `fg-{palette}-contrast` on it.

## Variants

| Prefix | Covers | Example |
|---|---|---|
| `hover:` | Colour roles, the control steps of neutral, accent-1 and danger, opacity, cursor (only on devices that can hover). For hover and press tints use `state`; keep `hover:bg-*` for an element whose pressed or selected state changes its fill | `hover:bg-neutral-4` |
| `active:`, `focus-visible:`, `focus-within:` | Colors; borders for focus | `focus-within:border-accent-1-8` |
| `selected:`, `current:`, `pressed:`, `expanded:`, `open:`, `has-checked:` | Colors, and `shadow-xs`/`-sm`/`-none` to lift a chosen item | `pressed:bg-white pressed:fg-black` |
| `invalid:`, `has-invalid:`, `disabled:` | Colors; opacity and cursor for disabled | `has-invalid:border-danger-7` |
| `group-hover:`, `group-focus-within:`, `group-open:` | Opacity, visibility, rotation, text color | `group-open:rotate-180` |
| `sm:` 640, `md:` 768, `lg:` 1024, `xl:` 1280, `2xl:` 1536 | Layout: display, grid, flex, alignment, widths, inline padding, gaps | `md:grid-cols-3` |
| `@sm:` 384, `@md:` 448, `@lg:` 512 | A component's layout (display, direction, grid, basis, gaps, alignment), against the nearest `@container` | `@md:flex-row` |

```html
<button role="tab" aria-selected="true"
        class="h-control px-control border-b-2 border-transparent selected:border-accent-1-8 fg-neutral-11 selected:fg-neutral-12">
  <span>Profile</span>
</button>
```

## Changing the theme

**Colors.** Each palette is one file in `theme/colors-semantic/`. Switch a palette's family by changing its import, and set its contrast token from the family's `solidLabel`. [AGENTS.md](AGENTS.md) has the steps for adding a palette.

**Type and space.** Regenerate the fluid base with your own viewport range and base sizes (the step fractions are Tailwind's, in `scripts/utopia.mjs`):

```bash
node scripts/utopia.mjs --min-vw 360 --max-vw 1240 --min-base 14 --max-base 18
```

**Geometry.** The slopes and offsets in `theme/theme.geometry.css` set the control height, margin and radius curves. The defaults are Affine's, with corners 2px softer (`--radius-offset: -4px`); raise or lower that one token to change every corner at once, and nesting stays exact.

**Shadows, motion and materials** are generated from a few constants in `scripts/shadows.mjs`, `scripts/motion.mjs` and `scripts/materials.mjs`.

After any change, regenerate the classes and the bundle:

```bash
node scripts/utilities.mjs
node scripts/bundle.mjs
```

The scripts need Node 18 or later and have no dependencies. People who use Nowind never run them. [AGENTS.md](AGENTS.md) lists every file, the script order and the rules `scripts/check.mjs` enforces.

## Browser support

Nowind uses `light-dark()`, `@layer`, `@property`, `@container`, `clamp()` and `:where()`, which every current browser supports. Some features are progressive and fall back cleanly: CSS typed arithmetic (the root-scaled fluid term), anchor positioning, the customizable `select`, `field-sizing`, `interpolate-size` and the glass lens (Chromium only).

## Credits

Derived from [Prewind](https://github.com/codepilotsf/prewind) by [Codepilot](https://codepilot.com), with the class system of [Tailwind CSS](https://tailwindcss.com), the color system of [Radix Colors](https://www.radix-ui.com/colors) and the fluid scales of [Utopia](https://utopia.fyi). Geometry after Affine UI; type roles, shadows, motion and materials after the Massimo kit.
