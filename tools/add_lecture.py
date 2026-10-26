#!/usr/bin/env python3
"""Wire a finished lecture page into the rest of the site.

Usage:
  python3 -I tools/add_lecture.py docs/l09.html --sum "一句話摘要（首頁講次列表用）"
  python3 -I tools/add_lecture.py --check      # rebuild every sidenav in memory, write nothing,
                                               # report pages whose sidenav would change

The new page must already pass check_article.py and check_discuss.py. Everything the
script needs is read from that page:
  key      main[data-lecture]            (l09)
  title    h1 inside header.lecture-head
  en       p.en-title
  date     p.eyebrow "Lecture 09 · 2026-10-19 · Part II"
  part     the same eyebrow ("Part I" / "Part II")
  pdf      main[data-pdf]; pages main[data-pages-total]; read time span.read-time

What it changes (idempotent; running it twice changes nothing the second time):
  1. Every page with aside.sidenav (index, lXX): the lecture rows are rebuilt
     from all lecture pages, grouped by part. Each page keeps its own expanded block;
     the new page gets an expanded block built from its sections. The "slides 公開後加入"
     line stays after the last part; once a Part II page exists it reads
     "Part II 其他講次在 slides 公開後加入".
  2. Every lecture page: "LX / N" in nav.lecnav uses the new N.
  3. The previous lecture: nav.lecnav gets "LX →"; its pager's right link points to the new page.
  4. index.html: a row in 已公開的講次; the row with the same date leaves ul.later.
     Course-map chips are NOT added: pick anchors by hand (add_anchors.py prints them).
Afterwards run tools/discuss.py on the new page: it opens the GitHub issues and writes the links.
"""
import argparse
import html as H
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "docs"
WRAP_HEAD = re.compile(r"\A<!doctype html><html><head>.*?</head><body>\n", re.S)
WRAP_TAIL = re.compile(r"\n*</body></html>\s*\Z")


def read(p):
    return p.read_text(encoding="utf-8")


def strip_wrapper(s):
    if WRAP_HEAD.match(s):
        s = WRAP_HEAD.sub("", s, count=1)
        s = WRAP_TAIL.sub("\n", s)
    return s


def text(fragment):
    return H.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def meta(path):
    s = read(path)
    m = re.search(r'<main[^>]*data-lecture="(l\d\d)"[^>]*>', s)
    if not m:
        return None
    tag = m.group(0)
    head = s[s.index("<header class=\"lecture-head\">"):]
    eyebrow = text(re.search(r'<p class="eyebrow">(.*?)</p>', head, re.S).group(1))
    date = re.search(r"\d{4}-(\d\d-\d\d)", eyebrow).group(1)
    part = re.search(r"Part [IVX]+", eyebrow).group(0)
    return {
        "key": m.group(1),
        "no": int(m.group(1)[1:]),
        "title": text(re.search(r"<h1>(.*?)</h1>", head, re.S).group(1)),
        "en": text(re.search(r'<p class="en-title">(.*?)</p>', head, re.S).group(1)),
        "date": date,
        "part": part,
        "pdf": re.search(r'data-pdf="([^"]+)"', tag).group(1),
        "pages": int(re.search(r'data-pages-total="(\d+)"', tag).group(1)),
        "read": re.search(r'<span class="read-time">約 (\d+) 分鐘</span>', s).group(1),
        "path": path,
    }


def lectures():
    out = [meta(p) for p in sorted(SITE.glob("l[0-9][0-9].html"))]
    return [m for m in out if m]


def row(m, here_block=None):
    if here_block:
        return here_block
    return (f'<li class="sn-lec"><a class="sn-row" href="{m["key"]}.html"><span class="sn-no">L{m["no"]}</span>'
            f'<span class="sn-t">{H.escape(m["title"], quote=False)}</span><span class="sn-ck" data-read-key="{m["key"]}" '
            f'title="已讀" hidden>✓</span></a></li>')


def sec(href, n, label, short=None, extra=""):
    short = short or label
    return (f'<li><a class="sn-sec" href="#{href}" data-spy data-short="{short}"><span class="sn-n">{n}</span>'
            f'<span class="sn-t">{label}</span>{extra}</a>')


def subs(items):
    if not items:
        return ""
    return '<ol class="sn-subs">' + "".join(f'<li><a class="sn-sub" href="#{i}">{t}</a></li>' for i, t in items) + "</ol>"


def section_html(s, sid):
    i = s.find(f'id="{sid}"')
    j = s.find("</section>", i)
    return s[i:j]


