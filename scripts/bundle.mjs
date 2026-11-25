#!/usr/bin/env node
// Bundles theme.css (with every @import inlined) and nowind.css into one file, plus a minified copy.
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
let utilities = stripComments(readFileSync(join(root, "nowind.css"), "utf8"));

// The layer order statement goes first, so it is declared before any layered rule.
const order = utilities.match(/@layer\s+[\w\s,-]+;/);
if (!order) throw new Error("nowind.css has no @layer order statement");
utilities = utilities.replace(order[0], "");

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

const kib = (s) => (Buffer.byteLength(s) / 1024).toFixed(1);
const gz = (s) => (gzipSync(s).length / 1024).toFixed(1);
console.log(`dist/nowind.bundle.css  ${kib(bundle)} KiB (${gz(bundle)} KiB gzip)`);
console.log(`dist/nowind.min.css     ${kib(min)} KiB (${gz(min)} KiB gzip)`);
