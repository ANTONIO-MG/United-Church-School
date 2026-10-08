/* sortable-lite.js — a tiny, dependency-free drag-to-reorder helper.
 *
 * Pointer-based (works with mouse + touch), reorders direct children of a
 * container by dragging a handle, and calls onEnd(newOrderOfIds) after a drop.
 * Used by the lesson block editor (and reusable anywhere a vendored SortableJS
 * would otherwise be needed).
 *
 *   SortableLite.create(containerEl, {
 *     handle: '.le-grip',        // selector for the drag handle within an item
 *     itemSelector: '.le-block', // selector identifying draggable items
 *     idAttr: 'data-id',         // attribute read to build the order array
 *     draggingClass, targetClass,
 *     onEnd: (ids) => { ... }
 *   });
 */
(function (global) {
  'use strict';

  function create(container, opts) {
    opts = opts || {};
    var handleSel = opts.handle || '.le-grip';
    var itemSel = opts.itemSelector || '.le-block';
    var idAttr = opts.idAttr || 'data-id';
    var draggingClass = opts.draggingClass || 'is-dragging';
    var targetClass = opts.targetClass || 'drop-target';
    var onEnd = opts.onEnd || function () {};

    var dragEl = null, startY = 0, lastTarget = null;

    function itemFrom(node) {
      while (node && node !== container) {
        if (node.matches && node.matches(itemSel)) return node;
        node = node.parentNode;
      }
      return null;
    }

    function onPointerDown(e) {
      var handle = e.target.closest ? e.target.closest(handleSel) : null;
      if (!handle || !container.contains(handle)) return;
      var item = itemFrom(handle);
      if (!item) return;
      e.preventDefault();
      dragEl = item;
      startY = e.clientY;
      item.classList.add(draggingClass);
      document.addEventListener('pointermove', onPointerMove);
      document.addEventListener('pointerup', onPointerUp, { once: true });
    }

    function siblings() {
      return Array.prototype.filter.call(container.children, function (c) {
        return c.matches && c.matches(itemSel);
      });
    }

    function onPointerMove(e) {
      if (!dragEl) return;
      var y = e.clientY;
      var over = null;
      siblings().forEach(function (el) {
        if (el === dragEl) return;
        var r = el.getBoundingClientRect();
        if (y >= r.top && y <= r.bottom) over = el;
      });
      if (lastTarget && lastTarget !== over) lastTarget.classList.remove(targetClass);
      if (over) {
        over.classList.add(targetClass);
        lastTarget = over;
        var r = over.getBoundingClientRect();
        var before = y < r.top + r.height / 2;
        if (before) container.insertBefore(dragEl, over);
        else container.insertBefore(dragEl, over.nextSibling);
      }
    }

    function onPointerUp() {
      document.removeEventListener('pointermove', onPointerMove);
      if (lastTarget) lastTarget.classList.remove(targetClass);
      if (dragEl) dragEl.classList.remove(draggingClass);
      dragEl = null; lastTarget = null;
      var ids = siblings().map(function (el) { return el.getAttribute(idAttr); });
      onEnd(ids);
    }

    container.addEventListener('pointerdown', onPointerDown);
    return {
      destroy: function () { container.removeEventListener('pointerdown', onPointerDown); }
    };
  }

  global.SortableLite = { create: create };
})(window);
