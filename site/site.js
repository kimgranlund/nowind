// Site search: ⌘K or Ctrl+K (or "/") opens a command palette over every page, block heading, component and class.
// The index, search.json beside this script, is written by scripts/templates.py and loaded on first open. Results come
// in groups (pages, components, sections, classes), one line each; Tab cycles the filter, ↑↓ move, Enter opens.
(() => {
  const base = new URL(".", document.currentScript.src);
  const KINDS = { Page: "ph-file-text", Section: "ph-hash", Component: "ph-squares-four", Pattern: "ph-stack", Block: "ph-layout", Class: "ph-brackets-curly" };
  const GROUPS = [["Page", "Pages"], ["Component", "Components"], ["Pattern", "Patterns"], ["Block", "Blocks"], ["Section", "Sections"], ["Class", "Classes"]];
  const FILTERS = [["", "All"], ...GROUPS.map(([k, n]) => [k, n])];
  const KEY = "inline-flex items-center justify-center h-nested min-w-nested px-2xs rounded-xs border text-mono-sm";
  let rows = null, hits = [], active = 0, filter = "";

  const dialog = document.createElement("dialog");
  dialog.setAttribute("aria-label", "Search Nowind");
  dialog.className = "w-full max-w-measure h-command m-auto p-0 rounded-lg bg fg border shadow-xl";
  dialog.innerHTML = `
    <div class="flex flex-col h-full">
      <div class="flex items-center gap-gutter ps-md pe-xs py-xs">
        <i class="icon ph ph-magnifying-glass fg-weak"></i>
        <input type="text" role="combobox" aria-expanded="true" aria-controls="search-results" aria-autocomplete="list"
          placeholder="Search pages, components and classes" aria-label="Search"
          class="grow min-w-0 p-0 border-0 bg-transparent fg text-lg outline-0">
        <button type="button" aria-label="Close" class="inline-flex items-center justify-center size-control shrink-0 rounded-sm border border-transparent bg-transparent state fg-weak cursor-pointer"><i class="icon ph ph-x"></i></button>
      </div>
      <div role="group" aria-label="Filter" class="flex flex-wrap items-center gap-3xs px-md pb-xs border-b">
        ${FILTERS.map(([k, n]) => `<button type="button" data-filter="${k}" aria-pressed="${k === ""}" class="inline-flex items-center h-nested px-nested rounded-sm border border-transparent bg-transparent state text-sm fg-weak pressed:bg-component pressed:fg cursor-pointer"><span>${n}</span></button>`).join("")}
      </div>
      <ul id="search-results" role="listbox" aria-label="Results" class="list-none px-xs py-inset flex flex-col grow min-h-0 overflow-y-auto"></ul>
      <div class="flex flex-wrap items-center gap-md px-md py-xs border-t text-sm fg-weak">
        <span class="inline-flex items-center gap-3xs"><kbd class="${KEY}">↑</kbd><kbd class="${KEY}">↓</kbd><span>Navigate</span></span>
        <span class="inline-flex items-center gap-3xs"><kbd class="${KEY}">↵</kbd><span>Open</span></span>
        <span class="inline-flex items-center gap-3xs"><kbd class="${KEY}">Tab</kbd><span>Filter</span></span>
        <span class="inline-flex items-center gap-3xs"><kbd class="${KEY}">Esc</kbd><span>Close</span></span>
        <span class="ms-auto" aria-live="polite"></span>
      </div>
    </div>`;
  document.body.append(dialog);
  const input = dialog.querySelector("input"), list = dialog.querySelector("ul"), status = dialog.querySelector("[aria-live]");
  const filters = [...dialog.querySelectorAll("[data-filter]")];

  const esc = (t) => t.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  function score(r, q, words) {
    const t = r[0].toLowerCase(), d = (r[3] || "").toLowerCase();
    if (!words.every((w) => t.includes(w) || d.includes(w))) return 0;
    let s = 1;
    if (t === q || t === "." + q) s += 100;
    else if (t.startsWith(q) || t.startsWith("." + q)) s += 50;
    else if (t.includes(q)) s += 20;
    s += { Page: 8, Component: 6, Pattern: 6, Block: 6, Section: 4, Class: 0 }[r[2]];
    return s - t.length / 100;
  }

  const row = (r, i, sub) => `<li role="option" id="search-${i}" aria-selected="${i === active}">
      <a href="${new URL(r[1], base)}" tabindex="-1" aria-selected="${i === active}" class="flex items-center gap-gutter h-control px-control rounded-sm no-underline fg hover:bg-component-weak selected:bg-component">
        <i class="icon ph ${KINDS[r[2]]} fg-weak"></i>
        <span class="grow min-w-0 truncate ${r[2] === "Class" ? "text-mono-sm" : "text-body-md"}">${esc(r[0])}</span>
        ${sub ? `<span class="shrink-0 truncate text-sm fg-weak">${esc(sub)}</span>` : ""}
        <i class="icon icon-sm ph ph-arrow-elbow-down-left fg-weak ${i === active ? "" : "invisible"}" aria-hidden="true"></i>
      </a></li>`;

  function render() {
    const q = input.value.trim().toLowerCase();
    if (!rows) { status.textContent = "Loading…"; return; }
    const pool = filter ? rows.filter((r) => r[2] === filter) : rows;
    // No query: the site map, pages grouped by section. A query: hits grouped by kind, in the order each kind's best hit
    // ranks, keeping the ranking inside a group.
    let groups;
    if (!q && !filter) {
      const pages = rows.filter((r) => r[2] === "Page");
      groups = [...new Set(pages.map((r) => r[3]))].map((g) => [g, pages.filter((r) => r[3] === g), () => ""]);
    } else {
      const words = q.split(/\s+/);
      const found = !q ? pool.slice(0, 60) : pool.map((r) => [score(r, q, words), r]).filter(([sc]) => sc > 0).sort((a, b) => b[0] - a[0]).slice(0, 60).map(([, r]) => r);
      groups = [...new Set(found.map((r) => r[2]))].map((k) => [GROUPS.find(([g]) => g === k)[1], found.filter((r) => r[2] === k), (r) => r[2] === "Component" || r[2] === "Pattern" || r[2] === "Block" ? "" : r[3]]);
    }
    hits = groups.flatMap(([, rs]) => rs);
    active = 0;
    let i = 0;
    list.innerHTML = groups.map(([name, rs, sub]) => (filter ? "" : `<li role="presentation" class="px-control pt-xs pb-3xs text-sm fg-weak">${esc(name)}</li>`) + rs.map((r) => row(r, i++, sub(r))).join("")).join("")
      || `<li role="presentation" class="px-control py-md text-body-md fg-weak">No results for “${esc(input.value.trim())}”</li>`;
    input.setAttribute("aria-activedescendant", hits.length ? "search-0" : "");
    status.textContent = q ? `${hits.length === 60 ? "First 60" : hits.length} results` : `${rows.length} entries`;
  }

  function move(d) {
    if (!hits.length) return;
    const set = (n, on) => { const li = list.querySelector(`#search-${n}`); li.setAttribute("aria-selected", on); li.firstElementChild.setAttribute("aria-selected", on); li.querySelector(".ph-arrow-elbow-down-left").classList.toggle("invisible", !on); return li; };
    set(active, false);
    active = (active + d + hits.length) % hits.length;
    set(active, true).scrollIntoView({ block: "nearest" });
    input.setAttribute("aria-activedescendant", `search-${active}`);
  }

  function setFilter(k) {
    filter = k;
    filters.forEach((b) => b.setAttribute("aria-pressed", b.dataset.filter === k));
    render();
  }

  async function open() {
    if (dialog.open) return;
    dialog.showModal();
    input.select();
    if (!rows) {
      render();
      try { rows = await (await fetch(new URL("search.json", base))).json(); }
      catch { status.textContent = "The index didn't load. Open the site through a web server, not from a file."; return; }
    }
    render();
  }

  input.addEventListener("input", render);
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
    else if (e.key === "Tab") { e.preventDefault(); const n = FILTERS.findIndex(([k]) => k === filter); setFilter(FILTERS[(n + (e.shiftKey ? -1 : 1) + FILTERS.length) % FILTERS.length][0]); }
    else if (e.key === "Enter" && hits[active]) { e.preventDefault(); location.href = new URL(hits[active][1], base); dialog.close(); }
  });
  filters.forEach((b) => b.addEventListener("click", () => { setFilter(b.dataset.filter); input.focus(); }));
  dialog.querySelector('[aria-label="Close"]').addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
  document.addEventListener("keydown", (e) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
    if ((e.key === "k" && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !typing)) { e.preventDefault(); open(); }
  });
  document.querySelectorAll("[data-search-open]").forEach((b) => b.addEventListener("click", open));
})();