def here_block(m):
    """Expanded sidenav block for a lecture page, built from its own sections."""
    s = read(m["path"])
    ideas = section_html(s, "s-ideas")
    idea_items, starts, ends = [], [], []
    for iid, h3 in re.findall(r'<div class="idea" id="(i\d+)">\s*<h3>(.*?)</h3>', ideas, re.S):
        idea_items.append((iid, re.sub(r"\s*<a class=\"ref\".*", "", h3, flags=re.S).strip()))
        for a, b in re.findall(r"p\.(\d+)(?:–(\d+))?", text(re.search(r'<a class="ref"[^>]*>(.*?)</a>', h3, re.S).group(1)) if 'class="ref"' in h3 else ""):
            starts.append(int(a)); ends.append(int(b or a))
    span = f'<span class="sn-p">p.{min(starts)}–{max(ends)}</span>' if starts else ""
    bg = section_html(s, "s-background")
    terms = [(tid, re.sub(r"<small>.*?</small>", "", dt, flags=re.S).strip())
             for tid, dt in re.findall(r'<div id="(t\d+)">\s*<dt>(.*?)</dt>', bg, re.S)]
    by = section_html(s, "s-beyond")
    beyond = [(xid, re.sub(r"\s*<a class=\"ref\".*", "", h3, flags=re.S).strip())
              for xid, h3 in re.findall(r'<div class="idea" id="(x\d+)">\s*<h3>(.*?)</h3>', by, re.S)]
    has_beyond = 'id="s-beyond"' in s  # 2026-10-26: L4 folded 延伸思考 into the chapters; later sections renumber
    k = 5 if has_beyond else 4
    parts = [
        sec("tldr-h", "", "先看這裡") + "</li>",
        sec("s-arch", "1", "架構") + "</li>",
        sec("s-ideas", "2", "核心觀念", extra=span) + subs(idea_items) + "</li>",
        sec("s-background", "3", "觀念補充") + subs(terms) + "</li>",
    ]
    if has_beyond:
        parts.append(sec("s-beyond", "4", "延伸思考") + subs(beyond) + "</li>")
    parts += [
        sec("s-discuss", str(k), "問題討論") + "</li>",
        sec("s-try", str(k + 1), "動手試試") + "</li>",
        sec("s-submit", str(k + 2), "大家的討論", short="討論") + "</li>",
        sec("wrap", "", "延伸閱讀") + "</li>",
    ]
    return (f'<li class="sn-lec is-here"><a class="sn-row" href="{m["key"]}.html" aria-current="page">'
            f'<span class="sn-no">L{m["no"]}</span><span class="sn-t">{H.escape(m["title"], quote=False)}</span>'
            f'<span class="sn-ck" data-read-key="{m["key"]}" title="已讀" hidden>✓</span></a>'
            f'<ol class="sn-secs">{"".join(parts)}</ol></li>')


def rebuild_sidenav(page_name, s, lecs, new_key):
    a = s.find('<aside class="sidenav"')
    b = s.find("</aside>", a)
    if a < 0:
        return s
    nav = s[a:b]
    lines = nav.split("\n")
    # keep this page's own expanded block, unless it is the new page (built fresh)
    own = {}
    for ln in lines:
        m = re.match(r'<li class="sn-lec is-here"><a class="sn-row(?: plain)?" href="([\w.]+)"', ln)
        if m:
            own[m.group(1)] = ln
    head_end = next(i for i, ln in enumerate(lines) if ln.startswith('<p class="sn-label">Part'))
    tail_start = next(i for i, ln in enumerate(lines) if ln.startswith('<p class="sn-label">讀書會'))
    soon = [ln for ln in lines[head_end:tail_start] if ln.startswith('<p class="sn-soon">')]
    if any(m["part"] == "Part II" for m in lecs):
        soon = [re.sub(r'(<a href="index.html#later-h">)[^<]*(</a>)', r"\1Part II 其他講次在 slides 公開後加入\2", ln) for ln in soon]
    body = []
    for part in sorted({m["part"] for m in lecs}, key=lambda p: len(p)):
        body.append(f'<p class="sn-label">{part} · 講次</p>')
        body.append('<ol class="sn-list">')
        for m in [x for x in lecs if x["part"] == part]:
            fn = f'{m["key"]}.html'
            if fn == page_name:
                body.append(here_block(m) if (m["key"] == new_key or fn not in own) else own[fn])
            else:
                body.append(row(m))
        body.append("</ol>")
    body += soon
    out = "\n".join(lines[:head_end] + body + lines[tail_start:])
    return s[:a] + out + s[b:]


