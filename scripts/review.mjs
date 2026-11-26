#!/usr/bin/env node
// Universal theme review: loads every site page in headless Chromium across a matrix and collects what each domain's
// rendered audit finds. No dependencies: it drives the browser over the DevTools protocol with Node's own WebSocket.
//
// Usage: node scripts/review.mjs [domain] [--pages a,b] [--widths 375,768] [--roots 12,16] [--quick] [--strict]
//        node scripts/review.mjs all         the release gate: every domain with --strict (fail on any finding), then the self-test
//        node scripts/review.mjs --self-test   break the showcase seventeen ways and confirm the layout, paint and behaviour audits catch each
//   domain  form (type, geometry, layout; the default), paint (colour by step in light and dark) or behaviour (hover,
//           press, focus, on, disabled, targets and motion, forced per element over the DevTools protocol); one width and root
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
  behaviour: { audits: [], globals: {}, widths: "1280", roots: "16", custom: true },
};
if (domain === "all") {
  // The release gate: every domain, then the self-test, each in its own run; fails if any finds anything.
  const { spawnSync } = await import("node:child_process");
  const me = fileURLToPath(import.meta.url);
  let failed = 0;
  for (const run of [...Object.keys(DOMAINS).map((d) => [d, "--strict"]), ["--self-test"]]) {
    console.log(`\n== review ${run.join(" ")}`);
    const r = spawnSync(process.execPath, [me, ...run, ...args.filter((a) => a !== "all")], { stdio: "inherit" });
    if (r.status !== 0) failed++;
  }
  console.log(failed ? `\nreview all: ${failed} run(s) failed` : "\nreview all: clean");
  process.exit(failed ? 1 : 0);
}
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

