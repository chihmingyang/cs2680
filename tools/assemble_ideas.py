#!/usr/bin/env python3
"""Rebuild a lecture page's 核心觀念 from chapter fragments (used for the L5、L6 rewrite, 2026-10-29).

Usage:
  python3 -I tools/assemble_ideas.py docs/l05.html notes/l05

Fragments in the folder (notes/ is git-ignored scratch, so keep them only for the session):
  head.html   <section class="part" id="s-ideas"> … header.part-head, nav.map, opening <div class="ideas">
              nav.map's minutes may be written as __i1__, __i2__ …; they are filled with the
              check_article.py formula (400 units per minute, chapter text with every <details> closed)
  i1.html …   one <div class="idea" id="iN"> per file (plus its p.idea-group when it starts a group)
  tldr.html   optional: the whole <section class="tldr">
  arch.html   optional: the whole <div class="prose"> of #s-arch

What it does: replaces #s-ideas (everything up to the 問題討論 comment), the tldr and the arch prose,
then rebuilds this page's own three-level sidenav line from the new h3 / p[id="iN-k"] structure
(add_lecture.py keeps that line as is, so --check stays in sync). Links elsewhere on the page
(tk-rel, digests) are not touched: fix them by hand, then run check_article.py --fix-time.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_article as ca  # noqa: E402

page = Path(sys.argv[1]).resolve()
frag = Path(sys.argv[2]).resolve()
s = page.read_text(encoding="utf-8")

head = (frag / "head.html").read_text(encoding="utf-8")
chapters = sorted(frag.glob("i[0-9].html"), key=lambda p: int(p.stem[1:]))
body = "".join(p.read_text(encoding="utf-8") for p in chapters)

# chapter minutes for nav.map placeholders
for p in chapters:
    v = ca.Vis(); v.feed("<main>" + p.read_text(encoding="utf-8") + "</main>")
    head = head.replace(f"__{p.stem}__", str(-(-v.b["read-time"] // 400)))

new_ideas = head + body + "        </div>\n      </section>\n"
a = s.index('      <section class="part" id="s-ideas">')
b = s.index("      <!-- ===================== 3 問題討論")
s = s[:a] + new_ideas + "\n" + s[b:]

t = frag / "tldr.html"
if t.exists():
    a = s.index('  <section class="tldr"')
    b = s.index("</section>", a) + len("</section>\n")
    s = s[:a] + t.read_text(encoding="utf-8") + s[b:]

t = frag / "arch.html"
if t.exists():
    a = s.index('<section class="part" id="s-arch">')
    i = s.index('<div class="prose">', a)
    j = s.index("</div>", i) + len("</div>")
    s = s[:i] + t.read_text(encoding="utf-8").strip() + s[j:]

# this page's own sidenav line
ideas = s[s.index('id="s-ideas"'):s.index('id="s-discuss"')]
subs, starts, ends = [], [], []
pat = re.compile(r'<div class="idea" id="(i\d)">\s*<h3><span class="idea-no">([\d.]+)</span>(.*?)<a class="ref"[^>]*>(.*?)</a></h3>(.*?)(?=<div class="idea" id="i\d">|\Z)', re.S)
for iid, no, title, pages, rest in pat.findall(ideas):
    short = title.split("：")[0].strip()
    for x, y in re.findall(r"p\.(\d+)(?:–(\d+))?", pages):
        starts.append(int(x)); ends.append(int(y or x))
    sub2 = re.findall(r'<p id="(i\d-\d+)"><b>(.*?)</b>', rest, re.S)
    items = "".join(f'<li><a class="sn-sub2" href="#{sid}">{re.sub(r"<[^>]+>", "", st).rstrip("。")}</a></li>' for sid, st in sub2)
    subs.append(f'<li><a class="sn-sub" href="#{iid}"><span class="sn-n">{no}</span><span class="sn-t">{short}</span></a><ol class="sn-sub2s">{items}</ol></li>')
span = f'<span class="sn-p">p.{min(starts)}–{max(ends)}</span>'
line = re.search(r'<li class="sn-lec is-here">.*?</li>\n', s).group(0)
hdr = re.search(r'(<li class="sn-lec is-here">.*?<ol class="sn-secs">)', line, re.S).group(1)
tail = line[line.index('<li><a class="sn-sec" href="#s-discuss"'):]
pre = line[len(hdr):line.index('<li><a class="sn-sec" href="#s-ideas"')]
ideas_li = (f'<li><a class="sn-sec" href="#s-ideas" data-spy data-short="核心觀念"><span class="sn-n">2</span><span class="sn-t">核心觀念</span>{span}</a>'
            f'<ol class="sn-subs">{"".join(subs)}</ol></li>')
s = s.replace(line, hdr + pre + ideas_li + tail)
page.write_text(s, encoding="utf-8")
print(f"{page.name}: {len(chapters)} chapters, {sum(x.count('sn-sub2\"') for x in subs)} sidenav sub-items; "
      "next: fix tk-rel / digest links by hand, then check_article.py --fix-time")
