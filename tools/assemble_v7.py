#!/usr/bin/env python3
"""Turn a lecture page into the v7 layout from chapter fragments (STYLE_ARTICLE 第 0 節, 2026-11-03).

Usage:
  python3 -I tools/assemble_v7.py docs/lXX.html notes/lXX [--base notes/lXX/old.html]

--base starts from a saved copy of the old page, so a build script can rerun from scratch.
Without it the page itself is the base (running twice gives the same page).

Fragments in the folder (notes/ is git-ignored):
  head.html       <section class="part" id="s-ideas"> … header.part-head, nav.map, opening <div class="ideas">
                  nav.map minutes may be written as __i1__, __i2__ …: filled with the check_article.py
                  formula (400 units per minute, every <details> closed)
  i1.html …       one <div class="idea" id="iN"> per file; h3 = <span class="idea-no">N</span>主題：主張, no a.ref
  tldr.html       the whole <section class="tldr"> … </section>
  fineprint.html  optional: the whole <p class="fineprint"> … </p>
  try.html        optional: the whole <section class="part" id="s-try"> … </section>
  wrap.html       optional: the whole <section class="wrap" id="wrap"> … </section>
                  A new lecture starts from tools/new_lecture.py's skeleton and fills all of these.

What it does:
  - replaces the tldr and #s-ideas, removes #s-arch
  - renumbers the sections: 1 核心觀念, 2 動手試試, 3 延伸閱讀 (問題討論 removed 2026-11-09) (HTML comments and kickers)
  - eyebrow gets「· 依想法重組」, the meta row「頁碼」goes away, the styles.css link copies l05.html's version
  - rebuilds this page's own three-level sidenav line from the h3s and the <p id="…"><b>小標</b> paragraphs

What it leaves to you: tk-rel lines, digests and any「第 N 段」text in the kept sections. Next step:
check_article.py --fix-time. `h1` and `p.en-title` stay as they are.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_article as ca  # noqa: E402

SECTIONS = {"問題討論": 2, "動手試試": 3, "延伸閱讀": 4}


def clean(html):
    return re.sub(r"<[^>]+>", "", html).strip()


def sidenav_line(s):
    """The page's own li.sn-lec.is-here, rebuilt from the chapters. Shared with the check in test mode."""
    line = re.search(r'<li class="sn-lec is-here">.*?</li>\n', s).group(0)
    hdr = re.search(r'(<li class="sn-lec is-here">.*?<ol class="sn-secs">)', line, re.S).group(1)
    return hdr + v7_secs(s) + "</ol></li>\n", line


def v7_secs(s):
    """The sections of a v7 page for the sidenav: 先看這裡, 1 核心觀念 (chapters and their 小標), 2–3.
    add_lecture.py uses it too, so a new v7 page gets this block on its first wiring (2026-11-06)."""
    ideas = s[s.index('id="s-ideas"'):s.index('id="s-try"')]
    parts = re.split(r'(?=<div class="idea" id="i\d+">)', ideas)[1:]
    subs = []
    for part in parts:
        iid = re.match(r'<div class="idea" id="(i\d+)">', part).group(1)
        m = re.search(r'<h3><span class="idea-no">([\d.]+)</span>(.*?)</h3>', part, re.S)
        no, title = m.group(1), clean(m.group(2))
        short = title.split("：")[0].strip()
        # 小標 inside <details> are reference notes, not part of the chapter's outline
        top = re.sub(r"<details\b.*?</details>", "", part, flags=re.S)
        sub2 = re.findall(r'<p id="([^"]+)"[^>]*>(?:<span class="anchor" id="[^"]+"></span>)*<b>(.*?)</b>', top, re.S)
        items = "".join(f'<li><a class="sn-sub2" href="#{sid}">{clean(st).rstrip("。")}</a></li>' for sid, st in sub2)
        nested = f'<ol class="sn-sub2s">{items}</ol>' if items else ""
        subs.append(f'<li><a class="sn-sub" href="#{iid}"><span class="sn-n">{no}</span><span class="sn-t">{short}</span></a>{nested}</li>')

    def sec(href, n, label):
        return f'<li><a class="sn-sec" href="#{href}" data-spy data-short="{label}"><span class="sn-n">{n}</span><span class="sn-t">{label}</span></a>'

    return (sec("tldr-h", "", "先看這裡") + "</li>"
            + sec("s-ideas", 1, "核心觀念") + f'<ol class="sn-subs">{"".join(subs)}</ol></li>'
            + sec("s-try", 2, "動手試試") + "</li>"
            + sec("wrap", 3, "延伸閱讀") + "</li>")


