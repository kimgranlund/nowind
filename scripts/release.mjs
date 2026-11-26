#!/usr/bin/env node
// Cuts a release locally, and only if everything passes. Never pushes.
//
// Usage: node scripts/release.mjs <version> --reviewed
//   1. First review the changes since the last tag: run /code-review in Claude Code on that range (this script prints
//      it when run without --reviewed). --reviewed says the review is done and its findings are fixed.
//   2. The script then: checks the tree is clean and on main, and the version is newer than the last tag; dates the
//      changelog's Unreleased entries under the new version; moves the README and landing-page links to the new tag;
//      regenerates (bundle, components, templates); runs check.mjs, its self-test and review.mjs all. If any step
//      fails it puts every file back and stops. Otherwise it commits "Release <version>" and tags v<version>.
//   3. Push yourself, after reading the result: git push origin main && git push origin v<version>
import { execFileSync, spawnSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const version = args.find((a) => !a.startsWith("--"));
const git = (...a) => execFileSync("git", a, { cwd: root, encoding: "utf8" }).trim();
const fail = (msg) => { console.error(`release: ${msg}`); process.exit(1); };

if (!version || !/^\d+\.\d+\.\d+$/.test(version)) fail("give the version as X.Y.Z, e.g. node scripts/release.mjs 0.12.1 --reviewed");
const last = git("describe", "--tags", "--abbrev=0").replace(/^v/, "");
const newer = (a, b) => { const [x, y] = [a, b].map((v) => v.split(".").map(Number)); for (let i = 0; i < 3; i++) if (x[i] !== y[i]) return x[i] > y[i]; return false; };
if (!newer(version, last)) fail(`${version} is not newer than the last release, ${last}`);
if (git("tag", "-l", `v${version}`)) fail(`the tag v${version} already exists`);
const commits = git("log", "--oneline", `v${last}..HEAD`).split("\n").filter(Boolean).length;
if (!commits) fail(`nothing to release: no commits since v${last}`);
if (!args.includes("--reviewed")) {
  console.log(`release: review the changes since v${last} first. In Claude Code, run /code-review on the range v${last}..HEAD:`);
  console.log(`  ${commits} commit${commits === 1 ? "" : "s"}, ${git("diff", "--shortstat", `v${last}..HEAD`)}`);
  console.log(`Fix what it finds, then run: node scripts/release.mjs ${version} --reviewed`);
  process.exit(1);
}
if (git("rev-parse", "--abbrev-ref", "HEAD") !== "main") fail("release from main");
if (git("status", "--porcelain")) fail("the working tree has changes; commit them first");

const changelog = join(root, "CHANGELOG.md");
const log = readFileSync(changelog, "utf8");
const m = log.match(/## Unreleased\n([\s\S]*?)\n## /);
if (!m || !m[1].trim()) fail("CHANGELOG.md has nothing under ## Unreleased");

const restore = () => { try { git("checkout", "--", "."); git("clean", "-fdq"); } catch {} };
const steps = [];
try {
  const today = new Date();
  const date = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  writeFileSync(changelog, log.replace("## Unreleased\n", `## Unreleased\n\n## ${version} (${date})\n`));
  const [lmaj, lmin] = last.split("."), [vmaj, vmin] = version.split(".");
  const readme = join(root, "README.md");
  writeFileSync(readme, readFileSync(readme, "utf8").replaceAll(`v${last}`, `v${version}`).replaceAll(`Nowind ${lmaj}.${lmin}<`, `Nowind ${vmaj}.${vmin}<`));
  const landing = join(root, "site/index.html");
  writeFileSync(landing, readFileSync(landing, "utf8").replaceAll(`v${last}`, `v${version}`).replaceAll(`>${last}<`, `>${version}<`).replaceAll(`Nowind ${last}`, `Nowind ${version}`));

  const run = (label, cmd, a) => {
    process.stdout.write(`release: ${label} … `);
    const r = spawnSync(cmd, a, { cwd: root, encoding: "utf8" });
    const out = (r.stdout || "") + (r.stderr || "");
    if (r.status !== 0) { console.log("failed"); console.log(out.split("\n").filter((l) => /error|fail|missed|finding/i.test(l)).slice(0, 20).join("\n")); throw new Error(label); }
    console.log("ok"); steps.push(label);
  };
  run("bundle", process.execPath, ["scripts/bundle.mjs"]);
  run("components", process.execPath, ["scripts/components.mjs"]);
  run("templates", "python3", ["scripts/templates.py"]);
  run("check", process.execPath, ["scripts/check.mjs"]);
  run("check self-test", process.execPath, ["scripts/check.mjs", "--self-test"]);
  run("review all", process.execPath, ["scripts/review.mjs", "all"]);
} catch (e) {
  restore();
  fail(`stopped at ${e.message}; every file is back as it was. Fix it, commit, and run again.`);
}
try {
  git("add", "-A");
  git("commit", "-q", "-m", `Release ${version}`);
} catch (e) { restore(); fail(`the release commit failed (${e.message.split("\n")[0]}); every file is back as it was.`); }
try { git("tag", "-a", `v${version}`, "-m", `Nowind ${version}`); }
catch (e) { fail(`committed ${git("rev-parse", "--short", "HEAD")} but the tag failed (${e.message.split("\n")[0]}). Fix it with: git tag -a v${version} -m "Nowind ${version}"`); }
console.log(`release: committed and tagged v${version} (${git("rev-parse", "--short", "HEAD")}). Not pushed. When you're ready:`);
console.log(`  git push origin main && git push origin v${version}`);
