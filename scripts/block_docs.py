"""Block docs data for scripts/templates.py: one entry per block, a whole section of a page (a hero, a footer, an app
shell) put together from the components and patterns. Same shape as pattern_docs.py: "components" and "patterns" are
the slugs it is built from, linked from its page. Utility classes only."""

from component_docs import BTN_PRIMARY, BTN_SECONDARY, CARD, GHOST_ICON, BOX, BARE
from pattern_docs import tier, HELP, BADGE, AVATAR

KICKER = "text-xs font-mono uppercase tracking-widest fg-accent-1-11"
HEADLINE = "text-3xl font-display font-extrabold tracking-tight"
LINK = "fg-neutral-11 hover:fg-neutral-12 no-underline"
NAV_LINK = "flex items-center gap-gutter h-control px-control rounded-sm border border-transparent no-underline text-base fg-neutral-12 hover:bg-neutral-3 current:bg-accent-1-3 current:fg-accent-1-11"


def stat(label, value, delta, up=True):
    tone, icon = ("fg-success-11", "ph-trend-up") if up else ("fg-danger-11", "ph-trend-down")
    return f"""    <div class="flex flex-col gap-3xs {CARD}">
      <span class="{HELP}">{label}</span>
      <div class="flex flex-wrap items-baseline gap-xs">
        <span class="{HEADLINE} tabular-nums">{value}</span>
        <span class="inline-flex items-baseline text-sm {tone}"><i class="icon icon-sm ph-bold {icon}"></i><span>{delta}</span></span>
      </div>
    </div>"""


def nav_item(icon, label, current=False):
    return f'<a href="#" aria-current="{"page" if current else "false"}" class="{NAV_LINK}"><i class="icon ph {icon}"></i><span class="grow">{label}</span></a>'


def footer_col(title, links):
    lis = "".join(f'<li><a href="#" class="{LINK} text-sm">{l}</a></li>' for l in links)
    return f"""    <div class="flex flex-col gap-xs">
      <span class="{KICKER.replace('fg-accent-1-11', 'fg-neutral-11')}">{title}</span>
      <ul class="flex flex-col gap-2xs list-none p-0">{lis}</ul>
    </div>"""


def quote(text, initials, tone, name, role):
    return f"""  <figure class="flex flex-col gap-md {CARD}">
    <blockquote><p class="text-base">“{text}”</p></blockquote>
    <figcaption class="flex items-center gap-sm">
      <span class="{AVATAR} bg-{tone}-9 fg-{tone}-contrast">{initials}</span>
      <div class="flex flex-col gap-3xs"><span class="text-base">{name}</span><span class="{HELP}">{role}</span></div>
    </figcaption>
  </figure>"""