// Behaviour (theme/theme.behaviour.manifest.json): marks every interactive element, reads its transitions at rest, then
// freezes transitions and forces :hover, :hover:active and :focus-visible on each through CSS.forcePseudoState,
// comparing computed styles. Findings: hover, press, focus, on-vs-hover, disabled, target, motion-tokens.
const BEHAVIOUR_SETUP = `(() => {
  const SEL = "a[href], button, summary, select, input:not([type=hidden]), textarea, [role=button], [role=tab], [role=option], [role=menuitem], [role=switch], [role=checkbox], [role=radio]";
  const visible = (e) => { const c = getComputedStyle(e), r = e.getBoundingClientRect(); return c.display !== "none" && c.visibility !== "hidden" && r.width > 0 && r.height > 0 && !e.closest("dialog:not([open]), [popover]:not(:popover-open), [hidden], template, .sr-only, [data-page-css] ~ *"); };
  if (document.querySelector("style[data-page-css]")) return JSON.stringify({ info: [], durs: [], eases: [] });
  document.querySelectorAll("[data-nwb], [data-nwbox]").forEach((e) => { e.removeAttribute("data-nwb"); e.removeAttribute("data-nwbox"); });
  const els = [...document.querySelectorAll(SEL)].filter(visible).filter((e) => !e.closest("[data-semantic-demo]") && !(e.tagName === "INPUT" && /^(range|color|file|hidden)$/.test(e.type)));
  els.forEach((e, i) => { e.setAttribute("data-nwb", i); const box = e.matches("input, select, textarea") && e.parentElement.closest(".cursor-text"); if (box) box.setAttribute("data-nwbox", ((box.getAttribute("data-nwbox") || "") + " " + i).trim()); });
  const probe = document.createElement("div"); document.body.append(probe);
  const durs = new Set(["0s"]), eases = new Set();
  for (const n of ["fade", "snappy", "smooth", "bouncy"]) { probe.style.transitionDuration = "var(--duration-" + n + ")"; durs.add(getComputedStyle(probe).transitionDuration); }
  for (const n of ["standard", "smooth", "snappy", "bouncy", "out", "in"]) { probe.style.transitionTimingFunction = "var(--ease-" + n + ")"; eases.add(getComputedStyle(probe).transitionTimingFunction); }
  probe.style.transitionDuration = "var(--motion-duration)"; durs.add(getComputedStyle(probe).transitionDuration);
  probe.style.transitionTimingFunction = "var(--motion-easing)"; eases.add(getComputedStyle(probe).transitionTimingFunction);
  probe.remove();
  const where = (e) => { const s = e.closest("section[id], header, footer, [data-example]"); const tag = s ? (s.id ? "#" + s.id : s.tagName.toLowerCase()) : "?"; return tag + " " + e.tagName.toLowerCase() + "." + [...e.classList].slice(0, 5).join(".") + " “" + (e.textContent.trim() || e.getAttribute("aria-label") || e.value || "").replace(/\\s+/g, " ").slice(0, 24) + "”"; };
  const ON = (e) => !!e.closest('[aria-sort=ascending], [aria-sort=descending]') || e.matches('[aria-pressed=true], [aria-selected=true], [aria-checked=true], [aria-expanded=true], [open], :checked') || (e.matches("[aria-current]") && e.getAttribute("aria-current") !== "false");
  const info = els.map((e) => {
    const c = getComputedStyle(e), r = e.getBoundingClientRect();
    const inText = e.tagName === "A" && [...e.parentElement.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    const box = e.matches("input, select, textarea") && e.parentElement.closest(".cursor-text");
    const field = e.matches("input:not([type=checkbox], [type=radio], [type=button], [type=submit], [type=reset]), select, textarea");
    return { where: where(e), w: r.width, h: r.height, x: r.left + r.width / 2, y: r.top + r.height / 2, rect: [r.left, r.top, r.right, r.bottom], boxed: !!box, field,
      label: !!e.closest("label") && e.matches("input[type=checkbox], input[type=radio]"), disabled: e.matches(":disabled, [aria-disabled=true]"), on: ON(e), state: e.classList.contains("state"), inText,
      sig: e.tagName + "|" + [...e.classList].filter((k) => !/^(pressed|selected|current|expanded|open):/.test(k)).sort().join(" "),
      prop: c.transitionProperty, dur: c.transitionDuration, ease: c.transitionTimingFunction };
  });
  const still = document.createElement("style"); still.id = "nwb-still"; still.textContent = "*, *::before, *::after { transition: none !important; animation: none !important; }"; document.head.append(still);
  window.__nwSnap = (i, box) => { const e = document.querySelector(box ? '[data-nwbox~="' + i + '"]' : '[data-nwb="' + i + '"]'), c = getComputedStyle(e), a = getComputedStyle(e, "::after"), b = getComputedStyle(e, "::before");
    return JSON.stringify([c.backgroundColor, c.color, c.outlineStyle + " " + c.outlineWidth + " " + c.outlineColor, c.borderTopColor, c.borderBottomColor, c.borderInlineStartColor, c.boxShadow, c.opacity, c.textDecorationLine, c.textDecorationColor, c.filter, c.transform, a.backgroundColor, a.opacity, b.backgroundColor, b.opacity]); };
  window.__nwRing = (i) => { const e = document.querySelector('[data-nwb="' + i + '"]'), c = getComputedStyle(e); return JSON.stringify({ outline: c.outlineStyle !== "none" && parseFloat(c.outlineWidth) > 0, shadow: c.boxShadow }); };
  return JSON.stringify({ info, durs: [...durs], eases: [...eases] });
})()`;

