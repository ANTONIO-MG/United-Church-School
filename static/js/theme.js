/* =============================================================================
   theme.js — the light / dark / auto switch, everywhere.

   The navbar's Mode buttons used to set `data-bs-theme-value` and nothing
   listened, so the toggle did nothing and the saved preference on the settings
   page never reached the browser. This is the missing half:

     • apply   — write `data-bs-theme` on <html> (omitted for "auto", so
                 prefers-color-scheme decides, and re-applied when the OS
                 setting changes while the page is open).
     • persist — POST to /community/preferences/theme/ so the choice follows the
                 user to their next session and their other devices. localStorage
                 is kept in step too, purely so a signed-out page paints right.
     • sync    — the settings page's Theme <select> and the navbar buttons drive
                 each other; changing either one changes the page immediately.

   The FIRST paint is already correct because the layout stamps the attribute
   server-side from the user's row; this script only handles changes made after
   load, and the signed-out case.
   ========================================================================== */
(function () {
  'use strict';
  if (window.__themeInit) return;
  window.__themeInit = true;

  var KEY = 'thrivehub.theme';
  var ENDPOINT = '/community/preferences/theme/';
  var VALID = { light: 1, dark: 1, auto: 1 };
  var root = document.documentElement;
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function stored() {
    try { var v = localStorage.getItem(KEY); return VALID[v] ? v : null; } catch (e) { return null; }
  }

  function current() {
    // The server-rendered attribute is the truth on load; fall back to whatever
    // this browser last chose while signed out.
    var attr = root.getAttribute('data-bs-theme');
    if (VALID[attr]) return attr;
    return stored() || 'auto';
  }

  function apply(mode) {
    if (mode === 'auto') root.removeAttribute('data-bs-theme');
    else root.setAttribute('data-bs-theme', mode);
    root.setAttribute('data-theme-choice', mode);
    reflect(mode);
  }

  function reflect(mode) {
    document.querySelectorAll('[data-bs-theme-value]').forEach(function (btn) {
      var on = btn.getAttribute('data-bs-theme-value') === mode;
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    document.querySelectorAll('select[name="theme"]').forEach(function (sel) {
      if (sel.value !== mode) sel.value = mode;
    });
  }

  function csrf() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
  }

  function persist(mode) {
    try { localStorage.setItem(KEY, mode); } catch (e) { /* private mode */ }
    var token = csrf();
    if (!token) return;                       // signed out: localStorage is enough
    var body = new FormData();
    body.append('theme', mode);
    fetch(ENDPOINT, {
      method: 'POST', body: body, credentials: 'same-origin',
      headers: { 'X-CSRFToken': token }, appQuiet: true
    }).catch(function () { /* the page is already the right colour */ });
  }

  function set(mode) {
    if (!VALID[mode]) mode = 'auto';
    apply(mode);
    persist(mode);
  }
  window.setAppTheme = set;

  // ---- Wire the controls --------------------------------------------------
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-bs-theme-value]');
    if (!btn) return;
    e.preventDefault();
    set(btn.getAttribute('data-bs-theme-value'));
  });

  // The settings page's Theme <select>: change it and the page changes with it,
  // so "save" confirms a choice already visible rather than announcing one.
  document.addEventListener('change', function (e) {
    var sel = e.target;
    if (sel && sel.tagName === 'SELECT' && sel.name === 'theme') set(sel.value);
  });

  // Following the system means following it as it changes, not only at load.
  if (media && media.addEventListener) {
    media.addEventListener('change', function () {
      if (current() === 'auto') apply('auto');
    });
  }

  apply(current());
})();
