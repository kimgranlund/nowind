#!/usr/bin/env node
// Convenience classes: each is a recipe of Nowind utility classes, written out by copying every utility rule the recipe
// uses (pseudo-states, variants and media queries included) under the new class. A convenience class is therefore the
// same as its utility stack, by construction. They ship in their own file, dist/nowind.components.css, in the
// `components` layer, which the main bundle orders before `nowind`, so any utility on the element still wins.
// Writes dist/nowind.components.css, its minified copy and nowind.components.manifest.json.
// Usage: node scripts/components.mjs   (run after utilities.mjs; check.mjs confirms the output matches)
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { gzipSync } from "node:zlib";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const BTN = "inline-flex items-center justify-center h-control px-control gap-gutter rounded-sm border state font-medium text-base cursor-pointer";
const TONES = {
  primary: "border-transparent bg-accent-1-9 fg-accent-1-contrast",
  secondary: "border-transparent bg-neutral-a2 fg-neutral-12",
  soft: "border-transparent bg-accent-1-3 fg-accent-1-11",
  ghost: "border-transparent bg-transparent fg-neutral-12",
  danger: "border-transparent bg-danger-9 fg-danger-contrast",
};
const BADGE_TONES = { neutral: "neutral", accent: "accent-1", success: "success", warning: "warning", danger: "danger", info: "info" };

export const RECIPES = [
  { name: "btn", use: "A button: control height and padding, icon gap, control radius, state layer. Add a tone.", recipe: BTN },
  ...Object.entries(TONES).map(([t, r]) => ({ name: `btn-${t}`, use: `The ${t} tone for btn, btn-sm or icon-btn.`, recipe: r })),
  { name: "btn-sm", use: "A small button inside an inset container (a toolbar, field or segmented group), never beside full-size controls.", recipe: "inline-flex items-center justify-center h-nested px-nested gap-gutter-half rounded-inner border state font-medium text-base cursor-pointer" },
  { name: "icon-btn", use: "A square button holding one icon; give it an aria-label and a tone.", recipe: "inline-flex items-center justify-center size-control rounded-sm border state cursor-pointer" },
  { name: "field", use: "A field box around a bare input (and its icons, prefix or suffix): control height, border, hover and invalid borders.", recipe: "flex items-center gap-gutter h-control px-control rounded-sm border border-neutral-5 hover:border-neutral-7 focus-within:border-accent-1-8 has-invalid:border-danger-7 bg-neutral-1 text-base cursor-text transition" },
  { name: "badge", use: "A status pill: small height, pill radius, label size. Add a tone.", recipe: "inline-flex items-center h-nested px-nested rounded-full border text-sm font-medium" },
  ...Object.entries(BADGE_TONES).map(([t, p]) => ({ name: `badge-${t}`, use: `The ${t} tone for badge.`, recipe: `bg-${p}-3 border-${p}-6 fg-${p}-11` })),
  { name: "card", use: "A card: surface padding and radius, border and fill.", recipe: "p-md rounded-md border border-neutral-6 bg-neutral-1" },
  { name: "segmented", use: "A segmented control's group: control height, inset border, soft fill. Holds segment buttons with aria-pressed.", recipe: "inline-flex items-center h-control rounded-sm border-2 border-transparent bg-neutral-a2" },
  { name: "segment", use: "One segment in a segmented group: white when pressed (aria-pressed=true) in both modes.", recipe: "inline-flex items-center justify-center self-stretch px-nested gap-gutter-half rounded-inner border-0 bg-transparent hover:bg-neutral-4 pressed:bg-white fg-neutral-11 pressed:fg-black font-medium text-base cursor-pointer" },
];

// A small CSS reader: rules and at-rules with their children. Nowind's CSS has no comments and no braces in strings.
function parse(css) {
  let i = 0;
  const block = () => {
    const out = [];
    while (i < css.length) {
      while (/\s/.test(css[i] || "")) i++;
      if (i >= css.length || css[i] === "}") { i++; return out; }
      const start = i;
      while (i < css.length && css[i] !== "{" && css[i] !== ";" && css[i] !== "}") i++;
      const head = css.slice(start, i).trim();
      if (css[i] === ";") { i++; out.push({ type: "statement", head }); continue; }
      if (css[i] === "}") continue;
      i++;
      if (head.startsWith("@")) out.push({ type: "at", head, kids: block() });
      else { const b = i; let d = 1; while (d) { if (css[i] === "{") d++; else if (css[i] === "}") d--; i++; } out.push({ type: "rule", head, body: css.slice(b, i - 1).trim() }); }
    }
    return out;
  };
  return block();
}

const esc = (cls) => cls.replace(/([:/.@\[\]%!])/g, "\\$1").replace(/^(\d)/, (d) => `\\3${d} `);  // CSS writes a leading digit as a hex escape: .\32 xl\:…

// Replace .token with .name in a selector, outside :has() and :not() (where it would invert a rule), and only where
// the class name ends there.
function rename(selector, token, name) {
  const needle = "." + esc(token);
  let out = "", depth = 0, hasDepth = -1, i = 0;
  while (i < selector.length) {
    const fn = selector.startsWith(":has(", i) ? ":has(" : selector.startsWith(":not(", i) ? ":not(" : null;
    if (fn) { if (hasDepth < 0) hasDepth = depth; out += fn; depth++; i += fn.length; continue; }
    const ch = selector[i];
    if (ch === "(") depth++;
    if (ch === ")") { depth--; if (depth === hasDepth) hasDepth = -1; }
    if (hasDepth < 0 && selector.startsWith(needle, i) && !/[\w\\-]/.test(selector[i + needle.length] || "")) { out += "." + name; i += needle.length; continue; }
    out += ch; i++;
  }
  return out;
}
const splitList = (sel) => { const parts = []; let d = 0, s = 0; for (let i = 0; i < sel.length; i++) { if (sel[i] === "(") d++; else if (sel[i] === ")") d--; else if (sel[i] === "," && !d) { parts.push(sel.slice(s, i).trim()); s = i + 1; } } parts.push(sel.slice(s).trim()); return parts; };

