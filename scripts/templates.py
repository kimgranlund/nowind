#!/usr/bin/env python3
"""Stamp the Nowind docs templates (designed with the massimo-vignelli agent). Shared parts are defined once here.
Usage: python3 scripts/templates.py [output-dir]   (default: site/docs/)"""
import html, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from component_docs import COMPONENTS  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "docs")
E = html.escape

# ---------------------------------------------------------------- site map
PAGES = [
    ("docs-home.html", "Overview"),
    ("guide.html", "Lay out a docs page"),
    ("reference.html", "Page grid and shell"),
    ("classes.html", "Classes"),
    ("semantic.html", "Semantic classes"),
    ("changelog.html", "Changelog"),
    ("index.html", "About these templates"),
    ("components-index.html", "Components"),
] + [(f"c-{c['slug']}.html", c["name"]) for c in COMPONENTS]
TITLES = dict(PAGES)

NAV_GROUPS = [
    ("Getting started", [("docs-home.html", "Overview", "ph-house"),
                         ("guide.html", "Lay out a docs page", "ph-book-open")]),
    ("Reference", [("reference.html", "Page grid and shell", "ph-grid-four"),
                   ("classes.html", "Classes", "ph-list-bullets"),
                   ("semantic.html", "Semantic classes", "ph-tag"),
                   ("../components.html", "Showcase", "ph-squares-four"),
                   ("../specimen.html", "Specimen", "ph-palette")]),
    ("Components", [("components-index.html", "All components", "ph-stack")] +
                   [(f"c-{c['slug']}.html", c["name"], c["icon"]) for c in COMPONENTS]),
    ("Project", [("changelog.html", "Changelog", "ph-clock-counter-clockwise"),
                 ("index.html", "Templates", "ph-ruler")]),
]

TOP_NAV = [("docs-home.html", "Docs"), ("guide.html", "Guide"), ("components-index.html", "Components"),
           ("reference.html", "Reference"), ("classes.html", "Classes"), ("changelog.html", "Changelog")]

# ---------------------------------------------------------------- shared parts
HEAD = """<!doctype html>
<html lang="en" class="scroll-pt-header">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Nowind docs</title>
<link rel="icon" href="data:,">
<link rel="stylesheet" href="../../theme.css">
<link rel="stylesheet" href="../../nowind.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/regular/style.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/bold/style.css">
</head>
<body class="bg fg">
"""

def band():
    return '<div class="shrink-0 py-3xs bg-inverse" aria-hidden="true"></div>\n'

def header(current):
    links = []
    for href, label in TOP_NAV:
        if href == current or (current == "index.html" and False):
            links.append(f'      <a href="{href}" aria-current="page" class="inline-flex items-center h-control px-control border-b-2 border-accent-1-strong no-underline fg text-title-sm">{label}</a>')
        else:
            links.append(f'      <a href="{href}" class="inline-flex items-center h-control px-control border-b-2 border-transparent no-underline fg-weak hover:fg hover:border-strong text-title-sm transition-colors">{label}</a>')
    return f"""<header class="sticky top-0 z-30 flex items-center justify-between gap-row h-header px-grid border-b border-weak bg">
    <a href="docs-home.html" class="inline-flex items-center gap-gutter no-underline fg">
      <i class="icon ph-bold ph-wind"></i><span class="text-subtitle">Nowind</span><span class="text-kicker fg-weak">__VERSION__</span>
    </a>
    <nav aria-label="Main" class="hidden lg:flex items-center gap-3xs">
{chr(10).join(links)}
    </nav>
    <a href="https://github.com/kimgranlund/nowind" class="inline-flex items-center justify-center h-control px-control gap-gutter border bg hover:bg-component-weak no-underline fg text-title-sm transition-colors" aria-label="Nowind on GitHub">
      <i class="icon ph ph-github-logo"></i><span class="hidden xl:inline">GitHub</span>
    </a>
  </header>
"""

