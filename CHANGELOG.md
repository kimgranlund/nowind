# Changelog

## Unreleased

- **Icon classes are primitives:** `icon`, `icon-sm`, `icon-md` and `icon-lg` are lengths from the base size, so they count as regular classes and the examples use them: `<i class="icon ph ph-gear">` in place of five layout classes and a type size (which made icons about 18% too big). Carets are `icon icon-sm`. The examples lint requires every Phosphor icon to sit in an `icon` box.
- **Square icon buttons:** every icon-only button in the examples pads the same on all sides (`p-xs`, or `p-3xs` when small), so it is square; the examples lint rejects uneven padding on one.
- **Docs pages:** previous and next sit side by side at every width; table cells pad less on a phone; a class name in a table breaks only at a hyphen or colon, never mid-word.
- **Radii nest, after Affine UI:** one unit runs the radius scale: `rounded-xs` (control − margin), `rounded-sm` (control), new `rounded-md` (control + margin), `rounded-lg` (+2 margins) and `rounded-xl` (+3). New `p-inset` (margin − border) pads between levels, so `rounded-md p-inset border` holds `rounded-sm` items concentrically. New `rounded-inner` gives any item the parent's radius minus its padding and border. Breaking: `rounded-lg` was the card radius and is now the dialog's; cards are `rounded-md`, dialogs `rounded-lg`.
- **Docs for the system:** new Colour, Type and space, States and variants, and Materials pages, their tables read from the manifests (state-variant counts from `nowind.css`). The docs home's figures come from the manifests too. The README covers the lens, backdrops, fields, native controls, default transitions and the new files.
- **Single-line controls never wrap:** the reset keeps buttons, selects and inputs on one line. In `select-base`, a `<button>` holding `<selectedcontent>` lets a long value end in an ellipsis before the caret; `select-base` no longer zeroes its block padding. Toasts move their actions to a second line instead of squeezing the message. New `basis-0`.
- **Carets are always the small icon size:** `caret`, the select's picker icon and every caret in the examples (checked by the examples lint).
- **Showcase form to the field standard:** every field is a slot box with a leading icon for the kind of value, a bare input, `focus-within:` and `has-invalid:` on the box, units in a suffix, a themed select, and a counted bio. New `has-checked:` state variant lets a choice card follow its checked radio. `select-base` puts its caret at the end of the field.
- **Manifests:** `components.manifest.json` lists every component as data (page, group, summary, use, avoid, classes). `nowind.manifest.json` counts state and group variants and describes rotation, the open-popover group and the contrast classes; the materials manifest describes the lens.
- **Transitions by default:** the reset gives every interactive element (links, buttons, summaries, fields, labels and the button, tab, option, menuitem and switch roles) a transition on its colours, opacity, shadow and transforms, at the motion duration and easing; reduced motion cuts it. The examples lint requires a transition class on any other element that changes with state.
- **Indicators follow state:** new `rotate-0/45/90/180` and `-rotate-45/90/180`; `group-open:` now also matches a group holding an open popover and takes rotations, so a caret with `transition group-open:rotate-180` turns over when its disclosure or menu opens.
- **Glass lens, after Apple's Liquid Glass:** `lens` refracts what is behind a glass part. The site's script draws a displacement map for each lens at its own size and corner radius: the surface refracts like a rounded glass edge (the bend follows the slope of a quarter-circle bevel, steep at the rim and easing across a band up to a third of the part's height), the whole body magnifies slightly, and red, green and blue bend by slightly different amounts. Clear glass drops its gloss band and blur (0.5px) and catches the light as two thin crescents on opposite corners. The lens runs where the page sets `data-lens="on"`, which the script does in Chromium, the only engine that applies an SVG filter in `backdrop-filter`; elsewhere glass keeps its blur. The showcase has a glass slider over a track to show it.
- **Light and dark toggle:** a button in the band switches the scheme and remembers it; a head script applies the choice before the page paints.
- **Dot grid:** `bg-dots` paints a dot grid in `currentColor`, spaced by `bg-dots-sm`, `-md` or `-lg`. The materials demo uses it in place of coloured stripes, so the blur of frosted and glass is easy to read.
- **Examples in primitives:** every component snippet and showcase block now uses regular classes only (palette steps, the space scale, type sizes), checked by `scripts/templates.py --lint`. The materials, shell and tiers demos keep their semantic classes. To keep hover and states, the raw steps of neutral, accent-1 to accent-4 and danger now take hover and state variants (nowind.css 236 → 381 KiB, the minified bundle 41 → 52.5 KB gzipped), and new `fg-{palette}-contrast` classes give text on a solid.
- **Breaking, state variants without `aria-`:** `aria-selected:` is now `selected:`, `aria-current:` is `current:`, `aria-pressed:` is `pressed:`, `aria-expanded:` is `expanded:` and `aria-invalid:` is `invalid:`. They still match the same ARIA attributes.
- **Field slots:** a field is a box around a bare input with five slots: leading icon, prefix, input, suffix, trailing. New state variants `focus-within:` and `has-invalid:` let the box show the input's focus and errors. An `h-nested` or `size-nested` control at either end of a control now takes the same inset as an icon.
- **Text field docs:** slots, ten data types (password with a show toggle, card number, date, time, weight, percentage, quantity, colour, postal code, duration) with the right `type`, `inputmode` and `autocomplete`, and the invalid, counted, read-only and disabled states.
- **One control recipe:** buttons, links, inputs, selects and textareas share height, side padding, a border width (transparent on fills, so a solid button and a field line up to the pixel), radius and type. New `rounded-control` and `rounded-nested`. `scripts/check.mjs` flags a control that drifts.
- **One caret:** `caret` on an icon box draws the disclosure chevron in CSS, and `select-base` draws the same one as its picker icon. Both turn over when open (`[open]`, `aria-expanded="true"`, an open select).
- **Native controls:** the reset themes the file input's button, `progress` and `meter` (which turns success, warning or danger from its `low`, `high` and `optimum`), with system colours in forced colours. New `field-sizing-content` and `field-sizing-fixed`.
- **Select:** `select-base` centres the chosen value in the field, the highlighted option shows by its background with no focus ring, and the picker arrow takes the weak text colour.
- **Focus:** text fields (text-like inputs, textarea, select) no longer get the focus ring; their border turns accent instead. Buttons, links and checkable controls keep the ring, and in forced colours a focused field gets a Highlight outline.
- **One page template:** every page (docs, component pages, the showcase, the specimen, the utilities demo, the landing page) shares one frame after Vignelli's Unigrid: an inverse band with the four sections, a bar with a site-map menu (every section and page, no script), a search field and previous and next, and blocks with their label in three of twelve columns. The docs sidebar, phone menu and on-page contents are gone.
- **Search:** press ⌘K, Ctrl+K or `/` on any page to search every page, block heading, component and class. `site/search.json` is written with the pages.
- **Class lists:** roles named after `accent-1` to `accent-4` (`bg-accent-1`, `bg-component-accent-4`) now list as semantic, not regular.
- **Docs frame:** the page scrolls as a whole. The header is sticky, the sidebar sticks under it, and `main` is no longer a scroll box. Below 1024px only the Menu row shows, the GitHub button is icon-only below 1280px, tables wrap instead of scrolling sideways, and the class lists become two-line rows on a phone. New `scroll-pt-header` and `scroll-mt-*` keep linked rows clear of sticky bars.
- **Breaking, background and border role classes:** the role group is dropped when it matches the prefix, as `fg-` already did: `bg-bg` is `bg`, `bg-bg-accent-1` is `bg-accent-1`, `border-border-weak` is `border-weak`. Plain `border-border` is `border-default`, and the reset now draws every border in `--border`, so `border` alone needs no colour class.
- **Breaking, text colour classes:** raw steps and on-solid now take `fg-` like the text roles: `text-accent-1-11` is `fg-accent-1-11`, `text-on-solid-danger` is `fg-on-solid-danger`. `text-inherit` and `text-current` are `fg-inherit` and `fg-current`. Every text colour class now starts with `fg`.
- **Site moved:** the landing page, showcase, specimen and utilities demo are in `site/`, the docs in `site/docs/`. The root `index.html` redirects to `site/`.
- **Classes page:** `site/docs/classes.html` lists all 1349 base classes by category with their declarations, a preview for colours, borders, radius and shadow, and a filter, under a grid linking to each group. Regular classes (a scale step or a value: `p-md`, `border-warning-7`) and semantic classes (a role: `p-surface`, `fg-weak`, `text-heading-md`) get separate pages, `classes.html` and `semantic.html`. Component pages link each class to its row.

## 0.8.0 (2026-11-25)

- **Group variants:** `group` on a parent, `group-hover:`, `group-focus-within:` and `group-open:` on a child (opacity, visibility and `fg-*`), for tooltips and reveal-on-hover.
- **Offsets:** `top-full`, `bottom-full`, `left-full`, `right-full`.
- **Component docs:** tooltip, combobox, sortable table, date range and media card (26 pages).
- **Forced colors:** in Windows High Contrast, controls and overlays keep an outline, selected and current items get a Highlight outline, and checkboxes, radios, switches and sliders are redrawn in system colors.

## 0.7.0 (2026-11-25)

- **Renamed:** text-color role classes drop `text-`: `text-fg-weak` is now `fg-weak`, `text-fg-accent-1` is `fg-accent-1`, with their variants (`hover:fg`, `aria-selected:fg`). `text-on-solid-*` and the raw-step `text-*` classes are unchanged.

## 0.6.0 (2026-11-25)

- **Component docs:** a page per component in `templates/` (21 so far), each with the component live, its HTML to copy, when to use it and when not to, and the classes it uses; plus an index. Content lives in `scripts/component_docs.py`.

## 0.5.0 (2026-11-25)

- **Tiers grow the type:** inside `tier-content` and `tier-brand` the whole type scale and the type roles grow with the tier's body size.
- **Sticky under a header:** `top-header`, `h-below-header`, `max-h-below-header`.
- **Breakpoints** now cover padding, position, `top-*`, overflow and heights (`lg:sticky`, `md:p-surface`, `lg:overflow-y-auto`).
- **Level padding sides:** `pt-` and `pb-` for `surface`, `dialog`, `region` and `page`.
- **Reset:** inline code no longer wraps at hyphens; `list-none` also hides Safari's `<summary>` marker.

## 0.4.0 (2026-11-25)

- **Popovers, select, animation:** `anchor-*` (CSS anchor positioning for popovers), `select-base` (customizable select), `animate-spin`, `animate-pulse`.
- **Showcase components:** accordion, dropdown, modal dialog, avatar group, progress, stepper, input groups, description list, activity, pricing, dropzone, tags, rating, popover menu and info, toast stack, loading states, toolbar, notifications, command palette.
- **Fixed:** the reset's backdrop and selection rules were ignored (pseudo-elements in `:where()`); the scrim now dims only modal dialogs.
- **State variants:** `active:`, `focus-visible:`, `aria-selected:`, `aria-current:`, `aria-pressed:`, `aria-expanded:`, `open:`, `aria-invalid:`, `disabled:`, colors only, for the neutral and accent roles. The showcase's tabs, toggles, nav and pagination now take their look from ARIA state.
- **Docs-site templates:** `templates/` holds a docs home, a guide with sidebar and table of contents, a reference page and a changelog, built only from utility classes and generated by `scripts/templates.py`.

## 0.3.0 (2026-11-25)

- **Fonts:** `theme.css` and the bundle load Inter, Inter Tight and IBM Plex Mono from Google Fonts. `--font-heading` is Inter Tight and `--font-mono` IBM Plex Mono.
- **Motion:** Massimo's springs (`--ease-smooth`, `--ease-snappy`, `--ease-bouncy`) as CSS `linear()` easings with their durations, ease curves, and `transition-*`, `duration-*`, `ease-*` classes.
- **Page grid and shell:** Affine's grid gutter, inset and edge margins, and shell lengths (sidebar, rail, header, measure, dock width) with `gap-grid`, `p-grid-inset`, `px-grid`, `w-sidebar`, `w-rail`, `h-header`, `max-w-measure`.
- **Form marks:** the reset draws checkboxes, radios, switches (`role="switch"`) and sliders at Affine's mark sizes; `mark-sm`, `mark-lg`.
- **Materials:** Massimo's flat, physical, frosted, glass and outline materials (`material-*` on a region, `relief-*` on a part), with generated paint tokens.
- **Dev server:** `scripts/serve.mjs` serves previews with caching off.

## 0.2.0 (2026-11-25)

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
