// Site search: ⌘K or Ctrl+K (or "/") opens a dialog over every page, block heading, component and class.
// The index, search.json beside this script, is written by scripts/templates.py and loaded on first open.
(() => {
  const base = new URL(".", document.currentScript.src);
  const KINDS = { Page: "ph-file-text", Section: "ph-hash", Component: "ph-squares-four", Class: "ph-brackets-curly" };
  let rows = null, hits = [], active = 0;

  const dialog = document.createElement("dialog");
  dialog.setAttribute("aria-label", "Search Nowind");
  dialog.className = "w-full max-w-form max-h-below-header mt-3xl mx-auto p-0 rounded-md bg fg border shadow-xl";
  dialog.innerHTML = `
    <div class="flex flex-col max-h-below-header">
      <div class="flex items-center gap-gutter px-control border-b">
        <i class="icon ph ph-magnifying-glass fg-weak"></i>
        <input type="text" role="combobox" aria-expanded="true" aria-controls="search-results" aria-autocomplete="list"
          placeholder="Search pages, components and classes" aria-label="Search"
          class="grow min-w-0 h-control bg-transparent border-0 fg text-control-md">
        <kbd class="text-mono-sm fg-weak">Esc</kbd>
      </div>
      <ul id="search-results" role="listbox" aria-label="Results" class="list-none ps-0 flex flex-col min-h-0 overflow-y-auto"></ul>
      <p class="px-control py-2xs border-t text-caption fg-weak" aria-live="polite"></p>
    </div>`;
  document.body.append(dialog);
  const input = dialog.querySelector("input"), list = dialog.querySelector("ul"), status = dialog.querySelector("p");

  const esc = (t) => t.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  function score(r, q, words) {
    const t = r[0].toLowerCase(), d = (r[3] || "").toLowerCase();
    if (!words.every((w) => t.includes(w) || d.includes(w))) return 0;
    let s = 1;
    if (t === q || t === "." + q) s += 100;
    else if (t.startsWith(q) || t.startsWith("." + q)) s += 50;
    else if (t.includes(q)) s += 20;
    s += { Page: 8, Component: 6, Section: 4, Class: 0 }[r[2]];
    return s - t.length / 100;
  }

  function render() {
    const q = input.value.trim().toLowerCase();
    if (!rows) { status.textContent = "Loading the index…"; return; }
    if (!q) hits = rows.filter((r) => r[2] === "Page");
    else {
      const words = q.split(/\s+/);
      hits = rows.map((r) => [score(r, q, words), r]).filter(([s]) => s > 0).sort((a, b) => b[0] - a[0]).slice(0, 60).map(([, r]) => r);
    }
    active = 0;
    list.innerHTML = hits.map((r, i) => `<li role="option" id="search-${i}" aria-selected="${i === 0}">
      <a href="${new URL(r[1], base)}" tabindex="-1" class="flex items-center gap-gutter px-control py-2xs no-underline fg selected:bg-component-accent-1-weak hover:bg-component-weak">
        <i class="icon ph ${KINDS[r[2]]} fg-weak"></i>
        <span class="flex flex-col grow min-w-0"><span class="truncate ${r[2] ==="Class" ? "text-mono-sm" : "text-title-sm"}">${esc(r[0])}</span><span class="truncate text-caption fg-weak">${esc(r[3] || "")}</span></span>
        <span class="text-kicker fg-subtle">${r[2]}</span>
      </a></li>`).join("");
    list.querySelectorAll("li").forEach((li) => li.firstElementChild.setAttribute("aria-selected", li.getAttribute("aria-selected")));
    input.setAttribute("aria-activedescendant", hits.length ? "search-0" : "");
    status.textContent = q ? `${hits.length === 60 ? "First 60" : hits.length} results · ↑↓ to move · Enter to open` : `${rows.length} entries · type to search`;
  }

  function move(d) {
    if (!hits.length) return;
    const items = list.querySelectorAll("li");
    items[active].setAttribute("aria-selected", "false"); items[active].firstElementChild.setAttribute("aria-selected", "false");
    active = (active + d + hits.length) % hits.length;
    items[active].setAttribute("aria-selected", "true"); items[active].firstElementChild.setAttribute("aria-selected", "true");
    items[active].scrollIntoView({ block: "nearest" });
    input.setAttribute("aria-activedescendant", `search-${active}`);
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
    else if (e.key === "Enter" && hits[active]) { e.preventDefault(); location.href = new URL(hits[active][1], base); dialog.close(); }
  });
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

// Type audit (open any page with ?audit=type): checks the rendered examples against the size contract's three rules
// (sizeContract.rules in theme/theme.type-roles.manifest.json) and logs what breaks them; window.nowindTypeAudit holds
// the list. Rows: text side by side shares a size, unless one side is a control, figure, badge, keycap or kicker.
// Order: within a surface, title >= body >= supporting, and a dialog title is larger than its buttons. Icons: an icon
// takes the step of the text beside it (icon-sm with text-sm, icon with text-base, icon-lg with a title).
(() => {
  if (new URLSearchParams(location.search).get("audit") !== "type") return;
  const run = () => {
    const out = [];
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
      if (!cs.display.includes("flex") || cs.flexDirection !== "row" || isControl(row) || row.closest("button, a, summary, [role=option], [role=menuitem]")) continue;
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
      if (host && host.matches(".h-nested, .size-nested, .h-full") && i.matches(".icon-sm")) continue;
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
  if (new URLSearchParams(location.search).get("audit") !== "geometry") return;
  const run = () => {
    const out = [];
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
      if (radius(e) > 0 && painted(e)) {
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
      if (p && e === p.lastElementChild && e.matches(".size-nested, .size-control, .h-full, kbd") && radius(p) > 0 && cs(p).display.includes("flex") && cs(p).flexDirection === "row" && painted(p)) {
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
          if (host !== e || n.parentElement.closest("code, kbd, input, select, textarea")) continue;
          const rg = document.createRange(); rg.selectNodeContents(n); const t = rg.getBoundingClientRect();
          if (!t.width) continue;
          const s0 = t.left - r.left - px(c.borderLeftWidth), en = r.right - t.right - px(c.borderRightWidth);
          if (s0 < 2 || en < 2) { out.push({ rule: "edges", where: where(e), detail: `text ${s0.toFixed(1)}px from the start, ${en.toFixed(1)}px from the end` }); break; }
        }
      }
      // Shape: squares and circles.
      if (e.matches(".aspect-square, .size-nested, .size-control") && Math.abs(r.width - r.height) > 1) out.push({ rule: "shape", where: where(e), detail: `${r.width.toFixed(1)}×${r.height.toFixed(1)}px` });
      // Clipping.
      if (c.overflow === "hidden" || c.overflowY === "hidden") {
        if (e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1) out.push({ rule: "clipping", where: where(e), detail: `content ${e.scrollWidth}×${e.scrollHeight} in ${e.clientWidth}×${e.clientHeight}` });
      }
      // Heights: full-size controls side by side.
      if (c.display.includes("flex") && c.flexDirection === "row" && !e.matches(".flex-wrap")) {
        const ctrls = [...e.children].filter((k) => k.matches(".h-control, .size-control"));
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