def nav_groups(current, indent="      "):
    out = []
    for group, items in NAV_GROUPS:
        lis = []
        for href, label, icon in items:
            if href == current:
                lis.append(f'{indent}    <li><a href="{href}" aria-current="page" class="flex items-center h-control px-control gap-gutter border-l-2 border-accent-1-strong bg-component-weak no-underline fg text-title-sm"><i class="icon ph {icon}"></i><span class="truncate">{label}</span></a></li>')
            else:
                lis.append(f'{indent}    <li><a href="{href}" class="flex items-center h-control px-control gap-gutter border-l-2 border-transparent no-underline fg-weak hover:fg hover:bg-component-weak text-title-sm transition-colors"><i class="icon ph {icon}"></i><span class="truncate">{label}</span></a></li>')
        out.append(f"""{indent}<div class="flex flex-col gap-field">
{indent}  <span class="text-kicker fg-weak">{group}</span>
{indent}  <ul role="list" class="flex flex-col gap-3xs">
{chr(10).join(lis)}
{indent}  </ul>
{indent}</div>""")
    return "\n".join(out)

def menu(current):
    """Phone and tablet navigation: a disclosure row under the header. No script."""
    return f"""<details class="lg:hidden border-b border-weak bg-strong">
    <summary class="flex items-center gap-gutter h-control px-grid list-none cursor-pointer fg text-title-sm"><i class="icon ph ph-list"></i><span>Menu</span></summary>
    <nav aria-label="Documentation" class="flex flex-col gap-group px-grid pt-2xs pb-md">
{nav_groups(current)}
    </nav>
  </details>
"""

def sidebar(current):
    return f"""<aside class="hidden lg:flex flex-col shrink-0 self-start sticky top-header w-sidebar h-below-header overflow-y-auto p-region border-r border-weak bg-strong">
      <nav aria-label="Documentation" class="flex flex-col gap-group">
{nav_groups(current, "        ")}
      </nav>
    </aside>
"""

def toc(items, label="On this page"):
    lis = "\n".join(
        f'            <li><a href="#{i}" class="block py-3xs pl-sm border-l-2 border-weak hover:border-strong no-underline fg-weak hover:fg text-caption transition-colors">{E(t)}</a></li>'
        for i, t in items)
    return f"""<aside class="hidden xl:block xl:col-span-3">
        <nav aria-label="{label}" class="sticky top-header flex flex-col gap-field py-page">
          <span class="text-kicker fg-weak">{label}</span>
          <ol role="list" class="flex flex-col">
{lis}
          </ol>
        </nav>
      </aside>
"""

def footer():
    return """<footer class="flex flex-col md:flex-row md:items-center justify-between gap-field px-grid py-surface border-t border-weak text-caption fg-weak">
        <span>Nowind __VERSION__. Every page here is built from Nowind utility classes only.</span>
        <span class="flex flex-wrap gap-row">
          <a href="changelog.html" class="no-underline fg-weak hover:fg transition-colors">Changelog</a>
          <a href="index.html" class="no-underline fg-weak hover:fg transition-colors">About these templates</a>
          <a href="https://github.com/kimgranlund/nowind" class="no-underline fg-weak hover:fg transition-colors">GitHub</a>
        </span>
      </footer>
"""

def prev_next(current):
    order = [p for p, _ in PAGES]
    i = order.index(current)
    prev = order[i - 1] if i > 0 else None
    nxt = order[i + 1] if i < len(order) - 1 else None
    cells = []
    if prev:
        cells.append(f"""          <a href="{prev}" class="flex flex-col gap-3xs p-surface border border-weak hover:border-strong no-underline transition-colors">
            <span class="inline-flex items-center gap-gutter-half text-kicker fg-weak"><i class="icon icon-sm ph-bold ph-arrow-left"></i><span>Previous</span></span>
            <span class="text-subtitle fg-accent-1-weak">{TITLES[prev]}</span>
          </a>""")
    else:
        cells.append('          <span class="hidden md:block"></span>')
    if nxt:
        cells.append(f"""          <a href="{nxt}" class="flex flex-col md:items-end gap-3xs p-surface border border-weak hover:border-strong no-underline md:text-right transition-colors">
            <span class="inline-flex items-center gap-gutter-half text-kicker fg-weak"><span>Next</span><i class="icon icon-sm ph-bold ph-arrow-right"></i></span>
            <span class="text-subtitle fg-accent-1-weak">{TITLES[nxt]}</span>
          </a>""")
    return '<nav aria-label="Previous and next page" class="grid grid-cols-1 md:grid-cols-2 gap-grid">\n' + "\n".join(cells) + "\n        </nav>\n"

CALLOUT = {
    "note": ("info", "ph-info", "Note"),
    "tip": ("success", "ph-check-circle", "Tip"),
    "warning": ("warning", "ph-warning", "Warning"),
}

