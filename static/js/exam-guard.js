/* exam-guard.js — the focus guard for a proctored assessment attempt.
 *
 * Config comes from window.EXAM_GUARD (set inline by assessments/take.html):
 *   { enabled, limit, action, blockCopy, requireFullscreen, graceSeconds,
 *     blurContent, warnings, url, submitUrl, csrf }
 *
 * What it watches, and how each signal is treated:
 *
 *   tab hidden / window blurred  → counted immediately. This is the reliable
 *       signal that the student went to another tab, window or program.
 *   pointer leaves the window    → NOT counted on its own. The pointer crosses
 *       the edge constantly (scrollbars, a second monitor, the OS dock), so
 *       counting every crossing would bury real events in noise. Instead it
 *       shows the overlay at once and only counts if the pointer stays outside
 *       for `graceSeconds` — which is exactly the case where the student has
 *       actually gone somewhere else.
 *   fullscreen exit              → counted when fullscreen is required.
 *   copy / paste / right-click / print → blocked and recorded, but these never
 *       remove focus, so they are reported separately.
 *
 * The browser only reports *what happened*. The tally, the limit and the
 * decision to end an attempt all come back from the server, so editing this
 * file cannot lower a student's warning count.
 */
(function () {
  'use strict';
  var CFG = window.EXAM_GUARD;
  if (!CFG || !CFG.enabled) return;

  var form = document.getElementById('take-form');
  var overlay = document.getElementById('guardOverlay');
  var overlayMsg = document.getElementById('guardMsg');
  var counter = document.getElementById('guardCount');
  var content = document.getElementById('guardContent');

  var awaySince = null;       // when the window lost focus
  var pointerTimer = null;    // grace timer for the pointer leaving
  var ended = false;          // the attempt has been terminated
  var lastSentAt = 0;         // client-side throttle on top of server dedupe
  var dialogUntil = 0;        // ignore blur while an OS file dialog is open

  // Upload questions open a native file dialog, which blurs the window through
  // no fault of the student. Clicking a file input opens a short amnesty.
  document.addEventListener('click', function (e) {
    if (e.target && e.target.matches && e.target.matches('input[type=file]')) {
      dialogUntil = Date.now() + 60000;
    }
  }, true);
  function inDialog() { return Date.now() < dialogUntil; }

  /* ---------------- reporting ---------------- */
  function report(kind, secondsAway, note) {
    if (ended) return;
    var now = Date.now();
    // Never flood: at most one report every 700ms. The server dedupes properly.
    if (now - lastSentAt < 700 && kind !== 'fullscreen') return;
    lastSentAt = now;

    var body = new FormData();
    body.append('kind', kind);
    body.append('seconds', Math.round(secondsAway || 0));
    if (note) body.append('detail', note);

    fetch(CFG.url, {
      method: 'POST', credentials: 'same-origin',
      headers: { 'X-CSRFToken': CFG.csrf }, body: body
    }).then(function (r) { return r.json(); })
      .then(handleState)
      .catch(function () { /* offline: the next event re-reports */ });
  }

  function handleState(state) {
    if (!state || !state.ok) return;
    if (typeof state.warnings === 'number') setCount(state.warnings, state.limit);
    if (state.message) showBanner(state.message, state.action);

    if (state.action === 'autosubmit') {
      ended = true;
      lockDown(state.message);
      // Submit what the student has so their work is not simply lost.
      setTimeout(function () { if (form) form.submit(); }, 2500);
    }
  }

  function setCount(warnings, limit) {
    if (!counter) return;
    counter.hidden = false;
    counter.textContent = limit
      ? 'Warnings ' + warnings + '/' + limit
      : 'Warnings ' + warnings;
    counter.className = 'guard-count' + (limit && warnings >= limit ? ' is-over'
      : warnings > 0 ? ' is-warn' : '');
  }

  /* ---------------- overlay + banner ---------------- */
  function showOverlay(text) {
    if (!overlay || ended) return;
    if (overlayMsg && text) overlayMsg.textContent = text;
    overlay.hidden = false;
    if (CFG.blurContent && content) content.classList.add('guard-blurred');
  }
  function hideOverlay() {
    if (!overlay || ended) return;
    overlay.hidden = true;
    if (content) content.classList.remove('guard-blurred');
  }
  function lockDown(text) {
    if (!overlay) return;
    overlay.hidden = false;
    overlay.classList.add('is-final');
    if (overlayMsg) overlayMsg.textContent = text || 'This attempt has ended.';
    if (content) content.classList.add('guard-blurred');
  }

  var bannerTimer = null;
  function showBanner(text, action) {
    var el = document.getElementById('guardBanner');
    if (!el) return;
    el.textContent = text;
    el.hidden = false;
    el.className = 'guard-banner' + (action ? ' is-severe' : '');
    clearTimeout(bannerTimer);
    bannerTimer = setTimeout(function () { el.hidden = true; }, 7000);
  }

  /* ---------------- away / back ---------------- */
  function goneAway(kind, note) {
    if (ended || inDialog()) return;
    if (awaySince === null) awaySince = Date.now();
    showOverlay();
    report(kind, 0, note);
  }

  function cameBack() {
    if (ended) return;
    hideOverlay();
    // Coming back from a file dialog closes the amnesty.
    dialogUntil = 0;
    if (awaySince === null) return;
    var seconds = (Date.now() - awaySince) / 1000;
    awaySince = null;
    // Bank the time away against the attempt (a long absence matters more than
    // a brief one, and the educator sees the total).
    if (seconds >= 1) {
      var body = new FormData();
      body.append('kind', 'blur');
      body.append('seconds', Math.round(seconds));
      body.append('detail', 'returned after ' + Math.round(seconds) + 's');
      fetch(CFG.url, {
        method: 'POST', credentials: 'same-origin',
        headers: { 'X-CSRFToken': CFG.csrf }, body: body
      }).then(function (r) { return r.json(); }).then(handleState).catch(function () {});
    }
  }

  /* ---------------- signals ---------------- */
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) goneAway('hidden');
    else cameBack();
  });

  window.addEventListener('blur', function () { goneAway('blur'); });
  window.addEventListener('focus', cameBack);

  // Pointer leaving the window: show the overlay at once, but only count it if
  // the pointer stays out past the grace period.
  document.addEventListener('mouseout', function (e) {
    if (ended || inDialog()) return;
    if (e.relatedTarget || e.toElement) return;   // still inside the page
    showOverlay('Your pointer has left the assessment window.');
    clearTimeout(pointerTimer);
    pointerTimer = setTimeout(function () {
      if (document.hasFocus && document.hasFocus()) {
        // Focus is still here — count it as a real absence, not a stray flick.
        report('pointer_out', CFG.graceSeconds || 3,
               'pointer outside for ' + (CFG.graceSeconds || 3) + 's');
      }
    }, (CFG.graceSeconds || 3) * 1000);
  });
  document.addEventListener('mouseover', function () {
    clearTimeout(pointerTimer);
    if (awaySince === null) hideOverlay();
  });

  /* ---------------- fullscreen ---------------- */
  if (CFG.requireFullscreen) {
    var askBtn = document.getElementById('guardFullscreen');
    var request = function () {
      var el = document.documentElement;
      var fn = el.requestFullscreen || el.webkitRequestFullscreen || el.msRequestFullscreen;
      if (fn) { try { fn.call(el); } catch (e) { /* needs a user gesture */ } }
    };
    if (askBtn) askBtn.addEventListener('click', function () { request(); askBtn.hidden = true; });
    document.addEventListener('fullscreenchange', function () {
      if (document.fullscreenElement) { hideOverlay(); if (askBtn) askBtn.hidden = true; return; }
      if (ended) return;
      showOverlay('Fullscreen is required for this assessment.');
      if (askBtn) askBtn.hidden = false;
      report('fullscreen', 0);
    });
  }

  /* ---------------- copy / paste / right-click / print ---------------- */
  if (CFG.blockCopy) {
    ['copy', 'cut'].forEach(function (evt) {
      document.addEventListener(evt, function (e) {
        // Let the student copy inside their own answer boxes.
        if (e.target && e.target.closest && e.target.closest('input, textarea')) return;
        e.preventDefault();
        report('copy', 0);
      });
    });
    document.addEventListener('paste', function (e) {
      e.preventDefault();
      report('paste', 0);
    });
    document.addEventListener('contextmenu', function (e) {
      if (e.target && e.target.closest && e.target.closest('input, textarea')) return;
      e.preventDefault();
      report('contextmenu', 0);
    });
    window.addEventListener('beforeprint', function () { report('print', 0); });
    // Ctrl/⌘+P, Ctrl/⌘+S — the usual "get a copy of the paper" shortcuts.
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && ['p', 's'].indexOf((e.key || '').toLowerCase()) !== -1) {
        e.preventDefault();
        report('print', 0);
      }
    });
  }

  /* ---------------- submitting clears the guard ---------------- */
  if (form) form.addEventListener('submit', function () {
    ended = true;
    hideOverlay();
  });

  // Seed the visible tally from the server's count (a resumed attempt keeps it).
  if (CFG.warnings) setCount(CFG.warnings, CFG.limit);
})();