def replace_section(s, sid, frag_text):
    """Swap one whole <section …id="sid">…</section> for a fragment holding the same section (new pages)."""
    a = s.index(f'id="{sid}"')
    a = s.rfind("<section", 0, a)
    b = s.index("</section>", a) + len("</section>")
    frag_text = frag_text.strip()
    if f'id="{sid}"' not in frag_text[:300] or not frag_text.startswith("<section"):
        sys.exit(f"fragment for #{sid} must be the whole <section … id=\"{sid}\"> … </section>")
    return s[:a] + frag_text + s[b:]


def main():
    args = sys.argv[1:]
    base = None
    if "--base" in args:
        k = args.index("--base")
        base = Path(args[k + 1])
        del args[k:k + 2]
    page, frag = Path(args[0]).resolve(), Path(args[1]).resolve()
    s = (base or page).read_text(encoding="utf-8")

    head = (frag / "head.html").read_text(encoding="utf-8")
    chapters = sorted(frag.glob("i[0-9]*.html"), key=lambda p: int(p.stem[1:]))
    chapters = [p for p in chapters if re.fullmatch(r"i\d+", p.stem)]
    if not chapters:
        sys.exit(f"no i1.html … in {frag}")
    for p in chapters:
        text = p.read_text(encoding="utf-8")
        v = ca.Vis()
        v.feed("<main>" + text + "</main>")
        head = head.replace(f"__{p.stem}__", str(-(-v.b["read-time"] // 400)))
        if 'class="ref"' in text:
            sys.exit(f"{p.name}: v7 chapters have no a.ref")
    left = re.findall(r"__i\d+__", head)
    if left:
        sys.exit(f"head.html: no fragment for {left}")
    body = "".join(p.read_text(encoding="utf-8") for p in chapters)
    new_ideas = head.rstrip() + "\n" + body.rstrip() + "\n        </div>\n      </section>\n\n"

    # tldr
    a = s.index('<section class="tldr"')
    b = s.index("</section>", a) + len("</section>")
    s = s[:a] + (frag / "tldr.html").read_text(encoding="utf-8").strip() + s[b:]

    # #s-arch out, #s-ideas replaced; everything up to the 問題討論 comment goes
    start = s.index('<div class="content">') + len('<div class="content">')
    m = re.search(r'[ \t]*<!-- =+ \d 問題討論 =+ -->', s)
    if not m:
        sys.exit("no 問題討論 comment")
    s = s[:start] + "\n" + new_ideas.lstrip("\n") + s[m.start():]

    # section numbers
    for name, n in SECTIONS.items():
        s = re.sub(rf'(<!-- =+ )\d( {name} =+ -->)', rf'\g<1>{n}\g<2>', s)
        s = re.sub(rf'(<p class="kicker">)\d( · {name}</p>)', rf'\g<1>{n}\g<2>', s)

    # eyebrow, meta, css version
    s = re.sub(r'(<p class="eyebrow">Lecture \d+ · [\d-]+ · Part [IVX]+)(?: · 依想法重組)?(</p>)', r'\1 · 依想法重組\2', s)
    s = s.replace('      <li><span class="k">頁碼</span>PDF 檢視器的頁數</li>\n', "")
    l5 = (page.parent / "l05.html").read_text(encoding="utf-8")
    css = re.search(r'href="(styles\.css[^"]*)"', l5).group(1)
    s = re.sub(r'href="styles\.css[^"]*"', f'href="{css}"', s, count=1)

    # fineprint
    t = frag / "fineprint.html"
    if t.exists():
        s = re.sub(r'<p class="fineprint">.*?</p>', lambda _: t.read_text(encoding="utf-8").strip(), s, count=1, flags=re.S)

    # new pages (tools/new_lecture.py): the other two sections can come from fragments too
    for name, sid in (("try.html", "s-try"), ("wrap.html", "wrap")):
        t = frag / name
        if t.exists():
            s = replace_section(s, sid, t.read_text(encoding="utf-8"))

    new, old = sidenav_line(s)
    s = s.replace(old, new)
    page.write_text(s, encoding="utf-8")
    n2 = new.count('class="sn-sub2"')
    print(f"{page.name}: {len(chapters)} chapters, {n2} sidenav sub-items. "
          "Next: fix tk-rel, digests and「第 N 段」, then check_article.py --fix-time")


if __name__ == "__main__":
    main()
