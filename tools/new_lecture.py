#!/usr/bin/env python3
"""Write the skeleton of a NEW v7 lecture page (2026-11-06; L9–L11 were the first).

Usage:
  python3 -I tools/new_lecture.py l09 --date 2026-10-19 --part "Part II" \
      --title "LLM 的結構與 serving 的帳" --en "Efficient LLM serving basics I: intro to LLMs" \
      --pdf 9_llm_serving_basics_1.pdf --pages 51
  # a lecture with two decks (L10): repeat --pdf / --pages; data-pdf is the first deck,
  # data-pages-total the sum, the meta row lists both
  python3 -I tools/new_lecture.py l10 ... --pdf 10_llm_serving_basics_2a.pdf --pages 41 --deck-date 10/21 \
      --pdf 10_llm_serving_basics_2b.pdf --pages 55 --deck-date 11/02

What you get (docs/lXX.html; refuses to overwrite unless --force):
  head, topbar (← previous lecture, "LX / N"), this page's sidenav (built like add_lecture.py would),
  main[data-lecture][data-pdf][data-pages-total], lecture-head (eyebrow with「· 依想法重組」, h1, en-title, meta),
  placeholder tldr and #s-ideas, the fixed frame of #s-discuss (tabs, ledes, copy buttons with the right
  data-title / data-slides, textarea, quiz, #s-submit shell), #s-try, #wrap (rg-legend, readmark),
  pager (← previous, 回總覽), fineprint, scripts. Copied from docs/l05.html, the v7 template.

Then write the fragments in notes/lXX/ (head.html, i1.html…, tldr.html, fineprint.html, and the whole
sections discuss.html, try.html, wrap.html) and run tools/assemble_v7.py docs/lXX.html notes/lXX.
Wire it to the site last: add_lecture.py, then discuss.py (WORKFLOW B5).
"""
import argparse
import html as H
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import add_lecture as al  # noqa: E402

