/* Person card pop-up.
 *
 * Clicking a person's name or picture opens a small card about them (picture,
 * name, role, where they study, modules in common) instead of jumping straight
 * to their full profile. Works for:
 *   - anything with data-person-card="<card url>?fragment=1" ({% person_chip %})
 *   - any link to a full profile, /community/profile/<id>/ (the card offers
 *     "Full profile"; Ctrl/Cmd-click or middle-click still opens the page).
 * Without JavaScript every link simply goes where it says.
 */
(function () {
  'use strict';
  var PROFILE = /^\/community\/profile\/(\d+)\/?$/;
  var modal, body, bsModal;

  function ensureModal() {
    if (modal) return;
    modal = document.createElement('div');
    modal.className = 'modal fade pc-modal';
    modal.tabIndex = -1;
    modal.setAttribute('aria-label', 'Person');
    modal.innerHTML = '<div class="modal-dialog modal-dialog-centered modal-sm"><div class="modal-content">' +
      '<button type="button" class="btn-close pc-modal__close" data-bs-dismiss="modal" aria-label="Close"></button>' +
      '<div class="modal-body"></div></div></div>';
    document.body.appendChild(modal);
    body = modal.querySelector('.modal-body');
    bsModal = window.bootstrap ? new window.bootstrap.Modal(modal) : null;
  }

  function open(url, fallback) {
    ensureModal();
    if (!bsModal) { window.location = fallback; return; }
    body.innerHTML = '<div class="pc pc--loading"><div class="spinner-border spinner-border-sm"></div></div>';
    bsModal.show();
    fetch(url, {credentials: 'same-origin', headers: {'X-Requested-With': 'XMLHttpRequest'}})
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
      .then(function (html) { body.innerHTML = html; })
      .catch(function () { bsModal.hide(); window.location = fallback; });
  }

  document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest('a[data-person-card], a[href]');
    if (!a || a.closest('.pc')) return;        // links inside the card behave normally
    var card = a.getAttribute('data-person-card');
    if (!card) {
      var url;
      try { url = new URL(a.href, window.location.href); } catch (err) { return; }
      if (url.origin !== window.location.origin) return;
      var m = PROFILE.exec(url.pathname);
      if (!m || window.location.pathname.indexOf('/community/profile/') === 0) return;
      card = '/community/people/' + m[1] + '/card/?fragment=1';
    }
    e.preventDefault();
    open(card, a.href);
  });
})();