// The lens, after Apple's Liquid Glass: each .lens element gets its own displacement map, drawn at its size and corner
// radius. A pixel inside the rim band shows the backdrop from further in, along the edge's inward normal, by an amount
// that grows towards the edge (a convex rim); the centre is untouched. Red, green and blue bend by slightly different
// amounts, so the rim fringes. Only Chromium applies an SVG filter in backdrop-filter, so the lens runs there, and not
// when the reader asks for less transparency; elsewhere glass keeps its blur. Elements marked data-lens-label say which.
(() => {
  const chromium = navigator.userAgentData?.brands?.some((b) => /Chromium/.test(b.brand)) || (/Chrome\//.test(navigator.userAgent) && !/CriOS/.test(navigator.userAgent));
  const on = chromium && !matchMedia("(prefers-reduced-transparency: reduce)").matches;
  document.documentElement.dataset.lens = on ? "on" : "off";
  document.querySelectorAll("[data-lens-label]").forEach((el) => { el.textContent = on ? "Lens on" : "Lens off: this browser can't refract, so glass shows its blur"; });
  if (!on) return;

  const NS = "http://www.w3.org/2000/svg";
  const host = document.createElementNS(NS, "svg");
  host.setAttribute("width", "0"); host.setAttribute("height", "0"); host.setAttribute("aria-hidden", "true");
  host.style.position = "absolute";
  document.body.append(host);
  let n = 0;

  function map(w, h, r, band, shift) {
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    const ctx = c.getContext("2d"), img = ctx.createImageData(w, h), d = img.data;
    const hx = w / 2, hy = h / 2;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const px = x + 0.5 - hx, py = y + 0.5 - hy;
      const qx = Math.abs(px) - (hx - r), qy = Math.abs(py) - (hy - r);
      let dist, nx, ny;
      if (qx > 0 && qy > 0) { const l = Math.hypot(qx, qy) || 1; dist = l - r; nx = qx / l; ny = qy / l; }
      else if (qx > qy) { dist = qx - r; nx = 1; ny = 0; } else { dist = qy - r; nx = 0; ny = 1; }
      const depth = -dist, s = Math.min(Math.max(depth / band, 0), 1);
      // Refraction through a rounded-sm glass edge: the surface is a quarter circle across the band, and the bend follows
      // its slope, steep at the rim and easing towards the flat centre.
      const z = Math.sqrt(Math.max(1 - (1 - s) * (1 - s), 1e-4));
      const m = depth > 0 && s < 1 ? Math.min(((1 - s) / z) * 0.35, 1) : 0;
      // feDisplacementMap reads the backdrop at p + scale·(map − ½), so a negative offset towards the centre shows the
      // backdrop from further in: the rim bends inward and the whole body magnifies slightly (6%), as a thick lens does.
      const zoom = 0.06 / shift;
      const dx = Math.max(-1, Math.min(1, -Math.sign(px) * nx * m - px * zoom)), dy = Math.max(-1, Math.min(1, -Math.sign(py) * ny * m - py * zoom));
      const i = (y * w + x) * 4;
      d[i] = 128 + 127 * dx; d[i + 1] = 128 + 127 * dy; d[i + 2] = 128; d[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    return c.toDataURL();
  }

  function build(el) {
    const w = Math.round(el.offsetWidth), h = Math.round(el.offsetHeight);
    if (!w || !h) return;
    const r = Math.min(parseFloat(getComputedStyle(el).borderTopLeftRadius) || 0, w / 2, h / 2);
    const band = Math.max(Math.min(Math.max(r, 16), 0.32 * Math.min(w, h)), 6);
    const shift = Math.min(band * 0.7, 28);
    const id = el.dataset.lensId || (el.dataset.lensId = `nowind-lens-${++n}`);
    let f = host.querySelector(`#${id}`);
    if (!f) { f = document.createElementNS(NS, "filter"); f.id = id; host.append(f); }
    for (const [k, v] of Object.entries({ x: 0, y: 0, width: w, height: h, filterUnits: "userSpaceOnUse", primitiveUnits: "userSpaceOnUse", "color-interpolation-filters": "sRGB" })) f.setAttribute(k, v);
    const disp = (k, res) => `<feDisplacementMap in="SourceGraphic" in2="map" scale="${(2 * shift * k).toFixed(2)}" xChannelSelector="R" yChannelSelector="G" result="${res}"/>`;
    f.innerHTML = `<feImage href="${map(w, h, r, band, shift)}" x="0" y="0" width="${w}" height="${h}" preserveAspectRatio="none" result="map"/>`
      + disp(1, "dr") + disp(1.06, "dg") + disp(1.12, "db")
      + `<feColorMatrix in="dr" values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0" result="cr"/>`
      + `<feColorMatrix in="dg" values="0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0" result="cg"/>`
      + `<feColorMatrix in="db" values="0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0" result="cb"/>`
      + `<feBlend in="cr" in2="cg" mode="screen" result="rg"/><feBlend in="rg" in2="cb" mode="screen"/>`;
    el.style.setProperty("--_lens-filter", `url(#${id})`);
  }

  const seen = new WeakMap();
  const ro = new ResizeObserver((entries) => entries.forEach((e) => {
    const k = `${Math.round(e.target.offsetWidth)}x${Math.round(e.target.offsetHeight)}`;
    if (seen.get(e.target) !== k) { seen.set(e.target, k); build(e.target); }
  }));
  document.querySelectorAll(".lens").forEach((el) => ro.observe(el));
})();

// Glass slider demo: a range input drives a glass thumb over a track.
document.querySelectorAll("[data-glass-slider]").forEach((box) => {
  const input = box.querySelector("input[type=range]"), thumb = box.querySelector("[data-thumb]"), fill = box.querySelector("[data-fill]");
  const place = () => {
    const t = (input.value - input.min) / (input.max - input.min), track = box.querySelector("[data-track]");
    const x = t * track.offsetWidth;
    fill.style.width = `${x}px`;
    thumb.style.marginLeft = `${track.offsetLeft + x - thumb.offsetWidth / 2}px`;
  };
  input.addEventListener("input", place);
  new ResizeObserver(place).observe(box);
  place();
});

// Display settings: the band's panel sets the theme (light, dark or the system's), the root font size (12 to 18px) and
// the tier (until one is chosen each region keeps its own and the panel shows the main region's; product, content or
// brand applies one to the main region and every example frame, the tiers demo excepted). Each is remembered; the head script applies the theme and size before paint.
(() => {
  const root = document.documentElement, media = matchMedia("(prefers-color-scheme: dark)");
  const store = (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch {} };
  const read = (k) => { try { return localStorage.getItem(k); } catch { return null; } };
  const targets = [...document.querySelectorAll("#content, .tier-product, .tier-content, .tier-brand")].filter((e) => !e.closest("[data-semantic-demo], .text-chrome"));
  targets.forEach((e) => { e.dataset.tierDefault = (e.className.match(/\btier-(product|content|brand)\b/) || [, ""])[1]; });
  const state = {
    theme: read("nowind-color-mode") || "system",
    size: String(Math.round(parseFloat(getComputedStyle(root).fontSize))),
    tier: read("nowind-tier") || (document.getElementById("content")?.dataset.tierDefault) || "product",
  };
  const apply = {
    theme(v) { if (v === "system") delete root.dataset.colorMode; else root.dataset.colorMode = v; store("nowind-color-mode", v === "system" ? null : v); },
    size(v) { root.style.fontSize = `${v}px`; store("nowind-root-size", v); },
    tier(v) {
      targets.forEach((e) => {
        e.classList.remove("tier-product", "tier-content", "tier-brand");
        e.classList.add(`tier-${v}`);
      });
      store("nowind-tier", v);
    },
  };
  const show = () => document.querySelectorAll("[data-setting]").forEach((b) => b.setAttribute("aria-pressed", String(state[b.dataset.setting] === b.dataset.value)));
  document.querySelectorAll("[data-setting]").forEach((b) => b.addEventListener("click", () => {
    state[b.dataset.setting] = b.dataset.value;
    apply[b.dataset.setting](b.dataset.value);
    show();
  }));
  if (read("nowind-tier")) apply.tier(state.tier);
  media.addEventListener("change", show);
  show();
})();

// Audits: ?audit= takes one name or a comma list (type, geometry, layout); "form" runs all three.
window.nowindAudits = () => (new URLSearchParams(location.search).get("audit") || "").split(",").flatMap((a) => a === "form" ? ["type", "geometry", "layout"] : [a]);
// A page whose own stylesheet carries data-page-css (the specimen) is outside Nowind's class rules: the audits check only its page overflow.
window.nowindOwnCSS = () => !!document.querySelector("style[data-page-css]");

// Type audit (open any page with ?audit=type): checks the rendered examples against the size contract's three rules
// (sizeContract.rules in theme/theme.type-roles.manifest.json) and logs what breaks them; window.nowindTypeAudit holds
// the list. Rows: text side by side shares a size, unless one side is a control, figure, badge, keycap or kicker.
// Order: within a surface, title >= body >= supporting, and a dialog title is larger than its buttons. Icons: an icon
// takes the step of the text beside it (icon-sm with text-sm, icon with text-base, icon-lg with a title).
(() => {
  if (!window.nowindAudits().includes("type")) return;
  const run = () => {
    const out = [];
    if (window.nowindOwnCSS()) { window.nowindTypeAudit = out; return out; }
    const px = (el) => parseFloat(getComputedStyle(el).fontSize);
    const F = (el) => parseFloat(getComputedStyle(el).getPropertyValue("--F")) || px(el);
    const where = (el) => { const s = el.closest("section[id]"); return `#${s ? s.id : "?"} ${el.tagName.toLowerCase()}.${[...el.classList].slice(0, 4).join(".")} “${el.textContent.trim().slice(0, 28)}”`; };
    const isControl = (el) => el.matches("a, button, select, input, textarea, summary, [role=tab], [role=option], [role=menuitem], .h-control, .h-nested, .size-control, .size-nested");
    const isMark = (el) => el.matches("kbd, .rounded-full, .font-display, .uppercase") || !!el.closest("kbd, .rounded-full");
    const ownText = (el) => [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    const texty = (el) => !el.matches(".icon") && el.textContent.trim() && (ownText(el) || el.children.length === 1 && ownText(el.children[0]));
    const scope = [...document.querySelectorAll("main section[id]")].filter((s) => !s.matches("[data-semantic-demo]"));
    const frames = [...document.querySelectorAll("[data-example]")];
    const inScope0 = frames.length ? (el) => !!el.closest("[data-example]") : (el) => scope.some((s) => s.contains(el)) && !el.closest("[data-semantic-demo]");
    const inScope = (el) => inScope0(el) && !el.closest(".scope");
    // 1. Rows
    for (const row of document.querySelectorAll("main *")) {
      if (!inScope(row)) continue;
      const cs = getComputedStyle(row);
      if (!cs.display.includes("flex") || cs.flexDirection !== "row" || cs.alignItems === "baseline" || isControl(row) || row.closest("button, a, summary, [role=option], [role=menuitem]")) continue;
      const kids = [...row.children].filter((k) => texty(k) && !isControl(k) && !isMark(k) && getComputedStyle(k).display !== "none");
      const sizes = [...new Set(kids.map((k) => px(k).toFixed(1)))];
      if (kids.length > 1 && sizes.length > 1) out.push({ rule: "row", where: where(row), detail: kids.map((k) => `${px(k).toFixed(1)}px “${k.textContent.trim().slice(0, 16)}”`).join(" | ") });
    }
    // 2. Order within a surface
    const surfaces = [...document.querySelectorAll("main dialog, main [role=dialog], main [role=status], main [role=alert], main article, main .rounded-md.border, main .rounded-lg")].filter((e) => inScope(e) && !e.matches("[data-example]"));
    for (const s of surfaces) {
      const title = s.querySelector("h1, h2, h3, h4, .font-semibold");
      const body = [...s.querySelectorAll("p")].find((p) => !p.closest("button"));
      const btn = s.querySelector("button .text-base, button:not(:has(.icon:only-child))");
      if (title && body && px(title) < px(body)) out.push({ rule: "order", where: where(s), detail: `title ${px(title).toFixed(1)}px < body ${px(body).toFixed(1)}px` });
      if (s.matches("dialog, [role=dialog]") && title && btn && px(title) <= px(btn)) out.push({ rule: "order", where: where(s), detail: `dialog title ${px(title).toFixed(1)}px <= button ${px(btn).toFixed(1)}px` });
      const muted = [...s.querySelectorAll("p, span")].filter((e) => [...e.classList].some((c) => /^fg-[a-z]+(-\d)?-(8|11)$/.test(c)) && ownText(e) && !e.closest("button, kbd, .rounded-full"));
      for (const m of muted) if (body && m !== body && px(m) > px(body)) out.push({ rule: "order", where: where(m), detail: `supporting ${px(m).toFixed(1)}px > body ${px(body).toFixed(1)}px` });
    }
    // 3. Icons pair with the text beside them
    for (const i of document.querySelectorAll("main .icon")) {
      if (!inScope(i) || i.matches(".caret, [class*=ph-caret-]")) continue;
      const host = i.closest("button, a, summary, [role=option], [role=menuitem]");
      if (host && host.matches(".h-nested, .size-nested, .h-full, .btn-sm, .segment") && i.matches(".icon-sm")) continue;
      const near = [i.nextElementSibling, i.previousElementSibling].find((n) => n && texty(n));
      if (!near) continue;
      const r = px(near) / F(near);
      const bold = parseInt(getComputedStyle(near).fontWeight) >= 600;
      const want = r < 0.92 ? "icon-sm" : bold && near.matches("h1, h2, h3, h4, .font-semibold") && i.matches(".icon-lg") ? "icon-lg" : "icon";
      const has = i.matches(".icon-sm") ? "icon-sm" : i.matches(".icon-lg") ? "icon-lg" : "icon";
      if (has !== want) out.push({ rule: "icon", where: where(i.parentElement), detail: `${has} beside ${px(near).toFixed(1)}px text (want ${want})` });
    }
    window.nowindTypeAudit = out;
    console.log(`Type audit: ${out.length} finding(s)`);
    if (out.length) console.table(out);
    return out;
  };
  window.addEventListener("load", run);
  window.nowindRunTypeAudit = run;
})();

// Geometry audit (open any page with ?audit=geometry): measures the rendered examples against the geometry contract's
// rules (geometryContract.rules in theme/theme.geometry.manifest.json) and logs what breaks them; window.nowindGeometryAudit
// holds the list. Nesting: a part tucked into a rounded container's corner has that radius less its offset. Insets: a
// part at a container's end sits the same distance from each edge it faces. Edges: no text within 2px of a painted box's
// edge. Heights: controls side by side share a height. Shape: squares and circles are square. Clipping: no clipping box
// hides its content.
(() => {
  if (!window.nowindAudits().includes("geometry")) return;
  const run = () => {
    const out = [];
    if (window.nowindOwnCSS()) { window.nowindGeometryAudit = out; return out; }
    const R = (e) => e.getBoundingClientRect();
    const cs = (e) => getComputedStyle(e);
    const px = (v) => parseFloat(v) || 0;
    const frames = [...document.querySelectorAll("[data-example]")];
    const sections = [...document.querySelectorAll("main section[id]")].filter((s) => !s.matches("[data-semantic-demo]"));
    const inScope = (el) => (frames.length ? !!el.closest("[data-example]") : sections.some((s) => s.contains(el)) && !el.closest("[data-semantic-demo]")) && !el.closest(".scope");
    const where = (el) => { const s = el.closest("section[id]"); return `#${s ? s.id : "?"} ${el.tagName.toLowerCase()}.${[...el.classList].slice(0, 5).join(".")} “${el.textContent.trim().slice(0, 24)}”`; };
    const radius = (e) => { const r = R(e); return Math.min(px(cs(e).borderTopLeftRadius), r.width / 2, r.height / 2); };
    const painted = (e) => { const c = cs(e); return (c.backgroundColor !== "rgba(0, 0, 0, 0)" && c.backgroundColor !== "transparent") || (["Top", "Right", "Bottom", "Left"].every((sd) => px(c[`border${sd}Width`]) > 0) && c.borderTopColor !== "rgba(0, 0, 0, 0)"); };
    const all = [...document.querySelectorAll("main *")].filter((e) => inScope(e) && cs(e).display !== "none" && R(e).width > 0);
    for (const e of all) {
      const c = cs(e), r = R(e);
      // Nesting: e tucked into the corner of its nearest painted, rounded ancestor.
      if (radius(e) > 0 && painted(e) && !(Math.abs(r.width - r.height) < 1 && radius(e) >= r.width / 2 - 0.5)) {
        let a = e.parentElement;
        while (a && !(radius(a) > 0 && painted(a))) a = a.parentElement;
        if (a && inScope(a)) {
          const ar = R(a), ra = radius(a), bw = px(cs(a).borderTopWidth);
          const corners = [[r.top - ar.top, r.left - ar.left], [r.top - ar.top, ar.right - r.right], [ar.bottom - r.bottom, r.left - ar.left], [ar.bottom - r.bottom, ar.right - r.right]];
          for (const [dy, dx] of corners) {
            if (Math.abs(dy - dx) < 1 && dy < ra && dy >= 0) {
              const want = Math.max(0, ra - dy), have = radius(e);
              if (Math.abs(have - want) > 1.5) out.push({ rule: "nesting", where: where(e), detail: `radius ${have.toFixed(1)}px in a ${ra.toFixed(1)}px corner ${dy.toFixed(1)}px in (want ${want.toFixed(1)}px)` });
              break;
            }
          }
        }
      }
      // Insets: a sized part at the end of a rounded flex row container faces three edges evenly.
      const p = e.parentElement;
      if (p && e === p.lastElementChild && e.matches(".size-nested, .size-control, .h-full, kbd") && !e.matches("input, select, textarea") && !(p.firstElementChild && Math.abs(R(p.firstElementChild).top - r.top) > r.height / 2) && radius(p) > 0 && cs(p).display.includes("flex") && cs(p).flexDirection === "row" && painted(p)) {
        const pr = R(p), bw = px(cs(p).borderTopWidth);
        const centred = cs(p).alignItems === "center" || cs(p).alignItems === "normal";
        const gaps = centred ? [r.top - pr.top - bw, pr.bottom - r.bottom - bw, pr.right - r.right - bw] : [r.top - pr.top - bw, pr.right - r.right - bw];
        if (Math.max(...gaps) - Math.min(...gaps) > 1.5) out.push({ rule: "insets", where: where(e), detail: gaps.map((g) => g.toFixed(1) + "px").join(", ") });
      }
      // Edges: text whose nearest painted box is e sits clear of e's sides.
      if (painted(e) && !/auto|scroll/.test(c.overflowX) && !e.matches("input, textarea, select, option, code, kbd, progress, meter, .rounded-full.size-nested, .rounded-full.size-control")) {
        const walker = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
        for (let n = walker.nextNode(); n; n = walker.nextNode()) {
          if (!n.textContent.trim()) continue;
          let host = n.parentElement;
          while (host && host !== e && !painted(host)) host = host.parentElement;
          if (host !== e || n.parentElement.closest("code, kbd, input, select, textarea, .truncate") || (() => { for (let a = n.parentElement; a && a !== e; a = a.parentElement) if (/auto|scroll/.test(cs(a).overflowX)) return true; return false; })()) continue;
          const rg = document.createRange(); rg.selectNodeContents(n); const t = rg.getBoundingClientRect();
          if (!t.width) continue;
          const s0 = t.left - r.left - px(c.borderLeftWidth), en = r.right - t.right - px(c.borderRightWidth);
          const floor = (pad) => pad < 0.5 ? 2 : Math.min(2, pad) - 0.75;  // no padding: keep 2px; tiny padding by geometry: the padding itself
          const padOf = (side) => { let m = 0; for (let a = n.parentElement; a; a = a.parentElement) { m = Math.max(m, px(cs(a)[side])); if (a === e) break; } return m; };
          if (s0 < floor(padOf("paddingInlineStart")) || en < floor(padOf("paddingInlineEnd"))) { out.push({ rule: "edges", where: where(e), detail: `text ${s0.toFixed(1)}px from the start, ${en.toFixed(1)}px from the end` }); break; }
        }
      }
      // Shape: squares and circles.
      if (e.matches(".aspect-square, .size-nested, .size-control") && Math.abs(r.width - r.height) > 1) out.push({ rule: "shape", where: where(e), detail: `${r.width.toFixed(1)}×${r.height.toFixed(1)}px` });
      // Clipping.
      if (c.overflow === "hidden" || c.overflowY === "hidden") {
        if (e.scrollHeight > e.clientHeight + 1 || (e.scrollWidth > e.clientWidth + 1 && c.textOverflow !== "ellipsis")) out.push({ rule: "clipping", where: where(e), detail: `content ${e.scrollWidth}×${e.scrollHeight} in ${e.clientWidth}×${e.clientHeight}` });
      }
      // Heights: full-size controls side by side.
      if (c.display.includes("flex") && c.flexDirection === "row" && !e.matches(".flex-wrap")) {
        const ctrls = [...e.children].filter((k) => k.matches(".h-control, .size-control") && !k.matches(".rounded-full.size-control:not(button, a, input)"));  // an avatar holding initials grows to fit them, so a group may differ
        const hs = [...new Set(ctrls.map((k) => Math.round(R(k).height)))];
        if (hs.length > 1) out.push({ rule: "heights", where: where(e), detail: `controls at ${hs.join(", ")}px` });
      }
    }
    window.nowindGeometryAudit = out;
    console.log(`Geometry audit: ${out.length} finding(s)`);
    if (out.length) console.table(out);
    return out;
  };
  window.addEventListener("load", run);
  window.nowindRunGeometryAudit = run;
})();

// Layout audit (open any page with ?audit=layout): measures the page against the layout contract (layoutContract in
// theme/theme.geometry.manifest.json) and the alignment contract (alignmentContract in theme/theme.type-roles.manifest.json);
// window.nowindLayoutAudit holds the list. It covers the whole page, chrome included. Baselines and centring come from
// the font's own metrics (canvas measureText), so they hold for any face.
(() => {
  if (!window.nowindAudits().includes("layout")) return;
  const run = () => {
    const out = [];
    const R = (e) => e.getBoundingClientRect();
    const cs = (e) => getComputedStyle(e);
    const px = (v) => parseFloat(v) || 0;
    const where = (el) => { const s = el.closest("section[id], header, footer, [data-example]"); const tag = s ? (s.id ? `#${s.id}` : s.tagName.toLowerCase()) : "?"; return `${tag} ${el.tagName.toLowerCase()}.${[...el.classList].slice(0, 5).join(".")} “${el.textContent.trim().replace(/\s+/g, " ").slice(0, 24)}”`; };
    const visible = (e) => { const c = cs(e); return c.display !== "none" && c.visibility !== "hidden" && R(e).width > 0; };
    const skip = (e) => !!e.closest(".scope, [data-semantic-demo], dialog:not([open]), [popover]:not(:popover-open), script, style, template, svg, pre");
    const ctx = document.createElement("canvas").getContext("2d");
    const metrics = (el) => { const c = cs(el); ctx.font = `${c.fontStyle} ${c.fontWeight} ${c.fontSize} ${c.fontFamily}`; const m = ctx.measureText("H"); return { asc: m.fontBoundingBoxAscent, desc: m.fontBoundingBoxDescent, cap: m.actualBoundingBoxAscent }; };
    const firstText = (el) => { const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); for (let n = w.nextNode(); n; n = w.nextNode()) if (n.textContent.trim() && !n.parentElement.closest(".icon, [aria-hidden=true], .sr-only, select, option, datalist, template")) return n; return null; };
    const lineRect = (n) => { const rg = document.createRange(); rg.selectNodeContents(n); return rg.getClientRects()[0]; };
    const baseline = (n) => { const r = lineRect(n); return r ? r.top + metrics(n.parentElement).asc : null; };
    const isControl = (e) => e.matches("button, a.h-control, a.size-control, select, input, textarea, summary, .h-control, .h-nested, .size-control, .size-nested, [role=tab], [role=option], [role=menuitem]");
    // page-overflow
    const sw = document.scrollingElement.scrollWidth, vw = document.documentElement.clientWidth;
    if (sw > vw + 1) {
      const wide = [...document.querySelectorAll("body *")].filter((e) => visible(e) && R(e).right > vw + 1 && !e.closest("[class*=overflow-x-auto], [class*=overflow-auto], [class*=overflow-hidden], dialog:not([open]), [popover]:not(:popover-open)")).sort((a, b) => R(b).right - R(a).right);
      out.push({ rule: "page-overflow", where: wide[0] ? where(wide[0]) : "document", detail: `page ${sw}px wide in a ${vw}px viewport` });
    }
    const all = window.nowindOwnCSS() ? [] : [...document.querySelectorAll("body *")].filter((e) => !skip(e) && visible(e));
    for (const e of all) {
      const c = cs(e), r = R(e);
      // text-overflow: own text spilling past its box, where the box neither scrolls nor truncates.
      if ([...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()) && c.overflowX === "visible" && c.textOverflow !== "ellipsis" && !e.matches("input, textarea, select, option, code, kbd, .size-control, .size-nested") && !e.closest("[class*=overflow-x-auto], [class*=overflow-auto], .truncate")) {
        for (const n of e.childNodes) {
          if (n.nodeType !== 3 || !n.textContent.trim()) continue;
          const rg = document.createRange(); rg.selectNodeContents(n);
          const t = rg.getBoundingClientRect();
          if (t.width && t.right > r.right - px(c.paddingRight) - px(c.borderRightWidth) + 1.5 && c.display !== "inline") { out.push({ rule: "text-overflow", where: where(e), detail: `text ends ${(t.right - r.right).toFixed(1)}px past the box` }); break; }
        }
      }
      // padding-symmetry: a painted box with uneven inline padding and nothing at the short edge to explain it.
      const bg = c.backgroundColor !== "rgba(0, 0, 0, 0)" && c.backgroundColor !== "transparent";
      const ps = px(c.paddingInlineStart), pe = px(c.paddingInlineEnd);
      if (bg && Math.abs(ps - pe) > 1.5 && !e.matches("input, textarea, select, option, td, th, html, body, main, header, footer")) {
        const kids = [...e.children].filter(visible);
        const shortStart = ps < pe, edge = shortStart ? kids[0] : kids[kids.length - 1];
        const explained = edge && (edge.matches(".icon, .h-nested, .size-nested, .size-control, .h-full:not(input, textarea, select), .rounded-full, input, kbd, img, svg") || !!edge.querySelector(":scope > .icon:only-child"));
        if (!explained) out.push({ rule: "padding-symmetry", where: where(e), detail: `start ${ps.toFixed(1)}px, end ${pe.toFixed(1)}px` });
      }
      // baseline: text children side by side in a row, centred rather than baseline-aligned.
      if (c.display.includes("flex") && c.flexDirection === "row" && !isControl(e) && !e.closest("button, a, summary, [role=option], [role=menuitem]")) {
        const oneLine = (k) => { const n = firstText(k); return R(k).height < 1.6 * (px(cs(n.parentElement).lineHeight) || px(cs(n.parentElement).fontSize) * 1.5); };
        const kids = [...e.children].filter((k) => visible(k) && !k.matches(".icon, img, svg, input, select, textarea, progress, meter") && !isControl(k) && firstText(k) && !firstText(k).parentElement.closest("button, a, select, summary, [role=option], [role=menuitem], .h-control, .h-nested, .size-control, .size-nested") && oneLine(k));
        const lines = kids.map((k) => { const n = firstText(k); return { k, b: baseline(n), size: cs(n.parentElement).fontSize, fam: cs(n.parentElement).fontFamily, top: R(k).top }; }).filter((x) => x.b !== null);
        const same = (a, b) => Math.abs(R(a.k).top - R(b.k).top) < R(a.k).height && Math.abs(R(a.k).top - R(b.k).top) < R(b.k).height;
        for (let i = 1; i < lines.length; i++) {
          const a = lines[i - 1], b = lines[i];
          if (!same(a, b) || (a.size === b.size && a.fam === b.fam)) continue;
          const d = Math.abs(a.b - b.b);
          if (d > 1) { out.push({ rule: "baseline", where: where(e), detail: `“${a.k.textContent.trim().slice(0, 12)}” ${a.size} and “${b.k.textContent.trim().slice(0, 12)}” ${b.size}: baselines ${d.toFixed(1)}px apart (align-items ${c.alignItems})` }); break; }
        }
      }
      // centering: a single-line label's cap height centred in its control.
      if (e.matches(".h-control, .h-nested, button.size-control, a.size-control") && !e.matches("input, select, textarea")) {
        const n = firstText(e);
        if (n && n.parentElement.closest(".h-control, .h-nested, .size-control, .size-nested") === e && lineRect(n) && document.createRange && (() => { const rg = document.createRange(); rg.selectNodeContents(n); return rg.getClientRects().length === 1; })()) {
          const m = metrics(n.parentElement), b = baseline(n);
          const top = r.top + px(c.borderTopWidth), bottom = r.bottom - px(c.borderBottomWidth);
          const mid = b - m.cap / 2, box = (top + bottom) / 2;
          if (Math.abs(mid - box) > 1.25) out.push({ rule: "centering", where: where(e), detail: `cap middle ${(mid - box).toFixed(1)}px ${mid > box ? "below" : "above"} the box middle` });
        }
      }
      // double-edge: a visible border flush against the same edge of a bordered ancestor draws two lines.
      const edge = (el, side) => { const k = cs(el); return px(k[`border${side}Width`]) > 0 && k[`border${side}Style`] !== "none" && !/rgba\(0, 0, 0, 0\)|transparent/.test(k[`border${side}Color`]); };
      for (const side of ["Top", "Bottom"]) {
        if (!edge(e, side) || e.matches("input, select, textarea, hr, [role=tab], .h-nested, .size-nested, kbd")) continue;  // a nested part's inset is the insets rule's job
        let a = e.parentElement;
        while (a && a !== document.body && !edge(a, side) && !/auto|scroll|hidden/.test(cs(a).overflowY)) a = a.parentElement;
        if (!a || a === document.body || !edge(a, side)) continue;
        const ar = R(a), inner = side === "Top" ? ar.top + px(cs(a).borderTopWidth) : ar.bottom - px(cs(a).borderBottomWidth);
        const mine = side === "Top" ? r.top : r.bottom;
        if (Math.abs(mine - inner) <= 1.5) { out.push({ rule: "double-edge", where: where(e), detail: `its ${side.toLowerCase()} border lies on ${where(a).split(" ")[1] || "its container"}'s ${side.toLowerCase()} border` }); break; }
      }
      // margin-gap: a margin on a child of a container that already spaces its children with gap.
      const pa = e.parentElement;
      if (pa && e !== pa.lastElementChild && !e.matches("legend")) {  // a fieldset's legend sits outside its flex layout, so gap never spaces it
        const pc = cs(pa), flex = pc.display.includes("flex"), grid = pc.display.includes("grid");
        if (flex || grid) {
          const column = flex ? pc.flexDirection.startsWith("column") : false;
          const gapV = px(pc.rowGap), gapH = px(pc.columnGap);
          const vertical = column || grid;
          const isAuto0 = (el, prop) => { try { return String(el.computedStyleMap().get(prop)) === "auto"; } catch { return false; } };
          const mEnd = isAuto0(e, vertical ? "margin-bottom" : "margin-right") ? 0 : vertical ? px(c.marginBlockEnd) : px(c.marginInlineEnd);
          const next = e.nextElementSibling, nc = next && cs(next);
          const isAuto = (el, prop) => { try { return String(el.computedStyleMap().get(prop)) === "auto"; } catch { return false; } };  // ms-auto pushes, it doesn't space
          const mStart = next && nc.display !== "none" && !isAuto(next, vertical ? "margin-top" : "margin-left") ? (vertical ? px(nc.marginBlockStart) : px(nc.marginInlineStart)) : 0;
          const m = Math.max(mEnd, mStart), gap = vertical ? gapV : gapH;
          if (gap > 0 && m > 0.5 && !(next && next.matches("legend"))) out.push({ rule: "margin-gap", where: where(mEnd >= mStart ? e : next), detail: `${m.toFixed(1)}px margin on top of the parent's ${gap.toFixed(1)}px gap` });
        }
      }
      // measure: running text wider than max-w-text (68ch of its own font).
      if (e.matches("p, li") && !e.closest("table, nav, [role=menu], [role=listbox]") && e.textContent.trim().length > 160) {
        ctx.font = `${c.fontWeight} ${c.fontSize} ${c.fontFamily}`;
        const ch = ctx.measureText("0").width, w = r.width - px(c.paddingLeft) - px(c.paddingRight);
        if (w > 68 * ch + 2) out.push({ rule: "measure", where: where(e), detail: `${(w / ch).toFixed(0)}ch wide (max-w-text is 68ch)` });
      }
      // shared-edge: sibling surfaces (cards, panels, a bordered table) inset their text alike, so a table's first column
      // lines up with the cards beside it. It compares cards (padded at --space-md) and tables stacked at one left edge,
      // looking through unpainted wrappers. A surface is a child with a border or a fill of its own; its inset is its border
      // and start padding, or, for a table or a box holding one, the border and the first cell's start padding.
      {
        const surface = (k) => { const kc = cs(k); return visible(k) && !isControl(k) && kc.position !== "absolute" && !kc.display.startsWith("inline") && (px(kc.borderLeftWidth) > 0 || (kc.backgroundColor !== "rgba(0, 0, 0, 0)" && kc.backgroundColor !== "transparent")); };
        const cardPad = (() => { const d = document.createElement("div"); d.style.paddingInlineStart = "var(--space-md)"; e.append(d); const v = px(cs(d).paddingInlineStart); d.remove(); return v; })();
        const atEdge = (k, depth = 0) => { if (!visible(k)) return null; if (surface(k)) return k; if (depth >= 2 || cs(k).paddingInlineStart !== "0px") return null; const f = k.firstElementChild; return f && Math.abs(R(f).left - R(k).left) < 1 ? atEdge(f, depth + 1) : null; };
        const insets = [...e.children].map((k) => atEdge(k)).filter((k) => k && !k.matches("figure, [data-example], details, dialog, pre")).map((k) => {
          const kc = cs(k), table = k.matches("table") ? k : (k.firstElementChild && k.firstElementChild.matches("table") ? k.firstElementChild : null);
          const cell = table && table.querySelector("th, td");
          if (px(kc.borderLeftWidth) >= 3) return null;  // a callout's start rule sets it apart on purpose
          const first = k.firstElementChild, item = first && !cell && isControl(first) && R(first).left - R(k).left < px(kc.borderLeftWidth) + px(kc.paddingInlineStart) + 2 ? first : null;
          const x = px(kc.borderLeftWidth) + (cell ? px(cs(cell).paddingInlineStart) : px(kc.paddingInlineStart) + (item ? px(cs(item).paddingInlineStart) + px(cs(item).borderLeftWidth) : 0));
          const card = Math.abs(px(kc.paddingInlineStart) - cardPad) < 1;  // a card pads at --space-md
          return (cell || card) ? { k, x: Math.round(x), left: Math.round(R(k).left) } : null;
        }).filter(Boolean);
        const columns = {}; insets.forEach((x) => (columns[x.left] = columns[x.left] || []).push(x));
        for (const col of Object.values(columns)) if (col.length >= 2) {
          const insets = col;
          const counts = {}; insets.forEach((x) => counts[x.x] = (counts[x.x] || 0) + 1);
          const [mode, n] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
          const base = n >= 2 ? +mode : insets[0].x;
          for (const x of insets) if (Math.abs(x.x - base) > 1.5 && Math.abs(x.x - base) < 40) out.push({ rule: "shared-edge", where: where(x.k), detail: `inset ${x.x}px, the surfaces stacked with it ${base}px` });
        }
      }
      // start-edge: block children in one column whose text starts off the column's shared edge.
      if ((c.display === "block" || (c.display.includes("flex") && c.flexDirection === "column")) && e.children.length >= 3 && !e.matches("ul, ol, table, tbody, thead, tr, nav")) {
        const textBlock = (k) => k.matches("p, h1, h2, h3, h4, h5, h6, span, label, legend, dt, dd, small, strong, em, a, li") && !k.querySelector("div, p, ul, ol, table, figure");
        const rows = [...e.children].filter((k) => visible(k) && !isControl(k) && textBlock(k) && cs(k).position !== "absolute").map((k) => {
          const lead = k.firstElementChild;
          if (lead && lead.matches(".icon, img, svg, input, .rounded-full, .size-control, .size-nested, kbd")) return null;
          const n = firstText(k); if (!n) return null;
          const lr = lineRect(n); return lr ? { k, x: Math.round(lr.left) } : null;
        }).filter(Boolean);
        if (rows.length >= 3) {
          const counts = {}; rows.forEach((x) => counts[x.x] = (counts[x.x] || 0) + 1);
          const [mode, n] = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
          if (n >= 2) for (const x of rows) if (Math.abs(x.x - mode) > 1.5 && Math.abs(x.x - mode) < 40) { out.push({ rule: "start-edge", where: where(x.k), detail: `text starts ${(x.x - mode).toFixed(0)}px off the column's edge` }); }
        }
      }
    }
    window.nowindLayoutAudit = out;
    console.log(`Layout audit: ${out.length} finding(s)`);
    if (out.length) console.table(out);
    return out;
  };
  window.addEventListener("load", () => document.fonts.ready.then(run));
  window.nowindRunLayoutAudit = run;
})();

// Paint audit (open any page with ?audit=paint): checks the paint contract's rendered rules (paintContract in
// theme/theme.colors.manifest.json); window.nowindPaintAudit holds the list. Parity: a part that stands apart from its
// surface by at least half a step in one mode does in the other. Each fill is composited over its surface and mapped to
// the nearest neutral step in that mode (by OKLab lightness), so the check counts steps, not contrast. Relief: a
// relief-* part sits inside a material-* region.
(() => {
  if (!window.nowindAudits().includes("paint")) return;
  const run = () => {
    const out = [];
    if (window.nowindOwnCSS()) { window.nowindPaintAudit = out; return out; }
    const root = document.documentElement, was = root.dataset.colorMode;
    const ctx = document.createElement("canvas").getContext("2d", { willReadFrequently: true });
    const rgba = (str) => { ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = "rgba(0,0,0,0)"; ctx.fillStyle = str; ctx.fillRect(0, 0, 1, 1); const d = ctx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
    const over = (top, under) => top[3] >= 1 ? top : [0, 1, 2].map((i) => top[i] * top[3] + under[i] * (1 - top[3])).concat(1);
    const L = ([r, g, b]) => { const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }; const [R, G, B] = [lin(r), lin(g), lin(b)]; return Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B) * 0.2104542553 + Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B) * 0.7936177850 + Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B) * -0.0040720468; };
    const frames = [...document.querySelectorAll("[data-example]")];
    const sections = [...document.querySelectorAll("main section[id]")].filter((s) => !s.matches("[data-semantic-demo]"));
    const inScope = (el) => frames.length ? !!el.closest("[data-example]") : sections.some((s) => s.contains(el)) && !el.closest("[data-semantic-demo]");
    const where = (el) => { const s = el.closest("section[id]"); return `#${s ? s.id : "?"} ${el.tagName.toLowerCase()}.${[...el.classList].slice(0, 5).join(".")} “${el.textContent.trim().replace(/\s+/g, " ").slice(0, 24)}”`; };
    const chroma = ([r, g, b]) => { const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }; const [R, G, B] = [lin(r), lin(g), lin(b)]; const l = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B), m = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B), s2 = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B); const A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s2, Bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s2; return Math.hypot(A, Bb); };
    const parts = [...document.querySelectorAll("main *")].filter((e) => inScope(e) && getComputedStyle(e).display !== "none" && e.getBoundingClientRect().width > 0);
    const measure = (mode) => {
      root.dataset.colorMode = mode;
      const probe = document.createElement("div"); document.body.append(probe);
      const steps = Array.from({ length: 12 }, (_, i) => { probe.style.background = `var(--neutral-${i + 1})`; return L(rgba(getComputedStyle(probe).backgroundColor)); });
      probe.remove();
      const toStep = (l) => { let best = 0, bd = Infinity; steps.forEach((s, i) => { const d = Math.abs(s - l); if (d < bd) { bd = d; best = i; } }); const n = best + (best < 11 && Math.sign(steps[best + 1] - steps[best]) === Math.sign(l - steps[best]) ? Math.abs(l - steps[best]) / Math.abs(steps[best + 1] - steps[best] || 1) : best > 0 && Math.sign(steps[best - 1] - steps[best]) === Math.sign(l - steps[best]) ? -Math.abs(l - steps[best]) / Math.abs(steps[best - 1] - steps[best] || 1) : 0); return n + 1; };
      const eff = new Map();
      const colourOf = (e) => { if (!e || e === root) return rgba(getComputedStyle(document.body).backgroundColor); if (eff.has(e)) return eff.get(e); const c = over(rgba(getComputedStyle(e).backgroundColor), colourOf(e.parentElement)); eff.set(e, c); return c; };
      const res = new Map();
      for (const e of parts) {
        const own = rgba(getComputedStyle(e).backgroundColor);
        if (own[3] === 0 || getComputedStyle(e).backgroundImage !== "none" || [...e.classList].some((c) => c.startsWith("relief-"))) continue;  // a relief part stands apart by light (its material's shadows), which steps can't read
        const surf = colourOf(e.parentElement), mine = colourOf(e);
        if (chroma(mine) > 0.03 || chroma(surf) > 0.03) continue;  // a coloured fill: the neutral step map can't place it
        res.set(e, Math.abs(toStep(L(mine)) - toStep(L(surf))));
      }
      return res;
    };
    const still = document.createElement("style"); still.textContent = "*, *::before, *::after { transition: none !important; animation: none !important; }"; document.head.append(still);
    const light = measure("light"), dark = measure("dark");
    if (was) root.dataset.colorMode = was; else delete root.dataset.colorMode;
    still.remove();
    for (const [e, dl] of light) {
      const dd = dark.get(e);
      if (dd === undefined) continue;
      if ((dl >= 0.5) !== (dd >= 0.5)) out.push({ rule: "parity", where: where(e), detail: `${dl.toFixed(1)} steps from its surface in light, ${dd.toFixed(1)} in dark` });
    }
    for (const e of parts) if ([...e.classList].some((c) => c.startsWith("relief-")) && !e.closest("[class*=material-]")) out.push({ rule: "relief", where: where(e), detail: "relief-* outside a material-* region" });
    window.nowindPaintAudit = out;
    console.log(`Paint audit: ${out.length} finding(s)`);
    if (out.length) console.table(out);
    return out;
  };
  window.addEventListener("load", run);
  window.nowindRunPaintAudit = run;
})();
