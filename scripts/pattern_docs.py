"""Pattern docs data for scripts/templates.py: one entry per pattern, a composition of components that answers one task
(sign in, change a setting, filter a list). Same shape as component_docs.py, plus "components": the component slugs it
is built from, linked from its page. Utility classes only."""

from component_docs import BTN, BTN_PRIMARY, BTN_SECONDARY, BOX, BARE, CARD

LABEL = "text-sm font-medium"
HELP = "text-sm fg-neutral-11"
AVATAR = "inline-flex items-center justify-center size-control shrink-0 rounded-full text-sm font-medium"
ICON_BTN = "inline-flex items-center justify-center size-control shrink-0 rounded-sm state border border-transparent bg-transparent fg-neutral-11 cursor-pointer"
BADGE = "inline-flex items-center h-nested px-nested rounded-full border text-sm font-medium"
BTN_DANGER = f"{BTN} state border border-transparent bg-danger-9 fg-danger-contrast text-base font-medium cursor-pointer"


def field(fid, label, icon, attrs, help_=None):
    h = f'\n    <span class="{HELP}">{help_}</span>' if help_ else ""
    return f"""  <div class="flex flex-col gap-2xs">
    <label for="{fid}" class="{LABEL}">{label}</label>
    <div class="{BOX}"><i class="icon ph {icon} fg-neutral-11" aria-hidden="true"></i><input id="{fid}" class="{BARE}" {attrs}></div>{h}
  </div>"""


def setting(title, detail, control):
    return f"""  <div class="flex flex-col sm:flex-row sm:items-center gap-sm py-md border-t border-neutral-6">
    <div class="grow flex flex-col gap-3xs"><span class="text-base">{title}</span><span class="{HELP}">{detail}</span></div>
    {control}
  </div>"""


def person_row(initials, tone, name, meta, badge):
    return f"""    <li class="flex items-center gap-sm py-xs border-t border-neutral-6">
      <span class="{AVATAR} bg-{tone}-9 fg-{tone}-contrast">{initials}</span>
      <div class="grow min-w-0 flex flex-col gap-3xs"><span class="text-base truncate">{name}</span><span class="{HELP} truncate">{meta}</span></div>
      {badge}
      <button class="{ICON_BTN}" aria-label="Actions for {name}"><i class="icon ph-bold ph-dots-three-vertical"></i></button>
    </li>"""


def note(unread, icon, title, when):
    dot = '<i class="icon icon-sm ph-bold ph-dot-outline fg-accent-1-9" role="img" aria-label="Unread"></i>' if unread else '<i class="icon icon-sm" aria-hidden="true"></i>'
    return f"""    <li class="flex items-start gap-sm px-md py-sm border-t border-neutral-6">
      <i class="icon ph {icon} fg-neutral-11"></i>
      <div class="grow min-w-0 flex flex-col gap-3xs"><span class="text-base">{title}</span><span class="{HELP}">{when}</span></div>
      {dot}
    </li>"""


def tier(name, price, blurb, feats, primary):
    lis = "".join(f'<li class="flex gap-gutter"><i class="icon ph-bold ph-check fg-success-11"></i><span>{f}</span></li>' for f in feats)
    btn = BTN_PRIMARY if primary else BTN_SECONDARY
    ring = "border-accent-1-8" if primary else "border-neutral-6"
    return f"""  <div class="flex flex-col gap-md p-md rounded-md bg-neutral-1 border {ring}">
    <div class="flex flex-col gap-3xs"><span class="text-lg font-semibold">{name}</span><span class="{HELP}">{blurb}</span></div>
    <div class="flex items-baseline gap-3xs"><span class="text-3xl font-display font-extrabold tracking-tight tabular-nums">{price}</span><span class="{HELP}">per seat a month</span></div>
    <ul class="flex flex-col gap-xs list-none p-0 text-base">{lis}</ul>
    <button class="{btn} w-full"><span>Choose {name}</span></button>
  </div>"""


