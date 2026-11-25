#!/usr/bin/env node
// Checks the rules AGENTS.md states. Usage:
//   node scripts/check.mjs              check this repository
//   node scripts/check.mjs --self-test  break a copy seventeen ways and confirm each check fails
import { readFileSync, readdirSync, statSync, cpSync, mkdtempSync, rmSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, relative } from "node:path";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");

const walk = (dir) => readdirSync(dir).flatMap((n) => {
  const p = join(dir, n);
  return statSync(p).isDirectory() ? walk(p) : [p];
});

// The CSS Nowind owns: everything except the copied colour library.
const ownCss = (root) => [
  join(root, "theme.css"),
  join(root, "nowind.css"),
  ...walk(join(root, "theme")).filter((p) => p.endsWith(".css") && !p.includes(`${join("theme", "colors-raw")}`)),
  ...walk(join(root, "dist")).filter((p) => p.endsWith(".css")),
];

// Companion suffixes (--{role}--line-height) are named on their own in prose; they are not tokens.
const COMPANIONS = new Set(["line-height", "font-weight", "font-family", "letter-spacing", "font-variant-numeric", "text-transform", "font-style", "font-variant-ligatures"]);

const GENERATED = [
  "nowind.css",
  "nowind.manifest.json",
  "classes.md",
  "theme/theme.typography.css",
  "theme/theme.typography.manifest.json",
  "theme/theme.space.css",
  "theme/theme.space.manifest.json",
  "theme/theme.shadows.css",
  "theme/theme.shadows.manifest.json",
  "theme/theme.motion.css",
  "theme/theme.motion.manifest.json",
  "theme/theme.materials.css",
  "theme/theme.materials.manifest.json",
  "dist/nowind.bundle.css",
  "dist/nowind.min.css",
  ...readdirSync(join(repo, "site", "docs")).filter((n) => n.endsWith(".html")).map((n) => `site/docs/${n}`),
  "site/search.json",
  "components.manifest.json",
  "site/index.html",
  "site/components.html",
  "site/specimen.html",
  "site/utilities.html",
];

