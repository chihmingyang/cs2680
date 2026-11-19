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
      ' 分鐘，第 ' + m.back + '、' + (m.back + 2) + ' 分鐘回來。' + ttlSay(m, t) +
      '到這時候，5 分鐘 TTL 花了 ' + fmtK(c.sum5) + '，1 小時 TTL 花了 ' + fmtK(c.sum1) + '。';
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

  CALCS.ttl = function (fig, box) {
    function q(sel) { return box.querySelector(sel); }
    var svg = fig.querySelector('svg');
    var inT = q('[data-k="t"]'), inD = q('[data-k="d"]');
    var outT = q('[data-v="t"]'), outD = q('[data-v="d"]');
    var out5 = q('[data-v="c5"]'), out1 = q('[data-v="c1"]');
    var bar5 = q('[data-bar="c5"]'), bar1 = q('[data-bar="c1"]');
    var res = q('.calc-out'), btn = q('.calc-reset');
    var play = q('[data-act="play"]'), step = q('[data-act="step"]');
    if (!svg || !inT || !inD || !outT || !outD || !out5 || !out1 || !bar5 || !bar1 || !res || !btn || !play || !step) return null;

    var END = TTL.END, D0 = inD.defaultValue;
    var FULL = 1.25 * (TTL.C + TTL.G);       /* the longest bar: one rewrite of C plus the new content */
    var SPEED = 5, HOLD = 700;               /* minutes per second; pause at each event, ms */
    var orig = {
      svg: svg.innerHTML, label: svg.getAttribute('aria-label'),
      t: outT.innerHTML, d: outD.innerHTML, c5: out5.innerHTML, c1: out1.innerHTML,
      b5: bar5.innerHTML, b1: bar1.innerHTML, res: res.innerHTML, play: play.innerHTML
    };
    var cur = END, raf = 0, lastTs = 0, hold = 0, said = '';
    /* no moving playhead for readers who asked for less motion: they step or drag */
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) play.hidden = true;

    function widths(bar, vals) {
      for (var i = 0; i < vals.length; i++) {
        if (bar.children[i]) bar.children[i].style.width = (vals[i] / FULL * 100).toFixed(2) + '%';
      }
    }
    /* on a narrow screen the figure scrolls sideways: keep the playhead in view */
    var scroller = fig.querySelector('.scroll');
    function follow() {
      if (!scroller || scroller.scrollWidth <= scroller.clientWidth + 1) return;
      var px = (TTL.X0 + TTL.PX * cur) / 720 * svg.getBoundingClientRect().width;
      if (px < scroller.scrollLeft + 48 || px > scroller.scrollLeft + scroller.clientWidth - 48) {
        scroller.scrollLeft = Math.max(0, px - scroller.clientWidth / 2);
      }
    }
    function render() {
      var d = +inD.value, m = ttlModel(d), c = ttlCost(m, cur);
      svg.innerHTML = FRAMES.ttl(cur, d);
      follow();
      outT.textContent = '第 ' + Math.floor(cur) + ' 分鐘';
      outD.textContent = d + ' 分鐘（5 分鐘的 cache ' + (m.expired ? '會過期' : '還在') + '）';
      widths(bar5, [c.new5, c.miss5, c.read5]);
      widths(bar1, [c.new1, 0, c.read1]);
      out5.textContent = fmtK(c.sum5);
      out1.textContent = fmtK(c.sum1);
      var msg = ttlSay(m, cur);
      if (msg !== said) {
        said = msg;
        res.textContent = msg;
        svg.setAttribute('aria-label', ttlAria(m, cur));
      }
      btn.disabled = false;
    }
    function restore() {
      svg.innerHTML = orig.svg;
      svg.setAttribute('aria-label', orig.label);
      outT.innerHTML = orig.t;
      outD.innerHTML = orig.d;
      out5.innerHTML = orig.c5;
      out1.innerHTML = orig.c1;
      bar5.innerHTML = orig.b5;
      bar1.innerHTML = orig.b1;
      res.innerHTML = orig.res;
      said = '';
      btn.disabled = true;
    }
    /* the default (last frame, the text's example) is the source SVG, byte for byte */
    function show() {
      if (!raf && cur >= END && inD.value === D0) restore();
      else render();
    }
    function stop() {
      if (raf) cancelAnimationFrame(raf);
      raf = 0; lastTs = 0; hold = 0;
      play.innerHTML = orig.play;
    }
    function nextEvent() {
      var ev = ttlModel(+inD.value).ev;
      for (var i = 0; i < ev.length; i++) if (ev[i].t > cur + 1e-6) return ev[i].t;
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
      if (cur >= END) cur = 0;
      inT.value = cur;
      play.textContent = '❚❚ 暫停';
      hold = HOLD;
      raf = requestAnimationFrame(tick);
      render();
    });
    step.addEventListener('click', function () {
      stop();
      cur = cur >= END ? 0 : nextEvent();
      inT.value = cur;
      show();
    });
    inT.addEventListener('input', function () { stop(); cur = +inT.value; show(); });
    inD.addEventListener('input', function () { stop(); cur = END; inT.value = END; show(); });
    function reset() {
      stop();
      inD.value = D0;
      inT.value = END;
      cur = END;
      restore();
    }
    btn.addEventListener('click', reset);
    return { reset: reset };
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
