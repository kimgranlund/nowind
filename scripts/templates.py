#!/usr/bin/env python3
"""Stamp the Nowind docs templates (designed with the massimo-vignelli agent). Shared parts are defined once here.
Usage: python3 scripts/templates.py [output-dir]   (default: site/docs/)"""
import html, json, os, re, sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from component_docs import COMPONENTS  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "docs")
E = html.escape

# ---------------------------------------------------------------- site map
# Every page of the site in four sections, docs and hand-written alike. Paths are relative to site/.
GROUP_ORDER = list(dict.fromkeys(c["group"] for c in COMPONENTS))
BY_GROUP = sorted(COMPONENTS, key=lambda c: GROUP_ORDER.index(c["group"]))
SECTIONS = [
    ("Docs", [("docs/docs-home.html", "Overview"), ("docs/guide.html", "Guide"), ("docs/colour.html", "Colour"),
              ("docs/type-space.html", "Type and space"), ("docs/states.html", "States and variants"),
              ("docs/materials.html", "Materials"), ("docs/reference.html", "Reference"), ("docs/resets.html", "Resets"), ("docs/convenience.html", "Convenience classes"),
              ("docs/changelog.html", "Changelog"), ("docs/index.html", "Templates")]),
    ("Components", [("docs/components-index.html", "All components"), ("components.html", "Showcase")] +
                   [(f"docs/c-{c['slug']}.html", c["name"]) for c in BY_GROUP]),
    ("Specimen", [("specimen.html", "Tokens"), ("utilities.html", "Utilities demo")]),
    ("Classes", [("docs/classes.html", "Regular"), ("docs/semantic.html", "Semantic")]),
]
HAND_PAGES = ["index.html", "components.html", "specimen.html", "utilities.html"]
ORDER = [path for _, pages in SECTIONS for path, _ in pages]
LABELS = {path: label for _, pages in SECTIONS for path, label in pages}
TITLES = {"docs/colour.html": "Colour", "docs/type-space.html": "Type and space", "docs/states.html": "States and variants",
          "docs/materials.html": "Materials", "docs/convenience.html": "Convenience classes", "docs/resets.html": "Resets", "docs/docs-home.html": "Overview", "docs/guide.html": "Lay out a docs page", "docs/reference.html": "Page grid and shell",
          "docs/changelog.html": "Changelog", "docs/index.html": "About these templates", "docs/components-index.html": "Components",
          "components.html": "Showcase", "specimen.html": "Specimen", "utilities.html": "Utilities demo",
          "docs/classes.html": "Classes", "docs/semantic.html": "Semantic classes"}
TITLES.update({f"docs/c-{c['slug']}.html": c["name"] for c in COMPONENTS})

def rel(target, frm):
    """A link from the page at site path frm to site path target."""
    return os.path.relpath(target, os.path.dirname(frm) or ".").replace(os.sep, "/")

def section_of(path):
    return next((name for name, pages in SECTIONS if any(pp == path for pp, _ in pages)), None)

# ---------------------------------------------------------------- shared parts
HEAD = """<!doctype html>
<html lang="en" class="scroll-pt-4xl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Nowind</title>
<link rel="icon" href="data:,">
{head_extra}<link rel="stylesheet" href="../../theme.css">
<link rel="stylesheet" href="../../nowind.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/regular/style.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/bold/style.css">
</head>
<body class="bg fg">
"""

# The head script applies a saved light or dark choice before the page paints.
HEAD_EXTRA = '<script>try{var d=document.documentElement,m=localStorage.getItem("nowind-color-mode"),z=localStorage.getItem("nowind-root-size");if(m)d.dataset.colorMode=m;if(z)d.style.fontSize=z+"px"}catch(e){}</script>\n'

# The lens: a displacement map that bends a band along the rim (red = x, green = y, 50% = none; the centre is neutral),
# displaced three times for an R/G/B fringe and recombined. Box units, so it fits any element. Used by the lens class.
LENS_MAP = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'%3E%3Cdefs%3E%3ClinearGradient id='r'%3E%3Cstop offset='0' stop-color='#f00'/%3E%3Cstop offset='1' stop-color='#000'/%3E%3C/linearGradient%3E%3ClinearGradient id='g' x2='0' y2='1'%3E%3Cstop offset='0' stop-color='#0f0'/%3E%3Cstop offset='1' stop-color='#000'/%3E%3C/linearGradient%3E%3Cfilter id='b' x='-20%' y='-20%' width='140%' height='140%'%3E%3CfeGaussianBlur stdDeviation='7'/%3E%3C/filter%3E%3C/defs%3E%3Crect width='100' height='100' fill='url(#r)'/%3E%3Crect width='100' height='100' fill='url(#g)' style='mix-blend-mode:screen'/%3E%3Crect x='16' y='16' width='68' height='68' rx='8' fill='#808000' filter='url(#b)'/%3E%3C/svg%3E"
LENS_SVG = ('<svg width="0" height="0" class="absolute" aria-hidden="true" focusable="false"><filter id="nowind-lens" x="0" y="0" width="1" height="1" '
            'filterUnits="objectBoundingBox" primitiveUnits="objectBoundingBox" color-interpolation-filters="sRGB">'
            f'<feImage href="{E(LENS_MAP)}" x="0" y="0" width="1" height="1" preserveAspectRatio="none" result="map"/>'
            '<feDisplacementMap in="SourceGraphic" in2="map" scale="0.13" xChannelSelector="R" yChannelSelector="G" result="dr"/>'
            '<feDisplacementMap in="SourceGraphic" in2="map" scale="0.1365" xChannelSelector="R" yChannelSelector="G" result="dg"/>'
            '<feDisplacementMap in="SourceGraphic" in2="map" scale="0.143" xChannelSelector="R" yChannelSelector="G" result="db"/>'
            '<feColorMatrix in="dr" values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0" result="cr"/>'
            '<feColorMatrix in="dg" values="0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0" result="cg"/>'
            '<feColorMatrix in="db" values="0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0" result="cb"/>'
            '<feBlend in="cr" in2="cg" mode="screen" result="rg"/><feBlend in="rg" in2="cb" mode="screen" result="rgb"/>'
            '<feGaussianBlur in="rgb" stdDeviation="0.004"/></filter></svg>\n')

CUR_SEC = ' aria-current="true"'
CUR_PAGE = ' aria-current="page"'

def site_map(path):
    """The popover behind the bar's menu button: every section and its pages, the current page marked."""
    def links(pages, two=False):
        lis = "".join(
            f'<li><a href="{rel(pp, path)}"{CUR_PAGE if pp == path else ""} class="inline-flex items-center w-fit h-nested px-nested rounded-xs no-underline text-body-sm {"bg-component-accent-1 fg-accent-1 font-medium" if pp == path else "state fg-weak hover:fg"}">{label}</a></li>'
            for pp, label in pages)
        return f'<ul role="list" class="grid {"grid-cols-2 gap-x-md" if two else "grid-cols-1"}">{lis}</ul>'
    def col(name, pages, two=False, span=""):
        return f'<div class="{span} flex flex-col gap-2xs min-w-0"><span class="px-nested text-kicker fg-weak">{name}</span>{links(pages, two)}</div>'
    sec = dict(SECTIONS)
    lead = [pp for pp in sec["Components"] if not pp[0].startswith("docs/c-")]
    def group(g):
        return (f'<div class="flex flex-col gap-3xs min-w-0"><span class="px-nested text-label fg-subtle">{g}</span>'
                f'{links([(f"docs/c-{c['slug']}.html", c["name"]) for c in BY_GROUP if c["group"] == g])}</div>')
    sizes = [sum(c["group"] == g for c in COMPONENTS) + 1 for g in GROUP_ORDER]
    half, run, cut = sum(sizes) / 2, 0, len(GROUP_ORDER)
    for i, n in enumerate(sizes):
        if run + n / 2 > half:
            cut = i
            break
        run += n
    stacks = [GROUP_ORDER[:cut], GROUP_ORDER[cut:]]
    groups = "".join(f'<div class="flex flex-col gap-sm min-w-0">{"".join(group(g) for g in st)}</div>' for st in stacks)
    components = (f'<div class="md:col-span-2 flex flex-col gap-2xs min-w-0"><span class="px-nested text-kicker fg-weak">Components</span>'
                  f'{links(lead, two=True)}<div class="grid grid-cols-2 gap-x-md gap-y-sm pt-2xs">{groups}</div></div>')
    return f"""<div id="site-map" popover class="anchor-bottom w-full max-w-measure max-h-below-header overflow-y-auto p-surface rounded-md bg fg border shadow-lg">
  <nav aria-label="Site map" class="grid grid-cols-1 md:grid-cols-4 gap-group">
    {col("Docs", sec["Docs"])}
    {components}
    <div class="flex flex-col gap-group">{col("Specimen", sec["Specimen"])}{col("Classes", sec["Classes"])}</div>
  </nav>
</div>
"""

def top(path):
    """The band (wordmark, sections, GitHub) and the bar under it: where you are with the site map, search, previous and next."""
    cur = section_of(path)
    band_on = "inline-flex items-center h-header border-b-2 border-accent-1 no-underline fg-inverse text-title-sm"
    band_off = "inline-flex items-center h-header border-b-2 border-transparent no-underline fg-inverse-weak hover:fg-inverse text-title-sm transition-colors"
    secs = "".join(
        f'<a href="{rel(pages[0][0], path)}"{CUR_SEC if name == cur else ""} class="{band_on if name == cur else band_off}">{name}</a>'
        for name, pages in SECTIONS)
    where = (f'<span class="fg-weak">{cur}</span><span class="fg-subtle">/</span><span class="truncate">{LABELS[path]}</span>'
             if cur else '<span>Site map</span>')
    step = ""
    if cur:
        i = ORDER.index(path)
        arrow = "inline-flex items-center justify-center size-control rounded-sm border hover:bg-component-weak no-underline fg transition-colors"
        prev_a = (f'<a href="{rel(ORDER[i - 1], path)}" class="{arrow}" aria-label="Previous: {TITLES.get(ORDER[i - 1], LABELS[ORDER[i - 1]])}"><i class="icon ph ph-arrow-left"></i></a>'
                  if i > 0 else "")
        next_a = (f'<a href="{rel(ORDER[i + 1], path)}" class="{arrow}" aria-label="Next: {TITLES.get(ORDER[i + 1], LABELS[ORDER[i + 1]])}"><i class="icon ph ph-arrow-right"></i></a>'
                  if i < len(ORDER) - 1 else "")
        step = f'<span class="hidden sm:flex items-center gap-3xs">{prev_a}{next_a}</span>'
    return f"""<div class="sticky top-0 z-30">
<header class="light bg-inverse fg-inverse">
  <div class="flex items-center gap-lg h-header px-grid">
    <a href="{rel("index.html", path)}" class="inline-flex items-center gap-gutter-half no-underline fg-inverse hover:fg-inverse-weak transition-colors"><i class="icon ph-bold ph-wind"></i><span class="text-subtitle">Nowind</span><span class="text-kicker fg-inverse-weak">__VERSION__</span></a>
    <nav aria-label="Sections" class="hidden md:flex items-center gap-lg">{secs}</nav>
    <button type="button" popovertarget="site-settings" class="inline-flex items-center justify-center size-nested ms-auto rounded-xs border border-transparent bg-transparent fg-inverse-weak hover:fg-inverse cursor-pointer transition-colors" aria-label="Display settings"><i class="icon ph ph-sliders-horizontal"></i></button>
    <a href="https://github.com/kimgranlund/nowind" class="inline-flex items-center justify-center size-nested no-underline fg-inverse-weak hover:fg-inverse transition-colors" aria-label="Nowind on GitHub"><i class="icon ph ph-github-logo"></i></a>
  </div>
</header>
<div id="site-settings" popover class="anchor-bottom-end scope text-chrome w-max p-surface rounded-md bg fg border shadow-lg">
  <div class="flex flex-col gap-sm">
  <div class="flex flex-col gap-3xs">
    <span class="fg-weak">Theme</span>
    <div class="flex h-control rounded-sm border-2 border-transparent bg-component-weak" role="group" aria-label="Theme"><button type="button" data-setting="theme" data-value="light" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><i class="icon icon-sm ph ph-sun"></i><span>Light</span></button><button type="button" data-setting="theme" data-value="dark" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><i class="icon icon-sm ph ph-moon"></i><span>Dark</span></button><button type="button" data-setting="theme" data-value="system" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><i class="icon icon-sm ph ph-desktop"></i><span>System</span></button></div>
  </div>
  <div class="flex flex-col gap-3xs">
    <span class="fg-weak">Base size</span>
    <div class="flex h-control rounded-sm border-2 border-transparent bg-component-weak" role="group" aria-label="Base size"><button type="button" data-setting="size" data-value="12" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><span>12</span></button><button type="button" data-setting="size" data-value="14" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><span>14</span></button><button type="button" data-setting="size" data-value="16" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><span>16</span></button><button type="button" data-setting="size" data-value="18" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><span>18</span></button></div>
  </div>
  <div class="flex flex-col gap-3xs">
    <span class="fg-weak">Tier</span>
    <div class="flex h-control rounded-sm border-2 border-transparent bg-component-weak" role="group" aria-label="Tier"><button type="button" data-setting="tier" data-value="product" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><span>Product</span></button><button type="button" data-setting="tier" data-value="content" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><span>Content</span></button><button type="button" data-setting="tier" data-value="brand" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg-white fg-weak pressed:fg-black font-medium cursor-pointer"><span>Brand</span></button></div>
  </div>
  </div>
</div>
<div class="flex items-center gap-xs px-grid py-2xs border-b-2 border-strong bg">
  <button type="button" popovertarget="site-map" class="inline-flex items-center gap-gutter-half min-w-0 h-control px-control rounded-sm border hover:bg-component-weak bg text-title-sm cursor-pointer transition-colors" aria-label="Site map: {cur or "all pages"}">{where}<i class="icon caret fg-weak" aria-hidden="true"></i></button>
  <button type="button" data-search-open class="inline-flex items-center gap-gutter grow min-w-0 max-w-form h-control px-control rounded-sm border hover:border-strong bg-strong fg-subtle text-control-md cursor-text transition-colors" aria-label="Search the site"><i class="icon ph ph-magnifying-glass"></i><span class="grow truncate text-start">Search pages, components and classes</span><kbd class="hidden sm:inline text-mono-sm">⌘K</kbd></button>
  <span class="flex-1 hidden lg:block"></span>
  {step}
</div>
</div>
{site_map(path)}"""

def bottom(path):
    """The footer and the search script, for the page at site path."""
    return f"""<footer class="flex flex-col md:flex-row md:items-center justify-between gap-field px-grid py-surface border-t-2 border-strong text-caption fg-weak">
  <span>Nowind __VERSION__. Every page here is built from Nowind utility classes only.</span>
  <span class="flex flex-wrap gap-row">
    <a href="{rel("docs/changelog.html", path)}" class="no-underline fg-weak hover:fg transition-colors">Changelog</a>
    <a href="{rel("docs/index.html", path)}" class="no-underline fg-weak hover:fg transition-colors">About these templates</a>
    <a href="https://github.com/kimgranlund/nowind" class="no-underline fg-weak hover:fg transition-colors">GitHub</a>
  </span>
</footer>
{LENS_SVG}<script src="{rel("site.js", path)}" defer></script>
"""

def prev_next(path):
    i = ORDER.index(path)
    prev = ORDER[i - 1] if i > 0 else None
    nxt = ORDER[i + 1] if i < len(ORDER) - 1 else None
    cells = []
    if prev:
        cells.append(f"""          <a href="{rel(prev, path)}" class="flex flex-col gap-3xs min-w-0 p-surface border border-weak hover:border-strong no-underline transition-colors">
            <span class="inline-flex items-center gap-gutter-half text-kicker fg-weak"><i class="icon icon-sm ph-bold ph-arrow-left"></i><span>Previous</span></span>
            <span class="text-subtitle fg-accent-1-weak break-words max-w-full">{TITLES.get(prev, LABELS[prev])}</span>
          </a>""")
    else:
        cells.append('          <span></span>')
    if nxt:
        cells.append(f"""          <a href="{rel(nxt, path)}" class="flex flex-col items-end gap-3xs min-w-0 p-surface border border-weak hover:border-strong no-underline text-end transition-colors">
            <span class="inline-flex items-center gap-gutter-half text-kicker fg-weak"><span>Next</span><i class="icon icon-sm ph-bold ph-arrow-right"></i></span>
            <span class="text-subtitle fg-accent-1-weak break-words max-w-full">{TITLES.get(nxt, LABELS[nxt])}</span>
          </a>""")
    return '<nav aria-label="Previous and next page" class="col-span-12 grid grid-cols-2 gap-grid py-page border-t border-strong">\n' + "\n".join(cells) + "\n        </nav>\n"

