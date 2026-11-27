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
]