def comment(initials, tone, name, when, text):
    return f"""    <li class="flex gap-sm">
      <span class="{AVATAR} bg-{tone}-9 fg-{tone}-contrast">{initials}</span>
      <div class="grow min-w-0 flex flex-col gap-3xs">
        <div class="flex flex-wrap items-baseline gap-xs"><span class="text-base">{name}</span><span class="{HELP}">{when}</span></div>
        <p class="text-base">{text}</p>
      </div>
    </li>"""


def check_row(id_, label, done, files):
    return f"""    <tr class="border-t border-neutral-6 transition state">
      <td class="h-control px-control"><input type="checkbox" aria-label="Select {label}"{" checked" if done else ""}></td>
      <td class="h-control px-control">{label}</td>
      <td class="h-control ps-control pe-md text-end tabular-nums">{files}</td>
    </tr>"""


def task(done, title, detail, action=None):
    mark = ('<span class="inline-flex items-center justify-center size-nested shrink-0 rounded-full bg-success-9 fg-success-contrast"><i class="icon icon-sm ph-bold ph-check"></i></span>' if done
            else '<span class="inline-flex items-center justify-center size-nested shrink-0 rounded-full border border-neutral-7" aria-hidden="true"></span>')
    act = f'\n      <button class="{BTN_SECONDARY}"><span>{action}</span></button>' if action else ""
    return f"""    <li class="flex flex-wrap items-center gap-sm py-sm border-t border-neutral-6">
      {mark}
      <div class="grow min-w-0 flex flex-col gap-3xs"><span class="text-base{" line-through" if done else ""}">{title}</span><span class="{HELP}">{detail}</span></div>{act}
    </li>"""


def upload(name, size, pct, state):
    if state == "done":
        tail = '<i class="icon ph ph-check-circle fg-success-11" role="img" aria-label="Uploaded"></i>'
        bar = f'\n        <span class="{HELP} tabular-nums">{size}</span>'
    elif state == "error":
        tail = f'<button class="{ICON_BTN}" aria-label="Retry {name}"><i class="icon ph ph-arrow-clockwise"></i></button>'
        bar = f'\n        <span class="text-sm fg-danger-11">Upload failed. The file is over 10 MB.</span>'
    else:
        tail = f'<button class="{ICON_BTN}" aria-label="Cancel {name}"><i class="icon ph ph-x"></i></button>'
        bar = f'\n        <progress value="{pct}" max="100" aria-label="{name}">{pct}%</progress>\n        <span class="{HELP} tabular-nums">{pct}% uploaded</span>'
    return f"""    <li class="flex items-center gap-sm py-xs border-t border-neutral-6">
      <i class="icon ph ph-file-image fg-neutral-11"></i>
      <div class="grow min-w-0 flex flex-col gap-2xs">
        <span class="text-base truncate">{name}</span>{bar}
      </div>
      {tail}
    </li>"""


def faq(q, a, open_=False):
    return f"""  <details class="group border-b border-neutral-6"{" open" if open_ else ""}>
    <summary class="flex items-center justify-between gap-sm py-sm list-none cursor-pointer text-base font-semibold hover:fg-accent-1-11">{q}<i class="icon icon-sm ph ph-caret-down fg-neutral-11 transition group-open:rotate-180" aria-hidden="true"></i></summary>
    <p class="text-base fg-neutral-11 pb-sm">{a}</p>
  </details>"""


def feature(icon, title, text):
    return f"""  <div class="flex flex-col gap-xs">
    <span class="inline-flex items-center justify-center size-control shrink-0 rounded-sm bg-accent-1-3 fg-accent-1-11"><i class="icon ph {icon}"></i></span>
    <span class="text-lg font-semibold">{title}</span>
    <p class="text-base fg-neutral-11">{text}</p>
  </div>"""


def detail(term, value):
    return f'  <dt class="text-sm font-medium fg-neutral-11">{term}</dt>\n  <dd class="sm:col-span-2">{value}</dd>'