CALLOUT = {
    "note": ("info", "ph-info", "Note"),
    "tip": ("success", "ph-check-circle", "Tip"),
    "warning": ("warning", "ph-warning", "Warning"),
}

def callout(kind, body_html):
    pal, icon, label = CALLOUT[kind]
    return f"""<aside role="note" class="flex gap-gutter p-md border-s-4 border-{pal}-7 bg-{pal}-3">
            <i class="icon ph {icon} fg-{pal}-11"></i>
            <div class="flex flex-col gap-3xs min-w-0">
              <span class="text-sm font-medium fg-{pal}-12">{label}</span>
              <p class="text-base max-w-text break-words">{body_html}</p>
            </div>
          </aside>"""

def code(filename, lang, src):
    return f"""<figure class="flex flex-col min-w-0 border border-weak bg-strong">
            <figcaption class="flex items-center justify-between gap-row px-surface py-2xs border-b border-weak">
              <span class="text-mono-sm fg-weak truncate">{E(filename)}</span><span class="text-mono-sm uppercase tracking-widest fg-subtle">{lang}</span>
            </figcaption>
            <pre class="p-surface overflow-x-auto whitespace-pre text-mono-sm"><code>{E(src.strip(chr(10)))}</code></pre>
          </figure>"""

def table(headers, rows, align=None):
    align = [{"left": "start", "right": "end"}.get(x, x) for x in (align or ["left"] * len(headers))]
    ths = "".join(f'<th scope="col" class="text-{a} px-2xs md:px-sm py-xs border-b text-label fg-weak">{h}</th>' for h, a in zip(headers, align))
    trs = []
    for n, r in enumerate(rows):
        last = n == len(rows) - 1
        b = "" if last else " border-b border-weak"
        # A class name in the first column breaks only after a hyphen, colon, slash or dot, never mid-word; code in the
        # other columns may break anywhere, so a wide table still fits a phone.
        joint = lambda c: re.sub(r"<code>(.*?)</code>", lambda m: '<code class="whitespace-normal">' + re.sub(r"([-:/.])(?=[^<>]*?(?:<|$))", r"\1<wbr>", m.group(1)) + "</code>", c)
        r = [joint(c) if k == 0 else c.replace("<code>", '<code class="whitespace-normal break-all">') for k, c in enumerate(r)]
        tds = "".join(f'<td class="text-{a} align-top px-2xs md:px-sm py-xs break-words{b}">{c}</td>' for c, a in zip(r, align))
        trs.append(f"                <tr>{tds}</tr>")
    return f"""<div class="border border-weak overflow-x-auto">
            <table class="w-full text-body-md">
              <thead class="bg-strong"><tr>{ths}</tr></thead>
              <tbody>
{chr(10).join(trs)}
              </tbody>
            </table>
          </div>"""

def page_head(kicker, title, intro, meta=None):
    m = f'\n            <span class="text-caption fg-weak">{meta}</span>' if meta else ""
    return f"""<header class="col-span-12 flex flex-col gap-field pt-page pb-xl">
            <span class="text-kicker fg-weak">{kicker}</span>
            <h1 class="text-display-sm text-balance">{title}</h1>
            <p class="text-body-md fg-weak max-w-text">{intro}</p>{m}
          </header>"""

def block(sid, label, *parts, attrs=""):
    """One block of a page: its label in the first three of twelve columns, its content in the other nine."""
    inner = "\n          ".join(parts)
    ident = f' id="{sid}"' if sid else ""
    return f"""<section{ident}{attrs} class="col-span-12 grid grid-cols-12 gap-x-grid gap-y-2xs pt-sm pb-xl border-t border-strong">
          <div class="col-span-12 md:col-span-3 flex flex-col gap-3xs">{label}</div>
          <div class="col-span-12 md:col-span-9 min-w-0 flex flex-col gap-group">
          {inner}
          </div>
        </section>"""

def section(sid, title, *parts):
    return block(sid, f'<h2 class="text-heading-md text-balance">{title}</h2>', *parts)

def subhead(t):
    return f'<h3 class="text-subtitle">{t}</h3>'

def p(t):
    return f'<p class="text-body-md max-w-text break-words">{t}</p>'

def ul(items):
    lis = "\n".join(f'            <li>{i}</li>' for i in items)
    return f'<ul class="flex flex-col gap-3xs ps-md list-disc text-body-md max-w-text">\n{lis}\n          </ul>'

def doc_page(current, title, article_html, toc_items=None, wide=False, sidebar_on=True, head_extra=""):
    """Every generated page: band and section row, the twelve-column grid of blocks, previous and next, footer."""
    path = "docs/" + current
    return (HEAD.format(title=E(title), head_extra=HEAD_EXTRA + head_extra) + top(path) +
f"""<main id="content" class="tier-content px-grid">
  <div class="grid grid-cols-12 gap-x-grid">
        {article_html}
        {prev_next(path)}  </div>
</main>
{bottom(path)}</body>
</html>
""")

# ================================================================ pages

def guide():
    toc_items = []
    art = "\n        ".join([
        page_head("Guide", "Lay out a docs page",
                  "Build a documentation page from Nowind's shell lengths, its 12-column grid and four type roles. Every part on this page is the template you can copy.",
                  "Applies to Nowind __VERSION__"),
        section("frame", "The frame",
            p("Every page on the site has the same three parts, after Vignelli's Unigrid: an inverse band with the four sections, a bar under a heavy rule with where you are, search and the next page, and the page itself, a stack of blocks. The band and the bar stick to the top together; the page scrolls under them."),
            code("frame.html", "HTML", """
<html class="scroll-pt-4xl">
<div class="sticky top-0 z-30">
<header class="light bg-inverse fg-inverse">
  <div class="flex items-center gap-lg h-header px-grid">…wordmark, sections, search…</div>
</header>
<div class="flex items-center gap-xs px-grid py-2xs border-b-2 border-strong bg">…site map button, search, previous and next…</div>
</div>
<main class="tier-content px-grid">
  <div class="grid grid-cols-12 gap-x-grid">…page head, blocks…</div>
</main>"""),
            p("The band is <code>h-header</code> tall and follows the base size, so it grows with the type from a phone to a wide screen. <code>scroll-pt-4xl</code> on <code>html</code> keeps a linked block clear of the band and the bar."),
            callout("note", "Keep one scroller: the page. Don't make <code>main</code> a scroll box; browsers paint very tall nested scrollers badly, and in-page links, find and the back button work against the window."),
        ),
        section("grid", "The block",
            p("Every block hangs from a label column: its label in the first three of twelve columns, its content in the other nine. A component's example, a palette and a release in the changelog all have this one shape. Below 768px the label sits above the content."),
            code("block.html", "HTML", """
<section class="col-span-12 grid grid-cols-12 gap-x-grid gap-y-2xs pt-sm pb-xl border-t border-strong">
  <div class="col-span-12 md:col-span-3"><h2 class="text-heading-md">Example</h2></div>
  <div class="col-span-12 md:col-span-9 min-w-0 flex flex-col gap-group">…</div>
</section>"""),
            table(["Width", "Sections", "Label"], [
                ["Under 768px", "In the site map", "Above the content"],
                ["768px (<code>md:</code>) and up", "In the band", "Columns 1–3, content 4–12"],
            ]),
        ),
        section("measure", "The reading column",
            p("Prose stops at <code>max-w-text</code>, 68 characters of its own font. The article is a <code>tier-content</code> region, so its section gaps and page padding are one and a half times the product rhythm and its measure grows with the tier's larger base size."),
            callout("tip", "Put the tier on <code>main</code> only. The band and the section row stay in the product tier, so they look the same on every page."),
        ),
        section("type", "Four type sizes",
            p("A docs page needs four sizes and no more. Contrast between them is the hierarchy, so they sit far apart: a display size for the page title, a heading size for sections, the base size for reading and controls, and a small size for labels and code."),
            table(["Size", "Classes", "Used for"], [
                ["Display", "<code>text-display-sm</code>", "The page title, once per page"],
                ["Heading", "<code>text-heading-md</code>", "Section headings, each under a rule"],
                ["Base", "<code>text-body-md</code>, <code>text-subtitle</code>, <code>text-title-sm</code>", "Prose, subheadings, navigation and buttons"],
                ["Small", "<code>text-caption</code>, <code>text-label</code>, <code>text-kicker</code>, <code>text-mono-sm</code>", "Metadata, table heads, kickers and code"],
            ]),
            p("Weight, not size, separates a subheading from prose: <code>text-subtitle</code> is the base size at a semibold weight."),
        ),
        section("parts", "Callouts, code and tables",
            p("A callout is a coloured rule on the left, a word and a sentence. The colour codes the kind and the word says it, so the meaning never depends on colour alone."),
            callout("warning", "A callout interrupts the reader. Use at most one per section."),
            p("A code block is a figure: the file name and language in a caption, the code in a <code>pre</code> that scrolls sideways rather than wrapping. Tables wrap their cells instead of scrolling, so the code block is the only thing on the page that scrolls sideways."),
            code("callout.html", "HTML", """
<aside role="note" class="flex gap-gutter p-md border-s-4 border-info-7 bg-info-3">
  <i class="icon ph ph-info fg-info-11"></i>
  <div class="flex flex-col gap-3xs">
    <span class="text-sm font-medium fg-info-12">Note</span>
    <p class="text-base">One sentence the reader must not miss.</p>
  </div>
</aside>"""),
        ),
        section("menu", "Search",
            p("Press ⌘K or Ctrl+K, or <code>/</code>, on any page to search every page, block heading, component and class. The index, <code>search.json</code>, is written with the pages, so it never falls behind."),
            callout("note", "The search script is the only script every page loads. Without it the band, the section row and every link still work."),
        ),
    ])
    return doc_page("guide.html", "Lay out a docs page", art, toc_items)


def radius_section():
    gm = json.load(open(os.path.join(ROOT, "theme", "theme.geometry.manifest.json")))
    def find(o):
        if isinstance(o, dict):
            for v in o.values():
                if isinstance(v, list) and any(isinstance(x, dict) and x.get("token") == "--radius-md" for x in v):
                    return v
                r = find(v)
                if r is not None:
                    return r
    rows = [[f"<code>rounded-{x['token'][9:]}</code>", E(x["formula"]), E(x["use"])] for x in find(gm) if x.get("token", "").startswith("--radius-") and len(x["token"]) <= 11]
    return section("radius", "Radius and nesting", p(E(gm["nesting"])), table(["Class", "Value", "Use"], rows),
                   code("nest.html", "HTML", '<div popover class="rounded-md p-inset border …">\n  <a class="rounded-sm …">Rename</a>   <!-- concentric: md − inset − border = sm -->\n</div>\n<div class="rounded-lg p-sm border">\n  <div class="rounded-inner …">…</div>   <!-- any other padding -->\n</div>'))


def lengths_section():
    gc = _m("theme/theme.geometry.manifest.json")["geometryContract"]
    rows = [[E(k["kind"]), E(k["identify"]), f'<code>{E(k["height"])}</code>', f'<code>{E(k["padding"])}</code>', E(k["gap"]), f'<code>{E(k["corner"])}</code>'] for k in gc["kinds"]]
    return section("lengths", "Where each length goes",
        p(E(gc["description"].split(" A lint")[0]) + " The examples lint enforces it, and <code>?audit=geometry</code> on any page measures the rules below."),
        table(["Part", "Identified by", "Height", "Padding", "Gap", "Corner"], rows),
        p(" ".join(E(r) for r in gc["rules"])))


def reference():
    toc_items = [("grid", "Page grid"), ("shell", "Shell lengths"), ("levels", "Container levels"),
                 ("tiers", "Tiers"), ("radius", "Radius and nesting"), ("lengths", "Where each length goes"), ("breakpoints", "Breakpoints")]
    art = "\n        ".join([
        page_head("Reference", "Page grid and shell",
                  "The classes that place a page: the column gutter and edge padding, the shell's sidebar, header and reading measure, the container levels and the tiers. Each length is derived from the base size <code class=\"whitespace-nowrap\">--F</code>.",
                  "Nowind __VERSION__ · from classes.md"),
        section("grid", "Page grid",
            p("Grid columns are <code>grid-cols-1</code> to <code>grid-cols-12</code> with <code>col-span-*</code>. These classes set the space between and around them."),
            table(["Class", "Declaration", "Derived from"], [
                ["<code>gap-grid</code>", "<code>gap: var(--grid-gutter)</code>", "2 × margin"],
                ["<code>gap-x-grid</code>", "<code>column-gap: var(--grid-gutter)</code>", "2 × margin"],
                ["<code>p-grid-inset</code>", "<code>padding: var(--grid-inset)</code>", "Half a gutter"],
                ["<code>px-grid</code>", "<code>padding-inline: var(--grid-margin-regular)</code>", "One slot"],
                ["<code>px-grid-compact</code>", "<code>padding-inline: var(--grid-margin-compact)</code>", "The larger of a gutter and half a slot"],
            ]),
            code("grid.html", "HTML", """
<div class="grid grid-cols-4 md:grid-cols-12 gap-grid px-grid">
  <div class="col-span-4 md:col-span-8">Content</div>
  <div class="col-span-4 md:col-span-4">Aside</div>
</div>"""),
        ),
        section("shell", "Shell lengths",
            p("The app shell's lengths grow with the type, so a sidebar that fits its labels on a phone still fits them on a wide screen."),
            table(["Class", "Declaration", "Derived from"], [
                ["<code>w-sidebar</code>", "<code>width: var(--shell-sidebar-width)</code>", "16F + 16px"],
                ["<code>w-rail</code>", "<code>width: var(--shell-rail-width)</code>", "Control height + 2 slots"],
                ["<code>h-header</code>", "<code>height: var(--shell-header-height)</code>", "Control height + 1 slot"],
                ["<code>min-h-header</code>", "<code>min-height: var(--shell-header-height)</code>", "Control height + 1 slot"],
                ["<code>max-w-measure</code>", "<code>max-width: var(--shell-measure)</code>", "44F"],
            ]),
            callout("note", "Breakpoint variants cover layout only: display, grid, flex, alignment, widths and gaps. There is no <code>lg:w-sidebar</code>; show and hide the sidebar with <code>hidden lg:flex</code> instead."),
        ),
        section("levels", "Container levels",
            p("Pad a box by what it is, not by a size. The values are at a 16px base."),
            table(["Class", "Use", "At 16px"], [
                ["<code>p-surface</code>", "Card or panel", "23px"],
                ["<code>p-dialog</code>", "Dialog", "37px"],
                ["<code>p-region</code>", "Sidebar", "24px"],
                ["<code>p-page</code>", "Page content area", "38px"],
                ["<code>gap-field</code>", "Label to control, control to help", "7px"],
                ["<code>gap-row</code>", "Controls side by side", "14px"],
                ["<code>gap-group</code>", "Field to field", "19px"],
                ["<code>gap-section</code>", "Before a new section", "24px"],
            ], ["left", "left", "right"]),
        ),
        section("tiers", "Tiers",
            p("A tier changes the rhythm of a whole region. Every length inside it recomputes."),
            table(["Class", "Base size", "Page and section spacing"], [
                ["<code>tier-product</code>", "Unchanged", "× 1"],
                ["<code>tier-content</code>", "+ 2px", "× 1.5"],
                ["<code>tier-brand</code>", "+ 4px", "× 2"],
            ]),
            code("tier.html", "HTML", """
<article class="tier-content flex flex-col gap-section py-page max-w-measure">…</article>"""),
        ),
        radius_section(),
        lengths_section(),
        section("breakpoints", "Breakpoints",
            table(["Prefix", "Min width", "In these templates"], [
                ["<code>sm:</code>", "640px", "Previous and next appear; the search field shows ⌘K"],
                ["<code>md:</code>", "768px", "Sections appear in the band; block labels take three columns"],
                ["<code>lg:</code>", "1024px", "Not used"],
                ["<code>xl:</code>", "1280px", "Not used"],
                ["<code>2xl:</code>", "1536px", "Not used"],
            ], ["left", "right", "left"]),
        ),
    ])
    return doc_page("reference.html", "Page grid and shell", art, toc_items)


