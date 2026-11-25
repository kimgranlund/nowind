"""Component docs data for scripts/templates.py: one entry per component, each a single HTML snippet that is both
rendered live and shown as code, with when to use it and when not to. Utility classes only."""

BTN = "inline-flex items-center justify-center h-control px-control gap-gutter rounded-sm"
BTN_PRIMARY = f"{BTN} border-0 bg-solid-accent-1 hover:bg-solid-accent-1-strong active:bg-solid-accent-1-strong text-on-solid-accent-1 text-title-sm cursor-pointer transition-colors"
BTN_SECONDARY = f"{BTN} border border-border bg-component-weak hover:bg-component active:bg-component-strong fg text-title-sm cursor-pointer transition-colors"
FIELD = "h-control px-control rounded-sm border border-border hover:border-border-strong aria-invalid:border-border-danger bg-bg text-control-md w-full transition-colors"
CARD = "p-surface rounded-lg bg-bg border border-border-weak"
MENU_ITEM = "flex items-center gap-gutter h-control px-control rounded-sm no-underline fg hover:bg-component-weak aria-selected:bg-component-accent-1-weak aria-selected:fg-accent-1-weak transition-colors"

COMPONENTS = [
    {
        "slug": "button", "name": "Button", "icon": "ph-cursor-click", "group": "Actions",
        "summary": "Starts an action. One control height tall, padded by the text edge, with an icon side that steps in by one margin.",
        "html": f"""<div class="flex flex-wrap items-center gap-row">
  <button class="{BTN_PRIMARY}"><span>Save changes</span></button>
  <button class="{BTN_SECONDARY}"><i class="icon ph ph-download-simple"></i><span>Export</span></button>
  <button class="{BTN} border-0 bg-transparent hover:bg-component-weak fg text-title-sm cursor-pointer transition-colors"><span>Cancel</span></button>
  <button class="{BTN} border-0 bg-solid-danger hover:bg-solid-danger-strong text-on-solid-danger text-title-sm cursor-pointer transition-colors"><i class="icon ph ph-trash"></i><span>Delete</span></button>
</div>""",
        "use": ["One primary button per view, for the action most people take.", "Wrap the label in a <code>&lt;span&gt;</code> so <code>px-control</code> can find an icon at either edge."],
        "avoid": ["A button for navigation; use a link styled the same way.", "Two primary buttons side by side; make the second secondary."],
    },
    {
        "slug": "icon-button", "name": "Icon button", "icon": "ph-plus-circle", "group": "Actions",
        "summary": "A button with only an icon. The same padding rules make it exactly one control height square.",
        "html": f"""<div class="flex items-center gap-row">
  <button class="{BTN} border border-border bg-component-weak hover:bg-component fg cursor-pointer transition-colors" aria-label="Settings"><i class="icon ph ph-gear"></i></button>
  <button class="{BTN} rounded-full border-0 bg-solid-accent-1 hover:bg-solid-accent-1-strong text-on-solid-accent-1 cursor-pointer transition-colors" aria-label="Add"><i class="icon ph-bold ph-plus"></i></button>
  <button class="inline-flex items-center justify-center h-nested px-nested rounded-xs border-0 bg-transparent hover:bg-component-weak fg-weak cursor-pointer transition-colors" aria-label="Close"><i class="icon icon-sm ph-bold ph-x"></i></button>
</div>""",
        "use": ["Always give it an <code>aria-label</code>.", "Use <code>h-nested px-nested</code> and <code>icon-sm</code> inside dense rows."],
        "avoid": ["An icon whose meaning isn't obvious; add a text label instead."],
    },
    {
        "slug": "segmented", "name": "Segmented control", "icon": "ph-squares-four", "group": "Actions",
        "summary": "A set of mutually exclusive options. The pressed segment is styled by <code>aria-pressed</code>, not by a class.",
        "html": """<div class="inline-flex items-center gap-3xs p-3xs rounded bg-component-weak" role="group" aria-label="Range">
  <button aria-pressed="true" class="inline-flex items-center h-nested px-nested rounded-xs border-0 bg-transparent hover:bg-component aria-pressed:bg-bg fg-weak aria-pressed:fg text-title-sm cursor-pointer transition-colors"><span>Day</span></button>
  <button aria-pressed="false" class="inline-flex items-center h-nested px-nested rounded-xs border-0 bg-transparent hover:bg-component aria-pressed:bg-bg fg-weak aria-pressed:fg text-title-sm cursor-pointer transition-colors"><span>Week</span></button>
  <button aria-pressed="false" class="inline-flex items-center h-nested px-nested rounded-xs border-0 bg-transparent hover:bg-component aria-pressed:bg-bg fg-weak aria-pressed:fg text-title-sm cursor-pointer transition-colors"><span>Month</span></button>
</div>""",
        "use": ["Two to five short options that change a view in place."],
        "avoid": ["Options that navigate to another page; use tabs."],
    },
    {
        "slug": "badge", "name": "Badge", "icon": "ph-tag", "group": "Status",
        "summary": "A short label for a status or category, at the nested control size.",
        "html": """<div class="flex flex-wrap items-center gap-2xs">
  <span class="inline-flex items-center h-nested px-nested gap-gutter-half rounded-full bg-component-weak border border-border-weak fg-weak text-label">Draft</span>
  <span class="inline-flex items-center h-nested px-nested gap-gutter-half rounded-full bg-component-success-weak border border-border-success-weak fg-success-weak text-label"><i class="icon icon-sm ph-bold ph-check"></i><span>Paid</span></span>
  <span class="inline-flex items-center h-nested px-nested gap-gutter-half rounded-full bg-component-warning-weak border border-border-warning-weak fg-warning-weak text-label"><i class="icon icon-sm ph-bold ph-clock"></i><span>Pending</span></span>
  <span class="inline-flex items-center h-nested px-nested rounded-full bg-solid-info text-on-solid-info text-label">New</span>
</div>""",
        "use": ["Pair a status color with its word, never color alone."],
        "avoid": ["A badge as a button; badges aren't interactive."],
    },
    {
        "slug": "alert", "name": "Alert", "icon": "ph-warning-circle", "group": "Status",
        "summary": "A message about the page or a task, tinted by its status.",
        "html": """<div class="flex gap-gutter p-surface rounded-lg bg-component-warning-weak border border-border-warning-weak" role="status">
  <i class="icon ph ph-warning fg-warning-weak"></i>
  <div class="flex flex-col gap-3xs">
    <span class="text-title fg-warning">Your trial ends in 3 days</span>
    <span class="text-body-sm fg-warning-weak">Add a payment method to keep your projects active.</span>
  </div>
</div>""",
        "use": ["<code>role=\"status\"</code> for information, <code>role=\"alert\"</code> only for errors that need attention now."],
        "avoid": ["Stacking several alerts; merge them into one."],
    },
    {
        "slug": "toast", "name": "Toast", "icon": "ph-bell-ringing", "group": "Status",
        "summary": "A brief confirmation on the inverse colors, with an optional action.",
        "html": """<div class="flex items-center gap-sm p-sm pl-md w-fit rounded-lg bg-bg-inverse shadow-lg" role="status">
  <i class="icon ph ph-check-circle fg-inverse"></i>
  <span class="text-body-sm fg-inverse">Invite sent</span>
  <button class="inline-flex items-center h-nested px-nested rounded-xs border-0 bg-transparent fg-accent-1-subtle text-title-sm cursor-pointer">Undo</button>
</div>""",
        "use": ["Confirm an action that already happened, with Undo when it can be reversed."],
        "avoid": ["Errors the person must fix; use an alert near the problem."],
    },
    {
        "slug": "text-field", "name": "Text field", "icon": "ph-textbox", "group": "Forms",
        "summary": "A labelled input with help text. <code>aria-invalid</code> switches the border to danger.",
        "html": f"""<div class="flex flex-col gap-group max-w-form">
  <div class="flex flex-col gap-field">
    <label for="doc-name" class="text-label">Full name</label>
    <input id="doc-name" class="{FIELD}" placeholder="Ada Lovelace">
    <span class="text-caption fg-weak">Shown on your profile.</span>
  </div>
  <div class="flex flex-col gap-field">
    <label for="doc-email" class="text-label">Email</label>
    <input id="doc-email" type="email" class="{FIELD}" value="ada@" aria-invalid="true" aria-describedby="doc-email-error">
    <span id="doc-email-error" class="text-caption fg-danger-weak">Enter a complete email address.</span>
  </div>
</div>""",
        "use": ["<code>gap-field</code> between label, control and help; <code>gap-group</code> between fields."],
        "avoid": ["A placeholder instead of a label."],
    },
    {
        "slug": "select", "name": "Select", "icon": "ph-list-dashes", "group": "Forms",
        "summary": "A native select. <code>select-base</code> turns on the customizable select, so the picker takes the theme.",
        "html": f"""<div class="flex flex-col gap-field max-w-form">
  <label for="doc-tz" class="text-label">Time zone</label>
  <select id="doc-tz" class="select-base {FIELD}">
    <option>Europe/Helsinki (UTC+2)</option>
    <option>Europe/London (UTC+0)</option>
    <option>America/New_York (UTC−5)</option>
  </select>
</div>""",
        "use": ["Five or more options; fewer fit a segmented control or radios."],
        "avoid": ["Options people need to compare side by side."],
    },
    {
        "slug": "form-controls", "name": "Checkbox, radio and switch", "icon": "ph-toggle-right", "group": "Forms",
        "summary": "Native inputs drawn by the reset at Affine's mark size. A switch is a checkbox with <code>role=\"switch\"</code>.",
        "html": """<div class="flex flex-col gap-xs">
  <label class="inline-flex items-center gap-xs text-body-md cursor-pointer"><input type="checkbox" checked> Product updates</label>
  <label class="inline-flex items-center gap-xs text-body-md cursor-pointer"><input type="radio" name="doc-plan" checked> Team plan</label>
  <label class="inline-flex items-center gap-xs text-body-md cursor-pointer"><input type="radio" name="doc-plan"> Business plan</label>
  <label class="flex items-center justify-between gap-sm max-w-form text-body-md cursor-pointer"><span>Email me about mentions</span><input type="checkbox" role="switch" checked></label>
  <input type="range" class="max-w-form" value="60" aria-label="Volume">
</div>""",
        "use": ["A switch for a setting that applies at once; a checkbox for one that waits for Save.", "<code>mark-sm</code> or <code>mark-lg</code> to change the size."],
        "avoid": ["Wrapping inputs in custom elements; the reset styles the native ones."],
    },
    {
        "slug": "card", "name": "Card", "icon": "ph-cards", "group": "Layout",
        "summary": "A surface that groups related content, padded at the surface level.",
        "html": f"""<article class="flex flex-col gap-field {CARD} shadow-sm max-w-form">
  <span class="text-kicker fg-accent-1-weak">Guide</span>
  <h3 class="text-title">Designing with fluid type</h3>
  <p class="text-body-sm fg-weak">Sizes that grow with the screen, without a single media query.</p>
  <div class="flex gap-row pt-xs"><button class="{BTN_SECONDARY}"><span>Read</span></button></div>
</article>""",
        "use": ["<code>p-surface</code> for padding; it already subtracts the border."],
        "avoid": ["Cards inside cards; use a divider or a subtle background instead."],
    },
    {
        "slug": "tabs", "name": "Tabs", "icon": "ph-tabs", "group": "Navigation",
        "summary": "Switches between views of the same thing. The selected tab is styled by <code>aria-selected</code>.",
        "html": """<div class="flex gap-md border-b border-border-weak overflow-x-auto" role="tablist">
  <button role="tab" aria-selected="true" class="inline-flex items-center gap-gutter h-control border-0 border-b-2 border-transparent aria-selected:border-border-accent-1-strong bg-transparent fg-weak hover:fg aria-selected:fg text-title-sm cursor-pointer transition-colors"><i class="icon ph ph-user"></i><span>Profile</span></button>
  <button role="tab" aria-selected="false" class="inline-flex items-center gap-gutter h-control border-0 border-b-2 border-transparent aria-selected:border-border-accent-1-strong bg-transparent fg-weak hover:fg aria-selected:fg text-title-sm cursor-pointer transition-colors"><i class="icon ph ph-credit-card"></i><span>Billing</span></button>
  <button role="tab" aria-selected="false" class="inline-flex items-center gap-gutter h-control border-0 border-b-2 border-transparent aria-selected:border-border-accent-1-strong bg-transparent fg-weak hover:fg aria-selected:fg text-title-sm cursor-pointer transition-colors"><i class="icon ph ph-users"></i><span>Members</span></button>
</div>""",
        "use": ["Moving <code>aria-selected</code> is all the script a tab needs for its look."],
        "avoid": ["More than six tabs; use a sidebar."],
    },
    {
        "slug": "breadcrumbs", "name": "Breadcrumbs", "icon": "ph-caret-right", "group": "Navigation",
        "summary": "Shows where a page sits in the hierarchy.",
        "html": """<nav aria-label="Breadcrumb">
  <ol role="list" class="flex flex-wrap items-center gap-2xs text-body-sm fg-weak">
    <li><a href="#" class="fg-weak hover:fg no-underline transition-colors">Projects</a></li>
    <li class="inline-flex" aria-hidden="true"><i class="icon icon-sm ph-bold ph-caret-right fg-subtle"></i></li>
    <li><a href="#" class="fg-weak hover:fg no-underline transition-colors">Nowind</a></li>
    <li class="inline-flex" aria-hidden="true"><i class="icon icon-sm ph-bold ph-caret-right fg-subtle"></i></li>
    <li class="fg" aria-current="page">Settings</li>
  </ol>
</nav>""",
        "use": ["Three or more levels deep."],
        "avoid": ["Repeating the page title right below it."],
    },
    {
        "slug": "pagination", "name": "Pagination", "icon": "ph-dots-three", "group": "Navigation",
        "summary": "Moves through pages of results. The current page is styled by <code>aria-current</code>.",
        "html": """<nav aria-label="Pagination" class="inline-flex items-center gap-3xs">
  <a href="#" class="inline-flex items-center justify-center size-control rounded-sm fg-weak hover:bg-component-weak no-underline transition-colors" aria-label="Previous"><i class="icon ph ph-caret-left"></i></a>
  <a href="#" class="inline-flex items-center justify-center size-control rounded-sm fg-weak hover:bg-component-weak aria-current:bg-solid-accent-1 aria-current:text-on-solid-accent-1 no-underline text-numeral transition-colors">2</a>
  <a href="#" aria-current="page" class="inline-flex items-center justify-center size-control rounded-sm fg-weak hover:bg-component-weak aria-current:bg-solid-accent-1 aria-current:text-on-solid-accent-1 no-underline text-numeral transition-colors">3</a>
  <a href="#" class="inline-flex items-center justify-center size-control rounded-sm fg-weak hover:bg-component-weak aria-current:bg-solid-accent-1 aria-current:text-on-solid-accent-1 no-underline text-numeral transition-colors">4</a>
  <a href="#" class="inline-flex items-center justify-center size-control rounded-sm fg-weak hover:bg-component-weak no-underline transition-colors" aria-label="Next"><i class="icon ph ph-caret-right"></i></a>
</nav>""",
        "use": ["Long lists where people jump to a page; show the total near it."],
        "avoid": ["Feeds people scroll through; load more instead."],
    },
    {
        "slug": "menu", "name": "Popover menu", "icon": "ph-list", "group": "Overlays",
        "summary": "A menu that opens with <code>popovertarget</code> and sits against its button with <code>anchor-bottom</code>. No script.",
        "html": f"""<button class="{BTN_SECONDARY}" popovertarget="doc-sort"><i class="icon ph ph-sort-ascending"></i><span>Sort</span><i class="icon icon-sm ph-bold ph-caret-down"></i></button>
<div id="doc-sort" popover class="anchor-bottom w-sidebar p-3xs rounded-lg bg-bg border border-border-weak shadow-lg">
  <div class="flex flex-col" role="listbox" aria-label="Sort by">
    <a href="#" class="{MENU_ITEM}" role="option" aria-selected="true"><i class="icon ph ph-clock"></i><span class="grow">Last edited</span></a>
    <a href="#" class="{MENU_ITEM}" role="option" aria-selected="false"><i class="icon ph ph-text-aa"></i><span class="grow">Name</span></a>
  </div>
</div>""",
        "use": ["Put layout classes such as <code>flex</code> on an inner element: on the popover itself they would keep it visible when closed."],
        "avoid": ["A menu for the page's main navigation."],
    },
    {
        "slug": "dialog", "name": "Dialog", "icon": "ph-app-window", "group": "Overlays",
        "summary": "A modal <code>&lt;dialog&gt;</code> opened with the <code>command</code> attribute; the reset dims the page behind it.",
        "html": f"""<button class="{BTN_SECONDARY}" commandfor="doc-dialog" command="show-modal"><i class="icon ph ph-trash"></i><span>Delete project…</span></button>
<dialog id="doc-dialog" class="m-auto p-dialog rounded-xl bg-bg border-0 shadow-xl max-w-form w-full" aria-labelledby="doc-dialog-title">
  <div class="flex flex-col gap-group">
    <h3 id="doc-dialog-title" class="text-title">Delete project?</h3>
    <p class="text-body-sm fg-weak">This removes the project for everyone. You can't undo this.</p>
    <div class="flex justify-end gap-row">
      <button class="{BTN_SECONDARY}" commandfor="doc-dialog" command="close"><span>Cancel</span></button>
      <button class="{BTN} border-0 bg-solid-danger hover:bg-solid-danger-strong text-on-solid-danger text-title-sm cursor-pointer transition-colors" commandfor="doc-dialog" command="close"><span>Delete</span></button>
    </div>
  </div>
</dialog>""",
        "use": ["<code>m-auto</code> centers it; the reset zeroes margins.", "Confirm destructive actions with the action's own word, not OK."],
        "avoid": ["Dialogs that open on page load."],
    },
    {
        "slug": "accordion", "name": "Accordion", "icon": "ph-rows", "group": "Disclosure",
        "summary": "Sections that open and close, built from <code>&lt;details&gt;</code>.",
        "html": """<div class="max-w-form">
  <details class="border-b border-border-weak" open>
    <summary class="flex items-center justify-between gap-sm py-sm list-none cursor-pointer text-title hover:fg-accent-1-weak transition-colors">Do I need a build step?<i class="icon ph ph-caret-down fg-weak"></i></summary>
    <p class="text-body-sm fg-weak pb-sm">No. Link one stylesheet; every class already exists.</p>
  </details>
  <details class="border-b border-border-weak">
    <summary class="flex items-center justify-between gap-sm py-sm list-none cursor-pointer text-title hover:fg-accent-1-weak transition-colors">Does it work in a CMS?<i class="icon ph ph-caret-down fg-weak"></i></summary>
    <p class="text-body-sm fg-weak pb-sm">Yes. Any class works in any HTML.</p>
  </details>
</div>""",
        "use": ["<code>list-none</code> on the summary hides the marker, including Safari's."],
        "avoid": ["Hiding content most people need; show it."],
    },
    {
        "slug": "avatar", "name": "Avatar and group", "icon": "ph-user-circle", "group": "Data display",
        "summary": "Initials on an accent solid, one control height square; a group overlaps them.",
        "html": """<div class="flex items-center">
  <span class="inline-flex items-center justify-center size-control rounded-full border-2 border-neutral-1 bg-solid-accent-1 text-on-solid-accent-1 text-label">AL</span>
  <span class="inline-flex items-center justify-center size-control rounded-full border-2 border-neutral-1 bg-solid-accent-2 text-on-solid-accent-2 text-label -ml-2xs">GH</span>
  <span class="inline-flex items-center justify-center size-control rounded-full border-2 border-neutral-1 bg-solid-accent-3 text-on-solid-accent-3 text-label -ml-2xs">KJ</span>
  <span class="inline-flex items-center justify-center size-control rounded-full border-2 border-neutral-1 bg-component fg-weak text-label -ml-2xs">+5</span>
</div>""",
        "use": ["A border in the page color separates overlapping avatars."],
        "avoid": ["More than five in a row; end with a count."],
    },
    {
        "slug": "progress", "name": "Progress bar", "icon": "ph-chart-bar-horizontal", "group": "Data display",
        "summary": "A track and a fill sized with a fraction class.",
        "html": """<div class="flex flex-col gap-field max-w-form">
  <div class="flex justify-between text-label"><span>Storage</span><span class="fg-weak tabular-nums">6.4 of 10 GB</span></div>
  <div class="rounded-full bg-component overflow-hidden" role="progressbar" aria-valuenow="64" aria-valuemin="0" aria-valuemax="100" aria-label="Storage used">
    <div class="w-2/3 py-3xs rounded-full bg-solid-accent-1"></div>
  </div>
</div>""",
        "use": ["Always print the value next to the bar."],
        "avoid": ["A bar for something that isn't a share of a whole."],
    },
    {
        "slug": "table", "name": "Table", "icon": "ph-table", "group": "Data display",
        "summary": "Rows of records in a surface that scrolls sideways on narrow screens.",
        "html": """<div class="rounded-lg bg-bg border border-border-weak overflow-x-auto">
  <table class="w-full text-body-sm">
    <thead class="bg-bg-strong">
      <tr><th class="text-left px-md py-xs text-label fg-weak border-b border-border-weak">Invoice</th><th class="text-left px-md py-xs text-label fg-weak border-b border-border-weak">Status</th><th class="text-right px-md py-xs text-label fg-weak border-b border-border-weak">Amount</th></tr>
    </thead>
    <tbody>
      <tr class="hover:bg-component-weak"><td class="px-md py-sm text-mono-sm border-b border-border-weak">INV-1042</td><td class="px-md py-sm border-b border-border-weak">Paid</td><td class="px-md py-sm text-right text-data border-b border-border-weak">$1,280.00</td></tr>
      <tr class="hover:bg-component-weak"><td class="px-md py-sm text-mono-sm">INV-1043</td><td class="px-md py-sm">Pending</td><td class="px-md py-sm text-right text-data">$640.50</td></tr>
    </tbody>
  </table>
</div>""",
        "use": ["<code>text-data</code> for figures so columns line up."],
        "avoid": ["A table for layout."],
    },
    {
        "slug": "empty-state", "name": "Empty state", "icon": "ph-folder-open", "group": "Feedback",
        "summary": "What a view shows before it has content, with the action that fills it.",
        "html": f"""<div class="flex flex-col items-center justify-center text-center gap-xs p-2xl rounded-lg border-2 border-dashed border-border">
  <span class="inline-flex items-center justify-center size-control rounded-full bg-component-weak fg-weak"><i class="icon ph ph-folder-open"></i></span>
  <h3 class="text-title">No projects yet</h3>
  <p class="text-body-sm fg-weak max-w-text">Create a project to collect designs, notes and feedback in one place.</p>
  <button class="{BTN_PRIMARY} mt-xs"><i class="icon ph ph-plus"></i><span>New project</span></button>
</div>""",
        "use": ["Say what will appear here and how to start."],
        "avoid": ["Jokes or illustrations that hide the action."],
    },
    {
        "slug": "loading", "name": "Spinner and skeleton", "icon": "ph-circle-notch", "group": "Feedback",
        "summary": "<code>animate-spin</code> for a short wait, <code>animate-pulse</code> placeholders for content that's on its way.",
        "html": """<div class="flex flex-col gap-group max-w-form">
  <div class="flex items-center gap-row"><i class="icon ph-bold ph-circle-notch animate-spin fg-accent-1-weak" aria-hidden="true"></i><span class="text-body-sm fg-weak">Saving changes…</span></div>
  <div class="flex items-center gap-sm animate-pulse" aria-hidden="true">
    <span class="size-control rounded-full bg-component"></span>
    <span class="flex flex-col gap-2xs grow"><span class="w-1/2 py-2xs rounded-full bg-component"></span><span class="w-3/4 py-2xs rounded-full bg-component"></span></span>
  </div>
</div>""",
        "use": ["Shape skeletons like the content that replaces them."],
        "avoid": ["A spinner for a wait longer than a few seconds; show progress."],
    },
    {
        "slug": "tooltip", "name": "Tooltip", "icon": "ph-chat-centered-text", "group": "Overlays",
        "summary": "A hint that shows when its trigger is hovered or focused. The wrapper is a <code>group</code>; the hint uses <code>group-hover:</code> and <code>group-focus-within:</code>. No script.",
        "html": """<span class="group relative inline-block">
  <button class="inline-flex items-center justify-center h-control px-control rounded-sm border border-border bg-component-weak hover:bg-component fg cursor-pointer transition-colors" aria-label="Copy link" aria-describedby="doc-tip"><i class="icon ph ph-link"></i></button>
  <span id="doc-tip" role="tooltip" class="absolute top-full left-0 z-20 mt-3xs px-xs py-3xs rounded-xs bg-bg-inverse fg-inverse text-caption whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible group-focus-within:opacity-100 group-focus-within:visible transition-opacity">Copy link</span>
</span>""",
        "use": ["A short label for an icon-only button, also given as its <code>aria-label</code>.", "<code>group-focus-within:</code> as well as <code>group-hover:</code>, so keyboard users see it."],
        "avoid": ["Anything people need to read to finish a task; put it on the page."],
    },
    {
        "slug": "combobox", "name": "Combobox", "icon": "ph-magnifying-glass", "group": "Forms",
        "summary": "A text field with suggestions, using the native <code>list</code> attribute and a <code>&lt;datalist&gt;</code>.",
        "html": f"""<div class="flex flex-col gap-field max-w-form">
  <label for="doc-country" class="text-label">Country</label>
  <input id="doc-country" list="doc-countries" class="{FIELD}" placeholder="Start typing">
  <datalist id="doc-countries">
    <option value="Finland"></option><option value="France"></option><option value="Germany"></option><option value="Japan"></option>
  </datalist>
</div>""",
        "use": ["Long lists where typing is faster than scrolling, and free text is allowed."],
        "avoid": ["A fixed set of five or fewer; use radios or a segmented control."],
    },
    {
        "slug": "sortable-table", "name": "Sortable table", "icon": "ph-sort-ascending", "group": "Data display",
        "summary": "Column headers hold buttons; <code>aria-sort</code> on the header says which column sorts the rows and in which order.",
        "html": """<div class="rounded-lg bg-bg border border-border-weak overflow-x-auto">
  <table class="w-full text-body-sm">
    <thead class="bg-bg-strong">
      <tr>
        <th aria-sort="ascending" class="text-left px-md py-xs border-b border-border-weak"><button class="inline-flex items-center gap-gutter-half border-0 bg-transparent fg text-label cursor-pointer">Name<i class="icon icon-sm ph-bold ph-caret-up"></i></button></th>
        <th aria-sort="none" class="text-right px-md py-xs border-b border-border-weak"><button class="inline-flex items-center gap-gutter-half border-0 bg-transparent fg-weak hover:fg text-label cursor-pointer transition-colors">Seats<i class="icon icon-sm ph-bold ph-caret-up-down"></i></button></th>
      </tr>
    </thead>
    <tbody>
      <tr class="hover:bg-component-weak"><td class="px-md py-sm border-b border-border-weak">Contoso</td><td class="px-md py-sm text-right text-data border-b border-border-weak">48</td></tr>
      <tr class="hover:bg-component-weak"><td class="px-md py-sm border-b border-border-weak">Fabrikam</td><td class="px-md py-sm text-right text-data border-b border-border-weak">12</td></tr>
      <tr class="hover:bg-component-weak"><td class="px-md py-sm">Northwind</td><td class="px-md py-sm text-right text-data">7</td></tr>
    </tbody>
  </table>
</div>""",
        "use": ["Show the sort direction with an icon and in <code>aria-sort</code>.", "Sorting itself is a script's job; the classes only show the state."],
        "avoid": ["Sorting columns nobody compares."],
    },
    {
        "slug": "date-range", "name": "Date range", "icon": "ph-calendar-blank", "group": "Forms",
        "summary": "Two native date fields grouped as one, with their own labels.",
        "html": f"""<fieldset class="flex flex-col gap-field border-0 p-0 max-w-form">
  <legend class="text-label mb-2xs">Stay</legend>
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-row">
    <div class="flex flex-col gap-field"><label for="doc-from" class="text-caption fg-weak">Check in</label><input id="doc-from" type="date" class="{FIELD}" value="2027-03-01"></div>
    <div class="flex flex-col gap-field"><label for="doc-to" class="text-caption fg-weak">Check out</label><input id="doc-to" type="date" class="{FIELD}" value="2027-03-05"></div>
  </div>
</fieldset>""",
        "use": ["Native date inputs: they bring the platform's picker and keyboard support."],
        "avoid": ["A single text field for both dates."],
    },
    {
        "slug": "media-card", "name": "Media card", "icon": "ph-image", "group": "Layout",
        "summary": "A card led by a 16:9 media area, then a title, a line of detail and its author.",
        "html": f"""<article class="flex flex-col {CARD} p-0 overflow-hidden max-w-form">
  <div class="aspect-video flex items-center justify-center bg-accent-2-a4 fg-accent-2-weak"><i class="icon icon-lg ph-light ph-mountains"></i></div>
  <div class="flex flex-col gap-field p-surface">
    <span class="text-kicker fg-accent-2-weak">Case study</span>
    <h3 class="text-title">Rebuilding a design system in a week</h3>
    <div class="flex items-center gap-xs pt-2xs">
      <span class="inline-flex items-center justify-center size-nested rounded-full bg-solid-accent-3 text-on-solid-accent-3 text-label">GH</span>
      <span class="text-caption fg-weak">Grace Hopper · 6 min read</span>
    </div>
  </div>
</article>""",
        "use": ["<code>aspect-video</code> keeps the media area's shape before the image loads."],
        "avoid": ["Text over the image without a scrim."],
    },
]
