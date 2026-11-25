#!/usr/bin/env node
// Generates nowind.css: Prewind-style utility classes over the Nowind theme tokens.
// Usage: node scripts/utilities.mjs
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => readFileSync(join(root, p), "utf8");
const props = (css) => [...css.matchAll(/^\s*(--[\w-]+)\s*:/gm)].map((m) => m[1]);

// ---- Tokens, read from the theme so the classes follow it ----
const semanticDir = "theme/colors-semantic";
const paletteProps = readdirSync(join(root, semanticDir)).filter((f) => f.endsWith(".css")).flatMap((f) => props(read(`${semanticDir}/${f}`)));
const colorProps = props(read("theme/theme.colors.css"));
const COLORS = [...paletteProps, ...colorProps]
  .filter((p) => !/-contrast-(white|black)$/.test(p) && !/^--shadow/.test(p))
  .map((p) => p.slice(2));
const typeProps = props(read("theme/theme.typography.css"));
const SIZES = typeProps.filter((p) => /^--text-[a-z0-9]+$/.test(p)).map((p) => p.slice(7));
const KICKERS = typeProps.filter((p) => /^--kicker-(sm|md|lg)$/.test(p)).map((p) => p.slice(2));
const roleProps = props(read("theme/theme.type-roles.css"));
const ROLES = roleProps.filter((p) => p.endsWith("--font-family")).map((p) => p.slice(2, -"--font-family".length));
const roleHas = (r, prop) => roleProps.includes(`--${r}--${prop}`);
const SPACE = props(read("theme/theme.space.css")).map((p) => p.slice(8));

// ---- Class table ----
const D = new Map();
const add = (cls, decl) => D.set(cls, decl);
const sv = (s) => (s === "0" ? "0" : `var(--space-${s})`);
const box = { "": ["{p}"], t: ["{p}-top"], r: ["{p}-right"], b: ["{p}-bottom"], l: ["{p}-left"], x: ["{p}-inline"], y: ["{p}-block"] };

// Spacing
for (const [pre, prop] of [["p", "padding"], ["m", "margin"]]) {
  for (const [side, ps] of Object.entries(box)) {
    for (const s of ["0", ...SPACE]) add(`${pre}${side}-${s}`, ps.map((p) => `${p.replace("{p}", prop)}: ${sv(s)}`).join("; "));
  }
}
for (const [side, ps] of Object.entries(box)) {
  for (const s of SPACE) add(`-m${side}-${s}`, ps.map((p) => `${p.replace("{p}", "margin")}: calc(var(--space-${s}) * -1)`).join("; "));
  add(`m${side}-auto`, ps.map((p) => `${p.replace("{p}", "margin")}: auto`).join("; "));
}
for (const s of ["0", ...SPACE]) {
  add(`gap-${s}`, `gap: ${sv(s)}`);
  add(`gap-x-${s}`, `column-gap: ${sv(s)}`);
  add(`gap-y-${s}`, `row-gap: ${sv(s)}`);
}
for (const s of SPACE) add(`scroll-mt-${s}`, `scroll-margin-block-start: var(--space-${s})`);

// Layout
add("container", "width: min(100%, var(--container-max)); margin-inline: auto; padding-inline: var(--container-padding)");
for (const d of ["block", "inline-block", "inline", "flex", "inline-flex", "grid", "inline-grid", "contents"]) add(d, `display: ${d}`);
for (let n = 1; n <= 12; n++) add(`grid-cols-${n}`, `grid-template-columns: repeat(${n}, minmax(0, 1fr))`);
add("grid-cols-none", "grid-template-columns: none");
for (let n = 1; n <= 12; n++) add(`col-span-${n}`, `grid-column: span ${n} / span ${n}`);
add("col-span-full", "grid-column: 1 / -1");
add("hidden", "display: none");
for (const d of ["row", "col", "row-reverse", "col-reverse"]) add(`flex-${d}`, `flex-direction: ${d.replace("col", "column")}`);
add("flex-wrap", "flex-wrap: wrap");
add("flex-nowrap", "flex-wrap: nowrap");
for (const [k, v] of [["start", "flex-start"], ["center", "center"], ["end", "flex-end"], ["between", "space-between"], ["around", "space-around"], ["evenly", "space-evenly"]]) add(`justify-${k}`, `justify-content: ${v}`);
for (const [k, v] of [["start", "flex-start"], ["center", "center"], ["end", "flex-end"], ["stretch", "stretch"], ["baseline", "baseline"]]) {
  add(`items-${k}`, `align-items: ${v}`);
  add(`self-${k}`, `align-self: ${v}`);
}
add("self-auto", "align-self: auto");
add("flex-1", "flex: 1 1 0%");
add("flex-auto", "flex: 1 1 auto");
add("flex-none", "flex: none");
add("grow", "flex-grow: 1");
add("grow-0", "flex-grow: 0");
add("shrink", "flex-shrink: 1");
add("shrink-0", "flex-shrink: 0");
for (const p of ["static", "relative", "absolute", "fixed", "sticky"]) add(p, `position: ${p}`);
add("inset-0", "inset: 0");
for (const p of ["top", "right", "bottom", "left"]) {
  add(`${p}-0`, `${p}: 0`);
  add(`${p}-full`, `${p}: 100%`);
}
for (let z = 0; z <= 100; z += 10) add(`z-${z}`, `z-index: ${z}`);

// Typography
for (const t of SIZES) add(`text-${t}`, `font-size: var(--text-${t}); line-height: var(--text-${t}--line-height)`);
for (const k of KICKERS) add(`text-${k}`, `font-size: var(--${k}); line-height: calc(var(--${k}) * 1.5 - 3px); font-family: var(--kicker-font); font-weight: var(--kicker-weight); letter-spacing: var(--kicker-tracking); text-transform: var(--kicker-transform)`);
for (const r of ROLES) {
  if (KICKERS.includes(r)) continue;
  const decl = [`font-size: var(--${r})`, `line-height: var(--${r}--line-height)`, `font-weight: var(--${r}--font-weight)`, `font-family: var(--${r}--font-family)`];
  for (const p of ["letter-spacing", "font-variant-numeric", "text-transform", "font-style", "font-variant-ligatures"]) if (roleHas(r, p)) decl.push(`${p}: var(--${r}--${p})`);
  add(`text-${r}`, decl.join("; "));
}
for (const a of ["left", "center", "right", "justify", "start", "end"]) add(`text-${a}`, `text-align: ${a}`);
add("italic", "font-style: italic");
add("not-italic", "font-style: normal");
add("underline", "text-decoration-line: underline");
add("line-through", "text-decoration-line: line-through");
add("no-underline", "text-decoration-line: none");
for (const w of ["normal", "medium", "semibold", "bold"]) add(`font-${w}`, `font-weight: var(--font-weight-${w})`);
for (const f of ["body", "heading", "mono", "control"]) add(`font-${f}`, `font-family: var(--font-${f})`);
add("font-sans", "font-family: var(--font-body)");
for (const l of ["none", "tight", "snug", "normal", "relaxed"]) add(`leading-${l}`, `line-height: var(--leading-${l})`);
for (const t of ["tight", "normal", "wide", "widest"]) add(`tracking-${t}`, `letter-spacing: var(--tracking-${t})`);
add("uppercase", "text-transform: uppercase");
add("lowercase", "text-transform: lowercase");
add("capitalize", "text-transform: capitalize");
add("normal-case", "text-transform: none");
add("tabular-nums", "font-variant-numeric: tabular-nums");
add("text-balance", "text-wrap: balance");
add("text-pretty", "text-wrap: pretty");

