/* CS2680 觀念導讀 — code snippet colors, loaded on every page that has code
   (lecture pages and l02-readings.html). No storage, no network. */
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
    if (/^\s*\$ /.test(text)) return 'shell';              // a typed command and its output
    if (/輸出/.test(c)) return 'text';                        // "x.py 的輸出": output, not the file
    if (/^(terminal|shell)/.test(c)) return 'sh';
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
