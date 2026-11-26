#!/usr/bin/env node
// Universal theme review: loads every site page in headless Chromium across a matrix and collects what each domain's
// rendered audit finds. No dependencies: it drives the browser over the DevTools protocol with Node's own WebSocket.
//
// Usage: node scripts/review.mjs [domain] [--pages a,b] [--widths 375,768] [--roots 12,16] [--quick]
//        node scripts/review.mjs --self-test   break the showcase nine ways and confirm the layout and paint audits catch each
//   domain  form (type, geometry, layout; the default) or paint (colour by step in light and dark; one width and root)
//   --quick one width (1280) and one root (16)
// Writes review/<domain>.json (every finding with its page, width and root) and review/<domain>.md (grouped by rule,
// each finding once with the contexts it appears in). The review folder is not committed.
// The browser: $NOWIND_CHROME, else the newest Chromium headless shell in Playwright's cache.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : def; };
const domain = args.find((a) => !a.startsWith("--") && !args[args.indexOf(a) - 1]?.startsWith("--")) || "form";
const DOMAINS = {
  form: { audits: ["type", "geometry", "layout"], globals: { type: "nowindRunTypeAudit", geometry: "nowindRunGeometryAudit", layout: "nowindRunLayoutAudit" } },
  paint: { audits: ["paint"], globals: { paint: "nowindRunPaintAudit" }, widths: "1280", roots: "16" },
};
if (!DOMAINS[domain]) { console.error(`review: unknown domain "${domain}". Known: ${Object.keys(DOMAINS).join(", ")}`); process.exit(2); }
const quick = args.includes("--quick");
const widths = (opt("widths", quick ? "1280" : DOMAINS[domain]?.widths || "375,768,1280")).split(",").map(Number);
const roots = (opt("roots", quick ? "16" : DOMAINS[domain]?.roots || "12,16,18")).split(",").map(Number);
const PORT = 8765, BASE = `http://localhost:${PORT}`;

const pages = (() => {
  const want = opt("pages", "");
  const found = [
    ...readdirSync(join(root, "site")).filter((n) => n.endsWith(".html")).map((n) => `site/${n}`),
    ...readdirSync(join(root, "site/docs")).filter((n) => n.endsWith(".html")).map((n) => `site/docs/${n}`),
  ].filter((p) => p !== "site/docs/classes.html" && p !== "site/docs/semantic.html" || want);
  return want ? found.filter((p) => want.split(",").some((w) => p.includes(w))) : found;
})();

function chromePath() {
  if (process.env.NOWIND_CHROME) return process.env.NOWIND_CHROME;
  const cache = join(homedir(), process.platform === "darwin" ? "Library/Caches/ms-playwright" : ".cache/ms-playwright");
  if (!existsSync(cache)) return null;
  const shells = readdirSync(cache).filter((n) => n.startsWith("chromium_headless_shell-")).sort((a, b) => Number(b.split("-")[1]) - Number(a.split("-")[1]));
  for (const s of shells) for (const d of readdirSync(join(cache, s))) {
    const bin = join(cache, s, d, process.platform === "win32" ? "chrome-headless-shell.exe" : "chrome-headless-shell");
    if (existsSync(bin)) return bin;
  }
  return null;
}

const SELF_TEST = `(async () => {
  await document.fonts.ready;
  const has = (k) => window.nowindRunLayoutAudit().some((f) => f.rule === k);
  const host = document.querySelector("#data .p-md.rounded-md");
  const add = (html) => { const d = document.createElement("div"); d.innerHTML = html; host.append(d); return () => d.remove(); };
  const breaks = {
    "page-overflow": () => add('<div style="width:3000px">x</div>'),
    "text-overflow": () => add('<p style="width:60px;white-space:nowrap">This text will not wrap here</p>'),
    "padding-symmetry": () => { host.style.paddingInlineEnd = "40px"; return () => host.style.paddingInlineEnd = ""; },
    "start-edge": () => add('<p>One line of text</p><p class="ps-xs">Two indented</p><p>Three</p>'),
    "baseline": () => add('<div class="flex items-center gap-xs"><span class="text-3xl">Big</span><span class="text-xs">small</span></div>'),
    "centering": () => { const st = document.createElement("style"); st.textContent = ".h-control{padding-top:8px!important}"; document.head.append(st); return () => st.remove(); },
    "measure": () => add('<p style="width:1200px">' + "Long running text. ".repeat(20) + "</p>"),
  };
  const out = {};
  for (const [k, f] of Object.entries(breaks)) {
    if (has(k)) { out[k] = "already reported before the break"; continue; }
    const undo = f(); await new Promise((r) => setTimeout(r, 60));
    out[k] = has(k) ? "caught" : "missed"; undo();
  }
  return JSON.stringify(out);
})()`;

