#!/usr/bin/env python3
"""Insert the 「7 · 交作業」 section, its TOC entry and submit.js into each lecture page.
Idempotent: a page that already has #s-submit is left alone.
Usage: python3 -I tools/add_submit.py site
"""
import re
import sys
from pathlib import Path

SITE = Path(sys.argv[1])

SECTION = """      <!-- ===================== 7 交作業 ===================== -->
      <section class="part" id="s-submit">
        <header class="part-head">
          <p class="kicker">7 · 交作業</p>
          <h2>上傳你的討論</h2>
          <p class="lede">讀書會前，把你對進階題的回答貼在這裡。所有成員都看得到彼此的內容。重新送出會覆蓋你上一次的那一份。<a href="submissions.html">收作業總表</a>列出誰交了哪幾堂。</p>
        </header>
        <form class="subform" id="sub-form" hidden>
          <label class="field"><span>顯示名稱（選填）</span><input type="text" id="sub-nick" maxlength="40" autocomplete="nickname" placeholder="留空就用你的帳號名稱"></label>
          <label class="field"><span>你的討論</span><textarea id="sub-text" rows="10" placeholder="Q1. &#10;Q2. &#10;…"></textarea></label>
          <div class="field" id="sub-filerow" hidden>
            <label for="sub-file"><span>附件（選填：PDF、圖片、Markdown、txt、csv、json，20 MB 以內）</span></label>
            <input type="file" id="sub-file" accept=".pdf,.png,.jpg,.jpeg,.gif,.webp,.md,.txt,.csv,.json">
            <ul class="attach" id="sub-attach"></ul>
          </div>
          <div class="copyrow">
            <button type="submit" class="copybtn" id="sub-send">送出</button>
            <button type="button" class="ghostbtn" id="sub-copy">複製成文字</button>
            <span class="copyhint" id="sub-status" role="status"></span>
          </div>
        </form>
        <p class="sub-note" id="sub-note" role="status">連線中…</p>
        <h3 class="subhead">已收到的討論 <span class="count" id="sub-count"></span></h3>
        <ol class="sublist" id="sub-list"><li class="empty">載入中…</li></ol>
      </section>

"""

TOC_ITEM = '          <li><a href="#s-submit">7 交作業<span>上傳</span></a></li>\n'

for page in sorted(SITE.glob("l0*.html")):
    html = page.read_text(encoding="utf-8")
    if 'id="s-submit"' in html:
        print(f"{page.name}: already has #s-submit")
        continue
    # 1. section: before the 延伸閱讀 comment when present, else before section.wrap
    m = re.search(r'^[ \t]*<!-- =+ 延伸閱讀 =+ -->\n', html, re.M)
    if not m:
        m = re.search(r'^[ \t]*<section class="wrap"', html, re.M)
    assert m, f"{page.name}: no wrap section"
    html = html[: m.start()] + SECTION + html[m.start():]
    # 2. TOC entry before the #wrap item
    toc = re.search(r'^[ \t]*<li><a href="#wrap">', html, re.M)
    assert toc, f"{page.name}: no #wrap toc item"
    html = html[: toc.start()] + TOC_ITEM + html[toc.start():]
    # 3. script
    assert html.count('<script src="app.js"></script>') == 1, page.name
    html = html.replace('<script src="app.js"></script>', '<script src="app.js"></script>\n<script src="submit.js"></script>')
    page.write_text(html, encoding="utf-8")
    print(f"{page.name}: inserted")
