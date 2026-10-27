/* CS2680 觀念導讀 — small per-viewer conveniences.
   localStorage only remembers this viewer's choices; every access is wrapped
   so the page still works when storage is blocked. */
(function () {
  var root = document.documentElement;

  function get(key) {
    try { return window.localStorage.getItem(key); } catch (e) { return null; }
  }
  function set(key, value) {
    try {
      if (value === null) window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, value);
    } catch (e) { /* storage unavailable: keep the in-page state only */ }
  }
  function onMq(mq, fn) {
    if (!mq) return;
    if (mq.addEventListener) mq.addEventListener('change', fn);
    else if (mq.addListener) mq.addListener(fn);
  }

  /* 淺色 / 深色: the viewer's own choice (data-mode on <html>) wins over the
     claude.ai theme (data-theme) and the system setting. Choosing the theme the
     page would show anyway clears the choice, so the page follows the system
     again. This runs first, so a stored choice applies before anything else. */
  var MODE_KEY = 'cs2680.mode';
  var savedMode = get(MODE_KEY);
  if (savedMode === 'light' || savedMode === 'dark') root.setAttribute('data-mode', savedMode);
  var darkMq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function baseTheme() {
    var host = root.getAttribute('data-theme');
    if (host === 'light' || host === 'dark') return host;
    return darkMq && darkMq.matches ? 'dark' : 'light';
  }
  function shownTheme() {
    var name = '';
    try { name = window.getComputedStyle(root).getPropertyValue('--theme-name').trim(); } catch (e) { /* keep light */ }
    return name === 'dark' ? 'dark' : 'light';
  }

  var topbar = document.querySelector('.topbar');
  var topbarInner = document.querySelector('.topbar-inner');
  var themeBtn = null;
  function syncThemeBtn() {
    if (!themeBtn) return;
    var label = shownTheme() === 'dark' ? '切換成淺色模式' : '切換成深色模式';
    themeBtn.setAttribute('aria-label', label);
    themeBtn.title = label;
  }
  function setMode(mode) {
    if (mode === baseTheme()) {
      root.removeAttribute('data-mode');
      set(MODE_KEY, null);
    } else {
      root.setAttribute('data-mode', mode);
      set(MODE_KEY, mode);
    }
    syncThemeBtn();
  }
  if (topbarInner) {
    themeBtn = document.createElement('button');
    themeBtn.type = 'button';
    themeBtn.className = 'theme-btn';
    themeBtn.innerHTML =
      '<svg class="i-moon" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M14 8.53A6 6 0 1 1 7.47 2a4.67 4.67 0 0 0 6.53 6.53z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>' +
      '<svg class="i-sun" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><circle cx="8" cy="8" r="3.1" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 .9v1.4M8 13.7v1.4M.9 8h1.4M13.7 8h1.4M3 3l1 1M12 12l1 1M3 13l1-1M12 4l1-1" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>';
    topbarInner.appendChild(themeBtn);
    themeBtn.addEventListener('click', function () {
      setMode(shownTheme() === 'dark' ? 'light' : 'dark');
    });
    syncThemeBtn();
    onMq(darkMq, syncThemeBtn);
    if (window.MutationObserver) {
      new MutationObserver(syncThemeBtn).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    }
  }

  /* 只看重點: hide the .teach blocks, keep the one-line gist of every slide */
  var GIST_KEY = 'cs2680.gistOnly';
  var toggle = document.getElementById('gist-toggle');
  function applyGist(on) {
    root.classList.toggle('gist-only', on);
    if (toggle) toggle.setAttribute('aria-pressed', on ? 'true' : 'false');
  }
  applyGist(get(GIST_KEY) === '1');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var on = !root.classList.contains('gist-only');
      applyGist(on);
      set(GIST_KEY, on ? '1' : null);
    });
  }

  /* 閱讀進度: a 3px line under the top bar on every page */
  if (topbar && !topbar.querySelector('.readbar')) {
    var bar = document.createElement('div');
    bar.className = 'readbar';
    bar.setAttribute('aria-hidden', 'true');
    bar.appendChild(document.createElement('i'));
    topbar.appendChild(bar);
  }
  var readbar = document.querySelector('.readbar i');

  /* 左側目錄: sticky column on wide screens, drawer on narrow ones.
     Scroll-spy marks the section in view and the sections already passed. */
  var nav = document.getElementById('sidenav');
  var openBtn = document.querySelector('.sn-open');
  var scrim = document.querySelector('.sn-scrim');
  var closeBtn = nav ? nav.querySelector('.sn-close') : null;
  var whereEl = document.querySelector('.sn-where');
  var wideMq = window.matchMedia ? window.matchMedia('(min-width: 1100px)') : null;
  function isWide() { return wideMq ? wideMq.matches : true; }

  function setTopbarH() {
    if (topbar) root.style.setProperty('--topbar-h', topbar.offsetHeight + 'px');
  }

  function keepInView(el) {
    if (!el || !nav) return;
    var box = nav.getBoundingClientRect();
    var r = el.getBoundingClientRect();
    if (!box.height) return;
    var head = nav.querySelector('.sn-head');
    var top = box.top + (head ? head.offsetHeight : 0) + 24; /* clear the drawer's sticky head */
    var pad = 32;
    if (r.top < top) nav.scrollTop -= (top - r.top);
    else if (r.bottom > box.bottom - pad) nav.scrollTop += (r.bottom - box.bottom + pad);
  }

  function setDrawer(open, refocus) {
    if (!nav) return;
    var wasOpen = root.classList.contains('sn-is-open');
    root.classList.toggle('sn-is-open', open);
    if (scrim) scrim.hidden = !open;
    if (openBtn) openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) {
      keepInView(nav.querySelector('.sn-sub.is-active, .is-active > .sn-sec, [aria-current="page"]'));
      if (closeBtn) closeBtn.focus();
    } else {
      if (refocus && openBtn) openBtn.focus();
      /* the spy pauses while the drawer is open; resync once it closes */
      if (wasOpen && typeof requestSpy === 'function') { lastActive = -2; requestSpy(); }
    }
  }

  if (nav) {
    if (openBtn) openBtn.addEventListener('click', function () { setDrawer(!root.classList.contains('sn-is-open'), false); });
    if (scrim) scrim.addEventListener('click', function () { setDrawer(false, true); });
    if (closeBtn) closeBtn.addEventListener('click', function () { setDrawer(false, true); });
    nav.addEventListener('click', function (event) {
      var link = event.target.closest ? event.target.closest('a') : null;
      if (link && !isWide()) setDrawer(false, false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && root.classList.contains('sn-is-open')) setDrawer(false, true);
    });
    var onWide = function () { if (isWide()) setDrawer(false, false); setTopbarH(); };
    onMq(wideMq, onWide);
  }

  /* 還剩多久: lecture pages show the share read and the minutes left, from
     the 「約 N 分鐘」 estimate. In the top bar on wide screens, in the drawer
     head on phones. */
  var holder = document.querySelector('[data-lecture]');
  var readTime = document.querySelector('.read-time');
  var totalMin = 0;
  if (readTime) {
    var minutes = readTime.textContent.match(/\d+/);
    if (minutes) totalMin = parseInt(minutes[0], 10);
  }
  var leftEls = [];
  if (totalMin) {
    if (topbarInner) {
      var barLeft = document.createElement('span');
      barLeft.className = 'readleft';
      barLeft.setAttribute('aria-hidden', 'true');
      topbarInner.insertBefore(barLeft, topbarInner.querySelector('.lecnav') || themeBtn);
      leftEls.push(barLeft);
    }
    var snTitle = nav ? nav.querySelector('.sn-title') : null;
    if (snTitle) {
      var navLeft = document.createElement('span');
      navLeft.className = 'sn-prog';
      snTitle.parentNode.insertBefore(navLeft, snTitle.nextSibling);
      leftEls.push(navLeft);
    }
  }
  var lastLeft = '';
  function showLeft(p) {
    if (!leftEls.length) return;
    var text;
    if (p < 0.01) text = '全文約 ' + totalMin + ' 分';
    else if (p > 0.98) text = '讀到結尾了';
    else text = Math.round(p * 100) + '% · 剩約 ' + Math.max(1, Math.ceil(totalMin * (1 - p))) + ' 分';
    if (text === lastLeft) return;
    lastLeft = text;
    for (var i = 0; i < leftEls.length; i++) leftEls[i].textContent = text;
  }

  /* 回到頂端: shows after about 1.5 screens, only while the reader scrolls up
     (or at the very end), so it does not cover text during reading */
  var totop = document.createElement('button');
  totop.type = 'button';
  totop.className = 'totop';
  totop.setAttribute('aria-label', '回到頂端');
  totop.title = '回到頂端';
  totop.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M8 13.5V3M3.5 7.5 8 3l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  document.body.appendChild(totop);
  totop.addEventListener('click', function () { window.scrollTo(0, 0); });

  var spy = [];
  if (nav) {
    var secLinks = nav.querySelectorAll('[data-spy]');
    for (var s = 0; s < secLinks.length; s++) {
      var target = document.getElementById(secLinks[s].getAttribute('href').slice(1));
      if (!target) continue;
      var item = secLinks[s].parentNode;
      var subs = [];
      var subLinks = item.querySelectorAll('.sn-sub');
      for (var k = 0; k < subLinks.length; k++) {
        var subTarget = document.getElementById(subLinks[k].getAttribute('href').slice(1));
        if (!subTarget) continue;
        /* third level (L4 layout): the chapter's own sub-sections, shown only while the chapter is in view */
        var sub2 = [];
        var sub2Links = subLinks[k].parentNode.querySelectorAll('.sn-sub2');
        for (var k2 = 0; k2 < sub2Links.length; k2++) {
          var t2 = document.getElementById(sub2Links[k2].getAttribute('href').slice(1));
          if (t2) sub2.push({ link: sub2Links[k2], el: t2 });
        }
        subs.push({ link: subLinks[k], li: subLinks[k].parentNode, el: subTarget, subs: sub2 });
      }
      spy.push({ link: secLinks[s], li: item, el: target, subs: subs });
    }
  }

  /* 上次讀到哪裡: a lecture page remembers the heading in view, so a later
     visit can offer to jump back. Per viewer, per lecture. */
  var POS_KEY = holder ? 'cs2680.pos.' + holder.getAttribute('data-lecture') : null;
  var pending = null;
  if (POS_KEY && !location.hash) {
    try { pending = JSON.parse(get(POS_KEY) || 'null'); } catch (e) { pending = null; }
  }
  var place = null;
  var lastSave = 0;
  function savePlace() {
    if (!POS_KEY || !place) return;
    lastSave = Date.now();
    set(POS_KEY, place.done ? null : JSON.stringify(place));
  }
  function notePlace(p, active, sub, line) {
    if (!POS_KEY) return;
    var anchor = sub ? sub.el : (active >= 0 ? spy[active].el : null);
    if (p > 0.97) {
      place = { done: true };
    } else if (anchor && anchor.id && p > 0.02) {
      place = {
        id: anchor.id,
        off: Math.round(line - anchor.getBoundingClientRect().top),
        p: Math.round(p * 1000) / 1000,
        s: spy[active].link.getAttribute('data-short') || ''
      };
    } else {
      return;
    }
    if (Date.now() - lastSave > 1500) savePlace();
  }
  window.addEventListener('pagehide', savePlace);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') savePlace();
  });

  function readingLine() {
    return (topbar ? topbar.getBoundingClientRect().bottom : 0) + Math.min(160, window.innerHeight * 0.25);
  }
  function isShown(el) { return el.getClientRects().length > 0; }

  var lastActive = -2;
  var lastSub = null;
  var lastSub2 = null;
  var ticking = false;
  var lastY = 0;
  var goingUp = false;
  function updateSpy() {
    ticking = false;
    /* the reader cannot scroll the page while the drawer is open; a scroll
       event then comes from layout changes, so keep the last good state */
    if (root.classList.contains('sn-is-open')) return;
    var doc = document.documentElement;
    var y = window.pageYOffset || doc.scrollTop || 0;
    var maxScroll = doc.scrollHeight - window.innerHeight;
    var p = maxScroll > 0 ? Math.min(1, Math.max(0, y / maxScroll)) : 1;
    if (readbar) readbar.style.transform = 'scaleX(' + p + ')';
    showLeft(p);
    if (y < lastY - 2) goingUp = true;
    else if (y > lastY + 2) goingUp = false;
    lastY = y;
    totop.classList.toggle('is-shown', y > window.innerHeight * 1.5 && (goingUp || y >= maxScroll - 2));
    if (!spy.length) return;
    var line = readingLine();
    var active = -1;
    for (var i = 0; i < spy.length; i++) {
      if (spy[i].el.getBoundingClientRect().top <= line) active = i;
    }
    if (maxScroll > 0 && y >= maxScroll - 2) active = spy.length - 1;
    var sub = null;
    if (active >= 0) {
      var list = spy[active].subs;
      for (var j = 0; j < list.length; j++) {
        if (isShown(list[j].el) && list[j].el.getBoundingClientRect().top <= line) sub = list[j];
      }
    }
    var sub2 = null;
    if (sub && sub.subs) {
      for (var j2 = 0; j2 < sub.subs.length; j2++) {
        if (isShown(sub.subs[j2].el) && sub.subs[j2].el.getBoundingClientRect().top <= line) sub2 = sub.subs[j2];
      }
    }
    notePlace(p, active, sub, line);
    if (active === lastActive && sub === lastSub && sub2 === lastSub2) return;
    for (var n = 0; n < spy.length; n++) {
      spy[n].li.classList.toggle('is-active', n === active);
      spy[n].li.classList.toggle('is-past', n < active);
      if (n === active) spy[n].link.setAttribute('aria-current', 'location');
      else spy[n].link.removeAttribute('aria-current');
    }
    if (lastSub && lastSub !== sub) {
      lastSub.link.classList.remove('is-active');
      if (lastSub.li) lastSub.li.classList.remove('is-active');
    }
    if (sub) {
      sub.link.classList.add('is-active');
      if (sub.li) sub.li.classList.add('is-active');
    }
    if (lastSub2 && lastSub2 !== sub2) lastSub2.link.classList.remove('is-active');
    if (sub2) sub2.link.classList.add('is-active');
    lastActive = active;
    lastSub = sub;
    lastSub2 = sub2;
    if (whereEl) whereEl.textContent = active >= 0 ? (spy[active].link.getAttribute('data-short') || '目錄') : '目錄';
    keepInView(sub2 ? sub2.link : (sub ? sub.link : (active >= 0 ? spy[active].link : null)));
  }
  function requestSpy() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(updateSpy);
  }
  setTopbarH();
  updateSpy();
  window.addEventListener('scroll', requestSpy, { passive: true });
  window.addEventListener('resize', function () { setTopbarH(); requestSpy(); });
  window.addEventListener('load', function () { setTopbarH(); lastActive = -2; updateSpy(); });

  /* offer the stored place once, after the browser's own scroll restore */
  function offerResume() {
    if (!pending || !pending.id || !(pending.p > 0.05)) return;
    if (!document.getElementById(pending.id)) return;
    if ((window.pageYOffset || 0) > window.innerHeight * 0.5) return;
    var box = document.createElement('div');
    box.className = 'resume';
    box.setAttribute('role', 'status');
    var text = document.createElement('span');
    text.className = 'resume-t';
    text.appendChild(document.createTextNode('上次讀到'));
    if (pending.s) {
      var where = document.createElement('b');
      where.textContent = pending.s;
      text.appendChild(where);
      text.appendChild(document.createTextNode('· '));
    } else {
      text.appendChild(document.createTextNode(' '));
    }
    text.appendChild(document.createTextNode(Math.round(pending.p * 100) + '%'));
    var go = document.createElement('button');
    go.type = 'button';
    go.className = 'resume-go';
    go.textContent = '繼續讀';
    var shut = document.createElement('button');
    shut.type = 'button';
    shut.className = 'resume-x';
    shut.setAttribute('aria-label', '關閉提示');
    shut.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M4 4l8 8M12 4l-8 8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
    box.appendChild(text);
    box.appendChild(go);
    box.appendChild(shut);
    document.body.appendChild(box);
    var timer = window.setTimeout(dismiss, 15000);
    function dismiss() {
      window.clearTimeout(timer);
      window.removeEventListener('scroll', onScrollAway);
      if (box.parentNode) box.parentNode.removeChild(box);
    }
    function onScrollAway() {
      if ((window.pageYOffset || 0) > window.innerHeight) dismiss();
    }
    window.addEventListener('scroll', onScrollAway, { passive: true });
    shut.addEventListener('click', dismiss);
    go.addEventListener('click', function () {
      dismiss();
      var to = document.getElementById(pending.id);
      if (!to) return;
      var top = to.getBoundingClientRect().top + (window.pageYOffset || 0) - readingLine() + (pending.off || 0);
      var before = root.style.scrollBehavior;
      root.style.scrollBehavior = 'auto';
      window.scrollTo(0, Math.max(0, top));
      root.style.scrollBehavior = before;
    });
  }
  function offerSoon() { window.setTimeout(offerResume, 400); }
  if (pending) {
    if (document.readyState === 'complete') offerSoon();
    else window.addEventListener('load', offerSoon);
  }

  /* 寬圖與寬表: on narrow screens they scroll sideways inside their box.
     A one-line hint says so; it fades after the first swipe. */
  function onSwipe() {
    if (this.scrollLeft < 16) return;
    this.removeEventListener('scroll', onSwipe);
    var hint = this.nextElementSibling;
    if (hint && hint.classList.contains('swipe-hint')) hint.classList.add('is-done');
  }
  function markWide() {
    var boxes = document.querySelectorAll('.diagram .scroll, .table-wrap, .boardwrap');
    for (var i = 0; i < boxes.length; i++) {
      var box = boxes[i];
      if (!isShown(box)) continue; /* in a closed panel: decide when it opens */
      var next = box.nextElementSibling;
      var hint = next && next.classList.contains('swipe-hint') ? next : null;
      var wide = box.scrollWidth > box.clientWidth + 4;
      if (wide && !hint) {
        hint = document.createElement('p');
        hint.className = 'swipe-hint';
        hint.setAttribute('aria-hidden', 'true');
        hint.textContent = box.classList.contains('scroll') ? '← 左右滑動看完整的圖 →' : '← 左右滑動看完整的表 →';
        box.parentNode.insertBefore(hint, box.nextSibling);
        box.addEventListener('scroll', onSwipe, { passive: true });
      } else if (!wide && hint) {
        hint.parentNode.removeChild(hint);
        box.removeEventListener('scroll', onSwipe);
      }
    }
  }
  var wideTimer = 0;
  function markWideSoon() {
    window.clearTimeout(wideTimer);
    wideTimer = window.setTimeout(markWide, 200);
  }
  markWide();
  window.addEventListener('resize', markWideSoon);
  window.addEventListener('load', markWideSoon);
  document.addEventListener('toggle', markWideSoon, true); /* a <details> opened */
  if (window.MutationObserver) {
    new MutationObserver(markWideSoon).observe(document.querySelector('main') || document.body, { childList: true, subtree: true });
  }

  /* 基礎 / 進階 tabs: remembered per viewer */
  var QSET_KEY = 'cs2680.qset';
  var tabs = document.querySelectorAll('.qtab');
  function showSet(name) {
    for (var t = 0; t < tabs.length; t++) {
      var on = tabs[t].getAttribute('aria-controls') === 'qset-' + name;
      tabs[t].setAttribute('aria-selected', on ? 'true' : 'false');
      var panel = document.getElementById(tabs[t].getAttribute('aria-controls'));
      if (panel) panel.hidden = !on;
    }
    markWideSoon();
  }
  if (tabs.length) {
    var saved = get(QSET_KEY);
    if (saved === 'adv' || saved === 'basic') showSet(saved);
    for (var t = 0; t < tabs.length; t++) {
      tabs[t].addEventListener('click', function () {
        var name = this.getAttribute('aria-controls').replace('qset-', '');
        showSet(name);
        set(QSET_KEY, name);
      });
    }
    /* a link to a card in the hidden set (#q3, #b2) opens that set */
    function revealHash() {
      var id = location.hash.replace('#', '');
      var card = id && document.getElementById(id);
      var panel = card && card.closest ? card.closest('.qset') : null;
      if (panel) { showSet(panel.id.replace('qset-', '')); card.scrollIntoView(); }
    }
    window.addEventListener('hashchange', revealHash);
    revealHash();
  }

  /* 名詞註: a dotted term (a.tm) opens its note; a link into any closed <details>
     (#t8 from another page, #x3 from the index) opens it so the target is visible */
  function openDetailsFor(el) {
    var opened = false;
    for (var d = el; d && d !== document.body; d = d.parentNode) {
      if (d.tagName === 'DETAILS' && !d.open) { d.open = true; opened = true; }
    }
    return opened;
  }
  function revealTarget(id) {
    var el = id && document.getElementById(id);
    if (!el) return;
    if (openDetailsFor(el)) {
      /* the browser scrolled before the content existed; scroll again now that it does */
      el.scrollIntoView();
    }
    if (el.classList && el.classList.contains('gloss')) {
      el.classList.add('is-lit');
      setTimeout(function () { el.classList.remove('is-lit'); }, 2500);
    }
  }
  document.addEventListener('click', function (event) {
    var a = event.target.closest ? event.target.closest('a.tm') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.charAt(0) !== '#') return;
    var note = document.getElementById(href.slice(1));
    if (!note) return;
    event.preventDefault();
    openDetailsFor(note);
    note.scrollIntoView({ block: 'nearest' });
    note.classList.add('is-lit');
    setTimeout(function () { note.classList.remove('is-lit'); }, 2500);
    if (history.replaceState) history.replaceState(null, '', href);
  });
  window.addEventListener('hashchange', function () { revealTarget(location.hash.slice(1)); });
  if (location.hash) revealTarget(location.hash.slice(1));

  /* 複製題目: one button per set; copies question, context and answer checklist only */
  var copyBtns = document.querySelectorAll('.copybtn');
  for (var b = 0; b < copyBtns.length; b++) {
    (function (copyBtn) {
      var label = copyBtn.textContent;
      copyBtn.addEventListener('click', function () {
        var setEl = copyBtn.closest ? copyBtn.closest('.qset') : null;
        var lines = [copyBtn.getAttribute('data-title') || document.title];
        var slides = copyBtn.getAttribute('data-slides');
        var isBasic = copyBtn.getAttribute('data-copy') === 'basic';
        if (slides) lines.push(isBasic ? '先讀題目，再看 slides：' + slides : '課前閱讀：slides ' + slides + '，以及這堂的導讀文章');
        if (!isBasic) lines.push('每個要點在網站上都有提示和作答範本。挑一點寫兩三句也可以。');
        lines.push('');
        var cards = (setEl || document).querySelectorAll('.qlist > li');
        for (var i = 0; i < cards.length; i++) {
          var q = cards[i].querySelector('.qtext');
          var c = cards[i].querySelector('.qctx');
          var ref = cards[i].querySelector('.qtag .ref');
          var items = cards[i].querySelectorAll('.qcover li');
          var head = (isBasic ? 'B' : 'Q') + (i + 1) + '. ' + (q ? q.textContent.trim() : '');
          if (isBasic && ref) head += '（看 ' + ref.textContent.trim() + '）';
          lines.push(head);
          if (c) lines.push(c.textContent.trim());
          if (items.length) {
            lines.push('回答時請涵蓋：');
            for (var j = 0; j < items.length; j++) {
              /* the 提示 line stays on the site; the pasted text keeps only the point itself */
              var point = items[j].cloneNode(true);
              var hs = point.querySelectorAll('.qh');
              for (var h = 0; h < hs.length; h++) hs[h].parentNode.removeChild(hs[h]);
              lines.push('- ' + point.textContent.replace(/\s+/g, ' ').trim());
            }
          }
          lines.push('');
        }
        var text = lines.join('\n').trim();
        var box = document.getElementById('copy-fallback');
        function showBox() {
          if (!box) return;
          box.value = text;
          box.hidden = false;
          box.focus();
          box.select();
          copyBtn.textContent = '請手動複製下方文字';
        }
        function copied() {
          copyBtn.textContent = '已複製 ' + cards.length + ' 題';
          setTimeout(function () { copyBtn.textContent = label; }, 2500);
        }
        try {
          navigator.clipboard.writeText(text).then(copied, showBox);
        } catch (e) {
          showBox();
        }
      });
    })(copyBtns[b]);
  }

  /* 已讀 marks: one checkbox per lecture page, pills on the index */
  var readBox = document.getElementById('read-box');
  if (holder && readBox) {
    var key = 'cs2680.read.' + holder.getAttribute('data-lecture');
    readBox.checked = get(key) === '1';
    readBox.addEventListener('change', function () {
      set(key, readBox.checked ? '1' : null);
      var marks = document.querySelectorAll('[data-read-key="' + holder.getAttribute('data-lecture') + '"]');
      for (var m = 0; m < marks.length; m++) marks[m].hidden = !readBox.checked;
    });
  }
  var pills = document.querySelectorAll('[data-read-key]');
  for (var i = 0; i < pills.length; i++) {
    if (get('cs2680.read.' + pills[i].getAttribute('data-read-key')) === '1') pills[i].hidden = false;
  }
})();