const PAINT_SELF_TEST = `(async () => {
  const has = (k) => window.nowindRunPaintAudit().some((f) => f.rule === k);
  const host = document.querySelector("#data .p-md.rounded-md");
  const add = (html) => { const d = document.createElement("div"); d.innerHTML = html; host.append(d); return () => d.remove(); };
  const breaks = {
    "parity": () => add('<span class="block p-sm bg-black">gone in dark</span>'),
    "relief": () => add('<div class="relief-raised p-sm">no material</div>'),
  };
  const out = {};
  for (const [k, f] of Object.entries(breaks)) {
    if (has(k)) { out[k] = "already reported before the break"; continue; }
    const undo = f(); await new Promise((r) => setTimeout(r, 60));
    out[k] = has(k) ? "caught" : "missed"; undo();
  }
  return JSON.stringify(out);
})()`;

async function up() { try { return (await fetch(`${BASE}/site/index.html`)).ok; } catch { return false; } }

async function main() {
  let server = null;
  if (!(await up())) {
    server = spawn(process.execPath, [join(root, "scripts/serve.mjs"), String(PORT)], { stdio: "ignore" });
    for (let i = 0; i < 50 && !(await up()); i++) await new Promise((r) => setTimeout(r, 100));
  }
  const bin = chromePath();
  if (!bin) { console.error("review: no Chromium found. Fix: set NOWIND_CHROME to a Chrome or chrome-headless-shell binary, or run `npx playwright install chromium-headless-shell`."); process.exit(2); }
  const chrome = spawn(bin, ["--headless", "--remote-debugging-port=0", "--no-first-run", "--hide-scrollbars", "--force-color-profile=srgb", "about:blank"], { stdio: ["ignore", "ignore", "pipe"] });
  const wsUrl = await new Promise((res, rej) => {
    let buf = "";
    chrome.stderr.on("data", (d) => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) res(m[1]); });
    chrome.on("exit", () => rej(new Error("Chromium exited before it listened")));
  });
  const ws = new WebSocket(wsUrl);
  await new Promise((r) => ws.addEventListener("open", r, { once: true }));
  let id = 0; const waiting = new Map(), listeners = [];
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && waiting.has(msg.id)) { const { res, rej } = waiting.get(msg.id); waiting.delete(msg.id); msg.error ? rej(new Error(msg.error.message)) : res(msg.result); }
    else listeners.forEach((l) => l(msg));
  });
  const send = (method, params = {}, sessionId) => new Promise((res, rej) => { const i = ++id; waiting.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
  const once = (method, sessionId) => new Promise((res) => { const l = (m) => { if (m.method === method && m.sessionId === sessionId) { listeners.splice(listeners.indexOf(l), 1); res(m.params); } }; listeners.push(l); });

  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
  await send("Page.enable", {}, sessionId);
  await send("Runtime.enable", {}, sessionId);
  if (args.includes("--self-test")) {
    // Break the showcase nine ways and confirm the layout and paint audits report each rule.
    await send("Emulation.setDeviceMetricsOverride", { width: 768, height: 900, deviceScaleFactor: 1, mobile: false }, sessionId);
    const loaded = once("Page.loadEventFired", sessionId);
    await send("Page.navigate", { url: `${BASE}/site/components.html?audit=layout,paint` }, sessionId);
    await loaded;
    const res = {};
    for (const expr of [SELF_TEST, PAINT_SELF_TEST]) {
      const { result } = await send("Runtime.evaluate", { awaitPromise: true, returnByValue: true, expression: expr }, sessionId);
      Object.assign(res, JSON.parse(result.value));
    }
    ws.close(); chrome.kill(); if (server) server.kill();
    for (const [rule, v] of Object.entries(res)) console.log(`${v === "caught" ? "PASS" : "FAIL"}  self-test "${rule}" ${v}`);
    const bad = Object.values(res).some((v) => v !== "caught");
    console.log(bad ? "review self-test: a break went unreported" : "review self-test: every break was caught");
    process.exit(bad ? 1 : 0);
  }
  const { audits, globals } = DOMAINS[domain];
  const findings = [];
  const total = pages.length * widths.length * roots.length;
  let done = 0;
  for (const rootSize of roots) {
    const { identifier } = await send("Page.addScriptToEvaluateOnNewDocument", { source: `try{localStorage.setItem("nowind-root-size","${rootSize}");localStorage.removeItem("nowind-tier");localStorage.removeItem("nowind-color-mode")}catch(e){}` }, sessionId);
    for (const width of widths) {
      await send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 768 }, sessionId);
      for (const page of pages) {
        const loaded = once("Page.loadEventFired", sessionId);
        await send("Page.navigate", { url: `${BASE}/${page}?audit=${audits.join(",")}` }, sessionId);
        await Promise.race([loaded, new Promise((r) => setTimeout(r, 15000))]);
        const expr = `(async () => { await document.fonts.ready; await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); const out = {}; ${audits.map((a) => `out.${a} = window.${globals[a]} ? window.${globals[a]}() : [{ rule: \"missing\", where: \"page\", detail: \"${globals[a]} is not defined\" }];`).join(" ")} return JSON.stringify(out); })()`;
        const { result, exceptionDetails } = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }, sessionId);
        if (exceptionDetails) findings.push({ domain, audit: "harness", rule: "error", page, width, root: rootSize, where: "page", detail: exceptionDetails.exception?.description?.split("\n")[0] || exceptionDetails.text });
        else for (const [audit, list] of Object.entries(JSON.parse(result.value))) for (const f of list || []) findings.push({ domain, audit, page, width, root: rootSize, ...f });
        done++;
        if (process.stdout.isTTY) process.stdout.write(`\rreview ${domain}: ${done}/${total}`);
      }
    }
    await send("Page.removeScriptToEvaluateOnNewDocument", { identifier }, sessionId);
  }
  if (process.stdout.isTTY) process.stdout.write("\n");
  ws.close(); chrome.kill(); if (server) server.kill();

  const dir = join(root, "review"); mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, `${domain}.json`), JSON.stringify({ domain, pages, widths, roots, findings }, null, 1) + "\n");
  const groups = new Map();
  for (const f of findings) {
    const key = `${f.audit}|${f.rule}|${f.page}|${f.where}`;
    if (!groups.has(key)) groups.set(key, { ...f, contexts: [] });
    groups.get(key).contexts.push(`${f.width}/${f.root}`);
  }
  const byRule = {};
  for (const g of groups.values()) (byRule[`${g.audit}: ${g.rule}`] ||= []).push(g);
  const lines = [`# Review: ${domain}`, "", `${pages.length} pages × widths ${widths.join(", ")} × roots ${roots.join(", ")}: ${findings.length} findings, ${groups.size} distinct.`, ""];
  for (const [rule, gs] of Object.entries(byRule).sort((a, b) => b[1].length - a[1].length)) {
    lines.push(`## ${rule} (${gs.length})`, "");
    for (const g of gs) lines.push(`- ${g.page} ${g.where}: ${g.detail} [${g.contexts.length === widths.length * roots.length ? "all" : g.contexts.join(" ")}]`);
    lines.push("");
  }
  writeFileSync(join(dir, `${domain}.md`), lines.join("\n"));
  console.log(`review ${domain}: ${findings.length} findings, ${groups.size} distinct, across ${Object.keys(byRule).length} rules. Report: review/${domain}.md`);
  for (const [rule, gs] of Object.entries(byRule).sort((a, b) => b[1].length - a[1].length)) console.log(`  ${String(gs.length).padStart(4)}  ${rule}`);
  process.exit(0);
}
main().catch((e) => { console.error(`review: ${e.message}`); process.exit(1); });
