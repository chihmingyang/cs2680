/* CS2680 觀念導讀 — 讀書會討論（submit.js）
   每一講「基礎題」每一題下面的留言串、「進階題」每一題下面的討論區、第 7 段「大家的討論」，
   以及 submissions.html 的討論總覽，都由這個檔案驅動。
   共用資料放在 artifact 的 db capability；身份來自 user capability；附件走 assets。
   沒有 window.claude（本機開檔、或 viewer 沒授權）時，頁面照常顯示，只是不能寫。

   兩種形式：
     進階題 answers — 一人一則，再存會覆蓋；別人的預設收合，鼓勵先寫自己的。
     基礎題 notes   — 留言串，一人可以留很多則，照時間排，預設展開；收看 slides 時卡住的地方、
                      跟參考答案不同的點、想再問的問題。

   資料結構：collection "submissions"，每位成員一份 doc，id 就是 user id。
     submissions/<uid> = {
       nick: "顯示名稱（選填）", updatedAt: ISO,
       l02: {
         answers: { q1: { text, at }, q4: { text, at } },   // 進階題：每一題一則想法
         notes:   { b1: [{ id, text, at }, ...], b3: [...] }, // 基礎題：每一題一串留言
         text: "整體補充",                                   // 跨題的補充（選填）
         files: [{ id, name, type, size }],                  // 附件（選填）
         updatedAt: ISO
       }, ...
     }
   規則（publish 時宣告）：所有人可讀，每個人只能寫自己的 doc，owner（主持人）可改任何人的。

   新增講次時，只要在下面的 LECTURES 加一行，討論總覽、參與概況、匯出都會跟著出現。 */