// Color
// Each property takes only the roles made for it; raw palette steps go everywhere (alpha steps on backgrounds only).
const PALETTES = [...new Set(paletteProps.map((p) => p.match(/^--([a-z]+(?:-\d)?)-1$/)).filter(Boolean).map((m) => m[1]))];
const step = (c) => PALETTES.some((p) => new RegExp(`^${p}-\\d+$`).test(c));
const alphaStep = (c) => PALETTES.some((p) => new RegExp(`^${p}-a\\d+$`).test(c));
const contrastStep = (c) => PALETTES.some((p) => c === `${p}-contrast`);
const forText = (c) => step(c) || contrastStep(c) || /^(fg|on-solid)(-|$)/.test(c);
const forBg = (c) => step(c) || alphaStep(c) || /^(bg|component|solid|scrim)(-|$)/.test(c) || /-(surface|indicator|track)$/.test(c);
const forBorder = (c) => step(c) || /^border(-|$)/.test(c);
// A colour class is the property prefix plus the token name, minus the role group when it matches the prefix:
// --fg-weak is fg-weak, --bg-accent-1 is bg-accent-1, --border-weak is border-weak. --border itself is border-default,
// because border is the width class (the reset already draws borders in --border).
const isRoleToken = (c) => !step(c) && !alphaStep(c) && !/^shadow/.test(c) && !/-(surface|indicator|track)$/.test(c);
const ROLE_CLASSES = new Set();
const colorAdd = (name, c, decl) => { add(name, decl); if (isRoleToken(c)) ROLE_CLASSES.add(name); };
for (const c of COLORS) {
  if (forText(c)) colorAdd(/^fg(-|$)/.test(c) ? c : `fg-${c}`, c, `color: var(--${c})`);
  if (forBg(c)) colorAdd(/^bg(-|$)/.test(c) ? c : `bg-${c}`, c, `background-color: var(--${c})`);
  if (forBorder(c)) colorAdd(c === "border" ? "border-default" : /^border-/.test(c) ? c : `border-${c}`, c, `border-color: var(--${c})`);
}
add("fg-inherit", "color: inherit");
add("fg-current", "color: currentColor");
add("bg-transparent", "background-color: transparent");
add("border-transparent", "border-color: transparent");
for (let o = 0; o <= 100; o += 10) add(`opacity-${o}`, `opacity: ${o / 100}`);

// Backgrounds
add("bg-repeat", "background-repeat: repeat");
add("bg-repeat-x", "background-repeat: repeat-x");
add("bg-repeat-y", "background-repeat: repeat-y");
add("bg-no-repeat", "background-repeat: no-repeat");
add("lens", "--_lens: 1");
add("bg-dots", "background-image: radial-gradient(circle, currentColor var(--_dot, 1.5px), transparent calc(var(--_dot, 1.5px) + 0.75px)); background-size: var(--_dots, var(--space-sm)) var(--_dots, var(--space-sm)); background-position: center")
for (const [n, gap, dot] of [["sm", "--space-xs", "1px"], ["md", "--space-sm", "1.5px"], ["lg", "--space-md", "2px"]]) add(`bg-dots-${n}`, `--_dots: var(${gap}); --_dot: ${dot}`);
for (const s of ["cover", "contain", "auto"]) add(`bg-${s}`, `background-size: ${s}`);
for (const p of ["center", "top", "bottom", "left", "right", "left-top", "left-bottom", "right-top", "right-bottom"]) add(`bg-${p}`, `background-position: ${p.replace("-", " ")}`);
for (const a of ["fixed", "local", "scroll"]) add(`bg-${a}`, `background-attachment: ${a}`);
add("bg-clip-text", "-webkit-background-clip: text; background-clip: text");

// Borders, radius, outline, shadow
for (const [suf, w] of [["", "var(--border-width)"], ["-0", "0"], ["-2", "2px"], ["-4", "4px"]]) {
  add(`border${suf}`, `border-width: ${w}; border-style: solid`);
  for (const [s, p] of [["t", "top"], ["r", "right"], ["b", "bottom"], ["l", "left"], ["x", "inline"], ["y", "block"]]) add(`border-${s}${suf}`, `border-${p}-width: ${w}; border-${p}-style: solid`);
}
for (const s of ["solid", "dashed", "dotted", "none"]) add(`border-${s}`, `border-style: ${s}`);
add("rounded-none", "border-radius: 0");
add("rounded-xs", "border-radius: var(--radius-nested)");
add("rounded-sm", "border-radius: var(--radius-control)");
add("rounded", "border-radius: var(--radius-control)");
add("rounded-control", "border-radius: var(--radius-control)");
add("rounded-nested", "border-radius: var(--radius-nested)");
add("rounded-lg", "border-radius: var(--radius-surface)");
add("rounded-xl", "border-radius: var(--radius-dialog)");
add("rounded-full", "border-radius: 9999px");
add("outline", "outline-width: var(--border-width); outline-style: solid");
add("outline-2", "outline-width: 2px; outline-style: solid");
add("outline-0", "outline-width: 0");
add("outline-offset-2", "outline-offset: 2px");
for (const s of ["solid", "dashed", "dotted"]) add(`outline-${s}`, `outline-style: ${s}`);
// A cast and a recess compose, as in Tailwind v4: each class sets its own part, and box-shadow draws both.
const SHADOW_BOX = "box-shadow: var(--_inset-shadow, 0 0 #0000), var(--_shadow, 0 0 #0000)";
for (const lv of ["xs", "sm", "md", "lg", "xl"]) add(`shadow-${lv}`, `--_shadow: var(--shadow-${lv}); ${SHADOW_BOX}`);
add("shadow", `--_shadow: var(--shadow-sm); ${SHADOW_BOX}`);
add("shadow-none", `--_shadow: 0 0 #0000; ${SHADOW_BOX}`);

// Motion (after Massimo's springs and Affine's single state change). The transition classes animate on the state
// change length and easing; duration-* and ease-* swap in a spring or curve.
const T = "transition-duration: var(--_duration, var(--motion-duration)); transition-timing-function: var(--_ease, var(--motion-easing))";
add("transition", `transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, translate, scale, rotate; ${T}`);
add("transition-colors", `transition-property: color, background-color, border-color, outline-color, text-decoration-color, fill, stroke; ${T}`);
add("transition-opacity", `transition-property: opacity; ${T}`);
add("transition-shadow", `transition-property: box-shadow; ${T}`);
add("transition-transform", `transition-property: transform, translate, scale, rotate; ${T}`);
add("transition-none", "transition-property: none");

// Animations (Tailwind v4 names). The reset cuts them under prefers-reduced-motion.
add("animate-spin", "animation: nw-spin 1s linear infinite");
add("animate-pulse", "animation: nw-pulse 2s var(--ease-standard) infinite");
add("animate-none", "animation: none");

// Anchor positioning: a popover placed against its invoker (the implicit anchor of popovertarget), flipping when it
// would leave the screen. Where anchor positioning is missing, the popover falls back to the browser's centred box.
const ANCHOR = "position-try-fallbacks: flip-block, flip-inline; inset: auto; margin: var(--space-3xs)";
add("anchor-bottom", `position-area: block-end span-inline-end; ${ANCHOR}`);
add("anchor-top", `position-area: block-start span-inline-end; ${ANCHOR}`);
add("anchor-end", `position-area: inline-end span-block-end; ${ANCHOR}`);
add("anchor-start", `position-area: inline-start span-block-end; ${ANCHOR}`);
add("anchor-center", `position-area: block-end center; ${ANCHOR}`);

// The customizable select (appearance: base-select): the picker takes the theme's overlay look.
add("select-base", "appearance: base-select; align-items: center; padding-block: 0");
for (const d of ["fade", "snappy", "smooth", "bouncy"]) add(`duration-${d}`, `--_duration: var(--duration-${d}); transition-duration: var(--duration-${d})`);
for (const e of ["smooth", "snappy", "bouncy", "standard", "out", "in"]) add(`ease-${e}`, `--_ease: var(--ease-${e}); transition-timing-function: var(--ease-${e})`);
for (const lv of ["xs", "sm"]) add(`inset-shadow-${lv}`, `--_inset-shadow: var(--inset-shadow-${lv}); ${SHADOW_BOX}`);
add("inset-shadow-none", `--_inset-shadow: 0 0 #0000; ${SHADOW_BOX}`);