# ---------------------------------------------------------------- releases, read from CHANGELOG.md
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def inline_md(text):
    """Escape, then turn `code` into <code> and **bold** into <strong>."""
    text = E(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)


def read_releases():
    """[(version, date, latest, intro, [(group or None, [(name or None, html)])])], newest first, Unreleased skipped."""
    releases, cur = [], None
    for line in open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read().splitlines():
        m = re.match(r"^## (\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\)", line)
        if m:
            cur = [m.group(1), m.group(2), False, [], [[None, []]]]
            releases.append(cur)
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur is None or not line.strip():
            continue
        if line.startswith("### "):
            cur[4].append([line[4:].strip(), []])
        elif line.startswith("- "):
            item = line[2:].strip()
            m = re.match(r"^\*\*([^*]+?):?\*\*:?\s*(.*)$", item)
            name, text = (m.group(1), m.group(2)) if m else (None, item)
            if name and text[:1].islower():
                text = text[0].upper() + text[1:]
            cur[4][-1][1].append((name, inline_md(text)))
        else:
            cur[3].append(inline_md(line.strip()))
    for r in releases:
        r[4] = [g for g in r[4] if g[1]]
    if releases:
        releases[0][2] = True
    return [tuple(r) for r in releases]


RELEASES = read_releases()
VERSION = RELEASES[0][0] if RELEASES else "0.0.0"

def changelog():
    toc_items = [("v" + v.replace(".", "-"), v) for v, *_ in RELEASES]
    blocks = [page_head("Changelog", "Release notes",
                        "What changed in each release of Nowind, newest first. Pin a release in the CDN link and your site changes only when you change the version.")]
    blocks.append(section("pin", "Pin a release", code("index.html", "HTML", """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kimgranlund/nowind@v__VERSION__/dist/nowind.min.css">""")))
    for v, date, latest, intro, groups in RELEASES:
        badge = '\n              <span class="inline-flex items-center w-fit h-nested px-nested bg-solid-accent-1 fg-on-solid-accent-1 text-label">Latest</span>' if latest else ""
        body = [p(t) for t in intro]
        for g, entries in groups:
            if g:
                body.append(subhead(g))
            lis = []
            for name, text in entries:
                if name:
                    lis.append(f"""                <li class="flex flex-col gap-3xs max-w-text"><span class="text-label fg-weak">{name}</span><p class="text-body-md break-words">{text}</p></li>""")
                else:
                    lis.append(f"""                <li><p class="text-body-md max-w-text break-words">{text}</p></li>""")
            body.append('<ul role="list" class="flex flex-col gap-group">\n' + "\n".join(lis) + "\n              </ul>")
        label = f"""<h2 class="text-subtitle">{v}</h2>
              <time datetime="{date}" class="text-caption fg-weak">{date}</time>{badge}"""
        blocks.append(block("v" + v.replace(".", "-"), label, *body))
    art = "\n        ".join(blocks)
    return doc_page("changelog.html", "Changelog", art)


def docs_home():
    entries = [
        ("guide.html", "ph-book-open", "Guide", "Lay out a docs page: the band, the grid, the label column and four type sizes."),
        ("reference.html", "ph-grid-four", "Reference", "Every grid, shell, level and tier class with its declaration and where it comes from."),
        ("classes.html", "ph-list-bullets", "Classes", "Every class and what it declares, regular and semantic, with a filter."),
        ("components-index.html", "ph-squares-four", "Components", "Buttons, forms, tables and dialogs built only from utility classes."),
    ]
    cards = "\n".join(f"""            <a href="{h}" class="flex flex-col gap-field p-surface border border-weak hover:border-strong no-underline fg transition-colors">
              <i class="icon ph {i} fg-accent-1-weak"></i>
              <span class="text-subtitle">{t}</span>
              <span class="text-body-md fg-weak">{d}</span>
            </a>""" for h, i, t, d in entries)
    counts = json.load(open(os.path.join(ROOT, "nowind.manifest.json")))["counts"]
    roles = json.load(open(os.path.join(ROOT, "theme", "theme.type-roles.manifest.json")))["roles"]
    palettes = json.load(open(os.path.join(ROOT, "theme", "theme.colors.manifest.json")))["palettes"]
    figures = [(f"{counts['classes']:,}", "utility classes"), (f"{counts['hover']:,}", "hover variants"),
               (f"{counts['state']:,}", "state variants"), (f"{counts['group']:,}", "group variants"),
               (f"{counts['responsive']:,}", "breakpoint variants"), (str(len(roles)), "type roles"), (str(len(palettes)), "colour palettes")]
    figs = "\n".join(f"""            <div class="flex items-baseline justify-between gap-row py-xs border-b border-weak">
              <dt class="text-body-md fg-weak">{l}</dt><dd class="text-heading-md tabular-nums">{n}</dd>
            </div>""" for n, l in figures)
    art = "\n        ".join([
        page_head("Documentation · __VERSION__", "Nowind documentation",
                  "Theme tokens and utility classes in plain CSS. Link one file and every class already exists, so it works in any HTML, including what a CMS writes. Press ⌘K on any page to search every page, component and class."),
        section("sections", "Where to go", f'<div class="grid grid-cols-1 md:grid-cols-2 gap-grid">\n{cards}\n          </div>'),
        section("start", "Start in one line",
            p("Link the minified bundle from the CDN. The link pins release __VERSION__, so your site won't change until you change the version."),
            code("index.html", "HTML", '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kimgranlund/nowind@v__VERSION__/dist/nowind.min.css">'),
            callout("note", "Put your own CSS in <code>@layer styles</code>, so a utility class always wins over it.")),
        section("inside", "In the box", f'<dl class="flex flex-col max-w-measure">\n{figs}\n          </dl>',
            '<p class="text-caption fg-weak">Read from <code>nowind.manifest.json</code>, the type-role manifest and the colour manifest when the pages are built.</p>'),
    ])
    return doc_page("docs-home.html", "Overview", art)


def index():
    toc_items = [("purpose", "Purpose"), ("frame", "The frame"), ("grid", "The grid"), ("type", "Type scale"),
                 ("colour", "Colour and form"), ("parts", "Which classes make which part"),
                 ("templates", "The templates"), ("limits", "Known limits")]
    # live grid strip
    cols = "\n".join('            <div class="col-span-1 py-xs bg-component-accent-1-weak fg-accent-1-weak text-label text-center">' + str(n) + '</div>' for n in range(1, 13))
    grid_strip = f"""<div class="grid grid-cols-4 md:grid-cols-12 gap-grid" aria-hidden="true">
{cols}
          </div>"""
    frame_diagram = """<div class="flex flex-col border" role="img" aria-label="Diagram of the frame: an inverse band with the sections, a bar with the site map and search under a heavy rule, then blocks with a label column of three and content of nine">
            <div class="flex items-center px-sm py-xs bg-inverse fg-inverse text-label">band · sections · search</div>
            <div class="px-sm py-xs border-b-2 border-strong text-label fg-weak">site map · search · previous, next</div>
            <div class="grid grid-cols-12 border-b border-weak">
              <div class="col-span-3 p-sm text-label">label · 3</div>
              <div class="col-span-9 p-sm text-label fg-weak">content · 9</div>
            </div>
            <div class="grid grid-cols-12">
              <div class="col-span-3 p-sm text-label">label · 3</div>
              <div class="col-span-9 p-sm text-label fg-weak">content · 9</div>
            </div>
          </div>"""
    type_rows = [
        ('<span class="text-display-sm">Aa</span>', "Display", "<code>text-display-sm</code>", "<code>--text-4xl</code>", "Page title"),
        ('<span class="text-heading-md">Aa</span>', "Heading", "<code>text-heading-md</code>", "<code>--text-xl</code>", "Section heading"),
        ('<span class="text-body-md">Aa</span>', "Base", "<code>text-body-md</code> · <code>text-subtitle</code> · <code>text-title-sm</code>", "<code>--text-base</code>", "Prose, subheads, nav, buttons"),
        ('<span class="text-caption">Aa</span>', "Small", "<code>text-caption</code> · <code>text-label</code> · <code>text-kicker</code> · <code>text-mono-sm</code>", "<code>--text-sm</code>", "Metadata, labels, code"),
    ]
    parts = [
        ["Band", "Inside a <code>sticky top-0 z-30</code> wrapper with the bar: <code>light bg-inverse fg-inverse</code> (dark in both modes); inner <code>flex items-center gap-lg h-header px-grid</code>"],
        ["Section link", "<code>h-header border-b-2 fg-inverse-weak text-title-sm</code>; current: <code>border-accent-1 fg-inverse</code>"],
        ["Site map", "A <code>popovertarget</code> button naming the section and page; the popover <code>anchor-bottom max-w-measure max-h-below-header overflow-y-auto</code>"],
        ["Search field", "A button that looks like a field: <code>grow max-w-form h-control border bg-strong cursor-text</code> with <code>data-search-open</code>"],
        ["Bar", "<code>flex items-center gap-xs px-grid py-2xs border-b-2 border-strong</code>; previous and next <code>size-control border</code>"],
        ["Main grid", "<code>tier-content px-grid</code>, inner <code>grid grid-cols-12 gap-x-grid</code>"],
        ["Page head", "<code>col-span-12 flex flex-col gap-field pt-page pb-xl</code>; title <code>text-display-sm</code>"],
        ["Block", "<code>col-span-12 grid grid-cols-12 gap-x-grid pt-sm pb-xl border-t border-strong</code>; label <code>md:col-span-3</code>, content <code>md:col-span-9</code>"],
        ["Callout", "<code>flex gap-gutter p-md border-s-4 border-info-7 bg-info-3</code>"],
        ["Code block", "<code>figure</code> with <code>border bg-strong</code>; <code>pre</code> with <code>p-surface overflow-x-auto whitespace-pre text-mono-sm</code>"],
        ["Table", "Box <code>border</code>, no scrolling; <code>th</code> <code>px-sm py-xs text-label</code>; <code>td</code> <code>px-sm py-xs border-b break-words</code>, code in cells <code>whitespace-normal break-all</code>"],
        ["Previous and next", "<code>grid grid-cols-1 md:grid-cols-2 gap-grid</code>; each <code>p-surface border hover:border-strong</code>"],
        ["Footer", "<code>flex flex-col md:flex-row gap-field px-grid py-surface border-t text-caption</code>"],
    ]
    tpls = [
        ("docs-home.html", "Docs home", "A landing page: title, two actions, four entry points on the grid, an install snippet and the figures."),
        ("guide.html", "Guide", "The band, the bar with the site map and search, and the block with its label column."),
        ("reference.html", "Reference", "Tables of classes and declarations, with code."),
        ("changelog.html", "Changelog", "Releases as rows on a 1 + 3 grid, with a release index in place of the contents."),
    ]
    tpl_list = "\n".join(f"""            <li><a href="{h}" class="flex items-center justify-between gap-row py-sm border-b border-weak no-underline fg hover:fg-accent-1 transition-colors"><span class="flex flex-col gap-3xs"><span class="text-subtitle">{t}</span><span class="text-body-md fg-weak">{d}</span></span><i class="icon ph ph-arrow-right fg-weak"></i></a></li>""" for h, t, d in tpls)
    art = "\n        ".join([
        page_head("Templates", "A documentation system for Nowind",
                  "Four page templates for a docs site, built only from Nowind's utility classes. One frame, one grid, four type sizes, one accent. Copy a page and replace the words.",
                  "No style element, no style attribute, no script"),
        section("purpose", "Purpose",
            p("A documentation reader is looking for one thing and wants to find it fast. These templates keep every part in the same place on every page, so after one visit the reader stops looking at the frame and reads the content."),
        ),
        section("frame", "The frame",
            frame_diagram,
            p("An inverse band with the four sections, then a bar under a heavy rule with the site map, search and the next page, then the page as a stack of blocks. The band and the bar stick together; the page scrolls under them. Below 768px the sections are reached through the site map."),
        ),
        section("grid", "The grid",
            grid_strip,
            p("Twelve columns, spaced by <code>gap-grid</code> and held off the edge by <code>px-grid</code>. Every block puts its label in three columns and its content in nine; below 768px the two stack. Prose inside a block stops at <code>max-w-text</code>."),
        ),
        section("type", "Type scale",
            p("Four sizes, far apart. Weight separates roles that share a size."),
            table(["Sample", "Size and use", "Classes"], [[smp, f'{size}<br><span class="text-caption fg-weak">{use}, {tok}</span>', cls] for smp, size, cls, tok, use in type_rows]),
            p("One family carries everything: Inter for text, Inter Tight for display and headings, IBM Plex Mono for code and kickers. Nowind has no serif, so these pages have none."),
        ),
        section("colour", "Colour and form",
            ul([
                "Neutral roles for everything: <code>bg</code>, <code>bg-strong</code>, <code>fg</code>, <code>fg-weak</code>, <code>border-weak</code>.",
                "One accent, <code>accent-1</code>, for links, the current page, the primary button, entry icons and the Latest release badge.",
                "Status colours only in callouts, each paired with its word: Note, Tip, Warning.",
                "Square corners and no shadows. Rules and white space do the separating.",
                "Every colour is a role class, so the pages follow light and dark mode by themselves.",
            ]),
        ),
        section("parts", "Which classes make which part",
            table(["Part", "Classes"], parts),
        ),
        section("templates", "The templates",
            f'<ul role="list" class="flex flex-col border-t border-weak">\n{tpl_list}\n          </ul>',
        ),
        section("limits", "Known limits",
            ul([
                "Margins and type have no breakpoint variants; padding, position, overflow, widths and gaps do. The templates rely on the fluid type scale.",
                "Search needs a web server: browsers block loading the index from a file.",
            ]),
        ),
    ])
    return doc_page("index.html", "About these templates", art, toc_items)



# ---------------------------------------------------------------- class list
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def class_id(name):
    return "class-" + re.sub(r"[^a-z0-9-]", "_", name)

def read_classes():
    """Categories from classes.md, the generated list: (title, [(class, declarations)])."""
    cats, cur = [], None
    for line in open(os.path.join(ROOT, "classes.md")):
        if line.startswith("## "):
            cur = (line[3:].strip(), [])
            cats.append(cur)
        elif cur and line.startswith("| `."):
            m = re.match(r"\| `\.([^`]+)` \| `(.*)` \|$", line.strip())
            if m:
                cur[1].append((m.group(1), m.group(2)))
    return cats

PREVIEW = {
    "Text color": lambda k: f'<span class="{k} text-title">Aa</span>',
    "Background color": lambda k: f'<span class="block size-control rounded-xs border border-weak {k}"></span>',
    "Border color": lambda k: f'<span class="block size-control rounded-xs border-2 bg {k}"></span>',
    "Borders, radius, shadow": lambda k: f'<span class="block size-control bg-strong border border-weak {k}"></span>',
}

CLASS_FILTER = """<script>
{
  const input = document.getElementById("class-filter"), count = document.getElementById("class-count");
  const sections = [...document.querySelectorAll("[data-classes]")];
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    let shown = 0;
    for (const s of sections) {
      let n = 0;
      for (const r of s.querySelectorAll("[data-row]")) {
        const hit = !q || r.textContent.toLowerCase().includes(q);
        r.hidden = !hit;
        n += hit;
      }
      s.hidden = n === 0;
      shown += n;
    }
    count.textContent = q ? `${shown} matching` : count.dataset.all;
  });
}
</script>
"""

SEMANTIC_CATS = {"Controls and icons", "Levels and tiers", "Materials", "Page grid and shell"}
SEMANTIC_WORDS = re.compile(r"-(surface|dialog|region|page|field|row|group|section|control|nested|gutter|grid|sidebar|rail|header|measure)(-|$)")

