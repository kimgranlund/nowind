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
              ("docs/materials.html", "Materials"), ("docs/reference.html", "Reference"),
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
          "docs/materials.html": "Materials", "docs/docs-home.html": "Overview", "docs/guide.html": "Lay out a docs page", "docs/reference.html": "Page grid and shell",
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
<html lang="en" class="scroll-pt-header">
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
            f'<li><a href="{rel(pp, path)}"{CUR_PAGE if pp == path else ""} class="block py-3xs no-underline text-body-sm {"fg font-semibold" if pp == path else "fg-weak hover:fg"} transition-colors">{label}</a></li>'
            for pp, label in pages)
        return f'<ul role="list" class="grid {"grid-cols-2 gap-x-md" if two else "grid-cols-1"}">{lis}</ul>'
    def col(name, pages, two=False, span=""):
        return f'<div class="{span} flex flex-col gap-2xs min-w-0"><span class="text-kicker fg-weak">{name}</span>{links(pages, two)}</div>'
    sec = dict(SECTIONS)
    lead = [pp for pp in sec["Components"] if not pp[0].startswith("docs/c-")]
    def group(g):
        return (f'<div class="flex flex-col gap-3xs min-w-0"><span class="text-label fg-subtle">{g}</span>'
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
    components = (f'<div class="md:col-span-2 flex flex-col gap-2xs min-w-0"><span class="text-kicker fg-weak">Components</span>'
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
    return f"""<header class="sticky top-0 z-30 bg-inverse fg-inverse">
  <div class="flex items-center gap-lg h-header px-grid">
    <a href="{rel("index.html", path)}" class="inline-flex items-center gap-gutter-half no-underline fg-inverse"><i class="icon ph-bold ph-wind"></i><span class="text-subtitle">Nowind</span><span class="text-kicker fg-inverse-weak">__VERSION__</span></a>
    <nav aria-label="Sections" class="hidden md:flex items-center gap-lg">{secs}</nav>
    <button type="button" popovertarget="site-settings" class="inline-flex items-center justify-center size-nested ms-auto rounded-xs border border-transparent bg-transparent fg-inverse-weak hover:fg-inverse cursor-pointer transition-colors" aria-label="Display settings"><i class="icon ph ph-sliders-horizontal"></i></button>
    <div id="site-settings" popover class="anchor-bottom-end scope text-chrome w-max p-surface rounded-md bg fg border shadow-lg">
      <div class="flex flex-col gap-sm">
      <div class="flex flex-col gap-3xs">
        <span class="fg-weak">Theme</span>
        <div class="flex h-control rounded-sm border-2 border-transparent bg-component-weak" role="group" aria-label="Theme"><button type="button" data-setting="theme" data-value="light" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><i class="icon icon-sm ph ph-sun"></i><span>Light</span></button><button type="button" data-setting="theme" data-value="dark" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><i class="icon icon-sm ph ph-moon"></i><span>Dark</span></button><button type="button" data-setting="theme" data-value="system" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><i class="icon icon-sm ph ph-desktop"></i><span>System</span></button></div>
      </div>
      <div class="flex flex-col gap-3xs">
        <span class="fg-weak">Base size</span>
        <div class="flex h-control rounded-sm border-2 border-transparent bg-component-weak" role="group" aria-label="Base size"><button type="button" data-setting="size" data-value="12" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><span>12</span></button><button type="button" data-setting="size" data-value="14" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><span>14</span></button><button type="button" data-setting="size" data-value="16" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><span>16</span></button><button type="button" data-setting="size" data-value="18" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><span>18</span></button></div>
      </div>
      <div class="flex flex-col gap-3xs">
        <span class="fg-weak">Tier</span>
        <div class="flex h-control rounded-sm border-2 border-transparent bg-component-weak" role="group" aria-label="Tier"><button type="button" data-setting="tier" data-value="auto" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><span>Auto</span></button><button type="button" data-setting="tier" data-value="product" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><span>Product</span></button><button type="button" data-setting="tier" data-value="content" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><span>Content</span></button><button type="button" data-setting="tier" data-value="brand" aria-pressed="false" class="grow inline-flex items-center justify-center gap-gutter-half h-full px-nested rounded-inner border-0 bg-transparent hover:bg-component pressed:bg pressed:shadow-xs fg-weak pressed:fg font-medium cursor-pointer"><span>Brand</span></button></div>
      </div>
      </div>
    </div>
    <a href="https://github.com/kimgranlund/nowind" class="inline-flex items-center justify-center size-nested no-underline fg-inverse-weak hover:fg-inverse transition-colors" aria-label="Nowind on GitHub"><i class="icon ph ph-github-logo"></i></a>
  </div>
</header>
<div class="flex items-center gap-xs px-grid py-2xs border-b-2 border-strong bg">
  <button type="button" popovertarget="site-map" class="inline-flex items-center gap-gutter-half min-w-0 h-control px-control rounded-sm border hover:bg-component-weak bg text-title-sm cursor-pointer transition-colors" aria-label="Site map: {cur or "all pages"}">{where}<i class="icon caret fg-weak" aria-hidden="true"></i></button>
  <button type="button" data-search-open class="inline-flex items-center gap-gutter grow min-w-0 max-w-form h-control px-control rounded-sm border hover:border-strong bg-strong fg-subtle text-control-md cursor-text transition-colors" aria-label="Search the site"><i class="icon ph ph-magnifying-glass"></i><span class="grow truncate text-start">Search pages, components and classes</span><kbd class="hidden sm:inline text-mono-sm">⌘K</kbd></button>
  <span class="flex-1 hidden lg:block"></span>
  {step}
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
        cells.append(f"""          <a href="{rel(prev, path)}" class="flex flex-col gap-3xs p-surface border border-weak hover:border-strong no-underline transition-colors">
            <span class="inline-flex items-center gap-gutter-half text-kicker fg-weak"><i class="icon icon-sm ph-bold ph-arrow-left"></i><span>Previous</span></span>
            <span class="text-subtitle fg-accent-1-weak">{TITLES.get(prev, LABELS[prev])}</span>
          </a>""")
    else:
        cells.append('          <span></span>')
    if nxt:
        cells.append(f"""          <a href="{rel(nxt, path)}" class="flex flex-col items-end gap-3xs p-surface border border-weak hover:border-strong no-underline text-end transition-colors">
            <span class="inline-flex items-center gap-gutter-half text-kicker fg-weak"><span>Next</span><i class="icon icon-sm ph-bold ph-arrow-right"></i></span>
            <span class="text-subtitle fg-accent-1-weak">{TITLES.get(nxt, LABELS[nxt])}</span>
          </a>""")
    return '<nav aria-label="Previous and next page" class="col-span-12 grid grid-cols-2 gap-grid py-page border-t border-strong">\n' + "\n".join(cells) + "\n        </nav>\n"

CALLOUT = {
    "note": ("info", "ph-info", "Note"),
    "tip": ("success", "ph-check-circle", "Tip"),
    "warning": ("warning", "ph-warning", "Warning"),
}

def callout(kind, body_html):
    pal, icon, label = CALLOUT[kind]
    return f"""<aside role="note" class="flex gap-gutter p-surface border-s-4 border-{pal} bg-component-{pal}-weak">
            <i class="icon ph {icon} fg-{pal}-weak"></i>
            <div class="flex flex-col gap-3xs min-w-0">
              <span class="text-label fg-{pal}">{label}</span>
              <p class="text-body-md">{body_html}</p>
            </div>
          </aside>"""

def code(filename, lang, src):
    return f"""<figure class="flex flex-col min-w-0 border border-weak bg-strong">
            <figcaption class="flex items-center justify-between gap-row px-surface py-2xs border-b border-weak">
              <span class="text-mono-sm fg-weak truncate">{E(filename)}</span><span class="text-kicker fg-subtle">{lang}</span>
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
    return f"""<div class="border border-weak">
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
            <p class="text-body-md fg-weak max-w-measure">{intro}</p>{m}
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
    return block(sid, f'<h2 class="text-subtitle text-balance">{title}</h2>', *parts)

def subhead(t):
    return f'<h3 class="text-subtitle">{t}</h3>'

def p(t):
    return f'<p class="text-body-md max-w-measure">{t}</p>'

def ul(items):
    lis = "\n".join(f'            <li>{i}</li>' for i in items)
    return f'<ul class="flex flex-col gap-3xs ps-md list-disc text-body-md max-w-measure">\n{lis}\n          </ul>'

def doc_page(current, title, article_html, toc_items=None, wide=False, sidebar_on=True):
    """Every generated page: band and section row, the twelve-column grid of blocks, previous and next, footer."""
    path = "docs/" + current
    return (HEAD.format(title=E(title), head_extra=HEAD_EXTRA) + top(path) +
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
            p("Every page on the site has the same three parts, after Vignelli's Unigrid: an inverse band with the four sections, a bar under a heavy rule with where you are, search and the next page, and the page itself, a stack of blocks. The band sticks to the top; everything else scrolls with the page."),
            code("frame.html", "HTML", """
<html class="scroll-pt-header">
<header class="sticky top-0 z-30 bg-inverse fg-inverse">
  <div class="flex items-center gap-lg h-header px-grid">…wordmark, sections, search…</div>
</header>
<div class="flex items-center gap-xs px-grid py-2xs border-b-2 border-strong">…site map button, search, previous and next…</div>
<main class="tier-content px-grid">
  <div class="grid grid-cols-12 gap-x-grid">…page head, blocks…</div>
</main>"""),
            p("The band is <code>h-header</code> tall and follows the base size, so it grows with the type from a phone to a wide screen. <code>scroll-pt-header</code> on <code>html</code> keeps a linked block clear of it."),
            callout("note", "Keep one scroller: the page. Don't make <code>main</code> a scroll box; browsers paint very tall nested scrollers badly, and in-page links, find and the back button work against the window."),
        ),
        section("grid", "The block",
            p("Every block hangs from a label column: its label in the first three of twelve columns, its content in the other nine. A component's example, a palette and a release in the changelog all have this one shape. Below 768px the label sits above the content."),
            code("block.html", "HTML", """
<section class="col-span-12 grid grid-cols-12 gap-x-grid gap-y-2xs pt-sm pb-xl border-t border-strong">
  <div class="col-span-12 md:col-span-3"><h2 class="text-subtitle">Example</h2></div>
  <div class="col-span-12 md:col-span-9 min-w-0 flex flex-col gap-group">…</div>
</section>"""),
            table(["Width", "Sections", "Label"], [
                ["Under 768px", "In the site map", "Above the content"],
                ["768px (<code>md:</code>) and up", "In the band", "Columns 1–3, content 4–12"],
            ]),
        ),
        section("measure", "The reading column",
            p("Prose stops at <code>max-w-measure</code>, 44 times the base size. The article is a <code>tier-content</code> region, so its section gaps and page padding are one and a half times the product rhythm and its measure grows with the tier's larger base size."),
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
<aside role="note" class="flex gap-gutter p-surface border-s-4 border-info bg-component-info-weak">
  <i class="icon ph ph-info fg-info-weak"></i>
  <div class="flex flex-col gap-3xs">
    <span class="text-label fg-info">Note</span>
    <p class="text-body-md">One sentence the reader must not miss.</p>
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


def reference():
    toc_items = [("grid", "Page grid"), ("shell", "Shell lengths"), ("levels", "Container levels"),
                 ("tiers", "Tiers"), ("breakpoints", "Breakpoints")]
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
                    lis.append(f"""                <li class="flex flex-col gap-3xs"><span class="text-label fg-weak">{name}</span><p class="text-body-md">{text}</p></li>""")
                else:
                    lis.append(f"""                <li><p class="text-body-md">{text}</p></li>""")
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
        ["Band", "<code>sticky top-0 z-30 bg-inverse fg-inverse</code>; inner <code>flex items-center gap-lg h-header px-grid</code>"],
        ["Section link", "<code>h-header border-b-2 fg-inverse-weak text-title-sm</code>; current: <code>border-accent-1 fg-inverse</code>"],
        ["Site map", "A <code>popovertarget</code> button naming the section and page; the popover <code>anchor-bottom max-w-measure max-h-below-header overflow-y-auto</code>"],
        ["Search field", "A button that looks like a field: <code>grow max-w-form h-control border bg-strong cursor-text</code> with <code>data-search-open</code>"],
        ["Bar", "<code>flex items-center gap-xs px-grid py-2xs border-b-2 border-strong</code>; previous and next <code>size-control border</code>"],
        ["Main grid", "<code>tier-content px-grid</code>, inner <code>grid grid-cols-12 gap-x-grid</code>"],
        ["Page head", "<code>col-span-12 flex flex-col gap-field pt-page pb-xl</code>; title <code>text-display-sm</code>"],
        ["Block", "<code>col-span-12 grid grid-cols-12 gap-x-grid pt-sm pb-xl border-t border-strong</code>; label <code>md:col-span-3</code>, content <code>md:col-span-9</code>"],
        ["Callout", "<code>flex gap-gutter p-surface border-l-4 border-info bg-component-info-weak</code>"],
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
            p("An inverse band with the four sections, then a bar under a heavy rule with the site map, search and the next page, then the page as a stack of blocks. Only the band sticks; the page scrolls as a whole. Below 768px the sections are reached through the site map."),
        ),
        section("grid", "The grid",
            grid_strip,
            p("Twelve columns, spaced by <code>gap-grid</code> and held off the edge by <code>px-grid</code>. Every block puts its label in three columns and its content in nine; below 768px the two stack. Prose inside a block stops at <code>max-w-measure</code>."),
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
        return not re.search(r"(accent-\d|neutral|danger|warning|success|info)-(a?\d+|contrast)$|-(inherit|current|transparent)$", k)
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
    toc = [("sizes", "Type sizes"), ("roles", "Type roles"), ("faces", "Faces"), ("space", "Space")]
    art = "\n        ".join([
        page_head("Docs", "Type and space",
                  "One fluid scale for each: sizes grow with the viewport between a phone and a wide screen, and every space step is a multiple of the base size, F. Sizes are the primitives; roles name a size, weight and face for a use."),
        section("sizes", "Type sizes", p("Each <code>text-*</code> class sets the size and its line height, as Tailwind v4 does. Sizes are measured at the smallest and largest viewport."),
                table(["Class", "Sample", "Size", "Line height"], sizes)),
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
        section("states", "State variants", table(["Variant", "Matches", "Applies to", "Classes"], rows),
                code("tab.html", "HTML", '<button role="tab" aria-selected="true" class="py-xs px-sm border-b-2 border-transparent selected:border-accent-1-8 fg-neutral-11 selected:fg-neutral-12">Profile</button>')),
        section("groups", "Group variants", p("Put <code>group</code> on a parent; a child reacts to its state. These cover opacity, visibility, rotation and the text roles."),
                table(["Variant", "When", "Classes"], grows)),
        section("breakpoints", "Breakpoints", p(_plain(nm["variants"]["responsive"]))),
        section("containers", "Container queries", p(_plain(nm["variants"]["container"])),
                code("card.html", "HTML", '<div class="@container">\n  <article class="flex flex-col @md:flex-row">\n    <div class="aspect-video @md:basis-1/3 shrink-0">…</div>\n    <div class="p-md">…</div>\n  </article>\n</div>')),
        section("layer", "State layer", p(_plain(nm["categories"]["state"])),
                code("ghost.html", "HTML", '<button class="state py-xs px-sm rounded-sm bg-transparent fg-neutral-12">Ghost</button>\n<button class="state py-xs px-sm rounded-sm bg-accent-1-9 fg-accent-1-contrast">Primary</button>')),
        section("motion", "Transitions and focus",
                p("Every interactive element (links, buttons, summaries, fields, labels, and the button, tab, option, menuitem and switch roles) transitions its colours, opacity, shadow and transforms by default, at the motion duration and easing. Reduced motion cuts it. Anything else that changes with state names <code>transition</code>."),
                p("Focus: buttons, links and checkable controls get a 2px accent ring on <code>:focus-visible</code>. Text fields get no ring; their border turns accent, and a field box shows its input's focus with <code>focus-within:</code>.")),
        section("indicators", "Indicators", p("An indicator follows the state it shows. A caret turns over when its disclosure or menu opens: put <code>group</code> on the <code>details</code> or on the wrapper holding the button and its popover."),
                code("caret.html", "HTML", '<details class="group">\n  <summary class="flex items-center justify-between list-none">\n    Shipping <i class="icon icon-sm ph ph-caret-down transition group-open:rotate-180"></i>\n  </summary>\n  …\n</details>')),
    ])
    return doc_page("states.html", "States and variants", art)

def materials_page():
    mm = _m("theme/theme.materials.manifest.json")
    rows = [[f"<code>material-{k}</code>", E(v)] for k, v in mm["materials"].items()]
    toc = [("materials", "Materials"), ("reliefs", "Parts"), ("glass", "Glass and the lens"), ("backdrops", "Backdrops")]
    art = "\n        ".join([
        page_head("Docs", "Materials",
                  "A material is how a region is painted: flat, lit, frosted, clear glass or outlined. It never changes a length, so switching material moves nothing. Set it once on a region; every part inside paints itself by what it is."),
        section("materials", "Materials", table(["Class", "What it does"], rows)),
        section("reliefs", "Parts", p(_plain(mm["usage"])),
                code("material.html", "HTML", '<div class="material-frosted relief-ground p-md rounded-md">\n  <input class="relief-field …">\n  <button class="relief-raised-solid …">Invite</button>\n</div>')),
        section("glass", "Glass and the lens", p(_plain(mm["materials"]["glass"])), p(_plain(mm["glass"]["lens"])),
                code("lens.html", "HTML", '<div class="material-glass relief-ground lens rounded-md">…</div>\n<!-- the page provides the filter and sets data-lens="on" on <html> where the engine can draw it;\n     on this site, site.js does both -->'),
                callout("note", "Only Chromium applies an SVG filter behind an element. Elsewhere glass keeps its blur, so text over it must read without the lens.")),
        section("backdrops", "Backdrops", p("Glass needs something behind it to bend. <code>bg-dots</code> paints a dot grid in <code>currentColor</code>, spaced by <code>bg-dots-sm</code>, <code>-md</code> or <code>-lg</code>: the showcase sets its materials on one."),
                code("dots.html", "HTML", '<div class="bg-neutral-2 fg-accent-1-9 bg-dots bg-dots-md">…</div>')),
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
    use = "\n".join(f'            <li class="flex gap-gutter"><i class="icon icon-sm ph-bold ph-check fg-success-weak"></i><span>{t}</span></li>' for t in c["use"])
    avoid = "\n".join(f'            <li class="flex gap-gutter"><i class="icon icon-sm ph-bold ph-x fg-danger-weak"></i><span>{t}</span></li>' for t in c["avoid"])
    art = "\n        ".join([
        page_head(c["group"], c["name"], c["summary"]),
        example("example", "Example", c["html"]),
        *[example(x["id"], x["label"], x["html"], x.get("summary")) for x in extras],
        section("usage", "Usage",
            f"""<div class="grid grid-cols-1 md:grid-cols-2 gap-grid">
            <div class="flex flex-col gap-field"><span class="text-label fg-success-weak">Use</span><ul role="list" class="flex flex-col gap-xs text-body-md">
{use}
            </ul></div>
            <div class="flex flex-col gap-field"><span class="text-label fg-danger-weak">Avoid</span><ul role="list" class="flex flex-col gap-xs text-body-md">
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
            f"""            <a href="c-{c['slug']}.html" class="flex flex-col gap-3xs p-surface border border-weak hover:border-strong hover:bg-component-weak no-underline fg transition-colors">
              <span class="inline-flex items-center gap-gutter text-subtitle"><i class="icon ph {c['icon']} fg-accent-1-weak"></i><span>{c['name']}</span></span>
              <span class="text-body-sm fg-weak">{c['summary']}</span>
            </a>""" for c in COMPONENTS if c["group"] == g)
        sid = g.lower().replace(" ", "-")
        groups.append((sid, g, f'<div class="grid grid-cols-1 md:grid-cols-2 gap-grid">\n{cards}\n          </div>'))
    art = "\n        ".join(
        [page_head("Components", "Components",
                   f"{len(COMPONENTS)} components, each a single snippet of HTML built only from Nowind utility classes. Every page shows the component live, its code to copy, when to use it and the classes it uses.")]
        + [section(sid, g, body) for sid, g, body in groups])
    return doc_page("components-index.html", "Components", art, [(sid, g) for sid, g, _ in groups], wide=True)

SIZE_RE = re.compile(r"text-(xs|sm|base|lg|xl|[2-6]xl)")


def example_sources():
    """(where, html) for every component snippet and every showcase block that is not a semantic demo."""
    out = [(f"scripts/component_docs.py {c['slug']} {x['id']}", x["html"]) for c in COMPONENTS for x in [{"id": "example", "html": c["html"]}] + c.get("examples", [])]
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
    WANT = {"inline": set(), "control": {"base"}, "option label": {"base"}, "cell": {"base"}, "header": {"sm"}, "label": {"sm"}, "supporting": {"sm"},
            "body": {"base"}, "title": {"base"}, "dialog title": {"lg"}, "badge": {"sm"}, "keycap": {"xs"}, "kicker": {"xs"}, "figure": {"3xl"}}

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
        sized = bool({"h-control", "h-nested", "size-control", "size-nested"} & set(n.toks)) and n.tag in ("a", "button", "div", "td", "th", "input")
        return n.tag in ("button", "select", "summary", "textarea", "input") or role in ("tab", "option", "menuitem") or sized or "cursor-text" in n.toks

    def kind(n):
        if any(is_control(a) or a.tag == "kbd" for a in n.ancestors()): return None  # text inside a control or keycap is the control's
        if n.tag == "kbd": return "keycap"
        if "font-display" in n.toks: return "figure"
        if "uppercase" in n.toks: return "kicker"
        if is_control(n):
            field = n.tag in ("input", "textarea", "select") or "cursor-text" in n.toks or n.has(lambda k: k.tag in ("input", "textarea", "select"))
            return "control" if field or n.alltext().strip() else None  # an icon-only button has no text to size
        if n.has(is_control) and any(t.startswith("bg-") for t in n.toks) and not n.text.strip(): return "control"  # a menu or popover of controls
        if n.tag == "th": return "header"
        if n.tag == "td": return "cell"
        if n.tag == "label" and n.has(lambda k: k.tag == "input" and k.attrs.get("type") in ("checkbox", "radio")): return "option label"
        if n.tag in ("label", "legend", "dt") and not n.text.strip(): return None  # a wrapper: its text children carry the kinds
        if n.tag in ("label", "legend", "dt") or (n.tag == "dl" and n.own): return "label"
        if "rounded-full" in n.toks and n.alltext().strip(): return "badge"
        if n.tag in ("h1", "h2", "h3", "h4"):
            return "dialog title" if any(a.tag == "dialog" or a.attrs.get("role") == "dialog" for a in n.ancestors()) else "title"
        if n.tag == "p": return "body"
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
            k = kind(n)
            label = f"<{n.tag} class=\"{' '.join(n.toks)[:70]}\">"
            if k and n.eff() not in WANT[k]:
                findings.append((where, k, n.eff(), "/".join(sorted(WANT[k])), label))
            elif not k and n.own and n.parent and n.parent.text.strip():
                if n.own != n.parent.eff(): findings.append((where, "inline", n.own, n.parent.eff(), label))
            elif not k and n.own and not any(is_control(a) for a in n.ancestors()):
                unclassified.append((where, n.own, label))
    return findings, unclassified


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
            if any(re.fullmatch(r"(hover|active):bg-.+", t) for t in toks) and not any(re.fullmatch(r"(pressed|selected|current|open|expanded|has-checked):bg-.+", t) for t in toks):
                out.append(f"{where}: <{tag}> tints its fill with hover:/active: bg variants. Fix: use state (keep bg variants only where a state changes the surface, such as current:bg-accent-1-9).")
            if tag in ("a", "button", "summary", "input", "select", "textarea", "label") or (role and role.group(1) in ("button", "tab", "option", "menuitem", "switch")):
                continue
            physical = [t for t in toks if re.fullmatch(r"(?:[a-z0-9@-]+:)?(?:-?[pm][lr]-.+|left-.+|right-.+|text-(?:left|right)|border-[lr](?:-\d)?)", t)]
            if physical:
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
                if base in cat and is_semantic(cat[base], base):
                    out.append(f"{where}: {t} is semantic. Fix: use regular classes in examples (the step, space or size it stands for).")
        return out
    errors = []
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
    return sorted(set(errors))


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {"guide.html": guide(), "reference.html": reference(), "changelog.html": changelog(),
             "docs-home.html": docs_home(), "index.html": index(), "components-index.html": components_index(), "classes.html": classes_page(), "semantic.html": classes_page(True),
             "colour.html": colour_page(), "type-space.html": type_space_page(), "states.html": states_page(), "materials.html": materials_page()}
    files.update({f"c-{c['slug']}.html": component_page(c) for c in COMPONENTS})
    for name, text in files.items():
        text = text.replace("<code>--", '<code class="whitespace-nowrap">--')
        text = text.replace("__VERSION__", VERSION)
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
if "--lint" in sys.argv:
    problems = lint_examples()
    print("\n".join(problems))
    sys.exit(1 if problems else 0)
main()