// Interaction and misc (as Prewind)
for (const c of ["auto", "default", "pointer", "wait", "text", "move", "not-allowed", "grab", "grabbing"]) add(`cursor-${c}`, `cursor: ${c}`);
add("list-none", "list-style-type: none");
add("list-disc", "list-style-type: disc");
add("list-decimal", "list-style-type: decimal");
add("list-inside", "list-style-position: inside");
add("list-outside", "list-style-position: outside");
for (const o of ["contain", "cover", "fill", "none", "scale-down"]) add(`object-${o}`, `object-fit: ${o}`);
for (const o of ["auto", "hidden", "clip", "visible", "scroll"]) {
  add(`overflow-${o}`, `overflow: ${o}`);
  add(`overflow-x-${o}`, `overflow-x: ${o}`);
  add(`overflow-y-${o}`, `overflow-y: ${o}`);
}
add("pointer-events-none", "pointer-events: none");
add("pointer-events-auto", "pointer-events: auto");
add("resize-none", "resize: none");
add("resize", "resize: both");
add("resize-y", "resize: vertical");
add("field-sizing-content", "field-sizing: content");
add("field-sizing-fixed", "field-sizing: fixed");
add("resize-x", "resize: horizontal");
for (const [d, p, u] of [["w", "width", "vw"], ["h", "height", "vh"]]) {
  add(`${d}-0`, `${p}: 0`);
  add(`${d}-auto`, `${p}: auto`);
  add(`${d}-full`, `${p}: 100%`);
  add(`${d}-screen`, `${p}: 100${u}`);
  add(`${d}-fit`, `${p}: fit-content`);
}
for (const [d, p, u] of [["min-w", "min-width", "vw"], ["max-w", "max-width", "vw"], ["min-h", "min-height", "vh"], ["max-h", "max-height", "vh"]]) {
  add(`${d}-0`, `${p}: 0`);
  add(`${d}-full`, `${p}: 100%`);
  add(`${d}-screen`, `${p}: 100${u}`);
}
for (const [d, p] of [["h", "height"], ["min-h", "min-height"], ["max-h", "max-height"]]) {
  for (const u of ["dvh", "svh", "lvh"]) add(`${d}-${u}`, `${p}: 100${u}`);
}
for (const [f, v] of [["1/2", "50%"], ["1/3", "33.333333%"], ["2/3", "66.666667%"], ["1/4", "25%"], ["3/4", "75%"], ["1/5", "20%"], ["2/5", "40%"], ["3/5", "60%"], ["4/5", "80%"]]) {
  add(`w-${f}`, `width: ${v}`);
  add(`basis-${f}`, `flex-basis: ${v}`);
}
add("basis-full", "flex-basis: 100%");
add("basis-auto", "flex-basis: auto");
add("max-w-text", "max-width: var(--max-w-text)");
add("max-w-prose", "max-width: var(--max-w-text)");
add("max-w-form", "max-width: var(--max-w-form)");
add("max-w-container", "max-width: var(--container-max)");
add("h-control", "height: var(--control-height)");

// Controls and icons (after Affine UI's button and icon): heights, square sizes, padding that steps in by one margin on a
// side that holds an icon (the :has() rules below), the gutter gap, and an S-square icon box with its glyph size.
add("h-nested", "height: var(--nested-height)");
add("size-control", "width: var(--control-height); height: var(--control-height)");
add("size-nested", "width: var(--nested-height); height: var(--nested-height)");
add("min-w-control", "min-width: var(--control-height)");
add("min-w-nested", "min-width: var(--nested-height)");
add("px-control", "padding-inline: var(--control-padding)");
add("px-nested", "padding-inline: var(--nested-padding)");
add("gap-gutter", "gap: var(--gutter)");

// Container levels (after Affine UI): padding and gaps by what a box is, not by a size. A bordered level pads by its
// level minus the border, as Affine does, so content lands on the same line with or without a border.
const LEVEL_PAD = {
  surface: "calc(var(--surface-padding) - var(--border-width))",
  dialog: "calc(var(--dialog-padding) - var(--border-width))",
  region: "var(--region-padding)",
  page: "var(--page-margin)",
};
for (const [lv, v] of Object.entries(LEVEL_PAD)) {
  add(`p-${lv}`, `padding: ${v}`);
  add(`px-${lv}`, `padding-inline: ${v}`);
  add(`py-${lv}`, `padding-block: ${v}`);
  add(`pt-${lv}`, `padding-top: ${v}`);
  add(`pb-${lv}`, `padding-bottom: ${v}`);
}
add("gap-field", "gap: var(--field-gap)");
add("gap-row", "gap: var(--row-gap)");
add("gap-group", "gap: var(--group-gap)");
add("gap-section", "gap: var(--section-gap)");
add("gap-page", "gap: var(--page-margin)");
add("mt-section", "margin-top: var(--section-gap)");
add("mb-section", "margin-bottom: var(--section-gap)");

// Page grid and app shell (after Affine UI).
add("gap-grid", "gap: var(--grid-gutter)");
add("gap-x-grid", "column-gap: var(--grid-gutter)");
add("p-grid-inset", "padding: var(--grid-inset)");
add("px-grid", "padding-inline: var(--grid-margin-regular)");
add("px-grid-compact", "padding-inline: var(--grid-margin-compact)");
add("w-sidebar", "width: var(--shell-sidebar-width)");
add("w-rail", "width: var(--shell-rail-width)");
add("h-header", "height: var(--shell-header-height)");
add("min-h-header", "min-height: var(--shell-header-height)");
add("top-header", "top: var(--shell-header-height)");
add("scroll-pt-header", "scroll-padding-block-start: var(--shell-header-height)");
add("h-below-header", "height: calc(100dvh - var(--shell-header-height))");
add("max-h-below-header", "max-height: calc(100dvh - var(--shell-header-height))");
add("max-w-measure", "max-width: var(--shell-measure)");

// Tiers (after Affine's space tiers): each is a scope with its own font size and spacing multiplier.
add("tier-product", "--tier: 1; --tier-text: 0px");
add("tier-content", "--tier: var(--tier-content); --tier-text: var(--tier-content-text); font-size: calc(1em + var(--tier-content-text))");
add("tier-brand", "--tier: var(--tier-brand); --tier-text: var(--tier-brand-text); font-size: calc(1em + var(--tier-brand-text))");
add("gap-gutter-half", "gap: calc(var(--gutter) / 2)");
add("icon", "display: inline-flex; align-items: center; justify-content: center; flex: none; width: var(--icon-box); height: var(--icon-box); font-size: var(--icon-md); line-height: 1");
add("caret", "--_caret: calc(var(--icon-md) * 0.4); --_caret-stroke: max(1.5px, calc(var(--icon-md) * 0.08))");
add("icon-sm", "font-size: var(--icon-sm)");
add("icon-md", "font-size: var(--icon-md)");
add("icon-lg", "font-size: var(--icon-lg)");
add("mark-sm", "--_mark: var(--mark-sm)");
add("mark-md", "--_mark: var(--mark-md)");
add("mark-lg", "--_mark: var(--mark-lg)");
for (const s of ["none", "text", "all", "auto"]) add(`select-${s}`, `user-select: ${s}`);
for (const a of ["baseline", "top", "middle", "bottom", "text-top", "text-bottom"]) add(`align-${a}`, `vertical-align: ${a}`);
add("visible", "visibility: visible");
add("invisible", "visibility: hidden");
for (const w of ["normal", "nowrap", "pre", "pre-wrap", "pre-line"]) add(`whitespace-${w}`, `white-space: ${w}`);
add("break-normal", "overflow-wrap: normal; word-break: normal");
add("break-words", "overflow-wrap: break-word");
add("break-all", "word-break: break-all");
add("truncate", "overflow: hidden; text-overflow: ellipsis; white-space: nowrap");
add("aspect-square", "aspect-ratio: 1 / 1");
add("aspect-video", "aspect-ratio: 16 / 9");
add("aspect-auto", "aspect-ratio: auto");
add("backdrop-blur-xs", "backdrop-filter: blur(4px)");
add("backdrop-blur-sm", "backdrop-filter: blur(8px)");
add("backdrop-blur", "backdrop-filter: blur(8px)");
add("backdrop-blur-md", "backdrop-filter: blur(12px)");
add("backdrop-blur-lg", "backdrop-filter: blur(16px)");
add("backdrop-blur-none", "backdrop-filter: none");
add("sr-only", "position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0");
add("not-sr-only", "position: static; width: auto; height: auto; margin: 0; overflow: visible; clip: auto; white-space: normal");
add("appearance-none", "appearance: none");
add("debug", "outline: 1px dashed red");
add("revert", "all: revert");