def is_semantic(cat, k):
    """Semantic classes name a role (p-surface, fg-weak, text-heading-md); regular ones a scale step or a property value (p-md, border-warning-7)."""
    if k in ("icon", "icon-sm", "icon-md", "icon-lg") or re.fullmatch(r"(h|size|min-w|px)-(control|nested)|gap-gutter(-half)?", k):
        return False  # icon sizes and control lengths are derived from the base size, like the space scale, not roles
    if cat in SEMANTIC_CATS or (cat != "Layout and misc" and SEMANTIC_WORDS.search(k)):
        return True
    if cat in ("Text color", "Background color", "Border color"):
        return not re.search(r"(accent-\d|neutral|danger|warning|success|info)-(a?\d+|contrast)$|-(inherit|current|transparent|white|black)$", k)
    if cat == "Type":
        return not re.fullmatch(r"text-(xs|sm|base|lg|\d?xl)", k)
    if cat == "Typography":
        return k in ("font-body", "font-heading", "font-control")
    if cat == "Motion, anchors and select":
        return re.fullmatch(r"(duration|ease)-(fade|snappy|smooth|bouncy)", k) is not None
    return False

CLASS_PAGES = {
    False: ("classes.html", "Classes", "Regular classes",
            "name a step on a scale or a property value, as in Tailwind and Prewind: <code>p-md</code>, <code>text-lg</code>, <code>border-warning-7</code>, <code>flex</code>.",
            ("semantic.html", "Semantic classes")),
    True: ("semantic.html", "Semantic classes", "Semantic classes",
           "name a role in the design rather than a value: a container level (<code>p-surface</code>, <code>gap-field</code>), a colour role (<code>fg-weak</code>, <code>bg-solid-accent-1</code>), a type role (<code>text-heading-md</code>), a control length, a material or a tier. Their values follow the theme.",
           ("classes.html", "Regular classes")),
}

def class_page_of(k):
    for cat, rows in read_classes():
        if any(c == k for c, _ in rows):
            return CLASS_PAGES[is_semantic(cat, k)][0]
    return "classes.html"

def classes_page(semantic=False):
    fname, title_, kicker_name, what, (other, other_title) = CLASS_PAGES[semantic]
    cats = [(t, [r for r in rows if is_semantic(t, r[0]) == semantic]) for t, rows in read_classes()]
    cats = [(t, rows) for t, rows in cats if rows]
    total = sum(len(rows) for _, rows in cats)
    sections, toc_items = [], []
    for title, rows in cats:
        sid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        toc_items.append((sid, title))
        prev = PREVIEW.get(title)
        span = ("md:col-span-4", "md:col-span-6", "md:col-span-2") if prev else ("md:col-span-4", "md:col-span-8", "")
        heads = ["Class", "Declarations"] + (["Preview"] if prev else [])
        head_row = "".join(f'<span class="{sp} text-label fg-weak">{h}</span>' for h, sp in zip(heads, span))
        rows_html = []
        for k, decl in rows:
            cells = [f'<code class="col-span-12 {span[0]} break-all text-mono-sm fg">.{E(k)}</code>',
                     f'<span class="col-span-12 {span[1]} break-words text-mono-sm fg-weak">{E(decl)}</span>']
            if prev:
                cells.append(f'<span class="col-span-12 {span[2]}">{prev(k)}</span>')
            rows_html.append(f'            <li id="{class_id(k)}" data-row class="scroll-mt-3xl grid grid-cols-12 gap-x-grid gap-y-3xs px-sm py-xs border-t border-weak">{"".join(cells)}</li>')
        sections.append(block(sid, f'<h2 class="text-subtitle">{title}</h2><span class="text-caption fg-weak">{len(rows)} classes</span>',
            f"""<ul role="list" class="border border-weak">
            <li aria-hidden="true" class="hidden md:grid grid-cols-12 gap-x-grid px-sm py-xs bg-strong">{head_row}</li>
{chr(10).join(rows_html)}
          </ul>""", attrs=" data-classes"))
    head = page_head("Reference", title_,
        f"{kicker_name} {what} {total} of them, with what each declares, read from <code>classes.md</code>. "
        f"The rest are in <a href=\"{other}\">{other_title}</a>. "
        "Colour, opacity and cursor classes also take <code>hover:</code> and the state variants; layout classes take <code>sm:</code> to <code>2xl:</code>.",
        "Nowind __VERSION__ · generated from classes.md")
    search = f"""<div class="col-span-12 sticky top-header z-10 flex items-center gap-row py-xs bg">
          <input id="class-filter" type="search" placeholder="Filter by class or declaration" aria-label="Filter classes" class="grow min-w-0 h-control px-control rounded-sm border hover:border-strong bg text-control-md transition-colors">
          <span id="class-count" data-all="{total} classes" aria-live="polite" class="text-caption fg-weak whitespace-nowrap">{total} classes</span>
        </div>"""
    cards = "\n".join(
        f"""            <a href="#{sid}" class="flex items-baseline justify-between gap-row p-surface border border-weak hover:border-strong hover:bg-component-weak no-underline fg transition-colors">
              <span class="text-subtitle">{title}</span><span class="text-caption fg-weak whitespace-nowrap">{len(rows)}</span>
            </a>""" for (sid, title), (_, rows) in zip(toc_items, cats))
    groups = section("groups", "Groups", f"""<nav aria-label="Class groups" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-grid">
{cards}
          </nav>""")
    art = "\n        ".join([head, groups, search] + sections)
    return doc_page(fname, title_, art, toc_items, wide=True).replace("</body>", CLASS_FILTER + "</body>", 1)



# ---------------------------------------------------------------- system pages, read from the manifests
def _m(name):
    return json.load(open(os.path.join(ROOT, name)))

def _plain(t):
    return E(t)

def colour_page():
    cm = _m("theme/theme.colors.manifest.json")
    nm = _m("nowind.manifest.json")
    ramps = []
    for name, pal in cm["palettes"].items():
        sw = "".join(f'<span class="block py-sm rounded-xs bg-{name}-{n}" title="--{name}-{n}"></span>' for n in range(1, 13))
        light = "contrast-white" in pal["contrast"] and "light-dark" not in pal["contrast"]
        ramps.append(f"""<div class="flex flex-col gap-3xs">
            <div class="flex flex-wrap items-baseline justify-between gap-xs"><span class="text-subtitle"><code>{name}</code> · {E(pal['family'])}</span><span class="text-caption fg-weak">{E(pal['use'])}</span></div>
            <div class="grid grid-cols-12 gap-3xs" aria-hidden="true">{sw}</div>
            <span class="text-caption fg-weak">Text on its solid: {"light in both modes" if light else "light, then dark"} (<code>fg-{name}-contrast</code>)</span>
          </div>""")
    rows = []
    for g in cm["roles"]:
        for t in g["tokens"]:
            neutral, accent = t.get("neutral", ""), t.get("accent", "")
            rows.append([f"<code>{E(neutral)}</code>", f"<code>{E(accent)}</code>", str(t.get("step", "")), E(t.get("use", ""))])
    toc = [("palettes", "Palettes"), ("roles", "Roles"), ("classes", "Class names"), ("solid", "Text on a solid"), ("modes", "Light and dark")]
    art = "\n        ".join([
        page_head("Docs", "Colour",
                  "Two layers: palettes of twelve steps, and roles that name what a step is for. Use roles where the meaning matters (a page background, a hover fill, an error border) and steps where you want a specific value. Every value is a <code>light-dark()</code> pair, so both modes come from one class."),
        section("palettes", "Palettes", p(f"{len(cm['palettes'])} palettes, each a radix-hct family of twelve steps (1–2 backgrounds, 3–5 component fills, 6–8 borders, 9–10 solids, 11–12 text) and twelve alpha steps for transparency."), *ramps),
        section("roles", "Roles", p("A role is a step chosen for a use. Moving a role moves every part that uses it, and nothing that names a step."),
                table(["Neutral", "Per palette", "Step", "Use"], rows)),
        section("classes", "Class names", p(_plain(nm["categories"]["colors"]))),
        section("solid", "Text on a solid", p("Text on a step-9 fill takes that palette's contrast colour: <code>fg-accent-1-contrast</code> in primitives, <code>fg-on-solid-accent-1</code> as a role. The accents and every status take light text in both modes; neutral is light, then dark."),
                code("solid.html", "HTML", '<button class="py-xs px-sm rounded-sm border border-transparent bg-accent-1-9 hover:bg-accent-1-10 fg-accent-1-contrast">Save</button>')),
        section("modes", "Light and dark", p("Colours follow the reader's system setting. <code>.light</code> and <code>.dark</code> (or <code>data-color-mode</code>) force a scheme on any subtree. The toggle in this site's band sets <code>data-color-mode</code> on the root and remembers it; a script in the head applies it before the page paints. There is no <code>dark:</code> variant.")),
    ])
    return doc_page("colour.html", "Colour", art)

def type_space_page():
    ty = _m("theme/theme.typography.manifest.json")
    tr = _m("theme/theme.type-roles.manifest.json")
    sp = _m("theme/theme.space.manifest.json")
    sizes = [[f'<code>text-{t["token"][7:]}</code>', f'<span class="text-{t["token"][7:]}">Aa</span>', f'{t["minPx"]}–{t["maxPx"]}px', str(t["lineHeight"])] for t in ty["sizes"]]
    roles = [[f'<code>text-{r["role"][2:]}</code>', f'<code>{E(r["size"])}</code>', str(r.get("weight", "")), E(r.get("use", ""))] for r in tr["roles"]]
    space = [[f'<code>{t["token"][8:]}</code>', f'<code>p-{t["token"][8:]}</code> · <code>gap-{t["token"][8:]}</code>', f'{t["multiplier"]} × F', f'{t["minPx"]}–{t["maxPx"]}px'] for t in sp["sizes"]]
    faces = ul([f'<code>{E(f["token"])}</code>: {E(f["use"])}' for f in ty["faces"]])
    toc = [("sizes", "Type sizes"), ("contract", "Where each size goes"), ("roles", "Type roles"), ("faces", "Faces"), ("space", "Space")]
    art = "\n        ".join([
        page_head("Docs", "Type and space",
                  "One fluid scale for each: sizes grow with the viewport between a phone and a wide screen, and every space step is a multiple of the base size, F. Sizes are the primitives; roles name a size, weight and face for a use."),
        section("sizes", "Type sizes", p("Each <code>text-*</code> class sets the size and its line height, as Tailwind v4 does. Sizes are measured at the smallest and largest viewport."),
                table(["Class", "Sample", "Size", "Line height"], sizes)),
        section("contract", "Where each size goes", p(E(tr["sizeContract"]["description"].split(". Every row")[0]) + ". The examples lint enforces it, and <code>?audit=type</code> on any page checks the rendered rules below."),
                table(["Kind", "Identified by", "Size", "Icon"], [[E(k["kind"]), E(k["identify"]), E(k["size"]), E(k["icon"])] for k in tr["sizeContract"]["kinds"] if k["status"] == "decided"]),
                p(" ".join(E(r) for r in tr["sizeContract"]["rules"]))),
        section("roles", "Type roles", p(f"{len(tr['roles'])} roles, each a size with its weight, face and leading, for a use. A role is semantic; in examples, write the size and weight instead."),
                table(["Class", "Size", "Weight", "Use"], roles)),
        section("faces", "Faces", faces),
        section("space", "Space", p("Space steps are a multiple of F, the base size: fluid at the page's root, and 1em inside a <code>.scope</code> or a tier, so a region with its own font size spaces itself to match. Every padding, margin and gap class takes these steps."),
                table(["Step", "Classes", "Value", "Size"], space)),
    ])
    return doc_page("type-space.html", "Type and space", art)

STATE_DOCS = [
    ("hover:", ":hover, on devices that can hover", "colour roles and the raw steps of neutral, accent-1 to accent-4 and danger; opacity; cursor"),
    ("active:", ":active", "neutral and accent colours"),
    ("focus-visible:", ":focus-visible", "neutral and accent border colours"),
    ("focus-within:", ":focus-within", "neutral and accent border colours (a field box)"),
    ("selected:", '[aria-selected="true"]', "neutral and accent colours"),
    ("current:", '[aria-current], not "false"', "neutral and accent colours"),
    ("pressed:", '[aria-pressed="true"]', "neutral and accent colours"),
    ("expanded:", '[aria-expanded="true"]', "neutral and accent colours"),
    ("open:", "[open], :popover-open", "neutral and accent colours"),
    ("invalid:", '[aria-invalid="true"], :user-invalid', "neutral and danger text and border colours"),
    ("has-invalid:", "holds an invalid element", "neutral and danger text and border colours"),
    ("has-checked:", "holds a checked radio or checkbox", "neutral and accent colours (a choice card)"),
    ("disabled:", ':disabled, [aria-disabled="true"]', "neutral colours, opacity, cursor"),
]
GROUP_DOCS = [
    ("group-hover:", "the .group is hovered"),
    ("group-focus-within:", "something in the .group has focus"),
    ("group-open:", 'the .group is [open], :popover-open, aria-expanded="true", or holds an open popover'),
]

# ---------------------------------------------------------------- live examples on the docs pages
def _snip(slug, ex=None):
    """A component's snippet (or one of its extra examples), reused so the docs show the lint-checked markup."""
    c = next(c for c in COMPONENTS if c["slug"] == slug)
    return c["html"] if ex is None else next(x["html"] for x in c.get("examples", []) if x["id"] == ex)


def live(name, html_, semantic=False, frame=""):
    """A rendered example and its code. semantic marks a demo built on role classes (materials), which the examples
    lint leaves alone; frame adds classes to the example's frame (relative overflow-hidden for a full-bleed backdrop)."""
    return (f"""<div data-example{' data-semantic-demo' if semantic else ''} class="tier-product p-surface rounded-md border border-weak bg-strong{' ' + frame if frame else ''}">
{html_}
          </div>""", code(name, "HTML", html_))


def _stack(html_):
    """Several snippets in one example, a section gap apart, each in a full-width block so it keeps its own width."""
    return '<div class="flex flex-col gap-md">\n' + "\n".join(f"<div>\n{h}\n</div>" for h in html_) + "\n</div>"


_STAT = '<div class="flex flex-col gap-3xs p-md rounded-md bg-neutral-1 border border-neutral-6">\n    <span class="text-sm fg-neutral-11">{label}</span>\n    <span class="text-3xl font-display font-extrabold tracking-tight tabular-nums">{value}</span>\n  </div>'
STATE_DEMOS = {
    "selected": _stack([_snip("tabs"), _snip("segmented"), _snip("pagination")]),
    "native": _stack([_snip("form-controls"), _snip("text-field", "states")]),
    "groups": _stack([_snip("tooltip"), _snip("menu")]),
    "breakpoints": '<div class="grid grid-cols-1 sm:grid-cols-2 2xl:grid-cols-4 gap-sm">\n  '
                   + "\n  ".join(_STAT.format(label=l, value=v) for l, v in [("Visitors", "48,210"), ("Signups", "2,318"), ("Revenue", "$9,640"), ("Churn", "1.4%")]) + "\n</div>",
    "containers": '<div class="grid grid-cols-1 md:grid-cols-3 gap-md">\n<div class="min-w-0">\n' + _snip("media-card") + '\n</div>\n<div class="min-w-0 md:col-span-2">\n' + _snip("media-card") + "\n</div>\n</div>",
    "layer": _snip("button"),
    "motion": _snip("icon-button", "toolbar"),
    "indicators": _snip("accordion"),
}


def _material_card(m):
    lens = " lens" if m == "glass" else ""
    label = ('<span class="flex flex-wrap items-baseline justify-between gap-xs"><span class="text-kicker fg-weak">glass</span><span data-lens-label class="text-caption fg-weak">Lens</span></span>'
             if m == "glass" else f'<span class="text-kicker fg-weak">{m}</span>')
    return f"""  <div class="material-{m}{lens} flex flex-col gap-field p-surface rounded-md relief-ground bg border border-weak">
    {label}
    <span class="text-title">Invite your team</span>
    <input class="relief-field h-control px-control rounded-sm border bg text-control-md w-full" placeholder="name@example.com" aria-label="Email">
    <div class="flex flex-wrap gap-row">
      <button class="relief-raised-solid inline-flex items-center h-control px-control rounded-sm border border-transparent bg-solid-accent-1 hover:bg-solid-accent-1-strong fg-on-solid-accent-1 text-title-sm cursor-pointer"><span>Invite</span></button>
      <button class="relief-raised inline-flex items-center h-control px-control rounded-sm border bg-component-weak hover:bg-component active:bg-component-strong fg text-title-sm cursor-pointer"><span>Later</span></button>
    </div>
  </div>"""


