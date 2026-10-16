/* CS2680 觀念導讀 — 讀書會交作業（submit.js）
   每一講的「7 · 交作業」段落，以及 submissions.html 的收作業總表，都由這個檔案驅動。
   共用資料放在 artifact 的 db capability；身份來自 user capability；附件走 assets。
   沒有 window.claude（本機開檔、或 viewer 沒授權）時，表單仍能打草稿、複製成文字。

   資料結構：collection "submissions"，每位成員一份 doc，id 就是 user id。
     submissions/<uid> = {
       nick: "顯示名稱（選填）", updatedAt: ISO,
       l02: { text, files: [{ id, name, type, size }], updatedAt: ISO }, ...
     }
   規則（publish 時宣告）：所有人可讀，每個人只能寫自己的 doc，owner 可改任何人的。 */
(function () {
  'use strict';

  var LECTURES = [
    ['l01', '課程總覽與 AI 系統'],
    ['l02', 'Claude Code 怎麼運作'],
    ['l03', '用多個 agent 放大產能'],
    ['l04', 'Context 管理與 tool 設計'],
    ['l05', 'Multi-agent 架構與溝通'],
    ['l06', 'Agent memory 與可靠性'],
    ['l07', 'Agent 評估'],
    ['l08', '成本、速度與 harness 架構']
  ];
  var TITLE = {};
  LECTURES.forEach(function (l) { TITLE[l[0]] = l[1]; });

  var lecMain = document.querySelector('main[data-lecture]');
  var lecture = lecMain ? lecMain.getAttribute('data-lecture') : null;
  var boardEl = document.getElementById('sub-board');
  var formEl = document.getElementById('sub-form');
  if (!(lecture && formEl) && !boardEl) return;

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
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }
  function fmtSize(bytes) {
    if (!(bytes >= 0)) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(0) + ' KB';
    return (bytes / 1024 / 1024).toFixed(1) + ' MB';
  }
  function clone(o) { return JSON.parse(JSON.stringify(o || {})); }
  function nameOf(data, profile) {
    var nick = (data && typeof data.nick === 'string') ? data.nick.trim() : '';
    if (nick) return nick;
    if (profile && profile.name) return profile.name;
    return '成員';
  }
  function lectureEntries(docs, key) {
    var out = [];
    docs.forEach(function (snap) {
      var data = snap.data() || {};
      var entry = data[key];
      if (entry && typeof entry.text === 'string' && entry.text.trim()) {
        out.push({ uid: snap.id, data: data, entry: entry });
      }
    });
    out.sort(function (a, b) { return (b.entry.updatedAt || '').localeCompare(a.entry.updatedAt || ''); });
    return out;
  }
  function blobUrl(id) { return '/_blob/' + id; }
  function safeId(id) { return typeof id === 'string' && /^[0-9a-f]{32}$/.test(id) ? id : null; }

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

  function subscribe(onDocs, onError) {
    if (!db) return;
    db.collection('submissions').onSnapshot(function (snap) {
      docs = snap.docs;
      onDocs(snap);
    }, function (err) { onError(err); });
  }

  /* ========================================================================
     Lecture page: form + list
     ======================================================================== */
  if (lecture && formEl) {
    var note = $('sub-note');
    var status = $('sub-status');
    var textEl = $('sub-text');
    var nickEl = $('sub-nick');
    var fileRow = $('sub-filerow');
    var fileEl = $('sub-file');
    var attachEl = $('sub-attach');
    var sendBtn = $('sub-send');
    var copyBtn = $('sub-copy');
    var listEl = $('sub-list');
    var countEl = $('sub-count');
    var DRAFT_KEY = 'cs2680.draft.' + lecture;
    var NICK_KEY = 'cs2680.nick';
    var assets = null;
    var pendingFiles = [];       // [{id, name, type, size}] kept on the next save
    var prefilled = false;
    var dirty = false;

    function setNote(text, warn) {
      if (!note) return;
      note.textContent = text || '';
      note.hidden = !text;
      note.classList.toggle('warn', !!warn);
    }
    function setStatus(text) { if (status) status.textContent = text || ''; }

    /* draft: this viewer only */
    formEl.hidden = false;
    var draft = lsGet(DRAFT_KEY);
    if (draft && textEl) { textEl.value = draft; dirty = true; }
    var savedNick = lsGet(NICK_KEY);
    if (savedNick && nickEl) nickEl.value = savedNick;
    var draftTimer = null;
    if (textEl) {
      textEl.addEventListener('input', function () {
        dirty = true;
        clearTimeout(draftTimer);
        draftTimer = setTimeout(function () { lsSet(DRAFT_KEY, textEl.value || null); }, 400);
      });
    }
    if (nickEl) nickEl.addEventListener('input', function () { lsSet(NICK_KEY, nickEl.value.trim() || null); });

    function renderAttach() {
      if (!attachEl) return;
      attachEl.textContent = '';
      pendingFiles.forEach(function (f, i) {
        var li = el('li');
        var a = el('a', null, f.name + (f.size ? '（' + fmtSize(f.size) + '）' : ''));
        a.href = blobUrl(f.id); a.target = '_blank'; a.rel = 'noopener';
        li.appendChild(a);
        var rm = el('button', 'ghostbtn small', '移除');
        rm.type = 'button';
        rm.addEventListener('click', function () { pendingFiles.splice(i, 1); renderAttach(); });
        li.appendChild(rm);
        attachEl.appendChild(li);
      });
    }

    function composeText() {
      var who = (nickEl && nickEl.value.trim()) || me.name || '';
      var head = 'CS2680 L' + parseInt(lecture.slice(1), 10) + ' 討論：' + TITLE[lecture] + (who ? ' · ' + who : '');
      return head + '\n\n' + (textEl ? textEl.value.trim() : '');
    }
    if (copyBtn) {
      var copyLabel = copyBtn.textContent;
      copyBtn.addEventListener('click', function () {
        var text = composeText();
        function done() { copyBtn.textContent = '已複製'; setTimeout(function () { copyBtn.textContent = copyLabel; }, 2000); }
        function fail() { if (textEl) { textEl.focus(); textEl.select(); } copyBtn.textContent = '請手動複製'; setTimeout(function () { copyBtn.textContent = copyLabel; }, 2500); }
        try { navigator.clipboard.writeText(text).then(done, fail); } catch (e) { fail(); }
      });
    }

    function render() {
      if (!listEl) return;
      var entries = lectureEntries(docs, lecture);
      if (countEl) countEl.textContent = entries.length ? '（' + entries.length + ' 份）' : '';
      var ids = entries.map(function (e) { return e.uid; });
      var profilesP = (user && ids.length) ? user.profiles(ids) : Promise.resolve({});
      profilesP.then(function (profiles) {
        listEl.textContent = '';
        if (!entries.length) { listEl.appendChild(el('li', 'empty', '還沒有人送出。')); return; }
        entries.forEach(function (e) {
          var p = profiles[e.uid];
          var mine = me.id && e.uid === me.id;
          var li = el('li', 'subitem');
          li.id = 'sub-' + e.uid;
          var det = el('details');
          if (mine) det.open = true;
          var sum = el('summary');
          if (p && p.avatarUrl) { var img = el('img', 'avatar'); img.src = p.avatarUrl; img.alt = ''; sum.appendChild(img); }
          sum.appendChild(el('b', 'who', nameOf(e.data, p)));
          if (mine) sum.appendChild(el('span', 'mine', '你'));
          sum.appendChild(el('span', 'when', fmtTime(e.entry.updatedAt)));
          var n = e.entry.text.length;
          var fc = Array.isArray(e.entry.files) ? e.entry.files.length : 0;
          sum.appendChild(el('span', 'meta', n + ' 字' + (fc ? ' · ' + fc + ' 個附件' : '')));
          det.appendChild(sum);
          det.appendChild(el('pre', 'subtext', e.entry.text));
          if (fc) {
            var ul = el('ul', 'attach');
            e.entry.files.forEach(function (f) {
              var id = safeId(f && f.id);
              if (!id) return;
              var a = el('a', null, String(f.name || '附件') + (f.size ? '（' + fmtSize(f.size) + '）' : ''));
              a.href = blobUrl(id); a.target = '_blank'; a.rel = 'noopener';
              var fli = el('li'); fli.appendChild(a); ul.appendChild(fli);
            });
            det.appendChild(ul);
          }
          if (mine || me.isOwner) {
            var act = el('div', 'actions');
            var del = el('button', 'ghostbtn small', mine ? '刪除我的這份' : '刪除（主持人）');
            del.type = 'button';
            del.addEventListener('click', function () { removeEntry(e.uid, del); });
            act.appendChild(del);
            det.appendChild(act);
          }
          li.appendChild(det);
          listEl.appendChild(li);
        });
        /* first snapshot: load my own saved answer into the form unless a draft exists */
        if (!prefilled && me.id) {
          prefilled = true;
          var mineE = entries.filter(function (x) { return x.uid === me.id; })[0];
          if (mineE) {
            if (!dirty && textEl && !textEl.value) textEl.value = mineE.entry.text;
            if (nickEl && !nickEl.value && mineE.data.nick) nickEl.value = mineE.data.nick;
            pendingFiles = Array.isArray(mineE.entry.files) ? clone(mineE.entry.files).filter(function (f) { return safeId(f.id); }) : [];
            renderAttach();
          }
        }
      });
    }

    function myDoc() { return db.doc('submissions/' + me.id); }

    function removeEntry(uid, btn) {
      if (!db) return;
      btn.disabled = true;
      var ref = db.doc('submissions/' + uid);
      ref.get().then(function (snap) {
        if (!snap.exists) return;
        var data = clone(snap.data());
        delete data[lecture];
        data.updatedAt = new Date().toISOString();
        return ref.set(data);
      }).then(function () {
        if (uid === me.id) { pendingFiles = []; renderAttach(); }
        setStatus('已刪除。');
      }, function (err) {
        btn.disabled = false;
        setStatus('刪除失敗：' + (err && err.code ? err.code : '未知錯誤'));
      });
    }

    var uploading = false;
    if (fileEl) {
      fileEl.addEventListener('change', function () {
        var file = fileEl.files && fileEl.files[0];
        if (!file || !assets) return;
        var type = typeFor(file);
        if (!type) { setStatus('這種檔案格式不能上傳。請用 PDF、圖片、Markdown、txt、csv 或 json。'); fileEl.value = ''; return; }
        if (file.size > 20 * 1024 * 1024) { setStatus('檔案超過 20 MB。'); fileEl.value = ''; return; }
        uploading = true;
        if (sendBtn) sendBtn.disabled = true;
        setStatus('上傳附件中…');
        assets.upload(file, { type: type }).then(function (res) {
          pendingFiles.push({ id: res.id, name: file.name, type: res.contentType, size: res.sizeBytes });
          renderAttach();
          setStatus('附件已上傳。按「送出」才會存進你的討論。');
        }, function (err) {
          var code = err && err.code;
          var msg = code === 'too_large' ? '檔案太大。' : code === 'unsupported_type' ? '這種檔案格式不能上傳。'
            : code === 'quota_or_state' ? '站台的附件空間已滿，請改貼文字。' : code === 'rate_limited' ? '上傳太頻繁，稍等再試。' : '上傳失敗（' + (code || '未知錯誤') + '）。';
          setStatus(msg);
        }).then(function () {
          uploading = false;
          fileEl.value = '';
          if (sendBtn) sendBtn.disabled = !canSend();
        });
      });
    }

    function canSend() { return !!(db && me.id && canWrite !== false && !uploading); }

    formEl.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (!canSend()) return;
      var text = textEl ? textEl.value.trim() : '';
      if (!text) { setStatus('請先寫下你的討論。'); if (textEl) textEl.focus(); return; }
      var nick = nickEl ? nickEl.value.trim().slice(0, 40) : '';
      sendBtn.disabled = true;
      setStatus('送出中…');
      var now = new Date().toISOString();
      var ref = myDoc();
      ref.get().then(function (snap) {
        var data = snap.exists ? clone(snap.data()) : {};
        data[lecture] = { text: text, files: pendingFiles.slice(), updatedAt: now };
        data.nick = nick;
        data.updatedAt = now;
        return ref.set(data);
      }).then(function () {
        lsSet(DRAFT_KEY, null);
        dirty = false;
        setStatus('已送出 ' + fmtTime(now) + '。重新送出會覆蓋這一份。');
        sendBtn.disabled = !canSend();
      }, function (err) {
        var code = err && err.code;
        if (code === 'invalid_argument') {
          canWrite = false;
          setNote('你目前是唯讀身份，不能送出。請主持人在分享設定把你加為 Contributor 或 Editor；或先按「複製成文字」貼到群組。', true);
          setStatus('');
        } else if (code === 'quota_exceeded') {
          setStatus('資料庫已滿，請通知主持人。');
          sendBtn.disabled = false;
        } else {
          setStatus('送出失敗（' + (code || '未知錯誤') + '），請再試一次。');
          sendBtn.disabled = false;
        }
      });
    });

    /* light up once the capabilities answer */
    if (sendBtn) sendBtn.disabled = true;
    setNote('連線中…');
    ready.then(function () {
      if (!db) {
        setNote('這個畫面連不到共用資料庫，所以不能送出。你可以先寫好，按「複製成文字」貼到群組。', true);
        if (sendBtn) sendBtn.hidden = true;
        return;
      }
      if (!me.id) {
        setNote('請先登入 claude.ai，再重新開這一頁，才能送出。', true);
      } else if (canWrite === false) {
        setNote('你目前是唯讀身份，可以看大家的討論，但不能送出。請主持人在分享設定把你加為 Contributor 或 Editor。', true);
      } else {
        setNote('送出後所有成員都看得到。重新送出會覆蓋你上一次的內容。');
      }
      if (sendBtn) sendBtn.disabled = !canSend();
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
     submissions.html: who handed in what
     ======================================================================== */
  if (boardEl) {
    var bnote = $('sub-note');
    var recentEl = $('sub-recent');
    var exportBtn = $('sub-export');
    var tbody = boardEl.querySelector('tbody');
    var tfoot = boardEl.querySelector('tfoot');

    function bnoteSet(text, warn) {
      if (!bnote) return;
      bnote.textContent = text || '';
      bnote.hidden = !text;
      bnote.classList.toggle('warn', !!warn);
    }

    function renderBoard() {
      var ids = docs.map(function (d) { return d.id; });
      var profilesP = (user && ids.length) ? user.profiles(ids) : Promise.resolve({});
      profilesP.then(function (profiles) {
        var rows = docs.map(function (snap) {
          var data = snap.data() || {};
          var count = 0, latest = '';
          LECTURES.forEach(function (l) {
            var e = data[l[0]];
            if (e && e.text && e.text.trim()) { count++; if ((e.updatedAt || '') > latest) latest = e.updatedAt; }
          });
          return { uid: snap.id, data: data, count: count, latest: latest, name: nameOf(data, profiles[snap.id]) };
        }).filter(function (r) { return r.count > 0; });
        rows.sort(function (a, b) { return b.count - a.count || a.name.localeCompare(b.name); });

        tbody.textContent = '';
        if (!rows.length) {
          var tr0 = el('tr'); var td0 = el('td', 'empty', '還沒有人送出任何討論。'); td0.colSpan = LECTURES.length + 2; tr0.appendChild(td0); tbody.appendChild(tr0);
        }
        var totals = {};
        rows.forEach(function (r) {
          var tr = el('tr');
          var th = el('th', null, r.name + (me.id === r.uid ? '（你）' : '')); th.scope = 'row';
          tr.appendChild(th);
          LECTURES.forEach(function (l) {
            var td = el('td');
            var e = r.data[l[0]];
            if (e && e.text && e.text.trim()) {
              totals[l[0]] = (totals[l[0]] || 0) + 1;
              var a = el('a', null, '✓'); a.href = l[0] + '.html#s-submit'; a.title = fmtTime(e.updatedAt);
              td.appendChild(a);
            } else {
              td.appendChild(el('span', 'no', '–'));
            }
            tr.appendChild(td);
          });
          tr.appendChild(el('td', 'when', fmtTime(r.latest)));
          tbody.appendChild(tr);
        });
        if (tfoot) {
          tfoot.textContent = '';
          var trf = el('tr');
          trf.appendChild(el('td', null, '份數'));
          LECTURES.forEach(function (l) { trf.appendChild(el('td', null, String(totals[l[0]] || 0))); });
          trf.appendChild(el('td', null, rows.length + ' 人'));
          tfoot.appendChild(trf);
        }

        if (recentEl) {
          var recent = [];
          docs.forEach(function (snap) {
            var data = snap.data() || {};
            LECTURES.forEach(function (l) {
              var e = data[l[0]];
              if (e && e.text && e.text.trim()) recent.push({ uid: snap.id, key: l[0], at: e.updatedAt || '', name: nameOf(data, profiles[snap.id]) });
            });
          });
          recent.sort(function (a, b) { return b.at.localeCompare(a.at); });
          recentEl.textContent = '';
          if (!recent.length) recentEl.appendChild(el('li', 'empty', '還沒有紀錄。'));
          recent.slice(0, 12).forEach(function (r) {
            var li = el('li');
            li.appendChild(el('span', 'when', fmtTime(r.at)));
            var span = el('span');
            span.appendChild(document.createTextNode(r.name + ' 送出了 '));
            var a = el('a', null, 'L' + parseInt(r.key.slice(1), 10) + ' ' + TITLE[r.key]);
            a.href = r.key + '.html#s-submit';
            span.appendChild(a);
            li.appendChild(span);
            recentEl.appendChild(li);
          });
        }
      });
    }

    function exportMarkdown() {
      var ids = docs.map(function (d) { return d.id; });
      var profilesP = (user && ids.length) ? user.profiles(ids) : Promise.resolve({});
      return profilesP.then(function (profiles) {
        var lines = ['# CS2680 讀書會討論彙整', '', '匯出時間：' + fmtTime(new Date().toISOString()), ''];
        LECTURES.forEach(function (l) {
          var entries = lectureEntries(docs, l[0]);
          if (!entries.length) return;
          lines.push('## L' + parseInt(l[0].slice(1), 10) + ' ' + l[1], '');
          entries.forEach(function (e) {
            lines.push('### ' + nameOf(e.data, profiles[e.uid]) + '（' + fmtTime(e.entry.updatedAt) + '）', '');
            lines.push(e.entry.text.trim(), '');
            if (Array.isArray(e.entry.files) && e.entry.files.length) {
              lines.push('附件：');
              e.entry.files.forEach(function (f) { if (safeId(f && f.id)) lines.push('- ' + String(f.name || '附件') + ' — ' + location.origin + blobUrl(f.id)); });
              lines.push('');
            }
          });
        });
        return lines.join('\n');
      });
    }

    bnoteSet('連線中…');
    ready.then(function () {
      if (!db) {
        bnoteSet('這個畫面連不到共用資料庫。請在 claude.ai 登入後開啟這一頁。', true);
        return;
      }
      bnoteSet('');
      subscribe(renderBoard, function (err) {
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
