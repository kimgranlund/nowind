#!/usr/bin/env node
// Checks the rules AGENTS.md states. Usage:
//   node scripts/check.mjs              check this repository
//   node scripts/check.mjs --self-test  break a copy four ways and confirm each check fails
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
  ...readdirSync(join(repo, "templates")).filter((n) => n.endsWith(".html")).map((n) => `templates/${n}`),
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

  // 4. Generated files match what the scripts write.
  const tmp = mkdtempSync(join(tmpdir(), "nowind-check-"));
  try {
    cpSync(root, tmp, { recursive: true, filter: (p) => !p.includes(`${join(root, ".git")}`) });
    for (const script of ["utopia.mjs", "shadows.mjs", "motion.mjs", "materials.mjs", "utilities.mjs", "bundle.mjs"]) {
      execFileSync(process.execPath, [join(tmp, "scripts", script)], { cwd: tmp, stdio: "ignore" });
    }
    execFileSync("python3", [join(tmp, "scripts", "templates.py"), join(tmp, "templates")], { cwd: tmp, stdio: "ignore" });
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
    ["comment in theme CSS", "theme/theme.colors.css", (s) => s.replace(":root {", ":root {\n  /* note */")],
    ["color-mix()", "theme/theme.type-roles.css", (s) => s.replace(":root {", ":root {\n  --x: color-mix(in oklab, red, blue);")],
    ["manifest names an undefined token", "theme/theme.geometry.manifest.json", (s) => s.replace('"--slot"', '"--slot-missing"')],
    ["hand-edited generated file", "nowind.css", (s) => s + "\n.hand-edit { color: red; }\n"],
  ];
  let ok = true;
  for (const [name, file, mutate] of breaks) {
    const tmp = mkdtempSync(join(tmpdir(), "nowind-selftest-"));
    try {
      cpSync(repo, tmp, { recursive: true, filter: (p) => !p.includes(`${join(repo, ".git")}`) });
      const target = join(tmp, file);
      const before = readFileSync(target, "utf8");
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