MATERIAL_DEMOS = {
    "materials": '<div class="absolute inset-0 bg-neutral-2 fg-accent-1-9 bg-dots bg-dots-xs" aria-hidden="true"></div>\n<div class="relative grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-group">\n'
                 + "\n".join(_material_card(m) for m in ["flat", "physical", "frosted", "glass", "outline"]) + "\n</div>",
    "reliefs": """<div class="material-physical flex flex-col gap-field p-surface rounded-md relief-ground bg border border-weak max-w-form">
  <span class="text-caption fg-weak">relief-ground: the panel others sit on</span>
  <input class="relief-field h-control px-control rounded-sm border bg text-control-md w-full" placeholder="relief-field: cut into the ground" aria-label="Field">
  <div class="flex flex-wrap gap-row">
    <button class="relief-raised-solid inline-flex items-center h-control px-control rounded-sm border border-transparent bg-solid-accent-1 hover:bg-solid-accent-1-strong fg-on-solid-accent-1 text-title-sm cursor-pointer"><span>relief-raised-solid</span></button>
    <button class="relief-raised inline-flex items-center h-control px-control rounded-sm border bg-component-weak hover:bg-component active:bg-component-strong fg text-title-sm cursor-pointer"><span>relief-raised</span></button>
  </div>
</div>""",
    "glass": """<div data-glass-slider class="flex flex-col gap-sm p-xl rounded-md bg-neutral-3 fg-neutral-7 bg-dots bg-dots-md">
  <div class="flex flex-wrap items-baseline justify-between gap-xs"><span class="text-kicker fg-weak">Glass slider: drag it</span><span data-lens-label class="text-caption fg-weak">Lens</span></div>
  <div class="relative py-2xl">
    <div data-track class="relative py-2xs rounded-full bg-neutral-6"><div data-fill class="absolute top-0 bottom-0 start-0 rounded-full bg-accent-1-9"></div></div>
    <div class="absolute inset-0 flex items-center pointer-events-none"><div data-thumb class="material-glass relief-raised lens px-2xl py-lg rounded-full"></div></div>
    <input type="range" min="0" max="100" value="55" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" aria-label="Glass slider">
  </div>
</div>""",
    "backdrops": '<div class="grid grid-cols-2 sm:grid-cols-4 gap-sm">\n'
                 + "\n".join(f'  <div class="flex items-end h-3xl p-sm rounded-md bg-neutral-3 fg-accent-1-9 bg-dots bg-dots-{k}"><span class="px-2xs rounded-inner bg fg text-caption">bg-dots-{k}</span></div>' for k in ["xs", "sm", "md", "lg"]) + "\n</div>",
}


CONV_DEMOS = [
    ("buttons", "Buttons", "<code>btn</code> takes a tone; <code>icon-btn</code> holds one icon and an <code>aria-label</code>.",
     '<div class="flex flex-wrap gap-xs">\n  <button class="btn btn-primary"><i class="icon ph ph-check"></i><span>Save</span></button>\n  <button class="btn btn-secondary"><span>Cancel</span></button>\n  <button class="btn btn-soft"><span>Soft</span></button>\n  <button class="btn btn-ghost"><span>Ghost</span></button>\n  <button class="btn btn-danger"><i class="icon ph ph-trash"></i><span>Delete</span></button>\n  <button class="icon-btn btn-secondary" aria-label="Settings"><i class="icon ph ph-gear"></i></button>\n</div>'),
    ("small", "Small buttons and segments", "<code>btn-sm</code> and <code>segment</code> sit only inside an inset container: a toolbar padded <code>p-3xs</code>, or a <code>segmented</code> group.",
     '<div class="flex flex-wrap items-center gap-sm">\n  <div class="inline-flex items-center gap-3xs p-3xs rounded-md border border-neutral-6 bg-neutral-2" role="toolbar" aria-label="Formatting">\n    <button class="btn-sm btn-ghost"><i class="icon icon-sm ph-bold ph-text-b"></i><span>Bold</span></button>\n    <button class="btn-sm btn-ghost"><i class="icon icon-sm ph-bold ph-link"></i><span>Link</span></button>\n  </div>\n  <div class="segmented" role="group" aria-label="Range">\n    <button class="segment" aria-pressed="true"><span>Day</span></button>\n    <button class="segment" aria-pressed="false"><span>Week</span></button>\n    <button class="segment" aria-pressed="false"><span>Month</span></button>\n  </div>\n</div>'),
    ("fields", "Fields and badges", "<code>field</code> is the box; the input inside stays bare. Wrap a badge's text in a <code>span</code>.",
     '<div class="flex flex-col gap-md max-w-form">\n  <div class="flex flex-col gap-2xs">\n    <label for="cv-email" class="text-sm font-medium">Email</label>\n    <div class="field">\n      <i class="icon ph ph-envelope-simple fg-neutral-11" aria-hidden="true"></i>\n      <input id="cv-email" type="email" class="grow min-w-0 h-full p-0 border-0 bg-transparent fg-neutral-12" placeholder="ada@example.com">\n    </div>\n  </div>\n  <div class="flex flex-wrap gap-2xs">\n    <span class="badge badge-neutral"><span>Draft</span></span>\n    <span class="badge badge-success"><i class="icon icon-sm ph-bold ph-check"></i><span>Paid</span></span>\n    <span class="badge badge-warning"><span>Pending</span></span>\n    <span class="badge badge-danger"><span>Failed</span></span>\n    <span class="badge badge-info"><span>New</span></span>\n  </div>\n</div>'),
    ("cards", "Cards", "<code>card</code> pads and rounds; lay its content out with utilities.",
     '<div class="card flex flex-col gap-xs max-w-form">\n  <h3 class="text-base font-semibold">Weekly report</h3>\n  <p class="fg-neutral-11">Six pages changed and two components were added.</p>\n  <div class="flex gap-xs pt-xs">\n    <button class="btn btn-primary"><span>Open</span></button>\n    <button class="btn btn-ghost"><span>Later</span></button>\n  </div>\n</div>'),
]


DEFAULTS_DEMO = """<form class="flex flex-col gap-md max-w-form" onsubmit="return false">
  <div>
    <label for="df-name">Team name</label>
    <input id="df-name" value="Design Ops">
  </div>
  <div>
    <label for="df-role">Default role</label>
    <select id="df-role"><option>Member</option><option>Admin</option></select>
  </div>
  <div>
    <label for="df-note">Note</label>
    <textarea id="df-note" rows="2" placeholder="Shown on invitations"></textarea>
  </div>
  <label><input type="checkbox" checked> Let anyone with a company email join</label>
  <label><input type="checkbox" role="switch"> Weekly digest</label>
  <input type="range" value="60" aria-label="Seats">
  <table>
    <tr><th>Member</th><th>Role</th></tr>
    <tr><td>Ada Lovelace</td><td>Owner</td></tr>
  </table>
  <p>Read the <a href="#">invitation policy</a>.</p>
  <div class="flex gap-xs">
    <button type="button">Cancel</button>
    <button type="submit">Save</button>
  </div>
</form>"""

BARE_DEMO = """<h3>A heading</h3>
<p>A paragraph with <a href="#">a link</a>, <code>inline code</code> and a <kbd>⌘K</kbd> key. Text wraps without leaving one word alone on the last line.</p>
<ul><li>A list keeps its markers</li><li>and its indent</li></ul>
<table><tr><th>Plan</th><th>Seats</th></tr><tr><td>Team</td><td>20</td></tr></table>
<p><button type="button">Button</button> <input placeholder="Input" aria-label="Input"> <select aria-label="Select"><option>Select</option></select></p>
<p><label><input type="checkbox" checked> Checkbox</label> <label><input type="radio" checked> Radio</label> <label><input type="checkbox" role="switch" checked> Switch</label></p>
<p><input type="range" value="40" aria-label="Range"> <progress value="60" max="100">60%</progress> <meter value="0.8" min="0" max="1" low="0.3" high="0.7" optimum="0.2">80%</meter></p>"""


def resets_page():
    dm = _m("nowind.defaults.manifest.json")
    rows = [[f"<code>{E(t['token'])}</code>", f"<code>{E(t['fallback'])}</code>", E(t["use"])] for t in dm["tokens"]]
    art = "\n        ".join([
        page_head("Docs", "Resets",
                  "Nowind starts from a reset that clears the browser's styles, then a layer of element defaults that gives bare buttons, fields and tables a finished look. Both sit in early layers, under <code>:where()</code>, so your CSS and any class win."),
        section("reset", "The reset",
                p("Every element gets <code>box-sizing: border-box</code> and zero-width solid borders, so a <code>border</code> class sets only the width. Headings take the heading roles unless a <code>text-*</code> class sizes them. Links keep their underline, and text wraps with balanced headings and pretty paragraphs. Checkboxes, radios, switches, sliders, progress and meter are drawn from the theme. Buttons start transparent and unpadded; the element defaults below then style them. Focus draws a ring, interactive elements transition, and reduced motion turns that off."),
                p("The example below has no classes: it is what the reset and the element defaults give you together."),
                *live("bare.html", BARE_DEMO, semantic=True)),
        section("defaults", "Element defaults",
                p("The <code>defaults</code> layer gives bare elements a finished look: buttons, text fields, selects, textareas, checkboxes, radios, switches, sliders, links, labels and table cells. A button with <code>type=\"submit\"</code> takes the primary fill. Nothing below carries a class, except the form's layout."),
                p("The defaults fill only what an element's classes leave unset, so a utility class still wins, and a utility-built control picks up a default for any property it doesn't set."),
                *live("defaults.html", DEFAULTS_DEMO)),
        section("tokens", "Default tokens", p("No token is declared, so each one is free to set. Its fallback resolves at the element, so it follows the element's scope and tier."),
                table(["Token", "Fallback", "Use"], rows)),
        section("override", "Override a default",
                p("Four ways, from widest to narrowest. A token on <code>:root</code> changes every element; on a region, only that region; a rule in <code>@layer styles</code> beats the defaults outright; a utility class changes one element."),
                code("override.css", "CSS", ":root { --button-radius: 9999px; }               /* everywhere */\n.settings { --field-border: var(--border); }       /* one region */\n@layer styles { button { font-weight: 600; } }     /* beats the defaults layer */"),
                code("override.html", "HTML", '<button class="rounded-none">Square</button>      <!-- one element: the class wins -->')),
        section("layers", "Layers",
                p("Nowind declares <code>@layer reset, defaults, styles, components, nowind</code>. The reset sits in <code>reset</code> and the element defaults in <code>defaults</code>; put your own CSS in <code>styles</code>, where it beats both; the optional convenience classes fill <code>components</code>; the utilities in <code>nowind</code> win over all of them."),
                code("layers.css", "CSS", "@layer styles {\n  .site-nav { display: flex; gap: var(--space-md); }\n}")),
    ])
    return doc_page("resets.html", "Resets", art)


def convenience_page():
    m = _m("nowind.components.manifest.json")
    rows = [[f"<code>{E(c['class'])}</code>", f"<code>{E(c['recipe'])}</code>", E(c["use"])] for c in m["classes"]]
    demos = [section(sid, label, p(intro),
                     f"""<div data-example class="tier-product p-surface rounded-md border border-weak bg-strong">
{html_}
          </div>""",
                     code(f"{sid}.html", "HTML", html_)) for sid, label, intro, html_ in CONV_DEMOS]
    art = "\n        ".join([
        page_head("Docs", "Convenience classes",
                  "The stacks that repeat most in the examples, as single classes in an optional second file. Each is written from its utility recipe and checked to render the same in every state, and any utility you add still wins. The rest of these docs show the utilities, so you can always see what a class is made of."),
        section("link", "Link it", p("After the main stylesheet. The classes sit in a <code>components</code> layer that comes before the utilities."),
                code("index.html", "HTML", '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kimgranlund/nowind@v__VERSION__/dist/nowind.min.css">\n<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kimgranlund/nowind@v__VERSION__/dist/nowind.components.min.css">')),
        *demos,
        section("defaults", "Element defaults", p('For markup with no classes at all, the <a href="resets.html#defaults">Resets</a> page shows the <code>defaults</code> layer, which styles bare buttons, fields and tables from overridable tokens.')),
        section("recipes", "Recipes", p("Every class and the utility stack it is. A utility on the element overrides any part: <code>btn btn-primary rounded-full</code> is a pill."),
                table(["Class", "Recipe", "Use"], rows)),
    ])
    return doc_page("convenience.html", "Convenience classes", art, head_extra='<link rel="stylesheet" href="../../dist/nowind.components.css">\n')


def states_page():
    css = open(os.path.join(ROOT, "nowind.css")).read()
    def count(prefix):
        return len(set(re.findall(r"\." + re.escape(prefix[:-1]) + r"\\:([a-z0-9-]+)", css)))
    nm = _m("nowind.manifest.json")
    rows = [[f"<code>{v}</code>", f"<code>{E(sel)}</code>", E(what), str(count(v))] for v, sel, what in STATE_DOCS]
    grows = [[f"<code>{v}</code>", E(when), str(count(v))] for v, when in GROUP_DOCS]
    toc = [("states", "State variants"), ("groups", "Group variants"), ("breakpoints", "Breakpoints"), ("containers", "Container queries"), ("layer", "State layer"), ("motion", "Transitions and focus"), ("indicators", "Indicators")]
    art = "\n        ".join([
        page_head("Docs", "States and variants",
                  "A variant applies a class only in a state: <code>hover:bg-neutral-4</code>, <code>selected:border-accent-1-8</code>, <code>md:flex</code>. Each variant covers a fixed set of classes, mostly colours, so the stylesheet stays one file. The markup drives the look: set the ARIA attribute and the class follows."),
        section("states", "State variants", table(["Variant", "Matches", "Applies to", "Classes"], rows)),
        section("selected", "Selected, pressed and current", p("Tabs read <code>aria-selected</code>, segments <code>aria-pressed</code>, the current page <code>aria-current</code>. Hover any of them: a chosen item never looks hovered."),
                *live("selected.html", STATE_DEMOS["selected"])),
        section("native", "Checked, invalid and disabled", p("These follow the browser's own state: tick a box, flip the switch, or leave a field invalid and move on (<code>:user-invalid</code>)."),
                *live("native.html", STATE_DEMOS["native"])),
        section("groups", "Group variants", p("Put <code>group</code> on a parent; a child reacts to its state. These cover opacity, visibility, rotation and the text roles. Hover or focus the link for its tooltip; open the menu and its caret turns."),
                table(["Variant", "When", "Classes"], grows), *live("groups.html", STATE_DEMOS["groups"])),
        section("breakpoints", "Breakpoints", p(_plain(nm["variants"]["responsive"])), p("Resize the window: one column, two from 640px, four from 1536px."),
                *live("breakpoints.html", STATE_DEMOS["breakpoints"])),
        section("containers", "Container queries", p(_plain(nm["variants"]["container"])), p("The same card twice: in the narrow column it stacks, in the wide one it turns into a row, at one window width."),
                *live("containers.html", STATE_DEMOS["containers"])),
        section("layer", "State layer", p(_plain(nm["categories"]["state"])), p("Hover and press each: one layer tints every fill, in its own text colour."),
                *live("layer.html", STATE_DEMOS["layer"])),
        section("motion", "Transitions and focus",
                p("Every interactive element (links, buttons, summaries, fields, labels, and the button, tab, option, menuitem and switch roles) transitions its colours, opacity, shadow and transforms by default, at the motion duration and easing. Reduced motion cuts it. Anything else that changes with state names <code>transition</code>."),
                p("Focus: buttons, links and checkable controls get a 2px accent ring on <code>:focus-visible</code>. A text field draws the ring over its own border, so a border class can't hide it, and a field box (<code>cursor-text</code>) draws it on the box while its bare input draws none."),
                p("Hover to see the fade, then press Tab to walk the ring along the toolbar."), *live("motion.html", STATE_DEMOS["motion"])),
        section("indicators", "Indicators", p("An indicator follows the state it shows. A caret turns over when its disclosure or menu opens: put <code>group</code> on the <code>details</code> or on the wrapper holding the button and its popover."), p("Open each row: its caret turns with it."),
                *live("indicators.html", STATE_DEMOS["indicators"])),
    ])
    return doc_page("states.html", "States and variants", art)

