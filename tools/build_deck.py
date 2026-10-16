#!/usr/bin/env python3
"""Render a lecture page in the slide + notes format from content/lXX.json.

Usage: python3 -I build_deck.py content/l02.json [--out site/l02.html]

The page works in two modes (see deck.js):
  - no PDF loaded: story line per section, then only the notes, each tagged
    with its slide page (links open the official PDF at that page);
  - PDF loaded by the viewer: every slide page is drawn in the browser, with
    its note beside it.
JSON fields: key no date part title en pdf pages prev next proto? tldr
sections[{id range title toc story[] notes[{pages[] title body}]}] quiz[{q a}] reading[]
"""
import html
import json
import sys
from pathlib import Path

FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
         "&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600"
         "&family=Noto+Sans+TC:wght@400;500;700&display=swap")
SLIDES = "https://cs2680.com/slides/"


def esc(s):
    return html.escape(s, quote=True)


def page_label(pages):
    return f"p.{pages[0]}" if len(pages) == 1 else f"p.{pages[0]}–{pages[-1]}"


def rows_html(d, sec):
    lo, hi = sec["range"]
    by_first = {n["pages"][0]: n for n in sec["notes"]}
    out = []
    for n in range(lo, hi + 1):
        note = by_first.get(n)
        label = page_label(note["pages"]) if note else f"p.{n}"
        aria = f"開啟原 slide 第 {n} 頁"
        slot = (f'<div class="slot"><a class="pg" href="{SLIDES}{d["pdf"]}#page={n}" target="_blank" rel="noopener" '
                f'aria-label="{aria}">{label}</a>'
                f'<div class="frame"><canvas role="img" aria-label="Slide 第 {n} 頁"></canvas></div></div>')
        if note:
            ann = f'<div class="ann"><h3>{note["title"]}</h3>{note["body"]}</div>'
            out.append(f'            <div class="srow" id="p{n}" data-page="{n}">{slot}\n              {ann}\n            </div>')
        else:
            out.append(f'            <div class="srow bare" id="p{n}" data-page="{n}">{slot}</div>')
    return "\n".join(out)


def section_html(d, sec):
    lo, hi = sec["range"]
    rng = f"p.{lo}–{hi}"
    story = "\n".join(f"            {p}" for p in sec["story"])
    label = '          <p class="notes-label">補充</p>\n' if sec["notes"] else ""
    return f"""      <section class="part" id="{sec['id']}" data-pages="{lo}-{hi}">
        <header class="part-head">
          <p class="range">{rng}</p>
          <h2>{sec['title']}</h2>
        </header>
        <div class="part-body">
          <div class="story">
{story}
          </div>
          <a class="readslides" href="{SLIDES}{d['pdf']}#page={lo}" target="_blank" rel="noopener">讀 slide <span>{rng}</span> ↗</a>
{label}          <div class="rows">
{rows_html(d, sec)}
          </div>
        </div>
      </section>"""


def build(d):
    no = d["no"]
    prev, nxt = d.get("prev"), d.get("next")
    nav = []
    if prev:
        nav.append(f'<a href="{prev["key"]}.html" rel="prev">← L{int(prev["key"][1:])}</a>')
    nav.append(f'<span class="here">L{no} / 8</span>')
    if nxt:
        nav.append(f'<a href="{nxt["key"]}.html" rel="next">L{int(nxt["key"][1:])} →</a>')
    toc = "\n".join(
        f'          <li><a href="#{s["id"]}">{s["toc"]}<span>p.{s["range"][0]}–{s["range"][1]}</span></a></li>'
        for s in d["sections"]) + '\n          <li><a href="#wrap">自我檢查<span>—</span></a></li>'
    core = "\n".join(f"      <li><span>{c}</span></li>" for c in d["tldr"]["core"])
    quiz = "\n".join(
        f'          <details>\n            <summary>{q["q"]}</summary>\n            <div class="answer">{q["a"]}</div>\n          </details>'
        for q in d["quiz"])
    reading = "\n".join(f"          <li>{r}</li>" for r in d["reading"])
    sections = "\n\n".join(section_html(d, s) for s in d["sections"])
    proto = f'  <p class="proto">{d["proto"]}</p>\n\n' if d.get("proto") else ""
    left = (f'<a class="prev" href="{prev["key"]}.html"><span>← 上一堂 L{int(prev["key"][1:])}</span>{prev["title"]}</a>'
            if prev else '<a class="prev" href="index.html"><span>← 回總覽</span>CS2680 觀念導讀</a>')
    right = (f'<a class="next" href="{nxt["key"]}.html"><span>下一堂 L{int(nxt["key"][1:])} →</span>{nxt["title"]}</a>'
             if nxt else '<a class="next" href="index.html"><span>回總覽 →</span>CS2680 觀念導讀</a>')
    pdf_url = SLIDES + d["pdf"]
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="claude:viewport-fit-sides" content="cover">
<title>L{no} {esc(d['title'])} · CS2680</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header class="topbar">
  <div class="topbar-inner gutter">
    <a class="brand" href="index.html">CS2680 <span>觀念導讀</span></a>
    <nav class="lecnav" aria-label="講次">
      {''.join(nav)}
    </nav>
    <button class="toggle" id="gist-toggle" type="button" aria-pressed="false">只看故事線</button>
  </div>
