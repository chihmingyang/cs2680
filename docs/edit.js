/* CS2680 觀念導讀 — 維護者的線上編輯與「問 Claude」。
   app.js loads this file only after the maintainer opened a page with ?edit once,
   so members never download it. Design notes: guide/WORKFLOW.md section G.

   Save: never serializes the page. It fetches the current source from GitHub,
   finds each edited block in that source by content (tag + original inner HTML +
   position among identical blocks), replaces only those bytes, and commits.
   A block that changed on GitHub meanwhile is reported, not overwritten.

   Ask: a question is an issue with the label "ask". .github/workflows/ask.yml runs
   Claude Code on it and replies in a comment; this panel polls for the reply. */
(function () {
  var REPO = 'chihmingyang/cs2680';
  var OWNER = 'chihmingyang';
  var API = 'https://api.github.com/repos/' + REPO;
  var BRANCH = 'main';
  var TOKEN_KEY = 'cs2680.ed.token';
  var TOKEN_URL = 'https://github.com/settings/personal-access-tokens/new?name=cs2680-web-editor' +
    '&description=' + encodeURIComponent('CS2680 site in-page editor') +
    '&target_name=' + OWNER + '&expires_in=365&contents=write&issues=write';

  var fileName = location.pathname.split('/').pop() || 'index.html';
  if (!/\.html$/.test(fileName)) fileName = 'index.html';
  var filePath = 'docs/' + fileName;
  var pageTag = fileName.replace(/\.html$/, '');

  var root = document.documentElement;
  var main = document.querySelector('main');
  var topbar = document.querySelector('.topbar');
  var topbarInner = document.querySelector('.topbar-inner');
  if (!main || !topbarInner) return;

  function store(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      if (value === null) localStorage.removeItem(key);
      else localStorage.setItem(key, value);
    } catch (e) { /* storage blocked: the page keeps working for this visit */ }
    return null;
  }
  function h(tag, cls, text) {
    var el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text !== undefined) el.textContent = text;
    return el;
  }
  function icon(path) {
    return '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="' + path + '" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }

  /* ---------- GitHub REST ---------- */
  function gh(path, opts) {
    opts = opts || {};
    var headers = { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };
    var token = store(TOKEN_KEY);
    if (token) headers.Authorization = 'Bearer ' + token;
    if (opts.body) headers['Content-Type'] = 'application/json';
    var url = path.indexOf('http') === 0 ? path : API + path;
    /* a GET goes through the browser cache otherwise, and we always want the live answer */
    if (!opts.method || opts.method === 'GET') url += (url.indexOf('?') < 0 ? '?' : '&') + '_=' + Date.now();
    return fetch(url, { method: opts.method || 'GET', headers: headers, body: opts.body ? JSON.stringify(opts.body) : undefined })
      .then(function (r) {
        return r.text().then(function (t) {
          var data = null;
          try { data = t ? JSON.parse(t) : null; } catch (e) { data = null; }
          if (!r.ok) {
            var err = new Error((data && data.message) || ('HTTP ' + r.status));
            err.status = r.status;
            throw err;
          }
          return data;
        });
      });
  }
  function fromBase64(b64) {
    var bin = atob(b64.replace(/\s/g, ''));
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder('utf-8').decode(bytes);
  }
  function toBase64(text) {
    var bytes = new TextEncoder().encode(text);
    var bin = '';
    for (var i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(bin);
  }

  /* ---------- which elements can be edited ---------- */
  var BLOCK_TAGS = { P: 1, LI: 1, H1: 1, H2: 1, H3: 1, H4: 1, H5: 1, TD: 1, TH: 1, FIGCAPTION: 1, BLOCKQUOTE: 1, DT: 1, DD: 1, DIV: 1 };
  var NOT_LEAF = 'p,ul,ol,li,div,table,pre,figure,details,section,h1,h2,h3,h4,h5,blockquote,svg,button,input,textarea,dl';
  var OFF_LIMITS = 'svg,pre,nav,button,summary,label,textarea,.qtabs,.swipe-hint,.pager,.readmark,.map-row';
  function isBlock(el) {
    if (!BLOCK_TAGS[el.tagName] || el.closest(OFF_LIMITS)) return false;
    if (el.querySelector(NOT_LEAF)) return false;
    if (el.tagName === 'DIV') {
      /* a div is a block only when it holds its own text */
      var own = false;
      for (var n = el.firstChild; n; n = n.nextSibling) {
        if (n.nodeType === 3 && n.nodeValue.trim()) own = true;
      }
      if (!own) return false;
    }
    return !!el.textContent.trim() || !!el.closest('[data-ed-new]');
  }
  function blockFrom(node) {
    var el = node && node.nodeType === 1 ? node : node && node.parentElement;
    if (!el || el.closest('.ed-ui') || el.closest('.ed-deleted')) return null;
    while (el && el !== main) {
      if (BLOCK_TAGS[el.tagName]) return isBlock(el) ? el : null;
      el = el.parentElement;
    }
    return null;
  }

  /* ---------- reading the source ---------- */
  var VOID = { area: 1, base: 1, br: 1, col: 1, embed: 1, hr: 1, img: 1, input: 1, link: 1, meta: 1, source: 1, track: 1, wbr: 1 };
  /* element spans inside <main>, in document order */
  function scanSource(src) {
    var re = /<!--[\s\S]*?-->|<(\/?)([a-zA-Z][\w:-]*)((?:[^>"']|"[^"]*"|'[^']*')*)>/g;
    var stack = [];
    var out = [];
    var m;
    while ((m = re.exec(src))) {
      if (!m[2]) continue;
      var tag = m[2].toLowerCase();
      if (m[1]) {
        var at = stack.length - 1;
        while (at >= 0 && stack[at].tag !== tag) at--;
        if (at < 0) continue;
        var open = stack[at];
        stack.length = at;
        open.closeStart = m.index;
        open.end = re.lastIndex;
        out.push(open);
      } else if (tag === 'script' || tag === 'style') {
        var close = src.toLowerCase().indexOf('</' + tag, re.lastIndex);
        if (close < 0) break;
        re.lastIndex = close;
      } else if (!VOID[tag] && !/\/\s*$/.test(m[3])) {
        stack.push({ tag: tag, start: m.index, openEnd: re.lastIndex, attrs: m[3] });
      }
    }
    var mains = out.filter(function (e) { return e.tag === 'main'; })[0];
    if (!mains) return [];
    return out.filter(function (e) {
      return e.start > mains.start && e.end < mains.end;
    }).sort(function (a, b) { return a.start - b.start; });
  }
  var tpl = document.createElement('template');
  function normalize(html) {
    tpl.innerHTML = html;
    return tpl.innerHTML;
  }
  function sourceIndex(src) {
    var index = {};
    scanSource(src).forEach(function (e) {
      if (!BLOCK_TAGS[e.tag.toUpperCase()]) return;
      var key = e.tag + '|' + normalize(src.slice(e.openEnd, e.closeStart));
      (index[key] = index[key] || []).push(e);
    });
    return index;
  }
  /* anything that can be deleted or have a block added after it (figures, tables, code,
     lists…). code.js rewrites code blocks at runtime, so these are found by their text:
     it keeps the characters. */
  var BOX_SEL = 'p,li,h2,h3,h4,h5,tr,figure,table,details,ul,ol,pre,blockquote,dt,dd,div.table-wrap';
  var BOX_TAGS = { p: 1, li: 1, h2: 1, h3: 1, h4: 1, h5: 1, tr: 1, figure: 1, table: 1, details: 1, ul: 1, ol: 1, pre: 1, blockquote: 1, dt: 1, dd: 1 };
  function squeeze(t) { return t.replace(/\s+/g, ''); }
  function boxIndex(src) {
    var index = {};
    scanSource(src).forEach(function (e) {
      if (!BOX_TAGS[e.tag] && !(e.tag === 'div' && /class="[^"]*\btable-wrap\b/.test(e.attrs))) return;
      tpl.innerHTML = src.slice(e.openEnd, e.closeStart);
      var key = e.tag + '|' + squeeze(tpl.content.textContent);
      (index[key] = index[key] || []).push(e);
    });
    return index;
  }

  /* ---------- edit state ---------- */
  var editing = false;
  var active = null;
  var recs = new WeakMap();      /* block element -> { key, nth, html, undo, redo } */
  var boxRecs = new WeakMap();   /* any box -> { key, nth }, from its text when editing began */
  var dirtyBlocks = [];
  var bar = null;
  var saveBtn = null;
  var statusEl = null;

  function indexBlocks() {
    recs = new WeakMap();
    var seen = {};
    var all = main.querySelectorAll('p,li,h1,h2,h3,h4,h5,td,th,figcaption,blockquote,dt,dd,div');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var html = el.innerHTML;
      var key = el.tagName.toLowerCase() + '|' + html;
      var nth = seen[key] || 0;
      seen[key] = nth + 1;
      recs.set(el, { key: key, nth: nth, html: html, undo: [], redo: [] });
    }
    dirtyBlocks = [];
    boxRecs = new WeakMap();
    var boxSeen = {};
    var boxes = main.querySelectorAll(BOX_SEL);
    for (var b = 0; b < boxes.length; b++) {
      var box = boxes[b];
      if (box.classList.contains('swipe-hint') || box.closest('.ed-ui')) continue;
      var text = box.textContent;
      /* app.js adds the swipe hint at runtime; it is not in the source */
      var hints = box.querySelectorAll('.swipe-hint');
      for (var h2 = 0; h2 < hints.length; h2++) text = text.replace(hints[h2].textContent, '');
      var boxKey = box.tagName.toLowerCase() + '|' + squeeze(text);
      var boxNth = boxSeen[boxKey] || 0;
      boxSeen[boxKey] = boxNth + 1;
      boxRecs.set(box, { key: boxKey, nth: boxNth });
    }
  }

  /* what the block's HTML will be in the source: no editing residue */
  function cleanHtml(el) {
    var box = el.cloneNode(true);
    var had = (recs.get(el) || { html: '' }).html.indexOf(' ') >= 0;
    Array.prototype.slice.call(box.querySelectorAll('*')).forEach(function (n) {
      n.removeAttribute('contenteditable');
      n.removeAttribute('spellcheck');
      n.removeAttribute('data-ed-new');
      n.classList.remove('ed-active', 'ed-dirty', 'ed-target');
      if (!n.getAttribute('class')) n.removeAttribute('class');
      if (n.tagName === 'IMG' && n.getAttribute('data-ed-file')) {
        n.setAttribute('src', n.getAttribute('data-ed-file'));
        n.removeAttribute('data-ed-file');
        n.removeAttribute('data-ed-sent');
        return;
      }
      var tag = n.tagName;
      var style = n.getAttribute('style') || '';
      var keepStyle = tag === 'SPAN' && /^color:\s*var\(--[\w-]+\);?$/.test(style.trim());
      if (tag === 'FONT' || tag === 'DIV' || (tag === 'SPAN' && !keepStyle && !n.attributes.length) || (tag === 'SPAN' && style && !keepStyle)) {
        unwrap(n);
        return;
      }
      if (style && !keepStyle) n.removeAttribute('style');
    });
    /* elements left empty by a split or a delete */
    Array.prototype.slice.call(box.querySelectorAll('b,strong,em,u,mark,span,code,a,figcaption')).reverse().forEach(function (n) {
      if (!n.textContent && !n.querySelector('img,svg,br') && !n.id && !n.classList.contains('anchor')) n.parentNode.removeChild(n);
    });
    while (box.lastChild && box.lastChild.nodeName === 'BR') box.removeChild(box.lastChild);
    if (!had) {
      var walker = document.createTreeWalker(box, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) walker.currentNode.nodeValue = walker.currentNode.nodeValue.replace(/ /g, ' ');
    }
    box.normalize();
    return box.innerHTML;
  }
  function unwrap(n) {
    var parent = n.parentNode;
    while (n.firstChild) parent.insertBefore(n.firstChild, n);
    parent.removeChild(n);
  }

  function markDirty(el) {
    var rec = recs.get(el);
    var dirty;
    if (el.classList.contains('ed-deleted')) {
      dirty = true;
    } else if (rec) {
      dirty = cleanHtml(el) !== rec.html;
      if (!dirty) {
        /* a split-off block keeps its origin dirty */
        var kids = main.querySelectorAll('[data-ed-new]');
        for (var i = 0; i < kids.length; i++) if (originOf(kids[i]) === el) dirty = true;
      }
    } else {
      dirty = true;
    }
    el.classList.toggle('ed-dirty', dirty);
    if (!el.getAttribute('class')) el.removeAttribute('class');
    refreshCount();
  }
  function changedRoots() {
    var roots = [];
    var marked = main.querySelectorAll('.ed-dirty');
    for (var i = 0; i < marked.length; i++) {
      var el = marked[i];
      /* a caption inside a new figure belongs to that figure */
      var fresh = el.parentElement && el.parentElement.closest('[data-ed-new]');
      if (fresh) el = fresh;
      /* inside something being deleted: the delete covers it */
      var gone = el.parentElement && el.parentElement.closest('.ed-deleted');
      if (gone) continue;
      var r = originOf(el) || el;
      if (roots.indexOf(r) < 0) roots.push(r);
    }
    return roots;
  }
  function refreshCount() {
    if (!saveBtn) return;
    var n = main.querySelectorAll('.ed-dirty').length;
    saveBtn.disabled = n === 0;
    saveBtn.textContent = n ? '儲存（' + n + ' 處）' : '儲存';
  }
  function say(text, kind) {
    if (!statusEl) return;
    statusEl.textContent = text || '';
    statusEl.className = 'ed-status' + (kind ? ' is-' + kind : '');
  }

  /* blocks made by pressing Enter hang off the source block they came from */
  var origins = new WeakMap();
  function originOf(el) { return origins.get(el) || null; }

  function activate(el) {
    if (active === el) return;
    deactivate();
    active = el;
    el.setAttribute('contenteditable', 'true');
    el.setAttribute('spellcheck', 'false');
    el.classList.add('ed-active');
  }
  function deactivate() {
    if (!active) return;
    var el = active;
    active = null;
    el.removeAttribute('contenteditable');
    el.removeAttribute('spellcheck');
    el.classList.remove('ed-active');
    if (!el.getAttribute('class')) el.removeAttribute('class');
    markDirty(el);
  }

  /* ---------- undo: our own stack, so toolbar edits and typing share it ---------- */
  var snapTimer = 0;
  function snapshot(el) {
    var rec = recs.get(el);
    if (!rec) { rec = { key: '', nth: 0, html: '', undo: [], redo: [] }; recs.set(el, rec); }
    var now = el.innerHTML;
    if (rec.undo[rec.undo.length - 1] !== now) rec.undo.push(now);
    if (rec.undo.length > 100) rec.undo.shift();
    rec.redo = [];
  }
  function restore(el, from, to) {
    if (!from.length) return;
    to.push(el.innerHTML);
    var html = from.pop();
    if (html === el.innerHTML && from.length) html = from.pop();
    el.innerHTML = html;
    var r = document.createRange();
    r.selectNodeContents(el);
    r.collapse(false);
    var sel = getSelection();
    sel.removeAllRanges();
    sel.addRange(r);
    markDirty(el);
  }

  /* ---------- formatting ---------- */
  function selectionInActive() {
    var sel = getSelection();
    if (!active || !sel.rangeCount || sel.isCollapsed) return null;
    var r = sel.getRangeAt(0);
    return active.contains(r.commonAncestorContainer) ? r : null;
  }
  function matches(el, tag, style) {
    return el.tagName === tag.toUpperCase() && (el.getAttribute('style') || '') === (style || '');
  }
  function format(tag, style) {
    var r = selectionInActive();
    if (!r) { say('先選取要改的文字', 'warn'); return; }
    var el = active;
    snapshot(el);
    /* inside the same format already: take it off */
    var up = r.commonAncestorContainer.nodeType === 1 ? r.commonAncestorContainer : r.commonAncestorContainer.parentElement;
    while (up && up !== el) {
      if (matches(up, tag, style)) {
        unwrap(up);
        el.normalize();
        markDirty(el);
        return;
      }
      up = up.parentElement;
    }
    var frag = r.extractContents();
    var inner = frag.querySelectorAll(tag + (tag === 'span' ? '[style]' : ''));
    Array.prototype.slice.call(inner).forEach(unwrap);
    var wrap = document.createElement(tag);
    if (style) wrap.setAttribute('style', style);
    wrap.appendChild(frag);
    r.insertNode(wrap);
    var sel = getSelection();
    var after = document.createRange();
    after.selectNodeContents(wrap);
    sel.removeAllRanges();
    sel.addRange(after);
    markDirty(el);
    say('');
  }
  function clearFormat() {
    var r = selectionInActive();
    if (!r) { say('先選取要清除格式的文字', 'warn'); return; }
    var el = active;
    snapshot(el);
    var plain = 'b,strong,em,i,u,mark,span[style]';
    /* the selection may sit inside a format: split it out first */
    var up = r.commonAncestorContainer.nodeType === 1 ? r.commonAncestorContainer : r.commonAncestorContainer.parentElement;
    while (up && up !== el) {
      var next = up.parentElement;
      if (up.matches(plain)) unwrap(up);
      up = next;
    }
    var sel = getSelection();
    r = sel.getRangeAt(0);
    var frag = r.extractContents();
    Array.prototype.slice.call(frag.querySelectorAll(plain)).forEach(unwrap);
    r.insertNode(frag);
    el.normalize();
    markDirty(el);
    say('');
  }
  function setLink() {
    var r = selectionInActive();
    if (!r) { say('先選取要加連結的文字', 'warn'); return; }
    var saved = r.cloneRange();
    var url = window.prompt('連結網址（留空就移除連結）', 'https://');
    var sel = getSelection();
    sel.removeAllRanges();
    sel.addRange(saved);
    var el = active;
    var up = saved.commonAncestorContainer.nodeType === 1 ? saved.commonAncestorContainer : saved.commonAncestorContainer.parentElement;
    var link = up.closest ? up.closest('a') : null;
    if (url === null) return;
    snapshot(el);
    if (link && el.contains(link)) unwrap(link);
    if (/^(https?:\/\/.+|#.+|l\d\d[\w-]*\.html.*)$/.test(url.trim())) {
      var frag = saved.extractContents();
      var a = document.createElement('a');
      a.href = url.trim();
      if (/^http/.test(url.trim())) { a.target = '_blank'; a.rel = 'noopener'; }
      a.appendChild(frag);
      saved.insertNode(a);
    }
    markDirty(el);
  }

  function splitBlock(el) {
    var sel = getSelection();
    if (!sel.rangeCount) return;
    var tail = sel.getRangeAt(0).cloneRange();
    tail.deleteContents();
    tail.setEndAfter(el.lastChild || el);
    snapshot(el);
    var frag = tail.extractContents();
    var fresh = el.cloneNode(false);
    fresh.removeAttribute('id');
    fresh.removeAttribute('contenteditable');
    fresh.removeAttribute('spellcheck');
    fresh.classList.remove('ed-active', 'ed-dirty');
    if (!fresh.getAttribute('class')) fresh.removeAttribute('class');
    fresh.setAttribute('data-ed-new', '');
    fresh.appendChild(frag);
    if (!fresh.textContent) fresh.appendChild(document.createElement('br'));
    el.parentNode.insertBefore(fresh, el.nextSibling);
    var from = originOf(el) || el;
    origins.set(fresh, from);
    el.classList.add('ed-dirty');
    fresh.classList.add('ed-dirty');
    activate(fresh);
    fresh.focus();
    var r = document.createRange();
    r.selectNodeContents(fresh);
    r.collapse(true);
    sel.removeAllRanges();
    sel.addRange(r);
    refreshCount();
  }

  /* ---------- save ---------- */
  function outerClean(el) {
    var box = el.cloneNode(false);
    box.removeAttribute('data-ed-new');
    box.removeAttribute('contenteditable');
    box.removeAttribute('spellcheck');
    box.classList.remove('ed-active', 'ed-dirty');
    if (!box.getAttribute('class')) box.removeAttribute('class');
    box.innerHTML = cleanHtml(el);
    return box.outerHTML;
  }
  function plainLen(el) { return el.textContent.replace(/\s/g, '').length; }
  function hasContent(el) { return plainLen(el) > 0 || !!el.querySelector('img'); }

  function buildPatches(src, roots) {
    var index = sourceIndex(src);
    var boxes = null;
    var patches = [];
    var failed = [];
    var kids = main.querySelectorAll('[data-ed-new]');
    function boxSpan(el) {
      if (!boxes) boxes = boxIndex(src);
      var r = boxRecs.get(el);
      var list = r && boxes[r.key];
      return list && list[r.nth];
    }
    roots.forEach(function (el) {
      var rec = recs.get(el);
      var deleted = el.classList.contains('ed-deleted');
      var editable = !deleted && rec && isBlock(el);
      var span = editable ? (index[rec.key] && index[rec.key][rec.nth]) : boxSpan(el);
      if (!span) { failed.push(el); return; }
      var followers = [];
      for (var i = 0; i < kids.length; i++) {
        if (originOf(kids[i]) === el && hasContent(kids[i])) followers.push(kids[i]);
      }
      var lineStart = src.lastIndexOf('\n', span.start) + 1;
      var lead = src.slice(lineStart, span.start);
      var indent = /^\s*$/.test(lead) ? lead : '';
      var extra = followers.map(function (k) { return '\n' + indent + outerClean(k); }).join('');
      if (deleted || (editable && !plainLen(el))) {
        if (extra) {
          patches.push({ start: span.start, end: span.end, text: extra.replace(/^\n\s*/, ''), cut: true });
        } else {
          /* the block goes away, with its line */
          var from = indent !== lead ? span.start : lineStart;
          var to = span.end;
          if (from === lineStart && src.charAt(to) === '\n') to += 1;
          patches.push({ start: from, end: to, text: '', cut: true });
        }
        return;
      }
      if (editable) patches.push({ start: span.openEnd, end: span.closeStart, text: cleanHtml(el) });
      if (extra) patches.push({ start: span.end, end: span.end, text: extra });
    });
    /* something edited inside a block that is also cut: the cut wins */
    var cuts = patches.filter(function (p) { return p.cut; });
    patches = patches.filter(function (p) {
      return p.cut || !cuts.some(function (c) { return p.start >= c.start && p.end <= c.end; });
    });
    return { patches: patches, failed: failed };
  }
  function applyPatches(src, patches) {
    patches.slice().sort(function (a, b) { return b.start - a.start || b.end - a.end; }).forEach(function (p) {
      src = src.slice(0, p.start) + p.text + src.slice(p.end);
    });
    return src;
  }

  /* a short summary of this save; the starting text of the commit message */
  function summarize(roots) {
    var edited = 0, cut = 0, added = 0, pics = 0;
    var kids = main.querySelectorAll('[data-ed-new]');
    roots.forEach(function (el) {
      if (el.classList.contains('ed-deleted')) cut++;
      else if (recs.get(el) && isBlock(el) && cleanHtml(el) !== recs.get(el).html) edited++;
    });
    for (var i = 0; i < kids.length; i++) {
      if (kids[i].parentElement.closest('[data-ed-new]')) continue;
      if (kids[i].querySelector('img')) pics++;
      else if (plainLen(kids[i])) added++;
    }
    var bits = [];
    if (edited) bits.push('改 ' + edited + ' 段');
    if (added) bits.push('加 ' + added + ' 段');
    if (pics) bits.push('貼 ' + pics + ' 張圖');
    if (cut) bits.push('刪 ' + cut + ' 處');
    var label = /^l\d/.test(pageTag) ? pageTag.replace(/^l0?(\d+)/, 'L$1') : pageTag;
    return label + ' ' + (bits.join('、') || '修改');
  }
  function dropEmptyNew() {
    Array.prototype.slice.call(main.querySelectorAll('[data-ed-new]')).forEach(function (el) {
      if (!el.parentElement.closest('[data-ed-new]') && !hasContent(el)) el.parentNode.removeChild(el);
    });
    refreshCount();
  }

  var commitRow = null;
  function askMessage() {
    if (saving) return;
    deactivate();
    dropEmptyNew();
    var roots = changedRoots();
    if (!roots.length) { say('沒有要存的修改'); return; }
    if (!store(TOKEN_KEY)) { showSettings('存檔要先設定 GitHub token。'); return; }
    if (commitRow) { commitRow.querySelector('input').focus(); return; }
    commitRow = h('div', 'ed-commit gutter');
    commitRow.appendChild(h('span', 'ed-commit-pre', '網頁編輯：'));
    var input = h('input', 'ed-commit-input');
    input.type = 'text';
    input.value = summarize(roots);
    input.setAttribute('aria-label', 'Commit message');
    commitRow.appendChild(input);
    var send = h('button', 'ed-save', '送出 commit');
    send.type = 'button';
    commitRow.appendChild(send);
    var cancel = h('button', 'ed-exit', '取消');
    cancel.type = 'button';
    commitRow.appendChild(cancel);
    bar.appendChild(commitRow);
    window.dispatchEvent(new Event('resize'));
    function shut() {
      if (commitRow && commitRow.parentNode) commitRow.parentNode.removeChild(commitRow);
      commitRow = null;
      window.dispatchEvent(new Event('resize'));
    }
    function go() {
      var text = input.value.trim() || summarize(roots);
      shut();
      save(false, '網頁編輯：' + text);
    }
    send.addEventListener('click', go);
    cancel.addEventListener('click', shut);
    input.addEventListener('keydown', function (e) {
      if (e.isComposing || e.keyCode === 229) return;
      if (e.key === 'Enter') { e.preventDefault(); go(); }
      else if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); shut(); }
    });
    input.focus();
    input.select();
  }

  /* pasted images go in as their own commit first, so the page never points at a missing file */
  function uploadImages(message) {
    var pending = Array.prototype.slice.call(main.querySelectorAll('[data-ed-new] img[data-ed-file]')).filter(function (img) {
      return !img.hasAttribute('data-ed-sent') && !img.closest('.ed-deleted');
    });
    return pending.reduce(function (chain, img) {
      return chain.then(function () {
        return gh('/contents/docs/' + img.getAttribute('data-ed-file'), {
          method: 'PUT',
          body: { message: message + '（圖檔）', content: img.src.split(',')[1], branch: BRANCH }
        }).then(function () { img.setAttribute('data-ed-sent', ''); });
      });
    }, Promise.resolve());
  }

  var saving = false;
  function save(retry, message) {
    if (saving && !retry) return;
    deactivate();
    var roots = changedRoots();
    if (!roots.length) { say('沒有要存的修改'); return; }
    saving = true;
    deployRun++;
    saveBtn.disabled = true;
    say('儲存中…');
    var failed = [];
    var snippet = '';
    uploadImages(message).then(function () {
      return gh('/contents/' + filePath + '?ref=' + BRANCH);
    }).then(function (file) {
      var src = fromBase64(file.content);
      var built = buildPatches(src, roots);
      failed = built.failed;
      if (!built.patches.length) throw new Error('nothing');
      var written = built.patches.filter(function (p) { return p.text; })[0];
      snippet = written ? written.text : '';
      var next = applyPatches(src, built.patches);
      if (next === src) throw new Error('same');
      return gh('/contents/' + filePath, {
        method: 'PUT',
        body: { message: message, content: toBase64(next), sha: file.sha, branch: BRANCH }
      });
    }).then(function (res) {
      saving = false;
      /* what was saved is now the baseline; keep failed blocks marked so they are not lost */
      var kept = failed.map(function (el) {
        return { el: el, rec: recs.get(el), box: boxRecs.get(el) };
      });
      Array.prototype.slice.call(main.querySelectorAll('.ed-deleted')).forEach(function (el) {
        if (failed.indexOf(el) < 0 && el.parentNode) el.parentNode.removeChild(el);
      });
      Array.prototype.slice.call(main.querySelectorAll('.ed-dirty')).forEach(function (el) {
        el.classList.remove('ed-dirty');
        if (!el.getAttribute('class')) el.removeAttribute('class');
      });
      Array.prototype.slice.call(main.querySelectorAll('[data-ed-new]')).forEach(function (el) { el.removeAttribute('data-ed-new'); });
      Array.prototype.slice.call(main.querySelectorAll('p,li,h1,h2,h3,h4,h5,td,th,figcaption,blockquote,dt,dd')).forEach(function (el) {
        if (!el.textContent.trim() && !el.querySelector('img,svg,input') && failed.indexOf(el) < 0) el.parentNode.removeChild(el);
      });
      origins = new WeakMap();
      indexBlocks();
      kept.forEach(function (k) {
        if (k.rec) recs.set(k.el, k.rec);
        if (k.box) boxRecs.set(k.el, k.box);
        k.el.classList.add('ed-dirty', 'ed-conflict');
      });
      moveHandle(null);
      refreshCount();
      var sha = res && res.commit && res.commit.sha ? res.commit.sha.slice(0, 7) : '';
      if (failed.length) {
        say('存了，但有 ' + failed.length + ' 處在 GitHub 上已被改過，沒有存（紅框）。請重新整理後再改那幾處。', 'warn');
      } else if (snippet) {
        say('已存（' + sha + '），等站台更新…', 'ok');
        waitForDeploy(snippet, sha);
      } else {
        say('已存（' + sha + '），站台約 1–2 分鐘後更新', 'ok');
      }
    }).catch(function (err) {
      saving = false;
      refreshCount();
      if (err.message === 'nothing') {
        say('這幾處在 GitHub 上已被改過，存不進去。請重新整理頁面。', 'warn');
        roots.forEach(function (el) { el.classList.add('ed-conflict'); });
      } else if (err.message === 'same') {
        Array.prototype.slice.call(main.querySelectorAll('.ed-dirty')).forEach(function (el) { el.classList.remove('ed-dirty'); });
        refreshCount();
        say('內容和 GitHub 上一樣，沒有送 commit。');
      } else if (err.status === 409 && !retry) {
        save(true, message); /* someone pushed between the read and the write */
      } else if (err.status === 401 || err.status === 403 || err.status === 404) {
        say('');
        showSettings('GitHub 拒絕了（' + err.message + '）。token 可能過期，或權限不含 Contents: write。');
      } else {
        say('存檔失敗：' + err.message, 'warn');
      }
    });
  }
  /* GitHub Pages takes a minute or two; tell the reader when a reload is safe */
  var deployRun = 0;
  function waitForDeploy(snippet, sha) {
    var tries = 0;
    var run = ++deployRun;
    function check() {
      if (run !== deployRun) return; /* a newer save owns the status line */
      tries++;
      fetch(location.pathname + '?v=' + Date.now(), { cache: 'no-store' })
        .then(function (r) { return r.text(); })
        .then(function (t) {
          if (snippet && t.indexOf(snippet) >= 0) say('已存（' + sha + '），站台已更新', 'ok');
          else if (tries < 20) setTimeout(check, 15000);
          else say('已存（' + sha + '），站台還沒更新，晚點再重新整理', 'warn');
        })
        .catch(function () { if (tries < 20) setTimeout(check, 15000); });
    }
    setTimeout(check, 15000);
  }

  /* ---------- toolbar ---------- */
  var COLORS = [
    { name: '紅', v: 'var(--key)' },
    { name: '橙', v: 'var(--caution)' },
    { name: '綠', v: 'var(--example)' },
    { name: '藍', v: 'var(--signal)' },
    { name: '紫', v: 'var(--icode-ink)' }
  ];
  function tool(label, title, fn, cls) {
    var b = h('button', 'ed-tool' + (cls ? ' ' + cls : ''));
    b.type = 'button';
    b.innerHTML = label;
    b.title = title;
    b.setAttribute('aria-label', title);
    /* keep the text selection when a tool is pressed */
    b.addEventListener('mousedown', function (e) { e.preventDefault(); });
    b.addEventListener('click', fn);
    return b;
  }
  function buildBar() {
    bar = h('div', 'ed-bar ed-ui');
    var inner = h('div', 'ed-bar-inner gutter');
    inner.appendChild(tool('<b>B</b>', '粗體（黑色小標，⌘B）', function () { format('b'); }));
    inner.appendChild(tool('<strong>重</strong>', '紅字重點', function () { format('strong'); }));
    inner.appendChild(tool('<em>I</em>', '斜體（⌘I）', function () { format('em'); }));
    inner.appendChild(tool('<u>U</u>', '底線', function () { format('u'); }));
    inner.appendChild(tool('<code>&lt;/&gt;</code>', '行內 code', function () { format('code'); }));
    inner.appendChild(tool('<mark>亮</mark>', '螢光標記', function () { format('mark'); }));
    inner.appendChild(h('span', 'ed-sep'));
    COLORS.forEach(function (c) {
      var b = tool('<i style="background:' + c.v + '"></i>', '文字顏色：' + c.name, function () { format('span', 'color: ' + c.v); }, 'ed-swatch');
      inner.appendChild(b);
    });
    inner.appendChild(h('span', 'ed-sep'));
    inner.appendChild(tool('連結', '加或移除連結', setLink));
    inner.appendChild(tool('貼圖', '選一張圖，放在目前這一段後面（也可以直接 ⌘V 貼上）', function () { pickImage(); }));
    inner.appendChild(tool('清除', '清除選取文字的格式', clearFormat));
    inner.appendChild(tool('問 Claude', '問 Claude 選取的文字', function () { openAsk(); }));
    statusEl = h('span', 'ed-status');
    inner.appendChild(statusEl);
    saveBtn = h('button', 'ed-save', '儲存');
    saveBtn.type = 'button';
    saveBtn.disabled = true;
    saveBtn.addEventListener('mousedown', function (e) { e.preventDefault(); });
    saveBtn.addEventListener('click', function () { askMessage(); });
    inner.appendChild(saveBtn);
    var done = h('button', 'ed-exit', '結束');
    done.type = 'button';
    done.addEventListener('click', function () { setEditing(false); });
    inner.appendChild(done);
    bar.appendChild(inner);
    topbar.appendChild(bar);
  }
  function setEditing(on) {
    if (!on && main.querySelector('.ed-dirty') && !window.confirm('還有沒存的修改，要結束編輯嗎？（修改會留在頁面上，重新整理就消失）')) return;
    editing = on;
    var barBefore = topbar.offsetHeight;
    root.classList.toggle('ed-on', on);
    if (on) {
      if (!bar) buildBar();
      bar.hidden = false;
      indexBlocks();
      refreshCount();
    } else {
      deactivate();
      moveHandle(null);
      if (bar) bar.hidden = true;
    }
    editBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
    fab.classList.remove('is-shown');
    window.dispatchEvent(new Event('resize')); /* app.js re-measures the top bar */
    if (window.pageYOffset > 0) window.scrollBy({ top: topbar.offsetHeight - barBefore, behavior: 'instant' });
  }

  /* ---------- block handle: delete, add a paragraph, add an image ---------- */
  var NO_HANDLE = 'nav,.qtabs,.pager,.readmark,.map-row,.ed-ui,.swipe-hint';
  function boxLabel(n) {
    switch (n.tagName) {
      case 'P': return '這段';
      case 'LI': case 'DT': case 'DD': return '這項';
      case 'H2': case 'H3': case 'H4': case 'H5': return '這個標題';
      case 'TR': return '這一列';
      case 'FIGURE': return n.querySelector('pre') ? '這段 code' : '這張圖';
      case 'TABLE': return n.parentElement.classList.contains('table-wrap') ? '' : '整張表';
      case 'DIV': return n.classList.contains('table-wrap') ? '整張表' : '';
      case 'UL': case 'OL': return n.matches('.qlist,.rg') ? '' : '整個清單';
      case 'DETAILS': return '整個收合區塊';
      case 'PRE': return n.closest('figure') ? '' : '這段 code';
      case 'BLOCKQUOTE': return '這段引用';
      default: return '';
    }
  }
  function targetsFor(node) {
    var el = node && node.nodeType === 1 ? node : node && node.parentElement;
    if (!el || !main.contains(el) || el.closest(NO_HANDLE)) return [];
    var out = [];
    for (var n = el; n && n !== main && out.length < 2; n = n.parentElement) {
      if (boxLabel(n)) out.push(n);
    }
    return out;
  }
  function liftToFlow(el) {
    var up = el.closest('figure,.table-wrap,table,ul,ol,details') || el;
    return up;
  }
  var handle = h('div', 'ed-handle ed-ui');
  handle.hidden = true;
  document.body.appendChild(handle);
  var handleFor = null;
  var handleTimer = 0;
  function placeHandle() {
    if (!handleFor) return;
    var r = handleFor.getBoundingClientRect();
    var barBottom = topbar.getBoundingClientRect().bottom;
    var top = Math.max(barBottom + 4, r.top - handle.offsetHeight + 1);
    handle.style.top = top + 'px';
    handle.style.left = Math.max(8, Math.min(r.right - handle.offsetWidth, window.innerWidth - handle.offsetWidth - 8)) + 'px';
    handle.hidden = r.bottom < barBottom || r.top > window.innerHeight;
  }
  function handleButton(label, title, fn, target, cls) {
    var b = h('button', 'ed-hbtn' + (cls ? ' ' + cls : ''), label);
    b.type = 'button';
    b.title = title;
    b.addEventListener('mousedown', function (e) { e.preventDefault(); });
    b.addEventListener('click', fn);
    if (target) {
      b.addEventListener('mouseenter', function () { target.classList.add('ed-target'); });
      b.addEventListener('mouseleave', function () { target.classList.remove('ed-target'); });
    }
    return b;
  }
  function clearTargets() {
    Array.prototype.slice.call(main.querySelectorAll('.ed-target')).forEach(function (el) { el.classList.remove('ed-target'); });
  }
  function moveHandle(node) {
    var list = editing ? targetsFor(node) : [];
    clearTargets();
    handle.textContent = '';
    handleFor = list[0] || null;
    if (!handleFor) { handle.hidden = true; return; }
    var dead = handleFor.closest('.ed-deleted');
    if (dead) {
      handleFor = dead;
      handle.appendChild(handleButton('復原', '取消刪除', function () { undelete(dead); }));
    } else {
      list.forEach(function (t) {
        handle.appendChild(handleButton('刪除' + boxLabel(t), '存檔時才真的刪；存檔前可以復原', function () { markDeleted(t); }, t, 'is-del'));
      });
      if (handleFor.tagName !== 'TR') {
        handle.appendChild(handleButton('＋段落', '在下面加一段文字', function () { addParagraph(handleFor); }));
        handle.appendChild(handleButton('＋圖', '在下面放一張圖', function () { pickImage(handleFor); }));
      }
    }
    handle.hidden = false;
    placeHandle();
  }
  function markDeleted(el) {
    if (el === active || el.contains(active)) deactivate();
    if (el.hasAttribute('data-ed-new')) {
      el.parentNode.removeChild(el);
      moveHandle(null);
      refreshCount();
      return;
    }
    /* anchors inside it may be linked from the table of contents or the text */
    var ids = [];
    if (el.id) ids.push(el.id);
    Array.prototype.forEach.call(el.querySelectorAll('[id]'), function (n) { ids.push(n.id); });
    var refs = 0;
    ids.forEach(function (id) {
      var links = document.querySelectorAll('a[href="#' + (window.CSS && CSS.escape ? CSS.escape(id) : id) + '"]');
      Array.prototype.forEach.call(links, function (a) { if (!el.contains(a)) refs++; });
    });
    if (refs && !window.confirm('目錄或內文有 ' + refs + ' 個連結指到這裡，刪掉後那些連結會失效。還是要刪嗎？')) return;
    el.classList.add('ed-deleted', 'ed-dirty');
    moveHandle(el);
    refreshCount();
  }
  function undelete(el) {
    el.classList.remove('ed-deleted', 'ed-dirty');
    if (!el.getAttribute('class')) el.removeAttribute('class');
    markDirty(el);
    /* markDirty adds ed-dirty to a box with no text record; a box has nothing else to save */
    if (!recs.get(el) || !isBlock(el)) el.classList.remove('ed-dirty');
    if (!el.getAttribute('class')) el.removeAttribute('class');
    moveHandle(el);
    refreshCount();
  }
  function newAfter(target, fresh) {
    var next = target.nextElementSibling;
    /* the swipe hint belongs to the box before it */
    var at = next && next.classList.contains('swipe-hint') ? next : target;
    target.parentNode.insertBefore(fresh, at.nextSibling);
    fresh.setAttribute('data-ed-new', '');
    fresh.classList.add('ed-dirty');
    origins.set(fresh, originOf(target) || target);
  }
  function addParagraph(target) {
    var fresh = document.createElement(target.tagName === 'LI' ? 'li' : 'p');
    fresh.appendChild(document.createElement('br'));
    newAfter(target, fresh);
    activate(fresh);
    fresh.focus();
    var r = document.createRange();
    r.selectNodeContents(fresh);
    r.collapse(true);
    var sel = getSelection();
    sel.removeAllRanges();
    sel.addRange(r);
    moveHandle(fresh);
    refreshCount();
  }

  /* images */
  var IMG_EXT = { 'image/png': 'png', 'image/jpeg': 'jpg', 'image/gif': 'gif', 'image/webp': 'webp' };
  var imgCount = 0;
  var filePick = h('input', 'ed-file ed-ui');
  filePick.type = 'file';
  filePick.accept = 'image/png,image/jpeg,image/gif,image/webp';
  filePick.hidden = true;
  document.body.appendChild(filePick);
  var pickFor = null;
  function imageTarget() {
    var base = handleFor || active;
    return base ? (base.tagName === 'LI' || base.tagName === 'TR' ? liftToFlow(base) : base) : null;
  }
  function pickImage(target) {
    pickFor = target ? (target.tagName === 'LI' ? liftToFlow(target) : target) : imageTarget();
    if (!pickFor) { say('先點要把圖放在哪一段的後面', 'warn'); return; }
    filePick.value = '';
    filePick.click();
  }
  filePick.addEventListener('change', function () {
    if (filePick.files[0] && pickFor) insertImage(filePick.files[0], pickFor);
  });
  function insertImage(file, target) {
    var ext = IMG_EXT[file.type];
    if (!ext) { say('只支援 PNG、JPEG、GIF、WebP', 'warn'); return; }
    if (file.size > 10 * 1024 * 1024) { say('圖超過 10 MB，請先縮小', 'warn'); return; }
    var reader = new FileReader();
    reader.onload = function () {
      var fig = document.createElement('figure');
      fig.className = 'pasted';
      var img = document.createElement('img');
      img.src = reader.result;
      img.alt = '';
      img.setAttribute('data-ed-file', 'img/' + pageTag + '-' + Date.now() + '-' + (++imgCount) + '.' + ext);
      fig.appendChild(img);
      fig.appendChild(document.createElement('figcaption'));
      newAfter(target, fig);
      moveHandle(fig);
      refreshCount();
      say('圖已放上，存檔時才會上傳。可以在下面點一下寫圖說。');
    };
    reader.readAsDataURL(file);
  }

  /* ---------- page events while editing ---------- */
  document.addEventListener('mousedown', function (e) {
    if (!editing || e.target.closest('.ed-ui')) return;
    var el = blockFrom(e.target);
    if (el) activate(el);
    else deactivate();
  }, true);
  document.addEventListener('mouseover', function (e) {
    if (!editing) return;
    if (e.target.closest && e.target.closest('.ed-handle')) { window.clearTimeout(handleTimer); return; }
    if (e.target.closest && e.target.closest('.ed-ui')) return;
    window.clearTimeout(handleTimer);
    var node = e.target;
    /* a short delay, so the mouse can travel to the handle across the block above */
    handleTimer = window.setTimeout(function () { moveHandle(node); }, 120);
  });
  document.addEventListener('pointerdown', function (e) {
    if (editing && e.pointerType !== 'mouse' && !e.target.closest('.ed-ui')) moveHandle(e.target);
  }, true);
  window.addEventListener('scroll', placeHandle, { passive: true });
  /* links and term notes stay put while editing */
  window.addEventListener('click', function (e) {
    if (!editing || !e.target.closest) return;
    if (e.target.closest('.ed-ui')) return;
    var link = e.target.closest('a');
    if (link && blockFrom(link)) {
      e.preventDefault();
      e.stopPropagation();
    }
  }, true);
  document.addEventListener('input', function (e) {
    if (!editing || !active || !active.contains(e.target)) return;
    if (e.isComposing) return;
    var el = active;
    window.clearTimeout(snapTimer);
    snapTimer = window.setTimeout(function () { markDirty(el); }, 300);
  });
  document.addEventListener('beforeinput', function (e) {
    if (!editing || !active || !active.contains(e.target) || e.isComposing) return;
    var rec = recs.get(active);
    var last = rec && rec.undo[rec.undo.length - 1];
    /* group typing: a new undo step after a pause or when the text jumped */
    if (!rec || last === undefined || Date.now() - (rec.at || 0) > 800) snapshot(active);
    if (recs.get(active)) recs.get(active).at = Date.now();
  });
  document.addEventListener('compositionend', function () {
    if (active) markDirty(active);
  });
  document.addEventListener('keydown', function (e) {
    if (!editing) return;
    var mod = e.metaKey || e.ctrlKey;
    var k = (e.key || '').toLowerCase();
    if (mod && k === 's') { e.preventDefault(); askMessage(); return; }
    if (!active || e.isComposing || e.keyCode === 229) return;
    var rec = recs.get(active);
    if (mod && k === 'z') {
      e.preventDefault();
      if (rec) {
        if (e.shiftKey) restore(active, rec.redo, rec.undo);
        else restore(active, rec.undo, rec.redo);
      }
    } else if (mod && k === 'b') { e.preventDefault(); format('b'); }
    else if (mod && k === 'i') { e.preventDefault(); format('em'); }
    else if (k === 'escape') { var was = active; deactivate(); was.blur(); }
    else if (k === 'enter') {
      e.preventDefault();
      if (e.shiftKey || !/^(P|LI)$/.test(active.tagName)) {
        document.execCommand('insertLineBreak');
      } else {
        splitBlock(active);
      }
    }
  });
  document.addEventListener('paste', function (e) {
    if (!editing || !e.clipboardData) return;
    if (e.target.closest && e.target.closest('.ed-ui')) return;
    var files = e.clipboardData.files;
    if (files && files.length && IMG_EXT[files[0].type]) {
      var at = imageTarget();
      e.preventDefault();
      if (at) insertImage(files[0], at);
      else say('先點要把圖放在哪一段的後面', 'warn');
      return;
    }
    if (!active || !active.contains(e.target)) return;
    e.preventDefault();
    var text = e.clipboardData.getData('text/plain');
    document.execCommand('insertText', false, text.replace(/\s*\n\s*/g, ' '));
  });
  window.addEventListener('beforeunload', function (e) {
    if (main.querySelector('.ed-dirty')) {
      e.preventDefault();
      e.returnValue = '';
    }
  });

  /* ---------- settings ---------- */
  var panel = null;
  var panelBody = null;
  function ensurePanel() {
    if (panel) return;
    panel = h('aside', 'ed-panel ed-ui');
    panel.hidden = true;
    var head = h('div', 'ed-panel-head');
    var title = h('button', 'ed-panel-title', '問 Claude');
    title.type = 'button';
    title.title = '回到這一頁的提問列表';
    title.addEventListener('click', function () { showList(); });
    head.appendChild(title);
    var gear = h('button', 'ed-panel-x');
    gear.type = 'button';
    gear.innerHTML = icon('M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M3.4 12.6l1.4-1.4M11.2 4.8l1.4-1.4');
    gear.setAttribute('aria-label', '設定');
    gear.title = '設定';
    gear.addEventListener('click', function () { showSettings(''); });
    head.appendChild(gear);
    var shut = h('button', 'ed-panel-x');
    shut.type = 'button';
    shut.innerHTML = icon('M4 4l8 8M12 4l-8 8');
    shut.setAttribute('aria-label', '關閉');
    shut.addEventListener('click', function () { closePanel(); });
    head.appendChild(shut);
    panel.appendChild(head);
    panelBody = h('div', 'ed-panel-body');
    panel.appendChild(panelBody);
    document.body.appendChild(panel);
  }
  function openPanel() {
    ensurePanel();
    panel.hidden = false;
    root.classList.add('ed-panel-open');
  }
  function closePanel() {
    if (panel) panel.hidden = true;
    root.classList.remove('ed-panel-open');
    stopPoll();
  }
  function showSettings(reason) {
    openPanel();
    stopPoll();
    panelBody.textContent = '';
    if (reason) panelBody.appendChild(h('p', 'ed-note is-warn', reason));
    panelBody.appendChild(h('h3', 'ed-h', 'GitHub token'));
    panelBody.appendChild(h('p', 'ed-note', '存檔和發問都用這個 token 呼叫 GitHub。它只存在這個瀏覽器。'));
    var ol = h('ol', 'ed-steps');
    var li1 = h('li');
    var a = h('a', '', '開 GitHub 的建立頁');
    a.href = TOKEN_URL;
    a.target = '_blank';
    a.rel = 'noopener';
    li1.appendChild(a);
    li1.appendChild(document.createTextNode('。名稱與權限已帶好（Contents、Issues 都是 write）。'));
    ol.appendChild(li1);
    ol.appendChild(h('li', '', 'Repository access 選 Only select repositories，再選 cs2680。'));
    ol.appendChild(h('li', '', '按 Generate token，把 token 貼到下面。'));
    panelBody.appendChild(ol);
    var input = h('input', 'ed-input');
    input.type = 'password';
    input.placeholder = 'github_pat_…';
    input.autocomplete = 'off';
    panelBody.appendChild(input);
    var row = h('div', 'ed-row');
    var ok = h('button', 'ed-save', '驗證並儲存');
    ok.type = 'button';
    row.appendChild(ok);
    if (store(TOKEN_KEY)) {
      var clear = h('button', 'ed-exit', '清除 token');
      clear.type = 'button';
      clear.addEventListener('click', function () {
        store(TOKEN_KEY, null);
        showSettings('已清除。');
      });
      row.appendChild(clear);
    }
    panelBody.appendChild(row);
    var msg = h('p', 'ed-note');
    panelBody.appendChild(msg);
    ok.addEventListener('click', function () {
      var value = input.value.trim();
      if (!value) { msg.textContent = '先貼上 token。'; return; }
      store(TOKEN_KEY, value);
      msg.textContent = '驗證中…';
      gh('').then(function (repo) {
        if (!repo.permissions || !repo.permissions.push) throw new Error('這個 token 不能寫入 cs2680');
        msg.textContent = '可以用了。';
        showList();
      }).catch(function (err) {
        store(TOKEN_KEY, null);
        msg.textContent = '不能用：' + err.message;
      });
    });
    input.focus();
  }

  /* ---------- minimal Markdown for Claude's replies; everything is escaped first ---------- */
  function esc(t) {
    return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function inlineMd(t) {
    var parts = [];
    t = t.replace(/`([^`\n]+)`/g, function (_, c) { parts.push('<code>' + esc(c) + '</code>'); return '\u0000' + (parts.length - 1) + '\u0000'; });
    t = esc(t);
    t = t.replace(/\[([^\]\n]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    t = t.replace(/\*\*([^*\n]+)\*\*/g, '<b>$1</b>');
    return t.replace(/\u0000(\d+)\u0000/g, function (_, i) { return parts[+i]; });
  }
  function renderMd(md) {
    var lines = md.replace(/\r/g, '').split('\n');
    var out = [];
    var list = null;
    var para = [];
    function flush() {
      if (para.length) out.push('<p>' + inlineMd(para.join(' ')) + '</p>');
      para = [];
      if (list) { out.push('</' + list + '>'); list = null; }
    }
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var m;
      if (/^```/.test(line)) {
        flush();
        var code = [];
        for (i++; i < lines.length && !/^```/.test(lines[i]); i++) code.push(lines[i]);
        out.push('<pre><code>' + esc(code.join('\n')) + '</code></pre>');
      } else if (!line.trim()) {
        flush();
      } else if ((m = line.match(/^#{1,6}\s+(.*)/))) {
        flush();
        out.push('<h4>' + inlineMd(m[1]) + '</h4>');
      } else if ((m = line.match(/^>\s?(.*)/))) {
        flush();
        out.push('<blockquote>' + inlineMd(m[1]) + '</blockquote>');
      } else if ((m = line.match(/^\s*(?:[-*]|(\d+)\.)\s+(.*)/))) {
        if (para.length) flush();
        var want = m[1] ? 'ol' : 'ul';
        if (list !== want) { flush(); out.push('<' + want + '>'); list = want; }
        out.push('<li>' + inlineMd(m[2]) + '</li>');
      } else {
        if (list) flush();
        para.push(line.trim());
      }
    }
    flush();
    return out.join('');
  }

  /* ---------- ask ---------- */
  var pollTimer = 0;
  function stopPoll() { window.clearTimeout(pollTimer); }

  function anchorFor(node) {
    var el = node && node.nodeType === 1 ? node : node && node.parentElement;
    if (!el) return '';
    var ids = main.querySelectorAll('[id]');
    var best = '';
    for (var i = 0; i < ids.length; i++) {
      var pos = ids[i].compareDocumentPosition(el);
      if (ids[i] === el || (pos & Node.DOCUMENT_POSITION_FOLLOWING) || (pos & Node.DOCUMENT_POSITION_CONTAINED_BY)) best = ids[i].id;
      else break;
    }
    return best;
  }
  function currentQuote() {
    var sel = getSelection();
    if (!sel.rangeCount || sel.isCollapsed) return null;
    var r = sel.getRangeAt(0);
    if (!main.contains(r.commonAncestorContainer)) return null;
    return { text: sel.toString().trim(), anchor: anchorFor(r.startContainer) };
  }
  function openAsk() {
    composer(currentQuote());
  }
  function needToken() {
    if (store(TOKEN_KEY)) return false;
    showSettings('發問要先設定 GitHub token。');
    return true;
  }
  function composer(quote) {
    openPanel();
    stopPoll();
    if (needToken()) return;
    panelBody.textContent = '';
    if (quote && quote.text) {
      var q = h('blockquote', 'ed-quote', quote.text.length > 600 ? quote.text.slice(0, 600) + '…' : quote.text);
      panelBody.appendChild(q);
    } else {
      panelBody.appendChild(h('p', 'ed-note', '沒有選取文字。Claude 會看這一頁整頁。'));
    }
    var box = h('textarea', 'ed-input');
    box.rows = 5;
    box.placeholder = '想問什麼？例如：這段的 fork 是什麼意思？';
    panelBody.appendChild(box);
    var row = h('div', 'ed-row');
    var ask = h('button', 'ed-save', '問');
    ask.type = 'button';
    ask.title = '只回答，不改站台';
    var edit = h('button', 'ed-exit', '請 Claude 改站台');
    edit.type = 'button';
    edit.title = '照 rewrite-with-example 改 HTML、跑檢查、push';
    row.appendChild(ask);
    row.appendChild(edit);
    panelBody.appendChild(row);
    var msg = h('p', 'ed-note');
    panelBody.appendChild(msg);
    panelBody.appendChild(h('p', 'ed-note', '問題會開成 repo 的公開 issue（label: ask），答完自動關閉。通常 1–3 分鐘。'));
    function send(mode) {
      var text = box.value.trim();
      if (!text) { msg.textContent = '先寫問題。'; box.focus(); return; }
      ask.disabled = edit.disabled = true;
      msg.textContent = '送出中…';
      var anchor = quote && quote.anchor ? quote.anchor : '';
      var body = '<!-- cs2680:ask mode=' + mode + ' file=' + filePath + ' anchor=' + anchor + ' -->\n';
      body += '頁面：https://' + OWNER + '.github.io/cs2680/' + fileName + (anchor ? '#' + anchor : '') + '\n\n';
      if (quote && quote.text) body += quote.text.split('\n').map(function (l) { return '> ' + l; }).join('\n') + '\n\n';
      body += text;
      var title = '[' + pageTag + '] ' + text.replace(/\s+/g, ' ').slice(0, 50);
      gh('/issues', { method: 'POST', body: { title: title, body: body, labels: ['ask'] } }).then(function (issue) {
        showThread(issue.number);
      }).catch(function (err) {
        ask.disabled = edit.disabled = false;
        msg.textContent = '送不出去：' + err.message;
      });
    }
    ask.addEventListener('click', function () { send('ask'); });
    edit.addEventListener('click', function () { send('edit'); });
    box.focus();
  }
  function showList() {
    openPanel();
    stopPoll();
    if (needToken()) return;
    panelBody.textContent = '';
    var fresh = h('button', 'ed-save', '新問題');
    fresh.type = 'button';
    fresh.addEventListener('click', function () { openAsk(); });
    panelBody.appendChild(fresh);
    panelBody.appendChild(h('h3', 'ed-h', '這一頁問過的'));
    var ul = h('ul', 'ed-threads');
    panelBody.appendChild(ul);
    var wait = h('p', 'ed-note', '讀取中…');
    panelBody.appendChild(wait);
    gh('/issues?labels=ask&state=all&per_page=50&sort=updated').then(function (list) {
      wait.textContent = '';
      var mine = (list || []).filter(function (i) { return i.title.indexOf('[' + pageTag + '] ') === 0 && i.user.login === OWNER; });
      if (!mine.length) wait.textContent = '還沒有。選取一段文字，按「問 Claude」。';
      mine.forEach(function (i) {
        var li = h('li');
        var b = h('button', 'ed-thread', i.title.slice(pageTag.length + 3));
        b.type = 'button';
        b.addEventListener('click', function () { showThread(i.number); });
        li.appendChild(b);
        ul.appendChild(li);
      });
    }).catch(function (err) { wait.textContent = '讀不到：' + err.message; });
  }
  function showBubble(parent, who, md, isBot) {
    var box = h('div', 'ed-msg' + (isBot ? ' is-bot' : ''));
    box.appendChild(h('div', 'ed-msg-who', who));
    var body = h('div', 'ed-msg-body');
    body.innerHTML = renderMd(md);
    box.appendChild(body);
    parent.appendChild(box);
  }
  function stripMarker(body) {
    return (body || '').replace(/<!--[\s\S]*?-->\s*/g, '').replace(/^頁面：\S+\s*/, '').trim();
  }
  function showThread(number) {
    openPanel();
    stopPoll();
    panelBody.textContent = '';
    var log = h('div', 'ed-log');
    panelBody.appendChild(log);
    var state = h('p', 'ed-note');
    panelBody.appendChild(state);
    var box = h('textarea', 'ed-input');
    box.rows = 3;
    box.placeholder = '接著問…';
    panelBody.appendChild(box);
    var row = h('div', 'ed-row');
    var ask = h('button', 'ed-save', '問');
    ask.type = 'button';
    var edit = h('button', 'ed-exit', '請 Claude 改站台');
    edit.type = 'button';
    row.appendChild(ask);
    row.appendChild(edit);
    panelBody.appendChild(row);
    var seen = -1;
    var started = Date.now();
    function load() {
      Promise.all([gh('/issues/' + number), gh('/issues/' + number + '/comments?per_page=100')]).then(function (res) {
        var issue = res[0];
        /* only the maintainer and the workflow: this repo's issues are open to anyone */
        var comments = (res[1] || []).filter(function (c) { return c.user.login === OWNER || c.user.login === 'github-actions[bot]'; });
        if (comments.length !== seen) {
          seen = comments.length;
          log.textContent = '';
          showBubble(log, '你', stripMarker(issue.body), false);
          comments.forEach(function (c) {
            var bot = c.user.login !== OWNER;
            showBubble(log, bot ? 'Claude' : '你', stripMarker(c.body), bot);
          });
          panelBody.scrollTop = panelBody.scrollHeight;
        }
        var last = comments[comments.length - 1];
        var answered = last && last.user.login !== OWNER;
        if (answered) {
          state.textContent = '';
        } else {
          var sec = Math.round((Date.now() - started) / 1000);
          state.textContent = 'Claude 處理中…（' + sec + ' 秒）';
          var run = h('a', '', '看執行狀況');
          run.href = 'https://github.com/' + REPO + '/actions/workflows/ask.yml';
          run.target = '_blank';
          run.rel = 'noopener';
          state.appendChild(document.createTextNode(' '));
          state.appendChild(run);
          pollTimer = window.setTimeout(load, 8000);
        }
      }).catch(function (err) {
        state.textContent = '讀不到回覆：' + err.message;
        pollTimer = window.setTimeout(load, 15000);
      });
    }
    function send(mode) {
      var text = box.value.trim();
      if (!text) { box.focus(); return; }
      ask.disabled = edit.disabled = true;
      gh('/issues/' + number + '/comments', { method: 'POST', body: { body: '<!-- cs2680:ask mode=' + mode + ' -->\n' + text } }).then(function () {
        box.value = '';
        ask.disabled = edit.disabled = false;
        started = Date.now();
        stopPoll();
        load();
      }).catch(function (err) {
        ask.disabled = edit.disabled = false;
        state.textContent = '送不出去：' + err.message;
      });
    }
    ask.addEventListener('click', function () { send('ask'); });
    edit.addEventListener('click', function () { send('edit'); });
    load();
  }

  /* selecting text anywhere in the article offers the question */
  var pop = h('button', 'ed-pop ed-ui', '問 Claude');
  pop.type = 'button';
  pop.hidden = true;
  document.body.appendChild(pop);
  pop.addEventListener('mousedown', function (e) { e.preventDefault(); });
  pop.addEventListener('click', function () { pop.hidden = true; openAsk(); });
  document.addEventListener('selectionchange', function () {
    window.clearTimeout(pop._t);
    pop._t = window.setTimeout(function () {
      var sel = getSelection();
      if (!sel.rangeCount || sel.isCollapsed || !main.contains(sel.getRangeAt(0).commonAncestorContainer) || !sel.toString().trim()) {
        pop.hidden = true;
        return;
      }
      var r = sel.getRangeAt(0).getBoundingClientRect();
      pop.hidden = false;
      pop.style.top = Math.max(8, r.bottom + 6 + window.pageYOffset) + 'px';
      pop.style.left = Math.max(8, Math.min(r.left + window.pageXOffset, window.innerWidth - pop.offsetWidth - 8)) + 'px';
    }, 200);
  });

  /* ---------- the two buttons in the top bar ---------- */
  var themeBtn = topbarInner.querySelector('.theme-btn');
  var editBtn = h('button', 'theme-btn ed-ui ed-open');
  editBtn.type = 'button';
  editBtn.innerHTML = icon('M10.6 2.6l2.8 2.8L5.5 13.3l-3.5.7.7-3.5zM9.2 4l2.8 2.8');
  editBtn.title = '編輯這一頁';
  editBtn.setAttribute('aria-label', '編輯這一頁');
  editBtn.setAttribute('aria-pressed', 'false');
  editBtn.addEventListener('click', function () { setEditing(!editing); });
  var askBtn = h('button', 'theme-btn ed-ui ed-open');
  askBtn.type = 'button';
  askBtn.innerHTML = icon('M2.5 3.5h11v7.5H7l-3 2.5V11H2.5z');
  askBtn.title = '問 Claude';
  askBtn.setAttribute('aria-label', '問 Claude');
  askBtn.addEventListener('click', function () {
    if (panel && !panel.hidden) closePanel();
    else if (currentQuote()) openAsk();
    else showList();
  });
  /* a floating pencil within thumb reach, the moment the reader scrolls up, anywhere on the page */
  var fab = h('button', 'ed-fab ed-ui');
  fab.type = 'button';
  fab.innerHTML = icon('M10.6 2.6l2.8 2.8L5.5 13.3l-3.5.7.7-3.5zM9.2 4l2.8 2.8');
  fab.title = '編輯這一頁';
  fab.setAttribute('aria-label', '編輯這一頁');
  fab.addEventListener('click', function () { setEditing(true); });
  document.body.appendChild(fab);
  var fabY = window.pageYOffset;
  window.addEventListener('scroll', function () {
    var y = window.pageYOffset;
    if (y < fabY - 1) fab.classList.toggle('is-shown', !editing && y > 0);
    else if (y > fabY + 1) fab.classList.remove('is-shown');
    fabY = y;
  }, { passive: true });
  topbarInner.insertBefore(askBtn, themeBtn);
  topbarInner.insertBefore(editBtn, askBtn);

  /* test hook: the patch logic, for tools/test_editor.py */
  window.__cs2680ed = { scanSource: scanSource, sourceIndex: sourceIndex, boxIndex: boxIndex, boxSel: BOX_SEL, indexBlocks: indexBlocks, isBlock: isBlock, recs: function () { return recs; }, boxRecs: function () { return boxRecs; }, main: main };

  if (/[?&]edit=now\b/.test(location.search)) setEditing(true);
})();