// ---- Variants (Prewind's rules) ----
const esc = (c) => c.replace(/[:./]/g, (ch) => `\\${ch}`).replace(/^(\d)/, (d) => `\\3${d} `);
const rule = (sel, decl) => `  .${esc(sel)} { ${decl}; }`;
const ROLE_COLORS = colorProps.filter((p) => !/^--shadow/.test(p) && !/-(surface|indicator|track)$/.test(p)).map((p) => p.slice(2));
// Raw steps of the interactive palettes take hover and state variants too, so an example can be written in primitives only.
const STEP_STATES = /^(fg|bg|border)-(neutral|accent-[1-4]|danger)-(\d+|contrast)$/;
const HOVER = [...D.keys()].filter((c) => ROLE_CLASSES.has(c) || STEP_STATES.test(c) || /^(fg|bg)-(inherit|current|transparent)$/.test(c) || /^opacity-|^cursor-/.test(c));
const LAYOUT = [...D.keys()].filter((c) => /^(block|inline-block|inline|flex|inline-flex|grid|inline-grid|contents|hidden|flex-(row|col)(-reverse)?|flex-wrap|flex-nowrap|justify-|items-|self-|text-(left|center|right|justify|start|end)$|col-span-|w-(\d\/\d|full|auto|fit|sidebar|rail)$|basis-|gap-|p[xytb]?-|static$|relative$|absolute$|fixed$|sticky$|top-|overflow-|h-(full|auto|dvh|screen|below-header)$)/.test(c));
const geometryCss = read("theme/theme.geometry.css");
const BREAKPOINTS = [...geometryCss.matchAll(/--breakpoint-([\w]+):\s*(\d+)px/g)].map((m) => [m[1], Number(m[2])]);

const reset = `@layer reset {
  :where(*, *::before, *::after) { box-sizing: border-box; border-color: var(--border); }
  :where(*) { margin: 0; }

  :where(html) {
    color-scheme: light dark;
    interpolate-size: allow-keywords;
    -webkit-text-size-adjust: none;
    text-size-adjust: none;
    hanging-punctuation: first last;
    tab-size: 4;
    scrollbar-gutter: stable;
    accent-color: var(--solid-accent-1);
    caret-color: var(--fg-accent-1-weak);
  }
  @media (prefers-reduced-motion: no-preference) {
    :where(html) { scroll-behavior: smooth; }
  }

  :where(body) {
    min-block-size: 100dvh;
    background: var(--bg);
    color: var(--fg);
    font-family: var(--font-body);
    font-size: var(--text-base);
    line-height: var(--text-base--line-height);
    font-synthesis: none;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  :where(h1, h2, h3, h4, h5, h6) { text-wrap: balance; overflow-wrap: break-word; }
  :where(h1) { font-size: var(--heading-xl); line-height: var(--heading-xl--line-height); font-weight: var(--heading-xl--font-weight); font-family: var(--heading-xl--font-family); letter-spacing: var(--heading-xl--letter-spacing); }
  :where(h2) { font-size: var(--heading-lg); line-height: var(--heading-lg--line-height); font-weight: var(--heading-lg--font-weight); font-family: var(--heading-lg--font-family); letter-spacing: var(--heading-lg--letter-spacing); }
  :where(h3) { font-size: var(--heading-md); line-height: var(--heading-md--line-height); font-weight: var(--heading-md--font-weight); font-family: var(--heading-md--font-family); letter-spacing: var(--heading-md--letter-spacing); }
  :where(h4) { font-size: var(--heading-sm); line-height: var(--heading-sm--line-height); font-weight: var(--heading-sm--font-weight); font-family: var(--heading-sm--font-family); }
  :where(h5) { font-size: var(--title); line-height: var(--title--line-height); font-weight: var(--title--font-weight); font-family: var(--title--font-family); }
  :where(h6) { font-size: var(--title-sm); line-height: var(--title-sm--line-height); font-weight: var(--title-sm--font-weight); font-family: var(--title-sm--font-family); }
  :where(p, li, figcaption, blockquote, dd) { text-wrap: pretty; overflow-wrap: break-word; }

  :where(img, picture, video, canvas, svg, iframe) { display: block; max-inline-size: 100%; }
  :where(img, video) { block-size: auto; }
  :where(img) { font-style: italic; background-repeat: no-repeat; background-size: cover; shape-margin: 1rem; }
  :where(svg:not([fill])) { fill: currentColor; }

  :where(input, button, textarea, select) { font: inherit; color: inherit; letter-spacing: inherit; word-spacing: inherit; }

  :where(input[type="checkbox"], input[type="radio"]) {
    --_mark: var(--mark-md);
    appearance: none;
    display: inline-grid;
    place-content: center;
    flex: none;
    box-sizing: border-box;
    inline-size: var(--_mark);
    block-size: var(--_mark);
    margin: 0;
    vertical-align: middle;
    border: var(--border-width) solid var(--border);
    background: var(--bg);
    cursor: pointer;
    transition: background-color var(--motion-duration) var(--motion-easing), border-color var(--motion-duration) var(--motion-easing);
  }
  :where(input[type="checkbox"]) { border-radius: calc(var(--mark-corner) * var(--_mark)); }
  :where(input[type="radio"]) { border-radius: 50%; }
  :where(input[type="checkbox"], input[type="radio"]):hover { border-color: var(--border-strong); }
  :where(input[type="checkbox"], input[type="radio"])::before {
    content: "";
    background: var(--on-solid-accent-1);
    transform: scale(0);
    transition: transform var(--duration-snappy) var(--ease-snappy);
  }
  :where(input[type="checkbox"])::before {
    inline-size: calc(var(--_mark) * 0.6);
    block-size: calc(var(--_mark) * 0.6);
    clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%);
  }
  :where(input[type="checkbox"]:indeterminate)::before { clip-path: inset(40% 10%); transform: scale(1); }
  :where(input[type="radio"])::before { inline-size: calc(var(--_mark) * 0.4); block-size: calc(var(--_mark) * 0.4); border-radius: 50%; }
  :where(input[type="checkbox"], input[type="radio"]):is(:checked, :indeterminate) { background: var(--solid-accent-1); border-color: var(--solid-accent-1); }
  :where(input[type="checkbox"], input[type="radio"]):checked::before { transform: scale(1); }

  :where(input[type="checkbox"][role="switch"]) {
    inline-size: calc(2 * var(--_mark) - 4 * var(--border-width));
    border-radius: 9999px;
    place-content: center start;
    background: var(--component-strong);
  }
  :where(input[type="checkbox"][role="switch"])::before {
    inline-size: calc(var(--_mark) - 4 * var(--border-width));
    block-size: calc(var(--_mark) - 4 * var(--border-width));
    margin-inline-start: var(--border-width);
    border-radius: 50%;
    clip-path: none;
    background: var(--bg);
    box-shadow: var(--shadow-xs);
    transform: none;
  }
  :where(input[type="checkbox"][role="switch"]):checked::before {
    transform: translateX(calc(var(--_mark) - 4 * var(--border-width)));
    background: var(--on-solid-accent-1);
  }
  :where(input[type="checkbox"], input[type="radio"]):disabled { opacity: 0.5; cursor: not-allowed; }

  :where(input[type="range"]) {
    --_mark: var(--mark-md);
    --_track: max(calc((var(--_mark) - var(--range-track-cut)) / var(--range-track-parts)), var(--border-width));
    --_thumb: var(--_mark);
    appearance: none;
    block-size: var(--_mark);
    margin: 0;
    background: transparent;
    cursor: pointer;
  }
  :where(input[type="range"])::-webkit-slider-runnable-track { block-size: var(--_track); border-radius: 9999px; background: var(--component-strong); }
  :where(input[type="range"])::-moz-range-track { block-size: var(--_track); border-radius: 9999px; background: var(--component-strong); }
  :where(input[type="range"])::-moz-range-progress { block-size: var(--_track); border-radius: 9999px; background: var(--solid-accent-1); }
  :where(input[type="range"])::-webkit-slider-thumb {
    appearance: none;
    inline-size: var(--_thumb);
    block-size: var(--_thumb);
    margin-block-start: calc((var(--_track) - var(--_thumb)) / 2);
    border: var(--border-width) solid var(--border-strong);
    border-radius: 50%;
    background: var(--bg);
    box-shadow: var(--shadow-xs);
  }
  :where(input[type="range"])::-moz-range-thumb {
    box-sizing: border-box;
    inline-size: var(--_thumb);
    block-size: var(--_thumb);
    border: var(--border-width) solid var(--border-strong);
    border-radius: 50%;
    background: var(--bg);
    box-shadow: var(--shadow-xs);
  }
  :where(textarea) { field-sizing: content; resize: vertical; }
  :where(textarea:not([rows])) { min-block-size: 6lh; }
  :where(input[type="file"]) { max-inline-size: 100%; color: var(--fg-weak); }
  :where(input[type="file"])::file-selector-button { font: inherit; font-weight: var(--title-sm--font-weight); color: var(--fg); block-size: var(--control-height); padding-inline: var(--control-padding); margin-inline-end: var(--gutter); border: var(--border-width) solid var(--border); border-radius: var(--radius-control); background: var(--component-weak); cursor: pointer; transition: background-color var(--motion-duration) var(--motion-easing); }
  :where(input[type="file"])::file-selector-button:hover { background: var(--component); }
  :where(progress, meter) { appearance: none; display: inline-block; inline-size: 100%; block-size: calc(var(--space-3xs) * 2); border: 0; border-radius: 9999px; background: var(--component-strong); overflow: hidden; vertical-align: middle; }
  :where(progress)::-webkit-progress-bar { background: var(--component-strong); border-radius: 9999px; }
  :where(progress)::-webkit-progress-value { background: var(--solid-accent-1); border-radius: 9999px; transition: inline-size var(--motion-duration) var(--motion-easing); }
  :where(progress)::-moz-progress-bar { background: var(--solid-accent-1); border-radius: 9999px; }
  :where(meter)::-webkit-meter-bar { block-size: 100%; border: 0; border-radius: 9999px; background: var(--component-strong); }
  :where(meter)::-webkit-meter-optimum-value { background: var(--solid-success); border-radius: 9999px; }
  :where(meter)::-webkit-meter-suboptimum-value { background: var(--solid-warning); border-radius: 9999px; }
  :where(meter)::-webkit-meter-even-less-good-value { background: var(--solid-danger); border-radius: 9999px; }
  :where(meter:-moz-meter-optimum)::-moz-meter-bar { background: var(--solid-success); border-radius: 9999px; }
  :where(meter:-moz-meter-sub-optimum)::-moz-meter-bar { background: var(--solid-warning); border-radius: 9999px; }
  :where(meter:-moz-meter-sub-sub-optimum)::-moz-meter-bar { background: var(--solid-danger); border-radius: 9999px; }
  :where(button, [role="button"], label[for], select, summary) { cursor: pointer; }
  :where(:disabled) { cursor: not-allowed; }

  :where(a:not([class])) { color: var(--fg-accent-1-weak); text-decoration-thickness: from-font; text-underline-offset: 0.15em; text-decoration-skip-ink: auto; }
  :where(a:not([class]):hover) { color: var(--fg-accent-1); }

  :where(:focus-visible) { outline: 2px solid var(--border-accent-1-strong); outline-offset: 2px; }
  :where(input:not([type="checkbox"], [type="radio"], [type="range"], [type="color"], [type="file"], [type="button"], [type="submit"], [type="reset"], [type="image"]), textarea, select):focus-visible { outline: none; border-color: var(--border-accent-1-strong); }
  :where(:target) { scroll-margin-block: 5ex; }
  :where([hidden]:not([hidden="until-found"])) { display: none !important; }

  :where(ul, ol)[role="list"] { list-style: none; padding: 0; }
  :where(table) { border-collapse: collapse; }
  :where(td, th) { font-variant-numeric: tabular-nums; }
  :where(code, kbd, samp, pre) { font-family: var(--font-mono); font-size: var(--code); }
  :where(pre) { white-space: pre-wrap; }
  :where(:not(pre) > code) { white-space: nowrap; }

  :where(dialog, [popover]) { color: inherit; font: inherit; }
  dialog::backdrop { background: var(--scrim); }
  ::selection { background: var(--accent-1-a5); color: var(--fg); }

  @media (forced-colors: active) {
    :where(button, [role="button"], [role="tab"], summary, [popover], dialog) { outline: 1px solid ButtonText; outline-offset: -1px; }
    :where(input:not([type="checkbox"], [type="radio"], [type="range"], [type="color"], [type="file"], [type="button"], [type="submit"], [type="reset"], [type="image"]), textarea, select):focus-visible { outline: 2px solid Highlight; outline-offset: 0; }
    :where([aria-selected="true"], [aria-pressed="true"], [aria-current]:not([aria-current="false"])) { outline: 2px solid Highlight; outline-offset: -2px; }
    :where(input[type="checkbox"], input[type="radio"]) { forced-color-adjust: none; border-color: CanvasText; background: Canvas; }
    :where(input[type="checkbox"], input[type="radio"]):is(:checked, :indeterminate) { border-color: Highlight; background: Highlight; }
    :where(input[type="checkbox"], input[type="radio"])::before { background: HighlightText; }
    :where(input[type="checkbox"][role="switch"])::before { background: CanvasText; }
    :where(input[type="checkbox"][role="switch"]):checked::before { background: HighlightText; }
    :where(input[type="range"]) { forced-color-adjust: none; }
    :where(progress, meter) { forced-color-adjust: none; background: Canvas; outline: 1px solid CanvasText; }
    :where(progress)::-webkit-progress-value { background: Highlight; }
    :where(progress)::-moz-progress-bar { background: Highlight; }
    :where(meter)::-webkit-meter-optimum-value, :where(meter)::-webkit-meter-suboptimum-value, :where(meter)::-webkit-meter-even-less-good-value { background: Highlight; }
    :where(meter)::-moz-meter-bar { background: Highlight; }
    :where(input[type="file"])::file-selector-button { border-color: ButtonText; }
    :where(input[type="range"])::-webkit-slider-runnable-track { background: CanvasText; }
    :where(input[type="range"])::-moz-range-track { background: CanvasText; }
    :where(input[type="range"])::-webkit-slider-thumb { background: Canvas; border-color: CanvasText; }
    :where(input[type="range"])::-moz-range-thumb { background: Canvas; border-color: CanvasText; }
  }

  @media (prefers-reduced-motion: reduce) {
    :where(*, *::before, *::after) {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
}
`;