def callout(kind, body_html):
    pal, icon, label = CALLOUT[kind]
    return f"""<aside role="note" class="flex gap-gutter p-surface border-l-4 border-{pal} bg-component-{pal}-weak">
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
    align = align or ["left"] * len(headers)
    ths = "".join(f'<th scope="col" class="text-{a} px-sm py-xs border-b text-label fg-weak">{h}</th>' for h, a in zip(headers, align))
    trs = []
    for n, r in enumerate(rows):
        last = n == len(rows) - 1
        b = "" if last else " border-b border-weak"
        r = [c.replace("<code>", '<code class="whitespace-normal break-all">') for c in r]
        tds = "".join(f'<td class="text-{a} align-top px-sm py-xs break-words{b}">{c}</td>' for c, a in zip(r, align))
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
    return f"""<header class="flex flex-col gap-field">
            <span class="text-kicker fg-weak">{kicker}</span>
            <h1 class="text-display-sm text-balance">{title}</h1>
            <p class="text-body-md fg-weak">{intro}</p>{m}
          </header>"""

def section(sid, title, *blocks):
    inner = "\n          ".join(blocks)
    return f"""<section id="{sid}" class="flex flex-col gap-group">
          <h2 class="text-heading-md pt-sm border-t">{title}</h2>
          {inner}
        </section>"""

def subhead(t):
    return f'<h3 class="text-subtitle">{t}</h3>'

def p(t):
    return f'<p class="text-body-md">{t}</p>'

def ul(items):
    lis = "\n".join(f'            <li>{i}</li>' for i in items)
    return f'<ul class="flex flex-col gap-3xs pl-md list-disc text-body-md">\n{lis}\n          </ul>'

def doc_page(current, title, article_html, toc_items, wide=False, sidebar_on=True):
    """The docs frame: band, header, menu, sidebar, main grid (article + TOC), footer."""
    measure = "" if wide else " max-w-measure"
    side = sidebar(current) if sidebar_on else ""
    return (HEAD.format(title=E(title)) +
f"""{band()}{header(current)}{menu(current)}<div class="flex">
  {side}  <main id="content" class="flex flex-col flex-1 min-w-0">
    <div class="grid grid-cols-4 md:grid-cols-12 gap-grid px-grid">
      <article class="col-span-4 md:col-span-12 xl:col-span-9 min-w-0 tier-content flex flex-col gap-section py-page{measure}">
        {article_html}
        {prev_next(current)}      </article>
      {toc(toc_items)}    </div>
    {footer()}  </main>
</div>
</body>
</html>
""")

# ================================================================ pages

def guide():
    toc_items = [("frame", "The frame"), ("grid", "The grid"), ("measure", "The reading column"),
                 ("type", "Four type sizes"), ("parts", "Callouts, code and tables"), ("menu", "Navigation on a phone")]
    art = "\n        ".join([
        page_head("Guide", "Lay out a docs page",
                  "Build a documentation page from Nowind's shell lengths, its 12-column grid and four type roles. Every part on this page is the template you can copy.",
                  "Applies to Nowind __VERSION__"),
        section("frame", "The frame",
            p("A docs page has five parts, always in the same place: a band and a header across the top, a sidebar on the left, the content in the middle and an on-page table of contents on the right. The page scrolls as a whole: the header sticks to the top and the sidebar sticks under it, scrolling on its own only when its links are taller than the window."),
            code("frame.html", "HTML", """
<html class="scroll-pt-header">
<div class="py-3xs bg-inverse"></div>
<header class="sticky top-0 z-30 flex items-center justify-between h-header px-grid border-b border-weak bg">…</header>
<div class="flex">
  <aside class="hidden lg:flex flex-col shrink-0 self-start sticky top-header w-sidebar h-below-header overflow-y-auto p-region">…</aside>
  <main class="flex flex-col flex-1 min-w-0">…</main>
</div>"""),
            p("The header is <code>h-header</code> tall and the sidebar <code>w-sidebar</code> wide. Both follow the base size, so they grow with the type from a phone to a wide screen."),
            callout("note", "Keep one scroller: the page. Don't make <code>main</code> a scroll box; browsers paint very tall nested scrollers badly, and in-page links, find and the back button work against the window. <code>scroll-pt-header</code> on <code>html</code> keeps linked headings clear of the sticky header."),
        ),
        section("grid", "The grid",
            p("Inside <code>main</code>, content sits on Nowind's page grid: four columns on a phone, twelve from 768px up, with <code>gap-grid</code> between columns and <code>px-grid</code> at the edges. The article takes nine columns and the table of contents three; below 1280px the table of contents is hidden and the article takes all twelve."),
            code("main.html", "HTML", """
