/* CS2680 觀念導讀 — interactive figures (STYLE_ARTICLE 6〈互動圖〉).
   A figure.diagram[data-calc="name"] keeps its static SVG in the HTML. That SVG
   is the default the text talks about, what readers without JS see, and what
   the checks, the review pack and the online editor read. Its div.calc
   (sliders, hidden in the HTML) is shown here; moving a slider redraws the SVG
   from the same formula. At the default values, and when the online editor
   starts (edit.js calls cs2680Calc.resetAll), the original SVG, aria-label and
   readouts come back byte for byte. No storage, no network. */
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  var CALCS = {};
  var live = [];

  function add(parent, tag, attrs, text) {
    var n = document.createElementNS(NS, tag);
    for (var a in attrs) n.setAttribute(a, attrs[a]);
    if (text !== undefined) n.textContent = text;
    parent.appendChild(n);
    return n;
  }
  function int(n) { return Math.round(n).toLocaleString('en-US'); }
  function strip(s) { return s.replace(/\.0+$/, ''); }
  /* rough width of a 13px label, to drop the breakdown when it would leave the viewBox */
  function textW(s) {
    var w = 0;
    for (var i = 0; i < s.length; i++) {
      var ch = s.charCodeAt(i);
      if (ch > 0x2e80) w += 13;
      else if (s[i] === ',' || s[i] === ' ' || s[i] === '.') w += 3.6;
      else w += 7.8;
    }
    return w;
  }

  /* L6 3.1：50 步的 run 切成幾段、每段尾驗證一次，平均總成本。
     sliders: c = 一次驗證算幾步, p = 每步成功率 (%). */
  CALCS.ckpt = function (fig, box) {
    var svg = fig.querySelector('svg');
    var inC = box.querySelector('[data-k="c"]');
    var inP = box.querySelector('[data-k="p"]');
    var outC = box.querySelector('[data-v="c"]');
    var outP = box.querySelector('[data-v="p"]');
    var res = box.querySelector('.calc-out');
    var btn = box.querySelector('.calc-reset');
    if (!svg || !inC || !inP || !outC || !outP || !res || !btn) return null;

    var N = 50, KS = [50, 25, 10, 5, 2, 1];
    var X0 = 212, W = 379, ROW0 = 58, DY = 48, RIGHT = 714, CLIP = 8;
    var C0 = inC.defaultValue, P0 = inP.defaultValue;
    var orig = {
      svg: svg.innerHTML, label: svg.getAttribute('aria-label'),
      c: outC.innerHTML, p: outP.innerHTML, res: res.innerHTML
    };
    /* defs and the legend (above the first row) stay; the rows are redrawn */
    var head = '';
    for (var i = 0; i < svg.children.length; i++) {
      var n = svg.children[i];
      var y = parseFloat(n.getAttribute('y'));
      if (n.tagName.toLowerCase() === 'defs' || y < ROW0 - 10) head += n.outerHTML;
    }
    var legendRe = /(驗證的成本：一次驗證算 )[\d.]+( 步)(（本文的假設）)?/;

    function pct(x) {
      var v = x * 100;
      if (v < 1) { var s = v.toFixed(1); return s === '0.0' ? '<0.1%' : s + '%'; }
      if (v >= 99) return strip(v.toFixed(1)) + '%';
      return Math.round(v) + '%';
    }
    function runs(r) {
      if (r >= 10) return int(r);
      if (r >= 1.1) return r.toFixed(1);
      return r.toFixed(2);
    }
    function every(p) {
      var m = 1 / (1 - p), r = Math.round(m);
      return (Math.abs(m - r) < 0.01 ? '平均每 ' : '平均約每 ') + int(m) + ' 步錯一次';
    }
    function name(k) { return k === N ? '不分段' : '每段 ' + k + ' 步'; }
    function rowName(r) { return r.k === N ? '不分段，共 1 段' : '每段 ' + r.k + ' 步，共 ' + r.segs + ' 段'; }

    function compute(c, p) {
      return KS.map(function (k) {
        var segs = N / k, ok = Math.pow(p, k), rr = 1 / ok;
        var steps = segs * k * rr, ver = segs * rr, cost = ver * c;
        var s = Math.round(steps), v = Math.round(cost);
        return { k: k, segs: segs, ok: ok, runs: rr, ver: ver, steps: s, cost: v, total: s + v, exact: steps + cost };
      });
    }
    /* best by the shown total; the exact value only breaks ties */
    function order(rows) {
      return rows.map(function (r, i) { return i; }).sort(function (a, b) {
        return (rows[a].total - rows[b].total) || (rows[a].exact - rows[b].exact);
      });
    }

    function draw(c, pRaw) {
      var p = pRaw / 100;
      var rows = compute(c, p);
      var rank = order(rows), best = rank[0], second = rank[1];
      var minT = rows[best].total, maxT = 0;
      rows.forEach(function (r) { if (r.total > maxT) maxT = r.total; });
      var dom = Math.max(1, Math.min(maxT, CLIP * minT));
      var sc = W / dom;
      var clippedAny = false;

      svg.innerHTML = head;
      var legend = svg.querySelectorAll('text');
      for (var i = 0; i < legend.length; i++) {
        if (legendRe.test(legend[i].textContent)) {
          legend[i].textContent = '驗證的成本：一次驗證算 ' + c + ' 步' + (String(c) === C0 ? '（本文的假設）' : '');
        }
      }
      var aria = '橫條圖：' + N + ' 步、每步 ' + pRaw + '% 的 run，每段切幾步時平均要花多少。列名下一行是一段的數字；長條是整個 run 的數字：要跑的步數加上驗證的成本，一次驗證算 ' + c + ' 步。';

      rows.forEach(function (r, i) {
        var y = ROW0 + DY * i, isBest = i === best;
        var okText = r.k === 1 ? pRaw + '%' : pct(r.ok);
        add(svg, 'text', { x: 200, y: y + 9, 'text-anchor': 'end', 'class': isBest ? 'dg-l-key' : 'dg-ls' }, rowName(r));
        add(svg, 'text', { x: 200, y: y + 27, 'text-anchor': 'end', 'class': 'dg-c' }, '每段全對 ' + okText + '，平均跑 ' + runs(r.runs) + ' 次');
        var clipped = r.total > dom;
        if (clipped) clippedAny = true;
        var gw = Math.min(r.steps, dom) * sc;
        var bw = Math.min(r.cost, Math.max(0, dom - r.steps)) * sc;
        add(svg, 'rect', { x: X0, y: y, width: gw.toFixed(1), height: 26, 'class': 'dg-n-n' });
        if (bw > 0.05) add(svg, 'rect', { x: (X0 + gw).toFixed(1), y: y, width: bw.toFixed(1), height: 26, 'class': 'dg-n-b' });
        var end = X0 + gw + bw;
        if (clipped) {
          /* a slanted gap near the end: this bar is cut, its number is the real one */
          var gx = end - 16;
          add(svg, 'polygon', { points: [gx + 2, y - 3, gx + 8, y - 3, gx + 2, y + 29, gx - 4, y + 29].join(' '), 'class': 'dg-gap' });
        }
        var lx = end + 8;
        var label = add(svg, 'text', { x: lx.toFixed(1), y: y + 18, 'class': isBest ? 'dg-k' : 'dg-cb' }, int(r.total));
        var parts = '（' + int(r.steps) + ' + ' + int(r.cost) + '）';
        var tail = isBest ? ' 最省' : '';
        if (lx + textW(int(r.total) + parts + tail) <= RIGHT) add(label, 'tspan', { 'class': 'dg-c' }, parts);
        if (tail) label.appendChild(document.createTextNode(tail));
        aria += rowName(r) + '：每段全對 ' + okText + '，平均跑 ' + runs(r.runs) + ' 次；整個 run 的步數 ' + int(r.steps) +
          '，驗證約 ' + r.ver.toFixed(1) + ' 次、成本 ' + int(r.cost) + '，合計 ' + int(r.total) + tail + '。';
      });

      var diff = rows[second].total - rows[best].total;
      var out = '最省：' + name(rows[best].k) + '，合計 ' + int(minT) + '。第二省是' + name(rows[second].k) +
        (diff > 0 ? '，多 ' + int(diff) + '。' : '，同樣約 ' + int(minT) + '。');
      if (clippedAny) out += '最長的長條超出圖寬，畫成截斷，數字是實際值。';
      res.textContent = out;
      aria += '結論：' + name(rows[best].k) + '最省。';
      svg.setAttribute('aria-label', aria);
    }

    function restore() {
      svg.innerHTML = orig.svg;
      svg.setAttribute('aria-label', orig.label);
      outC.innerHTML = orig.c;
      outP.innerHTML = orig.p;
      res.innerHTML = orig.res;
      btn.disabled = true;
    }
    function update() {
      var c = inC.value, pRaw = inP.value;
      if (c === C0 && pRaw === P0) { restore(); return; }
      outC.textContent = c === '0' ? '0 步，驗證不花成本' : c + ' 步';
      outP.textContent = pRaw + '%（' + every(+pRaw / 100) + '）';
      draw(+c, +pRaw);
      btn.disabled = false;
    }
    function reset() {
      inC.value = C0;
      inP.value = P0;
      restore();
    }
    inC.addEventListener('input', update);
    inP.addEventListener('input', update);
    btn.addEventListener('click', reset);
    return { reset: reset };
  };

  /* ---------- animated figures (STYLE_ARTICLE 6〈動畫圖〉) ----------
     Same contract as the slider figures, plus a time axis the reader plays or
     drags. The static SVG in the HTML is the last frame at the default setting.
     FRAMES.name(...) returns one frame as SVG markup (a string, no DOM), so
     tools/anim_static.js writes the static SVG from this same code. */
  var FRAMES = {};
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function fmtK(v) { return strip((Math.round(v * 10) / 10).toFixed(1)) + 'K'; }

  /* L8 3.4：同一段對話在 5 分鐘與 1 小時 TTL 底下。
     t = 現在第幾分鐘 (0–40)，d = 使用者離開幾分鐘 (1–34)。
     對話進行到一半：context C 已經在 cache 裡，五個 request 各新增 G / 5。
     單位是 K base input token，和正文的算式同一組數字 (C 200、G 30、r 0.1)。 */
  var TTL = { END: 40, X0: 120, PX: 14.4, Y5: 30, Y1: 120, H: 26, AX: 164, C: 200, G: 30, R: 0.1 };
  function ttlModel(d) {
    var back = 4 + d, expired = d >= 5, last = Math.min(TTL.END, back + 7);
    var ev = [{ t: 0, k: 'first' }, { t: 2, k: 'hit1' }, { t: 4, k: 'hit2' }];
    if (expired) ev.push({ t: 9, k: 'expire' });
    ev.push({ t: back, k: expired ? 'miss' : 'back' });
    ev.push({ t: back + 2, k: 'hit3' });
    if (back + 7 < TTL.END) ev.push({ t: back + 7, k: 'expire2' });
    ev.push({ t: TTL.END, k: 'end' });
    return {
      d: d, back: back, expired: expired, reqs: [0, 2, 4, back, back + 2],
      alive: expired ? [[0, 9], [back, last]] : [[0, last]], ev: ev
    };
  }
  /* only what differs between the two TTLs, plus the one read or rewrite of C on return */
  function ttlCost(m, t) {
    var g = TTL.G / 5, n = 0;
    m.reqs.forEach(function (r) { if (r <= t) n++; });
    var came = t >= m.back;
    var c = {
      new5: 1.25 * g * n, new1: 2 * g * n,
      miss5: came && m.expired ? 1.25 * TTL.C : 0,
      read5: came && !m.expired ? TTL.R * TTL.C : 0,
      read1: came ? TTL.R * TTL.C : 0
    };
    c.sum5 = c.new5 + c.miss5 + c.read5;
    c.sum1 = c.new1 + c.read1;
    return c;
  }
  function ttlEvent(m, t) {
    var cur = m.ev[0];
    m.ev.forEach(function (e) { if (e.t <= t) cur = e; });
    return cur;
  }
  function ttlSay(m, t) {
    var e = ttlEvent(m, t), at = '第 ' + e.t + ' 分鐘：';
    var g = fmtK(TTL.G / 5), rewrite = fmtK(1.25 * TTL.C), read = fmtK(TTL.R * TTL.C);
    switch (e.k) {
      case 'first': return at + '對話進行到一半，' + fmtK(TTL.C) + ' 的 context 已經在 cache 裡。這個 request 新增 ' + g + '，要寫進 cache：5 分鐘 TTL 收 1.25×，1 小時 TTL 收 2×。';
      case 'hit1': return at + 'cache hit。5 分鐘的 cache 重新計時，過期的時間從第 5 分鐘延到第 7 分鐘。';
      case 'hit2': return at + '又一次 cache hit，延到第 9 分鐘。接著使用者離開 ' + m.d + ' 分鐘。';
      case 'expire': return at + '5 分鐘的 cache 過期，留下的結果丟掉了。1 小時的 cache 還在。';
      case 'miss': return at + '使用者回來。5 分鐘 TTL 是 cache miss，整個 context 要重算、再寫進 cache，付 ' + rewrite + '；1 小時 TTL 是 cache read，付 ' + read + '。';
      case 'back': return at + '使用者回來。5 分鐘的 cache 要到第 9 分鐘才過期，還在。兩邊都是 cache read，各付 ' + read + '。';
      case 'hit3': return at + '兩邊都是 cache hit，回到平常的價錢。';
      case 'expire2': return at + '最後一個 request 之後 5 分鐘沒有新的 request，5 分鐘的 cache 又過期。';
    }
    var c = ttlCost(m, TTL.END);
    var sums = '結算：5 分鐘 TTL 花 ' + fmtK(c.sum5) + '，1 小時 TTL 花 ' + fmtK(c.sum1);
    return m.expired
      ? sums + '，1 小時 TTL 便宜約 ' + (c.sum5 / c.sum1).toFixed(1) + ' 倍。'
      : sums + '。Cache 沒有過期，5 分鐘 TTL 比較便宜。';
  }
  function ttlAria(m, t) {
    var c = ttlCost(m, t);
    return '兩條時間軸，橫軸 0 到 40 分鐘，現在是第 ' + Math.floor(t) + ' 分鐘。使用者在第 0、2、4 分鐘送 request，離開 ' + m.d +
      ' 分鐘，第 ' + m.back + '、' + (m.back + 2) + ' 分鐘回來。到這時候，5 分鐘 TTL 花了 ' + fmtK(c.sum5) + '，1 小時 TTL 花了 ' + fmtK(c.sum1) + '。';
  }
  FRAMES.ttl = function (t, d) {
    var m = ttlModel(d), o = [], END = TTL.END, Y5 = TTL.Y5, Y1 = TTL.Y1, AX = TTL.AX;
    function xn(min) { return TTL.X0 + TTL.PX * min; }
    function x(min) { return xn(min).toFixed(1); }
    function rect(a, b, y, cls, inset) {
      if (b - a < 0.01) return;
      var i = inset || 0;
      o.push('<rect x="' + (xn(a) + i).toFixed(1) + '" y="' + (y + i) + '" width="' + Math.max(0, TTL.PX * (b - a) - 2 * i).toFixed(1) +
        '" height="' + (TTL.H - 2 * i) + '" class="' + cls + '"/>');
    }
    function line(xx, y1, y2, cls) { o.push('<path d="M' + xx + ',' + y1 + ' L' + xx + ',' + y2 + '" class="' + cls + '"/>'); }
    var boxes = [];   /* labels between the rows: the playhead steps over them */
    function text(xx, y, cls, s, anchor) {
      if (typeof xx === 'number' && y > Y5 + TTL.H && y < Y1) {
        var w = textW(String(s)), left = anchor === 'middle' ? xx - w / 2 : xx;
        boxes.push([left - 4, left + w + 4, y - 14, y + 6]);
      }
      o.push('<text x="' + (typeof xx === 'number' ? xx.toFixed(1) : xx) + '" y="' + y + '"' +
        (anchor ? ' text-anchor="' + anchor + '"' : '') + ' class="' + cls + '">' + s + '</text>');
    }

    /* 倍率寫在列名底下：每一次寫入新內容都照這個倍率，不只第一次 */
    text(14, Y5 + 10, 'dg-cb', '5 分鐘 TTL');
    text(14, Y5 + 27, 'dg-c', 'write 1.25×');
    text(14, Y1 + 10, 'dg-cb', '1 小時 TTL');
    text(14, Y1 + 27, 'dg-c', 'write 2×');

    /* 青色：cache 活到現在的時間；虛線框：照現在的計時還能活到什麼時候 */
    var lastReq = 0, live5 = false;
    m.reqs.forEach(function (r) { if (r <= t) lastReq = r; });
    m.alive.forEach(function (iv) {
      rect(iv[0], Math.min(iv[1], t), Y5, 'dg-n-a');
      if (t >= iv[0] && t < iv[1]) live5 = true;
    });
    rect(0, t, Y1, 'dg-n-a');
    if (t < END) {
      if (live5) rect(t, Math.min(lastReq + 5, END), Y5, 'dg-ghost', 0.6);
      rect(t, END, Y1, 'dg-ghost', 0.6);
    }

    /* request：到了的畫實線，還沒到的畫淡 */
    m.reqs.forEach(function (r, i) {
      var past = r <= t;
      if (i === 3 && m.expired && past) line(x(r), Y5 - 6, Y5 + 32, 'dg-link-key');
      else line(x(r), Y5 - 4, Y5 + 30, past ? 'dg-link' : 'dg-link dg-next');
      line(x(r), Y1 - 4, Y1 + 30, past ? 'dg-link' : 'dg-link dg-next');
    });

    if (t >= m.back) {
      var xb = xn(m.back);
      if (m.expired) text(clamp(xb, 209, 623), Y5 - 10, 'dg-k', 'write 1.25×（整個 context）', 'middle');
      else text(clamp(xb, 154, 662), Y5 - 10, 'dg-c', 'cache read', 'middle');
      text(clamp(xb, 154, 662), Y1 - 10, 'dg-c', 'cache read', 'middle');
    }
    if (m.expired && t > 9) {
      var ge = Math.min(t, m.back);
      if (TTL.PX * (ge - 9) >= 104) text((xn(9) + xn(ge)) / 2, Y5 + 18, 'dg-c', 'cache 已過期', 'middle');
    }

    /* 使用者離開的那一段 */
    if (t > 4) {
      var be = Math.min(t, m.back);
      var awayX = clamp((xn(4) + xn(m.back)) / 2, 184, 648);
      o.push('<path d="M' + x(4) + ',66 L' + x(4) + ',70 L' + x(be) + ',70' + (t >= m.back ? ' L' + x(be) + ',66' : '') + '" class="dg-soft-link"/>');
      text(awayX, 87, 'dg-c', '使用者離開 ' + d + ' 分鐘', 'middle');
    }

    o.push('<path d="M' + x(0) + ',' + AX + ' L' + x(END) + ',' + AX + '" class="dg-link"/>');
    [0, 10, 20, 30, 40].forEach(function (v) {
      line(x(v), AX, AX + 5, 'dg-link');
      text(x(v), AX + 21, 'dg-mn', v, 'middle');
    });
    text(694, AX + 38, 'dg-c', '分鐘', 'end');
    text(118, AX + 38, 'dg-c', '短直條是 request，青色是 cache 活著的時間');

    if (t < END) {
      var px = xn(t), y0 = 24;
      boxes.filter(function (b) { return px > b[0] && px < b[1]; })
        .sort(function (a, b) { return a[2] - b[2]; })
        .forEach(function (b) { if (b[2] > y0) line(x(t), y0, b[2], 'dg-now'); y0 = Math.max(y0, b[3]); });
      line(x(t), y0, AX, 'dg-now');
      o.push('<circle cx="' + x(t) + '" cy="' + AX + '" r="4" class="dg-now-dot"/>');
    }
    return o.join('');
  };

  /* One controller for every animated figure. cfg:
       frame(t, s)   → SVG markup of one frame (s = the other sliders' values, by data-k)
       events(s)     → sorted times the play button pauses at and 下一步 jumps to; the last one is the end
       say(t, s)     → the one sentence for the event at or before t
       show(t, s, api) → optional: fill the outputs and bars under the figure
       x(t, s)       → optional: the playhead's x in viewBox units, to keep it in view on narrow screens
       speed, hold   → time units per second, and the pause at each event in ms
     The box needs [data-k="t"] (its max is the end), [data-act="play"], [data-act="step"], .calc-out, .calc-reset.
     Everything a frame may rewrite carries data-v or data-bar, so the default state can be put back exactly. */
  function makePlayer(fig, box, cfg) {
    function q(sel) { return box.querySelector(sel); }
    var svg = fig.querySelector('svg'), inT = q('[data-k="t"]');
    var res = q('.calc-out'), btn = q('.calc-reset');
    var play = q('[data-act="play"]'), step = q('[data-act="step"]');
    if (!svg || !inT || !res || !btn || !play || !step) return null;
    var params = [].slice.call(box.querySelectorAll('input[data-k]')).filter(function (i) { return i !== inT; });
    var keep = [].slice.call(box.querySelectorAll('[data-v], [data-bar], .calc-out'));
    var END = +inT.max, SPEED = cfg.speed || 5, HOLD = cfg.hold || 700;
    var orig = {
      svg: svg.innerHTML, label: svg.getAttribute('aria-label'), play: play.innerHTML,
      keep: keep.map(function (e) { return [e.innerHTML, e.className]; })
    };
    var vb = (svg.getAttribute('viewBox') || '0 0 720 0').split(/\s+/);
    var cur = END, raf = 0, lastTs = 0, hold = 0, said = '';
    /* no moving playhead for readers who asked for less motion: they step or drag */
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) play.hidden = true;

    function state() {
      var s = {};
      params.forEach(function (p) { s[p.getAttribute('data-k')] = +p.value; });
      return s;
    }
    var api = {
      set: function (k, text, cls) {
        var e = q('[data-v="' + k + '"]');
        if (!e) return;
        e.textContent = text;
        if (cls !== undefined) e.className = cls;
      },
      bar: function (k, vals, full) {
        var b = q('[data-bar="' + k + '"]');
        if (!b) return;
        for (var i = 0; i < vals.length; i++) {
          if (b.children[i]) b.children[i].style.width = (vals[i] / full * 100).toFixed(2) + '%';
        }
      }
    };
    /* on a narrow screen the figure scrolls sideways: keep the playhead in view */
    var scroller = fig.querySelector('.scroll');
    function follow(s) {
      if (!cfg.x || !scroller || scroller.scrollWidth <= scroller.clientWidth + 1) return;
      var px = cfg.x(cur, s) / (+vb[2] || 720) * svg.getBoundingClientRect().width;
      if (px < scroller.scrollLeft + 48 || px > scroller.scrollLeft + scroller.clientWidth - 48) {
        scroller.scrollLeft = Math.max(0, px - scroller.clientWidth / 2);
      }
    }
    function render() {
      var s = state();
      svg.innerHTML = cfg.frame(cur, s);
      follow(s);
      if (cfg.show) cfg.show(cur, s, api);
      var msg = cfg.say(cur, s);
      if (msg !== said) {
        said = msg;
        res.textContent = msg;
        svg.setAttribute('aria-label', (cfg.aria ? cfg.aria(cur, s) : '') + msg);
      }
      btn.disabled = false;
    }
    function restore() {
      svg.innerHTML = orig.svg;
      svg.setAttribute('aria-label', orig.label);
      keep.forEach(function (e, i) { e.innerHTML = orig.keep[i][0]; e.className = orig.keep[i][1]; });
      said = '';
      btn.disabled = true;
    }
    /* the default (last frame, the text's example) is the source SVG, byte for byte */
    function show() {
      var def = params.every(function (p) { return p.value === p.defaultValue; });
      if (!raf && cur >= END && def) restore();
      else render();
    }
    function stop() {
      if (raf) cancelAnimationFrame(raf);
      raf = 0; lastTs = 0; hold = 0;
      play.innerHTML = orig.play;
    }
    function nextEvent() {
      var ev = cfg.events(state());
      for (var i = 0; i < ev.length; i++) if (ev[i] > cur + 1e-6) return Math.min(ev[i], END);
      return END;
    }
    function tick(ts) {
      var dt = lastTs ? Math.min(100, ts - lastTs) : 0;
      lastTs = ts;
      if (hold > 0) hold -= dt;
      else {
        var next = nextEvent(), nt = cur + dt / 1000 * SPEED;
        if (nt >= next) { nt = next; hold = HOLD; }
        cur = nt;
        inT.value = cur;
        render();
      }
      if (cur >= END) { stop(); show(); return; }
      raf = requestAnimationFrame(tick);
    }
    play.addEventListener('click', function () {
      if (raf) { stop(); show(); return; }
      if (cur >= END) cur = +inT.min || 0;
      inT.value = cur;
      play.textContent = '❚❚ 暫停';
      hold = HOLD;
      raf = requestAnimationFrame(tick);
      render();
    });
    step.addEventListener('click', function () {
      stop();
      cur = cur >= END ? (+inT.min || 0) : nextEvent();
      inT.value = cur;
      show();
    });
    inT.addEventListener('input', function () { stop(); cur = +inT.value; show(); });
    params.forEach(function (p) {
      p.addEventListener('input', function () { stop(); cur = END; inT.value = END; show(); });
    });
    function reset() {
      stop();
      params.forEach(function (p) { p.value = p.defaultValue; });
      inT.value = END;
      cur = END;
      restore();
    }
    btn.addEventListener('click', reset);
    return { reset: reset };
  }

  /* SVG markup builder for frames: strings only, so node can run it (tools/anim_static.js). */
  function Draw(pre) {
    var o = [], boxes = [], clips = 0;
    function n(v) { return typeof v === 'number' ? v.toFixed(1).replace(/\.0$/, '') : v; }
    var d = {
      rect: function (x, y, w, h, cls, rx) {
        if (w < 0.05) return;
        o.push('<rect x="' + n(x) + '" y="' + n(y) + '" width="' + n(w) + '" height="' + n(h) + '"' + (rx ? ' rx="' + rx + '"' : '') + ' class="' + cls + '"/>');
      },
      path: function (p, cls) { o.push('<path d="' + p + '" class="' + cls + '"/>'); },
      vline: function (x, y1, y2, cls) { o.push('<path d="M' + n(x) + ',' + n(y1) + ' L' + n(x) + ',' + n(y2) + '" class="' + cls + '"/>'); },
      /* dodge: the playhead steps over this label instead of crossing it */
      text: function (x, y, cls, s, anchor, dodge) {
        if (dodge) {
          var w = textW(String(s)), left = anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w : x;
          boxes.push([left - 4, left + w + 4, y - 14, y + 6]);
        }
        o.push('<text x="' + n(x) + '" y="' + n(y) + '"' + (anchor ? ' text-anchor="' + anchor + '"' : '') + ' class="' + cls + '">' + s + '</text>');
      },
      playhead: function (x, y0, y1, dot) {
        boxes.filter(function (b) { return x > b[0] && x < b[1] && b[3] > y0 && b[2] < y1; })
          .sort(function (a, b) { return a[2] - b[2]; })
          .forEach(function (b) { if (b[2] > y0) d.vline(x, y0, b[2], 'dg-now'); y0 = Math.max(y0, b[3]); });
        if (y1 > y0) d.vline(x, y0, y1, 'dg-now');
        if (dot) o.push('<circle cx="' + n(x) + '" cy="' + n(y1) + '" r="4" class="dg-now-dot"/>');
      },
      /* a label on a block that is only partly filled with a dark colour: dark text, and light text
         clipped to the filled part [cx, cx + cw] */
      splitText: function (x, y, dark, lite, s, anchor, cx, cy, cw, ch) {
        d.text(x, y, dark, s, anchor);
        if (cw < 0.05) return;
        var id = pre + '-clip' + (++clips);
        o.push('<clipPath id="' + id + '"><rect x="' + n(cx) + '" y="' + n(cy) + '" width="' + n(cw) + '" height="' + n(ch) + '"/></clipPath><g clip-path="url(#' + id + ')">');
        d.text(x, y, lite, s, anchor);
        o.push('</g>');
      },
      html: function () { return o.join(''); }
    };
    return d;
  }

  CALCS.ttl = function (fig, box) {
    var FULL = 1.25 * (TTL.C + TTL.G);       /* the longest bar: one rewrite of C plus the new content */
    return makePlayer(fig, box, {
      frame: function (t, s) { return FRAMES.ttl(t, s.d); },
      events: function (s) { return ttlModel(s.d).ev.map(function (e) { return e.t; }); },
      say: function (t, s) { return ttlSay(ttlModel(s.d), t); },
      aria: function (t, s) { return ttlAria(ttlModel(s.d), t); },
      x: function (t) { return TTL.X0 + TTL.PX * t; },
      show: function (t, s, api) {
        var m = ttlModel(s.d), c = ttlCost(m, t);
        api.set('t', '第 ' + Math.floor(t) + ' 分鐘');
        api.set('d', s.d + ' 分鐘（5 分鐘的 cache ' + (m.expired ? '會過期' : '還在') + '）');
        api.bar('c5', [c.new5, c.miss5, c.read5], FULL);
        api.bar('c1', [c.new1, 0, c.read1], FULL);
        api.set('c5', fmtK(c.sum5), c.sum5 < c.sum1 ? 'calc-win' : '');
        api.set('c1', fmtK(c.sum1), c.sum1 < c.sum5 ? 'calc-win' : '');
      }
    });
  };

  /* L8 2.1：每一步重送整個 context。t = 走完幾步 (0–5)，小數是下一步正在送。
     10px = 1K token：開頭 12K，每一步新進來 4K、output 1K。 */
  var RS = { HEAD: 12, IN: 4, OUT: 1, N: 5 };
  /* 送給 model 的 token：重送的（上一列整列）與第一次出現的。粉色的 output 是 model 回的，這一步不算送出 */
  function rsCount(t) {
    var step = RS.IN + RS.OUT, nw = 0, re = 0;
    for (var k = 1; k <= RS.N; k++) {
      var old = k === 1 ? 0 : RS.HEAD + step * (k - 1), sent = RS.HEAD + step * (k - 1) + RS.IN, all = sent + RS.OUT;
      var got = t >= k ? all : t > k - 1 ? all * (t - (k - 1)) : 0;
      re += Math.min(got, old);
      nw += Math.max(0, Math.min(got, sent) - old);
    }
    return { nw: nw, re: re };
  }
  FRAMES.resend = function (t) {
    var d = Draw('rs'), n = Math.floor(t + 1e-9), f = t - n;
    for (var k = 1; k <= RS.N; k++) {
      var y = 12 + 34 * (k - 1), hist = 50 * (k - 1), end = 240 + hist;
      d.text(14, y + 18, 'dg-mn', 'step ' + k);
      if (k > n + 1 || (k === n + 1 && f < 0.001)) continue;
      var lim = k <= n ? end : 70 + (end - 70) * f;
      [[70, 120, 'dg-n-n'], [190, hist, 'dg-n-a'], [190 + hist, 40, 'dg-n-b'], [230 + hist, 10, 'dg-n-d']].forEach(function (s) {
        d.rect(s[0], y, Math.min(s[0] + s[1], lim) - s[0], 26, s[2]);
      });
      if (k === n + 1) d.playhead(lim, y - 3, y + 29);
      /* 重送的部分：上一列整列。走完的最後一列底下畫一條線，最後一格換成括號加字 */
      if (k === n && k >= 2 && t < RS.N) d.path('M70,' + (y + 29.5) + ' L' + (190 + hist) + ',' + (y + 29.5), 'dg-link-key');
    }
    if (t >= RS.N) {
      d.path('M70,182 L70,190 L390,190 L390,182', 'dg-link-key');
      d.text(230, 208, 'dg-k', '重送的部分：和上一步完全相同', 'middle');
    }
    [['dg-n-n', 'system prompt、tool 定義'], ['dg-n-a', '前幾步留下的歷史'], ['dg-n-b', '這一步新進來的'], ['dg-n-d', 'model 的 output']].forEach(function (g, i) {
      d.rect(510, 16 + 26 * i, 14, 14, g[0]);
      d.text(532, 28 + 26 * i, 'dg-c', g[1]);
    });
    return d.html();
  };
  CALCS.resend = function (fig, box) {
    var step = RS.IN + RS.OUT, FULL = rsCount(RS.N).nw + rsCount(RS.N).re;
    return makePlayer(fig, box, {
      speed: 0.7, hold: 900,
      frame: function (t) { return FRAMES.resend(t); },
      events: function () { return [0, 1, 2, 3, 4, 5]; },
      say: function (t) {
        var n = Math.floor(t + 1e-9), c = rsCount(RS.N);
        if (n === 0) return '每一列是一步送給 model 的 context。按播放或下一步，看它怎麼長出來。';
        if (n === 1) return 'Step 1：送出 ' + fmtK(RS.HEAD + RS.IN) + '，全部是第一次出現：system prompt 和 tool 定義 ' + fmtK(RS.HEAD) + '，加這一步新進來的 ' + fmtK(RS.IN) + '。Model 回了 ' + fmtK(RS.OUT) + ' 的 output（粉色）。';
        if (n < RS.N) return 'Step ' + n + '：上一步的黃色和粉色變成歷史，連同 system prompt 和 tool 定義一起重送，共 ' + fmtK(RS.HEAD + step * (n - 1)) + '；新進來的還是只有 ' + fmtK(RS.IN) + '。';
        return '五步送給 model 的合計 ' + fmtK(FULL) + '。第一次出現的只有 ' + fmtK(c.nw) + '：system prompt 和 tool 定義 ' + fmtK(RS.HEAD) + '，加五步各新進來的 ' + fmtK(RS.IN) + '。其餘 ' + fmtK(c.re) + ' 都是重送，佔 ' + Math.round(c.re / FULL * 100) + '%。';
      },
      aria: function (t) { return '每一步送給 model 的 context，現在走完 ' + Math.floor(t + 1e-9) + ' 步。'; },
      show: function (t, s, api) {
        var c = rsCount(t);
        api.set('t', '走完 ' + Math.floor(t + 1e-9) + ' 步');
        api.bar('nw', [c.nw], FULL);
        api.bar('re', [c.re], FULL);
        api.set('nw', fmtK(c.nw));
        api.set('re', fmtK(c.re));
      }
    });
  };

  /* L8 3.1：prefix cache 從第一個 token 往後比對。t = 比對到哪裡 (0–1)，c = 第三列改了哪裡。
     區塊的寬度當作 token 量：tools 66、system 90、messages 220、上一次的新內容 60、這一次的新內容 50。 */
  var PFX = { X0: 130, X1: 624, TAIL: 574 };
  function pfxRows(c) {
    var A = 'dg-n-a', D = 'dg-n-d', F = 'dg-n-focus', tail = [574, 624, 'new', 'dg-n-b'];
    var row3 = c === 0
      ? [[130, 196, '改 tool', F], [198, 288, 'system', D], [290, 510, 'messages', D], [512, 572, 'new', D], tail]
      : c === 2
        ? [[130, 196, 'tools', A], [198, 288, 'system', A], [290, 398, 'messages', A], [400, 440, '改', F], [442, 510, 'messages', D], [512, 572, 'new', D], tail]
        : [[130, 196, 'tools', A], [198, 238, '時間', F], [240, 298, 'system', D], [300, 510, 'messages', D], [512, 572, 'new', D], tail];
    return {
      row2: [[130, 196, 'tools', A], [198, 288, 'system', A], [290, 510, 'messages', A], [512, 572, 'new', A], tail],
      row3: row3,
      diff: c === 0 ? 130 : c === 2 ? 400 : 198,
      name: c === 0 ? '增減 tool 定義' : c === 2 ? '改寫舊的訊息' : '開頭放時間戳',
      where: c === 0 ? '一開頭的 tool 定義' : c === 2 ? 'messages 中間改過的那一則' : 'system 開頭的時間戳'
    };
  }
  /* token 量（區塊寬度）到游標為止：[cache hit, 重算, 新內容] */
  function pfxShare(row, cx) {
    var v = [0, 0, 0];
    row.forEach(function (b) {
      var w = Math.max(0, Math.min(b[1], cx) - b[0]);
      v[b[3] === 'dg-n-a' ? 0 : b[3] === 'dg-n-b' ? 2 : 1] += w;
    });
    return v;
  }
  FRAMES.prefix = function (t, c) {
    var d = Draw('px'), m = pfxRows(c), cx = PFX.X0 + (PFX.X1 - PFX.X0) * t;
    function row(blocks, y) {
      blocks.forEach(function (b) {
        var mid = (b[0] + b[1]) / 2;
        if (cx < b[1]) d.rect(b[0], y, b[1] - b[0], 36, 'dg-n-n', 4);
        if (cx > b[0]) d.rect(b[0], y, Math.min(b[1], cx) - b[0], 36, b[3], 4);
        if (b[3] !== 'dg-n-focus' || cx <= b[0]) d.text(mid, y + 23, 'dg-ls', b[2], 'middle');
        else if (cx >= b[1]) d.text(mid, y + 23, 'dg-l-on', b[2], 'middle');
        else d.splitText(mid, y + 23, 'dg-ls', 'dg-l-on', b[2], 'middle', b[0], y, cx - b[0], 36);
      });
    }
    d.text(14, 39, 'dg-cb', 'request N');
    [[130, 196, 'tools'], [198, 288, 'system'], [290, 510, 'messages']].forEach(function (b) {
      d.rect(b[0], 16, b[1] - b[0], 36, 'dg-n-n', 4);
      d.text((b[0] + b[1]) / 2, 39, 'dg-ls', b[2], 'middle');
    });
    d.rect(512, 16, 60, 36, 'dg-n-b', 4);
    d.text(542, 39, 'dg-ls', 'new', 'middle');
    d.text(582, 39, 'dg-c', '全部寫進 cache');
    d.text(14, 95, 'dg-cb', 'request N+1');
    d.text(14, 112, 'dg-c', '只在尾端加');
    row(m.row2, 76);
    if (cx >= PFX.TAIL) d.text(632, 99, 'dg-c', '青色讀 cache');
    d.text(14, 155, 'dg-cb', 'request N+1');
    d.text(14, 172, 'dg-c', m.name);
    row(m.row3, 136);
    if (cx >= m.diff) {
      d.text(Math.max(m.diff, 134), 130, 'dg-k', '第一個不同', null, true);
      d.text(632, 159, 'dg-k', '之後重算');
    }
    if (t < 1) d.playhead(cx, 66, 180);
    return d.html();
  };
  CALCS.prefix = function (fig, box) {
    var W = PFX.X1 - PFX.X0;
    var FULL = 486;   /* 第二列的總長，兩列用同一個分母 */
    function pct(v) { return Math.round(v[0] / FULL * 100) + '%'; }
    return makePlayer(fig, box, {
      speed: 0.22, hold: 900,
      frame: function (t, s) { return FRAMES.prefix(t, s.c); },
      events: function (s) {
        var e = [0, (pfxRows(s.c).diff - PFX.X0) / W, (PFX.TAIL - PFX.X0) / W, 1];
        return e.filter(function (v, i) { return i === 0 || v > e[i - 1]; });
      },
      x: function (t) { return PFX.X0 + W * t; },
      say: function (t, s) {
        var m = pfxRows(s.c), cx = PFX.X0 + W * t;
        if (t >= 1) return '結果：只在尾端加，cache hit ' + pct(pfxShare(m.row2, PFX.X1)) + '；' + m.name + '，cache hit ' + pct(pfxShare(m.row3, PFX.X1)) + '。越前面的東西改了，要重算的越多。';
        if (cx >= PFX.TAIL) return '第二列比到上一次的結尾才遇到新內容：前面全部是 cache hit，只有新加的一段要算。';
        if (cx >= m.diff) return '第三列在' + (/^[a-z]/i.test(m.where) ? ' ' : '') + m.where + '第一次和上一次不同。中間結果只和它前面的 token 有關，所以從這裡往後全部重算，就算後面的字一個都沒變。';
        return '從第一個 token 開始，拿這一次的 request 和 cache 裡的上一次比對。到這裡兩列都和上一次相同，都是 cache hit。';
      },
      aria: function (t, s) { return '三列 request，比對到 ' + Math.round(t * 100) + '%。第三列：' + pfxRows(s.c).name + '。'; },
      show: function (t, s, api) {
        var m = pfxRows(s.c), cx = PFX.X0 + W * t, a = pfxShare(m.row2, cx), b = pfxShare(m.row3, cx);
        api.set('t', Math.round(t * 100) + '%');
        api.set('c', m.name);
        api.set('n3', m.name);
        api.bar('r2', a, FULL);
        api.bar('r3', b, FULL);
        api.set('r2', pct(a), 'calc-win');
        api.set('r3', pct(b));
      }
    });
  };

  /* L8 3.7：batch 越大，每個 output token 要讀的 byte 越少，但 KV cache 攤不掉。
     t = batch 裡有幾個 request (1–52)。權重 141 GB，每個 request 的 KV cache 2.7 GB，記憶體 282 GB。 */
  var DEC = { W: 141, KV: 2.7, MEM: 282, PX: 465.6 / 141, MAX: 52 };
  FRAMES.decode = function (t) {
    var d = Draw('dc'), kv = DEC.KV * DEC.PX;
    function gb(b) { var v = DEC.W / b + DEC.KV; return (v >= 10 ? Math.round(v) : v.toFixed(1)) + ' GB'; }
    function row(y, b, name, note) {
      var w = DEC.W / b * DEC.PX;
      d.text(14, y + 16, 'dg-c', name);
      d.rect(170, y, w, 22, 'dg-n-a');
      d.rect(170 + w, y, kv, 22, 'dg-n-focus');
      d.text(170 + w + kv + 8.1, y + 16, 'dg-mn', gb(b) + (note || ''));
    }
    row(20, 1, 'batch 1');
    if (t >= 8) row(56, 8, 'batch 8');
    else if (t > 1) row(56, t, 'batch ' + Math.floor(t));
    if (t >= DEC.MAX) row(92, DEC.MAX, 'batch 52（放滿）', '，一半是 KV cache');
    else if (t > 8) row(92, t, 'batch ' + Math.floor(t));
    d.rect(170, 128, 14, 14, 'dg-n-a');
    d.text(190, 140, 'dg-c', '權重：整個 batch 共用，攤給 B 個 request');
    d.rect(170, 150, 14, 14, 'dg-n-focus');
    d.text(190, 162, 'dg-c', 'KV cache：每個 request 自己一份，攤不掉');
    return d.html();
  };
  CALCS.decode = function (fig, box) {
    function g(v) { return (v >= 10 ? Math.round(v) : Math.round(v * 10) / 10) + ' GB'; }
    return makePlayer(fig, box, {
      speed: 6, hold: 900,
      frame: function (t) { return FRAMES.decode(t); },
      events: function () { return [1, 2, 4, 8, 16, 32, 52]; },
      say: function (t) {
        var b = Math.floor(t + 1e-9), tot = DEC.W + DEC.KV * b;
        if (b <= 1) return 'Batch 1：這一輪把 ' + DEC.W + ' GB 的權重讀一遍，再讀這個 request 自己的 ' + DEC.KV + ' GB KV cache，只產生 1 個 token。';
        if (b >= DEC.MAX) return 'Batch 52：權重加 52 份 KV cache 共 ' + Math.round(tot) + ' GB，GPU 的 ' + DEC.MEM + ' GB 記憶體放滿，不能再加 request。這時每個 token 要讀 5.4 GB，一半是攤不掉的 KV cache。';
        return 'Batch ' + b + '：權重還是只讀一遍，' + b + ' 個 request 各拿它算出自己的下一個 token，每個 token 分到的權重是 ' + DEC.W + ' ÷ ' + b + ' ≈ ' + g(DEC.W / b) + '。每個 request 自己的 KV cache 還是 ' + DEC.KV + ' GB。';
      },
      aria: function (t) { return '每產生 1 個 output token 要從記憶體讀多少，batch 是 ' + Math.floor(t + 1e-9) + ' 個 request。'; },
      show: function (t, s, api) {
        var b = Math.floor(t + 1e-9);
        api.set('t', b + ' 個 request');
        api.bar('mem', [DEC.W, DEC.KV * b], DEC.MEM);
        api.set('mem', Math.round(DEC.W + DEC.KV * b) + ' GB');
        api.bar('tok', [DEC.W / b, DEC.KV], DEC.W + DEC.KV);
        api.set('tok', g(DEC.W / b + DEC.KV));
      }
    });
  };

  /* L8 8.1：完成時間看 critical path。t = 第幾秒 (0–60)，v = 加速哪一個（0 都不加速、1 A 快一倍、2 B 快一倍）。 */
  function cpModel(v) {
    var A = v === 1 ? 10 : 20, B = v === 2 ? 15 : 30, mx = Math.max(A, B), mn = Math.min(A, B);
    return {
      A: A, B: B, mx: mx, mn: mn, par: 10 + mx, seq: 10 + A + B, long: A > B ? 'A' : 'B', short: A > B ? 'B' : 'A',
      name: v === 1 ? 'A 快一倍' : v === 2 ? 'B 快一倍' : '都不加速'
    };
  }
  function cpSay(m, v, t) {
    var list = [
      [0, '兩種排法同時開始，都先做 plan。'],
      [5, 'Plan 做完。序列一次做一件，先做 A；平行把 A 和 B 同時派出去。'],
      [5 + m.mn, '平行：' + m.short + ' 做完了，但 merge 要等 ' + m.long + '，這條線空等 ' + (m.mx - m.mn) + ' 秒。'],
      [5 + m.mx, '平行：' + m.long + ' 做完，開始 merge。序列這時還在做 ' + (5 + m.mx < 5 + m.A ? 'A' : 'B') + '。'],
      [m.par, '平行在第 ' + m.par + ' 秒完成：plan 5 秒，加最長的 ' + m.long + ' ' + m.mx + ' 秒，加 merge 5 秒。'],
      [m.seq, '序列在第 ' + m.seq + ' 秒完成：四段時間全部相加。'],
      [60, v === 1 ? 'A 快一倍：序列從 60 秒變 50 秒，平行還是 40 秒，因為 A 不在 critical path 上。'
        : v === 2 ? 'B 快一倍：平行從 40 秒變 30 秒，而且 critical path 換成 plan → A → merge，下一個該加速的是 A。'
          : '序列 60 秒，平行 40 秒。平行的完成時間由 critical path（plan → B → merge）決定。']
    ];
    var msg = list[0][1];
    list.forEach(function (e) { if (e[0] <= t + 1e-9) msg = e[1]; });
    return msg;
  }
  FRAMES.cpath = function (t, v) {
    var d = Draw('cp'), m = cpModel(v), F = 'dg-n-focus';
    function x(s) { return 70 + 10 * s; }
    /* 一段工作：做完的塗滿，還沒開始的只有虛線框 */
    function blk(a, b, y, h, label, cls, small) {
      if (b - a < 0.01) return;
      var done = Math.min(t, b), mid = (x(a) + x(b)) / 2, ty = y + h / 2 + 5;
      var dark = small ? 'dg-c' : 'dg-ls', lite = small ? 'dg-c-on' : 'dg-l-on';
      if (t < b) d.rect(x(a) + 0.6, y + 0.6, 10 * (b - a) - 1.2, h - 1.2, 'dg-ghost', 4);
      if (t > a) d.rect(x(a), y, 10 * (done - a), h, cls, 4);
      if (cls !== F) d.text(mid, ty, 'dg-ls', label, 'middle');
      else if (t >= b) d.text(mid, ty, lite, label, 'middle');
      else if (t <= a) d.text(mid, ty, dark, label, 'middle');
      else d.splitText(mid, ty, dark, lite, label, 'middle', x(a), y, 10 * (done - a), h);
    }
    d.text(14, 39, 'dg-cb', '序列');
    blk(0, 5, 18, 32, 'plan', 'dg-n-n');
    blk(5, 5 + m.A, 18, 32, 'A', 'dg-n-c');
    blk(5 + m.A, 5 + m.A + m.B, 18, 32, 'B', 'dg-n-c');
    blk(m.seq - 5, m.seq, 18, 32, 'merge', 'dg-n-n');
    if (t >= m.seq) d.text(x(m.seq) + 8, 39, 'dg-cb', m.seq + ' 秒', null, true);
    d.text(14, 118, 'dg-cb', '平行');
    blk(0, 5, 78, 74, 'plan', F, true);
    blk(5, 5 + m.A, 78, 34, 'A', m.long === 'A' ? F : 'dg-n-c');
    blk(5, 5 + m.B, 118, 34, 'B', m.long === 'B' ? F : 'dg-n-c');
    if (m.mx > m.mn) blk(5 + m.mn, 5 + m.mx, m.short === 'A' ? 78 : 118, 34, '等 ' + (m.mx - m.mn) + ' 秒', 'dg-n-n');
    blk(5 + m.mx, m.par, 78, 74, 'merge', F, true);
    if (t >= m.par) {
      d.text(x(m.par) + 8, 112, 'dg-k', m.par + ' 秒', null, true);
      if (v === 0) {
        d.text(530, 92, 'dg-c', 'A 快一倍：仍是 40 秒', null, true);
        d.text(530, 132, 'dg-k', 'B 少 10 秒：30 秒', null, true);
      }
    }
    d.path('M70,164 L670,164', 'dg-link');
    [0, 10, 20, 30, 40, 50, 60].forEach(function (s) {
      d.vline(x(s), 164, 169, 'dg-link');
      d.text(x(s), 185, 'dg-mn', s, 'middle');
    });
    d.text(670, 201, 'dg-c', '秒', 'end');
    if (t < 60) d.playhead(x(t), 10, 164, true);
    return d.html();
  };
  CALCS.cpath = function (fig, box) {
    return makePlayer(fig, box, {
      speed: 7, hold: 800,
      frame: function (t, s) { return FRAMES.cpath(t, s.v); },
      events: function (s) {
        var m = cpModel(s.v);
        return [0, 5, 5 + m.mn, 5 + m.mx, m.par, m.seq, 60].sort(function (a, b) { return a - b; })
          .filter(function (e, i, arr) { return i === 0 || e > arr[i - 1]; });
      },
      x: function (t) { return 70 + 10 * t; },
      say: function (t, s) { return cpSay(cpModel(s.v), s.v, t); },
      aria: function (t, s) { return '同一個任務的兩種排法，橫軸是時間，現在是第 ' + Math.floor(t) + ' 秒，' + cpModel(s.v).name + '。'; },
      show: function (t, s, api) {
        var m = cpModel(s.v), a = Math.min(t, m.seq), b = Math.min(t, m.par);
        api.set('t', '第 ' + Math.floor(t) + ' 秒');
        api.set('v', m.name);
        api.bar('seq', [a], 60);
        api.bar('par', [b], 60);
        api.set('seq', Math.floor(a) + ' 秒' + (t >= m.seq ? '' : '…'));
        api.set('par', Math.floor(b) + ' 秒' + (t >= m.par ? '' : '…'), t >= m.par ? 'calc-win' : '');
      }
    });
  };

  var figs = document.querySelectorAll('figure[data-calc]');
  for (var i = 0; i < figs.length; i++) {
    var fig = figs[i];
    var make = CALCS[fig.getAttribute('data-calc')];
    var box = fig.querySelector('.calc');
    if (!make || !box) continue;
    var c = make(fig, box);
    if (!c) continue;
    live.push(c);
    box.hidden = false;
  }
  window.cs2680Calc = { resetAll: function () { live.forEach(function (c) { c.reset(); }); }, frames: FRAMES };
})();