def materials_page():
    mm = _m("theme/theme.materials.manifest.json")
    rows = [[f"<code>material-{k}</code>", E(v)] for k, v in mm["materials"].items()]
    toc = [("materials", "Materials"), ("reliefs", "Parts"), ("glass", "Glass and the lens"), ("backdrops", "Backdrops")]
    art = "\n        ".join([
        page_head("Docs", "Materials",
                  "A material is how a region is painted: flat, lit, frosted, clear glass or outlined. It never changes a length, so switching material moves nothing. Set it once on a region; every part inside paints itself by what it is."),
        section("materials", "Materials", table(["Class", "What it does"], rows), p("The same form in each material, over a dot grid so you can see what each does with what is behind it. Hover and press the buttons."), *live("materials.html", MATERIAL_DEMOS["materials"], semantic=True, frame="relative overflow-hidden")),
        section("reliefs", "Parts", p(_plain(mm["usage"])), p("One physical panel, each part labelled with its relief."),
                *live("reliefs.html", MATERIAL_DEMOS["reliefs"], semantic=True)),
        section("glass", "Glass and the lens", p(_plain(mm["materials"]["glass"])), p(_plain(mm["glass"]["lens"])),
                *live("glass.html", MATERIAL_DEMOS["glass"], semantic=True),
                code("lens.html", "HTML", '<div class="material-glass relief-ground lens rounded-md">…</div>\n<!-- the page provides the filter and sets data-lens="on" on <html> where the engine can draw it;\n     on this site, site.js does both -->'),
                callout("note", "Only Chromium applies an SVG filter behind an element. Elsewhere glass keeps its blur, so text over it must read without the lens.")),
        section("backdrops", "Backdrops", p("Glass needs something behind it to bend. <code>bg-dots</code> paints a dot grid in <code>currentColor</code>, spaced by <code>bg-dots-xs</code>, <code>-sm</code>, <code>-md</code> or <code>-lg</code>: the showcase sets its materials on one."),
                *live("backdrops.html", MATERIAL_DEMOS["backdrops"], semantic=True)),
    ])
    return doc_page("materials.html", "Materials", art)

# ---------------------------------------------------------------- component docs
def classes_of(snippet):
    """The utility classes a snippet uses, sorted (Phosphor's icon classes left out)."""
    found = {c for cls in re.findall(r'class="([^"]+)"', snippet) for c in cls.split() if not c.startswith("ph")}
    return sorted(found)


def component_page(c):
    name = f"c-{c['slug']}.html"
    toc_items = [("example", "Example"), ("usage", "Usage"), ("classes", "Classes")]
    extras = c.get("examples", [])
    all_html = c["html"] + "".join(x["html"] for x in extras)
    chips = " ".join(f'<a href="{class_page_of(k.split(":")[-1])}#{class_id(k.split(":")[-1])}" class="inline-flex items-center h-nested px-nested rounded-xs bg-strong border border-weak hover:border-strong no-underline fg text-mono-sm whitespace-nowrap transition-colors">{E(k)}</a>' for k in classes_of(all_html))
    def example(sid, label, html_, summary=None):
        return section(sid, label, *([p(summary)] if summary else []),
            f"""<div data-example class="tier-product p-surface rounded-md border border-weak bg-strong">
{html_}
          </div>""",
            code(f"{c['slug']}-{sid}.html" if sid != "example" else f"{c['slug']}.html", "HTML", html_))
    use = "\n".join(f'            <li class="flex gap-gutter"><i class="icon ph ph-check fg-success-weak"></i><span>{t}</span></li>' for t in c["use"])
    avoid = "\n".join(f'            <li class="flex gap-gutter"><i class="icon ph ph-x fg-danger-weak"></i><span>{t}</span></li>' for t in c["avoid"])
    art = "\n        ".join([
        page_head(c["group"], c["name"], c["summary"]),
        example("example", "Example", c["html"]),
        *[example(x["id"], x["label"], x["html"], x.get("summary")) for x in extras],
        section("usage", "Usage",
            f"""<div class="grid grid-cols-1 md:grid-cols-2 gap-grid">
            <div class="flex flex-col gap-field"><span class="text-label fg-success-weak">Use</span><ul role="list" class="flex flex-col gap-xs text-body-md max-w-text">
{use}
            </ul></div>
            <div class="flex flex-col gap-field"><span class="text-label fg-danger-weak">Avoid</span><ul role="list" class="flex flex-col gap-xs text-body-md max-w-text">
{avoid}
            </ul></div>
          </div>""",
        ),
        section("classes", "Classes",
            p(f"Every class in the examples, {len(classes_of(all_html))} in all. Each one links to its declarations in <a href=\"classes.html\">Classes</a> or <a href=\"semantic.html\">Semantic classes</a>."),
            f'<div class="flex flex-wrap gap-2xs">{chips}</div>',
        ),
    ])
    return doc_page(name, c["name"], art, toc_items)


def components_index():
    groups = []
    for g in dict.fromkeys(c["group"] for c in COMPONENTS):
        cards = "\n".join(
            f"""            <a href="c-{c['slug']}.html" class="flex flex-col gap-3xs min-w-0 p-surface border border-weak hover:border-strong hover:bg-component-weak no-underline fg transition-colors">
              <span class="inline-flex items-center gap-gutter text-subtitle"><i class="icon ph {c['icon']} fg-accent-1-weak"></i><span>{c['name']}</span></span>
              <span class="text-body-sm fg-weak break-words">{c['summary']}</span>
            </a>""" for c in COMPONENTS if c["group"] == g)
        sid = g.lower().replace(" ", "-")
        groups.append((sid, g, f'<div class="grid grid-cols-1 md:grid-cols-2 gap-grid">\n{cards}\n          </div>'))
    art = "\n        ".join(
        [page_head("Components", "Components",
                   f"{len(COMPONENTS)} components, each a single snippet of HTML built only from Nowind utility classes. Every page shows the component live, its code to copy, when to use it and the classes it uses.")]
        + [section(sid, g, body) for sid, g, body in groups])
    return doc_page("components-index.html", "Components", art, [(sid, g) for sid, g, _ in groups], wide=True)

SIZE_RE = re.compile(r"text-(xs|sm|base|lg|xl|[2-6]xl)")


_FILE_SOURCES = None  # set by --lint-file: (path, html) pairs checked in place of the examples


def example_sources():
    """(where, html) for every component snippet and every showcase block that is not a semantic demo."""
    if _FILE_SOURCES is not None:
        return _FILE_SOURCES
    out = [(f"scripts/component_docs.py {c['slug']} {x['id']}", x["html"]) for c in COMPONENTS for x in [{"id": "example", "html": c["html"]}] + c.get("examples", [])]
    out += [(f"scripts/templates.py states {k}", STATE_DEMOS[k]) for k in ("breakpoints", "containers")]
    page = open(os.path.join(OUT, "..", "components.html")).read()
    body = 'md:col-span-9 min-w-0 flex flex-col gap-group">'
    for m in re.finditer(r'<section id="([^"]+)"(.*?)\n  </section>', page, flags=re.S):
        sec = m.group(0)
        if "data-semantic-demo" not in sec[:80] and body in sec:
            out.append((f"site/components.html #{m.group(1)}", sec[sec.index(body) + len(body):]))
    return out


def type_audit():
    """Check every text-bearing element in the examples against the size contract in theme.type-roles.manifest.json
    (sizeContract). Each element gets a kind from its tag, role, classes and content; its effective size (its own
    text-* class, else the nearest ancestor's, else text-base) must be the kind's size. Returns (findings, unclassified)."""
    VOID = {"input", "img", "br", "hr", "meta", "link", "source", "wbr", "col"}
    WANT = {"inline": set(), "navigation": {"base"}, "control": {"base"}, "option label": {"base"}, "cell": {"base"}, "header": {"sm"}, "label": {"sm"}, "supporting": {"sm"},
            "body": {"base"}, "title": {"base"}, "dialog title": {"lg"}, "badge": {"sm"}, "count": {"xs"}, "keycap": {"sm"}, "kicker": {"xs"}, "figure": {"3xl"}}

    class Node:
        def __init__(self, tag, attrs, parent):
            self.tag, self.attrs, self.parent = tag, attrs, parent
            self.toks = (attrs.get("class") or "").split()
            self.own = next((m.group(1) for t in self.toks for m in [SIZE_RE.fullmatch(t)] if m), None)
            self.text, self.kids = "", []
        def ancestors(self):
            n = self.parent
            while n: yield n; n = n.parent
        def eff(self):
            return self.own or next((a.own for a in self.ancestors() if a.own), None) or "base"
        def alltext(self):
            return self.text + "".join(k.alltext() for k in self.kids)
        def has(self, pred):
            return any(pred(k) or k.has(pred) for k in self.kids)

    def is_control(n):
        role = n.attrs.get("role", "")
        sized = bool({"h-control", "h-nested", "size-control", "size-nested"} & set(n.toks)) and n.tag in ("a", "button", "div", "td", "input")
        return n.tag in ("button", "select", "summary", "textarea", "input") or role in ("tab", "option", "menuitem") or sized or "cursor-text" in n.toks

    def kind(n):
        if any(is_control(a) or a.tag == "kbd" for a in n.ancestors()): return None  # text inside a control or keycap is the control's
        if n.tag == "kbd": return "keycap"
        if any(a.tag == "th" for a in n.ancestors()) and is_control(n): return "header"  # a sort button is the header's text
        if n.tag == "th" and not n.text.strip() and n.has(is_control): return None  # its button carries the kind
        if "font-display" in n.toks: return "figure"
        if "uppercase" in n.toks: return "kicker"
        if is_control(n):
            field = n.tag in ("input", "textarea", "select") or "cursor-text" in n.toks or n.has(lambda k: k.tag in ("input", "textarea", "select"))
            return "control" if field or n.alltext().strip() else None  # an icon-only button has no text to size
        if n.has(is_control) and any(t.startswith("bg-") for t in n.toks) and not n.text.strip() and "rounded-full" not in n.toks: return "control"  # a menu or popover of controls (a chip holding a remove button is a badge)
        if n.tag == "th": return "header"
        if n.tag == "td": return "cell"
        if n.tag == "label" and n.has(lambda k: k.tag == "input" and k.attrs.get("type") in ("checkbox", "radio")): return "option label"
        if n.tag in ("label", "legend", "dt") and not n.text.strip(): return None  # a wrapper: its text children carry the kinds
        if n.tag in ("label", "legend", "dt") or (n.tag == "dl" and n.own): return "label"
        if "rounded-full" in n.toks and "size-nested" in n.toks and "tabular-nums" in n.toks: return "count"
        if "rounded-full" in n.toks and n.alltext().strip(): return "badge"
        if n.tag == "h1": return None  # a page heading takes the heading roles, not a surface title
        if n.tag in ("h2", "h3", "h4"):
            return "dialog title" if any(a.tag == "dialog" or a.attrs.get("role") == "dialog" for a in n.ancestors()) else "title"
        if n.tag == "p": return "body"
        navlist = lambda a: a.tag in ("ol", "ul") and any(b.tag == "nav" for b in a.ancestors())
        if any(navlist(a) for a in n.ancestors()): return None  # links and items in a navigation list take the list's size
        if navlist(n): return "navigation"
        if n.tag in ("span", "div", "li", "ol", "ul", "a") and n.alltext().strip():
            if n.parent and n.parent.text.strip(): return None  # inline in a sentence: takes the sentence's size
            if n.attrs.get("role") == "tooltip" or (("absolute" in n.toks or any(t.startswith("anchor-") for t in n.toks)) and any(t.startswith("bg-") for t in n.toks)): return "supporting"
            if "font-semibold" in n.toks or "font-bold" in n.toks: return "title"
            if "font-medium" in n.toks and (n.tag == "span" or "justify-between" in n.toks):
                sib = n.parent.kids[n.parent.kids.index(n) + 1] if n.parent and n.parent.kids.index(n) + 1 < len(n.parent.kids) else None
                if sib is not None and sib.tag in ("span", "p") and not sib.kids: return "title"  # heads a line of detail: a toast or item title
                return "label"  # names a group or a meter, as a field label does
            if any(re.fullmatch(r"fg-[a-z]+(-\d)?-(8|11)", t) for t in n.toks): return "supporting"
            if n.own: return "body"
        return None

    findings, unclassified = [], []
    for where, html_ in example_sources():
        nodes = []
        class P(HTMLParser):
            def __init__(self): super().__init__(); self.cur = None
            def handle_starttag(self, tag, attrs):
                n = Node(tag, dict(attrs), self.cur); nodes.append(n)
                if self.cur: self.cur.kids.append(n)
                if tag not in VOID: self.cur = n
            def handle_data(self, d):
                if self.cur: self.cur.text += d
            def handle_endtag(self, tag):
                n = self.cur
                while n and n.tag != tag: n = n.parent
                if n: self.cur = n.parent
        P().feed(html_)
        for n in nodes:
            if "scope" in n.toks or any("scope" in a.toks for a in n.ancestors()):
                continue  # a scope sets its own base size: sizes inside it are relative to that base
            k = kind(n)
            label = f"<{n.tag} class=\"{' '.join(n.toks)[:70]}\">"
            if k and n.eff() not in WANT[k]:
                findings.append((where, k, n.eff(), "/".join(sorted(WANT[k])), label))
            elif not k and n.own and n.parent and n.parent.text.strip():
                if n.own != n.parent.eff(): findings.append((where, "inline", n.own, n.parent.eff(), label))
            elif not k and n.own and not any(is_control(a) for a in n.ancestors()):
                unclassified.append((where, n.own, label))
    return findings, unclassified


def parse_tree(html_):
    """A light element tree: nodes with tag, attrs, classes, direct text, parent and children."""
    VOID = {"input", "img", "br", "hr", "meta", "link", "source", "wbr", "col"}

    class Node:
        def __init__(self, tag, attrs, parent):
            self.tag, self.attrs, self.parent = tag, attrs, parent
            self.toks = (attrs.get("class") or "").split()
            self.text, self.kids = "", []
        def ancestors(self):
            n = self.parent
            while n: yield n; n = n.parent
        def alltext(self):
            return self.text + "".join(k.alltext() for k in self.kids)

    nodes = []

    class P(HTMLParser):
        def __init__(self): super().__init__(); self.cur = None
        def handle_starttag(self, tag, attrs):
            n = Node(tag, {k: (v or "") for k, v in attrs}, self.cur); nodes.append(n)
            if self.cur: self.cur.kids.append(n)
            if tag not in VOID: self.cur = n
        def handle_data(self, d):
            if self.cur: self.cur.text += d
        def handle_endtag(self, tag):
            n = self.cur
            while n and n.tag != tag: n = n.parent
            if n: self.cur = n.parent
    P().feed(html_)
    return nodes


