# HTMX — boosted navigation & the persistent shell

The UCS LMS is a server-rendered Django app. To cut the "reconnect the WebSocket and
re-run all the JS on every page load" churn — and to move toward rich pages whose
sections swap in place — we use **[htmx](https://htmx.org/)** (self-hosted at
`static/vendor/htmx/htmx.min.js`).

This is being rolled out in **phases**. This document tracks what is live.

## Phase 1 — boosted navigation (LIVE)

**What it does:** clicking a **navbar or sidebar** link no longer reloads the whole
document. htmx fetches the next page, pulls out its `#appContentCol`, and swaps it
into the current one. The navbar, the sidebar, and — the point — the **WebSocket
connections in the shell survive**. One `ws/alerts/` socket per session instead of
one per page.

**How it's wired (all in `templates/myhub/elements/layouts/admin.html`):**
- `<body hx-boost="true" hx-target="#appContentCol" hx-select="#appContentCol" hx-swap="innerHTML show:window:top">`
  — boosted links fetch the page and swap only the content region.
- `<div id="appContentCol" hx-boost="false">` — links and forms **inside** the
  content area are **not** boosted, so exams, uploads and lesson pages keep their
  normal full-page behaviour. Only the navbar/sidebar chrome is boosted.
- A small config script adds the CSRF header to every boosted request, shows a top
  progress bar (`#htmxBar`), and re-initialises Bootstrap tooltips after a swap.

**Deliberately excluded from boosting (Phase 1):**
- **Chat** (`/communication/chat/`) — it opens its own `ws/chat/` socket and polling
  timers that would leak if the page were swapped away without cleanup. Handled in
  Phase 2. Marked `hx-boost="false"`.
- **Logout** (POST form) and anything that redirects to an auth page (no
  `#appContentCol` to select). Marked `hx-boost="false"`.
- Everything reached from **inside** the content area (exam/assessment pages, file
  uploads, PayFast, lesson player) — inert because `#appContentCol` is unboosted.

**How to verify:** open the app, watch the server log, and click Dashboard → My
Modules → Notifications → Support in the sidebar. You should see the content swap
(and the top progress bar) **without** a `WebSocket DISCONNECT/CONNECT` for
`/ws/alerts/` on each click — the socket stays connected for the whole session.

**To disable/roll back:** remove the `hx-boost` attributes from `<body>` (and the
htmx `<script>` tags) in `admin.html`. Everything reverts to normal full page loads
— the app is unchanged underneath.

## Phase 2 — lifecycle, chat teardown, safe boost scope (LIVE)

**Page-lifecycle API** (`static/js/htmx-app.js`, loaded in `<head>` after htmx so
`window.Thrive` exists before any content script runs):
- `window.Thrive.onTeardown(fn)` — cleanup that runs once on the next content
  swap (or full unload). Pages with sockets/timers register here so nothing leaks.
- CSRF header on every htmx request; the top progress bar; and idempotent re-init
  of per-element widgets after a swap (tooltips, auto-grow textareas).

**Chat is now boostable.** The chat script moved from `additional_js` into the
content block (so `hx-select="#appContentCol"` includes it), and it registers a
teardown that closes its `ws/chat/` socket (and stops it reconnecting) and clears
its polling intervals when you navigate away. Its `hx-boost="false"` is removed.

**Boost scope made safe.** htmx's `hx-select` only carries `#appContentCol`, so a
page whose init lives in `additional_js` (outside the content region) would lose
its JS when boosted. In Phase 2 the nav links to such pages were left
`hx-boost="false"` and full-loaded — Programme Feed, Calendar, Events, Progress,
Tasks, Shop, AI Assistant — while the boosted set was the script-light pages plus
chat. **Phase 5 migrated all of those into the boosted set** (see below); the only
`hx-boost="false"` links left are the two POST forms (search, logout) and the task
create/edit form (a `.flatpickr` page whose widget is initialised once, globally).

**To bring another page into the boosted set:** move its `additional_js` script
into its `{% block content %}` (making it idempotent / teardown-aware if it opens
sockets or timers), then remove its `hx-boost="false"`.

## Phase 3 — the module hub is one page: tabs swap in place (LIVE)

The module page already used the shared **profile shell** (`profiles/shell.html`)
with a tab strip — Schedule · Messages · Notifications · Documents · Live sessions ·
Mock exams · Blueprints · Assessments — all on one shell. Phase 3 makes that tab
strip **swap only the content** instead of reloading the whole page:

- `profiles/shell.html`: the content is wrapped in `#profContent`, and each tab is
  `hx-get="{{ t.url }}" hx-target="#profContent" hx-select="#profContent"
  hx-swap="outerHTML" hx-push-url="true"`. A full load of the same URL still works
  (progressive enhancement); the back button and deep links work via `hx-push-url`.