<div class="grid grid-cols-4 md:grid-cols-12 gap-grid px-grid">
  <article class="col-span-4 md:col-span-12 xl:col-span-9 tier-content max-w-measure">…</article>
  <aside class="hidden xl:block xl:col-span-3">…</aside>
</div>"""),
            table(["Width", "Sidebar", "Columns", "Table of contents"], [
                ["Under 768px", "In the menu", "4", "Hidden"],
                ["768px", "In the menu", "12", "Hidden"],
                ["1024px (<code>lg:</code>)", "<code>w-sidebar</code>", "12", "Hidden"],
                ["1280px (<code>xl:</code>)", "<code>w-sidebar</code>", "12: 9 + 3", "Shown"],
            ]),
        ),
        section("measure", "The reading column",
            p("Prose stops at <code>max-w-measure</code>, 44 times the base size. The article is a <code>tier-content</code> region, so its section gaps and page padding are one and a half times the product rhythm and its measure grows with the tier's larger base size."),
            callout("tip", "Put the tier on the article only. The header, sidebar and table of contents stay in the product tier, so they look the same on every page."),
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
<aside role="note" class="flex gap-gutter p-surface border-l-4 border-info bg-component-info-weak">
  <i class="icon ph ph-info fg-info-weak"></i>
  <div class="flex flex-col gap-3xs">
    <span class="text-label fg-info">Note</span>
    <p class="text-body-md">One sentence the reader must not miss.</p>
  </div>
</aside>"""),
        ),
        section("menu", "Navigation on a phone",
            p("Below 1024px the sidebar moves into a <code>details</code> element under the header. It opens and closes without a script, and the same list of links serves both places."),
            code("menu.html", "HTML", """
<details class="lg:hidden border-b border-weak bg-strong">
  <summary class="flex items-center gap-gutter h-control px-grid list-none text-title-sm">
    <i class="icon ph ph-list"></i><span>Menu</span>
  </summary>
  <nav class="flex flex-col gap-group px-grid pt-2xs pb-md">…</nav>
</details>"""),
        ),
    ])
    return doc_page("guide.html", "Lay out a docs page", art, toc_items)


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
        section("breakpoints", "Breakpoints",
            table(["Prefix", "Min width", "In these templates"], [
                ["<code>sm:</code>", "640px", "The GitHub label appears"],
                ["<code>md:</code>", "768px", "12 columns; header links appear"],
                ["<code>lg:</code>", "1024px", "The sidebar replaces the menu"],
                ["<code>xl:</code>", "1280px", "The table of contents appears"],
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
    blocks.append(code("index.html", "HTML", """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kimgranlund/nowind@v__VERSION__/dist/nowind.min.css">"""))
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
        blocks.append(f"""<section id="v{v.replace('.', '-')}" class="grid grid-cols-1 md:grid-cols-4 gap-grid pt-sm border-t">
            <div class="flex flex-col gap-field">
              <h2 class="text-heading-md">{v}</h2>
              <time datetime="{date}" class="text-caption fg-weak">{date}</time>{badge}
            </div>
            <div class="md:col-span-3 flex flex-col gap-group min-w-0">
              {chr(10).join("              " + b if i else b for i, b in enumerate(body))}
            </div>
          </section>""")
    art = "\n        ".join(blocks)
    return doc_page("changelog.html", "Changelog", art, toc_items, wide=True).replace(
        'aria-label="On this page"', 'aria-label="Releases"').replace(
        '<span class="text-kicker fg-weak">On this page</span>', '<span class="text-kicker fg-weak">Releases</span>')


def docs_home():
    cur = "docs-home.html"
    entries = [
        ("guide.html", "ph-book-open", "Guide", "Lay out a docs page: the frame, the grid, the reading column and four type sizes."),
        ("reference.html", "ph-grid-four", "Reference", "Every grid, shell, level and tier class with its declaration and where it comes from."),
        ("changelog.html", "ph-clock-counter-clockwise", "Changelog", "What changed in each release, newest first."),
        ("../components.html", "ph-squares-four", "Components", "Buttons, forms, tables and dialogs built only from utility classes."),
    ]
    cards = "\n".join(f"""        <a href="{h}" class="col-span-4 md:col-span-6 xl:col-span-3 flex flex-col gap-field p-surface border border-weak hover:border-strong no-underline fg transition-colors">
          <i class="icon ph {i} fg-accent-1-weak"></i>
          <span class="text-subtitle">{t}</span>
          <span class="text-body-md fg-weak">{d}</span>
        </a>""" for h, i, t, d in entries)
    figures = [("1,324", "utility classes"), ("660", "breakpoint variants"), ("162", "hover variants"), ("29", "type roles"), ("9", "colour palettes")]
    figs = "\n".join(f"""            <div class="flex items-baseline justify-between gap-row py-xs border-b border-weak">
              <dt class="text-body-md fg-weak">{l}</dt><dd class="text-heading-md tabular-nums">{n}</dd>
            </div>""" for n, l in figures)
    body = f"""{band()}{header(cur)}{menu(cur)}<main id="content" class="flex flex-col">
      <div class="grid grid-cols-4 md:grid-cols-12 gap-grid px-grid">
        <header class="col-span-4 md:col-span-12 tier-brand flex flex-col gap-group py-page">
          <span class="text-kicker fg-weak">Documentation · __VERSION__</span>
          <h1 class="text-display-sm text-balance">Nowind documentation</h1>
          <p class="text-body-md fg-weak max-w-measure">Theme tokens and utility classes in plain CSS. Link one file and every class already exists, so it works in any HTML, including what a CMS writes.</p>
          <div class="flex flex-wrap gap-row">
            <a href="guide.html" class="inline-flex items-center h-control px-control gap-gutter bg-solid-accent-1 hover:bg-solid-accent-1-strong no-underline fg-on-solid-accent-1 text-title-sm transition-colors"><span>Read the guide</span><i class="icon ph ph-arrow-right"></i></a>
            <a href="reference.html" class="inline-flex items-center h-control px-control gap-gutter border hover:bg-component-weak no-underline fg text-title-sm transition-colors"><span>Class reference</span></a>
          </div>
        </header>
{cards}
        <section id="start" class="col-span-4 md:col-span-12 xl:col-span-7 flex flex-col gap-group py-page">
          <h2 class="text-heading-md pt-sm border-t">Start in one line</h2>
          <p class="text-body-md max-w-measure">Link the minified bundle from the CDN. The link pins release __VERSION__, so your site won't change until you change the version.</p>
          {code("index.html", "HTML", '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/kimgranlund/nowind@v__VERSION__/dist/nowind.min.css">')}
          {callout("note", "Put your own CSS in <code>@layer styles</code>, so a utility class always wins over it.")}
        </section>
        <section id="inside" class="col-span-4 md:col-span-12 xl:col-span-5 flex flex-col gap-group py-page">
          <h2 class="text-heading-md pt-sm border-t">In the box</h2>
          <dl class="flex flex-col">
{figs}
          </dl>
          <p class="text-caption fg-weak">Counts from <code>nowind.manifest.json</code> and the type-role manifest.</p>
        </section>
      </div>
      {footer()}</main>
</body>
</html>
"""
    return HEAD.format(title="Overview") + body


def index():
    toc_items = [("purpose", "Purpose"), ("frame", "The frame"), ("grid", "The grid"), ("type", "Type scale"),
                 ("colour", "Colour and form"), ("parts", "Which classes make which part"),
                 ("templates", "The templates"), ("limits", "Known limits")]
    # live grid strip
    cols = "\n".join('            <div class="col-span-1 py-xs bg-component-accent-1-weak fg-accent-1-weak text-label text-center">' + str(n) + '</div>' for n in range(1, 13))
    grid_strip = f"""<div class="grid grid-cols-4 md:grid-cols-12 gap-grid" aria-hidden="true">
{cols}
          </div>"""
    frame_diagram = """<div class="flex flex-col border" role="img" aria-label="Diagram of the frame: a band and header across the top, a sidebar on the left, the article in the middle and the table of contents on the right">
            <div class="py-3xs bg-inverse"></div>
            <div class="flex items-center px-sm py-xs border-b border-weak text-label fg-weak">header · h-header</div>
            <div class="grid grid-cols-12">
              <div class="col-span-3 p-sm border-r border-weak bg-strong text-label fg-weak">sidebar · w-sidebar</div>
              <div class="col-span-6 p-sm text-label fg-weak">article · 9 columns · max-w-measure</div>
              <div class="col-span-3 p-sm border-l border-weak text-label fg-weak">contents · 3</div>
            </div>
          </div>"""
    type_rows = [
        ('<span class="text-display-sm">Aa</span>', "Display", "<code>text-display-sm</code>", "<code>--text-4xl</code>", "Page title"),
        ('<span class="text-heading-md">Aa</span>', "Heading", "<code>text-heading-md</code>", "<code>--text-xl</code>", "Section heading"),
        ('<span class="text-body-md">Aa</span>', "Base", "<code>text-body-md</code> · <code>text-subtitle</code> · <code>text-title-sm</code>", "<code>--text-base</code>", "Prose, subheads, nav, buttons"),
        ('<span class="text-caption">Aa</span>', "Small", "<code>text-caption</code> · <code>text-label</code> · <code>text-kicker</code> · <code>text-mono-sm</code>", "<code>--text-sm</code>", "Metadata, labels, code"),
    ]
    parts = [
        ["Band", "<code>py-3xs bg-inverse</code>"],
        ["Header", "<code>sticky top-0 z-30 flex items-center justify-between h-header px-grid border-b border-weak bg</code>"],
        ["Header link", "<code>inline-flex items-center h-control px-control border-b-2 text-title-sm</code>; current: <code>border-accent-1-strong fg</code>"],
        ["Menu (phone)", "<code>details</code> with <code>lg:hidden border-b</code>"],
        ["Sidebar", "<code>hidden lg:flex flex-col self-start sticky top-header w-sidebar h-below-header overflow-y-auto p-region border-r bg-strong</code>"],
        ["Sidebar link", "<code>flex items-center h-control px-control gap-gutter border-l-2 text-title-sm</code>; current: <code>border-accent-1-strong bg-component-weak fg</code>"],
        ["Main grid", "<code>grid grid-cols-4 md:grid-cols-12 gap-grid px-grid</code>"],
        ["Article", "<code>xl:col-span-9 tier-content flex flex-col gap-section py-page max-w-measure</code>"],
        ["Section heading", "<code>text-heading-md pt-sm border-t</code>"],
        ["Table of contents", "<code>hidden xl:block xl:col-span-3</code>, inner <code>sticky top-header</code>; links <code>pl-sm border-l-2 text-caption</code>"],
        ["Callout", "<code>flex gap-gutter p-surface border-l-4 border-info bg-component-info-weak</code>"],
        ["Code block", "<code>figure</code> with <code>border bg-strong</code>; <code>pre</code> with <code>p-surface overflow-x-auto whitespace-pre text-mono-sm</code>"],
        ["Table", "Box <code>border</code>, no scrolling; <code>th</code> <code>px-sm py-xs text-label</code>; <code>td</code> <code>px-sm py-xs border-b break-words</code>, code in cells <code>whitespace-normal break-all</code>"],
        ["Previous and next", "<code>grid grid-cols-1 md:grid-cols-2 gap-grid</code>; each <code>p-surface border hover:border-strong</code>"],
        ["Footer", "<code>flex flex-col md:flex-row gap-field px-grid py-surface border-t text-caption</code>"],
    ]
    tpls = [
        ("docs-home.html", "Docs home", "A landing page: title, two actions, four entry points on the grid, an install snippet and the figures."),
        ("guide.html", "Guide", "An article with the sidebar, the reading column and the table of contents."),
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
            p("An inverse band, then the header, then a row with the sidebar and the content. The header and band never scroll; the sidebar and the content scroll on their own. Below 1024px the sidebar becomes a menu under the header."),
        ),
        section("grid", "The grid",
            grid_strip,
            p("Four columns on a phone and twelve from 768px, spaced by <code>gap-grid</code> and held off the edge by <code>px-grid</code>. The article spans nine columns and the table of contents three from 1280px. Every width comes from the shell: <code>w-sidebar</code> for the sidebar and <code>max-w-measure</code> for prose."),
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
                "The table of contents does not mark the section in view. That needs a script.",
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
    if cat in SEMANTIC_CATS or (cat != "Layout and misc" and SEMANTIC_WORDS.search(k)):
        return True
    if cat in ("Text color", "Background color", "Border color"):
        return not re.search(r"-a?\d+$|-(inherit|current|transparent)$", k)
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
        sections.append(f"""<section id="{sid}" data-classes class="flex flex-col gap-group">
          <h2 class="flex items-baseline justify-between gap-row text-heading-md pt-sm border-t"><span>{title}</span><span class="text-caption fg-weak">{len(rows)} classes</span></h2>
          <ul role="list" class="border border-weak">
            <li aria-hidden="true" class="hidden md:grid grid-cols-12 gap-x-grid px-sm py-xs bg-strong">{head_row}</li>
{chr(10).join(rows_html)}
          </ul>
        </section>""")
    head = page_head("Reference", title_,
        f"{kicker_name} {what} {total} of them, with what each declares, read from <code>classes.md</code>. "
        f"The rest are in <a href=\"{other}\">{other_title}</a>. "
        "Colour, opacity and cursor classes also take <code>hover:</code> and the state variants; layout classes take <code>sm:</code> to <code>2xl:</code>.",
        "Nowind __VERSION__ · generated from classes.md")
    search = f"""<div class="sticky top-header z-10 flex items-center gap-row py-xs bg">
          <input id="class-filter" type="search" placeholder="Filter by class or declaration" aria-label="Filter classes" class="grow min-w-0 h-control px-control rounded-sm border hover:border-strong bg text-control-md transition-colors">
          <span id="class-count" data-all="{total} classes" aria-live="polite" class="text-caption fg-weak whitespace-nowrap">{total} classes</span>
        </div>"""
    cards = "\n".join(
        f"""            <a href="#{sid}" class="flex items-baseline justify-between gap-row p-surface border border-weak hover:border-strong hover:bg-component-weak no-underline fg transition-colors">
              <span class="text-subtitle">{title}</span><span class="text-caption fg-weak whitespace-nowrap">{len(rows)}</span>
            </a>""" for (sid, title), (_, rows) in zip(toc_items, cats))
    groups = f"""<nav aria-label="Class groups" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-grid">
{cards}
          </nav>"""
    art = "\n        ".join([head, groups, search] + sections)
    return doc_page(fname, title_, art, toc_items, wide=True).replace("</body>", CLASS_FILTER + "</body>", 1)


# ---------------------------------------------------------------- component docs
def classes_of(snippet):
    """The utility classes a snippet uses, sorted (Phosphor's icon classes left out)."""
    found = {c for cls in re.findall(r'class="([^"]+)"', snippet) for c in cls.split() if not c.startswith("ph")}
    return sorted(found)


def component_page(c):
    name = f"c-{c['slug']}.html"
    toc_items = [("example", "Example"), ("usage", "Usage"), ("classes", "Classes")]
    chips = " ".join(f'<a href="{class_page_of(k.split(":")[-1])}#{class_id(k.split(":")[-1])}" class="inline-flex items-center h-nested px-nested rounded-xs bg-strong border border-weak hover:border-strong no-underline fg text-mono-sm whitespace-nowrap transition-colors">{E(k)}</a>' for k in classes_of(c["html"]))
    use = "\n".join(f'            <li class="flex gap-gutter"><i class="icon icon-sm ph-bold ph-check fg-success-weak"></i><span>{t}</span></li>' for t in c["use"])
    avoid = "\n".join(f'            <li class="flex gap-gutter"><i class="icon icon-sm ph-bold ph-x fg-danger-weak"></i><span>{t}</span></li>' for t in c["avoid"])
    art = "\n        ".join([
        page_head(c["group"], c["name"], c["summary"]),
        section("example", "Example",
            f"""<div class="tier-product p-surface rounded-lg border border-weak bg-strong">
{c["html"]}
          </div>""",
            code(f"{c['slug']}.html", "HTML", c["html"]),
        ),
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
            p(f"Every class in the example, {len(classes_of(c['html']))} in all. Each one links to its declarations in <a href=\"classes.html\">Classes</a> or <a href=\"semantic.html\">Semantic classes</a>."),
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

def main():
    os.makedirs(OUT, exist_ok=True)
    files = {"guide.html": guide(), "reference.html": reference(), "changelog.html": changelog(),
             "docs-home.html": docs_home(), "index.html": index(), "components-index.html": components_index(), "classes.html": classes_page(), "semantic.html": classes_page(True)}
    files.update({f"c-{c['slug']}.html": component_page(c) for c in COMPONENTS})
    for name, text in files.items():
        text = text.replace("<code>--", '<code class="whitespace-nowrap">--')
        text = text.replace("__VERSION__", VERSION)
        with open(os.path.join(OUT, name), "w") as f:
            f.write(text)
        print("wrote", name, len(text))

main()