def paint_audit():
    """Check every palette class in the examples against the paint contract (paintContract in
    theme/theme.colors.manifest.json): each class's step must suit its job (fill, border, text, icon), and text and
    icons on a solid fill take that palette's contrast token. Returns a list of (where, rule, problem, element)."""
    PAL = r"(neutral|accent-\d|danger|warning|success|info)"
    CLS = re.compile(rf"(?:([a-z-]+):)?(bg|fg|border(?:-[trblsexy])?)-{PAL}-(a?\d+|contrast)")
    WB = re.compile(r"(?:([a-z-]+):)?(bg|fg)-(white|black)")
    num = lambda st: int(st.lstrip("a"))
    def base_bg(n):
        """The base (unvariant) fill class on n, as (palette, step) or ("wb", colour)."""
        for t in n.toks:
            m = CLS.fullmatch(t)
            if m and not m.group(1) and m.group(2) == "bg": return (m.group(3), m.group(4))
            m = WB.fullmatch(t)
            if m and not m.group(1) and m.group(2) == "bg": return ("wb", m.group(3))
        return None
    out = []
    for where, html_ in example_sources():
        for n in parse_tree(html_):
            label = f"<{n.tag} class=\"{' '.join(n.toks)[:70]}\">"
            icon = n.tag == "i" or "icon" in n.toks
            surface = next((b for b in (base_bg(a) for a in [n, *n.ancestors()]) if b), None)
            plain = surface and surface[0] != "wb" and not surface[1].startswith("a")
            inverse = plain and num(surface[1]) >= 11
            solid = plain and num(surface[1]) in (9, 10)
            ring = "rounded-full" in n.toks and "border-2" in n.toks
            for t in n.toks:
                m = CLS.fullmatch(t)
                if not m: continue
                variant, prop, pal, st = m.groups()
                prop = prop.split("-")[0]
                if st == "contrast": continue
                k, alpha = num(st), st.startswith("a")
                if prop == "bg":
                    ok = k <= 5 if alpha else (k <= 5 or k in (9, 10))
                    if not ok and k >= 11 and not alpha:
                        ok = any(re.fullmatch(rf"fg-{PAL}-(1|2|contrast)|fg-(white|black)", x) for x in n.toks) or not n.alltext().strip()
                    if not ok: out.append((where, "step-by-job", f"fill {t} (fills take 1–5, 9–10, a1–a5; 11–12 only as an inverse surface with fg 1–2)", label))
                elif prop == "border":
                    ok = (5 <= k <= 8) or (k <= 2 and not alpha and ring)
                    if not ok: out.append((where, "step-by-job", f"border {t} (borders take 5–8; 1–2 only as a cut-out ring)", label))
                else:
                    ok = k >= 6 if icon else (k in (8, 11, 12) or (k <= 2 and (inverse or bool(variant))))
                    if not ok: out.append((where, "step-by-job", f"{'icon' if icon else 'text'} {t} ({'icons take 6–12' if icon else 'text takes 11–12, 8 when quiet, 1–2 on an inverse surface'})", label))
                    if solid and not variant and surface[0] != pal and (icon or n.alltext().strip()):
                        out.append((where, "on-solid", f"{t} on a solid {surface[0]}-{surface[1]} fill (use fg-{surface[0]}-contrast, fg-white or fg-black)", label))
    return out


def behaviour_audit():
    """Check the behaviour contract's static rule (theme/theme.behaviour.manifest.json, variant-attribute): an element
    with an on-state variant carries the attribute or element that fires it, so the variant can ever apply.
    Returns a list of (where, rule, problem, element)."""
    FIELDS = ("input", "select", "textarea")
    def has_desc(n, pred):
        return any(pred(k) or has_desc(k, pred) for k in n.kids)
    NEEDS = {
        "pressed": ("aria-pressed", lambda n: "aria-pressed" in n.attrs),
        "selected": ("aria-selected or role tab, option, row or gridcell", lambda n: "aria-selected" in n.attrs or n.attrs.get("role") in ("tab", "option", "row", "gridcell")),
        "current": ("aria-current, or a link", lambda n: "aria-current" in n.attrs or n.tag == "a"),
        "expanded": ("aria-expanded", lambda n: "aria-expanded" in n.attrs),
        "open": ("details, dialog or popover", lambda n: n.tag in ("details", "dialog") or "popover" in n.attrs),
        "invalid": ("a field, or aria-invalid", lambda n: n.tag in FIELDS or "aria-invalid" in n.attrs),
        "has-invalid": ("a field inside", lambda n: has_desc(n, lambda k: k.tag in FIELDS)),
        "disabled": ("a control that can be disabled, or aria-disabled", lambda n: n.tag in ("button", "fieldset", "option", "optgroup") + FIELDS or "aria-disabled" in n.attrs),
        "has-checked": ("a checkbox or radio inside", lambda n: has_desc(n, lambda k: k.tag == "input" and k.attrs.get("type") in ("checkbox", "radio"))),
    }
    out = []
    for where, html_ in example_sources():
        for n in parse_tree(html_):
            seen = set()
            for t in n.toks:
                v = t.split(":")[0] if ":" in t else None
                if v in NEEDS and v not in seen:
                    seen.add(v)
                    what, ok = NEEDS[v]
                    if not ok(n):
                        out.append((where, "variant-attribute", f"{v}: variants without {what}, so they never apply", f"<{n.tag} class=\"{' '.join(n.toks)[:70]}\">"))
    return out


def geometry_audit():
    """Check every part in the examples against the geometry contract (geometryContract in
    theme/theme.geometry.manifest.json): each part gets a kind, and its height, padding, gap and corner classes must be
    the kind's. Returns a list of (where, kind, problem, element)."""
    H = lambda t: re.fullmatch(r"h-(control|nested|full|header)|size-(control|nested)|min-h-.+", t)
    PAD = lambda t: re.fullmatch(r"p[xytbse]?-[a-z0-9]+", t)
    GAP = lambda t: re.fullmatch(r"gap-[a-z0-9-]+", t) and not t.startswith(("gap-x-", "gap-y-"))
    RAD = lambda t: re.fullmatch(r"rounded(-[a-z]+)?", t) and not re.fullmatch(r"rounded-[se]-.+|rounded-[tblr]+-.+", t)

    def is_ctrl(n):
        return n.tag in ("button", "select", "summary") or n.attrs.get("role") in ("tab", "option", "menuitem") or (n.tag == "a" and bool({"h-control", "h-nested", "size-control", "size-nested", "h-full"} & set(n.toks)))

    def kind(n):
        t, toks, role = n.tag, set(n.toks), n.attrs.get("role", "")
        if any(a.tag == "kbd" for a in n.ancestors()): return None
        if "scope" in toks or any("scope" in a.toks for a in n.ancestors()): return None
        if t == "kbd": return "keycap"
        if "border-2" in toks and "h-control" in toks and role in ("group", "toolbar"): return "control box"
        if is_ctrl(n) and {"p-0", "border-0"} <= toks: return None  # a bare slot (select, selectedcontent) inside a field box: the box owns the geometry
        if is_ctrl(n) and any(a.tag in ("th", "td") for a in n.ancestors()) and not toks & {"h-control", "h-nested", "size-control", "size-nested"}: return "control in a cell"
        if is_ctrl(n):
            if "h-full" in toks: return "item in a control box"
            if toks & {"h-nested", "size-nested"}: return "small control"
            if t == "summary" and not toks & {"h-control", "size-control"}: return None  # a disclosure row, not a control
            if role == "tab" or "border-b-2" in toks: return "tab"
            return "control"
        if "cursor-text" in toks or ("h-control" in toks and any(k.tag in ("input", "select", "textarea") for k in n.kids)): return "field box"
        if "rounded-full" in toks and n.alltext().strip() and not toks & {"size-nested", "size-control"}: return "badge"
        if "rounded-full" in toks and toks & {"size-nested", "size-control"}: return "round marker"
        if "popover" in n.attrs or ("absolute" in toks and "rounded-md" in toks): return "tooltip" if "bg-neutral-12" in toks else "popover"
        if t == "dialog" or role == "dialog": return "dialog"
        if role in ("status", "alert"):
            if "bg-neutral-12" in toks: return "toast"
            return "alert" if any(re.fullmatch(r"bg-[a-z]+-3", x) for x in toks) else None
        if t == "label" and "rounded-sm" in toks and "border" in toks: return "option card"
        if t in ("div", "article", "section", "form") and "border" in toks and any(re.fullmatch(r"rounded-(xs|sm|md|lg|xl)", x) for x in toks) and any(PAD(x) for x in toks) and not role and not "border-dashed" in toks: return "card"
        return None

    # kind: (allowed height, allowed padding, allowed gap, allowed corner); None means any, "" means none allowed
    RULES = {
        "control": ({"h-control", "size-control"}, {"px-control"}, {"gap-gutter"}, {"rounded-sm", "rounded-full", "rounded-none"}),
        "tab": ({"h-control"}, {"px-control"}, {"gap-gutter"}, {"rounded-none", "rounded-t-sm"}),
        "control in a cell": (None, set(), {"gap-gutter-half"}, set()),
        "field box": ({"h-control"}, {"px-control"}, {"gap-gutter"}, {"rounded-sm"}),
        "small control": ({"h-nested", "size-nested"}, {"px-nested"}, {"gap-gutter-half"}, {"rounded-inner", "rounded-xs", "rounded-full"}),
        "item in a control box": ({"h-full"}, {"px-nested"}, {"gap-gutter-half"}, {"rounded-inner"}),
        "control box": ({"h-control"}, set(), set(), {"rounded-sm"}),
        "badge": ({"h-nested"}, {"px-nested"}, {"gap-gutter-half"}, {"rounded-full"}),
        "round marker": ({"size-nested", "size-control"}, {"p-0"}, None, {"rounded-full"}),
        "keycap": ({"h-nested"}, {"px-2xs"}, set(), {"rounded-xs"}),
        "card": (None, {"p-md", "p-0"}, None, {"rounded-md"}),
        "option card": (None, {"p-sm"}, {"gap-sm"}, {"rounded-sm"}),
        "popover": (None, {"p-inset"}, None, {"rounded-md"}),
        "tooltip": (None, {"py-2xs", "px-xs"}, None, {"rounded-sm"}),
        "alert": (None, {"py-xs", "ps-xs", "pe-sm", "p-xs"}, {"gap-gutter", "gap-3xs"}, {"rounded-md"}),
        "toast": (None, {"p-2xs", "p-xs"}, {"gap-gutter"}, {"rounded-md"}),
        "dialog": (None, {"p-lg", "p-inset"}, {"gap-md"}, {"rounded-lg", "rounded-md"}),
    }
    REQUIRED = {"control": "h", "tab": "h", "field box": "h", "small control": "h", "item in a control box": "h", "control box": "h", "keycap": "h", "round marker": "h", "card": "r", "popover": "r", "tooltip": "r", "alert": "r", "toast": "r", "dialog": "r", "badge": "r", "option card": "r"}
    out = []
    for where, html_ in example_sources():
        for n in parse_tree(html_):
            k = kind(n)
            if not k: continue
            hs, ps, gs, rs = RULES[k]
            label = f"<{n.tag} class=\"{' '.join(n.toks)[:90]}\">"
            if k == "control" and any("border-2" in a.toks and a.toks for a in n.ancestors()):
                rs = rs | {"rounded-inner"}  # an item in a 2px-inset box nests its corner
            fams = [("height", H, hs), ("padding", PAD, ps), ("gap", GAP, gs), ("corner", RAD, rs)]
            for name, test, allowed in fams:
                have = [t for t in n.toks if test(t)]
                if allowed is None: continue
                bad = [t for t in have if t not in allowed]
                if bad: out.append((where, k, f"{name} {' '.join(bad)} (contract: {' or '.join(sorted(allowed)) or 'none'})", label))
            req = REQUIRED.get(k, "")
            if "h" in req and not any(H(t) for t in n.toks) and k != "badge":
                if not (k == "badge" and n.has_btn if hasattr(n, "has_btn") else False):
                    out.append((where, k, f"no height class (contract: {' or '.join(sorted(hs))})", label))
            if "r" in req and not any(RAD(t) for t in n.toks):
                out.append((where, k, f"no corner class (contract: {' or '.join(sorted(rs))})", label))
    return out