(function () {
  'use strict';

  var LECTURES = [
    ['l01', '課程總覽與 AI 系統', '09-02'],
    ['l02', 'Claude Code 怎麼運作', '09-09'],
    ['l03', '用多個 agent 放大產能', '09-14'],
    ['l04', 'Context 管理與 tool 設計', '09-16'],
    ['l05', 'Multi-agent 架構與溝通', '09-23'],
    ['l06', 'Agent memory 與可靠性', '09-28'],
    ['l07', 'Agent 評估', '09-30'],
    ['l08', '成本、速度與 harness 架構', '10-07']
  ];
  /* Part II：slides 公開後，做好講次頁再搬到上面的 LECTURES。 */
  var UPCOMING = [
    ['10-19', 'Efficient LLM serving: basics I'],
    ['10-21', 'Efficient LLM serving: basics II'],
    ['10-28', 'Efficient LLM serving: speculative decoding'],
    ['11-02', 'Efficient agentic systems: scheduling and prefix caching'],
    ['11-04', 'Efficient LLM serving: pruning and quantization'],
    ['11-09', 'Guest lecture: Why Infrastructure sets the pace of AI (Meta)'],
    ['11-11', 'Efficient LLM serving: GPU and kernels'],
    ['11-16', 'Efficient LLM serving: KV-cache optimization and model architectures'],
    ['11-23', 'Efficient agentic system: routing and load balancing'],
    ['11-30', 'Efficient agentic systems: others']
  ];
  var TITLE = {};
  LECTURES.forEach(function (l) { TITLE[l[0]] = l[1]; });
  function lecNo(key) { return parseInt(key.slice(1), 10); }
  function lecLabel(key) { return 'L' + lecNo(key) + ' ' + (TITLE[key] || ''); }
  function qNo(qid) { return parseInt(String(qid).slice(1), 10); }

  var lecMain = document.querySelector('main[data-lecture]');
  var lecture = lecMain ? lecMain.getAttribute('data-lecture') : null;
  var advPanel = document.getElementById('qset-adv');
  var readerEl = document.getElementById('reader');
  var isLecturePage = !!(lecture && advPanel);
  var isOverview = !!readerEl;
  if (!isLecturePage && !isOverview) return;

  /* ---------- helpers ---------- */
  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }
  function lsGet(key) { try { return window.localStorage.getItem(key); } catch (e) { return null; } }
  function lsSet(key, value) {
    try {
      if (value === null) window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, value);
    } catch (e) { /* storage blocked: in-page state only */ }
  }
  function useCap(name) {
    try {
      if (window.claude && typeof window.claude.use === 'function') {
        return window.claude.use(name).then(function (ns) { return ns || null; }, function () { return null; });
      }
    } catch (e) { /* fall through */ }
    return Promise.resolve(null);
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function fmtTime(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return '';
    return pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }
  function fmtSize(bytes) {
    if (!(bytes >= 0)) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + ' KB';
    return (bytes / 1024 / 1024).toFixed(1) + ' MB';
  }
  function clone(o) { return JSON.parse(JSON.stringify(o || {})); }
  function nowIso() { return new Date().toISOString(); }
  function excerpt(text, n) {
    var t = String(text || '').replace(/\s+/g, ' ').trim();
    return t.length > n ? t.slice(0, n - 1) + '…' : t;
  }
  function blobUrl(id) { return '/_blob/' + id; }
  function safeId(id) { return typeof id === 'string' && /^[0-9a-f]{32}$/.test(id) ? id : null; }
  function copyText(text, btn, okLabel) {
    var label = btn.textContent;
    function done() { btn.textContent = okLabel || '已複製'; setTimeout(function () { btn.textContent = label; }, 2200); }
    function fail() { btn.textContent = '複製失敗，請手動選取'; setTimeout(function () { btn.textContent = label; }, 2500); }
    try { navigator.clipboard.writeText(text).then(done, fail); } catch (e) { fail(); }
  }

  /* ---------- reading the data ---------- */
  function nameOf(data, profile) {
    var nick = (data && typeof data.nick === 'string') ? data.nick.trim() : '';
    if (nick) return nick;
    if (profile && profile.name) return profile.name;
    return '成員';
  }
  function answersOf(entry) {
    var out = {};
    if (!entry || !entry.answers || typeof entry.answers !== 'object') return out;
    Object.keys(entry.answers).forEach(function (qid) {
      var a = entry.answers[qid];
      if (/^q\d{1,2}$/.test(qid) && a && typeof a.text === 'string' && a.text.trim()) out[qid] = { text: a.text, at: a.at || '' };
    });
    return out;
  }
  /* 基礎題留言：{ b1: [{id, text, at}, ...] }，只留格式正確的 */
  function notesOf(entry) {
    var out = {};
    if (!entry || !entry.notes || typeof entry.notes !== 'object') return out;
    Object.keys(entry.notes).forEach(function (qid) {
      var arr = entry.notes[qid];
      if (!/^b\d{1,2}$/.test(qid) || !Array.isArray(arr)) return;
      var keep = arr.filter(function (n) { return n && typeof n.text === 'string' && n.text.trim() && typeof n.id === 'string'; })
        .map(function (n) { return { id: n.id, text: n.text, at: n.at || '' }; });
      if (keep.length) out[qid] = keep;
    });
    return out;
  }
  function noteCount(entry) {
    var ns = notesOf(entry), n = 0;
    Object.keys(ns).forEach(function (q) { n += ns[q].length; });
    return n;
  }
  function newId() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }
  function hasOverall(entry) { return !!(entry && typeof entry.text === 'string' && entry.text.trim()); }
  function filesOf(entry) {
    return (entry && Array.isArray(entry.files) ? entry.files : []).filter(function (f) { return f && safeId(f.id); });
  }
  function hasAnything(entry) { return Object.keys(answersOf(entry)).length > 0 || noteCount(entry) > 0 || hasOverall(entry) || filesOf(entry).length > 0; }
  function latestOf(entry) {
    var t = (entry && entry.updatedAt) || '';
    var ans = answersOf(entry);
    Object.keys(ans).forEach(function (q) { if (ans[q].at > t) t = ans[q].at; });
    var ns = notesOf(entry);
    Object.keys(ns).forEach(function (q) { ns[q].forEach(function (n) { if (n.at > t) t = n.at; }); });
    return t;
  }
  /* everyone's notes under one 基礎題, oldest first */
  function noteThreadOf(docs, key, qid) {
    var out = [];
    docs.forEach(function (snap) {
      var data = snap.data() || {};
      var ns = notesOf(data[key]);
      (ns[qid] || []).forEach(function (n) { out.push({ uid: snap.id, data: data, id: n.id, text: n.text, at: n.at }); });
    });
    out.sort(function (a, b) { return (a.at || '').localeCompare(b.at || ''); });
    return out;
  }
  /* which 基礎題 of one lecture have notes, by id */
  function notedQuestions(docs, key) {
    var seen = {};
    docs.forEach(function (s) { var d = s.data() || {}; Object.keys(notesOf(d[key])).forEach(function (q) { seen[q] = true; }); });
    return Object.keys(seen).sort(function (a, b) { return qNo(a) - qNo(b); });
  }
  /* everyone's answers to one question of one lecture, oldest first */
  function threadOf(docs, key, qid) {
    var out = [];
    docs.forEach(function (snap) {
      var data = snap.data() || {};
      var ans = answersOf(data[key]);
      if (ans[qid]) out.push({ uid: snap.id, data: data, text: ans[qid].text, at: ans[qid].at });
    });
    out.sort(function (a, b) { return (a.at || '').localeCompare(b.at || ''); });
    return out;
  }
  /* everyone who left anything in one lecture */
  function peopleOf(docs, key) {
    var out = [];
    docs.forEach(function (snap) {
      var data = snap.data() || {};
      var entry = data[key];
      if (hasAnything(entry)) out.push({ uid: snap.id, data: data, entry: entry, answers: answersOf(entry), notes: notesOf(entry), files: filesOf(entry), latest: latestOf(entry) });
    });
    out.sort(function (a, b) { return (b.latest || '').localeCompare(a.latest || ''); });
    return out;
  }
  /* people: everyone who left anything; total/perQ: 進階題想法; notes/perB: 基礎題留言; writers: 寫了進階題的人數 */
  function statsOf(docs, key) {
    var people = peopleOf(docs, key);
    var perQ = {}, perB = {}, total = 0, notes = 0, writers = 0;
    people.forEach(function (p) {
      var qs = Object.keys(p.answers);
      if (qs.length) writers++;
      qs.forEach(function (q) { perQ[q] = (perQ[q] || 0) + 1; total++; });
      Object.keys(p.notes).forEach(function (b) { perB[b] = (perB[b] || 0) + p.notes[b].length; notes += p.notes[b].length; });
    });
    return { people: people, perQ: perQ, total: total, perB: perB, notes: notes, writers: writers };
  }
  function avatarImg(profile, cls) {
    var img = el('img', cls || 'avatar');
    img.alt = '';
    if (profile && profile.avatarUrl) img.src = profile.avatarUrl;
    else img.hidden = true;
    return img;
  }
  function avatarStack(uids, profiles, max) {
    var wrap = el('span', 'avs');
    var shown = uids.slice(0, max || 5);
    shown.forEach(function (uid) { wrap.appendChild(avatarImg(profiles[uid], 'avatar')); });
    if (uids.length > shown.length) wrap.appendChild(el('span', 'avs-more', '+' + (uids.length - shown.length)));
    return wrap;
  }
  function fileList(files) {
    var ul = el('ul', 'attach');
    files.forEach(function (f) {
      var a = el('a', null, String(f.name || '附件') + (f.size ? '（' + fmtSize(f.size) + '）' : ''));
      a.href = blobUrl(f.id); a.target = '_blank'; a.rel = 'noopener';
      var li = el('li'); li.appendChild(a); ul.appendChild(li);
    });
    return ul;
  }

  var ACCEPT = {
    pdf: 'application/pdf', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif',
    webp: 'image/webp', md: 'text/markdown', txt: 'text/plain', csv: 'text/csv', json: 'application/json'
  };
  var ACCEPT_TYPES = Object.keys(ACCEPT).map(function (k) { return ACCEPT[k]; });
  function typeFor(file) {
    if (ACCEPT_TYPES.indexOf(file.type) >= 0) return file.type;
    var ext = (file.name.split('.').pop() || '').toLowerCase();
    return ACCEPT[ext] || null;
  }

  /* ---------- shared state ---------- */
  var db = null, user = null, me = { id: null, name: '', isOwner: false, canEdit: false, avatarUrl: '' };
  var canWrite = null;           // user.can('data.write'): true / false / null (unknown)
  var docs = [];                 // latest QuerySnapshot.docs of "submissions"
  var ready = Promise.all([useCap('db'), useCap('user')]).then(function (r) {
    db = r[0]; user = r[1];
    if (!user) return;
    return user.me().then(function (m) { me = m; return user.can('data.write'); }).then(function (c) { canWrite = c; });
  });
  function profilesFor(ids) {
    var uniq = ids.filter(function (id, i) { return id && ids.indexOf(id) === i; });
    return (user && uniq.length) ? user.profiles(uniq) : Promise.resolve({});
  }
  function subscribe(onDocs, onError) {
    if (!db) return;
    db.collection('submissions').onSnapshot(function (snap) {
      docs = snap.docs;
      onDocs(snap);
    }, function (err) { onError(err); });
  }
  /* one write at a time, read-modify-write of a whole member doc */
  var writeChain = Promise.resolve();
  function mutateDoc(uid, fn) {
    var p = writeChain.then(function () {
      var ref = db.doc('submissions/' + uid);
      return ref.get().then(function (snap) {
        var data = snap.exists ? clone(snap.data()) : {};
        fn(data);
        data.updatedAt = nowIso();
        return ref.set(data);
      });
    });
    writeChain = p.then(function () {}, function () {});
    return p;
  }
  function errText(err, verb) {
    var code = err && err.code;
    if (code === 'invalid_argument') return '你目前是唯讀身份，不能' + verb + '。請主持人在分享設定把你加為 Contributor。';
    if (code === 'quota_exceeded') return '資料庫已滿，請通知主持人。';
    if (code === 'resource_exhausted') return '動作太頻繁，稍等再試。';
    return verb + '失敗（' + (code || '未知錯誤') + '），請再試一次。';
  }
  function canSend() { return !!(db && me.id && canWrite !== false); }

  /* two-step delete: 刪除 → 確定？ */
  function confirmButton(label, onConfirm, cls) {
    var wrap = el('span', 'confirm');
    var btn = el('button', 'ghostbtn small' + (cls ? ' ' + cls : ''), label); btn.type = 'button';
    var yes = el('button', 'ghostbtn small danger', '確定刪除'); yes.type = 'button'; yes.hidden = true;
    var no = el('button', 'ghostbtn small', '取消'); no.type = 'button'; no.hidden = true;
    btn.addEventListener('click', function () { btn.hidden = true; yes.hidden = false; no.hidden = false; yes.focus(); });
    no.addEventListener('click', function () { btn.hidden = false; yes.hidden = true; no.hidden = true; });
    yes.addEventListener('click', function () { yes.disabled = true; no.disabled = true; onConfirm(yes); });
    wrap.appendChild(btn); wrap.appendChild(yes); wrap.appendChild(no);
    return wrap;
  }
  function autoGrow(ta, minPx) {
    var min = minPx || 96;
    function fit() { ta.style.height = 'auto'; ta.style.height = Math.min(600, Math.max(ta.scrollHeight + 2, min)) + 'px'; }
    ta.addEventListener('input', fit);
    ta._fit = fit;
    fit();
  }

  /* ========================================================================
     Lecture page: one discussion block under every 進階題 + section 7
     ======================================================================== */
  if (isLecturePage) {
    var NICK_KEY = 'cs2680.nick';
    var OPEN_KEY = 'cs2680.talkOpen';
    var cards = Array.prototype.slice.call(advPanel.querySelectorAll('.qlist > li.dq'));
    var blocks = {};               // qid -> { root, head, list, mine, form, ta, status, ... }
    var basicPanel = document.getElementById('qset-basic');
    var bcards = basicPanel ? Array.prototype.slice.call(basicPanel.querySelectorAll('.qlist > li.bq')) : [];
    var nblocks = {};              // bid -> { root, head, headAvs, headText, list, form, ta, status, open }
    var tabBasic = document.getElementById('tab-basic');
    var tabAdv = document.getElementById('tab-adv');
    var tabBasicBase = tabBasic && tabBasic.querySelector('span') ? tabBasic.querySelector('span').textContent : '';
    var tabAdvBase = tabAdv && tabAdv.querySelector('span') ? tabAdv.querySelector('span').textContent : '';
    var expandAll = lsGet(OPEN_KEY) === '1';
    var manual = {};               // qid -> true/false when the viewer toggled a thread by hand
    var prefilled = false;
    var sumEl = $('talk-sum');
    var listEl = $('sub-list');
    var countEl = $('sub-count');
    var formEl = $('sub-form');
    var textEl = $('sub-text');
    var fileRow = $('sub-filerow');
    var fileEl = $('sub-file');
    var attachEl = $('sub-attach');
    var sendBtn = $('sub-send');
    var copyAllBtn = $('sub-copy');
    var statusEl = $('sub-status');
    var assets = null;
    var pendingFiles = [];
    var overallDirty = false;
    var OVERALL_KEY = 'cs2680.draft.' + lecture + '.all';

    /* --- identity bar, inserted above the question list --- */
    var idbar = el('div', 'idbar');
    idbar.id = 'idbar';
    var idWho = el('span', 'idbar-who');
    var idAv = el('img', 'avatar'); idAv.alt = ''; idAv.hidden = true;
    var idText = el('span', 'idbar-text', '連線中…');
    var idRename = el('button', 'linkbtn', '改名'); idRename.type = 'button'; idRename.hidden = true;
    idWho.appendChild(idAv); idWho.appendChild(idText); idWho.appendChild(idRename);
    var idForm = el('form', 'idbar-form'); idForm.hidden = true;
    var idInput = el('input'); idInput.type = 'text'; idInput.maxLength = 40; idInput.id = 'sub-nick'; idInput.placeholder = '顯示名稱'; idInput.autocomplete = 'nickname';
    var idSave = el('button', 'copybtn small', '儲存'); idSave.type = 'submit';
    var idCancel = el('button', 'ghostbtn small', '取消'); idCancel.type = 'button';
    idForm.appendChild(idInput); idForm.appendChild(idSave); idForm.appendChild(idCancel);
    var idRight = el('label', 'toggle');
    var idToggle = el('input'); idToggle.type = 'checkbox'; idToggle.id = 'talk-expand'; idToggle.checked = expandAll;
    idRight.appendChild(idToggle); idRight.appendChild(document.createTextNode('展開所有人的想法'));
    idbar.appendChild(idWho); idbar.appendChild(idForm); idbar.appendChild(idRight);
    var note = el('p', 'sub-note'); note.id = 'sub-note'; note.hidden = true;
    var qlist = advPanel.querySelector('.qlist');
    advPanel.insertBefore(idbar, qlist);
    advPanel.insertBefore(note, qlist);

    function setNote(text, warn) { note.textContent = text || ''; note.hidden = !text; note.classList.toggle('warn', !!warn); }
    function setIdText(name) {
      idText.textContent = '';
      idText.appendChild(document.createTextNode('你的想法會以 '));
      idText.appendChild(el('b', null, name));
      idText.appendChild(document.createTextNode(' 顯示'));
    }
    idRename.addEventListener('click', function () { idForm.hidden = false; idWho.hidden = true; idInput.focus(); });
    idCancel.addEventListener('click', function () { idForm.hidden = true; idWho.hidden = false; });
    idForm.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var nick = idInput.value.trim().slice(0, 40);
      lsSet(NICK_KEY, nick || null);
      if (!canSend()) { idForm.hidden = true; idWho.hidden = false; return; }
      idSave.disabled = true;
      mutateDoc(me.id, function (data) { data.nick = nick; }).then(function () {
        idSave.disabled = false; idForm.hidden = true; idWho.hidden = false;
      }, function (err) { idSave.disabled = false; setNote(errText(err, '改名'), true); });
    });
    idToggle.addEventListener('change', function () {
      expandAll = idToggle.checked;
      lsSet(OPEN_KEY, expandAll ? '1' : null);
      manual = {};
      Object.keys(blocks).forEach(function (q) { setOpen(q, expandAll || !!blocks[q].mineSaved); });
    });

    /* --- one block per question --- */
    cards.forEach(function (card, i) {
      var qid = card.id || ('q' + (i + 1));
      var body = card.querySelector('.qbody') || card;
      var root = el('div', 'qtalk');
      root.setAttribute('data-q', qid);

      var head = el('button', 'qtalk-head'); head.type = 'button'; head.setAttribute('aria-expanded', 'false');
      var headAvs = el('span', 'avs');
      var headText = el('span', 'qtalk-count', '載入中…');
      var chev = el('span', 'qtalk-chev'); chev.setAttribute('aria-hidden', 'true');
      head.appendChild(headAvs); head.appendChild(headText); head.appendChild(chev);
      var list = el('ol', 'qtalk-list'); list.hidden = true;
      var mine = el('div', 'qtalk-mine');

      /* composer */
      var form = el('form', 'qform'); form.hidden = true;
      var ta = el('textarea'); ta.id = 'ans-' + lecture + '-' + qid; ta.rows = 4;
      ta.placeholder = '寫下你對這題的想法。可以只寫一部分，也可以之後再改。';
      ta.setAttribute('aria-label', '你對第 ' + qNo(qid) + ' 題的想法');
      var row = el('div', 'qform-row');
      var save = el('button', 'copybtn small', '儲存'); save.type = 'submit';
      var cancel = el('button', 'ghostbtn small', '取消'); cancel.type = 'button'; cancel.hidden = true;
      var hint = el('span', 'copyhint', '按儲存後其他人才看得到 · Ctrl + Enter 儲存');
      var status = el('span', 'copyhint qform-status'); status.setAttribute('role', 'status');
      /* 用範本開始寫: paste the question's 作答範本 lines as plain text, then select the first blank */
      var tplLines = Array.prototype.map.call(card.querySelectorAll('.qstart .tpl'), function (p) {
        return p.textContent.replace(/\s+/g, ' ').trim();
      }).filter(Boolean);
      var useTpl = null;
      if (tplLines.length) {
        useTpl = el('button', 'ghostbtn small', '用範本開始寫'); useTpl.type = 'button';
        useTpl.addEventListener('click', function () {
          var cur = ta.value.replace(/\s+$/, '');
          var start = 0;
          if (cur.indexOf(tplLines[0]) < 0) {     /* add the template once; a second click only jumps to a blank */
            start = cur ? cur.length + 2 : 0;
            ta.value = (cur ? cur + '\n\n' : '') + tplLines.join('\n');
            ta.dispatchEvent(new Event('input', { bubbles: true }));
          }
          if (ta._fit) ta._fit();
          ta.focus();
          var pos = ta.value.indexOf('＿＿', start);
          if (pos >= 0 && ta.setSelectionRange) ta.setSelectionRange(pos, pos + 2);
        });
      }
      if (useTpl) ta.placeholder = '寫下你對這題的想法。可以只寫一部分，也可以之後再改。不知道怎麼開頭，就按「用範本開始寫」。';
      row.appendChild(save); row.appendChild(cancel); if (useTpl) row.appendChild(useTpl); row.appendChild(hint); row.appendChild(status);
      form.appendChild(ta); form.appendChild(row);
      var card_ = el('div', 'qtalk-card mine'); card_.hidden = true;

      mine.appendChild(card_); mine.appendChild(form);
      root.appendChild(head); root.appendChild(list); root.appendChild(mine);
      body.appendChild(root);

      var DRAFT_KEY = 'cs2680.draft.' + lecture + '.' + qid;
      var draft = lsGet(DRAFT_KEY);
      var b = blocks[qid] = { root: root, head: head, headAvs: headAvs, headText: headText, list: list, card: card_, form: form, ta: ta, save: save, cancel: cancel, status: status, draftKey: DRAFT_KEY, mineSaved: null, dirty: !!draft, editing: !!draft, others: 0 };
      if (draft) ta.value = draft;
      autoGrow(ta);

      var draftTimer = null;
      ta.addEventListener('input', function () {
        b.dirty = true;
        clearTimeout(draftTimer);
        draftTimer = setTimeout(function () { lsSet(DRAFT_KEY, ta.value || null); }, 400);
      });
      ta.addEventListener('keydown', function (ev) {
        if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') { ev.preventDefault(); form.requestSubmit ? form.requestSubmit() : save.click(); }
      });
      head.addEventListener('click', function () {
        var open = list.hidden;
        manual[qid] = open;
        setOpen(qid, open);
      });
      cancel.addEventListener('click', function () {
        b.editing = false; b.dirty = false;
        lsSet(DRAFT_KEY, null);
        ta.value = b.mineSaved ? b.mineSaved.text : '';
        if (ta._fit) ta._fit();
        renderMine(qid);
      });
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        if (!canSend()) return;
        var text = ta.value.trim();
        if (!text) { status.textContent = '還沒有內容。'; ta.focus(); return; }
        save.disabled = true; status.textContent = '儲存中…';
        var at = nowIso();
        mutateDoc(me.id, function (data) {
          var entry = data[lecture] || {};
          entry.answers = entry.answers || {};
          entry.answers[qid] = { text: text, at: at };
          entry.updatedAt = at;
          data[lecture] = entry;
          var nick = lsGet(NICK_KEY);
          if (nick && !data.nick) data.nick = nick;
        }).then(function () {
          lsSet(DRAFT_KEY, null);
          b.dirty = false; b.editing = false;
          save.disabled = false; status.textContent = '';
          setOpen(qid, true);
        }, function (err) {
          save.disabled = false;
          var code = err && err.code;
          if (code === 'invalid_argument') { canWrite = false; applyWriteState(); }
          status.textContent = errText(err, '儲存');
        });
      });
    });

    /* --- 基礎 tab: cross-link to the 進階 tab, a status line, and one 留言串 per 基礎題 --- */
    var bnote = el('p', 'sub-note'); bnote.hidden = true;
    if (basicPanel) {
      var cross = el('p', 'qset-cross');
      cross.appendChild(document.createTextNode('這一組只問 slides 講了什麼；每一題下面有留言串，隨手寫卡住的地方。讀書會的作答在'));
      var toAdv = el('button', 'linkbtn', '進階題'); toAdv.type = 'button';
      toAdv.addEventListener('click', function () { if (tabAdv) { tabAdv.click(); tabAdv.scrollIntoView({ block: 'start' }); } });
      cross.appendChild(toAdv);
      cross.appendChild(document.createTextNode('，每一題下面有討論區。'));
      var bLede = basicPanel.querySelector('.qset-lede');
      if (bLede && bLede.parentNode) bLede.parentNode.insertBefore(cross, bLede.nextSibling);
      else basicPanel.insertBefore(cross, basicPanel.firstChild);
      cross.parentNode.insertBefore(bnote, cross.nextSibling);
    }
    function setBNote(text, warn) { bnote.textContent = text || ''; bnote.hidden = !text; bnote.classList.toggle('warn', !!warn); }

    bcards.forEach(function (card, i) {
      var bid = card.id || ('b' + (i + 1));
      var body = card.querySelector('.qbody') || card;
      var root = el('div', 'qtalk qnotes');
      root.setAttribute('data-b', bid);

      var head = el('button', 'qtalk-head'); head.type = 'button'; head.setAttribute('aria-expanded', 'true');
      var headAvs = el('span', 'avs');
      var headText = el('span', 'qtalk-count', '載入中…');
      var chev = el('span', 'qtalk-chev'); chev.setAttribute('aria-hidden', 'true');
      head.appendChild(headAvs); head.appendChild(headText); head.appendChild(chev);
      var list = el('ol', 'qtalk-list');

      var form = el('form', 'qform qnote-form'); form.hidden = true;
      var ta = el('textarea'); ta.id = 'note-' + lecture + '-' + bid; ta.rows = 2;
      ta.placeholder = '留言：看 slides 時卡住的地方、跟參考答案不同的點、想再問的問題。';
      ta.setAttribute('aria-label', '對第 ' + qNo(bid) + ' 題基礎題的留言');
      var row = el('div', 'qform-row');
      var send = el('button', 'copybtn small', '送出'); send.type = 'submit';
      var hint = el('span', 'copyhint', '可以留很多則 · Ctrl + Enter 送出');
      var status = el('span', 'copyhint qform-status'); status.setAttribute('role', 'status');
      row.appendChild(send); row.appendChild(hint); row.appendChild(status);
      form.appendChild(ta); form.appendChild(row);

      root.appendChild(head); root.appendChild(list); root.appendChild(form);
      body.appendChild(root);

      var DRAFT_KEY = 'cs2680.ndraft.' + lecture + '.' + bid;
      var draft = lsGet(DRAFT_KEY);
      var nb = nblocks[bid] = { root: root, head: head, headAvs: headAvs, headText: headText, list: list, form: form, ta: ta, send: send, status: status, draftKey: DRAFT_KEY, open: true, count: 0 };
      if (draft) ta.value = draft;
      autoGrow(ta, 56);

      var draftTimer = null;
      ta.addEventListener('input', function () {
        clearTimeout(draftTimer);
        draftTimer = setTimeout(function () { lsSet(DRAFT_KEY, ta.value || null); }, 400);
      });
      ta.addEventListener('keydown', function (ev) {
        if ((ev.ctrlKey || ev.metaKey) && ev.key === 'Enter') { ev.preventDefault(); form.requestSubmit ? form.requestSubmit() : send.click(); }
      });
      head.addEventListener('click', function () { setNOpen(bid, list.hidden); });
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        if (!canSend()) return;
        var text = ta.value.trim();
        if (!text) { status.textContent = '還沒有內容。'; ta.focus(); return; }
        send.disabled = true; status.textContent = '送出中…';
        var at = nowIso();
        mutateDoc(me.id, function (data) {
          var entry = data[lecture] || {};
          entry.notes = entry.notes || {};
          if (!Array.isArray(entry.notes[bid])) entry.notes[bid] = [];
          entry.notes[bid].push({ id: newId(), text: text, at: at });
          entry.updatedAt = at;
          data[lecture] = entry;
          var nick = lsGet(NICK_KEY);
          if (nick && !data.nick) data.nick = nick;
        }).then(function () {
          lsSet(DRAFT_KEY, null);
          ta.value = ''; if (ta._fit) ta._fit();
          send.disabled = false; status.textContent = '';
          setNOpen(bid, true);
        }, function (err) {
          send.disabled = false;
          var code = err && err.code;
          if (code === 'invalid_argument') { canWrite = false; applyWriteState(); }
          status.textContent = errText(err, '送出');
        });
      });
    });
    function setNOpen(bid, open) {
      var nb = nblocks[bid];
      if (!nb) return;
      if (nb.count === 0) open = false;
      nb.open = open;
      nb.list.hidden = !open;
      nb.head.setAttribute('aria-expanded', open ? 'true' : 'false');
      nb.root.classList.toggle('is-open', open);
    }
    function renderNotes(profiles) {
      var st = statsOf(docs, lecture);
      bcards.forEach(function (card, i) {
        var bid = card.id || ('b' + (i + 1));
        var nb = nblocks[bid];
        var thread = noteThreadOf(docs, lecture, bid);
        var wasOpen = nb.open;
        nb.count = thread.length;
        nb.headAvs.textContent = '';
        var uids = [];
        thread.forEach(function (t) { if (uids.indexOf(t.uid) < 0) uids.push(t.uid); });
        var stack = avatarStack(uids, profiles, 5);
        while (stack.firstChild) nb.headAvs.appendChild(stack.firstChild);
        if (!thread.length) {
          nb.headText.textContent = canSend() ? '還沒有留言。卡住的地方、跟參考答案不同的點，寫在下面。' : '還沒有留言。';
          nb.head.disabled = true;
        } else {
          nb.headText.textContent = thread.length + ' 則留言';
          nb.head.disabled = false;
        }
        nb.list.textContent = '';
        thread.forEach(function (t) {
          var isMine = !!(me.id && t.uid === me.id);
          var li = el('li', 'qtalk-card' + (isMine ? ' mine' : ''));
          li.appendChild(cardHead(t.uid, profiles, t, isMine));
          li.appendChild(el('div', 'qtalk-text', t.text));
          if (isMine || me.isOwner) {
            var act = el('div', 'actions');
            act.appendChild(confirmButton(isMine ? '刪除' : '刪除（主持人）', function (btn) {
              mutateDoc(t.uid, function (data) {
                var entry = data[lecture]; if (!entry || !entry.notes || !Array.isArray(entry.notes[bid])) return;
                entry.notes[bid] = entry.notes[bid].filter(function (n) { return !n || n.id !== t.id; });
                if (!entry.notes[bid].length) delete entry.notes[bid];
                entry.updatedAt = nowIso();
              }).then(null, function (err) { btn.disabled = false; nb.status.textContent = errText(err, '刪除'); });
            }, isMine ? undefined : 'quiet'));
            li.appendChild(act);
          }
          nb.list.appendChild(li);
        });
        setNOpen(bid, wasOpen);
      });
      /* counts on the two tab labels */
      if (tabBasic && tabBasic.querySelector('span')) tabBasic.querySelector('span').textContent = tabBasicBase + (st.notes ? ' · ' + st.notes + ' 則留言' : '');
      if (tabAdv && tabAdv.querySelector('span')) tabAdv.querySelector('span').textContent = tabAdvBase + (st.writers ? ' · ' + st.writers + ' 人寫了' : '');
    }

    function setOpen(qid, open) {
      var b = blocks[qid];
      if (!b) return;
      if (b.others === 0) open = false;
      b.list.hidden = !open;
      b.head.setAttribute('aria-expanded', open ? 'true' : 'false');
      b.root.classList.toggle('is-open', open);
    }
    function openComposer(qid) {
      var b = blocks[qid];
      b.editing = true;
      if (!b.dirty && b.mineSaved) b.ta.value = b.mineSaved.text;
      renderMine(qid);
      if (b.ta._fit) b.ta._fit();
      b.ta.focus();
    }
    /* the composer stays visible until an answer is saved: an open textarea invites more than a button */
    function renderMine(qid) {
      var b = blocks[qid];
      var writable = canSend();
      b.form.hidden = !(writable && (b.editing || !b.mineSaved));
      b.card.hidden = !(b.mineSaved && !b.editing);
      b.cancel.hidden = !(b.mineSaved || b.dirty);
      b.cancel.textContent = b.mineSaved ? '取消' : '清除';
    }
    function applyWriteState() {
      Object.keys(blocks).forEach(renderMine);
      Object.keys(nblocks).forEach(function (b) { nblocks[b].form.hidden = !canSend(); });
      if (formEl) {
        if (sendBtn) sendBtn.disabled = !canSend();
        if (textEl) textEl.disabled = !canSend();
      }
    }

    /* --- render from the latest snapshot --- */
    function render() {
      var ids = [];
      docs.forEach(function (s) { ids.push(s.id); });
      if (me.id) ids.push(me.id);
      profilesFor(ids).then(function (profiles) {
        var myProfile = me.id ? profiles[me.id] : null;
        if (me.id) {
          if (me.avatarUrl) { idAv.src = me.avatarUrl; idAv.hidden = false; }
          var myDoc = null;
          docs.forEach(function (s) { if (s.id === me.id) myDoc = s.data() || {}; });
          var shown = nameOf(myDoc, myProfile);
          if (shown === '成員' && me.name) shown = me.name;
          setIdText(shown);
          idRename.hidden = !canSend();
          if (!idInput.value) idInput.value = (myDoc && myDoc.nick) || lsGet(NICK_KEY) || '';
        }

        /* per question */
        cards.forEach(function (card, i) {
          var qid = card.id || ('q' + (i + 1));
          var b = blocks[qid];
          var thread = threadOf(docs, lecture, qid);
          var mineE = null;
          var others = thread.filter(function (t) { if (me.id && t.uid === me.id) { mineE = t; return false; } return true; });
          b.others = others.length;

          /* my card */
          var hadSaved = !!b.mineSaved;
          b.mineSaved = mineE ? { text: mineE.text, at: mineE.at } : null;
          if (!prefilled && mineE && !b.dirty && !b.ta.value) { b.ta.value = mineE.text; if (b.ta._fit) b.ta._fit(); }
          b.card.textContent = '';
          if (mineE) {
            b.card.appendChild(cardHead(me.id, profiles, mineE, true));
            b.card.appendChild(el('div', 'qtalk-text', mineE.text));
            var act = el('div', 'actions');
            var edit = el('button', 'ghostbtn small', '編輯'); edit.type = 'button';
            edit.addEventListener('click', function () { openComposer(qid); });
            act.appendChild(edit);
            act.appendChild(confirmButton('刪除', function (btn) {
              mutateDoc(me.id, function (data) {
                var entry = data[lecture]; if (!entry || !entry.answers) return;
                delete entry.answers[qid];
                entry.updatedAt = nowIso();
              }).then(function () { b.ta.value = ''; b.dirty = false; lsSet(b.draftKey, null); if (b.ta._fit) b.ta._fit(); }, function (err) { btn.disabled = false; b.status.textContent = errText(err, '刪除'); });
            }));
            b.card.appendChild(act);
          }
          if (mineE && !hadSaved && !b.dirty) b.editing = false;
          renderMine(qid);

          /* others */
          b.headAvs.textContent = '';
          var stack = avatarStack(others.map(function (t) { return t.uid; }), profiles, 5);
          while (stack.firstChild) b.headAvs.appendChild(stack.firstChild);
          if (!others.length) {
            b.headText.textContent = mineE ? '還沒有其他人寫。' : '還沒有人寫想法。你先來？';
            b.head.disabled = true;
          } else {
            b.headText.textContent = others.length + ' 人寫了想法';
            b.head.disabled = false;
          }
          b.list.textContent = '';
          others.forEach(function (t) {
            var li = el('li', 'qtalk-card');
            li.appendChild(cardHead(t.uid, profiles, t, false));
            li.appendChild(el('div', 'qtalk-text', t.text));
            if (me.isOwner) {
              var act2 = el('div', 'actions');
              act2.appendChild(confirmButton('刪除（主持人）', function (btn) {
                mutateDoc(t.uid, function (data) {
                  var entry = data[lecture]; if (!entry || !entry.answers) return;
                  delete entry.answers[qid];
                  entry.updatedAt = nowIso();
                }).then(null, function (err) { btn.disabled = false; setNote(errText(err, '刪除'), true); });
              }, 'quiet'));
              li.appendChild(act2);
            }
            b.list.appendChild(li);
          });
          var open = manual[qid] !== undefined ? manual[qid] : (expandAll || !!mineE);
          setOpen(qid, open);
        });
        prefilled = true;

        /* 基礎題留言串 + tab counts */
        renderNotes(profiles);

        /* section 7 */
        renderSummary(profiles);
      });
    }
    function cardHead(uid, profiles, t, isMine) {
      var h = el('div', 'qtalk-who');
      var p = profiles[uid];
      var data = null;
      docs.forEach(function (s) { if (s.id === uid) data = s.data() || {}; });
      var img = avatarImg(p, 'avatar');
      if (isMine && img.hidden && me.avatarUrl) { img.src = me.avatarUrl; img.hidden = false; }
      h.appendChild(img);
      var nm = nameOf(data, p);
      if (isMine && nm === '成員' && me.name) nm = me.name;
      h.appendChild(el('b', 'who', nm));
      if (isMine) h.appendChild(el('span', 'mine-tag', '你'));
      h.appendChild(el('span', 'when', fmtTime(t.at)));
      return h;
    }

    function renderSummary(profiles) {
      var st = statsOf(docs, lecture);
      if (sumEl) {
        sumEl.textContent = '';
        var lead = el('p', 'talk-lead');
        if (!st.people.length) {
          lead.textContent = '這堂還沒有人留下想法。到第 5 段：基礎題下面可以留言，進階題下面可以寫想法。';
        } else {
          lead.appendChild(el('b', null, st.people.length + ' 人'));
          lead.appendChild(document.createTextNode(' 參與，共 '));
          if (st.total) {
            lead.appendChild(el('b', null, st.total + ' 則'));
            lead.appendChild(document.createTextNode(' 進階題想法'));
          }
          if (st.notes) {
            if (st.total) lead.appendChild(document.createTextNode('、'));
            lead.appendChild(el('b', null, st.notes + ' 則'));
            lead.appendChild(document.createTextNode(' 基礎題留言'));
          }
          if (!st.total && !st.notes) lead.appendChild(document.createTextNode('整體補充或附件'));
          lead.appendChild(document.createTextNode('。'));
        }
        sumEl.appendChild(lead);
        var chips = el('div', 'qchips');
        cards.forEach(function (card, i) {
          var qid = card.id || ('q' + (i + 1));
          var n = st.perQ[qid] || 0;
          var a = el('a', 'qchip' + (n ? '' : ' is-empty'));
          a.href = '#' + qid;
          a.appendChild(el('span', 'qchip-q', 'Q' + qNo(qid)));
          a.appendChild(el('span', 'qchip-n', n ? n + ' 人' : '—'));
          var qt = card.querySelector('.qtext');
          if (qt) a.title = qt.textContent.trim();
          chips.appendChild(a);
        });
        sumEl.appendChild(chips);
      }
      if (listEl) {
        listEl.textContent = '';
        if (countEl) countEl.textContent = st.people.length ? '（' + st.people.length + ' 人）' : '';
        if (!st.people.length) { listEl.appendChild(el('li', 'empty', '還沒有人。')); }
        st.people.forEach(function (p) {
          var li = el('li', 'person');
          var det = el('details');
          var sum = el('summary');
          var isMe = me.id && p.uid === me.id;
          var img = avatarImg(profiles[p.uid], 'avatar');
          if (isMe && img.hidden && me.avatarUrl) { img.src = me.avatarUrl; img.hidden = false; }
          sum.appendChild(img);
          var nm = nameOf(p.data, profiles[p.uid]);
          if (isMe && nm === '成員' && me.name) nm = me.name;
          sum.appendChild(el('b', 'who', nm));
          if (isMe) sum.appendChild(el('span', 'mine-tag', '你'));
          var qs = el('span', 'person-qs');
          Object.keys(p.answers).sort(function (a, b2) { return qNo(a) - qNo(b2); }).forEach(function (q) { qs.appendChild(el('span', 'qdot', 'Q' + qNo(q))); });
          var pn = noteCount(p.entry);
          if (pn) qs.appendChild(el('span', 'qdot alt', pn + ' 留言'));
          if (hasOverall(p.entry)) qs.appendChild(el('span', 'qdot alt', '補充'));
          if (p.files.length) qs.appendChild(el('span', 'qdot alt', p.files.length + ' 附件'));
          sum.appendChild(qs);
          sum.appendChild(el('span', 'when', fmtTime(p.latest)));
          det.appendChild(sum);
          var bodyEl = el('div', 'person-body');
          Object.keys(p.answers).sort(function (a, b2) { return qNo(a) - qNo(b2); }).forEach(function (q) {
            var blk = el('div', 'person-ans');
            var card = document.getElementById(q);
            var qt = card ? card.querySelector('.qtext') : null;
            var h = el('a', 'person-q'); h.href = '#' + q;
            h.appendChild(el('span', 'qchip-q', 'Q' + qNo(q)));
            h.appendChild(document.createTextNode(' ' + (qt ? excerpt(qt.textContent, 60) : '')));
            blk.appendChild(h);
            blk.appendChild(el('div', 'qtalk-text', p.answers[q].text));
            bodyEl.appendChild(blk);
          });
          Object.keys(p.notes).sort(function (a, b2) { return qNo(a) - qNo(b2); }).forEach(function (b) {
            var blk3 = el('div', 'person-ans');
            var bcard = document.getElementById(b);
            var bt = bcard ? bcard.querySelector('.qtext') : null;
            var h3 = el('a', 'person-q'); h3.href = '#' + b;
            h3.appendChild(el('span', 'qchip-q', 'B' + qNo(b) + ' 留言'));
            h3.appendChild(document.createTextNode(' ' + (bt ? excerpt(bt.textContent, 60) : '')));
            blk3.appendChild(h3);
            p.notes[b].forEach(function (n) {
              var line = el('div', 'qtalk-text');
              line.appendChild(el('span', 'when', fmtTime(n.at) + '　'));
              line.appendChild(document.createTextNode(n.text));
              blk3.appendChild(line);
            });
            bodyEl.appendChild(blk3);
          });
          if (hasOverall(p.entry)) {
            var blk2 = el('div', 'person-ans');
            blk2.appendChild(el('span', 'person-q', '整體補充'));
            blk2.appendChild(el('div', 'qtalk-text', p.entry.text));
            bodyEl.appendChild(blk2);
          }
          if (p.files.length) bodyEl.appendChild(fileList(p.files));
          if (me.isOwner && !isMe) {
            var act = el('div', 'actions');
            act.appendChild(confirmButton('刪除這個人這堂的全部（主持人）', function (btn) {
              mutateDoc(p.uid, function (data) { delete data[lecture]; }).then(null, function (err) { btn.disabled = false; setNote(errText(err, '刪除'), true); });
            }, 'quiet'));
            bodyEl.appendChild(act);
          }
          det.appendChild(bodyEl);
          li.appendChild(det);
          listEl.appendChild(li);
        });
        /* my overall text + files into the form, once */
        if (!overallPrefilled && me.id) {
          overallPrefilled = true;
          var mineP = st.people.filter(function (x) { return x.uid === me.id; })[0];
          if (mineP) {
            if (!overallDirty && textEl && !textEl.value && hasOverall(mineP.entry)) textEl.value = mineP.entry.text;
            pendingFiles = clone(mineP.files);
            renderAttach();
          }
        }
      }
    }
    var overallPrefilled = false;

    /* --- section 7 form: 整體補充 + 附件 --- */
    function renderAttach() {
      if (!attachEl) return;
      attachEl.textContent = '';
      pendingFiles.forEach(function (f, i) {
        var li = el('li');
        var a = el('a', null, f.name + (f.size ? '（' + fmtSize(f.size) + '）' : ''));
        a.href = blobUrl(f.id); a.target = '_blank'; a.rel = 'noopener';
        li.appendChild(a);
        var rm = el('button', 'ghostbtn small', '移除'); rm.type = 'button';
        rm.addEventListener('click', function () { pendingFiles.splice(i, 1); renderAttach(); if (statusEl) statusEl.textContent = '按「儲存」才會生效。'; });
        li.appendChild(rm);
        attachEl.appendChild(li);
      });
    }
    if (textEl) {
      var od = lsGet(OVERALL_KEY);
      if (od) { textEl.value = od; overallDirty = true; }
      var oTimer = null;
      textEl.addEventListener('input', function () {
        overallDirty = true;
        clearTimeout(oTimer);
        oTimer = setTimeout(function () { lsSet(OVERALL_KEY, textEl.value || null); }, 400);
      });
    }
    var uploading = false;
    if (fileEl) {
      fileEl.addEventListener('change', function () {
        var file = fileEl.files && fileEl.files[0];
        if (!file || !assets) return;
        var type = typeFor(file);
        if (!type) { statusEl.textContent = '這種檔案格式不能上傳。請用 PDF、圖片、Markdown、txt、csv 或 json。'; fileEl.value = ''; return; }
        if (file.size > 20 * 1024 * 1024) { statusEl.textContent = '檔案超過 20 MB。'; fileEl.value = ''; return; }
        uploading = true;
        if (sendBtn) sendBtn.disabled = true;
        statusEl.textContent = '上傳附件中…';
        assets.upload(file, { type: type }).then(function (res) {
          pendingFiles.push({ id: res.id, name: file.name, type: res.contentType, size: res.sizeBytes });
          renderAttach();
          statusEl.textContent = '附件已上傳。按「儲存」才會留在你的討論裡。';
        }, function (err) {
          var code = err && err.code;
          statusEl.textContent = code === 'too_large' ? '檔案太大。' : code === 'unsupported_type' ? '這種檔案格式不能上傳。'
            : code === 'quota_or_state' ? '站台的附件空間已滿，請改貼文字。' : code === 'rate_limited' ? '上傳太頻繁，稍等再試。' : '上傳失敗（' + (code || '未知錯誤') + '）。';
        }).then(function () {
          uploading = false;
          fileEl.value = '';
          if (sendBtn) sendBtn.disabled = !canSend();
        });
      });
    }
    if (formEl) {
      formEl.addEventListener('submit', function (ev) {
        ev.preventDefault();
        if (!canSend() || uploading) return;
        var text = textEl ? textEl.value.trim() : '';
        sendBtn.disabled = true;
        statusEl.textContent = '儲存中…';
        var at = nowIso();
        mutateDoc(me.id, function (data) {
          var entry = data[lecture] || {};
          entry.text = text;
          entry.files = pendingFiles.slice();
          entry.updatedAt = at;
          data[lecture] = entry;
        }).then(function () {
          lsSet(OVERALL_KEY, null);
          overallDirty = false;
          statusEl.textContent = '已儲存 ' + fmtTime(at) + '。';
          sendBtn.disabled = !canSend();
        }, function (err) {
          var code = err && err.code;
          if (code === 'invalid_argument') { canWrite = false; applyWriteState(); setNote(errText(err, '儲存'), true); }
          statusEl.textContent = errText(err, '儲存');
          sendBtn.disabled = false;
        });
      });
    }
    if (copyAllBtn) {
      copyAllBtn.addEventListener('click', function () {
        var who = (me.name || '');
        var lines = ['CS2680 ' + lecLabel(lecture) + ' 討論' + (who ? ' · ' + who : ''), ''];
        cards.forEach(function (card, i) {
          var qid = card.id || ('q' + (i + 1));
          var b = blocks[qid];
          var text = (b.ta.value || (b.mineSaved && b.mineSaved.text) || '').trim();
          if (!text) return;
          var qt = card.querySelector('.qtext');
          lines.push('Q' + qNo(qid) + '. ' + (qt ? qt.textContent.trim() : ''), text, '');
        });
        var ov = textEl ? textEl.value.trim() : '';
        if (ov) lines.push('整體補充', ov, '');
        copyText(lines.join('\n').trim(), copyAllBtn, '已複製');
      });
    }

    /* --- light up once the capabilities answer --- */
    if (sendBtn) sendBtn.disabled = true;
    setNote('連線中…');
    ready.then(function () {
      if (!db) {
        setNote('這個畫面連不到共用資料庫，所以看不到也寫不了討論。請在 claude.ai 登入後重新開這一頁。', true);
        setBNote('這個畫面連不到共用資料庫，看不到也寫不了留言。請在 claude.ai 登入後重新開這一頁。', true);
        idText.textContent = '未連線';
        Object.keys(blocks).forEach(function (q) { blocks[q].headText.textContent = '登入後可以看到大家的想法。'; blocks[q].head.disabled = true; });
        Object.keys(nblocks).forEach(function (b) { nblocks[b].headText.textContent = '登入後可以看到留言。'; nblocks[b].head.disabled = true; });
        if (formEl) formEl.hidden = true;
        return;
      }
      if (!me.id) {
        setNote('請先登入 claude.ai，再重新開這一頁，就可以寫想法。', true);
        setBNote('請先登入 claude.ai，再重新開這一頁，就可以留言。', true);
        idText.textContent = '尚未登入';
      } else if (canWrite === false) {
        setNote('你目前是唯讀身份，可以看大家的想法，但不能寫。請主持人在分享設定把你加為 Contributor。', true);
        setBNote('你目前是唯讀身份，可以看留言，但不能寫。請主持人在分享設定把你加為 Contributor。', true);
      } else {
        setNote('');
        setBNote('');
      }
      applyWriteState();
      subscribe(render, function (err) {
        var code = err && err.code;
        setNote(code === 'revoked' ? '連線已中斷，請重新整理。' : '讀取失敗（' + (code || '未知錯誤') + '），請重新整理。', true);
      });
      if (me.id && canWrite !== false) {
        useCap('assets').then(function (a) {
          assets = a;
          if (assets && fileRow) fileRow.hidden = false;
        });
      }
    });
  }

  /* ========================================================================
     submissions.html：討論總覽
     ======================================================================== */
  if (isOverview) {
    var bnote = $('sub-note');
    var pillsEl = $('lec-pills');
    var feedEl = $('sub-feed');
    var gridWrap = $('sub-grid');
    var exportBtn = $('sub-export');
    var upcomingEl = $('upcoming');
    var current = null;                 // lecture key shown in the reader
    var questionCache = {};             // key -> Promise<[{id, tag, text}]>

    function bnoteSet(text, warn) {
      if (!bnote) return;
      bnote.textContent = text || '';
      bnote.hidden = !text;
      bnote.classList.toggle('warn', !!warn);
    }
    /* question text comes from the lecture page itself, so nothing is duplicated */
    function questionsOf(key) {
      if (!questionCache[key]) {
        questionCache[key] = fetch(key + '.html', { credentials: 'same-origin' }).then(function (r) { return r.ok ? r.text() : ''; }).then(function (html) {
          var out = [];
          if (!html) return out;
          var doc = new DOMParser().parseFromString(html, 'text/html');
          var items = doc.querySelectorAll('#qset-adv .qlist > li.dq');
          for (var i = 0; i < items.length; i++) {
            var li = items[i];
            var tag = li.querySelector('.qtag');
            var text = li.querySelector('.qtext');
            out.push({ id: li.id || ('q' + (i + 1)), tag: tag ? tag.textContent.replace(/\s+/g, ' ').trim() : '', text: text ? text.textContent.trim() : '' });
          }
          var bitems = doc.querySelectorAll('#qset-basic .qlist > li.bq');
          for (var j = 0; j < bitems.length; j++) {
            var bli = bitems[j];
            var btag = bli.querySelector('.qtag');
            var btext = bli.querySelector('.qtext');
            out.push({ id: bli.id || ('b' + (j + 1)), tag: btag ? btag.textContent.replace(/\s+/g, ' ').trim() : '', text: btext ? btext.textContent.trim() : '', basic: true });
          }
          return out;
        }).catch(function () { return []; });
      }
      return questionCache[key];
    }
    /* 基礎題 rows for the reader and the export: every 基礎題 that has at least one note */
    function basicRows(key, qs) {
      var byId = {};
      qs.forEach(function (q) { if (q.basic) byId[q.id] = q; });
      return notedQuestions(docs, key).map(function (b) { return byId[b] || { id: b, tag: '', text: '', basic: true }; });
    }
    function questionList(key, docsNow) {
      /* questions seen in the data, in case the page could not be fetched */
      var seen = {};
      docsNow.forEach(function (s) { var d = s.data() || {}; Object.keys(answersOf(d[key])).forEach(function (q) { seen[q] = true; }); });
      return Object.keys(seen).sort(function (a, b) { return qNo(a) - qNo(b); });
    }

    if (upcomingEl) {
      upcomingEl.textContent = '';
      UPCOMING.forEach(function (u) {
        var li = el('li');
        li.appendChild(el('span', 'd', u[0]));
        li.appendChild(el('span', 'w', u[1]));
        upcomingEl.appendChild(li);
      });
    }

    function pickDefault() {
      var h = (location.hash || '').replace('#', '');
      if (TITLE[h]) return h;
      var best = null, bestAt = '';
      LECTURES.forEach(function (l) {
        docs.forEach(function (s) {
          var d = s.data() || {};
          var t = latestOf(d[l[0]]);
          if (hasAnything(d[l[0]]) && t > bestAt) { bestAt = t; best = l[0]; }
        });
      });
      return best || LECTURES[0][0];
    }
    function show(key, push) {
      if (!TITLE[key]) return Promise.resolve();
      current = key;
      if (push) { try { history.replaceState(null, '', '#' + key); } catch (e) { /* ignore */ } }
      return renderAll();
    }
    window.addEventListener('hashchange', function () {
      var h = (location.hash || '').replace('#', '');
      if (TITLE[h] && h !== current) show(h, false);
    });

    function renderPills(profiles) {
      if (!pillsEl) return;
      pillsEl.textContent = '';
      LECTURES.forEach(function (l) {
        var st = statsOf(docs, l[0]);
        var b = el('button', 'lecpill' + (l[0] === current ? ' is-on' : '') + (st.people.length ? '' : ' is-empty'));
        b.type = 'button';
        b.setAttribute('aria-pressed', l[0] === current ? 'true' : 'false');
        b.appendChild(el('span', 'lecpill-no', 'L' + lecNo(l[0])));
        b.appendChild(el('span', 'lecpill-t', l[1]));
        b.appendChild(el('span', 'lecpill-n', st.people.length ? st.people.length + ' 人 · ' + st.total + ' 則' + (st.notes ? ' · ' + st.notes + ' 留言' : '') : '還沒有討論'));
        b.addEventListener('click', function () { show(l[0], true); });
        pillsEl.appendChild(b);
      });
      var more = el('div', 'lecpill soon');
      more.appendChild(el('span', 'lecpill-no', 'Part II'));
      more.appendChild(el('span', 'lecpill-t', '10/19 起陸續加入'));
      more.appendChild(el('span', 'lecpill-n', UPCOMING.length + ' 堂待公開'));
      pillsEl.appendChild(more);
    }

    function renderReader(profiles) {
      var key = current;
      var st = statsOf(docs, key);
      readerEl.textContent = '';
      var head = el('header', 'reader-head');
      var h = el('h3');
      h.appendChild(el('span', 'reader-no', 'L' + lecNo(key)));
      h.appendChild(document.createTextNode(' ' + TITLE[key]));
      head.appendChild(h);
      var metaRow = el('p', 'reader-meta');
      metaRow.appendChild(document.createTextNode(st.people.length ? st.people.length + ' 人參與 · ' + st.total + ' 則想法' + (st.notes ? ' · ' + st.notes + ' 則留言' : '') : '這堂還沒有人留下想法。'));
      metaRow.appendChild(document.createTextNode(' · '));
      var toLec = el('a', null, '到這堂的進階題 →'); toLec.href = key + '.html#qset-adv';
      metaRow.appendChild(toLec);
      head.appendChild(metaRow);
      var tools = el('div', 'copyrow reader-tools');
      var copyBtn = el('button', 'ghostbtn', '複製這堂的討論'); copyBtn.type = 'button';
      copyBtn.addEventListener('click', function () { lectureMarkdown(key).then(function (md) { copyText(md, copyBtn, '已複製'); }); });
      tools.appendChild(copyBtn);
      tools.appendChild(el('span', 'copyhint', '純文字，方便貼到群組。'));
      head.appendChild(tools);
      readerEl.appendChild(head);

      var body = el('div', 'reader-body');
      readerEl.appendChild(body);
      body.appendChild(el('p', 'empty', '載入題目中…'));

      return questionsOf(key).then(function (all) {
        if (key !== current) return;
        body.textContent = '';
        var brows = basicRows(key, all);
        var qs = all.filter(function (q) { return !q.basic; });
        var ids = qs.map(function (q) { return q.id; });
        questionList(key, docs).forEach(function (q) { if (ids.indexOf(q) < 0) { qs.push({ id: q, tag: '', text: '' }); ids.push(q); } });
        qs.sort(function (a, b) { return qNo(a.id) - qNo(b.id); });
        if (!qs.length) { body.appendChild(el('p', 'empty', '讀不到這堂的題目。')); }
        qs.forEach(function (q) {
          var art = el('article', 'rq');
          art.id = 'r-' + key + '-' + q.id;
          var qh = el('header', 'rq-head');
          var tag = el('p', 'qtag');
          tag.appendChild(el('span', 'qchip-q', 'Q' + qNo(q.id)));
          if (q.tag) tag.appendChild(document.createTextNode(' ' + q.tag));
          qh.appendChild(tag);
          var qa = el('a', 'rq-text'); qa.href = key + '.html#' + q.id;
          qa.textContent = q.text || ('第 ' + qNo(q.id) + ' 題');
          qh.appendChild(qa);
          art.appendChild(qh);
          var thread = threadOf(docs, key, q.id);
          if (!thread.length) {
            art.appendChild(el('p', 'rq-empty', '還沒有人寫這題。'));
          } else {
            var ol = el('ol', 'qtalk-list is-flat');
            thread.forEach(function (t) {
              var li = el('li', 'qtalk-card');
              var who = el('div', 'qtalk-who');
              who.appendChild(avatarImg(profiles[t.uid], 'avatar'));
              who.appendChild(el('b', 'who', nameOf(t.data, profiles[t.uid])));
              if (me.id && t.uid === me.id) who.appendChild(el('span', 'mine-tag', '你'));
              who.appendChild(el('span', 'when', fmtTime(t.at)));
              li.appendChild(who);
              li.appendChild(el('div', 'qtalk-text', t.text));
              ol.appendChild(li);
            });
            art.appendChild(ol);
          }
          body.appendChild(art);
        });
        /* 基礎題留言：只列有人留言的題 */
        if (brows.length) {
          var bsec = el('article', 'rq rq-basic');
          var bh = el('header', 'rq-head');
          bh.appendChild(el('p', 'qtag', '基礎題留言'));
          var bl = el('p', 'rq-lede', '看 slides 時卡住的地方、跟參考答案不同的點。讀書會開頭先掃一遍，把共同卡住的地方挑出來。');
          bh.appendChild(bl);
          bsec.appendChild(bh);
          brows.forEach(function (q) {
            var bart = el('div', 'rq-b');
            bart.id = 'r-' + key + '-' + q.id;
            var qh = el('header', 'rq-head');
            var tag = el('p', 'qtag');
            tag.appendChild(el('span', 'qchip-q', 'B' + qNo(q.id)));
            if (q.tag) tag.appendChild(document.createTextNode(' ' + q.tag));
            qh.appendChild(tag);
            var qa = el('a', 'rq-text'); qa.href = key + '.html#' + q.id;
            qa.textContent = q.text || ('第 ' + qNo(q.id) + ' 題');
            qh.appendChild(qa);
            bart.appendChild(qh);
            var ol = el('ol', 'qtalk-list');
            noteThreadOf(docs, key, q.id).forEach(function (t) {
              var li = el('li', 'qtalk-card');
              var who = el('div', 'qtalk-who');
              who.appendChild(avatarImg(profiles[t.uid], 'avatar'));
              who.appendChild(el('b', 'who', nameOf(t.data, profiles[t.uid])));
              if (me.id && t.uid === me.id) who.appendChild(el('span', 'mine-tag', '你'));
              who.appendChild(el('span', 'when', fmtTime(t.at)));
              li.appendChild(who);
              li.appendChild(el('div', 'qtalk-text', t.text));
              ol.appendChild(li);
            });
            bart.appendChild(ol);
            bsec.appendChild(bart);
          });
          body.appendChild(bsec);
        }
        /* 整體補充與附件 */
        var extras = st.people.filter(function (p) { return hasOverall(p.entry) || p.files.length; });
        if (extras.length) {
          var art2 = el('article', 'rq');
          var qh2 = el('header', 'rq-head');
          qh2.appendChild(el('p', 'qtag', '整體補充與附件'));
          art2.appendChild(qh2);
          var ol2 = el('ol', 'qtalk-list is-flat');
          extras.forEach(function (p) {
            var li = el('li', 'qtalk-card');
            var who = el('div', 'qtalk-who');
            who.appendChild(avatarImg(profiles[p.uid], 'avatar'));
            who.appendChild(el('b', 'who', nameOf(p.data, profiles[p.uid])));
            who.appendChild(el('span', 'when', fmtTime(p.entry.updatedAt)));
            li.appendChild(who);
            if (hasOverall(p.entry)) li.appendChild(el('div', 'qtalk-text', p.entry.text));
            if (p.files.length) li.appendChild(fileList(p.files));
            ol2.appendChild(li);
          });
          art2.appendChild(ol2);
          body.appendChild(art2);
        }
      });
    }

    function renderFeed(profiles) {
      if (!feedEl) return;
      var items = [];
      docs.forEach(function (s) {
        var d = s.data() || {};
        LECTURES.forEach(function (l) {
          var e = d[l[0]];
          var ans = answersOf(e);
          Object.keys(ans).forEach(function (q) { items.push({ uid: s.id, data: d, key: l[0], q: q, at: ans[q].at || '', text: ans[q].text }); });
          var ns = notesOf(e);
          Object.keys(ns).forEach(function (b) { ns[b].forEach(function (n) { items.push({ uid: s.id, data: d, key: l[0], q: b, note: true, at: n.at || '', text: n.text }); }); });
          if (hasOverall(e)) items.push({ uid: s.id, data: d, key: l[0], q: null, at: e.updatedAt || '', text: e.text });
        });
      });
      items.sort(function (a, b) { return b.at.localeCompare(a.at); });
      feedEl.textContent = '';
      if (!items.length) { feedEl.appendChild(el('li', 'empty', '還沒有任何想法。第一則會出現在這裡。')); return; }
      items.slice(0, 15).forEach(function (it) {
        var li = el('li', 'feed-item');
        var top = el('div', 'feed-top');
        top.appendChild(avatarImg(profiles[it.uid], 'avatar'));
        top.appendChild(el('b', 'who', nameOf(it.data, profiles[it.uid])));
        var where = el('a', 'feed-where');
        where.href = it.key + '.html#' + (it.q || 's-submit');
        where.textContent = 'L' + lecNo(it.key) + (it.note ? ' · B' + qNo(it.q) + ' 留言' : it.q ? ' · Q' + qNo(it.q) : ' · 整體補充');
        top.appendChild(where);
        top.appendChild(el('span', 'when', fmtTime(it.at)));
        li.appendChild(top);
        var ex = el('p', 'feed-text', excerpt(it.text, 140));
        li.appendChild(ex);
        li.addEventListener('click', function (ev) {
          if (ev.target.closest && ev.target.closest('a')) return;
          show(it.key, true).then(function () {
            var target = document.getElementById('r-' + it.key + '-' + (it.q || ''));
            (target || readerEl).scrollIntoView({ block: 'start' });
          });
        });
        feedEl.appendChild(li);
      });
    }

    function renderGrid(profiles) {
      if (!gridWrap) return;
      gridWrap.textContent = '';
      var rows = docs.map(function (s) {
        var d = s.data() || {};
        var cells = {}, any = false, latest = '';
        LECTURES.forEach(function (l) {
          var e = d[l[0]];
          var n = Object.keys(answersOf(e)).length;
          var nn = noteCount(e);
          var extra = hasOverall(e) || filesOf(e).length;
          if (n || nn || extra) { any = true; cells[l[0]] = { n: n, nn: nn, extra: extra }; var t = latestOf(e); if (t > latest) latest = t; }
        });
        return { uid: s.id, name: nameOf(d, profiles[s.id]), cells: cells, any: any, latest: latest };
      }).filter(function (r) { return r.any; });
      rows.sort(function (a, b) { return b.latest.localeCompare(a.latest); });
      if (!rows.length) { gridWrap.appendChild(el('p', 'empty', '還沒有人留下想法。')); return; }
      var table = el('table', 'board');
      var thead = el('thead'); var trh = el('tr');
      var th0 = el('th', null, '成員'); th0.scope = 'col'; trh.appendChild(th0);
      LECTURES.forEach(function (l) {
        var th = el('th'); th.scope = 'col';
        var a = el('a', null, 'L' + lecNo(l[0])); a.href = '#' + l[0]; a.title = l[1];
        a.addEventListener('click', function (ev) { ev.preventDefault(); show(l[0], true); readerEl.scrollIntoView({ block: 'start' }); });
        th.appendChild(a); trh.appendChild(th);
      });
      thead.appendChild(trh); table.appendChild(thead);
      var tbody = el('tbody');
      rows.forEach(function (r) {
        var tr = el('tr');
        var th = el('th'); th.scope = 'row';
        th.appendChild(avatarImg(profiles[r.uid], 'avatar'));
        th.appendChild(document.createTextNode(r.name + (me.id === r.uid ? '（你）' : '')));
        tr.appendChild(th);
        LECTURES.forEach(function (l) {
          var td = el('td');
          var c = r.cells[l[0]];
          if (c) {
            var a = el('a', 'cell', c.n ? String(c.n) + (c.nn ? '+' : '') : c.nn ? '+' : '·');
            a.href = '#' + l[0];
            var parts = [];
            if (c.n) parts.push(c.n + ' 題進階題');
            if (c.nn) parts.push(c.nn + ' 則留言');
            if (c.extra) parts.push('補充或附件');
            a.title = parts.join(' + ');
            a.addEventListener('click', function (ev) { ev.preventDefault(); show(l[0], true); readerEl.scrollIntoView({ block: 'start' }); });
            td.appendChild(a);
          } else td.appendChild(el('span', 'no', '–'));
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      var tfoot = el('tfoot'); var trf = el('tr');
      trf.appendChild(el('td', null, '參與人數'));
      LECTURES.forEach(function (l) { trf.appendChild(el('td', null, String(statsOf(docs, l[0]).people.length || '–'))); });
      tfoot.appendChild(trf); table.appendChild(tfoot);
      var wrap = el('div', 'boardwrap'); wrap.appendChild(table);
      gridWrap.appendChild(wrap);
      gridWrap.appendChild(el('p', 'copyhint', '格子裡的數字是寫了幾題進階題。「+」表示有基礎題留言，「·」表示只有整體補充或附件。點格子可以切到那一堂。'));
    }

    function lectureMarkdown(key) {
      var ids = docs.map(function (d) { return d.id; });
      return Promise.all([profilesFor(ids), questionsOf(key)]).then(function (r) {
        var profiles = r[0], all = r[1];
        var lines = ['## ' + lecLabel(key), ''];
        var qs = all.filter(function (q) { return !q.basic; });
        var qids = qs.map(function (q) { return q.id; });
        questionList(key, docs).forEach(function (q) { if (qids.indexOf(q) < 0) { qs.push({ id: q, tag: '', text: '' }); } });
        qs.sort(function (a, b) { return qNo(a.id) - qNo(b.id); });
        qs.forEach(function (q) {
          var thread = threadOf(docs, key, q.id);
          if (!thread.length) return;
          lines.push('### Q' + qNo(q.id) + '. ' + (q.text || ''), '');
          thread.forEach(function (t) {
            lines.push('**' + nameOf(t.data, profiles[t.uid]) + '**（' + fmtTime(t.at) + '）', '', t.text.trim(), '');
          });
        });
        var brows = basicRows(key, all);
        if (brows.length) {
          lines.push('### 基礎題留言', '');
          brows.forEach(function (q) {
            lines.push('**B' + qNo(q.id) + '. ' + (q.text || '') + '**', '');
            noteThreadOf(docs, key, q.id).forEach(function (t) {
              lines.push('- ' + nameOf(t.data, profiles[t.uid]) + '（' + fmtTime(t.at) + '）：' + t.text.trim().replace(/\n+/g, ' '));
            });
            lines.push('');
          });
        }
        var extras = peopleOf(docs, key).filter(function (p) { return hasOverall(p.entry) || p.files.length; });
        if (extras.length) {
          lines.push('### 整體補充與附件', '');
          extras.forEach(function (p) {
            lines.push('**' + nameOf(p.data, profiles[p.uid]) + '**（' + fmtTime(p.entry.updatedAt) + '）', '');
            if (hasOverall(p.entry)) lines.push(p.entry.text.trim(), '');
            p.files.forEach(function (f) { lines.push('- 附件：' + String(f.name || '附件') + ' — ' + location.origin + blobUrl(f.id)); });
            if (p.files.length) lines.push('');
          });
        }
        return lines.join('\n').trim() + '\n';
      });
    }
    function exportMarkdown() {
      var keys = LECTURES.map(function (l) { return l[0]; }).filter(function (k) { return statsOf(docs, k).people.length; });
      return Promise.all(keys.map(lectureMarkdown)).then(function (parts) {
        return ['# CS2680 讀書會討論彙整', '', '匯出時間：' + new Date().toISOString().slice(0, 16).replace('T', ' ') + ' UTC', ''].concat(parts).join('\n');
      });
    }

    function renderAll() {
      var ids = docs.map(function (d) { return d.id; });
      return profilesFor(ids).then(function (profiles) {
        if (!current) current = pickDefault();
        renderPills(profiles);
        var p = renderReader(profiles);
        renderFeed(profiles);
        renderGrid(profiles);
        return p;
      });
    }

    bnoteSet('連線中…');
    ready.then(function () {
      if (!db) {
        bnoteSet('這個畫面連不到共用資料庫。請在 claude.ai 登入後開啟這一頁。', true);
        current = pickDefault();
        renderPills({});
        renderReader({});
        return;
      }
      bnoteSet('');
      subscribe(renderAll, function (err) {
        var code = err && err.code;
        bnoteSet(code === 'revoked' ? '連線已中斷，請重新整理。' : '讀取失敗（' + (code || '未知錯誤') + '），請重新整理。', true);
      });
      if (exportBtn) {
        useCap('downloads').then(function (dl) {
          if (!dl) return;
          exportBtn.hidden = false;
          var label = exportBtn.textContent;
          exportBtn.addEventListener('click', function () {
            exportBtn.disabled = true;
            exportMarkdown().then(function (md) {
              var d = new Date();
              var name = 'cs2680-discussions-' + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) + '.md';
              return dl.save({ filename: name, data: md });
            }).then(function () { exportBtn.textContent = '已下載'; }, function (err) {
              exportBtn.textContent = (err && err.code === 'declined') ? label : '下載失敗';
            }).then(function () {
              exportBtn.disabled = false;
              setTimeout(function () { exportBtn.textContent = label; }, 2500);
            });
          });
        });
      }
    });
  }
})();
