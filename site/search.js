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
        <input type="search" role="combobox" aria-expanded="true" aria-controls="search-results" aria-autocomplete="list"
          placeholder="Search pages, components and classes" aria-label="Search"
          class="grow min-w-0 h-control bg-transparent border-0 fg text-control-md">
        <kbd class="text-mono-sm fg-weak">Esc</kbd>
      </div>
      <ul id="search-results" role="listbox" aria-label="Results" class="flex flex-col min-h-0 overflow-y-auto py-3xs"></ul>
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
      <a href="${new URL(r[1], base)}" tabindex="-1" class="flex items-center gap-gutter px-control py-2xs no-underline fg aria-selected:bg-component-accent-1-weak hover:bg-component-weak">
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