def lint_examples():
    """Examples use regular (primitive) classes only. Returns one line per semantic class found in a component snippet
    or in a block of the showcase, except the showcase blocks marked data-semantic-demo."""
    cat = {k: t for t, rows in read_classes() for k, _ in rows}
    props = {k: {d.split(":")[0].strip() for d in v.strip("`").split(";") if ":" in d and not d.strip().startswith("--")} for _, rows in read_classes() for k, v in rows}
    MODIFIERS = {"icon-sm", "icon-md", "icon-lg"}  # size modifiers meant to override the icon box's glyph size
    variant = re.compile(r"^(hover|active|focus-visible|focus-within|selected|current|pressed|expanded|open|invalid|has-invalid|has-checked|disabled|group-hover|group-open|group-focus-within):")
    def bad(html_, where):
        out = []
        # An element that changes with state animates the change: interactive elements get it from the reset; any
        # other element with a state or hover variant names a transition class.
        for m in re.finditer(r'<(\w+)\b([^>]*?)\sclass="([^"]*)"([^>]*)>', html_):
            tag, toks = m.group(1), m.group(3).split()
            role = re.search(r'role="(\w+)"', m.group(2) + m.group(4))
            pads = [t for t in toks if re.fullmatch(r"p[xytbse]?-[a-z0-9]+", t)]
            sides = {"p": "xytbse", "px": "se", "py": "tb"}
            for a in pads:
                for b in pads:
                    fa, fb = a.split("-")[0], b.split("-")[0]
                    if a != b and fa in sides and (fb in sides.get(fa, "") or (len(fb) == 2 and fb[1] in sides[fa])) and fa != fb:
                        out.append(f"{where}: {a} and {b} both set padding on one side; which wins depends on stylesheet order. Fix: keep one per side (ps- and pe-, or px-).")
            seen = {}
            for t in toks:
                if ":" in t or t in MODIFIERS:
                    continue
                for pr in props.get(t, ()):
                    if pr in seen and seen[pr] != t:
                        out.append(f"{where}: {seen[pr]} and {t} both set {pr}; which wins depends on stylesheet order. Fix: keep one.")
                    seen[pr] = t
            if "rounded-full" in toks and any(re.fullmatch(r"p-(3xs|2xs|xs|sm)", t) for t in toks) and re.match(r"[^<]*[A-Za-z0-9+]", html_[m.end():]) and not re.match(r"\s*<", html_[m.end():]):
                out.append(f"{where}: a round <{tag}> holding text is sized by padding, so it is an oval. Fix: size-nested or size-control (and shrink-0).")
            if tag in ("button", "a") and re.match(r"\s*<i\b[^>]*></i>\s*</" + tag + ">", html_[m.end():]) and (any(t.startswith(("px-", "py-", "h-")) and not (t == "h-full" and "aspect-square" in toks) for t in toks) or not any(re.fullmatch(r"p-[a-z0-9]+|size-[a-z0-9]+|aspect-square", t) for t in toks)):
                out.append(f"{where}: an icon-only <{tag}> isn't square. Fix: size-control or size-nested (or one padding on all sides), no px-/py-.")
            if (tag in ("button", "select") or "cursor-text" in toks or (role and role.group(1) in ("tab", "option", "menuitem"))) and any(t in ("py-xs", "py-3xs") for t in toks) and any(re.fullmatch(r"p[xse]-.+", t) for t in toks):
                out.append(f"{where}: <{tag}> is sized by padding. Fix: a control takes the control geometry (h-control px-control, h-nested px-nested; size-control or size-nested when it holds only an icon).")
            if any(t in ("h-control", "h-nested", "size-control", "size-nested") for t in toks) and any(re.fullmatch(r"gap-(3xs|2xs|xs|sm)", t) for t in toks):
                out.append(f"{where}: <{tag}> spaces its icon and label with a space step. Fix: a control uses the control gap (gap-gutter, gap-gutter-half when nested).")
            if "border" in toks and any(re.fullmatch(r"py-(3xs|2xs|xs|sm)", t) for t in toks) and re.match(r'\s*(?:<[^>]+>[^<]*</[^>]+>\s*|<[^/>][^>]*>\s*)?<(?:input|select|textarea)\b', html_[m.end():]):
                out.append(f"{where}: a field box is sized by padding. Fix: the field box geometry (flex items-center gap-gutter h-control px-control rounded-sm border … cursor-text) with a bare input inside.")
            if any(t in ("px-sm", "px-2xs") for t in toks) and re.match(r'\s*<(?:i|span)\b[^>]*class="[^"]*\bicon\b', html_[m.end():]):
                out.append(f"{where}: <{tag}> pads its icon edge like a text edge. Fix: at an icon edge use the block padding (ps-xs pe-sm for px-sm, ps-3xs pe-2xs for px-2xs).")
            if tag != "select" and any(re.fullmatch(r"(hover|active):bg-.+", t) for t in toks) and not any(re.fullmatch(r"(pressed|selected|current|open|expanded|has-checked):bg-.+", t) for t in toks):
                out.append(f"{where}: <{tag}> tints its fill with hover:/active: bg variants. Fix: use state (keep bg variants only where a state changes the surface, such as current:bg-accent-1-9).")
            if tag in ("a", "button", "summary", "input", "select", "textarea", "label") or (role and role.group(1) in ("button", "tab", "option", "menuitem", "switch")):
                continue
            physical = [t for t in toks if re.fullmatch(r"(?:[a-z0-9@-]+:)?(?:-?[pm][lr]-.+|left-.+|right-.+|text-(?:left|right)|border-[lr](?:-\d)?)", t)]
            if physical and _FILE_SOURCES is None:
                out.append(f"{where}: {' '.join(physical)} is physical. Fix: use the logical class (ps-, pe-, ms-, me-, start-, end-, text-start, text-end, border-s, border-e).")
            if any(re.fullmatch(r"ph-caret-[a-z-]+", t) for t in toks) and "icon-sm" not in toks:
                out.append(f"{where}: a caret isn't the small icon size. Fix: give it icon icon-sm.")
            if tag == "i" and any(t.startswith("ph-") for t in toks) and "icon" not in toks:
                out.append(f"{where}: an icon isn't in an icon box. Fix: give it icon (and icon-sm or icon-lg for another size).")
            if any(variant.match(t) for t in toks) and not any(t.startswith("transition") for t in toks):
                out.append(f"{where}: <{tag}> changes with state but has no transition class. Fix: add transition.")
        # The small control size belongs inside an inset container (toolbar, field, segmented control), never beside
        # full-size controls in one row.
        class Rows(HTMLParser):
            def __init__(self): super().__init__(); self.stack = [[]]; self.bad = 0
            def handle_starttag(self, tag, attrs):
                cls = (dict(attrs).get("class") or "").split()
                if tag not in ("a", "button", "select", "input", "summary"): cls = [c for c in cls if c not in ("h-nested", "size-nested")]  # a badge or marker at the small size is not a control
                self.stack[-1].append(cls)
                if tag not in ("input", "img", "br", "hr", "meta", "link", "source", "wbr", "col"): self.stack.append([])
            def handle_endtag(self, tag):
                if len(self.stack) > 1:
                    kids = self.stack.pop()
                    if any({"h-nested", "size-nested"} & set(k) for k in kids) and any({"h-control", "size-control"} & set(k) for k in kids): self.bad += 1
        rows = Rows(); rows.feed(html_)
        if rows.bad:
            out.append(f"{where}: a small control (h-nested, size-nested) sits beside full-size controls. Fix: put it in an inset container (p-inset rounded-sm), such as a toolbar, or use the full size.")
        for cls in re.findall(r'class="([^"]+)"', html_):
            for t in cls.split():
                base = t.split(":")[-1]
                if base in cat and is_semantic(cat[base], base) and _FILE_SOURCES is None:
                    out.append(f"{where}: {t} is semantic. Fix: use regular classes in examples (the step, space or size it stands for).")
        return out
    errors = []
    if _FILE_SOURCES is not None:
        for w, h in _FILE_SOURCES:
            errors += bad(h, w)
    else:
        for c in COMPONENTS:
            for x in [{"id": "example", "html": c["html"]}] + c.get("examples", []):
                errors += bad(x["html"], f"scripts/component_docs.py {c['slug']} {x['id']}")
        page = open(os.path.join(OUT, "..", "components.html")).read()
        body = 'md:col-span-9 min-w-0 flex flex-col gap-group">'
        for m in re.finditer(r'<section id="([^"]+)"(.*?)\n  </section>', page, flags=re.S):
            sec = m.group(0)
            if "data-semantic-demo" in sec[:80] or body not in sec:
                continue
            errors += bad(sec[sec.index(body) + len(body):], f"site/components.html #{m.group(1)}")
    errors += [f"{w}: {k}: {prob}. Fix: the contract's classes (geometryContract in theme/theme.geometry.manifest.json). {lab}" for w, k, prob, lab in geometry_audit()]
    errors += [f"{w}: {k}: {prob}. Fix: the paint contract (paintContract in theme/theme.colors.manifest.json). {lab}" for w, k, prob, lab in paint_audit()]
    errors += [f"{w}: {k}: {prob}. Fix: the behaviour contract (theme/theme.behaviour.manifest.json). {lab}" for w, k, prob, lab in behaviour_audit()]
    css = open(os.path.join(OUT, "..", "..", "dist", "nowind.min.css")).read()
    unesc = lambda m: re.sub(r"\\(.)", r"\1", re.sub(r"\\([0-9a-fA-F]{1,6}) ?", lambda h: chr(int(h.group(1), 16)), m))
    defined = {unesc(m) for m in re.findall(r"\.((?:[a-zA-Z0-9_-]|\\[0-9a-fA-F]{1,6} ?|\\.)+)", css)}
    for w, h in example_sources():
        for t in sorted({t for c in re.findall(r'class="([^"]*)"', h) for t in c.split()}):
            if t not in defined and not re.match(r"ph(-|$)", t):
                errors.append(f"{w}: class {t} is not in the bundle, so it does nothing. Fix: use a class Nowind defines (classes.md lists them; variants cover the steps in AGENTS.md).")
    findings, unclassified = type_audit()
    errors += [f"{w}: {k} text is text-{eff}; the size contract wants text-{want}. Fix: the contract's size (sizeContract in theme/theme.type-roles.manifest.json). {lab}" for w, k, eff, want, lab in findings]
    errors += [f"{w}: {lab} sets text-{own} but has no kind in the size contract. Fix: give it a kind's classes, or let it inherit." for w, own, lab in unclassified]
    return sorted(set(errors))


def wrap_code(text):
    """Inline code keeps each class whole (the reset sets it nowrap), but a stack of classes may wrap between them, and a
    path after each slash, so a long recipe or path in prose fits a phone. Code blocks (pre) are left as they are."""
    parts = re.split(r"(<pre\b.*?</pre>)", text, flags=re.S)
    piece = lambda t: "".join(f'<span class="whitespace-nowrap">{x}</span>' for x in re.split(r"(?<=/)(?=.)", t))
    tok = lambda m: '<code class="whitespace-normal">' + " ".join(piece(t) for t in m.group(1).split(" ")) + "</code>"
    return "".join(p if p.startswith("<pre") else re.sub(r"<code>([^<\n]*?[ /][^<\n]*?)</code>", tok, p) for p in parts)


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {"guide.html": guide(), "reference.html": reference(), "changelog.html": changelog(),
             "docs-home.html": docs_home(), "index.html": index(), "components-index.html": components_index(), "classes.html": classes_page(), "semantic.html": classes_page(True),
             "colour.html": colour_page(), "type-space.html": type_space_page(), "states.html": states_page(), "materials.html": materials_page(), "convenience.html": convenience_page(), "resets.html": resets_page()}
    files.update({f"c-{c['slug']}.html": component_page(c) for c in COMPONENTS})
    for name, text in files.items():
        text = text.replace("<code>--", '<code class="whitespace-nowrap">--')
        text = text.replace("__VERSION__", VERSION)
        text = wrap_code(text)
        with open(os.path.join(OUT, name), "w") as f:
            f.write(text)
        print("wrote", name, len(text))
    site = os.path.join(OUT, "..")
    # Hand-written pages keep their content; the band, section row, footer and search script between the markers are stamped here.
    for path in HAND_PAGES:
        fp = os.path.join(site, path)
        text = open(fp).read()
        text = re.sub(r"<!--nowind:top-->.*?<!--/nowind:top-->", lambda m: "<!--nowind:top-->\n" + top(path) + "<!--/nowind:top-->", text, flags=re.S)
        text = re.sub(r"<!--nowind:head-->.*?<!--/nowind:head-->", lambda m: "<!--nowind:head-->\n" + HEAD_EXTRA + "<!--/nowind:head-->", text, flags=re.S)
        text = re.sub(r"<!--nowind:bottom-->.*?<!--/nowind:bottom-->", lambda m: "<!--nowind:bottom-->\n" + bottom(path) + "<!--/nowind:bottom-->", text, flags=re.S)
        text = text.replace("__VERSION__", VERSION)
        with open(fp, "w") as f:
            f.write(text)
        print("stamped", path)
        files["../" + path] = text
    # The search index: every page, every block heading, every class. Rows are [title, url, kind, detail], urls relative to site/.
    rows = [[TITLES.get(pp, label), pp, "Page", sec] for sec, pages in SECTIONS for pp, label in pages]
    for c in COMPONENTS:
        rows.append([c["name"], f"docs/c-{c['slug']}.html", "Component", html.unescape(re.sub(r"<[^>]+>", "", c["summary"]))])
    for name, text in files.items():
        path = os.path.normpath(os.path.join("docs", name)).replace(os.sep, "/")
        page = TITLES.get(path, path)
        for sid, h in re.findall(r'<section id="([^"]+)"[^>]*>\s*<div[^>]*>\s*<h2[^>]*>(.*?)</h2>', text, flags=re.S):
            rows.append([html.unescape(re.sub(r"<[^>]+>", "", h)).strip(), f"{path}#{sid}", "Section", page])
    for cat, crows in read_classes():
        for k, decl in crows:
            rows.append(["." + k, f"docs/{CLASS_PAGES[is_semantic(cat, k)][0]}#{class_id(k)}", "Class", decl])
    with open(os.path.join(site, "search.json"), "w") as f:
        f.write("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]\n")
    print("wrote search.json", len(rows), "entries")
    # The component manifest: each component's contract as data, from the same source as its pages.
    comp = {"file": "site/docs/c-*.html", "generated": "scripts/templates.py from scripts/component_docs.py",
            "description": "Every component Nowind documents: where its page is, what it is for, when to use it and not, and the classes its examples use. Examples use regular classes only.",
            "components": [{"slug": c["slug"], "name": c["name"], "group": c["group"], "page": f"site/docs/c-{c['slug']}.html",
                            "summary": html.unescape(re.sub(r"<[^>]+>", "", c["summary"])),
                            "use": [html.unescape(re.sub(r"<[^>]+>", "", t)) for t in c["use"]],
                            "avoid": [html.unescape(re.sub(r"<[^>]+>", "", t)) for t in c["avoid"]],
                            "examples": ["example"] + [x["id"] for x in c.get("examples", [])],
                            "classes": classes_of(c["html"] + "".join(x["html"] for x in c.get("examples", [])))}
                           for c in BY_GROUP]}
    with open(os.path.join(site, "..", "components.manifest.json"), "w") as f:
        f.write(json.dumps(comp, indent=2, ensure_ascii=False) + "\n")
    print("wrote components.manifest.json", len(comp["components"]), "components")

if "--behaviour-report" in sys.argv:
    g = behaviour_audit()
    print(f"{len(g)} behaviour findings\n")
    for f in g: print(f"OFF  {f[0]}: {f[1]}: {f[2]}  {f[3]}")
    sys.exit(0)
if "--paint-report" in sys.argv:
    import collections
    g = paint_audit()
    print(f"{len(g)} paint findings\n")
    for (k, prob), c in collections.Counter((f[1], f[2].split(" (")[0]) for f in g).most_common():
        print(f"  {c:3}  {k:12} {prob}")
    print()
    for f in g: print(f"OFF  {f[0]}: {f[1]}: {f[2]}  {f[3]}")
    sys.exit(0)
if "--geometry-report" in sys.argv:
    import collections
    g = geometry_audit()
    print(f"{len(g)} geometry findings\n")
    for (k, prob), c in collections.Counter((f[1], f[2].split(" (")[0]) for f in g).most_common():
        print(f"  {c:3}  {k:22} {prob}")
    print()
    for f in g: print(f"OFF  {f[0]}: {f[1]}: {f[2]}  {f[3]}")
    sys.exit(0)
if "--type-report" in sys.argv:
    findings, unclassified = type_audit()
    import collections
    print(f"{len(findings)} elements off the size contract, {len(unclassified)} set a size but have no kind\n")
    for k, n in collections.Counter((f[1], f[2], f[3]) for f in findings).most_common():
        print(f"  {k[0]:13} is text-{k[1]:5} want text-{k[2]:6} x{n}")
    print()
    for f in findings: print(f"OFF  {f[0]}: {f[1]} is text-{f[2]}, want text-{f[3]}  {f[4]}")
    for u in unclassified: print(f"KIND {u[0]}: text-{u[1]}  {u[2]}")
    sys.exit(0)
def default_notes(srcs):
    """Notes, not failures: a button or field styled partly with utilities takes the element defaults (the defaults
    layer) for every part of its box its classes leave unset. Name those parts, so an author sees what they inherit."""
    props = {k: {d.split(":")[0].strip() for d in v.strip("`").split(";") if ":" in d and not d.strip().startswith("--")} for _, rows in read_classes() for k, v in rows}
    BOX = {"height": ("height", "block-size"), "padding": ("padding", "padding-inline", "padding-left", "padding-right", "padding-inline-start", "padding-inline-end"),
           "fill": ("background-color", "background"), "border": ("border-width", "border-color", "border"), "corner": ("border-radius",)}
    WANT = {"button": ["height", "padding", "fill", "border", "corner"], "field": ["height", "padding", "fill", "border", "corner"]}
    out = []
    for where, html_ in srcs:
        for n in parse_tree(html_):
            kind = "button" if n.tag == "button" and not (n.parent and n.parent.tag == "select") else "field" if n.tag in ("input", "select", "textarea") and n.attrs.get("type") not in ("checkbox", "radio", "range", "color", "file", "hidden", "button", "submit", "reset") else None
            if not kind or not n.toks:
                continue
            got = set().union(*(props.get(t, set()) for t in n.toks if ":" not in t))
            if not got:
                continue
            missing = [part for part in WANT[kind] if not any(x in got for x in BOX[part])]
            if "border-0" in n.toks and "bg-transparent" in n.toks and "corner" in missing:
                missing.remove("corner")  # no border and no fill: no corner to see
            if missing and len(missing) < len(WANT[kind]):
                out.append(f"note: {where}: <{n.tag} class=\"{' '.join(n.toks)[:60]}\"> takes the default {', '.join(missing)} (the defaults layer fills what its classes leave unset).")
    return out


def expand_convenience(html_):
    """Replace each convenience class (nowind.components.manifest.json) with the utility stack it stands for, so the
    contracts see what renders. A utility the author added wins over an expanded one that sets the same property, as
    it does in the cascade (btn rounded-full is a pill)."""
    recipes = {c["class"]: c["recipe"].split() for c in _m("nowind.components.manifest.json")["classes"]}
    props = {k: {d.split(":")[0].strip() for d in v.strip("`").split(";") if ":" in d and not d.strip().startswith("--")} for _, rows in read_classes() for k, v in rows}
    def one(m):
        toks = m.group(1).split()
        own = [t for t in toks if t not in recipes]
        owned = set().union(*(props.get(t.split(":")[-1], set()) for t in own if ":" not in t)) if own else set()
        expanded = []
        for t in toks:
            for r in recipes.get(t, []):
                if r not in expanded and r not in own and not (":" not in r and props.get(r, set()) & owned):
                    expanded.append(r)
        return 'class="' + " ".join(expanded + own) + '"'
    return re.sub(r'class="([^"]*)"', one, html_)


if "--lint-file" in sys.argv:
    paths = [a for a in sys.argv[sys.argv.index("--lint-file") + 1:] if not a.startswith("--")]
    if not paths:
        print("usage: python3 scripts/templates.py --lint-file page.html [more.html …]"); sys.exit(2)
    srcs = []
    for path in paths:
        text = open(path).read()
        body = text[text.index("<body"):] if "<body" in text else text
        body = re.sub(r"class='([^']*)'", r'class="\1"', body)  # one quote style for the rules below
        srcs.append((path, expand_convenience(body)))
    _FILE_SOURCES = srcs
    problems = lint_examples()
    notes = default_notes(srcs)
    if problems: print("\n".join(problems))
    if notes: print("\n".join(notes))
    if not problems: print(f"{len(paths)} file(s): no findings" + (f", {len(notes)} note(s)" if notes else ""))
    sys.exit(1 if problems else 0)
if "--lint" in sys.argv:
    problems = lint_examples()
    print("\n".join(problems))
    sys.exit(1 if problems else 0)
main()