def set_counts(s, m, n, lecs):
    s = re.sub(r'<span class="here">L\d+ / \d+</span>', f'<span class="here">L{m["no"]} / {n}</span>', s)
    return s


def link_next(prev, new, s):
    """Previous lecture page: lecnav gets a next link, pager's right side points to the new page."""
    nav = re.search(r'(<nav class="lecnav" aria-label="講次">)(.*?)(</nav>)', s, re.S)
    if nav and f'href="{new["key"]}.html"' not in nav.group(2):
        inner = re.sub(r'\n\s*<a href="[^"]+" rel="next">.*?</a>', "", nav.group(2))
        inner = inner.rstrip() + f'\n      <a href="{new["key"]}.html" rel="next">L{new["no"]} →</a>\n    '
        s = s[:nav.start(2)] + inner + s[nav.end(2):]
    pg = re.search(r'<nav class="pager" aria-label="[^"]*">(.*?)</nav>', s, re.S)
    if pg:
        nxt = (f'<a class="next" href="{new["key"]}.html"><span>下一堂 L{new["no"]} →</span>'
               f'{H.escape(new["title"], quote=False)}</a>')
        inner = re.sub(r'<a class="next".*?</a>', nxt, pg.group(1), flags=re.S)
        label = "上一堂與下一堂" if 'class="prev" href="l' in inner else "回總覽與下一堂"
        s = s[:pg.start()] + f'<nav class="pager" aria-label="{label}">{inner}</nav>' + s[pg.end():]
    return s



def update_index(s, new, summary):
    s = strip_wrapper(s)
    if f'href="{new["key"]}.html"><span class="no">' not in s:
        r = (f'      <li><a class="row" href="{new["key"]}.html"><span class="no">{new["no"]:02d}</span>'
             f'<span class="t">{H.escape(new["title"], quote=False)}<span class="en">{H.escape(new["en"], quote=False)} · {new["date"]}</span></span>'
             f'<span class="sum">{H.escape(summary, quote=False)}</span><span class="side"><span>{new["pages"]} 頁</span>'
             f'<span>約 {new["read"]} 分</span><span class="pill" data-read-key="{new["key"]}" hidden>已讀</span></span></a></li>\n')
        i = s.index('<ol class="leclist">')
        j = s.index("    </ol>", i)
        s = s[:j] + r + s[j:]
    s = re.sub(rf'\n\s*<li><span class="d">{new["date"]}</span>.*?</li>', "", s, count=1)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page", nargs="?")
    ap.add_argument("--sum")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--prepare", action="store_true")
    a = ap.parse_args()
    lecs = lectures()
    if a.prepare:
        idx = SITE / "index.html"
        s0 = read(idx)
        s1 = strip_wrapper(s0)
        if s1 != s0:
            idx.write_text(s1, encoding="utf-8")
        print("index.html: " + ("publish wrapper removed" if s1 != s0 else "no wrapper (ok)"))
        a.check = True
    if a.check:
        changed = []
        for p in sorted(SITE.glob("*.html")):
            s = read(p)
            if rebuild_sidenav(p.name, s, lecs, None) != s:
                changed.append(p.name)
        print("sidenav would change in: " + (", ".join(changed) if changed else "nothing (in sync)"))
        sys.exit(1 if changed else 0)
    if not a.page or not a.sum:
        ap.error("give the new page and --sum")
    new = meta(Path(a.page).resolve())
    if not new or Path(a.page).resolve().parent != SITE:
        ap.error("the page must be docs/lXX.html with main[data-lecture]")
    n = len(lecs)
    touched = []
    for p in sorted(SITE.glob("*.html")):
        s0 = read(p)
        s = rebuild_sidenav(p.name, s0, lecs, new["key"])
        m = meta(p) if p.name.startswith("l") else None
        if m:
            s = set_counts(s, m, n, lecs)
            if m["no"] == new["no"] - 1:
                s = link_next(m, new, s)
        if p.name == "index.html":
            s = update_index(s, new, a.sum)
        if s != s0:
            p.write_text(s, encoding="utf-8")
            touched.append(p.name)
    print("changed: " + (", ".join(touched) if touched else "nothing"))
    print("next: python3 -I tools/discuss.py " + a.page + " (opens the GitHub issues, writes the links); "
          "by hand: index.html course-map chips (課程地圖); then audit.py, commit and push.")


if __name__ == "__main__":
    main()
