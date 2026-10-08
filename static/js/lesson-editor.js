/* lesson-editor.js — the lesson builder.
 *
 * Config comes from window.LESSON_EDITOR (set inline by lesson_editor.html):
 *   { lessonId, csrf, urls:{...}, blocks:[...], sections:[...], references:[...],
 *     styleFields:[...] }
 *
 * The main window is the lesson as **one continuous body**, written like a blog
 * post: elements stack in the order you drop them. A "dropdown section" is just
 * another element in that flow — one that holds its own blocks and collapses for
 * the learner. Anything can go above or below anything else.
 *
 * The side rail is the toolkit: the element palette, plus a Format panel that
 * binds to whichever block is selected and edits its `style` (font, size,
 * weight, colour, alignment, width, spacing, frame). Style keys are whitelisted
 * server-side in apps/learning/styles.py; this file only ever sends keys from
 * that list.
 *
 * Everything autosaves — the Save button only flushes the pending debounce early.
 */
(function () {
  'use strict';
  var CFG = window.LESSON_EDITOR;
  if (!CFG) return;

  var BLOCK_META = {
    heading:   { icon: 'bi-type-h2',            label: 'Heading' },
    text:      { icon: 'bi-text-paragraph',     label: 'Text' },
    image:     { icon: 'bi-image',              label: 'Image' },
    video:     { icon: 'bi-camera-video',       label: 'Video' },
    audio:     { icon: 'bi-music-note-beamed',  label: 'Audio' },
    embed:     { icon: 'bi-window',             label: 'Embed page' },
    file:      { icon: 'bi-paperclip',          label: 'File' },
    reference: { icon: 'bi-quote',              label: 'Reference' },
    quiz:      { icon: 'bi-ui-checks',          label: 'Quiz / test' },
    meeting:   { icon: 'bi-camera-video-fill',  label: 'Live session' },
    callout:   { icon: 'bi-info-circle',        label: 'Callout' },
    table:     { icon: 'bi-table',              label: 'Table' },
    diagram:   { icon: 'bi-diagram-3',          label: 'Diagram' },
    divider:   { icon: 'bi-dash-lg',            label: 'Divider' },
    section:   { icon: 'bi-chevron-bar-expand', label: 'Dropdown section' }
  };

  var blocks = (CFG.blocks || []).slice();
  var sections = (CFG.sections || []).slice();
  var bodyEl = document.getElementById('leBody');
  var saveTimers = {};
  var pendingFlush = [];   // functions the Save button calls to flush early
  var selectedId = null;   // the block the Format panel is bound to

  function sectionById(id) {
    return sections.find(function (s) { return String(s.id) === String(id); });
  }
  function blockById(id) {
    return blocks.find(function (b) { return String(b.id) === String(id); });
  }

  /* ---------------- fetch helper ---------------- */
  function api(url, body, isForm) {
    var opts = { method: 'POST', credentials: 'same-origin', headers: { 'X-CSRFToken': CFG.csrf } };
    if (isForm) { opts.body = body; }
    else { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body || {}); }
    return fetch(url, opts).then(function (r) { return r.json(); });
  }
  function u(name, id) { return CFG.urls[name].replace('0', id); }
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
  function toast(msg, kind) { if (window.appAlert) window.appAlert(msg, kind || 'success'); }

  function setSaveChip(state) {
    var chip = document.getElementById('leSaveChip');
    if (!chip) return;
    chip.className = 'le-savechip ' + state;
    chip.innerHTML = state === 'saving'
      ? '<i class="bi bi-arrow-repeat"></i>Saving…'
      : '<i class="bi bi-check-circle"></i>All changes saved';
  }

  /* ============================================================
   * Rich text — a real formatting toolbar
   * ============================================================ */
  var FONT_SIZES = [['', 'Size'], ['1', 'Tiny'], ['2', 'Small'], ['3', 'Normal'],
                    ['4', 'Medium'], ['5', 'Large'], ['6', 'Huge']];
  var BLOCK_FORMATS = [['p', 'Paragraph'], ['h2', 'Heading 1'], ['h3', 'Heading 2'],
                       ['h4', 'Heading 3'], ['blockquote', 'Quote'], ['pre', 'Code']];

  function richText(html, placeholder, onChange) {
    var wrap = document.createElement('div');
    var bar = document.createElement('div');
    bar.className = 'le-rt-toolbar';

    var ed = document.createElement('div');
    ed.className = 'le-rt';
    ed.contentEditable = 'true';
    ed.setAttribute('data-ph', placeholder || 'Write here…');
    ed.innerHTML = html || '';

    function exec(cmd, value) {
      ed.focus();
      document.execCommand(cmd, false, value === undefined ? null : value);
      onChange(ed.innerHTML);
      syncState();
    }
    function tool(cmd, icon, title, value) {
      var b = document.createElement('button');
      b.type = 'button'; b.title = title; b.innerHTML = '<i class="bi ' + icon + '"></i>';
      b.setAttribute('data-cmd', cmd);
      b.addEventListener('mousedown', function (e) { e.preventDefault(); exec(cmd, value); });
      bar.appendChild(b);
      return b;
    }
    function sep() { var s = document.createElement('span'); s.className = 'le-rt-sep'; bar.appendChild(s); }
    function select(options, title, onPick) {
      var sel = document.createElement('select');
      sel.title = title;
      options.forEach(function (o) {
        var op = document.createElement('option');
        op.value = o[0]; op.textContent = o[1];
        sel.appendChild(op);
      });
      sel.addEventListener('mousedown', function () { savedRange = currentRange(); });
      sel.addEventListener('change', function () {
        restoreRange();
        onPick(sel.value);
        sel.selectedIndex = 0;
      });
      bar.appendChild(sel);
      return sel;
    }

    // Selections are lost when a <select> or colour picker takes focus, so we
    // stash and restore the range around those controls.
    var savedRange = null;
    function currentRange() {
      var sel = window.getSelection();
      return (sel && sel.rangeCount && ed.contains(sel.anchorNode)) ? sel.getRangeAt(0).cloneRange() : null;
    }
    function restoreRange() {
      ed.focus();
      if (!savedRange) return;
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(savedRange);
    }

    select(BLOCK_FORMATS, 'Paragraph style', function (v) { if (v) exec('formatBlock', v); });
    select(FONT_SIZES, 'Font size', function (v) { if (v) exec('fontSize', v); });
    sep();
    tool('bold', 'bi-type-bold', 'Bold (Ctrl+B)');
    tool('italic', 'bi-type-italic', 'Italic (Ctrl+I)');
    tool('underline', 'bi-type-underline', 'Underline (Ctrl+U)');
    tool('strikeThrough', 'bi-type-strikethrough', 'Strikethrough');
    sep();

    // Text colour + highlight.
    var colour = document.createElement('input');
    colour.type = 'color'; colour.title = 'Text colour'; colour.value = '#344767';
    colour.addEventListener('mousedown', function () { savedRange = currentRange(); });
    colour.addEventListener('input', function () { restoreRange(); exec('foreColor', colour.value); });
    bar.appendChild(colour);

    var highlight = document.createElement('input');
    highlight.type = 'color'; highlight.title = 'Highlight'; highlight.value = '#fff3cd';
    highlight.addEventListener('mousedown', function () { savedRange = currentRange(); });
    highlight.addEventListener('input', function () {
      restoreRange();
      // hiliteColor is the standard; backColor is the Edge/IE spelling.
      if (!document.execCommand('hiliteColor', false, highlight.value)) {
        document.execCommand('backColor', false, highlight.value);
      }
      onChange(ed.innerHTML);
    });
    bar.appendChild(highlight);
    sep();

    tool('justifyLeft', 'bi-text-left', 'Align left');
    tool('justifyCenter', 'bi-text-center', 'Centre');
    tool('justifyRight', 'bi-text-right', 'Align right');
    tool('justifyFull', 'bi-justify', 'Justify');
    sep();
    tool('insertUnorderedList', 'bi-list-ul', 'Bulleted list');
    tool('insertOrderedList', 'bi-list-ol', 'Numbered list');
    tool('outdent', 'bi-text-indent-right', 'Outdent');
    tool('indent', 'bi-text-indent-left', 'Indent');
    sep();

    var linkBtn = document.createElement('button');
    linkBtn.type = 'button'; linkBtn.title = 'Insert link'; linkBtn.innerHTML = '<i class="bi bi-link-45deg"></i>';
    linkBtn.addEventListener('mousedown', function (e) {
      e.preventDefault();
      var url = prompt('Link URL', 'https://');
      if (url) exec('createLink', url);
    });
    bar.appendChild(linkBtn);
    tool('unlink', 'bi-link-45deg-slash' /* falls back to a blank glyph if absent */, 'Remove link');
    tool('removeFormat', 'bi-eraser', 'Clear formatting');

    /** Light up the buttons whose command is active at the caret. */
    function syncState() {
      bar.querySelectorAll('button[data-cmd]').forEach(function (b) {
        var cmd = b.getAttribute('data-cmd');
        var on = false;
        try { on = document.queryCommandState(cmd); } catch (e) { on = false; }
        b.classList.toggle('is-on', !!on);
      });
    }

    var t;
    ed.addEventListener('input', function () {
      clearTimeout(t);
      t = setTimeout(function () { onChange(ed.innerHTML); }, 500);
    });
    ed.addEventListener('blur', function () { onChange(ed.innerHTML); });
    ed.addEventListener('keyup', syncState);
    ed.addEventListener('mouseup', syncState);
    // Paste as plain text so pasted Word/web markup cannot break the layout.
    ed.addEventListener('paste', function (e) {
      var text = (e.clipboardData || window.clipboardData).getData('text/plain');
      if (text === undefined) return;
      e.preventDefault();
      document.execCommand('insertText', false, text);
    });

    wrap.appendChild(bar);
    wrap.appendChild(ed);
    return wrap;
  }

  /* ---------------- media upload ---------------- */
  function uploadWidget(block, accept, onDone) {
    var wrap = document.createElement('div');
    var dz = document.createElement('label'); dz.className = 'le-dropzone';
    dz.innerHTML = '<i class="bi bi-cloud-arrow-up fs-4 d-block mb-1"></i>Click or drop a file to upload' +
      (block.data.filename ? '<div class="small text-muted mt-1">Current: ' + esc(block.data.filename) + '</div>' : '');
    var input = document.createElement('input'); input.type = 'file'; input.accept = accept || '*/*'; input.hidden = true;
    var bar = document.createElement('div'); bar.className = 'le-uploadbar'; bar.innerHTML = '<i></i>';
    dz.appendChild(input);
    function doUpload(file) {
      if (!file) return;
      var fd = new FormData(); fd.append('file', file);
      bar.style.display = 'block';
      var xhr = new XMLHttpRequest();
      xhr.open('POST', u('upload', block.id));
      xhr.setRequestHeader('X-CSRFToken', CFG.csrf);
      xhr.upload.onprogress = function (e) { if (e.lengthComputable) bar.firstChild.style.width = (e.loaded / e.total * 100) + '%'; };
      xhr.onload = function () {
        bar.style.display = 'none'; bar.firstChild.style.width = '0';
        try { var res = JSON.parse(xhr.responseText); if (res.ok) { onDone(res.block); toast('Uploaded'); } }
        catch (e) { toast('Upload failed', 'error'); }
      };
      xhr.onerror = function () { bar.style.display = 'none'; toast('Upload failed', 'error'); };
      xhr.send(fd);
    }
    input.addEventListener('change', function () { doUpload(input.files[0]); });
    dz.addEventListener('dragover', function (e) { e.preventDefault(); e.stopPropagation(); dz.classList.add('hover'); });
    dz.addEventListener('dragleave', function () { dz.classList.remove('hover'); });
    dz.addEventListener('drop', function (e) {
      e.preventDefault(); e.stopPropagation(); dz.classList.remove('hover');
      doUpload(e.dataTransfer.files[0]);
    });
    wrap.appendChild(dz); wrap.appendChild(bar);
    return wrap;
  }

  function field(label, el) {
    var w = document.createElement('div'); w.className = 'mb-2';
    if (label) { var l = document.createElement('label'); l.className = 'form-label small text-muted mb-1'; l.textContent = label; w.appendChild(l); }
    w.appendChild(el); return w;
  }
  function input(val, ph, oninput) {
    var i = document.createElement('input'); i.className = 'form-control form-control-sm'; i.value = val || ''; i.placeholder = ph || '';
    i.addEventListener('input', function () { oninput(i.value); });
    return i;
  }
  function smallBtn(html, cls) {
    var b = document.createElement('button'); b.type = 'button';
    b.className = 'btn btn-sm ' + (cls || 'btn-outline-secondary'); b.innerHTML = html;
    return b;
  }
  function selectEl(options, current, onChange, cls) {
    var sel = document.createElement('select');
    sel.className = cls || 'form-select form-select-sm';
    options.forEach(function (o) {
      var op = document.createElement('option');
      op.value = o[0]; op.textContent = o[1];
      if (String(current) === String(o[0])) op.selected = true;
      sel.appendChild(op);
    });
    sel.addEventListener('change', function () { onChange(sel.value); });
    return sel;
  }

  /* ---------------- table editor ---------------- */
  function buildTableEditor(block, body, save) {
    var d = block.data || (block.data = {});
    if (!Array.isArray(d.headers)) d.headers = ['Column 1', 'Column 2'];
    if (!Array.isArray(d.rows)) d.rows = [['', ''], ['', '']];
    if (typeof d.has_header !== 'boolean') d.has_header = true;

    function cols() { return d.headers.length; }
    function normalise() {
      var n = cols();
      d.rows = d.rows.map(function (r) {
        r = (r || []).slice(0, n);
        while (r.length < n) r.push('');
        return r;
      });
    }

    var hdr = document.createElement('div'); hdr.className = 'form-check mb-2';
    hdr.innerHTML = '<input class="form-check-input" type="checkbox" id="tbh' + block.id + '"' + (d.has_header ? ' checked' : '') +
      '><label class="form-check-label small" for="tbh' + block.id + '">First row is a header</label>';
    hdr.querySelector('input').addEventListener('change', function (e) { d.has_header = e.target.checked; save(); draw(); });
    body.appendChild(hdr);

    var gridWrap = document.createElement('div'); gridWrap.className = 'le-table-wrap table-responsive';
    body.appendChild(gridWrap);

    var actions = document.createElement('div'); actions.className = 'd-flex gap-2 mt-2';
    var addRow = smallBtn('<i class="bi bi-plus-lg me-1"></i>Row');
    var addCol = smallBtn('<i class="bi bi-plus-lg me-1"></i>Column');
    addRow.addEventListener('click', function () { d.rows.push(new Array(cols()).fill('')); save(); draw(); });
    addCol.addEventListener('click', function () { d.headers.push('Column ' + (cols() + 1)); d.rows.forEach(function (r) { r.push(''); }); save(); draw(); });
    actions.appendChild(addRow); actions.appendChild(addCol);
    body.appendChild(actions);
    body.appendChild(field('Caption', input(d.caption, 'Optional table caption', function (v) { d.caption = v; save(); })));

    function cellInput(val, oninput) {
      var i = document.createElement('input'); i.className = 'form-control form-control-sm'; i.value = val || '';
      i.addEventListener('input', function () { oninput(i.value); save(); });
      return i;
    }
    function draw() {
      normalise();
      var tbl = document.createElement('table'); tbl.className = 'table table-bordered align-middle le-table-edit mb-0';
      var thead = document.createElement('thead'); var htr = document.createElement('tr');
      d.headers.forEach(function (h, c) {
        var th = document.createElement('th');
        var wrap = document.createElement('div'); wrap.className = 'd-flex align-items-center gap-1';
        wrap.appendChild(cellInput(h, function (v) { d.headers[c] = v; }));
        var del = smallBtn('<i class="bi bi-x"></i>', 'btn-outline-danger border-0 px-1'); del.title = 'Delete column';
        del.addEventListener('click', function () {
          if (cols() <= 1) return;
          d.headers.splice(c, 1); d.rows.forEach(function (r) { r.splice(c, 1); }); save(); draw();
        });
        wrap.appendChild(del); th.appendChild(wrap); htr.appendChild(th);
      });
      htr.appendChild(document.createElement('th'));
      thead.appendChild(htr); tbl.appendChild(thead);
      var tb = document.createElement('tbody');
      d.rows.forEach(function (row, r) {
        var tr = document.createElement('tr');
        row.forEach(function (cell, c) {
          var td = document.createElement('td');
          td.appendChild(cellInput(cell, function (v) { d.rows[r][c] = v; }));
          tr.appendChild(td);
        });
        var tdd = document.createElement('td'); tdd.className = 'text-center';
        var del = smallBtn('<i class="bi bi-trash"></i>', 'btn-outline-danger border-0 px-1'); del.title = 'Delete row';
        del.addEventListener('click', function () { if (d.rows.length <= 1) return; d.rows.splice(r, 1); save(); draw(); });
        tdd.appendChild(del); tr.appendChild(tdd); tb.appendChild(tr);
      });
      tbl.appendChild(tb);
      gridWrap.innerHTML = ''; gridWrap.appendChild(tbl);
    }
    draw();
  }

  /* ---------------- diagram editor (labelled image) ---------------- */
  function buildDiagramEditor(block, body, save, rerender) {
    var d = block.data || (block.data = {});
    if (!Array.isArray(d.labels)) d.labels = [];

    body.appendChild(uploadWidget(block, 'image/*', function (nb) {
      block.media_url = nb.media_url; block.data = nb.data;
      if (!Array.isArray(block.data.labels)) block.data.labels = [];
      rerender();
    }));
    body.appendChild(field('…or image URL', input(d.url, 'https://…', function (v) { d.url = v; save(); rerender(); })));
    body.appendChild(field('Alt text', input(d.alt, 'Describe the diagram', function (v) { d.alt = v; save(); })));
    body.appendChild(field('Caption', input(d.caption, 'Optional caption', function (v) { d.caption = v; save(); })));

    var src = block.media_url || d.url;
    var listBox = document.createElement('div'); listBox.className = 'le-diagram-labels mt-2';
    var drawMarkers = function () {};

    if (src) {
      var hint = document.createElement('div'); hint.className = 'small text-muted mb-1';
      hint.innerHTML = '<i class="bi bi-hand-index me-1"></i>Click on the image to drop a numbered label.';
      body.appendChild(hint);
      var stage = document.createElement('div'); stage.className = 'le-diagram-stage';
      var img = document.createElement('img'); img.src = src; img.alt = d.alt || ''; stage.appendChild(img);
      stage.addEventListener('click', function (e) {
        if (e.target !== img) return;
        var rect = img.getBoundingClientRect();
        var x = Math.round((e.clientX - rect.left) / rect.width * 1000) / 10;
        var y = Math.round((e.clientY - rect.top) / rect.height * 1000) / 10;
        d.labels.push({ n: d.labels.length + 1, x: x, y: y, text: '' });
        save(); drawMarkers(); drawList();
      });
      body.appendChild(stage);

      drawMarkers = function () {
        stage.querySelectorAll('.le-diagram-marker').forEach(function (m) { m.remove(); });
        d.labels.forEach(function (lb, i) {
          var m = document.createElement('span'); m.className = 'le-diagram-marker';
          m.style.left = lb.x + '%'; m.style.top = lb.y + '%'; m.textContent = (i + 1);
          stage.appendChild(m);
        });
      };
      drawMarkers();
    }

    body.appendChild(listBox);
    function drawList() {
      listBox.innerHTML = '';
      d.labels.forEach(function (lb, i) {
        lb.n = i + 1;
        var row = document.createElement('div'); row.className = 'le-refrow';
        var badge = document.createElement('span'); badge.className = 'le-diagram-badge'; badge.textContent = (i + 1);
        var ti = input(lb.text, 'Label text', function (v) { lb.text = v; save(); });
        var del = smallBtn('<i class="bi bi-x-lg"></i>', 'btn-outline-danger border-0');
        del.addEventListener('click', function () { d.labels.splice(i, 1); save(); drawList(); drawMarkers(); });
        row.appendChild(badge); row.appendChild(ti); row.appendChild(del); listBox.appendChild(row);
      });
    }
    drawList();
  }

  /* ---------------- per-type block body ---------------- */
  function bodyFor(block, rerender) {
    var t = block.block_type, d = block.data || {};
    var body = document.createElement('div');
    var save = function () { scheduleSave(block); };

    if (t === 'heading') {
      body.appendChild(selectEl([['2', 'Large (H2)'], ['3', 'Medium (H3)'], ['4', 'Small (H4)']],
        d.level, function (v) { d.level = parseInt(v, 10); save(); }, 'form-select form-select-sm mb-2'));
      body.appendChild(input(d.text, 'Heading text', function (v) { d.text = v; save(); }));

    } else if (t === 'text') {
      body.appendChild(richText(d.html, 'Write the lesson text… select text to format', function (h) { d.html = h; save(); }));

    } else if (t === 'callout') {
      body.appendChild(selectEl([['info', 'Info'], ['tip', 'Tip'], ['warning', 'Warning'], ['danger', 'Important']],
        d.variant || 'info', function (v) { d.variant = v; save(); }, 'form-select form-select-sm mb-2'));
      body.appendChild(richText(d.html, 'Callout text…', function (h) { d.html = h; save(); }));

    } else if (t === 'image') {
      body.appendChild(uploadWidget(block, 'image/*', function (nb) { block.media_url = nb.media_url; block.data = nb.data; rerender(); }));
      body.appendChild(field('…or image URL', input(d.url, 'https://…', function (v) { d.url = v; save(); })));
      body.appendChild(field('Alt text', input(d.alt, 'Describe the image', function (v) { d.alt = v; save(); })));
      body.appendChild(field('Caption', input(d.caption, 'Optional caption', function (v) { d.caption = v; save(); })));
      var src = block.media_url || d.url;
      if (src) { var pv = document.createElement('div'); pv.className = 'le-media-preview'; pv.innerHTML = '<img src="' + esc(src) + '" alt="">'; body.appendChild(pv); }

    } else if (t === 'video') {
      body.appendChild(field('Source', selectEl(
        [['file', 'Uploaded file'], ['youtube', 'YouTube'], ['vimeo', 'Vimeo'], ['url', 'Direct URL']],
        d.provider || 'file', function (v) { d.provider = v; save(); rerender(); })));
      if ((d.provider || 'file') === 'file') {
        body.appendChild(uploadWidget(block, 'video/*', function (nb) { block.media_url = nb.media_url; block.data = nb.data; rerender(); }));
      } else {
        body.appendChild(field('Video URL',
          input(d.url, 'Paste a YouTube, Vimeo or direct video link', function (v) { d.url = v; save(); })));
        var note = document.createElement('div'); note.className = 'small text-muted mb-2';
        note.innerHTML = '<i class="bi bi-info-circle me-1"></i>YouTube and Vimeo links play in the same in-lesson player as uploaded video.';
        body.appendChild(note);
      }
      var dur = input(d.seconds ? Math.round(d.seconds / 60) : '', 'e.g. 12', function (v) {
        d.seconds = (parseInt(v, 10) || 0) * 60; save();
      });
      dur.type = 'number'; dur.min = '0';
      body.appendChild(field('Length in minutes (shown on the section)', dur));
      body.appendChild(field('Caption', input(d.caption, 'Optional caption', function (v) { d.caption = v; save(); })));

    } else if (t === 'audio') {
      body.appendChild(uploadWidget(block, 'audio/*', function (nb) { block.media_url = nb.media_url; block.data = nb.data; rerender(); }));
      body.appendChild(field('…or audio URL', input(d.url, 'https://…', function (v) { d.url = v; save(); })));
      body.appendChild(field('Caption', input(d.caption, 'Optional caption', function (v) { d.caption = v; save(); })));

    } else if (t === 'file') {
      body.appendChild(uploadWidget(block, '*/*', function (nb) { block.media_url = nb.media_url; block.data = nb.data; rerender(); }));
      body.appendChild(field('Title', input(d.title, 'File title', function (v) { d.title = v; save(); })));
      body.appendChild(field('Description', input(d.description, 'Optional', function (v) { d.description = v; save(); })));

    } else if (t === 'embed') {
      body.appendChild(field('Page / video URL', input(d.url, 'https://… (a web page, article or video to embed)', function (v) { d.url = v; save(); })));
      body.appendChild(field('Title', input(d.title, 'What is this?', function (v) { d.title = v; save(); })));
      var h = input(d.height || 480, 'Height in px', function (v) { d.height = parseInt(v, 10) || 480; save(); }); h.type = 'number';
      body.appendChild(field('Height (px)', h));
      var tk = document.createElement('div'); tk.className = 'form-check';
      tk.innerHTML = '<input class="form-check-input" type="checkbox" id="trk' + block.id + '"' + (block.track ? ' checked' : '') +
        '><label class="form-check-label small" for="trk' + block.id + '">Track how long learners view this (xAPI)</label>';
      tk.querySelector('input').addEventListener('change', function (e) { block.track = e.target.checked; save(); });
      body.appendChild(tk);

    } else if (t === 'reference') {
      body.appendChild(field('Citation', input(d.text, 'Title of the work', function (v) { d.text = v; save(); })));
      body.appendChild(field('Authors', input(d.authors, 'e.g. Smith, J.', function (v) { d.authors = v; save(); })));
      body.appendChild(field('Year', input(d.year, 'e.g. 2024', function (v) { d.year = v; save(); })));
      body.appendChild(field('URL / DOI', input(d.url, 'https://…', function (v) { d.url = v; save(); })));

    } else if (t === 'quiz') {
      var qc = document.createElement('div'); qc.className = 'le-quizcard';
      qc.innerHTML = '<i class="bi bi-ui-checks ic"></i><div class="flex-grow-1"><strong>' + esc(d.title || 'Quiz') +
        '</strong><div class="small text-muted">Marks and the time limit come from the assessment itself</div></div>';
      if (block.assessment_id) {
        var open = document.createElement('a'); open.className = 'btn btn-sm btn-primary';
        open.href = CFG.urls.builder.replace('0', block.assessment_id); open.target = '_blank';
        open.innerHTML = '<i class="bi bi-pencil-square me-1"></i>Edit questions';
        qc.appendChild(open);
      }
      body.appendChild(qc);

    } else if (t === 'meeting') {
      var mc = document.createElement('div'); mc.className = 'le-meetcard';
      mc.innerHTML = '<i class="bi bi-camera-video-fill ic"></i><div class="flex-grow-1"><strong>' + esc(d.title || 'Live session') +
        '</strong><div class="small text-muted">' + esc(d.provider === 'teams' ? 'Microsoft Teams' : 'In-app video room') + '</div></div>';
      if (block.join_url || d.join_url) {
        var j = document.createElement('a'); j.className = 'btn btn-sm btn-outline-success';
        j.href = block.join_url || d.join_url; j.target = '_blank';
        j.innerHTML = '<i class="bi bi-box-arrow-up-right me-1"></i>Open room';
        mc.appendChild(j);
      }
      body.appendChild(mc);

    } else if (t === 'table') {
      buildTableEditor(block, body, save);

    } else if (t === 'diagram') {
      buildDiagramEditor(block, body, save, rerender);

    } else if (t === 'divider') {
      body.innerHTML = '<hr class="my-1"><div class="small text-muted text-center">Divider</div>';
    }
    return body;
  }

  /* ============================================================
   * Block cards
   * ============================================================ */
  function renderBlock(block) {
    if (block.block_type === 'section') return renderSectionBlock(block);

    var meta = BLOCK_META[block.block_type] || { icon: 'bi-square', label: block.block_type };
    var el = document.createElement('div');
    el.className = 'le-block';
    el.setAttribute('data-id', block.id);
    el.setAttribute('draggable', 'true');

    var head = document.createElement('div'); head.className = 'le-bhead';
    head.innerHTML = '<span class="le-grip" title="Drag to move"><i class="bi bi-grip-vertical"></i></span>' +
      '<span class="le-btype"><i class="bi ' + meta.icon + '"></i>' + meta.label + '</span>' +
      '<span class="le-bactions">' +
        '<button class="le-fmt" title="Format this element"><i class="bi bi-sliders"></i></button>' +
        '<button class="le-del" title="Delete block"><i class="bi bi-trash"></i></button></span>';
    head.querySelector('.le-del').addEventListener('click', function (e) {
      e.stopPropagation();
      if (!confirm('Delete this block?')) return;
      api(u('blockDelete', block.id), {}).then(function () {
        blocks = blocks.filter(function (b) { return b.id !== block.id; });
        if (selectedId === block.id) selectBlock(null);
        el.remove();
        renumber();
        refreshEstimates();
      });
    });
    head.querySelector('.le-fmt').addEventListener('click', function (e) {
      e.stopPropagation();
      selectBlock(block.id);
    });
    el.appendChild(head);

    var bodyWrap = document.createElement('div'); bodyWrap.className = 'le-bbody';
    // Live preview: the author sees their formatting on the block as they set it.
    bodyWrap.setAttribute('style', block.css || '');
    bodyWrap.appendChild(bodyFor(block, function () {
      var fresh = renderBlock(block);
      el.replaceWith(fresh);
      wireBlockDrag(fresh, block);
      if (selectedId === block.id) markSelected();
    }));
    el.appendChild(bodyWrap);

    // Clicking anywhere in the card selects it for the Format panel, but must
    // not steal focus from the rich-text area the author is typing in.
    el.addEventListener('mousedown', function () { selectBlock(block.id, true); });

    wireBlockDrag(el, block);
    if (selectedId === block.id) el.classList.add('is-selected');
    return el;
  }

  /* ============================================================
   * Drag and drop — palette → section, and block → section
   * ============================================================ */
  var dragging = null;   // { kind:'palette', type } | { kind:'block', id, el }

  function wireBlockDrag(el, block) {
    el.addEventListener('dragstart', function (e) {
      // Only start from the grip, so selecting text inside a block still works.
      if (!el._gripDown) { e.preventDefault(); return; }
      dragging = { kind: 'block', id: block.id, el: el };
      el.classList.add('is-dragging');
      e.dataTransfer.effectAllowed = 'move';
      try { e.dataTransfer.setData('text/plain', 'block:' + block.id); } catch (err) { /* Safari */ }
    });
    el.addEventListener('dragend', function () {
      el.classList.remove('is-dragging');
      el._gripDown = false;
      dragging = null;
      clearDropHints();
    });
    var grip = el.querySelector('.le-grip');
    if (grip) {
      grip.addEventListener('mousedown', function () { el._gripDown = true; });
      grip.addEventListener('touchstart', function () { el._gripDown = true; }, { passive: true });
    }
    el.addEventListener('mouseup', function () { el._gripDown = false; });
  }

  function clearDropHints() {
    document.querySelectorAll('.le-drop.le-dragover').forEach(function (z) { z.classList.remove('le-dragover'); });
  }

  /** A section can't go inside a section — the flow (and its gating) would be
   *  ambiguous. Everything else may be dropped anywhere. */
  function zoneAccepts(zone, drag) {
    var intoSection = !!zone.getAttribute('data-section');
    if (!intoSection) return true;
    if (drag.kind === 'palette') return drag.type !== 'section';
    var block = blockById(drag.id);
    return !block || block.block_type !== 'section';
  }

  function wireDropZone(zone) {
    zone.addEventListener('dragover', function (e) {
      if (!dragging || !zoneAccepts(zone, dragging)) return;
      e.preventDefault();
      e.stopPropagation();
      e.dataTransfer.dropEffect = dragging.kind === 'palette' ? 'copy' : 'move';
      zone.classList.add('le-dragover');
      // Position the placeholder relative to the card under the pointer.
      if (dragging.kind === 'block') {
        var after = cardAfter(zone, e.clientY);
        if (after === null) zone.appendChild(dragging.el);
        else zone.insertBefore(dragging.el, after);
      }
    });
    zone.addEventListener('dragleave', function (e) {
      if (e.target === zone) zone.classList.remove('le-dragover');
    });
    zone.addEventListener('drop', function (e) {
      if (!dragging || !zoneAccepts(zone, dragging)) return;
      e.preventDefault();
      e.stopPropagation();
      zone.classList.remove('le-dragover');
      var sectionId = zone.getAttribute('data-section') || '';
      if (dragging.kind === 'palette') {
        addBlock(dragging.type, sectionId, zone);
      } else {
        commitMove(dragging.id, sectionId, zone);
      }
      dragging = null;
    });
  }

  /** The card whose midpoint is below ``y`` — where a dragged block should land. */
  function cardAfter(zone, y) {
    var cards = Array.prototype.slice.call(zone.querySelectorAll(':scope > .le-block:not(.is-dragging)'));
    for (var i = 0; i < cards.length; i++) {
      var r = cards[i].getBoundingClientRect();
      if (y < r.top + r.height / 2) return cards[i];
    }
    return null;
  }

  function commitMove(blockId, sectionId, zone) {
    var block = blocks.find(function (b) { return String(b.id) === String(blockId); });
    if (block) block.section_id = sectionId ? parseInt(sectionId, 10) : null;
    var order = Array.prototype.map.call(zone.querySelectorAll(':scope > .le-block'),
      function (el) { return el.getAttribute('data-id'); });
    setSaveChip('saving');
    api(u('blockMove', blockId), { section_id: sectionId || null, order: order })
      .then(function () { setSaveChip('saved'); refreshEstimates(); });
  }

  function initPaletteDrag() {
    document.querySelectorAll('#lePalette [data-add]').forEach(function (btn) {
      btn.addEventListener('dragstart', function (e) {
        dragging = { kind: 'palette', type: btn.getAttribute('data-add') };
        btn.classList.add('is-dragging');
        e.dataTransfer.effectAllowed = 'copy';
        try { e.dataTransfer.setData('text/plain', 'palette:' + dragging.type); } catch (err) { /* Safari */ }
      });
      btn.addEventListener('dragend', function () {
        btn.classList.remove('is-dragging');
        dragging = null;
        clearDropHints();
      });
      // Clicking adds it where the author is working: inside the selected
      // section if one is selected, otherwise at the end of the body.
      btn.addEventListener('click', function () {
        var target = insertionTarget();
        addBlock(btn.getAttribute('data-add'), target.sectionId, target.zone);
      });
    });
  }

  /** Where a clicked palette element should land. */
  function insertionTarget() {
    var selected = selectedId ? blockById(selectedId) : null;
    if (selected && selected.block_type === 'section') {
      var id = String(selected.holds_section_id);
      return { sectionId: id, zone: zoneFor(id) };
    }
    if (selected && selected.section_id) {
      var sid = String(selected.section_id);
      return { sectionId: sid, zone: zoneFor(sid) };
    }
    return { sectionId: '', zone: bodyEl };
  }

  function zoneFor(sectionId) {
    if (!sectionId) return bodyEl;
    return document.querySelector('.le-drop[data-section="' + sectionId + '"]') || bodyEl;
  }

  /* ============================================================
   * Adding content
   * ============================================================ */
  function addBlock(type, sectionId, zone) {
    if (type === 'quiz') return attachQuiz(sectionId, zone);
    if (type === 'meeting') return attachMeeting(sectionId, zone);
    // Sections never nest — one always joins the body, wherever it was dropped.
    if (type === 'section') { sectionId = ''; zone = bodyEl; }

    setSaveChip('saving');
    api(u('blockAdd', CFG.lessonId), { block_type: type, section_id: sectionId || null }).then(function (res) {
      if (!res.ok) { toast('Could not add that block', 'error'); return; }
      setSaveChip('saved');
      if (res.section) sections.push(res.section);
      var el = placeNewBlock(res.block, zone);
      if (type === 'section') {
        var titleInput = el.querySelector('.le-sectitle');
        if (titleInput) { titleInput.focus(); titleInput.select(); }
      }
    });
  }

  function placeNewBlock(block, zone) {
    blocks.push(block);
    var el = renderBlock(block);
    (zone || bodyEl).appendChild(el);
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    selectBlock(block.id);
    renumber();
    refreshEstimates();
    return el;
  }

  function attachQuiz(sectionId, zone) {
    var pick = document.getElementById('leQuizPick');
    var existing = pick ? pick.value : '';
    var payload = existing ? { assessment_id: existing } : { kind: 'quiz' };
    payload.section_id = sectionId || null;
    api(u('attachQuiz', CFG.lessonId), payload).then(function (res) {
      if (!res.ok) { toast('Could not attach quiz', 'error'); return; }
      placeNewBlock(res.block, zone);
      if (res.builder_url) {
        toast('Quiz created — opening the question builder');
        window.open(res.builder_url, '_blank');
      }
    });
  }

  function attachMeeting(sectionId, zone) {
    var title = prompt('Name this live session', 'Live session');
    if (title === null) return;
    api(u('attachMeeting', CFG.lessonId), { title: title, section_id: sectionId || null }).then(function (res) {
      if (!res.ok) { toast('Could not create session', 'error'); return; }
      placeNewBlock(res.block, zone);
      toast('Live session added');
    });
  }

  /* ============================================================
   * Dropdown sections — an element in the body that holds other elements
   * ============================================================ */
  function renderSectionBlock(block) {
    var section = sectionById(block.holds_section_id);
    if (!section) {                       // shouldn't happen; degrade gracefully
      var stub = document.createElement('div');
      stub.className = 'le-block'; stub.setAttribute('data-id', block.id);
      stub.textContent = 'Section (unavailable)';
      return stub;
    }

    var el = document.createElement('div');
    el.className = 'le-block le-sec';
    el.setAttribute('data-id', block.id);
    el.setAttribute('data-section-id', section.id);
    el.setAttribute('draggable', 'true');

    /* --- header --- */
    var head = document.createElement('div'); head.className = 'le-sechead';
    var grip = document.createElement('span');
    grip.className = 'le-grip'; grip.title = 'Drag to move this section';
    grip.innerHTML = '<i class="bi bi-grip-vertical"></i>';
    head.appendChild(grip);

    var num = document.createElement('span'); num.className = 'le-secnum';
    num.innerHTML = '<i class="bi bi-chevron-bar-expand"></i>';
    num.title = 'Dropdown section';
    head.appendChild(num);

    var title = document.createElement('input');
    title.className = 'le-sectitle'; title.value = section.title || '';
    title.placeholder = 'Section title the learner sees';
    title.addEventListener('input', function () {
      section.title = title.value;
      // The anchor block caches the title too. Keep both in step, or a later
      // block save would push the stale copy back over the section.
      block.data = block.data || {};
      block.data.title = title.value;
      scheduleSectionSave(section);
    });
    head.appendChild(title);

    head.appendChild(selectEl(CFG.sectionTypes || [], section.section_type, function (v) {
      section.section_type = v;
      scheduleSectionSave(section, function (fresh) { estimate.textContent = estimateText(fresh); });
    }, 'form-select form-select-sm le-sectype'));

    var dur = document.createElement('input');
    dur.type = 'number'; dur.min = '0'; dur.className = 'form-control form-control-sm le-secdur';
    dur.value = section.duration_minutes || '';
    dur.placeholder = 'auto';
    dur.title = 'Minutes shown on the section — leave blank to estimate it from the content';
    dur.addEventListener('input', function () {
      section.duration_minutes = parseInt(dur.value, 10) || 0;
      scheduleSectionSave(section, function (fresh) { estimate.textContent = estimateText(fresh); });
    });
    head.appendChild(dur);

    var actions = document.createElement('span'); actions.className = 'le-secactions';
    var unwrap = document.createElement('button');
    unwrap.className = 'le-secdel'; unwrap.title = 'Remove the dropdown, keep its content in the body';
    unwrap.innerHTML = '<i class="bi bi-box-arrow-up"></i>';
    unwrap.addEventListener('click', function (e) {
      e.stopPropagation();
      if (!confirm('Remove "' + (section.title || 'this section') + '"? Its content stays, moving up into the body.')) return;
      api(u('sectionDelete', section.id), { keep_blocks: true }).then(function () {
        // Splice the children into the body exactly where the section sat, so
        // the reading order the author built is preserved.
        var cards = Array.prototype.slice.call(el.querySelectorAll('.le-block'));
        cards.forEach(function (card) {
          bodyEl.insertBefore(card, el);
          var b = blockById(card.getAttribute('data-id'));
          if (b) b.section_id = null;
        });
        sections = sections.filter(function (s) { return s.id !== section.id; });
        blocks = blocks.filter(function (b) { return b.id !== block.id; });
        el.remove();
        renumber();
      });
    });
    actions.appendChild(unwrap);

    var del = document.createElement('button');
    del.className = 'le-secdel'; del.title = 'Delete the section and everything in it';
    del.innerHTML = '<i class="bi bi-trash"></i>';
    del.addEventListener('click', function (e) {
      e.stopPropagation();
      if (!confirm('Delete "' + (section.title || 'this section') + '" and everything inside it?')) return;
      api(u('sectionDelete', section.id), { keep_blocks: false }).then(function () {
        var gone = {};
        Array.prototype.slice.call(el.querySelectorAll('.le-block')).forEach(function (card) {
          gone[card.getAttribute('data-id')] = true;
        });
        sections = sections.filter(function (s) { return s.id !== section.id; });
        blocks = blocks.filter(function (b) { return b.id !== block.id && !gone[String(b.id)]; });
        el.remove();
        renumber();
      });
    });
    actions.appendChild(del);
    head.appendChild(actions);
    el.appendChild(head);

    /* --- meta row --- */
    var meta = document.createElement('div'); meta.className = 'le-secmeta';

    var summary = document.createElement('input');
    summary.className = 'le-secsummary'; summary.value = section.summary || '';
    summary.placeholder = 'One-line summary (optional)';
    summary.addEventListener('input', function () {
      section.summary = summary.value;
      block.data = block.data || {};
      block.data.summary = summary.value;
      scheduleSectionSave(section);
    });
    meta.appendChild(summary);

    meta.appendChild(checkbox('req' + section.id, 'Required', section.is_required, function (on) {
      section.is_required = on; scheduleSectionSave(section);
    }));
    meta.appendChild(checkbox('lock' + section.id, 'Lock until earlier sections are done',
      section.requires_previous, function (on) {
        section.requires_previous = on; scheduleSectionSave(section);
      }));
    meta.appendChild(checkbox('open' + section.id, 'Open by default', section.open_by_default, function (on) {
      section.open_by_default = on; scheduleSectionSave(section);
    }));

    var estimate = document.createElement('span');
    estimate.className = 'le-secest ms-auto';
    estimate.textContent = estimateText(section);
    meta.appendChild(estimate);
    el.appendChild(meta);
    section._estimateEl = estimate;

    /* --- the blocks inside this section --- */
    var body = document.createElement('div'); body.className = 'le-secbody';
    var zone = document.createElement('div');
    zone.className = 'le-blocks le-drop';
    zone.setAttribute('data-section', section.id);
    zone.setAttribute('data-empty', 'Drop elements here to put them inside this section');
    body.appendChild(zone);
    el.appendChild(body);
    wireDropZone(zone);

    wireBlockDrag(el, block);
    return el;
  }

  function estimateText(section) {
    var label = section.type_label ? section.type_label : 'Section';
    return label + ' · ' + (section.duration_label || ((section.minutes || 1) + ' min'));
  }

  function checkbox(id, label, checked, onChange) {
    var wrap = document.createElement('div'); wrap.className = 'form-check form-switch';
    wrap.innerHTML = '<input class="form-check-input" type="checkbox" id="' + id + '"' + (checked ? ' checked' : '') +
      '><label class="form-check-label" for="' + id + '">' + esc(label) + '</label>';
    wrap.querySelector('input').addEventListener('change', function (e) { onChange(e.target.checked); });
    return wrap;
  }

  function renumber() {
    var count = document.getElementById('leBlockCount');
    if (count) count.textContent = blocks.length;
    var hint = document.getElementById('leBodyHint');
    if (hint) hint.hidden = blocks.length > 0;
  }

  /** Draw the whole body: top-level blocks in order, each section holding its own. */
  function renderAll() {
    bodyEl.innerHTML = '';
    blocks.sort(function (a, b) { return a.order - b.order; });

    // Sections first, so a child block always finds its zone already on the page.
    blocks.filter(function (b) { return !b.section_id; })
      .forEach(function (block) { bodyEl.appendChild(renderBlock(block)); });
    blocks.filter(function (b) { return b.section_id; })
      .forEach(function (block) {
        var zone = zoneFor(String(block.section_id));
        if (zone) zone.appendChild(renderBlock(block));
      });
    renumber();
  }

  /** Recompute the "Reading · 6 min read" hints after content changes. */
  function refreshEstimates() {
    sections.forEach(function (section) {
      scheduleSectionSave(section, function (fresh) {
        if (section._estimateEl) section._estimateEl.textContent = estimateText(fresh);
      }, 1200);
    });
  }

  /* ============================================================
   * Format panel — the toolkit that styles the selected block
   *
   * Every control carries `data-style="<key>"` naming one whitelisted key from
   * apps/learning/styles.py, plus an optional `data-unit` the numeric inputs
   * append ("px", "%"). Reading and writing therefore need no per-control code:
   * one loop binds them all, and adding a control to the template is enough.
   * ============================================================ */
  var fmtEl = document.getElementById('leFormat');

  function selectBlock(id, soft) {
    if (selectedId === id) return;
    selectedId = id;
    markSelected();
    syncFormat();
    // A click inside the body shouldn't yank the page around; only an explicit
    // Format button press scrolls the panel into view.
    if (!soft && fmtEl && id) fmtEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function markSelected() {
    document.querySelectorAll('#leBody .le-block.is-selected')
      .forEach(function (el) { el.classList.remove('is-selected'); });
    if (!selectedId) return;
    var el = document.querySelector('#leBody .le-block[data-id="' + selectedId + '"]');
    if (el) el.classList.add('is-selected');
  }

  /** Push the selected block's style into every control. */
  function syncFormat() {
    if (!fmtEl) return;
    var block = selectedId ? blockById(selectedId) : null;
    var body = document.getElementById('leFmtBody');
    var empty = document.getElementById('leFmtEmpty');
    var target = document.getElementById('leFmtTarget');
    if (body) body.hidden = !block;
    if (empty) empty.hidden = !!block;
    if (target) {
      var meta = block ? (BLOCK_META[block.block_type] || {}) : null;
      target.textContent = meta ? (meta.label || block.block_type) : 'nothing selected';
    }
    if (!block) return;
    var style = block.style || {};

    fmtEl.querySelectorAll('[data-style]').forEach(function (ctrl) {
      var key = ctrl.getAttribute('data-style');
      var unit = ctrl.getAttribute('data-unit') || '';
      var value = style[key] || '';
      if (ctrl.classList.contains('le-fmtseg')) {
        ctrl.querySelectorAll('button').forEach(function (b) {
          b.classList.toggle('is-on', b.getAttribute('data-value') === value);
        });
        return;
      }
      if (ctrl.type === 'color') {
        ctrl.value = /^#[0-9a-fA-F]{6}$/.test(value) ? value : (key === 'background' ? '#ffffff' : '#212529');
        return;
      }
      if (unit && value.slice(-unit.length) === unit) value = value.slice(0, -unit.length);
      ctrl.value = value;
      var out = fmtEl.querySelector('[data-out="' + key + '"]');
      if (out) out.textContent = (value || '100') + unit;
    });
  }

  /** Write one style key on the selected block and save. */
  function setStyle(key, value) {
    var block = selectedId ? blockById(selectedId) : null;
    if (!block) return;
    block.style = block.style || {};
    if (value === '' || value === null || value === undefined) delete block.style[key];
    else block.style[key] = String(value);
    applyPreview(block);
    scheduleSave(block);
  }

  /** Reflect the style on the card immediately — WYSIWYG without a reload. */
  function applyPreview(block) {
    var el = document.querySelector('#leBody .le-block[data-id="' + block.id + '"] > .le-bbody');
    if (!el) return;
    el.setAttribute('style', cssFor(block.style || {}));
  }

  /* Mirrors apps/learning/styles.py. Kept deliberately small: it is a *preview*,
     and the server re-cleans and re-renders on save, so a mismatch can only make
     the editor look slightly different — never let unsafe styling through. */
  var CSS_PROP = {
    align: 'text-align', width: 'width', float: 'float', display: 'display',
    font_family: 'font-family', font_size: 'font-size', font_weight: 'font-weight',
    font_style: 'font-style', text_transform: 'text-transform',
    line_height: 'line-height', letter_spacing: 'letter-spacing',
    color: 'color', background: 'background-color',
    padding: 'padding', margin_top: 'margin-top', margin_bottom: 'margin-bottom',
    radius: 'border-radius'
  };
  var CSS_BORDER = {
    none: '', thin: 'border:1px solid rgba(0,0,0,.12)',
    medium: 'border:2px solid rgba(0,0,0,.18)', thick: 'border:4px solid rgba(0,0,0,.22)',
    'left-accent': 'border-left:4px solid currentColor; padding-left:14px'
  };
  var CSS_SHADOW = {
    none: '', sm: 'box-shadow:0 1px 3px rgba(0,0,0,.10)',
    md: 'box-shadow:0 4px 14px rgba(0,0,0,.12)', lg: 'box-shadow:0 12px 32px rgba(0,0,0,.16)'
  };

  function cssFor(style) {
    var parts = [];
    Object.keys(style).forEach(function (key) {
      var value = style[key];
      if (key === 'border') { if (CSS_BORDER[value]) parts.push(CSS_BORDER[value]); return; }
      if (key === 'shadow') { if (CSS_SHADOW[value]) parts.push(CSS_SHADOW[value]); return; }
      if (CSS_PROP[key] && value) parts.push(CSS_PROP[key] + ':' + value);
    });
    return parts.join('; ');
  }

  function initFormat() {
    if (!fmtEl) return;

    fmtEl.querySelectorAll('[data-style]').forEach(function (ctrl) {
      var key = ctrl.getAttribute('data-style');
      var unit = ctrl.getAttribute('data-unit') || '';

      if (ctrl.classList.contains('le-fmtseg')) {
        ctrl.querySelectorAll('button').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var value = btn.getAttribute('data-value');
            var on = btn.classList.contains('is-on');
            ctrl.querySelectorAll('button').forEach(function (b) { b.classList.remove('is-on'); });
            if (!on) btn.classList.add('is-on');
            setStyle(key, on ? '' : value);      // clicking the active one clears it
          });
        });
        return;
      }

      var event = (ctrl.tagName === 'SELECT' || ctrl.type === 'color') ? 'change' : 'input';
      ctrl.addEventListener(event, function () {
        var value = ctrl.value;
        var out = fmtEl.querySelector('[data-out="' + key + '"]');
        if (out) out.textContent = (value || '') + unit;
        setStyle(key, value === '' ? '' : value + unit);
      });
    });

    fmtEl.querySelectorAll('[data-style-clear]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        btn.getAttribute('data-style-clear').split(',').forEach(function (key) {
          setStyle(key.trim(), '');
        });
        syncFormat();
      });
    });

    var reset = document.getElementById('leFmtReset');
    if (reset) {
      reset.addEventListener('click', function () {
        var block = selectedId ? blockById(selectedId) : null;
        if (!block) return;
        block.style = {};
        applyPreview(block);
        scheduleSave(block);
        syncFormat();
      });
    }
  }

  /* ---------------- autosave ---------------- */
  function scheduleSave(block) {
    setSaveChip('saving');
    clearTimeout(saveTimers['b' + block.id]);
    var run = function () {
      api(u('blockSave', block.id), { data: block.data, style: block.style || {}, track: block.track })
        .then(function (res) {
          setSaveChip('saved');
          // Adopt the server's cleaned style so the editor can never drift from
          // what the learner will actually see.
          if (res && res.block) { block.style = res.block.style; block.css = res.block.css; }
        });
    };
    saveTimers['b' + block.id] = setTimeout(run, 700);
    queueFlush('b' + block.id, run);
  }

  function scheduleSectionSave(section, onDone, delay) {
    setSaveChip('saving');
    clearTimeout(saveTimers['s' + section.id]);
    var run = function () {
      api(u('sectionSave', section.id), {
        title: section.title, summary: section.summary,
        section_type: section.section_type, duration_minutes: section.duration_minutes,
        is_required: section.is_required, requires_previous: section.requires_previous,
        open_by_default: section.open_by_default
      }).then(function (res) {
        setSaveChip('saved');
        if (res && res.section) {
          Object.keys(res.section).forEach(function (k) { section[k] = res.section[k]; });
          if (section._estimateEl) section._estimateEl.textContent = estimateText(section);
          if (onDone) onDone(section);
        }
      });
    };
    saveTimers['s' + section.id] = setTimeout(run, delay || 600);
    queueFlush('s' + section.id, run);
  }

  function queueFlush(key, run) {
    pendingFlush = pendingFlush.filter(function (p) { return p.key !== key; });
    pendingFlush.push({ key: key, run: run });
  }

  function flushAll() {
    Object.keys(saveTimers).forEach(function (k) { clearTimeout(saveTimers[k]); });
    var jobs = pendingFlush.slice();
    pendingFlush = [];
    jobs.forEach(function (p) { p.run(); });
    setSaveChip('saving');
    setTimeout(function () { setSaveChip('saved'); }, 500);
  }

  /* ---------------- reorder ----------------
   * Sections no longer reorder separately: they are blocks in the body, so the
   * same block drag-and-drop moves them. `commitMove` persists the order. */

  /* ---------------- meta, references, attachments, audience ---------------- */
  function initMeta() {
    var fields = ['title', 'subtitle', 'author_name', 'author_role', 'author_bio', 'estimated_minutes'];
    var payload = {};
    var t;
    function push() {
      clearTimeout(t);
      setSaveChip('saving');
      var run = function () { api(u('meta', CFG.lessonId), payload).then(function () { setSaveChip('saved'); }); };
      t = setTimeout(run, 700);
      queueFlush('meta', run);
    }
    fields.forEach(function (f) {
      var el = document.getElementById('meta_' + f);
      if (!el) return;
      el.addEventListener('input', function () {
        payload[f] = el.value;
        if (f === 'title') {
          var h = document.getElementById('leTitleEcho');
          if (h) h.textContent = el.value || 'Untitled lesson';
        }
        push();
      });
    });
  }

  function initReferences() {
    var box = document.getElementById('leRefs');
    if (!box) return;
    var refs = (CFG.references || []).slice();
    function saveRefs() {
      setSaveChip('saving');
      api(u('meta', CFG.lessonId), { references: refs }).then(function () { setSaveChip('saved'); });
    }
    function draw() {
      box.innerHTML = '';
      refs.forEach(function (r, i) {
        var row = document.createElement('div'); row.className = 'le-refrow';
        var ti = document.createElement('input'); ti.className = 'form-control form-control-sm';
        ti.placeholder = 'Citation'; ti.value = r.text || '';
        ti.addEventListener('input', function () { r.text = ti.value; saveRefs(); });
        var ui = document.createElement('input'); ui.className = 'form-control form-control-sm';
        ui.placeholder = 'URL'; ui.value = r.url || ''; ui.style.maxWidth = '38%';
        ui.addEventListener('input', function () { r.url = ui.value; saveRefs(); });
        var del = document.createElement('button'); del.type = 'button';
        del.className = 'btn btn-sm btn-outline-danger border-0'; del.innerHTML = '<i class="bi bi-x-lg"></i>';
        del.addEventListener('click', function () { refs.splice(i, 1); draw(); saveRefs(); });
        row.appendChild(ti); row.appendChild(ui); row.appendChild(del); box.appendChild(row);
      });
    }
    document.getElementById('leAddRef').addEventListener('click', function () { refs.push({ text: '', url: '' }); draw(); });
    draw();
  }

  function initAttachments() {
    var zone = document.getElementById('leAttachZone');
    var picker = document.getElementById('leAttachInput');
    var list = document.getElementById('leAttachments');
    var bar = document.getElementById('leAttachBar');
    if (!zone || !picker || !list) return;

    function upload(files) {
      if (!files || !files.length) return;
      var fd = new FormData();
      Array.prototype.forEach.call(files, function (f) { fd.append('files', f); });
      if (bar) bar.style.display = 'block';
      var xhr = new XMLHttpRequest();
      xhr.open('POST', u('attachAdd', CFG.lessonId));
      xhr.setRequestHeader('X-CSRFToken', CFG.csrf);
      xhr.upload.onprogress = function (e) {
        if (bar && e.lengthComputable) bar.firstChild.style.width = (e.loaded / e.total * 100) + '%';
      };
      xhr.onload = function () {
        if (bar) { bar.style.display = 'none'; bar.firstChild.style.width = '0'; }
        try {
          var res = JSON.parse(xhr.responseText);
          if (!res.ok) { toast('Upload failed', 'error'); return; }
          res.attachments.forEach(addRow);
          toast(res.attachments.length + ' file(s) attached');
        } catch (e) { toast('Upload failed', 'error'); }
      };
      xhr.onerror = function () { if (bar) bar.style.display = 'none'; toast('Upload failed', 'error'); };
      xhr.send(fd);
    }

    function addRow(a) {
      var li = document.createElement('li');
      li.setAttribute('data-id', a.id);
      li.innerHTML = '<i class="bi bi-file-earmark"></i>' +
        '<a href="' + esc(a.url) + '" target="_blank" rel="noopener">' + esc(a.title) + '</a>' +
        '<em>' + esc(a.kind_label) + '</em>' +
        '<button type="button" class="le-attdel" title="Remove"><i class="bi bi-x-lg"></i></button>';
      list.appendChild(li);
    }

    picker.addEventListener('change', function () { upload(picker.files); picker.value = ''; });
    zone.addEventListener('dragover', function (e) { e.preventDefault(); zone.classList.add('hover'); });
    zone.addEventListener('dragleave', function () { zone.classList.remove('hover'); });
    zone.addEventListener('drop', function (e) {
      e.preventDefault(); e.stopPropagation();
      zone.classList.remove('hover');
      upload(e.dataTransfer.files);
    });
    list.addEventListener('click', function (e) {
      var btn = e.target.closest('.le-attdel');
      if (!btn) return;
      var li = btn.closest('li');
      api(u('attachDelete', li.getAttribute('data-id')), {}).then(function () { li.remove(); });
    });
  }

  function initAudience() {
    var wrap = document.getElementById('leAudience');
    var hidden = document.getElementById('pubVisibility');
    if (!wrap || !hidden) return;

    function show(mode) {
      wrap.querySelectorAll('button').forEach(function (b) {
        b.classList.toggle('active', b.getAttribute('data-aud') === mode);
      });
      document.querySelectorAll('.le-audbody').forEach(function (body) {
        body.classList.toggle('show', body.getAttribute('data-aud-body') === mode);
      });
      hidden.value = mode;
    }
    wrap.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () { show(b.getAttribute('data-aud')); });
    });
    var initial = hidden.value;
    show(initial === 'individual' || initial === 'programme' ? initial : 'module');

    // Filter the student list by name.
    var filter = document.getElementById('leStudentFilter');
    var users = document.getElementById('pubUsers');
    if (filter && users) {
      var all = Array.prototype.slice.call(users.options);
      filter.addEventListener('input', function () {
        var q = filter.value.toLowerCase();
        users.innerHTML = '';
        all.forEach(function (o) { if (o.text.toLowerCase().indexOf(q) !== -1) users.appendChild(o); });
      });
    }
  }

  function initPublish() {
    var btn = document.getElementById('lePublishBtn');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var mode = document.getElementById('pubVisibility').value;
      var payload = { status: document.getElementById('pubStatus').value, visibility: mode };
      payload.target_users = picked('pubUsers');
      payload.target_programmes = picked('pubProgrammes');
      payload.target_modules = picked('pubModules');

      if (mode === 'individual' && !payload.target_users.length) {
        toast('Pick at least one student, or choose Programme / Module instead.', 'error');
        return;
      }
      if (mode === 'programme' && !payload.target_programmes.length) {
        toast('Pick at least one programme, or choose Module instead.', 'error');
        return;
      }
      btn.classList.add('is-loading');
      api(u('publish', CFG.lessonId), payload).then(function (res) {
        btn.classList.remove('is-loading');
        if (!res.ok) { toast('Could not save', 'error'); return; }
        toast(res.is_live ? 'Published — learners can see it now' : 'Saved (' + res.status + ')');
        var badge = document.getElementById('leStatusBadge');
        if (badge) badge.textContent = res.status;
      });
    });
  }

  function picked(id) {
    var sel = document.getElementById(id);
    if (!sel) return [];
    return Array.prototype.filter.call(sel.options, function (o) { return o.selected; })
      .map(function (o) { return o.value; });
  }

  /* ---------------- AI ---------------- */
  function initAi() {
    var btn = document.getElementById('leAiRun');
    var box = document.getElementById('leAiPrompt');
    if (!btn || !box) return;
    btn.addEventListener('click', function () {
      var prompt = box.value.trim();
      if (!prompt) { toast('Describe what you want added first.', 'error'); return; }
      btn.disabled = true;
      btn.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Writing…';
      var fd = new FormData();
      fd.append('prompt', prompt);
      fetch(u('aiExtend', CFG.lessonId), {
        method: 'POST', credentials: 'same-origin',
        headers: { 'X-CSRFToken': CFG.csrf }, body: fd
      }).then(function (r) { return r.json(); }).then(function (res) {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-stars me-1"></i>Generate sections';
        if (!res.ok) { toast(res.error || 'Generation failed', 'error'); return; }
        toast('Added ' + res.sections.length + ' draft section(s) — reloading so you can review them');
        setTimeout(function () { location.reload(); }, 900);
      }).catch(function () {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-stars me-1"></i>Generate sections';
        toast('Generation failed', 'error');
      });
    });
  }

  /* ---------------- boot ---------------- */
  wireDropZone(bodyEl);
  renderAll();
  initPaletteDrag();
  initFormat();
  initMeta();
  initReferences();
  initAttachments();
  initAudience();
  initPublish();
  initAi();

  var saveBtn = document.getElementById('leSaveBtn');
  if (saveBtn) saveBtn.addEventListener('click', flushAll);

  // Clicking the empty canvas deselects, so the Format panel doesn't keep
  // pointing at something the author has moved on from.
  bodyEl.addEventListener('mousedown', function (e) {
    if (e.target === bodyEl) selectBlock(null);
  });

  // Never lose an edit to a stray tab close.
  window.addEventListener('beforeunload', function (e) {
    if (!pendingFlush.length) return;
    flushAll();
    e.preventDefault();
    e.returnValue = '';
  });
})();
