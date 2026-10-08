/* =============================================================================
   chrome.js — shared app-chrome behaviour, loaded on every page after
   functions.js. Owns:
     • navbar height measurement (--app-nav-h)
     • sidebar collapse state persistence (survives navigation)
     • sidebar scroll-position memory (survives navigation)
     • far-left hover-to-reveal sidebar
     • global loading / upload / download affordances (window.appLoader.progress)
     • notification / message / incoming-call sounds (window.appSound)
   All features degrade gracefully when their target elements are absent.
   ========================================================================== */
(function () {
  'use strict';

  var doc = document;
  var body = doc.body;
  var root = doc.documentElement;

  var KEY_COLLAPSE = 'thrivehub.sidebar.collapsed';
  var KEY_SCROLL   = 'thrivehub.sidebar.scroll';

  var ls = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------------------------------------------------------------------------
     1. Keep --app-nav-h in sync with the real navbar height
     ------------------------------------------------------------------------ */
  function syncNavHeight() {
    var header = doc.querySelector('header.navbar-light');
    var h = header ? Math.round(header.getBoundingClientRect().height) : 66;
    if (h > 0) root.style.setProperty('--app-nav-h', h + 'px');
  }

  /* ---------------------------------------------------------------------------
     2. Sidebar collapse state — persisted across pages
     (functions.js toggles body.sidebar-start-enabled on .sidebar-start-toggle;
      we simply observe & remember it, and pre-apply it on load.)
     ------------------------------------------------------------------------ */
  function restoreCollapse() {
    if (ls.get(KEY_COLLAPSE) === '1') body.classList.add('sidebar-start-enabled');
  }
  function watchCollapse() {
    // Save after the theme handler has flipped the class (bubbles to document).
    doc.addEventListener('click', function (e) {
      var t = e.target.closest && e.target.closest('.sidebar-start-toggle');
      if (!t) return;
      requestAnimationFrame(function () {
        ls.set(KEY_COLLAPSE, body.classList.contains('sidebar-start-enabled') ? '1' : '0');
      });
    });
  }

  /* ---------------------------------------------------------------------------
     3. Sidebar scroll-position memory (the rail is constant across pages)
     ------------------------------------------------------------------------ */
  // Layouts mark their rail with .app-sidebar-col; the dashboard layout also
  // carries the older #appSidebarCol id. Match either, so every page with a
  // sidebar collapses — several used to ignore the navbar button entirely.
  function sidebarScroller() {
    return doc.getElementById('appSidebarCol') || doc.querySelector('.app-sidebar-col');
  }

  // A page with no rail must not show a collapse button that does nothing.
  function flagSidebarPresence() {
    body.classList.toggle('no-sidebar', !sidebarScroller());
  }

  function restoreSidebarScroll() {
    var el = sidebarScroller();
    if (!el) return;
    var y = parseInt(ls.get(KEY_SCROLL) || '0', 10);
    if (y > 0) {
      // wait a frame so the sidebar has its final height before we scroll it
      requestAnimationFrame(function () { el.scrollTop = y; });
    }
    var save = debounce(function () { ls.set(KEY_SCROLL, String(el.scrollTop)); }, 150);
    el.addEventListener('scroll', save, { passive: true });
    window.addEventListener('beforeunload', function () { ls.set(KEY_SCROLL, String(el.scrollTop)); });
  }

  /* ---------------------------------------------------------------------------
     4. Far-left hover-to-reveal (active while the sidebar is collapsed)
     ------------------------------------------------------------------------ */
  function setupHoverReveal() {
    if (doc.getElementById('sidebarHoverZone')) return;
    var zone = doc.createElement('div');
    zone.id = 'sidebarHoverZone';
    zone.setAttribute('aria-hidden', 'true');
    body.appendChild(zone);

    var col = sidebarScroller();
    var hideTimer = null;

    function open() {
      if (!body.classList.contains('sidebar-start-enabled')) return;
      clearTimeout(hideTimer);
      body.classList.add('sidebar-hover-open');
    }
    function scheduleClose() {
      clearTimeout(hideTimer);
      hideTimer = setTimeout(function () { body.classList.remove('sidebar-hover-open'); }, 220);
    }

    zone.addEventListener('mouseenter', open);
    zone.addEventListener('mouseleave', scheduleClose);
    if (col) {
      col.addEventListener('mouseenter', open);
      col.addEventListener('mouseleave', scheduleClose);
    }
    // Leaving the collapsed state should always drop the hover overlay.
    doc.addEventListener('click', function (e) {
      if (e.target.closest && e.target.closest('.sidebar-start-toggle')) {
        body.classList.remove('sidebar-hover-open');
      }
    });
  }

  /* ---------------------------------------------------------------------------
     5. Loading / upload / download affordances
     Extends the window.appLoader defined in partials/_loader.html with a
     determinate .progress(pct) for uploads & downloads, plus button helpers.
     ------------------------------------------------------------------------ */
  function setupLoader() {
    var el = doc.getElementById('appLoader');
    var bar = el && el.querySelector('.app-loader-bar');
    var base = window.appLoader || {};

    window.appLoader = Object.assign({}, base, {
      // Determinate progress 0..100 for uploads / downloads.
      progress: function (pct) {
        if (!el || !bar) return;
        pct = Math.max(0, Math.min(100, pct));
        el.classList.remove('done');
        el.classList.add('on');
        bar.classList.add('determinate');
        bar.style.width = pct + '%';
        bar.style.opacity = '1';
        if (pct >= 100) {
          setTimeout(function () {
            el.classList.remove('on');
            el.classList.add('done');
            setTimeout(function () { bar.classList.remove('determinate'); bar.style.width = ''; }, 320);
          }, 200);
        }
      }
    });

    // Buttons opted in with data-loading show a spinner on click/submit.
    doc.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('[data-loading]');
      if (b && !b.classList.contains('is-loading')) b.classList.add('is-loading');
    });
  }

  /* ---------------------------------------------------------------------------
     5b. Global "everything feels async" affordances
     Every real form submit + every internal link shows the loading bar and
     spins its submit button — no per-page wiring. Opt out with data-no-loader
     on the form/link (used by the nav search + any AJAX form that manages its
     own state). AJAX fetch() is already wrapped separately in wrapFetch().
     ------------------------------------------------------------------------ */
  function setupAsync() {
    // Form submits → top bar + submit-button spinner.
    doc.addEventListener('submit', function (e) {
      var form = e.target;
      if (!form || form.tagName !== 'FORM') return;
      if (form.hasAttribute('data-no-loader') || form.getAttribute('role') === 'search') return;
      // Skip forms handled in JS (they preventDefault) — if default is prevented, bail.
      if (e.defaultPrevented) return;   // form handled itself in JS (preventDefault)
      try { if (window.appLoader) window.appLoader.show(false); } catch (err) {}
      var btn = form.querySelector('button[type=submit], input[type=submit], button:not([type])');
      if (btn && !btn.classList.contains('is-loading')) btn.classList.add('is-loading');
    });   // bubble phase: runs after the form's own submit handler, so defaultPrevented is accurate

    // Internal link navigation → show the top bar so it feels instant.
    doc.addEventListener('click', function (e) {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var a = e.target.closest && e.target.closest('a[href]');
      if (!a) return;
      var href = a.getAttribute('href') || '';
      if (a.target && a.target !== '_self') return;
      if (a.hasAttribute('download') || a.hasAttribute('data-no-loader')) return;
      if (a.hasAttribute('data-bs-toggle') || a.getAttribute('role') === 'button') return;
      if (!href || href.charAt(0) === '#' || href.indexOf('javascript:') === 0 ||
          href.indexOf('mailto:') === 0 || href.indexOf('tel:') === 0) return;
      // same-origin only
      if (/^https?:\/\//i.test(href) && href.indexOf(location.origin) !== 0) return;
      try { if (window.appLoader) window.appLoader.show(false); } catch (err) {}
    });
    // A cached back/forward restore should clear any stuck bar.
    window.addEventListener('pageshow', function () { try { window.appLoader && window.appLoader.hide(); } catch (e) {} });
  }

  // Show the top bar around every same-origin fetch() automatically.
  function wrapFetch() {
    if (!window.fetch || window.__appFetchWrapped) return;
    window.__appFetchWrapped = true;
    var orig = window.fetch;
    window.fetch = function () {
      var quiet = arguments[1] && arguments[1].appQuiet;
      try { if (!quiet && window.appLoader) window.appLoader.show(false); } catch (e) {}
      return orig.apply(this, arguments).finally(function () {
        try { if (!quiet && window.appLoader) window.appLoader.hide(); } catch (e) {}
      });
    };
  }

  /* ---------------------------------------------------------------------------
     6. Sounds — new message / notification / incoming call (WebAudio, no asset)
     window.appSound.message() / .notify() / .call() / .stopCall()
     ------------------------------------------------------------------------ */
  function setupSound() {
    var Ctx = window.AudioContext || window.webkitAudioContext;
    var ctx = null, callTimer = null;
    function ac() { if (!ctx && Ctx) ctx = new Ctx(); return ctx; }
    function beep(freq, dur, when, type, gain) {
      var c = ac(); if (!c) return;
      if (c.state === 'suspended') { try { c.resume(); } catch (e) {} }
      var o = c.createOscillator(), g = c.createGain();
      o.type = type || 'sine';
      o.frequency.value = freq;
      var t0 = c.currentTime + (when || 0);
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(gain || 0.12, t0 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + (dur || 0.15));
      o.connect(g); g.connect(c.destination);
      o.start(t0); o.stop(t0 + (dur || 0.15) + 0.02);
    }
    window.appSound = {
      message: function () { beep(660, 0.12, 0, 'sine', 0.10); },
      notify:  function () { beep(880, 0.10, 0, 'triangle', 0.10); beep(1180, 0.12, 0.10, 'triangle', 0.09); },
      call: function () {
        this.stopCall();
        var ring = function () { beep(520, 0.4, 0, 'sine', 0.12); beep(660, 0.4, 0.15, 'sine', 0.12); };
        ring(); callTimer = setInterval(ring, 1600);
      },
      stopCall: function () { if (callTimer) { clearInterval(callTimer); callTimer = null; } }
    };
  }

  /* ---------------------------------------------------------------------------
     7. Global alert / toast stack — auto-dismiss after 3s + a window.appAlert API
     ------------------------------------------------------------------------ */
  var ALERT_TTL = 3000;
  function dismissAlert(el) {
    if (!el || el.classList.contains('hiding')) return;
    el.classList.add('hiding');
    setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 320);
  }
  function wireAlert(el) {
    if (el.__wired) return; el.__wired = true;
    var timer = setTimeout(function () { dismissAlert(el); }, ALERT_TTL);
    var btn = el.querySelector('.btn-close');
    if (btn) btn.addEventListener('click', function () { clearTimeout(timer); dismissAlert(el); });
    // pause the countdown while hovered
    el.addEventListener('mouseenter', function () { clearTimeout(timer); });
    el.addEventListener('mouseleave', function () { timer = setTimeout(function () { dismissAlert(el); }, ALERT_TTL); });
  }
  function setupAlerts() {
    var stack = doc.getElementById('appAlerts');
    if (!stack) return;
    Array.prototype.forEach.call(stack.querySelectorAll('.app-alert'), wireAlert);

    // Push an alert into the same stack from anywhere: appAlert('Saved!', 'success')
    var ICONS = { success: 'check-circle-fill', error: 'exclamation-octagon-fill',
                  danger: 'exclamation-octagon-fill', warning: 'exclamation-triangle-fill',
                  info: 'info-circle-fill' };
    window.appAlert = function (msg, level) {
      level = level || 'info';
      var color = level === 'error' ? 'danger' : level;
      var el = doc.createElement('div');
      el.className = 'app-alert alert alert-' + color + ' d-flex align-items-start';
      el.setAttribute('role', 'alert');
      el.innerHTML = '<i class="bi bi-' + (ICONS[level] || ICONS.info) + ' me-2 mt-1"></i>' +
                     '<div class="flex-grow-1"></div>' +
                     '<button type="button" class="btn-close ms-2" aria-label="Close"></button>';
      el.querySelector('.flex-grow-1').textContent = msg;
      stack.appendChild(el);
      wireAlert(el);
      return el;
    };
  }

  /* --------------------------------- utils --------------------------------- */
  function debounce(fn, ms) {
    var t; return function () { clearTimeout(t); var a = arguments, self = this;
      t = setTimeout(function () { fn.apply(self, a); }, ms); };
  }

  /* ---------------------------------------------------------------------------
     8. Live alert sounds — poll the unread counts and chime when they rise, so a
     new message or notification is heard the moment it lands while the user is on
     the site. Sound plumbing is setupSound()'s window.appSound.
     ------------------------------------------------------------------------ */
  function setupAlertPoll() {
    // Signed-in only: the notification bell (#suNotif) renders just for them.
    var bell = doc.getElementById('suNotif');
    if (!bell || !window.fetch) return;
    var COUNTS_URL = '/communication/alerts/counts/';
    var INTERVAL = 20000;   // 20s — cheap two-count query
    var last = null;        // baseline; no sound until we've seen it once
    var socketLive = false; // when the WebSocket is up, the poller stays silent

    function playFor(kind) {
      if (!window.appSound) return;
      try { kind === 'message' ? window.appSound.message() : window.appSound.notify(); } catch (e) {}
    }
    // Make sure the bell shows its "unread" dot without waiting for a reload.
    function ensureDot() {
      if (!bell.querySelector('.su-dot')) {
        var dot = doc.createElement('span'); dot.className = 'su-dot'; bell.appendChild(dot);
      }
    }

    /* --- Preferred path: a live WebSocket pushes each event instantly. --- */
    function openSocket() {
      if (!window.WebSocket) return;
      var proto = location.protocol === 'https:' ? 'wss' : 'ws';
      var ws;
      try { ws = new WebSocket(proto + '://' + location.host + '/ws/alerts/'); }
      catch (e) { return; }
      ws.onopen = function () { socketLive = true; };
      ws.onmessage = function (ev) {
        var d = {}; try { d = JSON.parse(ev.data); } catch (e) {}
        playFor(d.kind); ensureDot();
      };
      ws.onclose = function () {
        socketLive = false;
        // Reconnect after a short back-off; polling covers the gap meanwhile.
        setTimeout(openSocket, 5000);
      };
      ws.onerror = function () { try { ws.close(); } catch (e) {} };
    }

    /* --- Fallback: poll the counts and chime on a rise (silent if socket up). --- */
    function tick() {
      if (doc.hidden || socketLive) return;
      fetch(COUNTS_URL, { headers: { 'X-Requested-With': 'XMLHttpRequest' }, credentials: 'same-origin' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          if (!d) return;
          if (last) {
            if (d.notifications > last.notifications) { playFor('notification'); ensureDot(); }
            if (d.messages > last.messages) { playFor('message'); ensureDot(); }
          }
          last = d;
        })
        .catch(function () {});
    }

    tick();                       // establish the baseline (silent)
    setInterval(tick, INTERVAL);
    doc.addEventListener('visibilitychange', function () { if (!doc.hidden) tick(); });
    openSocket();
  }

  /* --------------------------------- init ---------------------------------- */
  restoreCollapse();               // pre-apply before the first paint we control
  function init() {
    syncNavHeight();
    flagSidebarPresence();
    watchCollapse();
    restoreSidebarScroll();
    setupHoverReveal();
    setupLoader();
    setupAsync();
    wrapFetch();
    setupSound();
    setupAlerts();
    setupAlertPoll();
    window.addEventListener('resize', debounce(syncNavHeight, 120));
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init);
  else init();
})();