- `htmx-app.js`: a delegated handler moves the `active` class to the clicked tab
  (the strip itself isn't swapped).
- `module_feed.html`: the Messages tab's chat script moved from `additional_js`
  into the tab content, so it swaps in with the tab and its `Thrive.onTeardown`
  closes the `ws/chat/` socket when you switch tab.

**Browser-verified** (headless Chrome): clicking Schedule → Documents → Messages →
Schedule swaps the section each time with **no full page reload**; the Messages tab
opens `ws/chat/<group>/` and switching away closes it; `ws/alerts/` stays open the
whole time. This also upgrades every *person/course profile* that uses the shell.

## Phase 4 — tab swaps return only the fragment (LIVE)

Phase 3 swapped the tab content in the browser, but the *server* still rendered the
whole shell (header, tab strip, rail) on every tab click and htmx threw all but
`#profContent` away. Phase 4 stops building what gets discarded: on a tab request
the view renders **only the content fragment**.

- `core/profiles.py` → `shell_base(request)`: returns `profiles/_content_fragment.html`
  when the request is a tab click — `HX-Request: true` **and** `HX-Target: profContent`
  — otherwise `profiles/shell.html`. Guarding on the *target id*, not just
  `HX-Request`, is what keeps a **boosted nav** to a profile page (which targets
  `#appContentCol` and needs the whole shell) rendering the full page.
- `templates/profiles/_content_fragment.html`: a tiny base that emits just
  `<div id="profContent">{% block profile_content %}{% endblock %}</div>` — no
  `<html>`, no chrome. It reproduces the exact element htmx swaps (`outerHTML`).
- The three shell pages now extend `base_template|default:'profiles/shell.html'`
  (`learning/module_feed.html`, `learning/module_profile.html`,
  `accounts/my-profile.html`); their views pass `base_template = shell_base(request)`.
  The `default:` keeps a plain render working even if a view forgets to set it.

**Measured** (admin, module hub Documents tab, live server): a full load is
**74,893 bytes**; the same tab as a fragment is **1,585 bytes** — ~47× smaller,
and the server skips assembling the header/tab-strip/rail entirely. Browser-verified
that tab swaps, URL push, and the Messages `ws/chat/` open/close still work on the
fragment responses; full role crawl still 0-broken.

## Phase 5 — wider boost: the remaining nav pages now boost (LIVE)

The pages Phase 2 left full-loading are now boosted. Two shared helpers in
`htmx-app.js` (defined in `<head>`, so a content script can call them) made it safe
to move each page's init into its `{% block content %}` — where `hx-select`
carries it — without a load-order race or a leak:

- `Thrive.whenReady(cb)` — runs `cb` after the DOM **and** the base scripts
  (jQuery/Bootstrap, which load near the end of `<body>`, *after* `#appContentCol`).
  On a full load a content script runs during parse, before those base scripts, so
  it waits for `DOMContentLoaded`; on a boost the document is already complete, so
  `cb` runs now. This is what lets a jQuery-dependent page (DataTables) init from its
  content block.
- `Thrive.ensureScript(src, cb)` — loads a vendor `<script src>` at most once per
  document, then calls `cb`; if already loaded (boosted back), `cb` fires
  immediately. Replaces putting a `<script src>` in a content block, where an htmx
  swap would load it **asynchronously** and the inline init after it could run
  before the library existed.

**Page CSS moved too.** `{% block additional_css %}` now renders at the top of
`#appContentCol` (not `<head>`), so htmx carries a page's own styles on a boosted
swap — otherwise a boosted-in page would render unstyled. CSS in `<body>` is valid
and cascades after the `<head>` base CSS exactly as before.

**Per-page:**
- Zero-JS pages (Events, Live calendar, Cart, Storefront, My Tasks): just dropped
  `hx-boost="false"`.
- Programme Feed (`pages/feed.html`): the media lightbox moved into content behind a
  `window.__flbInit` guard — it works by document-level delegation, so it must init
  exactly once and a re-run on boost is a no-op.
- AI Assistant (`ai_assistant/chat.html`): its controller moved into content; it is
  page-scoped (all listeners on elements inside the swapped content) and uses
  `fetch`, so it re-binds cleanly on each swap with nothing to tear down.
- Progress (`reports/my-progress.html`, Chart.js), Event management
  (`myhub/event-management.html`, FullCalendar — its dead `DOMContentLoaded` handler
  replaced), Tasks & Products lists (`tasks/all-tasks.html`, `shop/all-products.html`,
  DataTables): init moved into content via `whenReady` + `ensureScript`.

**Browser-verified** (headless Chrome, live server): clicking each of the 11 nav
links swaps its page with **no full reload** (`__fullLoads` stayed 1), each page's
widget initialised (feed lightbox, Chart, DataTables, FullCalendar, assistant), the
`ws/alerts/` socket stayed open across all of them, and **no JS errors** fired. Full
role crawl still 0-broken across admin/educator/student/parent.

Still `hx-boost="false"` on purpose: the search + logout POST forms, and the task
create/edit form (`.flatpickr` init runs once, globally — a boost wouldn't re-run
it, so that page full-loads).

## Phase 6 — socket-native live updates (optional)
Have the alert/chat consumers push **HTML fragments with `hx-swap-oob`** over the
WebSocket, letting htmx place them directly and retiring the bespoke socket→DOM JS.