const out = [];
out.push("@layer reset, styles, nowind;\n");
out.push(reset);
out.push("@layer nowind {");
for (const [c, d] of D) out.push(rule(c, d));
out.push("  .icon > svg { width: 1em; height: 1em; fill: currentColor; }");
out.push("  .list-none::-webkit-details-marker { display: none; }");
out.push("  @keyframes nw-spin { to { rotate: 360deg; } }");
out.push("  @keyframes nw-pulse { 50% { opacity: 0.5; } }");
out.push("  .select-base::picker(select) { appearance: base-select; margin-block: var(--space-3xs); padding: var(--space-3xs); border: var(--border-width) solid var(--border-weak); border-radius: var(--radius-surface); background: var(--bg); box-shadow: var(--shadow-lg); }");
out.push("  .select-base option { padding: var(--margin) var(--text-edge); border-radius: var(--radius-nested); }");
out.push("  .select-base option:hover, .select-base option:focus-visible { background: var(--component-weak); outline: none; }");
out.push("  .caret::before, .select-base::picker-icon { content: \"\"; flex: none; inline-size: var(--_caret); block-size: var(--_caret); border-inline-end: var(--_caret-stroke) solid currentColor; border-block-end: var(--_caret-stroke) solid currentColor; rotate: 45deg; translate: 0 -25%; transition: rotate var(--motion-duration) var(--motion-easing), translate var(--motion-duration) var(--motion-easing); }");
out.push("  .select-base { --_caret: calc(var(--icon-md) * 0.4); --_caret-stroke: max(1.5px, calc(var(--icon-md) * 0.08)); }");
out.push("  .select-base::picker-icon { color: var(--fg-weak); margin-inline: calc((var(--icon-box) - var(--_caret)) / 2); }");
out.push("  .select-base.px-control { padding-inline-end: var(--control-icon-padding); }");
out.push("  :is([open] > summary, [aria-expanded=\"true\"]) .caret::before, .select-base:open::picker-icon { rotate: 225deg; translate: 0 25%; }");
out.push("  :root[data-lens=\"on\"] .lens { -webkit-backdrop-filter: var(--_lens-filter, url(#nowind-lens)) saturate(1.8) brightness(1.05); backdrop-filter: var(--_lens-filter, url(#nowind-lens)) saturate(1.8) brightness(1.05); }");
out.push("  .select-base option:checked { background: var(--component-accent-1-weak); color: var(--fg-accent-1-weak); }");
out.push("  .h-nested > .icon { width: calc(var(--nested-height) - 2 * var(--border-width)); height: calc(var(--nested-height) - 2 * var(--border-width)); }");
for (const [cls, pad] of [["px-control", "--control-icon-padding"], ["px-nested", "--nested-icon-padding"]]) {
  out.push(`  .${cls}:where(:has(> :is(.icon, .h-nested, .size-nested):first-child)) { padding-inline-start: var(${pad}); }`);
  out.push(`  .${cls}:where(:has(> :is(.icon, .h-nested, .size-nested):last-child)) { padding-inline-end: var(${pad}); }`);
}
// ---- Materials (after massimo-v4): a region's material paints the reliefs inside it. The nearest material wins:
// each block is an @scope that stops at a nested material region. Flat is the default and paints nothing but casts.
const MATERIALS = ["flat", "physical", "frosted", "glass", "outline"];
const RELIEFS = ["raised", "raised-solid", "recessed", "field", "etched", "ground", "overlay"];
const shading = (top, bottom) => `linear-gradient(var(--paint-${top}), transparent, transparent, var(--paint-${bottom}))`;
const BEVEL = "inset 0 1px 0 var(--paint-bevel-top), inset 0 -1px 0 var(--paint-bevel-bottom), 0 0 0 0.5px var(--paint-bevel-ring)";
const BEVEL_SOLID = "inset 0 1px 0 var(--paint-bevel-top-solid), inset 0 -1px 0 var(--paint-bevel-bottom)";
const RECESS = (lv) => `var(--inset-shadow-${lv}), inset 0 0 0 0.5px var(--paint-recess-ring), 0 1px 0 var(--paint-recess-lip)`;
const rim = (k) => `inset 0 1px 0 var(--paint-rim-${k}-top), inset 0 -1px 0 var(--paint-rim-${k}-bottom), inset 0 0 0 0.5px var(--paint-rim-${k}-ring), inset 0 0 var(--q) 0 var(--paint-rim-${k}-glow), 0 0 0 0.5px var(--paint-rim-${k}-outer)`;
const LIT = {
  "raised": `background-image: ${shading("face-top", "face-bottom")}; box-shadow: ${BEVEL}, var(--shadow-sm)`,
  "raised:active": `background-image: none; box-shadow: ${RECESS("xs")}`,
  "raised-solid": `background-image: ${shading("face-top-solid", "face-bottom-solid")}; box-shadow: ${BEVEL_SOLID}, var(--shadow-sm)`,
  "raised-solid:active": `background-image: none; box-shadow: ${RECESS("xs")}`,
  "recessed": `box-shadow: ${RECESS("sm")}`,
  "field": `box-shadow: ${RECESS("sm")}`,
  "etched": "box-shadow: inset 0 1px 0 var(--paint-etch-top), inset 0 -1px 0 var(--paint-etch-ledge)",
  "ground": "box-shadow: inset 0 1px 0 var(--paint-bevel-top), var(--shadow-md)",
  "overlay": "box-shadow: var(--shadow-lg)",
};
// Clear glass after Apple's Liquid Glass: no gloss band, and the light catches the rim as two thin crescents on opposite
// corners (top left bright, bottom right softer) over a faint inner glow, instead of a lit top edge.
const rimLiquid = (k) => `inset 1.5px 1.5px 0 -0.5px var(--paint-rim-${k}-top), inset -1.5px -1.5px 0 -0.5px var(--paint-rim-${k}-bottom), inset 0 0 0 0.5px var(--paint-rim-${k}-ring), inset 0 0 calc(var(--q) * 2) 0 var(--paint-rim-${k}-glow), 0 0 0 0.5px var(--paint-rim-${k}-outer)`;
const glassPart = (k, face, filter, sheen, cast) =>
  `background-color: var(--glass-face-${face}); border-color: transparent; -webkit-backdrop-filter: ${filter}; backdrop-filter: ${filter}; background-image: ${sheen ? `linear-gradient(var(--paint-specular-${face}), transparent ${sheen})` : "none"}; box-shadow: ${sheen ? rim(k) : rimLiquid(k)}, var(--shadow-${cast})`;