function check(root) {
  const errors = [];
  const rel = (p) => relative(root, p);

  // 1. No comments in the CSS. 2. No color-mix().
  for (const file of ownCss(root)) {
    const css = readFileSync(file, "utf8");
    if (/\/\*/.test(css)) errors.push(`${rel(file)}: has a comment. Fix: move the note into its manifest.`);
    if (/color-mix\(/.test(css)) errors.push(`${rel(file)}: uses color-mix(). Fix: use an alpha step (--{palette}-a1..a12).`);
  }

  // 3. Every concrete token a manifest names is defined in the CSS.
  const defined = new Set();
  for (const file of [...ownCss(root), ...walk(join(root, "theme", "colors-raw")).filter((p) => p.endsWith(".css"))]) {
    for (const m of readFileSync(file, "utf8").matchAll(/(--[\w-]+)\s*:/g)) defined.add(m[1]);
  }
  const manifests = [join(root, "nowind.manifest.json"), ...readdirSync(join(root, "theme")).filter((n) => n.endsWith(".manifest.json")).map((n) => join(root, "theme", n))];
  for (const file of manifests) {
    const text = readFileSync(file, "utf8");
    JSON.parse(text);
    // A token followed by "-{", "-N" or a placeholder is a pattern, and a flag followed by a number is a CLI option.
    for (const m of text.matchAll(/(?<![\w}-])--[a-z][a-z0-9-]*[a-z0-9](?![\w{-]|\s\d)/g)) {
      if (COMPANIONS.has(m[0].slice(2))) continue;
      if (!defined.has(m[0])) errors.push(`${rel(file)}: names ${m[0]}, which no CSS file defines. Fix: update the manifest in the same change as the CSS.`);
    }
  }

  // 5. Controls share one recipe: every interactive element sized as a control has a border width (transparent on solid
  // or ghost fills, never border-0), a radius class and control padding. Examples have no control classes, so this covers the site's own chrome.
  const pages = [...readdirSync(join(root, "site")).filter((n) => n.endsWith(".html")).map((n) => join(root, "site", n)),
    ...readdirSync(join(root, "site", "docs")).filter((n) => n.endsWith(".html")).map((n) => join(root, "site", "docs", n))];
  for (const file of pages) {
    const text = readFileSync(file, "utf8");
    for (const m of text.matchAll(/<(a|button|summary|input|select|textarea)\b[^>]*\sclass="([^"]*)"/g)) {
      const t = m[2].split(/\s+/);
      if (!t.includes("h-control") && !t.includes("size-control")) continue;
      const miss = [];
      if (t.includes("border-0") || !t.some((x) => /^border(-[xytblr])?(-[24])?$/.test(x))) miss.push("a border width (border, with border-transparent on a fill)");
      if (!t.some((x) => /^rounded(-|$)/.test(x))) miss.push("a radius (rounded-sm)");
      if (t.includes("h-control") && !t.includes("px-control") && !t.includes("w-full")) miss.push("px-control");
      if (miss.length) errors.push(`${rel(file)}: <${m[1]} class="${m[2].slice(0, 60)}…"> lacks ${miss.join(", ")}. Fix: follow the control recipe in AGENTS.md.`);
    }
  }

  // 6. Examples (component snippets, showcase blocks) use regular classes only; scripts/templates.py --lint lists any semantic one.
  try {
    execFileSync("python3", [join(root, "scripts", "templates.py"), "--lint"], { cwd: root, encoding: "utf8" });
  } catch (e) {
    const lines = String(e.stdout || "").split("\n").filter(Boolean);
    if (lines.length) errors.push(...lines);
    else errors.push(`scripts/templates.py --lint failed: ${String(e.stderr || e.message).trim().split("\n").pop()}`);
  }

  // 7. AGENTS.md names every file in the repo (by path, glob or directory), and every path it names exists.
  {
    const agents = readFileSync(join(root, "AGENTS.md"), "utf8");
    const fenced = [...agents.matchAll(/```[^\n]*\n([\s\S]*?)```/g)].map((m) => m[1]);
    const prose = agents.replace(/```[\s\S]*?```/g, "");
    const tokens = [...fenced, ...[...prose.matchAll(/`([^`\n]+)`/g)].map((m) => m[1])].flatMap((t) => t.split(/\s+/));
    const refs = new Set(tokens.filter((t) => /^[\w.*/-]+$/.test(t) && /[./]/.test(t)));
    const glob = (pat) => new RegExp("^" + pat.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, "[^/]*") + "$");
    const rowDirs = [...agents.matchAll(/^\| `([\w/-]+\/)`/gm)].map((m) => m[1]);
    const covers = (f) => [...refs].some((r) => r === f || (r.includes("*") && glob(r).test(f))) || rowDirs.some((d) => f.startsWith(d));
    const listed = [
      ...readdirSync(root).filter((n) => /\.(css|json|md|html)$/.test(n)),
      ...["site", "scripts", "theme", "dist"].flatMap((d) => existsSync(join(root, d)) ? readdirSync(join(root, d)).filter((n) => /\.(css|json|md|html|js|mjs|py)$/.test(n)).map((n) => `${d}/${n}`) : []),
    ];
    for (const f of listed) if (!covers(f)) errors.push(`${f}: AGENTS.md doesn't name it. Fix: add it to the table in "Where things live".`);
    for (const r of refs) {
      if (!r.includes("/") || /^(https?:|\.\.?\/|@|--)/.test(r) || /[{}]/.test(r) || !/(\.(css|json|md|html|js|mjs|py)|\/)$/.test(r.split(/[#:]/)[0])) continue;
      const path = r.split(/[#:]/)[0];
      const ok = path.includes("*") ? readdirSync(join(root, dirname(path))).some((n) => glob(path).test(`${dirname(path)}/${n}`)) : existsSync(join(root, path));
      if (!ok) errors.push(`AGENTS.md: names ${r}, which doesn't exist. Fix: update the path.`);
    }
  }

  // 4. Generated files match what the scripts write.
  const tmp = mkdtempSync(join(tmpdir(), "nowind-check-"));
  try {
    cpSync(root, tmp, { recursive: true, filter: (p) => !p.includes(`${join(root, ".git")}`) });
    for (const script of ["utopia.mjs", "shadows.mjs", "motion.mjs", "materials.mjs", "utilities.mjs", "bundle.mjs"]) {
      execFileSync(process.execPath, [join(tmp, "scripts", script)], { cwd: tmp, stdio: "ignore" });
    }
    execFileSync("python3", [join(tmp, "scripts", "templates.py"), join(tmp, "site", "docs")], { cwd: tmp, stdio: "ignore" });
    for (const f of GENERATED) {
      const a = join(root, f), b = join(tmp, f);
      if (!existsSync(a)) { errors.push(`${f}: missing. Fix: run the scripts in AGENTS.md order.`); continue; }
      if (readFileSync(a, "utf8") !== readFileSync(b, "utf8")) errors.push(`${f}: differs from what the scripts write. Fix: edit the script or the theme, then run node scripts/utopia.mjs, shadows.mjs, utilities.mjs and bundle.mjs.`);
    }
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
  return errors;
}

if (process.argv.includes("--self-test")) {
  const breaks = [
    ["semantic class in an example", "site/components.html", (s) => s.replace(/(md:col-span-9 min-w-0 flex flex-col gap-group">[\s\S]*?class="[^"]*?)\bp-md\b/, "$1p-surface")],
    ["control without a border", "site/components.html", (s) => s.replace(/(<button[^>]*class="[^"]*\bh-control\b[^"]*?)\bborder\b/, "$1border-0")],
    ["comment in theme CSS", "theme/theme.colors.css", (s) => s.replace(":root {", ":root {\n  /* note */")],
    ["color-mix()", "theme/theme.type-roles.css", (s) => s.replace("{", "{\n  --x: color-mix(in oklab, red, blue);")],
    ["manifest names an undefined token", "theme/theme.geometry.manifest.json", (s) => s.replace('"--slot"', '"--slot-missing"')],
    ["hand-edited generated file", "nowind.css", (s) => s + "\n.hand-edit { color: red; }\n"],
    ["file AGENTS.md doesn't name", "site/unlisted.html", () => "<!doctype html>\n"],
    ["small control beside full-size ones", "site/components.html", (s) => s.replace(/(<button [^>]*aria-label="Settings">.*?<\/button>)/, '$1<button class="size-nested" aria-label="X"><i class="icon icon-sm ph ph-x"></i></button>')],
    ["badge off the geometry contract", "site/components.html", (s) => s.replace(/(class="inline-flex items-center h-nested )px-nested( rounded-full border)/, "$1px-2xs$2")],
    ["card off the geometry contract", "site/components.html", (s) => s.replace('<div class="p-md rounded-md bg-neutral-1 border border-neutral-6', '<div class="p-md rounded-sm bg-neutral-1 border border-neutral-6')],
    ["text off the size contract", "site/components.html", (s) => s.replace('<li class="flex items-center gap-xs text-base">', '<li class="flex items-center gap-xs text-sm">')],
    ["field box sized by padding", "site/components.html", (s) => s.replace(/<div class="flex items-center gap-gutter h-control px-control rounded-sm border[^"]*">(\s*<i class="icon ph ph-magnifying-glass)/, '<div class="flex items-center py-xs ps-xs pe-sm gap-gutter rounded-sm border bg-neutral-1">$1')],
    ["two classes set one property", "site/components.html", (s) => s.replace(/(md:col-span-9 min-w-0 flex flex-col gap-group">[\s\S]*?class="[^"]*?)\bh-control\b/, "$1h-control h-full")],
    ["oval round marker", "site/components.html", (s) => s.replace(/size-nested shrink-0 rounded-full border-2/, "p-3xs rounded-full border-2")],
    ["control gap from the space scale", "site/components.html", (s) => s.replace(/(md:col-span-9 min-w-0 flex flex-col gap-group">[\s\S]*?class="[^"]*?h-control px-control )gap-gutter\b/, "$1gap-xs")],
    ["control sized by padding", "site/components.html", (s) => s.replace(/(md:col-span-9 min-w-0 flex flex-col gap-group">[\s\S]*?<button class="[^"]*?)\bh-control px-control\b/, "$1py-xs px-sm")],
    ["text padding at an icon edge", "site/components.html", (s) => s.replace(/(md:col-span-9 min-w-0 flex flex-col gap-group">[\s\S]*?class="[^"]*?)\bps-xs pe-sm\b/, "$1px-sm")],
    ["hover tint in place of state", "site/components.html", (s) => s.replace(/(md:col-span-9 min-w-0 flex flex-col gap-group">[\s\S]*?class="[^"]*?)\bstate\b/, "$1hover:bg-neutral-4")],
  ];
  let ok = true;
  for (const [name, file, mutate] of breaks) {
    const tmp = mkdtempSync(join(tmpdir(), "nowind-selftest-"));
    try {
      cpSync(repo, tmp, { recursive: true, filter: (p) => !p.includes(`${join(repo, ".git")}`) });
      const target = join(tmp, file);
      const before = existsSync(target) ? readFileSync(target, "utf8") : "";
      const after = mutate(before);
      if (after === before) { console.log(`FAIL  self-test "${name}": the mutation did not apply`); ok = false; continue; }
      writeFileSync(target, after);
      const errors = check(tmp);
      if (errors.length) console.log(`PASS  self-test "${name}" is caught: ${errors[0]}`);
      else { console.log(`FAIL  self-test "${name}" was not caught`); ok = false; }
    } finally {
      rmSync(tmp, { recursive: true, force: true });
    }
  }
  console.log(ok ? "self-test: every break was caught" : "self-test: a break was missed");
  process.exit(ok ? 0 : 1);
}

const errors = check(repo);
for (const e of errors) console.log(`ERROR ${e}`);
console.log(`check: ${errors.length} error(s)`);
process.exit(errors.length ? 1 : 0);