async function behaviourPage(send, sessionId) {
  const out = [];
  await send("DOM.enable", {}, sessionId);
  await send("CSS.enable", {}, sessionId);
  const ev = async (expression) => { const { result, exceptionDetails } = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true }, sessionId); if (exceptionDetails) throw new Error(exceptionDetails.exception?.description?.split("\n")[0] || exceptionDetails.text); return result.value; };
  await ev("document.fonts.ready.then(() => 1)");
  const { info, durs, eases } = JSON.parse(await ev(BEHAVIOUR_SETUP));
  const { root } = await send("DOM.getDocument", { depth: 0 }, sessionId);
  const { nodeIds } = await send("DOM.querySelectorAll", { nodeId: root.nodeId, selector: "[data-nwb]" }, sessionId);
  const LAYOUT = /\b(all|width|height|inline-size|block-size|margin|padding|inset|top|left|right|bottom)\b/;
  const boxIds = {};
  for (const id of (await send("DOM.querySelectorAll", { nodeId: root.nodeId, selector: "[data-nwbox]" }, sessionId)).nodeIds) {
    const { attributes } = await send("DOM.getAttributes", { nodeId: id }, sessionId);
    for (const k of attributes[attributes.indexOf("data-nwbox") + 1].split(" ")) boxIds[k] = id;
  }
  const force = (nodeId, forcedPseudoClasses) => send("CSS.forcePseudoState", { nodeId, forcedPseudoClasses }, sessionId);
  const snaps = [];
  for (let i = 0; i < info.length; i++) {
    const e = info[i], nodeId = nodeIds[i];
    // motion, read at rest before the freeze
    if (e.prop !== "none" && e.dur.split(",").some((d) => d.trim() !== "0s")) {
      if (LAYOUT.test(e.prop)) out.push({ rule: "motion-tokens", where: e.where, detail: `transitions ${e.prop.slice(0, 60)}` });
      const badDur = e.dur.split(",").map((d) => d.trim()).find((d) => !durs.includes(d));
      if (badDur) out.push({ rule: "motion-tokens", where: e.where, detail: `duration ${badDur} is not a motion token (${durs.filter((d) => d !== "0s").join(", ")})` });
      const ease = e.ease.split(/,(?![^(]*\))/).map((x) => x.trim()).find((x) => !eases.includes(x));
      if (ease) out.push({ rule: "motion-tokens", where: e.where, detail: `easing ${ease.slice(0, 40)} is not a motion token` });
    }
    if (!nodeId) continue;
    const boxId = e.boxed ? boxIds[i] : null, hoverId = boxId || nodeId, snap = () => ev(`__nwSnap(${i}, ${boxId ? "true" : "false"})`);
    const rest = await snap();
    await force(hoverId, ["hover"]); const hover = await snap();
    await force(hoverId, ["hover", "active"]); const press = await snap();
    await force(hoverId, []);
    await force(nodeId, ["focus", "focus-visible"]); if (boxId) await force(boxId, ["focus-within"]);
    const focused = await snap(), ring = JSON.parse(await ev(`__nwRing(${i})`));
    await force(nodeId, []); if (boxId) await force(boxId, []);
    snaps[i] = { rest, hover };
    if (e.disabled) { if (hover !== rest) out.push({ rule: "disabled", where: e.where, detail: "changes on hover while disabled" }); continue; }
    if (!e.on && !e.field && hover === rest && !e.inText && !e.label) out.push({ rule: "hover", where: e.where, detail: "no visible change on hover" });
    if (!e.on && e.state && press === hover) out.push({ rule: "press", where: e.where, detail: "press looks the same as hover" });
    const ringed = ring.outline || /\d/.test(ring.shadow);
    if (e.field ? focused === rest && !ringed : !ringed) out.push({ rule: "focus", where: e.where, detail: e.field ? "no change on focus" : "no ring on focus-visible" });
    if (!e.inText && !e.label && (e.w < 24 || e.h < 24)) {
      // WCAG 2.5.8 spacing exception: a 24px circle on the target's centre touches no other target.
      const dist = (x, y, [l, t, r, b]) => Math.hypot(Math.max(l - x, 0, x - r), Math.max(t - y, 0, y - b));
      const crowded = info.some((o, k) => k !== i && !o.inText && (dist(e.x, e.y, o.rect) < 12 || ((o.w < 24 || o.h < 24) && Math.hypot(o.x - e.x, o.y - e.y) < 24)));
      if (crowded) out.push({ rule: "target", where: e.where, detail: `${e.w.toFixed(0)}×${e.h.toFixed(0)}px with another target within 12px (24×24 minimum, or spacing)` });
    }
  }
  // on-vs-hover: a chosen element against a hovered sibling of the same kind that is not chosen
  for (let i = 0; i < info.length; i++) {
    const e = info[i];
    if (!e.on || e.disabled || !snaps[i]) continue;
    const j = info.findIndex((x, k) => k !== i && !x.on && !x.disabled && x.sig === e.sig && snaps[k]);
    if (j >= 0 && snaps[j].hover === snaps[i].rest) out.push({ rule: "on-vs-hover", where: e.where, detail: "the chosen item looks like a hovered one" });
  }
  await ev(`document.getElementById("nwb-still")?.remove(), 1`);
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] }, sessionId);
  const slow = JSON.parse(await ev(`JSON.stringify([...document.querySelectorAll("[data-nwb]")].filter((e) => getComputedStyle(e).transitionDuration.split(",").some((d) => parseFloat(d) * (d.trim().endsWith("ms") ? 1 : 1000) > 1)).slice(0, 5).map((e) => e.getAttribute("data-nwb")))`));
  for (const i of slow) out.push({ rule: "reduced", where: info[i].where, detail: "still transitions under prefers-reduced-motion: reduce" });
  await send("Emulation.setEmulatedMedia", { features: [] }, sessionId);
  return out;
}

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
    // Break the showcase seventeen ways and confirm the layout, paint and behaviour audits report each rule.
    await send("Emulation.setDeviceMetricsOverride", { width: 768, height: 900, deviceScaleFactor: 1, mobile: false }, sessionId);
    const loaded = once("Page.loadEventFired", sessionId);
    await send("Page.navigate", { url: `${BASE}/site/components.html?audit=layout,paint` }, sessionId);
    await loaded;
    const res = {};
    for (const expr of [SELF_TEST, PAINT_SELF_TEST]) {
      const { result } = await send("Runtime.evaluate", { awaitPromise: true, returnByValue: true, expression: expr }, sessionId);
      Object.assign(res, JSON.parse(result.value));
    }
    const ev = async (expression) => (await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true }, sessionId)).result.value;
    const host = `document.querySelector("#data .p-md.rounded-md")`;
    const BREAKS = {
      hover: `${host}.insertAdjacentHTML("beforeend", '<button id="nwt" class="inline-flex items-center h-control px-control border border-transparent bg-neutral-3"><span>No hover</span></button>')`,
      press: `${host}.insertAdjacentHTML("beforeend", '<button id="nwt" class="inline-flex items-center h-control px-control border border-transparent bg-neutral-3 state"><span>Press</span></button><style id="nwt2">#nwt:active::after{opacity:var(--state-hover)!important}</style>')`,
      focus: `${host}.insertAdjacentHTML("beforeend", '<button id="nwt" class="inline-flex items-center h-control px-control border state bg-neutral-3 outline-none"><span>No ring</span></button><style id="nwt2">#nwt:focus-visible{outline:none!important}</style>')`,
      disabled: `${host}.insertAdjacentHTML("beforeend", '<button id="nwt" disabled class="inline-flex items-center h-control px-control border border-transparent bg-neutral-3 hover:bg-neutral-5"><span>Disabled</span></button>')`,
      "on-vs-hover": `${host}.insertAdjacentHTML("beforeend", '<div id="nwt"><button aria-pressed="true" class="inline-flex items-center h-control px-control border-0 bg-transparent hover:bg-neutral-4 pressed:bg-neutral-4"><span>A</span></button><button aria-pressed="false" class="inline-flex items-center h-control px-control border-0 bg-transparent hover:bg-neutral-4 pressed:bg-neutral-4"><span>B</span></button></div>')`,
      target: `${host}.insertAdjacentHTML("beforeend", '<div id="nwt" class="flex"><button class="state bg-neutral-3" style="width:12px;height:12px" aria-label="a"></button><button class="state bg-neutral-3" style="width:12px;height:12px" aria-label="b"></button></div>')`,
      "motion-tokens": `${host}.insertAdjacentHTML("beforeend", '<button id="nwt" class="inline-flex items-center h-control px-control border state bg-neutral-3"><span>Slow</span></button><style id="nwt2">#nwt{transition-duration:333ms!important}</style>')`,
      reduced: `${host}.insertAdjacentHTML("beforeend", '<button id="nwt" class="inline-flex items-center h-control px-control border state bg-neutral-3" style="transition-duration:160ms !important"><span>Moves</span></button>')`,
    };
    const navd = once("Page.loadEventFired", sessionId);
    await send("Page.navigate", { url: `${BASE}/site/components.html` }, sessionId);
    await navd;
    const base = new Set((await behaviourPage(send, sessionId)).map((f) => f.rule));
    for (const [rule, js] of Object.entries(BREAKS)) {
      if (base.has(rule)) { res[rule] = "already reported before the break"; continue; }
      await ev(js);
      const got = (await behaviourPage(send, sessionId)).some((f) => f.rule === rule);
      await ev(`document.getElementById("nwt")?.remove(); document.getElementById("nwt2")?.remove(); 1`);
      res[rule] = got ? "caught" : "missed";
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
        if (DOMAINS[domain].custom) {
          for (const f of await behaviourPage(send, sessionId)) findings.push({ domain, audit: "behaviour", page, width, root: rootSize, ...f });
          done++;
          if (process.stdout.isTTY) process.stdout.write(`\rreview ${domain}: ${done}/${total}`);
          continue;
        }
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
  process.exit(args.includes("--strict") && findings.length ? 1 : 0);
}
main().catch((e) => { console.error(`review: ${e.message}`); process.exit(1); });