const GLASS = (k, face, filter, sheen) => ({
  ...LIT,
  "raised": glassPart(k, face, filter, sheen, "sm"),
  "ground": glassPart(k, face, filter, sheen, "md"),
  "overlay": glassPart(k, face, filter, sheen, "lg"),
});
const LINE = "background-color: transparent; background-image: none; border-color: transparent; box-shadow: inset 0 0 0 1px var(--fg-weak)";
const PAINT = {
  flat: {},
  physical: LIT,
  frosted: GLASS("frosted", "frosted", "blur(8px) saturate(1.6)", "45%"),
  glass: GLASS("clear", "clear", "blur(0.5px) saturate(1.8) brightness(1.05)", null),
  outline: { "raised": LINE, "recessed": LINE, "field": LINE, "etched": LINE, "ground": LINE, "overlay": "background-color: var(--bg); background-image: none; border-color: transparent; box-shadow: inset 0 0 0 1px var(--fg-weak)" },
};
const materialCss = [];
for (const r of RELIEFS) add(`relief-${r}`, r === "overlay" ? "box-shadow: var(--shadow-lg)" : "--_relief: 1");
for (const m of MATERIALS) add(`material-${m}`, `--_material: ${m}`);
for (const m of MATERIALS) {
  const entries = Object.entries(PAINT[m]);
  if (!entries.length) continue;
  const others = MATERIALS.filter((x) => x !== m).map((x) => `.material-${x}`).join(", ");
  materialCss.push(`  @scope (.material-${m}) to (${others}) {`);
  for (const [part, decl] of entries) {
    const [name, state] = part.split(":");
    const st = state ? `:${state}` : "";
    materialCss.push(`    .relief-${name}${st}, :scope.relief-${name}${st} { ${decl}; }`);
  }
  materialCss.push("  }");
}
out.push(...materialCss);

out.push("  @media (hover: hover) {");
for (const c of HOVER) out.push(`    .${esc(`hover:${c}`)}:hover { ${D.get(c)}; }`);
out.push("  }");

// ---- State variants (Tailwind v4 names). Like hover, they change color only, plus opacity and cursor for disabled.
// Interaction states cover the neutral and accent roles; invalid covers the neutral and danger roles. Each rule is a
// class plus one state (specificity 0,2,0), so it beats the base class it pairs with.
const roleOf = (c) => c.replace(/^(text|bg|border)-/, "");
const inPalettes = (pals) => (c) => {
  const r = roleOf(c);
  const pal = r.match(/(?:^|-)(accent-\d|danger|warning|success|info)(-|$)/);
  return pal ? pals.includes(pal[1]) : pals.includes("neutral");
};
const ROLE_STATE = HOVER.filter((c) => !/^opacity-|^cursor-/.test(c));
const interactive = ROLE_STATE.filter(inPalettes(["neutral", "accent-1", "accent-2", "accent-3", "accent-4"]));
const STATES = [
  ["active", ":active", interactive],
  ["focus-visible", ":focus-visible", ROLE_STATE.filter((c) => /^border-/.test(c)).filter(inPalettes(["neutral", "accent-1", "accent-2", "accent-3", "accent-4"]))],
  ["focus-within", ":focus-within", ROLE_STATE.filter((c) => /^border-/.test(c)).filter(inPalettes(["neutral", "accent-1", "accent-2", "accent-3", "accent-4"]))],
  ["selected", '[aria-selected="true"]', interactive],
  ["aria-current", ':is([aria-current]:not([aria-current="false"]))', interactive],
  ["aria-pressed", '[aria-pressed="true"]', interactive],
  ["aria-expanded", '[aria-expanded="true"]', interactive],
  ["open", ":is([open], :popover-open)", interactive],
  ["aria-invalid", ':is([aria-invalid="true"], :user-invalid)', ROLE_STATE.filter((c) => /^(text|border|fg)(-|$)/.test(c)).filter(inPalettes(["neutral", "danger"]))],
  ["has-invalid", ':has(:is([aria-invalid="true"], :user-invalid))', ROLE_STATE.filter((c) => /^(text|border|fg)(-|$)/.test(c)).filter(inPalettes(["neutral", "danger"]))],
  ["disabled", ':is(:disabled, [aria-disabled="true"])', [...ROLE_STATE.filter(inPalettes(["neutral"])), ...[...D.keys()].filter((c) => /^opacity-|^cursor-/.test(c))]],
];
for (const [prefix, sel, list] of STATES) {
  for (const c of list) out.push(`  .${esc(`${prefix}:${c}`)}${sel} { ${D.get(c)}; }`);
}

