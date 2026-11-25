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

// Layout
add("container", "width: min(100%, var(--container-max)); margin-inline: auto; padding-inline: var(--container-padding)");
for (const d of ["block", "inline-block", "inline", "flex", "inline-flex", "grid", "inline-grid", "contents"]) add(d, `display: ${d}`);
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
for (const p of ["top", "right", "bottom", "left"]) add(`${p}-0`, `${p}: 0`);
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
const forText = (c) => step(c) || /^(fg|on-solid)(-|$)/.test(c);
const forBg = (c) => step(c) || alphaStep(c) || /^(bg|component|solid)(-|$)/.test(c) || /-(surface|indicator|track)$/.test(c);
const forBorder = (c) => step(c) || /^border(-|$)/.test(c);
for (const c of COLORS) {
  if (forText(c)) add(`text-${c}`, `color: var(--${c})`);
  if (forBg(c)) add(`bg-${c}`, `background-color: var(--${c})`);
  if (forBorder(c)) add(`border-${c}`, `border-color: var(--${c})`);
}
add("text-inherit", "color: inherit");
add("text-current", "color: currentColor");
add("bg-transparent", "background-color: transparent");
add("border-transparent", "border-color: transparent");
for (let o = 0; o <= 100; o += 10) add(`opacity-${o}`, `opacity: ${o / 100}`);

// Backgrounds
add("bg-repeat", "background-repeat: repeat");
add("bg-repeat-x", "background-repeat: repeat-x");
add("bg-repeat-y", "background-repeat: repeat-y");
add("bg-no-repeat", "background-repeat: no-repeat");
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
add("gap-gutter-half", "gap: calc(var(--gutter) / 2)");
add("icon", "display: inline-flex; align-items: center; justify-content: center; flex: none; width: var(--icon-box); height: var(--icon-box); font-size: var(--icon-md); line-height: 1");
add("icon-sm", "font-size: var(--icon-sm)");
add("icon-md", "font-size: var(--icon-md)");
add("icon-lg", "font-size: var(--icon-lg)");
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
const colorClass = new RegExp(`^(text|bg)-(${ROLE_COLORS.map((c) => c.replace(/[-]/g, "\\-")).join("|")}|inherit|current|transparent)$`);
const HOVER = [...D.keys()].filter((c) => colorClass.test(c) || /^opacity-|^cursor-/.test(c));
const LAYOUT = [...D.keys()].filter((c) => /^(block|inline-block|inline|flex|inline-flex|grid|inline-grid|contents|hidden|flex-(row|col)(-reverse)?|flex-wrap|flex-nowrap|justify-|items-|self-|text-(left|center|right|justify|start|end)$)/.test(c));
const geometryCss = read("theme/theme.geometry.css");
const BREAKPOINTS = [...geometryCss.matchAll(/--breakpoint-([\w]+):\s*(\d+)px/g)].map((m) => [m[1], Number(m[2])]);

