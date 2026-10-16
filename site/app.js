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

  /* section index starts collapsed on narrow screens */
  var tocBox = document.querySelector('.toc details');
  if (tocBox && window.matchMedia && window.matchMedia('(max-width: 1099px)').matches) {
    tocBox.open = false;
  }
  if (tocBox) {
    tocBox.addEventListener('click', function (event) {
      var link = event.target.closest ? event.target.closest('a') : null;
      if (link && window.matchMedia && window.matchMedia('(max-width: 1099px)').matches) {
        tocBox.open = false;
      }
    });
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
            for (var j = 0; j < items.length; j++) lines.push('- ' + items[j].textContent.trim());
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
  var holder = document.querySelector('[data-lecture]');
  var box = document.getElementById('read-box');
  if (holder && box) {
    var key = 'cs2680.read.' + holder.getAttribute('data-lecture');
    box.checked = get(key) === '1';
    box.addEventListener('change', function () { set(key, box.checked ? '1' : null); });
  }
  var pills = document.querySelectorAll('[data-read-key]');
  for (var i = 0; i < pills.length; i++) {
    if (get('cs2680.read.' + pills[i].getAttribute('data-read-key')) === '1') pills[i].hidden = false;
  }
})();