// Group variants (Tailwind v4 names): a child reacts to its .group ancestor being hovered, focused or open, for
// tooltips and reveal-on-hover parts. Opacity, visibility and the role colors of text only.
add("group", "--_group: 1");
const GROUP_CLASSES = [...D.keys()].filter((c) => /^opacity-|^(visible|invisible)$/.test(c) || (/^fg(-|$)/.test(c) && ROLE_COLORS.includes(c)));
const GROUP_VARIANTS = [
  ["group-hover", ".group:hover ", true],
  ["group-focus-within", ".group:focus-within ", false],
  ["group-open", ".group:is([open], :popover-open, [aria-expanded=\"true\"]) ", false],
];
for (const [prefix, pre, hoverOnly] of GROUP_VARIANTS) {
  if (hoverOnly) out.push("  @media (hover: hover) {");
  for (const c of GROUP_CLASSES) out.push(`  ${hoverOnly ? "  " : ""}${pre}.${esc(`${prefix}:${c}`)} { ${D.get(c)}; }`);
  if (hoverOnly) out.push("  }");
}
for (const [bp, w] of BREAKPOINTS) {
  out.push(`  @media (min-width: ${w}px) {`);
  for (const c of LAYOUT) out.push(`  ${rule(`${bp}:${c}`, D.get(c))}`);
  out.push("  }");
}
out.push("}");
const css = out.join("\n") + "\n";
writeFileSync(join(root, "nowind.css"), css);

const manifest = {
  file: "nowind.css",
  generated: "scripts/utilities.mjs",
  description: "Prewind-style utility classes over the Nowind theme, with Tailwind v4 names where they overlap. One plain stylesheet, no build step for consumers: every class already exists. Regenerate after changing theme tokens, then rebuild the bundle.",
  setup: {
    order: "@layer reset, styles, nowind; (declared at the top of nowind.css)",
    link: ["dist/nowind.min.css"],
    linkWhileDeveloping: ["theme.css", "nowind.css"],
    bundle: "node scripts/bundle.mjs writes dist/nowind.bundle.css and dist/nowind.min.css: theme.css with every @import inlined, then this file. Run it after this script.",
    rule: "Put your own global CSS in @layer styles. Unlayered CSS beats every utility.",
  },
  counts: { classes: D.size, hover: HOVER.length, responsive: LAYOUT.length * BREAKPOINTS.length, bytes: Buffer.byteLength(css) },
  naming: "property-value, as Prewind and Tailwind: p-md, gap-lg, bg-solid-accent-1. Colour classes take the token name without --; text-color roles are the token name alone (fg-weak, fg-accent-1).",
  variants: {
    hover: "Inside @media (hover: hover), as Tailwind v4, so taps on touch screens don't stick. hover:border-* for the border roles, hover:fg-* and hover:bg-* for the colour role tokens only (bg, component, border, solid, on-solid, fg and their palette versions), hover:opacity-*, hover:cursor-*. Raw steps of neutral, accent-1 to accent-4 and danger take hover too (hover:bg-neutral-4), so examples can use primitives only; alpha steps and the status palettes' steps have no hover class.",
    breakpoints: Object.fromEntries(BREAKPOINTS.map(([b, w]) => [b, `${w}px`])),
    responsive: "sm:, md:, lg:, xl:, 2xl: (read from the --breakpoint-* tokens) apply to layout: display, grid columns and spans, flex direction, wrap, basis, justify, align, text alignment, widths, heights, position, top, overflow, padding and gaps. Margins, colours and type have no breakpoint variants.",
    groups: "group on a parent; group-hover:, group-focus-within: and group-open: on a child, for opacity, visibility and text roles (tooltips, reveal-on-hover).",
    states: "active:, focus-visible:, focus-within: (a field wrapper whose input has focus), selected: (aria-selected=\"true\"), aria-current:, aria-pressed:, aria-expanded:, open: (details, popovers), aria-invalid: (also :user-invalid), has-invalid: (a wrapper holding an invalid input) and disabled: (also aria-disabled). Colors only (plus opacity and cursor for disabled), for the neutral and accent roles; aria-invalid for neutral and danger.",
    none: "No group- or dark: variants. Dark mode comes from the theme's light-dark() tokens.",
  },
  categories: {
    spacing: `p-, px-, py-, pt-, pr-, pb-, pl-, m-*, -m-*, m*-auto, gap-, gap-x-, gap-y- with 0 and ${SPACE.join(", ")}; scroll-mt-* (where a linked element stops under sticky bars) with the same steps, no 0`,
    typeScale: `text-{${SIZES.join(", ")}} (sets size and line height)`,
    kicker: `text-{${KICKERS.join(", ")}} (size and the kicker style)`,
    typeRoles: `text-{${ROLES.filter((r) => !KICKERS.includes(r)).join(", ")}} (every role companion)`,
    colors: "A colour class is the property prefix plus the token name, minus the role group when it matches the prefix (fg-weak, bg-accent-1, border-weak; bg-component-accent-1 keeps its group). --border is border-default, because border is the width class; the reset draws every border in --border. Each property takes only its own roles: fg- with fg-* and on-solid-*; bg- with bg-*, component-*, solid-*, surface, indicator and track; border- with border-*. Raw palette steps (fg-accent-1-9, bg-accent-1-9, border-accent-1-9) work with all three; alpha steps (neutral-a4) with bg- only. No outline colour classes: the reset sets the focus ring.",
    weights: "font-normal, font-medium, font-semibold, font-bold",
    faces: "font-body (alias font-sans), font-heading, font-mono, font-control",
    leading: "leading-none, tight, snug, normal, relaxed",
    tracking: "tracking-tight, normal, wide, widest",
    radius: "rounded-none, rounded-xs (nested), rounded-sm and rounded (control), rounded-lg (surface), rounded-xl (dialog), rounded-full. Tailwind v4 names.",
    shadows: "shadow-xs, shadow-sm (and bare shadow), shadow-md, shadow-lg, shadow-xl, shadow-none; inset-shadow-xs, inset-shadow-sm, inset-shadow-none. Compound shadows after Massimo (theme.shadows.css); a cast and a recess on one element compose, as in Tailwind v4.",
    borders: "border, border-0, -2, -4, with sides t r b l x y; border-solid/dashed/dotted/none",
    layout: "container, display, grid-cols-1…12, col-span-1…12 and -full, flex, basis fractions, position, inset, z-",
    controls: "h-control, h-nested (an .icon inside it shrinks by the two borders so it fits), size-control, size-nested, min-w-control, min-w-nested, px-control and px-nested (padding steps in by one margin on a side whose first or last child is .icon; wrap the label in a <span>), gap-gutter, gap-gutter-half",
    levels: "p-surface, p-dialog (each minus the border), p-region, p-page, with px- and py- versions; gap-field, gap-row, gap-group, gap-section, gap-page; mt-section, mb-section. After Affine's container levels.",
    materials: "material-flat, -physical, -frosted, -glass, -outline set a region's material (nearest wins, by @scope); relief-raised, -raised-solid, -recessed, -field, -etched, -ground, -overlay say what a part is. After Massimo.",
    grid: "gap-grid, gap-x-grid (2M), p-grid-inset (M), px-grid (slot), px-grid-compact; shell: w-sidebar (16F + 16), w-rail, h-header, min-h-header, top-header (a sticky offset under the header), scroll-pt-header (on <html>, so in-page links land below a sticky header), h-below-header, max-h-below-header, max-w-measure (44F). After Affine.",
    tiers: "tier-product (1×), tier-content (font +2px, spacing 1.5×), tier-brand (font +4px, spacing 2×). Each is a scope: --F and everything derived recompute inside it.",
    animation: "animate-spin, animate-pulse, animate-none (cut by the reset under reduced motion).",
    anchor: "anchor-bottom, -top, -start, -end, -center: place a popover against its invoker with CSS anchor positioning, flipping at the screen edge.",
    select: "select-base: the customizable select (appearance: base-select), its picker and options in the theme. The value is centred in the field; the highlighted option shows by its background, not a focus ring.",
    motion: "transition, transition-colors, -opacity, -shadow, -transform, -none (state-change length and easing by default); duration-fade, -snappy, -smooth, -bouncy; ease-smooth, -snappy, -bouncy (Massimo springs as linear()), ease-standard, -out, -in.",
    marks: "The reset draws checkboxes, radios, switches (<input type=checkbox role=switch>) and sliders at Affine's mark size (between F and the slot), filled with accent-1 when checked; mark-sm and mark-lg pick another size.",
    icons: "icon (an S-square box, glyph --icon-md), icon-sm, icon-md, icon-lg. Glyphs: Phosphor web font (<i class=\"icon ph ph-floppy-disk\">; ph-bold at sm, ph-light at lg) or an inline <svg> inside .icon.",
    sizing: "w-, h-, min-/max- with 0, full, screen (100vw/100vh), fit; w-1/2, 1/3, 2/3, 1/4, 3/4 and fifths; h-dvh, h-svh, h-lvh and min-/max- versions; max-w-text (alias max-w-prose), max-w-form, max-w-container, h-control",
  },
  changesFromPrewind: [
    "container: width min(100%, --container-max), so it never overflows a narrow screen (Prewind's 360px minimum did).",
    "No bg-opacity-*: it relied on relative colour syntax with no fallback and was inherited by children. Use the alpha steps (bg-accent-1-a3, bg-neutral-a5) instead.",
    "No m-full / p-full: margin and padding percentages are of the width, not a full size.",
    "Margins and padding x/y use logical properties (margin-inline, padding-block).",
    "text-{size} also sets the matching line height, as Tailwind v4.",
    "The reset keeps link underlines and adds a 2026 baseline: :where() selectors (no specificity), interpolate-size, text-size-adjust, font-synthesis none, headings set from the type roles (h1 heading-xl … h6 title-sm), text-wrap balance/pretty, field-sizing content, accent and caret colours, :focus-visible ring, :target scroll margin, [hidden] enforced, role=list, tabular table figures, ::backdrop and ::selection from tokens, and reduced-motion handling, and a forced-colors (Windows High Contrast) block: controls and overlays keep an outline, selected, pressed and current items a Highlight outline, and checkboxes, radios, switches and sliders are redrawn in system colors. Focus: buttons, links and checkable controls get a 2px accent ring on :focus-visible; text fields (text-like inputs, textarea, select) get no ring and turn their border accent instead, with a Highlight outline in forced colours. Native controls without a base appearance are themed in the reset: the file input's button looks like a secondary button, progress is an accent bar on a component track, and meter turns success, warning or danger from its low, high and optimum attributes; each gets system colours in forced colours. field-sizing-content and field-sizing-fixed size a field to its content or not (textareas grow by default). Controls share one recipe in utilities, enforced by scripts/check.mjs: h-control (or size-control), px-control, a border width (border-transparent on solid fills, never border-0), rounded-control and a control type role. caret, on an icon box (icon caret), is the one disclosure chevron; select-base draws the same chevron as its picker icon, and both turn over when open. bg-dots paints a dot grid in currentColor (set the colour with fg-*), spaced by bg-dots-sm, -md or -lg. lens refracts the backdrop through an SVG displacement filter (id nowind-lens, a bend along the rim with an R/G/B fringe) when the page sets data-lens=\"on\" on the root; only Chromium applies an SVG filter in backdrop-filter, so the page sets it after checking the engine, and without it the material's own blur applies.",
    "No outline-{colour} classes, no text-/border- classes for alpha steps, and no class that pairs a role with another property (no bg-fg-*, text-bg-*, bg-border-*). Text-color roles are named by their token alone: fg, fg-weak, fg-accent-1-weak.",
    "Tailwind v4 names where v4 renamed v3 ones: rounded-xs/sm, shadow-xs/sm, backdrop-blur-xs/sm; h-screen is 100vh with h-dvh/svh/lvh separate; a 2xl breakpoint; aliases max-w-prose and font-sans.",
    "Added: grid display, text-start/end, justify-evenly, items-baseline, tabular-nums, text-balance/pretty, w-fit, h-control, kicker and type-role classes.",
  ],
};
writeFileSync(join(root, "nowind.manifest.json"), JSON.stringify(manifest, null, 2) + "\n");