PATTERNS = [
    {
        "slug": "sign-in", "name": "Sign in", "icon": "ph-sign-in", "group": "Account",
        "components": ["card", "text-field", "button"],
        "summary": "A card with a title, two fields and one primary action the full width of the card, then a quieter second way in below a rule.",
        "html": f"""<form class="flex flex-col gap-md max-w-form {CARD}">
  <div class="flex flex-col gap-3xs"><h3 class="text-lg font-semibold">Sign in to Acme</h3><span class="{HELP}">Use the email you signed up with.</span></div>
{field("pat-email", "Email", "ph-envelope-simple", 'type="email" autocomplete="email" placeholder="ada@example.com"')}
{field("pat-password", "Password", "ph-lock-simple", 'type="password" autocomplete="current-password"', '<a href="#" class="fg-accent-1-11 hover:fg-accent-1-12">Forgot your password?</a>')}
  <button class="{BTN_PRIMARY} w-full" type="submit"><span>Sign in</span></button>
  <div class="flex items-center gap-sm {HELP}"><span class="grow border-t border-neutral-6" aria-hidden="true"></span><span>or</span><span class="grow border-t border-neutral-6" aria-hidden="true"></span></div>
  <button class="{BTN_SECONDARY} w-full" type="button"><i class="icon ph ph-key"></i><span>Use single sign-on</span></button>
</form>""",
        "use": ["Set <code>autocomplete</code> on each field, so password managers fill them.", "Put the reset link under the password, where people look when it fails."],
        "avoid": ["A sign-in form with a second primary button; one way in is the main one."],
    },
    {
        "slug": "settings-section", "name": "Settings section", "icon": "ph-sliders", "group": "Account",
        "components": ["form-controls", "select", "button"],
        "summary": "A titled group of settings, one per row: what it does on the left, its control on the right, a rule between rows. On a phone each row stacks.",
        "html": f"""<section class="flex flex-col max-w-form" aria-labelledby="pat-notify">
  <div class="flex flex-col gap-3xs pb-md"><h3 id="pat-notify" class="text-lg font-semibold">Notifications</h3><span class="{HELP}">Choose what reaches your inbox.</span></div>
{setting("Mentions", "When someone mentions you in a comment.", '<input type="checkbox" role="switch" checked aria-label="Mentions">')}
{setting("Weekly summary", "A digest of the week's changes, on Monday mornings.", '<input type="checkbox" role="switch" aria-label="Weekly summary">')}
{setting("Language", "Used for emails and dates.", f'<select class="select-base h-control px-control rounded-sm border border-neutral-5 hover:border-neutral-7 bg-neutral-1 text-base w-full sm:w-fit" aria-label="Language"><option>English (UK)</option><option>Deutsch</option><option>Suomi</option></select>')}
  <div class="flex justify-end gap-xs pt-md border-t border-neutral-6">
    <button class="{BTN_SECONDARY}"><span>Cancel</span></button>
    <button class="{BTN_PRIMARY}"><span>Save</span></button>
  </div>
</section>""",
        "use": ["Name each control after its row (<code>aria-label</code>), since the row's text is not its label.", "Switches take effect at once; keep Save for settings that wait for it."],
        "avoid": ["A switch and a Save button for the same setting."],
    },
    {
        "slug": "filter-bar", "name": "Filter bar", "icon": "ph-funnel", "group": "Data",
        "components": ["text-field", "segmented", "table"],
        "summary": "A search field that takes the free width, a segmented control for the view, and the count of what is shown, above the list it filters.",
        "html": f"""<div class="flex flex-col gap-sm">
  <div class="flex flex-wrap items-center gap-sm">
    <div class="{BOX} grow min-w-0"><i class="icon ph ph-magnifying-glass fg-neutral-11" aria-hidden="true"></i><input class="{BARE}" type="search" aria-label="Filter invoices" placeholder="Filter invoices"></div>
    <div class="inline-flex items-center h-control rounded-sm border-2 border-transparent bg-neutral-a2" role="group" aria-label="Status">
      <button aria-pressed="true" class="inline-flex items-center h-full px-nested rounded-inner border-0 bg-transparent hover:bg-neutral-4 pressed:bg-white fg-neutral-11 pressed:fg-black text-base font-medium cursor-pointer"><span>All</span></button>
      <button aria-pressed="false" class="inline-flex items-center h-full px-nested rounded-inner border-0 bg-transparent hover:bg-neutral-4 pressed:bg-white fg-neutral-11 pressed:fg-black text-base font-medium cursor-pointer"><span>Open</span></button>
      <button aria-pressed="false" class="inline-flex items-center h-full px-nested rounded-inner border-0 bg-transparent hover:bg-neutral-4 pressed:bg-white fg-neutral-11 pressed:fg-black text-base font-medium cursor-pointer"><span>Paid</span></button>
    </div>
  </div>
  <span class="{HELP}" role="status">Showing 3 of 3 invoices</span>
  <div class="overflow-x-auto rounded-md border border-neutral-6">
    <table class="w-full">
      <thead class="bg-neutral-2"><tr><th class="h-control ps-md pe-control text-start text-sm font-medium fg-neutral-11">Invoice</th><th class="h-control px-control text-start text-sm font-medium fg-neutral-11">Client</th><th class="h-control ps-control pe-md text-end text-sm font-medium fg-neutral-11">Amount</th></tr></thead>
      <tbody>
        <tr class="border-t border-neutral-6"><td class="h-control ps-md pe-control tabular-nums">1042</td><td class="h-control px-control">Northwind</td><td class="h-control ps-control pe-md text-end tabular-nums">€1,200</td></tr>
        <tr class="border-t border-neutral-6"><td class="h-control ps-md pe-control tabular-nums">1041</td><td class="h-control px-control">Contoso</td><td class="h-control ps-control pe-md text-end tabular-nums">€860</td></tr>
        <tr class="border-t border-neutral-6"><td class="h-control ps-md pe-control tabular-nums">1040</td><td class="h-control px-control">Fabrikam</td><td class="h-control ps-control pe-md text-end tabular-nums">€2,450</td></tr>
      </tbody>
    </table>
  </div>
</div>""",
        "use": ["Say how many of how many are shown, in a <code>role=\"status\"</code> line, so the change is announced."],
        "avoid": ["More than three filters in the bar; move the rest behind a Filters button."],
    },
    {
        "slug": "member-list", "name": "Member list", "icon": "ph-users", "group": "Data",
        "components": ["avatar", "badge", "action-menu"],
        "summary": "People one to a row: avatar, name and a supporting line, a role badge, and the row's actions behind one icon button at the end.",
        "html": f"""<section class="flex flex-col gap-sm max-w-form" aria-labelledby="pat-members">
  <div class="flex items-center justify-between gap-sm"><h3 id="pat-members" class="text-lg font-semibold">Members</h3><button class="{BTN_PRIMARY}"><i class="icon ph ph-user-plus"></i><span>Invite</span></button></div>
  <ul class="flex flex-col list-none p-0">
{person_row("AL", "accent-2", "Ada Lovelace", "ada@example.com", f'<span class="{BADGE} bg-accent-1-3 border-accent-1-6 fg-accent-1-11"><span>Owner</span></span>')}
{person_row("GH", "accent-3", "Grace Hopper", "grace@example.com", f'<span class="{BADGE} bg-neutral-3 border-neutral-6 fg-neutral-11"><span>Editor</span></span>')}
{person_row("KJ", "accent-4", "Katherine Johnson", "Invited 2 days ago", f'<span class="{BADGE} bg-warning-3 border-warning-6 fg-warning-11"><span>Pending</span></span>')}
  </ul>
</section>""",
        "use": ["Truncate the name and the supporting line, so the badge and actions stay on the row."],
        "avoid": ["A row of action buttons on every person; one menu keeps the list scannable."],
    },
    {
        "slug": "no-results", "name": "No results", "icon": "ph-magnifying-glass-minus", "group": "Feedback",
        "components": ["text-field", "empty-state", "button"],
        "summary": "A search that found nothing: the query stays in the field, and the empty state says what was searched and offers one way out.",
        "html": f"""<div class="flex flex-col gap-md max-w-form">
  <div class="{BOX}"><i class="icon ph ph-magnifying-glass fg-neutral-11" aria-hidden="true"></i><input class="{BARE}" type="search" aria-label="Search projects" value="quarterly forcast"><button class="inline-flex items-center justify-center size-nested shrink-0 rounded-xs state border border-transparent bg-transparent fg-neutral-11 cursor-pointer" aria-label="Clear search"><i class="icon icon-sm ph-bold ph-x"></i></button></div>
  <div class="flex flex-col items-center justify-center text-center gap-xs p-2xl rounded-md border-2 border-dashed" role="status">
    <span class="inline-flex items-center justify-center p-sm shrink-0 rounded-full bg-neutral-3 fg-neutral-11"><i class="icon icon-lg ph ph-magnifying-glass-minus"></i></span>
    <h3 class="text-lg font-semibold">No projects match “quarterly forcast”</h3>
    <p class="text-base fg-neutral-11 max-w-text">Check the spelling, or search all workspaces.</p>
    <button class="{BTN_SECONDARY}"><span>Search all workspaces</span></button>
  </div>
</div>""",
        "use": ["Repeat the query in the message, so people see what they typed."],
        "avoid": ["Clearing the field when nothing is found."],
    },
    {
        "slug": "notification-list", "name": "Notification list", "icon": "ph-bell", "group": "Feedback",
        "components": ["card", "button"],
        "summary": "A panel of notifications, newest first: an unread one carries a dot at the end, labelled for screen readers, and one action marks them all read.",
        "html": f"""<section class="flex flex-col max-w-form rounded-md bg-neutral-1 border border-neutral-6" aria-labelledby="pat-notes">
  <div class="flex items-center justify-between gap-sm ps-md pe-xs py-xs"><h3 id="pat-notes" class="text-lg font-semibold">Notifications</h3><button class="{BTN} state border border-transparent bg-transparent fg-neutral-12 text-base font-medium cursor-pointer"><span>Mark all read</span></button></div>
  <ul class="flex flex-col list-none p-0">
{note(True, "ph-chat-circle", "Grace replied to your comment on Q3 report", "5 minutes ago")}
{note(True, "ph-user-plus", "Katherine accepted your invite", "1 hour ago")}
{note(False, "ph-check-circle", "Export finished: invoices.csv", "Yesterday")}
  </ul>
</section>""",
        "use": ["Give the unread dot its own label, so the state is not colour alone."],
        "avoid": ["Notifications people must act on; send those to the page they concern."],
    },
    {
        "slug": "confirm-delete", "name": "Confirm delete", "icon": "ph-warning", "group": "Feedback",
        "components": ["dialog", "text-field", "button"],
        "summary": "The body of a dialog for an action that can't be undone: what will go, a field that asks for the name, and the danger button last. Shown here in place of the dialog.",
        "html": f"""<div class="flex flex-col gap-md max-w-form p-lg rounded-lg bg-neutral-1 border border-neutral-6 shadow-xl" role="alertdialog" aria-labelledby="pat-del-title" aria-describedby="pat-del-text">
  <h3 id="pat-del-title" class="text-lg font-semibold">Delete Q3 report?</h3>
  <p id="pat-del-text" class="text-base fg-neutral-11">This deletes the report and its 14 comments for everyone. You can't undo this.</p>
{field("pat-confirm", "Type the report's name to confirm", "ph-pencil-simple", 'autocomplete="off" placeholder="Q3 report"')}
  <div class="flex justify-end gap-xs">
    <button class="{BTN_SECONDARY}"><span>Cancel</span></button>
    <button class="{BTN_DANGER}"><i class="icon ph ph-trash"></i><span>Delete report</span></button>
  </div>
</div>""",
        "use": ["Name the thing and say what goes with it.", "Ask for the name only where a mistake is costly; one confirm is enough elsewhere."],
        "avoid": ["A confirm dialog for an action that can be undone; offer Undo in a toast instead."],
    },
    {
        "slug": "pricing", "name": "Pricing", "icon": "ph-currency-eur", "group": "Marketing",
        "components": ["card", "button"],
        "summary": "Plans side by side from <code>lg</code> up, each a card with a price in tabular figures, what it includes and its own button. The recommended plan takes the accent border.",
        "html": f"""<div class="grid grid-cols-1 lg:grid-cols-3 gap-md">
{tier("Starter", "€0", "For one person trying it out.", ["3 projects", "Community support"], False)}
{tier("Team", "€12", "For teams shipping every week.", ["Unlimited projects", "Shared libraries", "Email support"], True)}
{tier("Business", "€24", "For companies with many teams.", ["Everything in Team", "Single sign-on", "Audit log"], False)}
</div>""",
        "use": ["Three plans at most, with the one most people should pick in the middle."],
        "avoid": ["A feature list that differs only in numbers; put those in a comparison table."],
    },
    {
        "slug": "comment-thread", "name": "Comment thread", "icon": "ph-chats", "group": "Content",
        "components": ["avatar", "textarea", "button"],
        "summary": "Comments oldest first, each an avatar, a name with when it was written, and the text; the reply box last, where the thread ends.",
        "html": f"""<section class="flex flex-col gap-md max-w-form" aria-labelledby="pat-thread">
  <h3 id="pat-thread" class="text-lg font-semibold">Comments</h3>
  <ul class="flex flex-col gap-md list-none p-0">
{comment("GH", "accent-3", "Grace Hopper", "Monday, 09:12", "The forecast for March looks high. Is it before or after returns?")}
{comment("AL", "accent-2", "Ada Lovelace", "Monday, 10:40", "After returns. I've added a note under the chart.")}
  </ul>
  <div class="flex flex-col gap-2xs">
    <label for="pat-reply" class="{LABEL}">Reply</label>
    <textarea id="pat-reply" rows="3" class="px-control py-xs rounded-sm border border-neutral-5 hover:border-neutral-7 bg-neutral-1 text-base w-full" placeholder="Write a reply"></textarea>
    <div class="flex justify-end"><button class="{BTN_PRIMARY}"><span>Reply</span></button></div>
  </div>
</section>""",
        "use": ["Times relative while recent, a date once older than a week."],
        "avoid": ["Nesting replies more than one level; long threads read better flat."],
    },
    {
        "slug": "page-header", "name": "Page header", "icon": "ph-text-h", "group": "Navigation",
        "components": ["breadcrumbs", "button", "action-menu"],
        "summary": "Where the page sits, its title and one supporting line, with the page's actions at the end of the title row; on a phone the actions wrap under the title.",
        "html": f"""<header class="flex flex-col gap-sm pb-md border-b border-neutral-6">
  <nav aria-label="Breadcrumb">
    <ol role="list" class="flex flex-wrap items-center gap-2xs text-base fg-neutral-11">
      <li><a href="#" class="fg-neutral-11 hover:fg-neutral-12 no-underline">Projects</a></li>
      <li class="inline-flex" aria-hidden="true"><i class="icon icon-sm ph-bold ph-caret-right fg-neutral-8"></i></li>
      <li class="fg-neutral-12" aria-current="page">Q3 report</li>
    </ol>
  </nav>
  <div class="flex flex-wrap items-center gap-sm">
    <div class="grow min-w-0 flex flex-col gap-3xs"><h2 class="text-lg font-semibold">Q3 report</h2><span class="{HELP}">Edited 2 hours ago by Ada Lovelace</span></div>
    <div class="flex items-center gap-xs">
      <button class="{BTN_SECONDARY}"><i class="icon ph ph-share-network"></i><span>Share</span></button>
      <button class="{BTN_PRIMARY}"><span>Publish</span></button>
      <button class="inline-flex items-center justify-center size-control shrink-0 rounded-sm state border border-transparent bg-neutral-a2 fg-neutral-12 cursor-pointer" aria-label="More actions for Q3 report"><i class="icon ph-bold ph-dots-three"></i></button>
    </div>
  </div>
</header>""",
        "use": ["One primary action; the rest in secondary buttons or the menu."],
        "avoid": ["Breadcrumbs on a page one level down; the back link is enough."],
    },
    {
        "slug": "bulk-actions", "name": "Bulk actions", "icon": "ph-check-square", "group": "Data",
        "components": ["table", "form-controls", "button"],
        "summary": "A table with a checkbox on each row. While rows are selected a bar across the top of the table says how many, and holds what can be done to all of them.",
        "html": f"""<div class="overflow-x-auto rounded-md border border-neutral-6">
  <div class="flex flex-wrap items-center gap-sm p-inset bg-accent-1-3 border-b border-neutral-6" role="region" aria-label="Selection">
    <span class="grow ps-control text-base fg-accent-1-12 tabular-nums" role="status">2 folders selected</span>
    <button class="{BTN_SECONDARY}"><i class="icon ph ph-archive"></i><span>Archive</span></button>
    <button class="{BTN_DANGER}"><i class="icon ph ph-trash"></i><span>Delete</span></button>
  </div>
  <table class="w-full">
    <thead class="bg-neutral-2"><tr><td class="h-control px-control"><input type="checkbox" aria-label="Select all folders"></td><th class="h-control px-control text-start text-sm font-medium fg-neutral-11">Folder</th><th class="h-control ps-control pe-md text-end text-sm font-medium fg-neutral-11">Files</th></tr></thead>
    <tbody>
{check_row("a", "Invoices", True, "128")}
{check_row("b", "Contracts", True, "42")}
{check_row("c", "Receipts", False, "311")}
    </tbody>
  </table>
</div>""",
        "use": ["Put the count in a <code>role=\"status\"</code> line, so it is announced as it changes.", "A select-all checkbox in the header."],
        "avoid": ["Showing the bar before anything is selected."],
    },
    {
        "slug": "details-panel", "name": "Details panel", "icon": "ph-info", "group": "Data",
        "components": ["card", "description-list", "badge"],
        "summary": "One record's facts in a card: its name and status, then terms and values that stack on a phone and sit side by side from <code>sm</code> up.",
        "html": f"""<section class="flex flex-col gap-md max-w-form {CARD}" aria-labelledby="pat-inv">
  <div class="flex flex-wrap items-center gap-sm"><h3 id="pat-inv" class="grow text-lg font-semibold">Invoice 1042</h3><span class="{BADGE} bg-success-3 border-success-6 fg-success-11"><i class="icon icon-sm ph-bold ph-check"></i><span>Paid</span></span></div>
  <dl class="grid grid-cols-1 sm:grid-cols-3 gap-x-md gap-y-xs">
{detail("Client", "Northwind Traders")}
{detail("Issued", "2 March 2027")}
{detail("Amount", '<span class="tabular-nums">€1,200.00</span>')}
  </dl>
</section>""",
        "use": ["Status at the top, next to the name, where it is read first."],
        "avoid": ["Editing in place in a details panel; open a form."],
    },
    {
        "slug": "onboarding-checklist", "name": "Onboarding checklist", "icon": "ph-list-checks", "group": "Account",
        "components": ["card", "progress", "button"],
        "summary": "The first things to do, with how far along you are: done steps checked and struck through, the next one with its button.",
        "html": f"""<section class="flex flex-col gap-sm max-w-form {CARD}" aria-labelledby="pat-start">
  <div class="flex flex-col gap-2xs">
    <div class="flex items-baseline justify-between gap-sm"><h3 id="pat-start" class="text-lg font-semibold">Get started</h3><span class="{HELP} tabular-nums">1 of 3 done</span></div>
    <progress value="1" max="3" aria-labelledby="pat-start">1 of 3</progress>
  </div>
  <ul class="flex flex-col list-none p-0">
{task(True, "Create your workspace", "Done on Monday.")}
{task(False, "Invite your team", "People you invite can see every project.", "Invite")}
{task(False, "Import your files", "From a folder or another tool.", "Import")}
  </ul>
</section>""",
        "use": ["Three to five steps, each finished by one action."],
        "avoid": ["Hiding the product until the list is done."],
    },
    {
        "slug": "upload-list", "name": "Upload list", "icon": "ph-upload", "group": "Feedback",
        "components": ["file-upload", "progress", "icon-button"],
        "summary": "Files below the drop zone, one to a row: a bar while uploading with a way to cancel, the size once done, and the reason and a retry when it fails.",
        "html": f"""<section class="flex flex-col max-w-form" aria-label="Uploads">
  <ul class="flex flex-col list-none p-0">
{upload("cover.png", "2.4 MB", 100, "done")}
{upload("team-photo.jpg", "", 45, "progress")}
{upload("poster.tiff", "", 0, "error")}
  </ul>
</section>""",
        "use": ["Say why an upload failed, next to the file."],
        "avoid": ["One bar for the whole batch; people need to see which file is stuck."],
    },
    {
        "slug": "invite-form", "name": "Invite form", "icon": "ph-user-plus", "group": "Account",
        "components": ["text-field", "select", "button"],
        "summary": "An email field and a role on one row from <code>sm</code> up, the button at the end, and a line on what the role can do.",
        "html": f"""<form class="flex flex-col gap-2xs max-w-form">
  <label for="pat-invite" class="{LABEL}">Invite by email</label>
  <div class="flex flex-col sm:flex-row gap-xs">
    <div class="{BOX} grow min-w-0"><i class="icon ph ph-envelope-simple fg-neutral-11" aria-hidden="true"></i><input id="pat-invite" class="{BARE}" type="email" autocomplete="off" placeholder="name@example.com"></div>
    <select class="select-base h-control px-control rounded-sm border border-neutral-5 hover:border-neutral-7 bg-neutral-1 text-base w-full sm:w-fit" aria-label="Role"><option>Editor</option><option>Viewer</option><option>Owner</option></select>
    <button class="{BTN_PRIMARY}" type="submit"><span>Send invite</span></button>
  </div>
  <span class="{HELP}">Editors can change every project, but not billing.</span>
</form>""",
        "use": ["Default the role to the one most people get."],
        "avoid": ["Asking for a name; the person adds it when they join."],
    },
    {
        "slug": "faq", "name": "FAQ", "icon": "ph-question", "group": "Marketing",
        "components": ["accordion"],
        "summary": "Questions as an accordion under a title, the first answer open, and a way to ask something the list doesn't cover.",
        "html": f"""<section class="flex flex-col gap-md max-w-form" aria-labelledby="pat-faq">
  <h3 id="pat-faq" class="text-lg font-semibold">Questions</h3>
  <div class="flex flex-col">
{faq("Do I need a build step?", "No. Link one stylesheet and every class already exists.", True)}
{faq("Does it work in a CMS?", "Yes. Any class works in any HTML, including what an editor writes.")}
{faq("Can I change the colours?", "Set the palette tokens in your own stylesheet; every class follows.")}
  </div>
  <p class="text-base fg-neutral-11">Something else? <a href="#" class="fg-accent-1-11 hover:fg-accent-1-12">Ask us</a>.</p>
</section>""",
        "use": ["Questions in the words people ask them."],
        "avoid": ["An FAQ for things the product should explain where they happen."],
    },
    {
        "slug": "feature-grid", "name": "Feature grid", "icon": "ph-grid-nine", "group": "Marketing",
        "components": ["card"],
        "summary": "What a product does, three to a row from <code>lg</code> up: an icon in a tinted square, a title and one sentence each.",
        "html": f"""<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-lg">
{feature("ph-lightning", "No build step", "Link one stylesheet; every class is already there.")}
{feature("ph-moon", "Light and dark", "Every colour is a pair, so both modes come for free.")}
{feature("ph-text-aa", "Fluid type", "Sizes grow with the screen, without a media query.")}
</div>""",
        "use": ["One sentence per feature, about what it does for the reader."],
        "avoid": ["More than six features; the rest belong on their own page."],
    },
    {
        "slug": "newsletter", "name": "Newsletter sign-up", "icon": "ph-envelope", "group": "Marketing",
        "components": ["text-field", "button"],
        "summary": "A title, what people get and how often, and an email field with its button on one row from <code>sm</code> up.",
        "html": f"""<form class="flex flex-col gap-sm max-w-form {CARD}">
  <div class="flex flex-col gap-3xs"><h3 class="text-lg font-semibold">Release notes by email</h3><span class="{HELP}">One email when a version ships, about once a month.</span></div>
  <div class="flex flex-col sm:flex-row gap-xs">
    <div class="{BOX} grow min-w-0"><i class="icon ph ph-envelope-simple fg-neutral-11" aria-hidden="true"></i><input class="{BARE}" type="email" autocomplete="email" aria-label="Email" placeholder="ada@example.com"></div>
    <button class="{BTN_PRIMARY}" type="submit"><span>Subscribe</span></button>
  </div>
</form>""",
        "use": ["Say how often, so people know what they agree to."],
        "avoid": ["Asking for more than an email."],
    },
]