/* Code snippets: IDE-style token colors. Each pre > code is plain text in the
   HTML; this reads its text once, splits it into tokens and rebuilds it with
   span.tk-* (styles.css has the colors). The characters stay the same, so
   copying a snippet gives exactly what the page source has. The language is
   guessed from the figcaption (file name) and the first lines; a block can
   force one with <code class="lang-json"> (json, py, js, sh, shell, yaml, md,
   diff, text). */
(function () {
  var KW = {
    py: 'def class return if elif else for while in not and or is import from as with try except finally raise yield lambda pass break continue global async await',
    js: 'const let var function return if else for while of in new await async import export from class extends try catch finally throw typeof',
    sh: 'if then else elif fi for do done while case esac function export local set in return exit'
  };
  /* a plain (no "$") line that starts with one of these is a typed command */
  var CMD = {};
  'git claude cd ls cat cp mv rm mkdir echo export source npm npx node pip uv python python3 pytest jq curl gh docker kubectl make bash sh grep rg find sed awk tail head'.split(' ').forEach(function (w) { CMD[w] = 1; });
  var CONST = { 'true': 1, 'false': 1, 'null': 1, 'None': 1, 'True': 1, 'False': 1, 'undefined': 1 };
  var kwSets = {};
  for (var k in KW) {
    kwSets[k] = {};
    KW[k].split(' ').forEach(function (w) { kwSets[k][w] = 1; });
  }

  function esc(t) { return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function span(cls, t) { return t ? '<span class="tk-' + cls + '">' + esc(t) + '</span>' : ''; }

  function detect(text, cap, forced) {
    if (forced) return forced;
    var c = (cap || '').toLowerCase();
    if (/\.py\b/.test(c)) return 'py';
    if (/\.json\b/.test(c)) return 'json';
    if (/\.ya?ml\b/.test(c)) return 'yaml';
    if (/\.md\b/.test(c)) return 'md';
    if (/\.(ts|js)\b/.test(c) && !/改前與改後/.test(c)) return 'js';
    if (/^#!/.test(text) || /\.(sh|cmd)\b|hooks\/session-start/.test(c)) return 'sh';
    if (/^@@ -\d/m.test(text) || /^<{7} SEARCH/m.test(text)) return 'diff';
    var body = text.replace(/^\s*(\/\/|#).*\n/gm, '');
    if (/^\s*[\[{]/.test(body)) return 'json';
    if (/^\$ /m.test(text)) return 'shell';
    return 'text';
  }

  /* one token regex per language family; the first group that matches names the token.
     A family without some token gets ((?!)): a group that never matches, so the group numbers stay fixed. */
  function tokenRe(lang) {
    var parts = [
      '(\\u2190.*$)',                                     // 1 ← annotation (teaching note) to end of line
      '((?:^|\\s)\\/\\/.*$)',                              // 2 // comment
      (lang === 'json' || lang === 'js' || lang === 'md' || lang === 'diff') ? '((?!))' : '((?:^|\\s)#(?: |!|$).*$)', // 3 # comment
      '("(?:[^"\\\\\\n]|\\\\.)*")',                       // 4 "string"
      (lang === 'py' || lang === 'js' || lang === 'sh' || lang === 'shell' || lang === 'yaml') ? "((?:^|[^\\w'])'(?:[^'\\\\\\n]|\\\\.)*')" : '((?!))', // 5 'string'
      (lang === 'md' || lang === 'text') ? '(`[^`\\n]+`)' : '((?!))', // 6 `code`
      (lang === 'sh' || lang === 'shell') ? '(\\$\\{[^}\\n]*\\}|\\$\\(|\\$[A-Za-z_]\\w*)' : '((?!))', // 7 shell variable
      (lang === 'sh' || lang === 'shell' || lang === 'text' || lang === 'md') ? '((?:^|\\s)--?[A-Za-z][\\w-]*)' : '((?!))', // 8 flag
      '(\\b\\d[\\d,]*(?:\\.\\d+)?%?)',                     // 9 number
      '([A-Za-z_][\\w]*)'                                  // 10 word
    ];
    return new RegExp(parts.join('|'), 'g');
  }

  var ERR = /^(?:FAILED|FAIL|failed|Failed|ERROR|Error|error|errors|ETIMEDOUT|ENOENT|Traceback|\w+Error|\w+Exception)$/;
  var OK = /^(?:PASSED|PASS|passed|OK|ok)$/;

  /* tokens inside one stretch of a line; mode 'out' = program output: only notes, numbers off */
  function tokens(line, lang, re, out) {
    var html = '', last = 0, m;
    re.lastIndex = 0;
    while ((m = re.exec(line)) !== null) {
      if (m[0] === '') { re.lastIndex++; continue; }
      var t = m[0], start = m.index, cls = '', lead = '';
      // groups 2, 3, 5, 8 may start with one whitespace or punctuation char: keep it plain
      if ((m[2] || m[3] || m[8]) && /^\s/.test(t)) { lead = t.charAt(0); t = t.slice(1); }
      if (m[5] && !/^'/.test(t)) { lead = t.charAt(0); t = t.slice(1); }
      if (m[1] || m[2] || m[3]) cls = 'com';
      else if (m[4] || m[5] || m[6]) {
        cls = 'str';
        if (m[4] && /^\s*:/.test(line.slice(start + m[0].length)) && lang !== 'text') cls = 'key';
      }
      else if (m[7]) cls = out ? '' : 'var';
      else if (m[8]) cls = out ? '' : 'flag';
      else if (m[9]) cls = out ? '' : 'num';
      else if (m[10]) {
        var w = m[10], set = kwSets[lang === 'shell' ? 'sh' : lang];
        if (ERR.test(w) && (out || lang === 'text' || lang === 'shell')) cls = 'err';
        else if (OK.test(w) && (out || lang === 'text' || lang === 'shell')) cls = 'ok';
        else if (out) cls = '';
        else if (CONST[w] && lang !== 'text' && lang !== 'md') cls = 'const';
        else if (set && set[w]) cls = 'kw';
        else if (lang === 'py' && /^[A-Z][a-z]\w*$/.test(w)) cls = 'type';
        else if (/^\s*\(/.test(line.slice(start + w.length)) && /^(py|js|sh|shell)$/.test(lang)) cls = 'fn';
      }
      html += esc(line.slice(last, start)) + esc(lead) + (cls ? span(cls, t) : esc(t));
      last = start + m[0].length;
    }
    return html + esc(line.slice(last));
  }

  function highlight(text, lang) {
    var re = tokenRe(lang);
    var lines = text.split('\n');
    var out = [], inFront = false, prevCmd = false, side = '';
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i], m, h;
      // a whole-line note: ellipsis, "↑ …", "[... omitted ...]"
      if (/^\s*(\.\.\.|…|↑|\[\.\.\.)/.test(line)) { out.push(span('com', line)); continue; }
      if (lang === 'diff' || /^(<{7} SEARCH|={7}|>{7} REPLACE)\s*$/.test(line)) {
        if (/^<{7} SEARCH/.test(line)) { side = 'del'; out.push(span('hunk', line)); continue; }
        if (/^={7}\s*$/.test(line) && side) { side = 'add'; out.push(span('hunk', line)); continue; }
        if (/^>{7} REPLACE/.test(line)) { side = ''; out.push(span('hunk', line)); continue; }
        if (side) { out.push('<span class="ln-' + side + '">' + tokens(line, 'text', tokenRe('text')) + '</span>'); continue; }
        if (lang === 'diff') {
          if (/^(\+\+\+|---) /.test(line)) { out.push(tokens(line, 'text', re).replace(/^/, '<span class="tk-head">').replace(/(<span class="tk-com">|$)/, '</span>$1')); continue; }
          if ((m = /^(@@[^@]*@@)(.*)$/.exec(line))) { out.push(span('hunk', m[1]) + tokens(m[2], 'text', re)); continue; }
          if (/^[+-]/.test(line)) {
            var kind = line.charAt(0) === '+' ? 'add' : 'del';
            out.push('<span class="ln-' + kind + '"><span class="tk-sign">' + line.charAt(0) + '</span>' + tokens(line.slice(1), 'js', tokenRe('js')) + '</span>');
            continue;
          }
          out.push(tokens(line, 'js', tokenRe('js')));
          continue;
        }
      }
      // markdown: front matter, headings, list markers
      if (lang === 'md') {
        if (/^---\s*$/.test(line) && (i === 0 || inFront)) { inFront = !inFront && i === 0; out.push(span('dim', line)); continue; }
        if (inFront) {
          if ((m = /^(\s*)([\w.-]+)(:)(.*)$/.exec(line))) { out.push(esc(m[1]) + span('key', m[2]) + span('dim', m[3]) + tokens(m[4], 'yaml', tokenRe('yaml'))); continue; }
          out.push(tokens(line, 'yaml', tokenRe('yaml'))); continue;
        }
        if (/^#{1,6} /.test(line)) { h = line.split('←'); out.push(span('head', h[0]) + (h.length > 1 ? span('com', '←' + h.slice(1).join('←')) : '')); continue; }
        if ((m = /^(\s*)(\d+\.|[-*])( .*)$/.exec(line))) { out.push(esc(m[1]) + span('dim', m[2]) + tokens(m[3], 'md', re)); continue; }
        out.push(tokens(line, 'md', re));
        continue;
      }
      // a typed prompt: "$ cmd", "> message", "/command"
      if ((m = /^(\s*)(\$)( +)(\S+)(.*)$/.exec(line))) {
        out.push(esc(m[1]) + span('dim', m[2]) + esc(m[3]) + span('fn', m[4]) + tokens(m[5], 'shell', tokenRe('shell')));
        prevCmd = /\\\s*$/.test(line);
        continue;
      }
      if ((m = /^(\s*)(>)( .*)$/.exec(line)) && lang !== 'py' && lang !== 'js') {
        h = m[3].split('←');
        var tail = h.length > 1 ? '←' + h.slice(1).join('←') : '';
        var body = h[0], hash = (lang === 'text' || lang === 'shell' || lang === 'sh') ? body.search(/\s#\s/) : -1;
        if (hash >= 0) { tail = body.slice(hash) + tail; body = body.slice(0, hash); }
        out.push(esc(m[1]) + span('dim', m[2]) + span('in', body) + (tail ? span('com', tail) : ''));
        continue;
      }
      if ((m = /^(\s*)(\/[a-z][\w-]*)(\s.*|)$/.exec(line)) && lang !== 'py' && lang !== 'js' && lang !== 'json') {
        out.push(esc(m[1]) + span('fn', m[2]) + tokens(m[3], 'shell', tokenRe('shell')));
        continue;
      }
      // shell session: lines after a "$ cmd" are output unless the command continues with "\"
      if (lang === 'shell') {
        if (prevCmd) { prevCmd = /\\\s*$/.test(line); out.push(tokens(line, 'shell', re)); continue; }
        if (/^\s*#/.test(line)) { out.push(span('com', line)); continue; }
        out.push(tokens(line, 'shell', re, true));
        continue;
      }
      if (lang === 'text' && (m = /^(\s*)([a-z][\w.-]*)(\s.*|)$/.exec(line)) && CMD[m[2]]) {
        out.push(esc(m[1]) + span('fn', m[2]) + tokens(m[3], 'shell', tokenRe('shell')));
        continue;
      }
      // "Key: value" at the start of a line (YAML keys, Thought:/Action: traces, error labels)
      if ((lang === 'yaml' || lang === 'text') && (m = /^(\s*-?\s*)([A-Za-z_][\w.-]*)(:)(\s.*|)$/.exec(line))) {
        out.push(esc(m[1]) + span('key', m[2]) + span('dim', m[3]) + tokens(m[4], lang, re));
        continue;
      }
      if (lang === 'yaml' && (m = /^(\s*)(-)( .*)$/.exec(line))) { out.push(esc(m[1]) + span('dim', m[2]) + tokens(m[3], lang, re)); continue; }
      if (lang === 'sh' && (m = /^(\s*)([A-Za-z_]\w*)(=)(.*)$/.exec(line))) {
        out.push(esc(m[1]) + span('var', m[2]) + span('dim', m[3]) + tokens(m[4], lang, re));
        continue;
      }
      if (lang === 'sh' && (m = /^(\s*)([a-z][\w.-]*)(\s.*|)$/.exec(line)) && !kwSets.sh[m[2]]) {
        out.push(esc(m[1]) + span('fn', m[2]) + tokens(m[3], lang, re));
        continue;
      }
      out.push(tokens(line, lang, re));
    }
    return out.join('\n');
  }

  var blocks = document.querySelectorAll('pre > code');
  for (var b = 0; b < blocks.length; b++) {
    var code = blocks[b];
    if (code.children.length || code.getAttribute('data-hl')) continue;
    var fig = code.closest ? code.closest('figure') : null;
    var cap = fig && fig.querySelector('figcaption') ? fig.querySelector('figcaption').textContent : '';
    var forced = (/(?:^|\s)lang-(\w+)/.exec(code.className) || [])[1];
    var text = code.textContent;
    try {
      code.innerHTML = highlight(text, detect(text, cap, forced));
      code.setAttribute('data-hl', '1');
    } catch (e) {
      code.textContent = text;   /* any surprise: keep the plain text */
    }
  }
})();