// ---- classes.md: every base class and its declarations, for readers without a local server ----
const GROUPS = [
  ["Controls and icons", (c) => /^(icon|mark-|h-control|h-nested|size-control|size-nested|min-w-control|min-w-nested|px-control|px-nested|gap-gutter)/.test(c)],
  ["Levels and tiers", (c) => /^(p[xy]?-(surface|dialog|region|page)|gap-(field|row|group|section|page)|m[tb]-section|tier-)/.test(c)],
  ["Materials", (c) => /^(material|relief)-/.test(c)],
  ["Motion, anchors and select", (c) => /^(transition|duration-|ease-|animate-|anchor-|select-base)/.test(c)],
  ["Page grid and shell", (c) => /^(gap-(x-)?grid|p-grid-inset|px-grid|w-sidebar|w-rail|(min-)?h-header|top-header|(max-)?h-below-header|max-w-measure)/.test(c)],
  ["Type", (c, d) => /font-size/.test(d)],
  ["Text color", (c, d) => /^color:/.test(d)],
  ["Background color", (c, d) => /^background-color:/.test(d)],
  ["Border color", (c, d) => /^border-color:/.test(d)],
  ["Borders, radius, shadow", (c, d) => /border|outline|box-shadow/.test(d)],
  ["Spacing", (c, d) => /^(padding|margin|gap|column-gap|row-gap)/.test(d) && c !== "container"],
  ["Typography", (c, d) => /font-|line-height|letter-spacing|text-|white-space|word-break|overflow-wrap|list-style|vertical-align/.test(d)],
  ["Layout and misc", () => true],
];
const buckets = new Map(GROUPS.map(([g]) => [g, []]));
for (const [c, d] of D) buckets.get(GROUPS.find(([, f]) => f(c, d))[0]).push([c, d]);
const md = [
  "# Nowind classes",
  "",
  "Generated by `scripts/utilities.mjs` from the theme tokens; do not edit. Every base class in `nowind.css` with its declarations.",
  "",
  `Variants: \`hover:\` on the ${HOVER.length} role-colour, opacity and cursor classes (inside \`@media (hover: hover)\`); ` +
    `${BREAKPOINTS.map(([b, w]) => `\`${b}:\` ${w}px`).join(", ")} on the ${LAYOUT.length} layout classes (display, flex, alignment, text alignment).`,
  "",
  GROUPS.map(([g]) => `[${g}](#${g.toLowerCase().replace(/[^a-z0-9 ]/g, "").replace(/ /g, "-")})`).join(" · "),
];
for (const [g] of GROUPS) {
  const list = buckets.get(g);
  md.push("", `## ${g}`, "", `${list.length} classes.`, "", "| Class | Declarations |", "|---|---|");
  for (const [c, d] of list) md.push(`| \`.${c}\` | \`${d.replace(/\|/g, "\\|")}\` |`);
}
writeFileSync(join(root, "classes.md"), md.join("\n") + "\n");
console.log(`nowind.css and classes.md: ${D.size} classes, ${HOVER.length} hover, ${STATES.reduce((n, [, , l]) => n + l.length, 0)} state, ${LAYOUT.length * BREAKPOINTS.length} responsive, ${(Buffer.byteLength(css) / 1024).toFixed(1)} KiB`);