const tree = [...parse(readFileSync(join(root, "reset.css"), "utf8")), ...parse(readFileSync(join(root, "nowind.css"), "utf8"))];
const utilities = tree.find((n) => n.type === "at" && n.head === "@layer nowind");
const reset = tree.find((n) => n.type === "at" && n.head === "@layer reset");
if (!utilities || !reset) throw new Error("components: reset.css needs its @layer reset block and nowind.css its @layer nowind block");

const defined = new Set();
const walk = (nodes, fn) => nodes.forEach((n) => n.type === "at" ? walk(n.kids, fn) : n.type === "rule" && fn(n));
const unesc = (c) => c.replace(/\\([0-9a-fA-F]{1,6}) ?/g, (_, h) => String.fromCodePoint(parseInt(h, 16))).replace(/\\(.)/g, "$1");
walk(utilities.kids, (r) => { for (const m of r.head.matchAll(/\.((?:[\w-]|\\[0-9a-fA-F]{1,6} ?|\\.)+)/g)) defined.add(unesc(m[1])); });

// A rule that styles a child of the class (.h-nested > .icon) must stay in the nowind layer, where it outranks the
// child's own utilities (icon-sm) as it does for the stack; rules on the element itself go in components.
const flat = (sel) => { let o = "", d = 0; for (const ch of sel) { if (ch === "(") d++; if (!d) o += ch; if (ch === ")") d--; } return o; };
const targetsChild = (sel, name) => new RegExp(`\\.${name}(?![\\w-])[^\\s>+~]*\\s*[>+~\\s]\\s*[^\\s]`).test(flat(sel));
function emit(nodes, tokens, name, keep = () => true) {
  const out = [];
  for (const n of nodes) {
    if (n.type === "at") { const kids = emit(n.kids, tokens, name, keep); if (kids.length) out.push(`${n.head} {\n${kids.map((k) => "  " + k.replace(/\n/g, "\n  ")).join("\n")}\n}`); continue; }
    if (n.type !== "rule") continue;
    const parts = splitList(n.head).flatMap((p) => tokens.filter((t) => p !== rename(p, t, "\u0000")).map((t) => rename(p, t, name))).filter((p) => keep(p));
    if (parts.length) out.push(`${[...new Set(parts)].join(", ")} { ${n.body} }`);
  }
  // Merge neighbouring rules with the same selector, so .btn reads as one block.
  const merged = [];
  for (const r of out) {
    const m = r.match(/^([^{@]+) \{ ([^{}]*) \}$/), last = merged[merged.length - 1], lm = last && last.match(/^([^{@]+) \{ ([^{}]*) \}$/);
    if (m && lm && m[1] === lm[1]) merged[merged.length - 1] = `${m[1]} { ${lm[2].replace(/;?\s*$/, ";")} ${m[2]} }`;
    else merged.push(r);
  }
  return merged;
}

const sections = [], childRules = [], resetRules = [], manifest = [];
for (const { name, use, recipe } of RECIPES) {
  const tokens = recipe.split(/\s+/);
  const missing = tokens.filter((t) => !defined.has(t));
  if (missing.length) throw new Error(`components: ${name} uses ${missing.join(", ")}, which nowind.css doesn't define`);
  sections.push(...emit(utilities.kids, tokens, name, (p) => !targetsChild(p, name)));
  childRules.push(...emit(utilities.kids, tokens, name, (p) => targetsChild(p, name)));
  resetRules.push(...emit(reset.kids, tokens, name));
  manifest.push({ class: name, recipe, use });
}

const block = (layer, rules) => rules.length ? `\n@layer ${layer} {\n${rules.map((s) => "  " + s.replace(/\n/g, "\n  ")).join("\n")}\n}\n` : "";
const css = `@layer reset, defaults, styles, components, nowind;\n${block("reset", resetRules)}${block("components", sections)}${block("nowind", childRules)}`;
const min = css.replace(/\s+/g, " ").replace(/\s*([{};])\s*/g, "$1").replace(/;}/g, "}").replace(/,\s+(?![^(]*\))/g, ",").trim() + "\n";
let depth = 0; for (const ch of css) { depth += ch === "{" ? 1 : ch === "}" ? -1 : 0; if (depth < 0) throw new Error("components: unbalanced braces"); }
if (depth) throw new Error("components: unbalanced braces");

mkdirSync(join(root, "dist"), { recursive: true });
writeFileSync(join(root, "dist/nowind.components.css"), css);
writeFileSync(join(root, "dist/nowind.components.min.css"), min);
writeFileSync(join(root, "nowind.components.manifest.json"), JSON.stringify({
  generated: "by scripts/components.mjs; edit the RECIPES there, not this file",
  description: "Convenience classes for the most repeated utility stacks in the examples (mined by count and length). Each is written by copying the utility rules its recipe uses, so it is the same as its stack. They ship in dist/nowind.components.css, in the components layer, which comes before nowind: any utility on the element still wins. The examples and the site use the utility classes; these are for people writing markup by hand or by generation.",
  layer: "components (declared between styles and nowind)",
  classes: manifest,
}, null, 2) + "\n");
console.log(`dist/nowind.components.css  ${RECIPES.length} classes, ${(Buffer.byteLength(css) / 1024).toFixed(1)} KiB (${(gzipSync(min).length / 1024).toFixed(1)} KiB gzip minified)`);