BLOCKS = [
    {
        "slug": "hero", "name": "Hero", "icon": "ph-flag-banner", "group": "Marketing",
        "components": ["button", "badge"],
        "summary": "The top of a landing page: a kicker, a headline at the display size, one sentence of what it is, and two actions, the primary first. Centred, at a readable measure.",
        "html": f"""<section class="flex flex-col items-center text-center gap-md py-2xl px-md" aria-labelledby="blk-hero-title">
  <span class="{BADGE} bg-accent-1-3 border-accent-1-6 fg-accent-1-11"><span>New in 0.20</span></span>
  <h2 id="blk-hero-title" class="{HEADLINE} max-w-text">Design tokens and utilities in one plain CSS file</h2>
  <p class="text-base fg-neutral-11 max-w-text">Link one stylesheet and every class already exists. No build step, in any HTML.</p>
  <div class="flex flex-wrap justify-center gap-xs">
    <button class="{BTN_PRIMARY}"><span>Get started</span></button>
    <button class="{BTN_SECONDARY}"><i class="icon ph ph-book-open"></i><span>Read the docs</span></button>
  </div>
</section>""",
        "use": ["One headline and one sentence; the rest of the page explains.", "The primary action first, the secondary beside it."],
        "avoid": ["A carousel of headlines; people read the first."],
    },
    {
        "slug": "feature-section", "name": "Feature section", "icon": "ph-squares-four", "group": "Marketing",
        "components": ["card"], "patterns": ["feature-grid"],
        "summary": "A section heading with a kicker and a lead, then the feature grid under it.",
        "html": f"""<section class="flex flex-col gap-xl py-xl px-md" aria-labelledby="blk-feat-title">
  <div class="flex flex-col gap-xs max-w-text">
    <span class="{KICKER}">Why Nowind</span>
    <h2 id="blk-feat-title" class="text-3xl font-semibold tracking-tight">Everything a page needs, nothing to install</h2>
    <p class="text-base fg-neutral-11">The classes read tokens, so changing a token changes every page.</p>
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-lg">
    <div class="flex flex-col gap-xs"><span class="inline-flex items-center justify-center size-control shrink-0 self-start rounded-sm bg-accent-1-3 fg-accent-1-11"><i class="icon ph ph-lightning"></i></span><span class="text-lg font-semibold">No build step</span><p class="text-base fg-neutral-11">Link one stylesheet; every class is already there.</p></div>
    <div class="flex flex-col gap-xs"><span class="inline-flex items-center justify-center size-control shrink-0 self-start rounded-sm bg-accent-1-3 fg-accent-1-11"><i class="icon ph ph-moon"></i></span><span class="text-lg font-semibold">Light and dark</span><p class="text-base fg-neutral-11">Every colour is a pair, so both modes come for free.</p></div>
    <div class="flex flex-col gap-xs"><span class="inline-flex items-center justify-center size-control shrink-0 self-start rounded-sm bg-accent-1-3 fg-accent-1-11"><i class="icon ph ph-text-aa"></i></span><span class="text-lg font-semibold">Fluid type</span><p class="text-base fg-neutral-11">Sizes grow with the screen, without a media query.</p></div>
  </div>
</section>""",
        "use": ["Lead with what the reader gets, not with what the product has."],
        "avoid": ["A feature section with no heading; the grid alone doesn't say why."],
    },
    {
        "slug": "stats-band", "name": "Stats band", "icon": "ph-chart-bar", "group": "Marketing",
        "components": ["stat"],
        "summary": "Three or four figures in a row of cards from <code>md</code> up, each with what it counts and how it moved.",
        "html": f"""<section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-md" aria-label="Key figures">
{stat("Active teams", "1,284", "8%")}
{stat("Pages shipped", "48k", "12%")}
{stat("Median load", "0.9 s", "0.1 s")}
{stat("Support tickets", "37", "4%", up=False)}
</section>""",
        "use": ["Figures people can check, with what they count."],
        "avoid": ["More than four figures; the band stops being read."],
    },
    {
        "slug": "testimonials", "name": "Testimonials", "icon": "ph-quotes", "group": "Marketing",
        "components": ["card", "avatar"],
        "summary": "Quotes from people who use it, each a card with the quote and who said it, side by side from <code>md</code> up.",
        "html": f"""<section class="grid grid-cols-1 md:grid-cols-2 gap-md" aria-label="What people say">
{quote("We deleted our build step and nothing broke.", "GH", "accent-3", "Grace Hopper", "Engineer, Northwind")}
{quote("Our CMS pages finally look like the app.", "KJ", "accent-4", "Katherine Johnson", "Design lead, Contoso")}
</section>""",
        "use": ["A name and a role with every quote."],
        "avoid": ["Quotes nobody said."],
    },
    {
        "slug": "call-to-action", "name": "Call to action", "icon": "ph-megaphone-simple", "group": "Marketing",
        "components": ["button"], "patterns": ["newsletter"],
        "summary": "The last section of a landing page, on the accent's solid: one line of what to do, one sentence of why, and the action.",
        "html": f"""<section class="flex flex-col md:flex-row md:items-center gap-md p-xl rounded-lg bg-accent-1-9 fg-accent-1-contrast" aria-labelledby="blk-cta-title">
  <div class="grow flex flex-col gap-xs">
    <h2 id="blk-cta-title" class="text-3xl font-semibold tracking-tight fg-accent-1-contrast">Start with one stylesheet</h2>
    <p class="text-base fg-accent-1-contrast">Free and open source. Link it from the CDN and start writing classes.</p>
  </div>
  <button class="inline-flex items-center justify-center h-control px-control gap-gutter rounded-sm state border border-transparent bg-white fg-black text-base font-medium cursor-pointer"><span>Get started</span><i class="icon ph ph-arrow-right"></i></button>
</section>""",
        "use": ["The same action as the hero's primary."],
        "avoid": ["A second, different action here; the page has asked once."],
    },
    {
        "slug": "pricing-section", "name": "Pricing section", "icon": "ph-tag-chevron", "group": "Marketing",
        "components": ["card", "button"], "patterns": ["pricing", "faq"],
        "summary": "A centred heading and lead over the plans, and a line under them for anything a plan doesn't answer.",
        "html": f"""<section class="flex flex-col gap-xl py-xl px-md" aria-labelledby="blk-price-title">
  <div class="flex flex-col items-center text-center gap-xs">
    <span class="{KICKER}">Pricing</span>
    <h2 id="blk-price-title" class="text-3xl font-semibold tracking-tight">Pay per seat, cancel any time</h2>
    <p class="text-base fg-neutral-11 max-w-text">Every plan has every class. Plans differ in support and sign-in.</p>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-md">
{tier("Starter", "€0", "For one person trying it out.", ["3 projects", "Community support"], False)}
{tier("Team", "€12", "For teams shipping every week.", ["Unlimited projects", "Shared libraries", "Email support"], True)}
{tier("Business", "€24", "For companies with many teams.", ["Everything in Team", "Single sign-on", "Audit log"], False)}
  </div>
  <p class="text-base fg-neutral-11 text-center">Need more than 100 seats? <a href="#" class="fg-accent-1-11 hover:fg-accent-1-12">Talk to us</a>.</p>
</section>""",
        "use": ["Prices in the reader's currency, with what the price is per."],
        "avoid": ["Hiding the price behind a contact form for every plan."],
    },
    {
        "slug": "site-footer", "name": "Site footer", "icon": "ph-rows", "group": "Marketing",
        "components": [],
        "summary": "The foot of every page: the wordmark and one line, columns of links that stack on a phone, and a last row with the year and the legal links.",
        "html": f"""<footer class="flex flex-col gap-xl pt-xl px-md border-t border-neutral-6">
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-lg">
    <div class="flex flex-col gap-xs">
      <a href="#" class="inline-flex items-center gap-gutter no-underline fg-neutral-12 hover:fg-accent-1-11 text-lg font-semibold"><i class="icon ph-bold ph-wind fg-accent-1-9"></i><span>Nowind</span></a>
      <p class="text-base fg-neutral-11">Tokens and utilities in plain CSS.</p>
    </div>
{footer_col("Product", ["Docs", "Components", "Changelog"])}
{footer_col("Company", ["About", "Blog", "Careers"])}
{footer_col("Help", ["Support", "Status", "Contact"])}
  </div>
  <div class="flex flex-wrap items-center justify-between gap-sm py-md border-t border-neutral-6 text-sm fg-neutral-11">
    <span>© 2027 Nowind</span>
    <div class="flex flex-wrap gap-md"><a href="#" class="{LINK}">Privacy</a><a href="#" class="{LINK}">Terms</a></div>
  </div>
</footer>""",
        "use": ["The same footer on every page.", "Column titles as small labels, not headings."],
        "avoid": ["Links people need often; those belong in the header."],
    },
    {
        "slug": "app-shell", "name": "App shell", "icon": "ph-app-window", "group": "Application",
        "components": ["navbar", "sidebar-nav", "button"], "patterns": ["page-header"],
        "summary": "The frame of an app: the navbar across the top, the sidebar from <code>md</code> up (below that, the same links in a menu behind a button), and the page in the rest, starting with its header.",
        "html": f"""<div class="flex flex-col border border-neutral-6 bg-neutral-1">
  <header class="flex items-center gap-xs px-xs py-xs border-b border-neutral-6">
    <div class="md:hidden">
      <button class="{GHOST_ICON}" popovertarget="blk-shell-menu" aria-label="Menu"><i class="icon ph ph-list"></i></button>
      <div id="blk-shell-menu" popover class="anchor-bottom w-fit p-inset rounded-md bg-neutral-1 border border-neutral-6 shadow-lg">
        <nav aria-label="Workspace" class="flex flex-col gap-3xs">
          {nav_item("ph-house", "Home", True)}
          {nav_item("ph-folder-simple", "Projects")}
          {nav_item("ph-users", "Team")}
          {nav_item("ph-gear-six", "Settings")}
        </nav>
      </div>
    </div>
    <a href="#" class="inline-flex items-center gap-gutter px-xs no-underline fg-neutral-12 hover:fg-accent-1-11 text-lg font-semibold"><i class="icon ph-bold ph-wind fg-accent-1-9"></i><span>Acme</span></a>
    <span class="grow"></span>
    <button class="{GHOST_ICON}" aria-label="Notifications"><i class="icon ph ph-bell"></i></button>
    <span class="{AVATAR} bg-accent-2-9 fg-accent-2-contrast">AL</span>
  </header>
  <div class="flex">
    <nav aria-label="Workspace" class="hidden md:flex flex-col gap-3xs p-inset border-e border-neutral-6">
      {nav_item("ph-house", "Home", True)}
      {nav_item("ph-folder-simple", "Projects")}
      {nav_item("ph-users", "Team")}
      {nav_item("ph-gear-six", "Settings")}
    </nav>
    <main class="grow min-w-0 flex flex-col gap-md p-md">
      <div class="flex flex-wrap items-center gap-sm">
        <div class="grow min-w-0 flex flex-col gap-3xs"><h2 class="text-lg font-semibold">Home</h2><span class="{HELP}">3 projects changed today</span></div>
        <button class="{BTN_PRIMARY}"><i class="icon ph ph-plus"></i><span>New project</span></button>
      </div>
      <div class="flex flex-col items-center justify-center text-center gap-xs p-xl rounded-md border-2 border-dashed"><p class="text-base fg-neutral-11">The page goes here.</p></div>
    </main>
  </div>
</div>""",
        "use": ["In a real app give the bar <code>h-header</code> and the sidebar <code>w-sidebar</code>, the shell's own lengths.", "Below <code>md</code> move the sidebar's links into a menu in the bar."],
        "avoid": ["A second sidebar on the other side; put that detail in a drawer."],
    },
    {
        "slug": "dashboard", "name": "Dashboard", "icon": "ph-gauge", "group": "Application",
        "components": ["stat", "table", "badge"], "patterns": ["page-header", "filter-bar"],
        "summary": "A page header, a row of figures, then the table the figures summarise, with a link to see all of it.",
        "html": f"""<div class="flex flex-col gap-lg">
  <div class="flex flex-wrap items-center gap-sm">
    <div class="grow min-w-0 flex flex-col gap-3xs"><h2 class="text-lg font-semibold">Overview</h2><span class="{HELP}">March 2027</span></div>
    <button class="{BTN_SECONDARY}"><i class="icon ph ph-download-simple"></i><span>Export</span></button>
  </div>
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-md">
{stat("Revenue", "€48k", "12%")}
{stat("Invoices", "126", "5%")}
{stat("Overdue", "4", "2", up=False)}
  </div>
  <section class="flex flex-col gap-sm" aria-labelledby="blk-dash-recent">
    <div class="flex items-center justify-between gap-sm"><h3 id="blk-dash-recent" class="text-lg font-semibold">Recent invoices</h3><a href="#" class="text-sm fg-accent-1-11 hover:fg-accent-1-12">See all</a></div>
    <div class="overflow-x-auto rounded-md border border-neutral-6">
      <table class="w-full">
        <thead class="bg-neutral-2"><tr><th class="h-control ps-md pe-control text-start text-sm font-medium fg-neutral-11">Invoice</th><th class="h-control px-control text-start text-sm font-medium fg-neutral-11">Status</th><th class="h-control ps-control pe-md text-end text-sm font-medium fg-neutral-11">Amount</th></tr></thead>
        <tbody>
          <tr class="border-t border-neutral-6"><td class="h-control ps-md pe-control tabular-nums">1042</td><td class="h-control px-control"><span class="{BADGE} bg-success-3 border-success-6 fg-success-11"><span>Paid</span></span></td><td class="h-control ps-control pe-md text-end tabular-nums">€1,200</td></tr>
          <tr class="border-t border-neutral-6"><td class="h-control ps-md pe-control tabular-nums">1041</td><td class="h-control px-control"><span class="{BADGE} bg-warning-3 border-warning-6 fg-warning-11"><span>Due</span></span></td><td class="h-control ps-control pe-md text-end tabular-nums">€860</td></tr>
        </tbody>
      </table>
    </div>
  </section>
</div>""",
        "use": ["Figures first, then the rows behind them."],
        "avoid": ["Charts for a single number; the figure is clearer."],
    },
]