E = 'target="_blank" rel="noopener"'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("--date", required=True)
    ap.add_argument("--part", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--en", required=True)
    ap.add_argument("--pdf", action="append", required=True)
    ap.add_argument("--pages", action="append", type=int, required=True)
    ap.add_argument("--deck-date", action="append", help="label per deck when there are two, e.g. 10/21")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    key, no = a.key, int(a.key[1:])
    if len(a.pdf) != len(a.pages):
        ap.error("one --pages per --pdf")
    out = SITE / f"{key}.html"
    if out.exists() and not a.force:
        sys.exit(f"{out} exists (use --force)")
    tpl = (SITE / "l05.html").read_text(encoding="utf-8")
    prev = al.meta(SITE / f"l{no - 1:02d}.html")
    title, en = H.escape(a.title, quote=False), H.escape(a.en, quote=False)
    total = sum(a.pages)

    head = tpl[:tpl.index("</head>") + len("</head>")]
    head = re.sub(r"<title>.*?</title>", f"<title>L{no} {title} · CS2680</title>", head)
    topbar = tpl[tpl.index('<header class="topbar">'):tpl.index("</header>") + len("</header>")]
    topbar = re.sub(r'(<nav class="lecnav" aria-label="講次">).*?(</nav>)',
                    rf'\1\n      <a href="{prev["key"]}.html" rel="prev">← L{prev["no"]}</a>\n'
                    rf'      <span class="here">L{no} / {no}</span>\n    \2', topbar, flags=re.S)
    aside = tpl[tpl.index('<aside class="sidenav"'):tpl.index("</aside>") + len("</aside>")]
    tabs = re.search(r'[ \t]*<div class="qtabs".*?</div>\n', tpl, re.S).group(0)
    legend = re.search(r'[ \t]*<p class="rg-legend">.*?</p>\n', tpl).group(0)
    readmark = re.search(r'[ \t]*<label class="readmark">.*?</label>\n', tpl).group(0)
    submit_lis = re.search(r'<ul class="limits gh-how">.*?</ul>', tpl, re.S).group(0)

    if len(a.pdf) == 1:
        slides = f'<li><span class="k">Slides</span><a href="https://cs2680.com/slides/{a.pdf[0]}" {E}>{a.pdf[0]} ↗</a></li>'
        pages = str(a.pages[0])
    else:
        # one li per deck: two links in one li overflow the 390px layout (L10, 2026-11-06).
        # --deck-date gives each deck's date for its label; without it the labels are Slides 1, Slides 2
        labels = a.deck_date or [str(i) for i in range(1, len(a.pdf) + 1)]
        slides = "\n      ".join(f'<li><span class="k">Slides {d}</span><a href="https://cs2680.com/slides/{p}" {E}>{p} ↗</a></li>'
                                 for d, p in zip(labels, a.pdf))
        pages = f"{total}（" + "、".join(f"{p.rsplit('_', 1)[-1].split('.')[0]} {n}" for p, n in zip(a.pdf, a.pages)) + "）"
    url = f"https://chihmingyang.github.io/cs2680/{key}.html"
    s = f"""{head}
<body>
{topbar}

<div class="shell">

{aside}
<div class="sn-scrim" hidden></div>
<main class="page gutter article" data-lecture="{key}" data-format="article" data-pdf="{a.pdf[0]}" data-pages-total="{total}">
  <header class="lecture-head">
    <p class="eyebrow">Lecture {no:02d} · {a.date} · {a.part} · 依想法重組</p>
    <h1>{title}</h1>
    <p class="en-title">{en}</p>
    <ul class="meta">
      {slides}
      <li><span class="k">頁數</span>{pages}</li>
      <li><span class="k">閱讀</span><span class="read-time">約 1 分鐘</span></li>
      <li><span class="k">註</span><span class="deep-time">約 1 分鐘</span>，收合</li>
      <li><span class="k">全部展開</span><span class="full-time">約 1 分鐘</span></li>
    </ul>
  </header>

  <section class="tldr" aria-labelledby="tldr-h">
    <h2 class="label" id="tldr-h">先看這裡</h2>
    <p class="thesis">（待寫）</p>
    <ul class="core">
      <li><span><b>（待寫）</b></span></li>
    </ul>
  </section>

  <div class="layout">
    <div class="content">
      <section class="part" id="s-ideas">
        <header class="part-head">
          <p class="kicker">1 · 核心觀念</p>
          <h2>（待寫）</h2>
          <p class="lede">（待寫）</p>
        </header>
        <div class="ideas">
          <div class="idea" id="i1">
            <h3><span class="idea-no">1</span>（待寫）</h3>
            <div class="prose"><p>（待寫）</p></div>
          </div>
        </div>
      </section>

      <!-- ===================== 2 問題討論 ===================== -->
      <section class="part" id="s-discuss">
        <header class="part-head">
          <p class="kicker">2 · 問題討論</p>
          <h2>讀書會討論題</h2>
          <p class="lede">分兩組。基礎題在讀文章之前看，帶著問題讀，答案都在文章裡；卡住的地方，按題目下面的連結，到這堂的 GitHub 討論串隨手寫。進階題讀完文章後先想一想，讀書會當天一起討論。</p>
        </header>
{tabs}        <div class="qset" id="qset-basic" role="tabpanel" aria-labelledby="tab-basic">
          <p class="qset-lede">讀文章之前先看一遍這 5 題。它們依核心觀念的章節排列，每題標了答案在哪幾章。讀到那幾章時，把答案記下來；讀完再展開「參考答案與重點複習」對照：它先直接回答，再把這一題的觀念整理成複習筆記，有些附圖。卡住的地方，按題目下面的「到 GitHub 回答這一題」留言。</p>
          <div class="copyrow">
            <button type="button" class="copybtn" data-copy="basic" data-title="CS2680 L{no} 基礎題（帶著問題讀文章）：{title} {url}">複製基礎題</button>
            <span class="copyhint">只複製題目與章節，方便貼到群組。</span>
          </div>
          <ol class="qlist qlist-basic">
            <!-- li.bq#b1 … #b5 -->
          </ol>
        </div>
        <div class="qset" id="qset-adv" role="tabpanel" aria-labelledby="tab-adv" hidden>
          <p class="qset-lede">這 3 題留到讀書會當天一起討論，不用先寫在 GitHub。讀完文章後，先挑一題想一想。每個回答要點下面有一行提示。不用每點都答，挑一點想清楚就可以。不知道怎麼開頭，就展開「作答範本」，照著填空。「參考觀點與追問」建議討論後再展開。</p>
          <div class="copyrow">
            <button type="button" class="copybtn" data-copy="adv" data-title="CS2680 L{no} 進階題（讀書會討論）：{title}" data-slides="https://cs2680.com/slides/{a.pdf[0]}">複製進階題</button>
            <span class="copyhint">只複製題目、情境與回答要點，方便貼到群組。</span>
          </div>
          <ol class="qlist">
            <!-- li.dq#q1 … #q3 -->
          </ol>
        </div>
        <textarea class="copybox" id="copy-fallback" rows="8" readonly hidden aria-label="討論題文字，可手動複製"></textarea>

        <h3 class="subhead">自我檢查</h3>
        <div class="quiz">
          <!-- 3 × details > summary + div.answer -->
        </div>
        <div class="submit" id="s-submit">
          <h3 class="subhead">到 GitHub 寫你的答案</h3>
        </div>
      </section>

      <!-- ===================== 3 動手試試 ===================== -->
      <section class="part" id="s-try">
        <header class="part-head">
          <p class="kicker">3 · 動手試試</p>
          <h2>照著做一次</h2>
          <p class="lede">（待寫）點開才會展開。</p>
        </header>
        <div class="exlist">
        </div>
      </section>

      <!-- ===================== 4 延伸閱讀 ===================== -->
      <section class="wrap" id="wrap" aria-label="延伸閱讀">
        <p class="kicker">4 · 延伸閱讀</p>
        <h2>延伸閱讀</h2>
        <p class="rg-intro">（待寫）</p>
{legend}        <ol class="rg">
        </ol>

{readmark}      </section>

      <nav class="pager" aria-label="上一堂與總覽">
        <a class="prev" href="{prev["key"]}.html"><span>← 上一堂 L{prev["no"]}</span>{H.escape(prev["title"], quote=False)}</a>
        <a class="next" href="index.html"><span>回總覽 →</span>CS2680 觀念導讀</a>
      </nav>
      <p class="fineprint">本文取材自 CS2680 L{no} 的 slides 與下列來源，但不照 slides 的順序；標明「本文」的段落是本文的判斷，不代表講者。原始 slides 與課程內容的版權屬於 Juncheng Yang 與 Harvard CS2680。（待寫：來源）</p>
    </div>
  </div>
</main>
</div>
<script src="app.js"></script>
<script src="code.js"></script>
</body>
</html>
"""
    assert submit_lis  # the #s-submit block itself is filled by discuss.py
    out.write_text(s, encoding="utf-8")
    # this page's own sidenav, the way add_lecture.py builds it
    lecs = al.lectures()
    s = al.rebuild_sidenav(out.name, out.read_text(encoding="utf-8"), lecs, key)
    out.write_text(s, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(s):,} bytes). Next: fragments in notes/{key}/, then "
          f"python3 -I tools/assemble_v7.py docs/{key}.html notes/{key}")


if __name__ == "__main__":
    main()