</header>

<main class="page gutter" data-lecture="{d['key']}" data-format="companion" data-pdf="{d['pdf']}" data-pages-total="{d['pages']}">
{proto}  <header class="lecture-head">
    <p class="eyebrow">Lecture {no:02d} · {d['date']} · {d['part']}</p>
    <h1>{esc(d['title'])}</h1>
    <p class="en-title">{esc(d['en'])}</p>
    <ul class="meta">
      <li><span class="k">Slides</span><a href="{pdf_url}" target="_blank" rel="noopener">{d['pdf']} ↗</a></li>
      <li><span class="k">頁數</span>{d['pages']}</li>
      <li><span class="k">說明</span><span><span class="read-time">約 10 分鐘</span>（不含看 slide）</span></li>
    </ul>
  </header>

  <section class="tldr" aria-labelledby="tldr-h">
    <h2 class="label" id="tldr-h">先看這裡</h2>
    <p class="thesis">{d['tldr']['thesis']}</p>
    <ul class="core">
{core}
    </ul>
    <p class="readhow">讀法：先在下方載入 slides。之後從上讀到下：每一段先讀故事線，再看 slide;旁邊的文字只補 slide 沒說的事。</p>
  </section>

  <section class="loader" id="loader" aria-live="polite" aria-label="載入 slides">
    <div class="loader-empty">
      <p><b>圖文對照</b>:載入這堂的 slides PDF 後，每一頁 slide 會直接畫在說明旁邊。</p>
      <ol>
        <li>從課程網站下載 <a href="{pdf_url}" target="_blank" rel="noopener">{d['pdf']} ↗</a></li>
        <li>把 PDF 拖進這個頁面，或 <button type="button" id="pdf-pick">選擇 PDF</button></li>
      </ol>
      <p class="fine">PDF 只在你的瀏覽器裡開啟，不會上傳。這個瀏覽器會記住它，下次打開不用再載入。</p>
      <input class="visually-hidden" type="file" id="pdf-input" accept="application/pdf,.pdf" tabindex="-1" aria-hidden="true">
    </div>
    <div class="loader-done" hidden><span>已載入 <code class="fname"></code></span><button type="button" id="pdf-clear">移除</button></div>
    <p class="loader-msg" hidden></p>
  </section>

  <div class="layout">
    <nav class="toc" aria-label="本堂目錄">
      <details open>
        <summary>本堂目錄</summary>
        <ol>
{toc}
        </ol>
      </details>
    </nav>

    <div class="content">

{sections}

      <section class="wrap" id="wrap" aria-label="自我檢查">
        <h2>自我檢查</h2>
        <div class="quiz">
{quiz}
        </div>

        <h2>延伸閱讀</h2>
        <ul class="reading">
{reading}
        </ul>

        <label class="readmark"><input type="checkbox" id="read-box"> 我讀完這一堂了(只存在你的瀏覽器)</label>
      </section>

      <nav class="pager" aria-label="上一堂與下一堂">
        {left}
        {right}
      </nav>
      <p class="fineprint">本頁是 CS2680 slides 的補充筆記。Slide 畫面由你自己下載的官方 PDF,在你的瀏覽器裡產生;本站不存放 slides。原始 slides 與課程內容的版權屬於 Juncheng Yang 與 Harvard CS2680。Claude Code 的指令與設定依據 2026 年 10 月的官方文件。</p>
    </div>
  </div>
</main>
<script src="pdf.min.js"></script>
<script src="deck.js"></script>
<script src="app.js"></script>
</body>
</html>
"""


def main():
    src = Path(sys.argv[1])
    d = json.loads(src.read_text(encoding="utf-8"))
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else (Path(__file__).resolve().parent.parent / "site") / f"{d['key']}.html"
    out.write_text(build(d), encoding="utf-8")
    print(f"wrote {out} ({sum(len(s['notes']) for s in d['sections'])} notes, {d['pages']} pages)")


if __name__ == "__main__":
    main()
