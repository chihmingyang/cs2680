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
  window.cs2680Calc = { resetAll: function () { live.forEach(function (c) { c.reset(); }); } };
})();