const reset = `@layer reset {
  :where(*, *::before, *::after) { box-sizing: border-box; }
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
  :where(textarea) { field-sizing: content; resize: vertical; }
  :where(textarea:not([rows])) { min-block-size: 6lh; }
  :where(button, [role="button"], label[for], select, summary) { cursor: pointer; }
  :where(:disabled) { cursor: not-allowed; }

  :where(a:not([class])) { color: var(--fg-accent-1-weak); text-decoration-thickness: from-font; text-underline-offset: 0.15em; text-decoration-skip-ink: auto; }
  :where(a:not([class]):hover) { color: var(--fg-accent-1); }

  :where(:focus-visible) { outline: 2px solid var(--border-accent-1-strong); outline-offset: 2px; }
  :where(:target) { scroll-margin-block: 5ex; }
  :where([hidden]:not([hidden="until-found"])) { display: none !important; }

  :where(ul, ol)[role="list"] { list-style: none; padding: 0; }
  :where(table) { border-collapse: collapse; }
  :where(td, th) { font-variant-numeric: tabular-nums; }
  :where(code, kbd, samp, pre) { font-family: var(--font-mono); font-size: var(--code); }
  :where(pre) { white-space: pre-wrap; }

  :where(dialog, [popover]) { color: inherit; font: inherit; }
  :where(::backdrop) { background: var(--neutral-a8); }
  :where(::selection) { background: var(--accent-1-a5); color: var(--fg); }

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
out.push("  .h-nested > .icon { width: calc(var(--nested-height) - 2 * var(--border-width)); height: calc(var(--nested-height) - 2 * var(--border-width)); }");
for (const [cls, pad] of [["px-control", "--control-icon-padding"], ["px-nested", "--nested-icon-padding"]]) {
  out.push(`  .${cls}:where(:has(> .icon:first-child)) { padding-inline-start: var(${pad}); }`);
  out.push(`  .${cls}:where(:has(> .icon:last-child)) { padding-inline-end: var(${pad}); }`);
}
out.push("  @media (hover: hover) {");
for (const c of HOVER) out.push(`    .${esc(`hover:${c}`)}:hover { ${D.get(c)}; }`);
out.push("  }");
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
  naming: "property-value, as Prewind and Tailwind: p-md, gap-lg, text-fg-weak, bg-solid-accent-1. Colour classes take the token name without --.",
  variants: {
    hover: "Inside @media (hover: hover), as Tailwind v4, so taps on touch screens don't stick. hover:text-* and hover:bg-* for the colour role tokens only (bg, component, border, solid, on-solid, fg and their palette versions), hover:opacity-*, hover:cursor-*. Raw palette steps and alpha steps have no hover class.",
    breakpoints: Object.fromEntries(BREAKPOINTS.map(([b, w]) => [b, `${w}px`])),
    responsive: "sm:, md:, lg:, xl:, 2xl: (read from the --breakpoint-* tokens) apply to display, flex direction, wrap, justify, align and text alignment only, as Prewind.",
    none: "No focus:, active:, group- or dark: variants. Dark mode comes from the theme's light-dark() tokens.",
  },
  categories: {
    spacing: `p-, px-, py-, pt-, pr-, pb-, pl-, m-*, -m-*, m*-auto, gap-, gap-x-, gap-y- with 0 and ${SPACE.join(", ")}`,
    typeScale: `text-{${SIZES.join(", ")}} (sets size and line height)`,
    kicker: `text-{${KICKERS.join(", ")}} (size and the kicker style)`,
    typeRoles: `text-{${ROLES.filter((r) => !KICKERS.includes(r)).join(", ")}} (every role companion)`,
    colors: "Each property takes only its own roles: text- with fg-* and on-solid-*; bg- with bg-*, component-*, solid-*, surface, indicator and track; border- with border-*. Raw palette steps (accent-1-9) work with all three; alpha steps (neutral-a4) with bg- only. No outline colour classes: the reset sets the focus ring.",
    weights: "font-normal, font-medium, font-semibold, font-bold",
    faces: "font-body (alias font-sans), font-heading, font-mono, font-control",
    leading: "leading-none, tight, snug, normal, relaxed",
    tracking: "tracking-tight, normal, wide, widest",
    radius: "rounded-none, rounded-xs (nested), rounded-sm and rounded (control), rounded-lg (surface), rounded-xl (dialog), rounded-full. Tailwind v4 names.",
    shadows: "shadow-xs, shadow-sm (and bare shadow), shadow-md, shadow-lg, shadow-xl, shadow-none; inset-shadow-xs, inset-shadow-sm, inset-shadow-none. Compound shadows after Massimo (theme.shadows.css); a cast and a recess on one element compose, as in Tailwind v4.",
    borders: "border, border-0, -2, -4, with sides t r b l x y; border-solid/dashed/dotted/none",
    layout: "container, display, flex, position, inset, z-",
    controls: "h-control, h-nested (an .icon inside it shrinks by the two borders so it fits), size-control, size-nested, min-w-control, min-w-nested, px-control and px-nested (padding steps in by one margin on a side whose first or last child is .icon; wrap the label in a <span>), gap-gutter, gap-gutter-half",
    icons: "icon (an S-square box, glyph --icon-md), icon-sm, icon-md, icon-lg. Glyphs: Phosphor web font (<i class=\"icon ph ph-floppy-disk\">; ph-bold at sm, ph-light at lg) or an inline <svg> inside .icon.",
    sizing: "w-, h-, min-/max- with 0, full, screen (100vw/100vh), fit; h-dvh, h-svh, h-lvh and min-/max- versions; max-w-text (alias max-w-prose), max-w-form, max-w-container, h-control",
  },
  changesFromPrewind: [
    "container: width min(100%, --container-max), so it never overflows a narrow screen (Prewind's 360px minimum did).",
    "No bg-opacity-*: it relied on relative colour syntax with no fallback and was inherited by children. Use the alpha steps (bg-accent-1-a3, bg-neutral-a5) instead.",
    "No m-full / p-full: margin and padding percentages are of the width, not a full size.",
    "Margins and padding x/y use logical properties (margin-inline, padding-block).",
    "text-{size} also sets the matching line height, as Tailwind v4.",
    "The reset keeps link underlines and adds a 2026 baseline: :where() selectors (no specificity), interpolate-size, text-size-adjust, font-synthesis none, headings set from the type roles (h1 heading-xl … h6 title-sm), text-wrap balance/pretty, field-sizing content, accent and caret colours, :focus-visible ring, :target scroll margin, [hidden] enforced, role=list, tabular table figures, ::backdrop and ::selection from tokens, and reduced-motion handling.",
    "No outline-{colour} classes, no text-/border- classes for alpha steps, and no class that pairs a role with another property (no bg-fg-*, text-bg-*, bg-border-*).",
    "Tailwind v4 names where v4 renamed v3 ones: rounded-xs/sm, shadow-xs/sm, backdrop-blur-xs/sm; h-screen is 100vh with h-dvh/svh/lvh separate; a 2xl breakpoint; aliases max-w-prose and font-sans.",
    "Added: grid display, text-start/end, justify-evenly, items-baseline, tabular-nums, text-balance/pretty, w-fit, h-control, kicker and type-role classes.",
  ],
};
writeFileSync(join(root, "nowind.manifest.json"), JSON.stringify(manifest, null, 2) + "\n");

// ---- classes.md: every base class and its declarations, for readers without a local server ----
const GROUPS = [
  ["Controls and icons", (c) => /^(icon|h-control|h-nested|size-control|size-nested|min-w-control|min-w-nested|px-control|px-nested|gap-gutter)/.test(c)],
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
console.log(`nowind.css and classes.md: ${D.size} classes, ${HOVER.length} hover, ${LAYOUT.length * BREAKPOINTS.length} responsive, ${(Buffer.byteLength(css) / 1024).toFixed(1)} KiB`);
