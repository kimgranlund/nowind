// Site search: ⌘K or Ctrl+K (or "/") opens a dialog over every page, block heading, component and class.
// The index, search.json beside this script, is written by scripts/templates.py and loaded on first open.
(() => {
  const base = new URL(".", document.currentScript.src);
  const KINDS = { Page: "ph-file-text", Section: "ph-hash", Component: "ph-squares-four", Class: "ph-brackets-curly" };
  let rows = null, hits = [], active = 0;

  const dialog = document.createElement("dialog");
  dialog.setAttribute("aria-label", "Search Nowind");
  dialog.className = "w-full max-w-form max-h-below-header mt-3xl mx-auto p-0 rounded-lg bg fg border shadow-xl";
  dialog.innerHTML = `
    <div class="flex flex-col max-h-below-header">
      <div class="flex items-center gap-gutter px-control border-b">
        <i class="icon ph ph-magnifying-glass fg-weak"></i>
        <input type="text" role="combobox" aria-expanded="true" aria-controls="search-results" aria-autocomplete="list"
          placeholder="Search pages, components and classes" aria-label="Search"
          class="grow min-w-0 h-control bg-transparent border-0 fg text-control-md">
        <kbd class="text-mono-sm fg-weak">Esc</kbd>
      </div>
      <ul id="search-results" role="listbox" aria-label="Results" class="list-none pl-0 flex flex-col min-h-0 overflow-y-auto"></ul>
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
        <span class="flex flex-col grow min-w-0"><span class="truncate ${r[2] === "Class" ? "text-mono-sm" : "text-title-sm"}">${esc(r[0])}</span><span class="truncate text-caption fg-weak">${esc(r[3] || "")}</span></span>
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

// Light and dark: the band's toggle flips the scheme and remembers it; the head script applies it before paint.
(() => {
  const root = document.documentElement, media = matchMedia("(prefers-color-scheme: dark)");
  const current = () => root.dataset.colorMode || (media.matches ? "dark" : "light");
  const show = () => document.querySelectorAll("[data-theme-toggle]").forEach((b) => {
    const dark = current() === "dark";
    b.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    b.querySelector("i").className = `icon ph ${dark ? "ph-sun" : "ph-moon"}`;
  });
  document.querySelectorAll("[data-theme-toggle]").forEach((b) => b.addEventListener("click", () => {
    const next = current() === "dark" ? "light" : "dark";
    root.dataset.colorMode = next;
    try { localStorage.setItem("nowind-color-mode", next); } catch {}
    show();
  }));
  media.addEventListener("change", show);
  show();
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
      // Refraction through a rounded glass edge: the surface is a quarter circle across the band, and the bend follows
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
