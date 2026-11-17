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
  wrap.html       optional: the whole <section class="wrap" id="wrap"> … </section>
                  A new lecture starts from tools/new_lecture.py's skeleton and fills all of these.

What it does:
  - replaces the tldr and #s-ideas, removes #s-arch
  - section kickers carry no number (2026-11-16: the sidenav numbers 0 導讀 and the chapters only);
    the HTML comments keep theirs (this script finds the 原文出處 comment by it)
  - eyebrow gets「· 依想法重組」, the meta row「頁碼」goes away, the styles.css link copies l05.html's version
  - rebuilds this page's own sidenav line from the h3s and the <p id="…"><b>小標</b> paragraphs

What it leaves to you: tk-rel lines, digests and any「第 N 段」text in the kept sections. Next step:
check_article.py --fix-time. `h1` and `p.en-title` stay as they are.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_article as ca  # noqa: E402

SECTIONS = {"原文出處": 2}  # 2026-11-09: 問題討論 removed; 2026-11-17: 動手試試 removed


def clean(html):
    return re.sub(r"<[^>]+>", "", html).strip()


def sidenav_line(s):
    """The page's own li.sn-lec.is-here, rebuilt from the chapters. Shared with the check in test mode."""
    line = re.search(r'<li class="sn-lec is-here">.*?</li>\n', s).group(0)
    hdr = re.search(r'(<li class="sn-lec is-here">.*?<ol class="sn-secs">)', line, re.S).group(1)
    return hdr + v7_secs(s) + "</ol></li>\n", line


def v7_secs(s):
    """The sections of a v7 page for the sidenav (2026-11-16 James): 0 導讀, the chapters on the
    same level (each with its 小標), then one quiet line under a rule: 查閱 · 原文出處 (動手試試 removed
    2026-11-17, James: good exercises moved to 整合題).
    查閱 is the chapter whose h3 has no idea-no (the old numbered 目錄 chapter). The 核心觀念 link
    stays, hidden by CSS, so app.js keeps the chapters as the subs of one tracked section.
    add_lecture.py uses it too, so a new v7 page gets this block on its first wiring (2026-11-06)."""
    ideas = s[s.index('id="s-ideas"'):s.index('id="wrap"')]
    parts = re.split(r'(?=<div class="idea" id="i\d+">)', ideas)[1:]
    subs, refs = [], []
    for part in parts:
        iid = re.match(r'<div class="idea" id="(i\d+)">', part).group(1)
        m = re.search(r'<h3>(?:<span class="idea-no">(.*?)</span>)?(.*?)</h3>', part, re.S)
        no, title = m.group(1), clean(m.group(2))
        if no is not None and not re.fullmatch(r"[\d.]+", no.strip()):
            # 2026-11-16: an online edit put the L8 第 2 章 title inside the number; read as 查閱, the
            # chapter moved under the rule. Stop instead of guessing.
            raise SystemExit(f"{iid}: span.idea-no 只能放章號，現在是「{clean(no)}」；章名要放在 </span> 後面")
        short = title.split("：")[0].strip()
        if not no:
            refs.append((iid, short))
            continue
        # 小標 inside <details> are reference notes, not part of the chapter's outline
        top = re.sub(r"<details\b.*?</details>", "", part, flags=re.S)
        sub2 = re.findall(r'<p id="([^"]+)"[^>]*>(?:<span class="anchor" id="[^"]+"></span>)*<b>(.*?)</b>', top, re.S)
        items = "".join(f'<li><a class="sn-sub2" href="#{sid}">{clean(st).rstrip("。：: ")}</a></li>' for sid, st in sub2)
        nested = f'<ol class="sn-sub2s">{items}</ol>' if items else ""
        subs.append(f'<li><a class="sn-sub" href="#{iid}"><span class="sn-n">{no}</span><span class="sn-t">{short}</span></a>{nested}</li>')

    def link(href, label, n=None):
        num = f'<span class="sn-n">{n}</span>' if n is not None else ""
        return f'<a class="sn-sec" href="#{href}" data-spy data-short="{label}">{num}<span class="sn-t">{label}</span></a>'

    refs += [("wrap", "原文出處")]
    return ("<li>" + link("tldr-h", "導讀", 0) + "</li>"
            + '<li class="sn-ideas">' + link("s-ideas", "核心觀念") + f'<ol class="sn-subs">{"".join(subs)}</ol></li>'
            + '<li class="sn-refs"><ol class="sn-refrow">'
            + "".join(f"<li>{link(h, t)}</li>" for h, t in refs) + "</ol></li>")


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

    # #s-arch out, #s-ideas replaced; everything up to the next section's comment goes
    start = s.index('<div class="content">') + len('<div class="content">')
    # the section after 核心觀念: 問題討論 (before 2026-11-09), 動手試試 (before 2026-11-17), now 原文出處
    m = next((m for name in ("問題討論", "動手試試", "原文出處")
              if (m := re.search(rf'[ \t]*<!-- =+ \d {name} =+ -->', s))), None)
    if not m:
        sys.exit("no 原文出處 comment after #s-ideas")
    s = s[:start] + "\n" + new_ideas.lstrip("\n") + s[m.start():]

    # section numbers: comments keep them, kickers drop them (2026-11-16)
    for name, n in SECTIONS.items():
        s = re.sub(rf'(<!-- =+ )\d( {name} =+ -->)', rf'\g<1>{n}\g<2>', s)
    s = re.sub(r'(<p class="kicker">)\d · (核心觀念|原文出處)(</p>)', r'\1\2\3', s)

    # eyebrow, meta, css version
    s = re.sub(r'(<p class="eyebrow">Lecture \d+[a-z]? · [\d-]+ · Part [IVX]+)(?: · 依想法重組)?(</p>)', r'\1 · 依想法重組\2', s)
    s = s.replace('      <li><span class="k">頁碼</span>PDF 檢視器的頁數</li>\n', "")
    l5 = (page.parent / "l05.html").read_text(encoding="utf-8")
    css = re.search(r'href="(styles\.css[^"]*)"', l5).group(1)
    s = re.sub(r'href="styles\.css[^"]*"', f'href="{css}"', s, count=1)

    # fineprint
    t = frag / "fineprint.html"
    if t.exists():
        s = re.sub(r'<p class="fineprint">.*?</p>', lambda _: t.read_text(encoding="utf-8").strip(), s, count=1, flags=re.S)

    # new pages (tools/new_lecture.py): 原文出處 can come from a fragment too
    for name, sid in (("wrap.html", "wrap"),):
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
