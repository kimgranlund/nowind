"""Component docs data for scripts/templates.py: one entry per component, each a single HTML snippet that is both
rendered live and shown as code, with when to use it and when not to. Utility classes only."""

BTN = "inline-flex items-center justify-center py-xs px-sm gap-xs rounded-sm"
BTN_PRIMARY = f"{BTN} border border-transparent bg-accent-1-9 hover:bg-accent-1-10 active:bg-accent-1-10 fg-accent-1-contrast text-base font-medium cursor-pointer transition-colors"
BTN_SECONDARY = f"{BTN} border bg-neutral-3 hover:bg-neutral-4 active:bg-neutral-5 fg-neutral-12 text-base font-medium cursor-pointer transition-colors"
FIELD = "py-xs px-sm rounded-sm border hover:border-neutral-8 invalid:border-danger-7 bg-neutral-1 text-base w-full transition-colors"
BOX = "flex items-center gap-xs py-xs px-sm rounded-sm border hover:border-neutral-8 focus-within:border-accent-1-8 has-invalid:border-danger-7 bg-neutral-1 text-base cursor-text transition-colors"
BARE = "grow min-w-0 self-stretch p-0 border-0 bg-transparent fg-neutral-12"
KBD = "inline-flex items-center py-3xs px-2xs rounded-xs border fg-neutral-11 text-sm font-mono"
NESTED_SELECT = "select-base py-3xs px-2xs rounded-xs border border-transparent bg-transparent hover:bg-neutral-3 fg-neutral-12 text-base cursor-pointer"
NESTED_ICON = "inline-flex items-center justify-center p-3xs rounded-xs border border-transparent bg-transparent hover:bg-neutral-3 pressed:bg-neutral-4 fg-neutral-11 hover:fg-neutral-12 cursor-pointer transition-colors"
CARD = "p-md rounded-md bg-neutral-1 border border-neutral-6"
MENU_ITEM = "flex items-center gap-xs py-xs px-sm border border-transparent rounded-sm no-underline fg-neutral-12 hover:bg-neutral-3 selected:bg-accent-1-3 selected:fg-accent-1-11 transition-colors"

