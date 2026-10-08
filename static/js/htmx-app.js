/* HTMX app glue (Phase 2)
 * ------------------------------------------------------------------
 * Loaded in <head> (after htmx.min.js) so window.Thrive exists BEFORE any page
 * content script runs — a content script can always register its teardown.
 *
 * - window.Thrive.onTeardown(fn): cleanup that runs once, on the next content
 *   swap (or full unload), then clears. Pages with sockets/timers register here
 *   so nothing leaks when the user navigates away.
 * - CSRF header on every htmx request; a thin top progress bar.
 * - Idempotent re-init of per-element widgets after a swap (Bootstrap 5
 *   dropdowns/collapse use the data-API and need nothing).
 */
(function () {
  // Defined synchronously — content scripts run during parse, before <body>.
  var teardowns = [];
  window.Thrive = window.Thrive || {};
  window.Thrive.onTeardown = function (fn) { if (typeof fn === 'function') teardowns.push(fn); };
  function runTeardowns() {
    var list = teardowns; teardowns = [];
    list.forEach(function (fn) { try { fn(); } catch (e) {} });
  }

  // Run `cb` once the DOM and the base scripts (jQuery/Bootstrap, loaded near the
  // end of <body>) are ready. On a FULL page load a content script runs during
  // parse — before those base scripts — so it must wait for DOMContentLoaded, by
  // which point the synchronous base <script>s have executed. On an HTMX BOOST the
  // document is already complete and jQuery et al. are present, so `cb` runs now.
  // (Phase 5: lets a page's init live in its content block yet still find jQuery,
  // and re-run on every swap-in, without a leak — the full-load path adds a single
  // one-shot listener; the boost path adds none.)
  window.Thrive.whenReady = function (cb) {
    if (typeof cb !== 'function') return;
    if (document.readyState !== 'loading') { try { cb(); } catch (e) {} }
    else document.addEventListener('DOMContentLoaded', function () { try { cb(); } catch (e) {} }, { once: true });
  };

  // Load a script by URL at most once per document, then call `cb`. If it is
  // already loaded (e.g. the page was boosted back to), `cb` runs immediately with
  // no re-fetch and no re-execution. This replaces putting a <script src> in a
  // content block, where an HTMX swap would load it ASYNCHRONOUSLY and the inline
  // init after it could run before the library was defined. (Phase 5.)
  var scriptState = {};  // src -> 'done' | { pending: [cb, ...] }
  window.Thrive.ensureScript = function (src, cb) {
    cb = (typeof cb === 'function') ? cb : function () {};
    var st = scriptState[src];
    if (st === 'done') { try { cb(); } catch (e) {} return; }
    if (st && st.pending) { st.pending.push(cb); return; }
    scriptState[src] = { pending: [cb] };
    var s = document.createElement('script');
    s.src = src;
    s.onload = function () {
      var q = (scriptState[src] || { pending: [] }).pending;
      scriptState[src] = 'done';
      q.forEach(function (f) { try { f(); } catch (e) {} });
    };
    s.onerror = function () { scriptState[src] = null; };  // allow a later retry
    document.head.appendChild(s);
  };

  function ready(fn) {
    if (document.body) fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    if (!window.htmx) return;              // htmx absent → app is a normal MPA
    var doc = document, body = doc.body;

    function cookie(name) {
      var m = doc.cookie.match('(?:^|;\\s*)' + name + '=([^;]*)');
      return m ? decodeURIComponent(m[1]) : '';
    }
    body.addEventListener('htmx:configRequest', function (e) {
      e.detail.headers['X-CSRFToken'] = cookie('csrftoken');
    });

    var bar = doc.createElement('div');
    bar.id = 'htmxBar';
    body.appendChild(bar);
    body.addEventListener('htmx:beforeRequest', function () { bar.className = 'run'; });
    body.addEventListener('htmx:afterRequest', function () {
      bar.className = 'done'; setTimeout(function () { bar.className = ''; }, 260);
    });

    // Tear the outgoing page down before its content is swapped out.
    body.addEventListener('htmx:beforeSwap', runTeardowns);
    window.addEventListener('beforeunload', runTeardowns);

    function initWidgets(root) {
      root = root || doc;
      if (window.bootstrap && bootstrap.Tooltip) {
        root.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
          try { bootstrap.Tooltip.getOrCreateInstance(el); } catch (e) {}
        });
      }
      root.querySelectorAll('textarea[data-autoresize]').forEach(function (el) {
        if (el.dataset.thInit) return;
        el.dataset.thInit = '1';
        var grow = function () { el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 352) + 'px'; };
        el.addEventListener('input', grow); grow();
      });
    }
    body.addEventListener('htmx:load', function (e) { initWidgets(e.target); });

    // Profile/module tab strip (Phase 3): the strip itself isn't swapped, so move
    // the `active` class to the clicked tab when it HTMX-swaps #profContent.
    body.addEventListener('click', function (e) {
      var tab = e.target.closest ? e.target.closest('.js-prof-tab') : null;
      if (!tab) return;
      var strip = tab.closest('.prof-tabs');
      if (strip) strip.querySelectorAll('.js-prof-tab').forEach(function (a) { a.classList.remove('active'); });
      tab.classList.add('active');
    });
  });
})();
