#!/usr/bin/env node
// Bundles theme.css (with every @import inlined), reset.css, defaults.css and nowind.css into one file, plus a minified
// copy, and writes each part minified on its own (dist/nowind.{theme,reset,defaults,utilities}.min.css) for pages that
// take only some: classless (theme, reset, defaults) or with their own components (theme, reset, utilities).
// Usage: node scripts/bundle.mjs
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, relative } from "node:path";
import { gzipSync } from "node:zlib";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");

const stripComments = (css) => css.replace(/\/\*[\s\S]*?\*\//g, "");

// Remote imports (the web fonts) stay as @import and move to the top, where CSS requires them.
const remote = new Set();

function inline(file, seen = new Set()) {
  if (seen.has(file)) return "";
  seen.add(file);
  const css = stripComments(readFileSync(file, "utf8"));
  return css.replace(/@import\s+(?:url\()?["']([^"']+)["']\)?\s*;/g, (_, href) => {
    if (/^(https?:)?\/\//.test(href)) { remote.add(href); return ""; }
    return inline(join(dirname(file), href), seen);
  });
}

const theme = inline(join(root, "theme.css"));
// The layer order statement opens each layer file; the bundle declares it once, first, before any layered rule.
const layerFile = (name) => {
  const css = stripComments(readFileSync(join(root, name), "utf8"));
  const m = css.match(/@layer\s+[\w\s,-]+;/);
  if (!m) throw new Error(`${name} has no @layer order statement`);
  return { order: m[0], body: css.replace(m[0], "") };
};
const parts = { reset: layerFile("reset.css"), defaults: layerFile("defaults.css"), utilities: layerFile("nowind.css") };
const order = [parts.utilities.order];
if (new Set(Object.values(parts).map((x) => x.order)).size !== 1) throw new Error("reset.css, defaults.css and nowind.css declare different layer orders");
const utilities = [parts.reset.body, parts.defaults.body, parts.utilities.body].join("\n");

if (/@import/.test(theme + utilities)) throw new Error("A local @import was left unresolved");

const tidy = (css) => css.replace(/[ \t]+$/gm, "").replace(/\n{3,}/g, "\n\n").trim();
const imports = [...remote].map((u) => `@import url("${u}");`).join("\n");
const bundle = `${order[0]}\n${imports}\n\n${tidy(theme)}\n\n${tidy(utilities)}\n`;

function minify(css) {
  return css
    .replace(/\s+/g, " ")
    .replace(/\s*([{};])\s*/g, "$1")
    .replace(/;}/g, "}")
    .replace(/,\s+(?![^(]*\))/g, ",")
    .trim() + "\n";
}

// Check the braces balance before writing, so a broken bundle never ships.
for (const [name, css] of [["bundle", bundle]]) {
  let depth = 0;
  for (const ch of css) {
    if (ch === "{") depth++;
    if (ch === "}") depth--;
    if (depth < 0) throw new Error(`${name}: unbalanced braces`);
  }
  if (depth !== 0) throw new Error(`${name}: unbalanced braces`);
}

const min = minify(bundle);
mkdirSync(dist, { recursive: true });
writeFileSync(join(dist, "nowind.bundle.css"), bundle);
writeFileSync(join(dist, "nowind.min.css"), min);
const pieces = {
  theme: `${imports}\n\n${tidy(theme)}\n`,
  reset: `${order[0]}\n${tidy(parts.reset.body)}\n`,
  defaults: `${order[0]}\n${tidy(parts.defaults.body)}\n`,
  utilities: `${order[0]}\n${tidy(parts.utilities.body)}\n`,
};
for (const [name, css] of Object.entries(pieces)) writeFileSync(join(dist, `nowind.${name}.min.css`), minify(css));

const kib = (s) => (Buffer.byteLength(s) / 1024).toFixed(1);
const gz = (s) => (gzipSync(s).length / 1024).toFixed(1);
console.log(`dist/nowind.bundle.css  ${kib(bundle)} KiB (${gz(bundle)} KiB gzip)`);
console.log(`dist/nowind.min.css     ${kib(min)} KiB (${gz(min)} KiB gzip)`);
for (const [name, css] of Object.entries(pieces)) console.log(`dist/nowind.${name}.min.css`.padEnd(32) + `${gz(minify(css))} KiB gzip`);
console.log(`classless (theme, reset, defaults)     ${gz(minify(pieces.theme) + minify(pieces.reset) + minify(pieces.defaults))} KiB gzip, as three files`);