COMPONENTS = [
    {
        "slug": "button", "name": "Button", "icon": "ph-cursor-click", "group": "Actions",
        "summary": "Starts an action. One control height tall, padded by the text edge, with an icon side that steps in by one margin.",
        "html": f"""<div class="flex flex-wrap items-center gap-sm">
  <button class="{BTN_PRIMARY}"><span>Save changes</span></button>
  <button class="{BTN_SECONDARY}"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-download-simple"></i><span>Export</span></button>
  <button class="{BTN} border border-transparent bg-transparent hover:bg-neutral-3 fg-neutral-12 text-base font-medium cursor-pointer transition-colors"><span>Cancel</span></button>
  <button class="{BTN} border border-transparent bg-danger-9 hover:bg-danger-10 fg-danger-contrast text-base font-medium cursor-pointer transition-colors"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-trash"></i><span>Delete</span></button>
</div>""",
        "use": ["One primary button per view, for the action most people take.", "Wrap the label in a <code>&lt;span&gt;</code>, and put the icon in its own <code>&lt;i&gt;</code> beside it."],
        "avoid": ["A button for navigation; use a link styled the same way.", "Two primary buttons side by side; make the second secondary."],
    },
    {
        "slug": "icon-button", "name": "Icon button", "icon": "ph-plus-circle", "group": "Actions",
        "summary": "A button with only an icon. The same padding rules make it exactly one control height square.",
        "html": f"""<div class="flex items-center gap-sm">
  <button class="{BTN} border bg-neutral-3 hover:bg-neutral-4 fg-neutral-12 cursor-pointer transition-colors" aria-label="Settings"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-gear"></i></button>
  <button class="{BTN} rounded-full border border-transparent bg-accent-1-9 hover:bg-accent-1-10 fg-accent-1-contrast cursor-pointer transition-colors" aria-label="Add"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph-bold ph-plus"></i></button>
  <button class="inline-flex items-center justify-center py-3xs px-2xs rounded-xs border-0 bg-transparent hover:bg-neutral-3 fg-neutral-11 cursor-pointer transition-colors" aria-label="Close"><i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph-bold ph-x"></i></button>
</div>""",
        "use": ["Always give it an <code>aria-label</code>.", "Use <code>p-3xs</code> and a <code>text-base</code> icon inside dense rows."],
        "avoid": ["An icon whose meaning isn't obvious; add a text label instead."],
    },
    {
        "slug": "segmented", "name": "Segmented control", "icon": "ph-squares-four", "group": "Actions",
        "summary": "A set of mutually exclusive options. The pressed segment is styled by <code>aria-pressed</code>, not by a class.",
        "html": """<div class="inline-flex items-center gap-3xs p-inset rounded-sm border border-transparent bg-neutral-3" role="group" aria-label="Range">
  <button aria-pressed="true" class="inline-flex items-center py-3xs px-2xs rounded-xs border-0 bg-transparent hover:bg-neutral-4 pressed:bg-neutral-1 fg-neutral-11 pressed:fg-neutral-12 text-base font-medium cursor-pointer transition-colors"><span>Day</span></button>
  <button aria-pressed="false" class="inline-flex items-center py-3xs px-2xs rounded-xs border-0 bg-transparent hover:bg-neutral-4 pressed:bg-neutral-1 fg-neutral-11 pressed:fg-neutral-12 text-base font-medium cursor-pointer transition-colors"><span>Week</span></button>
  <button aria-pressed="false" class="inline-flex items-center py-3xs px-2xs rounded-xs border-0 bg-transparent hover:bg-neutral-4 pressed:bg-neutral-1 fg-neutral-11 pressed:fg-neutral-12 text-base font-medium cursor-pointer transition-colors"><span>Month</span></button>
</div>""",
        "use": ["Two to five short options that change a view in place."],
        "avoid": ["Options that navigate to another page; use tabs."],
    },
    {
        "slug": "badge", "name": "Badge", "icon": "ph-tag", "group": "Status",
        "summary": "A short label for a status or category, at the nested control size.",
        "html": """<div class="flex flex-wrap items-center gap-2xs">
  <span class="inline-flex items-center py-3xs px-2xs gap-2xs rounded-full bg-neutral-3 border border-neutral-6 fg-neutral-11 text-sm font-medium">Draft</span>
  <span class="inline-flex items-center py-3xs px-2xs gap-2xs rounded-full bg-success-3 border border-success-6 fg-success-11 text-sm font-medium"><i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph-bold ph-check"></i><span>Paid</span></span>
  <span class="inline-flex items-center py-3xs px-2xs gap-2xs rounded-full bg-warning-3 border border-warning-6 fg-warning-11 text-sm font-medium"><i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph-bold ph-clock"></i><span>Pending</span></span>
  <span class="inline-flex items-center py-3xs px-2xs rounded-full bg-info-9 fg-info-contrast text-sm font-medium">New</span>
</div>""",
        "use": ["Pair a status color with its word, never color alone."],
        "avoid": ["A badge as a button; badges aren't interactive."],
    },
    {
        "slug": "alert", "name": "Alert", "icon": "ph-warning-circle", "group": "Status",
        "summary": "A message about the page or a task, tinted by its status.",
        "html": """<div class="flex gap-xs p-md rounded-md bg-warning-3 border border-warning-6" role="status">
  <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-warning fg-warning-11"></i>
  <div class="flex flex-col gap-3xs">
    <span class="text-base font-semibold fg-warning-12">Your trial ends in 3 days</span>
    <span class="text-sm fg-warning-11">Add a payment method to keep your projects active.</span>
  </div>
</div>""",
        "use": ["<code>role=\"status\"</code> for information, <code>role=\"alert\"</code> only for errors that need attention now."],
        "avoid": ["Stacking several alerts; merge them into one."],
    },
    {
        "slug": "toast", "name": "Toast", "icon": "ph-bell-ringing", "group": "Status",
        "summary": "A brief confirmation on the inverse colors, with an optional action.",
        "html": """<div class="flex flex-wrap items-center gap-x-sm gap-y-2xs p-sm pl-md w-fit rounded-md bg-neutral-12 shadow-lg" role="status">
  <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-check-circle fg-neutral-1"></i>
  <span class="text-sm fg-neutral-1">Invite sent</span>
  <span class="ml-auto flex items-center gap-2xs"><button class="inline-flex items-center py-3xs px-2xs rounded-xs border-0 bg-transparent fg-accent-1-8 text-base font-medium cursor-pointer">Undo</button></span>
</div>""",
        "use": ["Confirm an action that already happened, with Undo when it can be reversed."],
        "avoid": ["Errors the person must fix; use an alert near the problem."],
    },
    {
        "slug": "text-field", "name": "Text field", "icon": "ph-textbox", "group": "Forms",
        "summary": "A labelled field built from slots: a leading icon that says what kind of value it takes, a prefix, the input, a suffix and a trailing action. The box is the control; the input inside is bare.",
        "html": f"""<div class="flex flex-col gap-md max-w-form">
  <div class="flex flex-col gap-2xs">
    <label for="doc-name" class="text-sm font-medium">Full name</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-user-circle fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-name" class="{BARE}" autocomplete="name" placeholder="Ada Lovelace">
    </div>
    <span class="text-sm fg-neutral-11">Shown on your profile.</span>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-email" class="text-sm font-medium">Email</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-envelope-simple fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-email" type="email" class="{BARE}" autocomplete="email" value="ada@" aria-invalid="true" aria-describedby="doc-email-error">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-warning-circle fg-danger-11" aria-hidden="true"></i>
    </div>
    <span id="doc-email-error" class="text-sm fg-danger-11">Enter a complete email address.</span>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-photo" class="text-sm font-medium">Photo</label>
    <input id="doc-photo" type="file" accept="image/*">
    <span class="text-sm fg-neutral-11">PNG or JPEG, up to 5 MB. The reset themes the button.</span>
  </div>
</div>""",
        "examples": [
            {"id": "slots", "label": "Slots",
             "summary": "Five slots, always in this order: leading icon, prefix, input, suffix, trailing. Any of them can be left out. An icon or a nested control at either end sits one margin from the edge, the same as in a button.",
             "html": f"""<div class="flex flex-col gap-md max-w-form">
  <div class="flex flex-col gap-2xs">
    <label for="doc-user" class="text-sm font-medium">Username <span class="fg-neutral-11">· leading icon</span></label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-at fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-user" class="{BARE}" autocomplete="username" spellcheck="false" placeholder="ada">
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-site" class="text-sm font-medium">Website <span class="fg-neutral-11">· prefix</span></label>
    <div class="{BOX}">
      <span class="fg-neutral-11 whitespace-nowrap" aria-hidden="true">https://</span>
      <input id="doc-site" type="text" inputmode="url" class="{BARE}" autocomplete="url" spellcheck="false" placeholder="yoursite.com">
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-find" class="text-sm font-medium">Search <span class="fg-neutral-11">· leading icon and trailing key</span></label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-magnifying-glass fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-find" type="search" class="{BARE}" placeholder="Search…">
      <kbd class="{KBD}">⌘S</kbd>
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-amount" class="text-sm font-medium">Amount <span class="fg-neutral-11">· prefix and trailing select</span></label>
    <div class="{BOX}">
      <span class="fg-neutral-11" aria-hidden="true">$</span>
      <input id="doc-amount" type="text" inputmode="decimal" class="{BARE} tabular-nums" placeholder="0.00">
      <select class="{NESTED_SELECT}" aria-label="Currency"><option>USD</option><option>EUR</option><option>GBP</option></select>
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-phone" class="text-sm font-medium">Phone <span class="fg-neutral-11">· leading select</span></label>
    <div class="{BOX}">
      <select class="{NESTED_SELECT}" aria-label="Country code"><option>US +1</option><option>FI +358</option><option>GB +44</option></select>
      <input id="doc-phone" type="tel" class="{BARE} tabular-nums" autocomplete="tel-national" placeholder="Phone number">
    </div>
  </div>
</div>"""},
            {"id": "types", "label": "Data types",
             "summary": "The leading icon names the kind of value; <code>type</code>, <code>inputmode</code> and <code>autocomplete</code> give the right keyboard and autofill. Units sit in the suffix, never in the value.",
             "html": f"""<div class="grid grid-cols-1 md:grid-cols-2 gap-md">
  <div class="flex flex-col gap-2xs">
    <label for="doc-pass" class="text-sm font-medium">Password</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-lock-simple fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-pass" type="password" class="{BARE}" autocomplete="new-password" value="correct horse">
      <button type="button" class="{NESTED_ICON}" aria-label="Show password" aria-pressed="false" onclick="const i=this.parentElement.querySelector('input');i.type=i.type==='password'?'text':'password';this.setAttribute('aria-pressed',i.type==='text')"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-eye"></i></button>
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-card" class="text-sm font-medium">Card number</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-credit-card fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-card" type="text" inputmode="numeric" class="{BARE} tabular-nums" autocomplete="cc-number" placeholder="1234 5678 9012 3456">
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-start" class="text-sm font-medium">Start date</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-calendar-blank fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-start" type="date" class="{BARE} tabular-nums" value="2027-03-01">
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-time" class="text-sm font-medium">Meeting time</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-clock fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-time" type="time" class="{BARE} tabular-nums" value="09:30">
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-weight" class="text-sm font-medium">Weight</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-scales fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-weight" type="text" inputmode="decimal" class="{BARE} tabular-nums" value="72.5">
      <span class="fg-neutral-11" aria-hidden="true">kg</span>
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-discount" class="text-sm font-medium">Discount</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-percent fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-discount" type="number" min="0" max="100" step="5" class="{BARE} tabular-nums" value="15">
      <span class="fg-neutral-11" aria-hidden="true">%</span>
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-quantity" class="text-sm font-medium">Quantity</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-hash fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-quantity" type="number" min="1" step="1" class="{BARE} tabular-nums" value="3">
      <span class="fg-neutral-11" aria-hidden="true">seats</span>
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-hex" class="text-sm font-medium">Brand colour</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-palette fg-neutral-11" aria-hidden="true"></i>
      <span class="fg-neutral-11" aria-hidden="true">#</span>
      <input id="doc-hex" type="text" class="{BARE} tabular-nums" spellcheck="false" maxlength="6" value="0090FF">
      <input type="color" class="p-3xs rounded-xs border border-transparent p-0 bg-transparent cursor-pointer" value="#0090ff" aria-label="Pick a colour">
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-zip" class="text-sm font-medium">Postal code</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-map-pin fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-zip" type="text" inputmode="numeric" class="{BARE} tabular-nums" autocomplete="postal-code" placeholder="00100">
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-duration" class="text-sm font-medium">Duration</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-timer fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-duration" type="number" min="0" step="15" class="{BARE} tabular-nums" value="45">
      <span class="fg-neutral-11" aria-hidden="true">min</span>
    </div>
  </div>
</div>"""},
            {"id": "states", "label": "States",
             "summary": "The box shows every state of the input inside it: <code>focus-within:</code> turns the border accent, <code>has-invalid:</code> turns it danger. A disabled or read-only field says so with its fill as well as its text.",
             "html": f"""<div class="grid grid-cols-1 md:grid-cols-2 gap-md">
  <div class="flex flex-col gap-2xs">
    <label for="doc-handle" class="text-sm font-medium">Handle</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-at fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-handle" class="{BARE}" value="ada lovelace" pattern="[a-z0-9_]+" aria-invalid="true" aria-describedby="doc-handle-error">
    </div>
    <span id="doc-handle-error" class="text-sm fg-danger-11">Use lowercase letters, numbers and underscores.</span>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-title" class="text-sm font-medium">Title</label>
    <div class="{BOX}">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-text-t fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-title" class="{BARE}" maxlength="40" value="Analytical Engine notes" aria-describedby="doc-title-count">
      <span id="doc-title-count" class="fg-neutral-11 text-sm tabular-nums">23/40</span>
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-id" class="text-sm font-medium">Account ID</label>
    <div class="{BOX} bg-neutral-2">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-identification-card fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-id" class="{BARE} fg-neutral-11 tabular-nums" value="AC-20481" readonly>
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-lock-simple fg-neutral-8" aria-hidden="true"></i>
    </div>
  </div>
  <div class="flex flex-col gap-2xs">
    <label for="doc-seat" class="text-sm font-medium fg-neutral-11">Seat</label>
    <div class="{BOX} bg-neutral-3 opacity-50 cursor-not-allowed">
      <i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-armchair fg-neutral-11" aria-hidden="true"></i>
      <input id="doc-seat" class="{BARE}" value="14C" disabled>
    </div>
  </div>
</div>"""},
        ],
        "use": ["A leading icon for the kind of value, so a long form scans by shape.", "Prefixes and suffixes for parts the person doesn't type: a scheme, a currency sign, a unit.", "<code>gap-2xs</code> between label, box and help; <code>gap-md</code> between fields."],
        "avoid": ["A placeholder instead of a label.", "A unit inside the value (\"72.5 kg\"): it breaks number keyboards and parsing.", "More than one trailing action in a box."],
    },
    {
        "slug": "select", "name": "Select", "icon": "ph-list-dashes", "group": "Forms",
        "summary": "A native select. <code>select-base</code> turns on the customizable select, so the picker takes the theme; a <code>&lt;button&gt;</code> holding <code>&lt;selectedcontent&gt;</code> lets a long value end in an ellipsis instead of wrapping.",
        "html": f"""<div class="flex flex-col gap-2xs max-w-form">
  <label for="doc-tz" class="text-sm font-medium">Time zone</label>
  <select id="doc-tz" class="select-base {FIELD}">
    <button class="grow min-w-0 p-0 border-0 bg-transparent text-left"><selectedcontent class="block truncate"></selectedcontent></button>
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
  <label class="inline-flex items-center gap-xs text-base cursor-pointer"><input type="checkbox" checked> Product updates</label>
  <label class="inline-flex items-center gap-xs text-base cursor-pointer"><input type="radio" name="doc-plan" checked> Team plan</label>
  <label class="inline-flex items-center gap-xs text-base cursor-pointer"><input type="radio" name="doc-plan"> Business plan</label>
  <label class="flex items-center justify-between gap-sm max-w-form text-base cursor-pointer"><span>Email me about mentions</span><input type="checkbox" role="switch" checked></label>
  <input type="range" class="max-w-form" value="60" aria-label="Volume">
</div>""",
        "use": ["A switch for a setting that applies at once; a checkbox for one that waits for Save.", "Wrap each one in its label, so the text is part of the target."],
        "avoid": ["Wrapping inputs in custom elements; the reset styles the native ones."],
    },
    {
        "slug": "card", "name": "Card", "icon": "ph-cards", "group": "Layout",
        "summary": "A surface that groups related content, padded at the surface level.",
        "html": f"""<article class="flex flex-col gap-2xs {CARD} shadow-sm max-w-form">
  <span class="text-xs font-mono uppercase tracking-widest fg-accent-1-11">Guide</span>
  <h3 class="text-base font-semibold">Designing with fluid type</h3>
  <p class="text-sm fg-neutral-11">Sizes that grow with the screen, without a single media query.</p>
  <div class="flex gap-sm pt-xs"><button class="{BTN_SECONDARY}"><span>Read</span></button></div>
</article>""",
        "use": ["<code>p-md</code> for padding, the same on every card."],
        "avoid": ["Cards inside cards; use a divider or a subtle background instead."],
    },
    {
        "slug": "tabs", "name": "Tabs", "icon": "ph-tabs", "group": "Navigation",
        "summary": "Switches between views of the same thing. The selected tab is styled by <code>aria-selected</code>.",
        "html": """<div class="flex gap-md border-b border-neutral-6 overflow-x-auto" role="tablist">
  <button role="tab" aria-selected="true" class="inline-flex items-center gap-xs py-xs px-sm border border-b-2 border-transparent selected:border-accent-1-8 bg-transparent fg-neutral-11 hover:fg-neutral-12 selected:fg-neutral-12 text-base font-medium cursor-pointer transition-colors rounded-none"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-user"></i><span>Profile</span></button>
  <button role="tab" aria-selected="false" class="inline-flex items-center gap-xs py-xs px-sm border border-b-2 border-transparent selected:border-accent-1-8 bg-transparent fg-neutral-11 hover:fg-neutral-12 selected:fg-neutral-12 text-base font-medium cursor-pointer transition-colors rounded-none"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-credit-card"></i><span>Billing</span></button>
  <button role="tab" aria-selected="false" class="inline-flex items-center gap-xs py-xs px-sm border border-b-2 border-transparent selected:border-accent-1-8 bg-transparent fg-neutral-11 hover:fg-neutral-12 selected:fg-neutral-12 text-base font-medium cursor-pointer transition-colors rounded-none"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-users"></i><span>Members</span></button>
</div>""",
        "use": ["Moving <code>aria-selected</code> is all the script a tab needs for its look."],
        "avoid": ["More than six tabs; use a sidebar."],
    },
    {
        "slug": "breadcrumbs", "name": "Breadcrumbs", "icon": "ph-caret-right", "group": "Navigation",
        "summary": "Shows where a page sits in the hierarchy.",
        "html": """<nav aria-label="Breadcrumb">
  <ol role="list" class="flex flex-wrap items-center gap-2xs text-sm fg-neutral-11">
    <li><a href="#" class="fg-neutral-11 hover:fg-neutral-12 no-underline transition-colors">Projects</a></li>
    <li class="inline-flex" aria-hidden="true"><i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph-bold ph-caret-right fg-neutral-8"></i></li>
    <li><a href="#" class="fg-neutral-11 hover:fg-neutral-12 no-underline transition-colors">Nowind</a></li>
    <li class="inline-flex" aria-hidden="true"><i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph-bold ph-caret-right fg-neutral-8"></i></li>
    <li class="fg-neutral-12" aria-current="page">Settings</li>
  </ol>
</nav>""",
        "use": ["Three or more levels deep."],
        "avoid": ["Repeating the page title right below it."],
    },
    {
        "slug": "pagination", "name": "Pagination", "icon": "ph-dots-three", "group": "Navigation",
        "summary": "Moves through pages of results. The current page is styled by <code>aria-current</code>.",
        "html": """<nav aria-label="Pagination" class="inline-flex items-center gap-3xs">
  <a href="#" class="inline-flex items-center justify-center p-xs border border-transparent rounded-sm fg-neutral-11 hover:bg-neutral-3 no-underline transition-colors" aria-label="Previous"><i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph ph-caret-left"></i></a>
  <a href="#" class="inline-flex items-center justify-center p-xs border border-transparent rounded-sm fg-neutral-11 hover:bg-neutral-3 current:bg-accent-1-9 current:fg-accent-1-contrast no-underline text-base font-medium tabular-nums transition-colors">2</a>
  <a href="#" aria-current="page" class="inline-flex items-center justify-center p-xs border border-transparent rounded-sm fg-neutral-11 hover:bg-neutral-3 current:bg-accent-1-9 current:fg-accent-1-contrast no-underline text-base font-medium tabular-nums transition-colors">3</a>
  <a href="#" class="inline-flex items-center justify-center p-xs border border-transparent rounded-sm fg-neutral-11 hover:bg-neutral-3 current:bg-accent-1-9 current:fg-accent-1-contrast no-underline text-base font-medium tabular-nums transition-colors">4</a>
  <a href="#" class="inline-flex items-center justify-center p-xs border border-transparent rounded-sm fg-neutral-11 hover:bg-neutral-3 no-underline transition-colors" aria-label="Next"><i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph ph-caret-right"></i></a>
</nav>""",
        "use": ["Long lists where people jump to a page; show the total near it."],
        "avoid": ["Feeds people scroll through; load more instead."],
    },
    {
        "slug": "menu", "name": "Popover menu", "icon": "ph-list", "group": "Overlays",
        "summary": "A menu that opens with <code>popovertarget</code> and sits against its button with <code>anchor-bottom</code>. No script.",
        "html": f"""<div class="group inline-block">
<button class="{BTN_SECONDARY}" popovertarget="doc-sort"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-sort-ascending"></i><span>Sort</span><i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph ph-caret-down transition group-open:rotate-180" aria-hidden="true"></i></button>
<div id="doc-sort" popover class="anchor-bottom w-fit p-inset rounded-md bg-neutral-1 border border-neutral-6 shadow-lg">
  <div class="flex flex-col" role="listbox" aria-label="Sort by">
    <a href="#" class="{MENU_ITEM}" role="option" aria-selected="true"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-clock"></i><span class="grow">Last edited</span></a>
    <a href="#" class="{MENU_ITEM}" role="option" aria-selected="false"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-text-aa"></i><span class="grow">Name</span></a>
  </div>
</div>
</div>""",
        "use": ["Put layout classes such as <code>flex</code> on an inner element: on the popover itself they would keep it visible when closed."],
        "avoid": ["A menu for the page's main navigation."],
    },
    {
        "slug": "dialog", "name": "Dialog", "icon": "ph-app-window", "group": "Overlays",
        "summary": "A modal <code>&lt;dialog&gt;</code> opened with the <code>command</code> attribute; the reset dims the page behind it.",
        "html": f"""<button class="{BTN_SECONDARY}" commandfor="doc-dialog" command="show-modal"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-trash"></i><span>Delete project…</span></button>
<dialog id="doc-dialog" class="m-auto p-lg rounded-lg bg-neutral-1 border-0 shadow-xl max-w-form w-full" aria-labelledby="doc-dialog-title">
  <div class="flex flex-col gap-md">
    <h3 id="doc-dialog-title" class="text-base font-semibold">Delete project?</h3>
    <p class="text-sm fg-neutral-11">This removes the project for everyone. You can't undo this.</p>
    <div class="flex justify-end gap-sm">
      <button class="{BTN_SECONDARY}" commandfor="doc-dialog" command="close"><span>Cancel</span></button>
      <button class="{BTN} border border-transparent bg-danger-9 hover:bg-danger-10 fg-danger-contrast text-base font-medium cursor-pointer transition-colors" commandfor="doc-dialog" command="close"><span>Delete</span></button>
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
  <details class="group border-b border-neutral-6" open>
    <summary class="flex items-center justify-between gap-sm py-sm list-none cursor-pointer text-base font-semibold hover:fg-accent-1-11 transition-colors">Do I need a build step?<i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph ph-caret-down fg-neutral-11 transition group-open:rotate-180" aria-hidden="true"></i></summary>
    <p class="text-sm fg-neutral-11 pb-sm">No. Link one stylesheet; every class already exists.</p>
  </details>
  <details class="group border-b border-neutral-6">
    <summary class="flex items-center justify-between gap-sm py-sm list-none cursor-pointer text-base font-semibold hover:fg-accent-1-11 transition-colors">Does it work in a CMS?<i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph ph-caret-down fg-neutral-11 transition group-open:rotate-180" aria-hidden="true"></i></summary>
    <p class="text-sm fg-neutral-11 pb-sm">Yes. Any class works in any HTML.</p>
  </details>
</div>""",
        "use": ["<code>list-none</code> on the summary hides the marker, including Safari's."],
        "avoid": ["Hiding content most people need; show it."],
    },
    {
        "slug": "avatar", "name": "Avatar and group", "icon": "ph-user-circle", "group": "Data display",
        "summary": "Initials on an accent solid, one control height square; a group overlaps them.",
        "html": """<div class="flex items-center">
  <span class="inline-flex items-center justify-center p-xs rounded-full border-2 border-neutral-1 bg-accent-1-9 fg-accent-1-contrast text-sm font-medium">AL</span>
  <span class="inline-flex items-center justify-center p-xs rounded-full border-2 border-neutral-1 bg-accent-2-9 fg-accent-2-contrast text-sm font-medium -ml-2xs">GH</span>
  <span class="inline-flex items-center justify-center p-xs rounded-full border-2 border-neutral-1 bg-accent-3-9 fg-accent-3-contrast text-sm font-medium -ml-2xs">KJ</span>
  <span class="inline-flex items-center justify-center p-xs rounded-full border-2 border-neutral-1 bg-neutral-4 fg-neutral-11 text-sm font-medium -ml-2xs">+5</span>
</div>""",
        "use": ["A border in the page color separates overlapping avatars."],
        "avoid": ["More than five in a row; end with a count."],
    },
    {
        "slug": "progress", "name": "Progress bar", "icon": "ph-chart-bar-horizontal", "group": "Data display",
        "summary": "Native <code>progress</code> and <code>meter</code>, themed by the reset, or a track and a fill sized with a fraction class.",
        "html": """<div class="flex flex-col gap-md max-w-form">
  <div class="flex flex-col gap-2xs">
    <div class="flex justify-between text-sm font-medium"><label for="doc-upload">Uploading</label><span class="fg-neutral-11 tabular-nums">64%</span></div>
    <progress id="doc-upload" value="64" max="100">64%</progress>
  </div>
  <div class="flex flex-col gap-2xs">
    <div class="flex justify-between text-sm font-medium"><label for="doc-disk">Disk</label><span class="fg-neutral-11 tabular-nums">9.1 of 10 GB</span></div>
    <meter id="doc-disk" value="9.1" min="0" max="10" low="6" high="8.5" optimum="2">9.1 of 10 GB</meter>
  </div>
  <div class="flex flex-col gap-2xs">
    <div class="flex justify-between text-sm font-medium"><span>Storage</span><span class="fg-neutral-11 tabular-nums">6.4 of 10 GB</span></div>
    <div class="rounded-full bg-neutral-4 overflow-hidden" role="progressbar" aria-valuenow="64" aria-valuemin="0" aria-valuemax="100" aria-label="Storage used">
      <div class="w-2/3 py-3xs rounded-full bg-accent-1-9"></div>
    </div>
  </div>
</div>""",
        "use": ["Always print the value next to the bar.", "<code>progress</code> for a task under way; <code>meter</code> for a level within a range, which turns warning or danger past its <code>high</code> and <code>low</code>."],
        "avoid": ["A bar for something that isn't a share of a whole."],
    },
    {
        "slug": "table", "name": "Table", "icon": "ph-table", "group": "Data display",
        "summary": "Rows of records in a surface that scrolls sideways on narrow screens.",
        "html": """<div class="rounded-md bg-neutral-1 border border-neutral-6 overflow-x-auto">
  <table class="w-full text-sm">
    <thead class="bg-neutral-2">
      <tr><th class="text-left px-md py-xs text-sm font-medium fg-neutral-11 border-b border-neutral-6">Invoice</th><th class="text-left px-md py-xs text-sm font-medium fg-neutral-11 border-b border-neutral-6">Status</th><th class="text-right px-md py-xs text-sm font-medium fg-neutral-11 border-b border-neutral-6">Amount</th></tr>
    </thead>
    <tbody>
      <tr class="hover:bg-neutral-3 transition"><td class="px-md py-sm text-sm font-mono border-b border-neutral-6">INV-1042</td><td class="px-md py-sm border-b border-neutral-6">Paid</td><td class="px-md py-sm text-right text-sm font-mono tabular-nums border-b border-neutral-6">$1,280.00</td></tr>
      <tr class="hover:bg-neutral-3 transition"><td class="px-md py-sm text-sm font-mono">INV-1043</td><td class="px-md py-sm">Pending</td><td class="px-md py-sm text-right text-sm font-mono tabular-nums">$640.50</td></tr>
    </tbody>
  </table>
</div>""",
        "use": ["<code>font-mono tabular-nums</code> for figures so columns line up."],
        "avoid": ["A table for layout."],
    },
    {
        "slug": "empty-state", "name": "Empty state", "icon": "ph-folder-open", "group": "Feedback",
        "summary": "What a view shows before it has content, with the action that fills it.",
        "html": f"""<div class="flex flex-col items-center justify-center text-center gap-xs p-2xl rounded-md border-2 border-dashed">
  <span class="inline-flex items-center justify-center p-xs rounded-full bg-neutral-3 fg-neutral-11"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-folder-open"></i></span>
  <h3 class="text-base font-semibold">No projects yet</h3>
  <p class="text-sm fg-neutral-11 max-w-text">Create a project to collect designs, notes and feedback in one place.</p>
  <button class="{BTN_PRIMARY} mt-xs"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-plus"></i><span>New project</span></button>
</div>""",
        "use": ["Say what will appear here and how to start."],
        "avoid": ["Jokes or illustrations that hide the action."],
    },
    {
        "slug": "loading", "name": "Spinner and skeleton", "icon": "ph-circle-notch", "group": "Feedback",
        "summary": "<code>animate-spin</code> for a short wait, <code>animate-pulse</code> placeholders for content that's on its way.",
        "html": """<div class="flex flex-col gap-md max-w-form">
  <div class="flex items-center gap-sm"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph-bold ph-circle-notch animate-spin fg-accent-1-11" aria-hidden="true"></i><span class="text-sm fg-neutral-11">Saving changes…</span></div>
  <div class="flex items-center gap-sm animate-pulse" aria-hidden="true">
    <span class="p-xs rounded-full bg-neutral-4"></span>
    <span class="flex flex-col gap-2xs grow"><span class="w-1/2 py-2xs rounded-full bg-neutral-4"></span><span class="w-3/4 py-2xs rounded-full bg-neutral-4"></span></span>
  </div>
</div>""",
        "use": ["Shape skeletons like the content that replaces them."],
        "avoid": ["A spinner for a wait longer than a few seconds; show progress."],
    },
    {
        "slug": "tooltip", "name": "Tooltip", "icon": "ph-chat-centered-text", "group": "Overlays",
        "summary": "A hint that shows when its trigger is hovered or focused. The wrapper is a <code>group</code>; the hint uses <code>group-hover:</code> and <code>group-focus-within:</code>. No script.",
        "html": """<span class="group relative inline-block">
  <button class="inline-flex items-center justify-center py-xs px-sm rounded-sm border bg-neutral-3 hover:bg-neutral-4 fg-neutral-12 cursor-pointer transition-colors" aria-label="Copy link" aria-describedby="doc-tip"><i class="inline-flex items-center justify-center shrink-0 text-xl leading-none ph ph-link"></i></button>
  <span id="doc-tip" role="tooltip" class="absolute top-full left-0 z-20 mt-3xs px-xs py-3xs rounded-xs bg-neutral-12 fg-neutral-1 text-sm whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible group-focus-within:opacity-100 group-focus-within:visible transition-opacity">Copy link</span>
</span>""",
        "use": ["A short label for an icon-only button, also given as its <code>aria-label</code>.", "<code>group-focus-within:</code> as well as <code>group-hover:</code>, so keyboard users see it."],
        "avoid": ["Anything people need to read to finish a task; put it on the page."],
    },
    {
        "slug": "combobox", "name": "Combobox", "icon": "ph-magnifying-glass", "group": "Forms",
        "summary": "A text field with suggestions, using the native <code>list</code> attribute and a <code>&lt;datalist&gt;</code>.",
        "html": f"""<div class="flex flex-col gap-2xs max-w-form">
  <label for="doc-country" class="text-sm font-medium">Country</label>
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
        "html": """<div class="rounded-md bg-neutral-1 border border-neutral-6 overflow-x-auto">
  <table class="w-full text-sm">
    <thead class="bg-neutral-2">
      <tr>
        <th aria-sort="ascending" class="text-left px-md py-xs border-b border-neutral-6"><button class="inline-flex items-center gap-2xs border-0 bg-transparent fg-neutral-12 text-base font-medium cursor-pointer">Name<i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph-bold ph-caret-up"></i></button></th>
        <th aria-sort="none" class="text-right px-md py-xs border-b border-neutral-6"><button class="inline-flex items-center gap-2xs border-0 bg-transparent fg-neutral-11 hover:fg-neutral-12 text-base font-medium cursor-pointer transition-colors">Seats<i class="inline-flex items-center justify-center shrink-0 text-base leading-none ph-bold ph-caret-up-down"></i></button></th>
      </tr>
    </thead>
    <tbody>
      <tr class="hover:bg-neutral-3 transition"><td class="px-md py-sm border-b border-neutral-6">Contoso</td><td class="px-md py-sm text-right text-sm font-mono tabular-nums border-b border-neutral-6">48</td></tr>
      <tr class="hover:bg-neutral-3 transition"><td class="px-md py-sm border-b border-neutral-6">Fabrikam</td><td class="px-md py-sm text-right text-sm font-mono tabular-nums border-b border-neutral-6">12</td></tr>
      <tr class="hover:bg-neutral-3 transition"><td class="px-md py-sm">Northwind</td><td class="px-md py-sm text-right text-sm font-mono tabular-nums">7</td></tr>
    </tbody>
  </table>
</div>""",
        "use": ["Show the sort direction with an icon and in <code>aria-sort</code>.", "Sorting itself is a script's job; the classes only show the state."],
        "avoid": ["Sorting columns nobody compares."],
    },
    {
        "slug": "date-range", "name": "Date range", "icon": "ph-calendar-blank", "group": "Forms",
        "summary": "Two native date fields grouped as one, with their own labels.",
        "html": f"""<fieldset class="flex flex-col gap-2xs border-0 p-0 max-w-form">
  <legend class="text-sm font-medium mb-2xs">Stay</legend>
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-sm">
    <div class="flex flex-col gap-2xs"><label for="doc-from" class="text-sm fg-neutral-11">Check in</label><input id="doc-from" type="date" class="{FIELD}" value="2027-03-01"></div>
    <div class="flex flex-col gap-2xs"><label for="doc-to" class="text-sm fg-neutral-11">Check out</label><input id="doc-to" type="date" class="{FIELD}" value="2027-03-05"></div>
  </div>
</fieldset>""",
        "use": ["Native date inputs: they bring the platform's picker and keyboard support."],
        "avoid": ["A single text field for both dates."],
    },
    {
        "slug": "media-card", "name": "Media card", "icon": "ph-image", "group": "Layout",
        "summary": "A card led by a 16:9 media area, then a title, a line of detail and its author.",
        "html": f"""<article class="flex flex-col {CARD} p-0 overflow-hidden max-w-form">
  <div class="aspect-video flex items-center justify-center bg-accent-2-a4 fg-accent-2-11"><i class="inline-flex items-center justify-center shrink-0 text-2xl leading-none ph-light ph-mountains"></i></div>
  <div class="flex flex-col gap-2xs p-md">
    <span class="text-xs font-mono uppercase tracking-widest fg-accent-2-11">Case study</span>
    <h3 class="text-base font-semibold">Rebuilding a design system in a week</h3>
    <div class="flex items-center gap-xs pt-2xs">
      <span class="inline-flex items-center justify-center p-3xs rounded-full bg-accent-3-9 fg-accent-3-contrast text-sm font-medium">GH</span>
      <span class="text-sm fg-neutral-11">Grace Hopper · 6 min read</span>
    </div>
  </div>
</article>""",
        "use": ["<code>aspect-video</code> keeps the media area's shape before the image loads."],
        "avoid": ["Text over the image without a scrim."],
    },
]
