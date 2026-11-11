#!/usr/bin/env python3
"""The scan path of a page: what a reader sees who only reads h3, <b> lead-ins and red marks (<strong>).

Red marks are placed AFTER the readability review (STYLE_ARTICLE 6c, skill mark-red): the review
rewrites sentences, so marks placed earlier end up on text that no longer exists. This script is the
gate and the working view for that step:

  1. gate    a group (tldr or chapter) whose review status is not ok is refused: review it first
             (tools/review_status.py). --force prints it anyway, for looking only.
  2. path    per group: the h3, then every <b> lead-in with the red marks that follow it.
             Read it top to bottom without the article: can you rebuild the chapter's argument?
  3. flags   - a <b> lead-in with no red mark before the next one (the question has no answer)
             - a red mark that leans on context (右邊、上圖、第 N 章、它、這兩個 …)
             - a red mark that is only a number (mark what the number means)
             - a red mark that repeats its <b> lead-in
             Flags are hints for the person marking, not failures: a short section may need no mark.

Counts and positions stay with check_article.py. Moving <strong> does not change the reader-visible
text, so the review record (text hash) stays valid.

Usage:
  python3 -I tools/red_path.py l06b              # every group of the page
  python3 -I tools/red_path.py l06b i2 i3        # these groups
  python3 -I tools/red_path.py l06b --force      # skip the gate (read-only look)
Exit code 1 when a requested group is not reviewed (without --force).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_pack import Node, chapters, parse, tldr_of  # noqa: E402
from review_status import checklist_version, groups_of, read_log  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"details", "figure", "table", "pre", "svg", "script", "style", "nav", "aside", "figcaption"}
CONTEXT = re.compile(r"右邊|左邊|上圖|下圖|上表|下表|第 ?\d+ ?章|這兩|這三|這個|這種|這類|^它|^這")
NUM_ONLY = re.compile(r"^[\s\d.,%％倍分個元美題步行條$~–\-+×x約只剩到從是有了多少幾乎]+$")


def walk(n, out, in_li=False):
    """(kind, text) in reading order: h3, b (lead-in), red; red inside details is kind 'deep'."""
    for c in n.children:
        if not isinstance(c, Node):
            continue
        if c.tag == "details":
            for s in c.find_all(lambda x: x.tag == "strong"):
                out.append(("deep", s.text()))
            continue
        if c.tag in SKIP:
            continue
        if c.tag in ("h2", "h3"):
            out.append(("h3", c.text()))
        elif c.tag == "b":
            if len(c.text()) >= 4:   # a lead-in that opens a paragraph is a section; one inside a list is a sub-item
                up, sub = c.parent, False
                while up is not None and up is not n:
                    sub = sub or up.tag == "li"
                    up = up.parent
                out.append(("sub" if sub or n.tag == "li" or in_li else "b", c.text()))
        elif c.tag == "strong":
            out.append(("red", c.text()))
        else:
            walk(c, out, in_li or c.tag == "li")


def status_of(page, html):
    cur, log, ver = groups_of(html), read_log(), checklist_version()
    st = {}
    for g, h in cur.items():
        r = log.get((page, g))
        st[g] = "沒審過" if r is None else "改過" if r[4] != h else "舊規則" if int(r[2]) != ver else "ok"
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("groups", nargs="*")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    html = (ROOT / "docs" / f"{a.page}.html").read_text(encoding="utf-8")
    root = parse(html)
    nodes = {}
    t = tldr_of(root)
    if t is not None:
        nodes["tldr"] = t
    for c in chapters(root):
        nodes[c.attrs.get("id", "?")] = c
    st = status_of(a.page, html)
    want = a.groups or list(nodes)
    blocked = [g for g in want if st.get(g) != "ok"]
    if blocked and not a.force:
        print(f"先做可讀性審查，再標紅字：{a.page} 的 " + "、".join(f"{g}（{st.get(g, '找不到')}）" for g in blocked))
        print(f"  python3 -I tools/review_pack.py docs/{a.page}.html --chapter {' '.join(blocked)} --prefix")
        print("  只想看現況：加 --force")
        want = [g for g in want if g not in blocked]
    for g in want:
        if g not in nodes:
            continue
        items = []
        walk(nodes[g], items)
        reds = [x for k, x in items if k == "red"]
        print(f"\n== {a.page} #{g}　審查 {st.get(g)}　紅字 {len(reds)}")
        flags, cur_b, cur_reds = [], None, 0

        def close():
            if cur_b is not None and cur_reds == 0:
                flags.append(f"小標後面沒有紅字：{cur_b[:30]}")
        for k, x in items:
            if k == "h3":
                print(f"  ## {x}")
            elif k == "b":
                close()
                cur_b, cur_reds = x, 0
                print(f"  ■ {x}")
            elif k == "sub":
                print(f"    · {x}")
            elif k == "red":
                cur_reds += 1
                print(f"      → {x}")
                if CONTEXT.search(x):
                    flags.append(f"靠上下文才懂（{CONTEXT.search(x).group()}）：{x[:30]}")
                if NUM_ONLY.match(x):
                    flags.append(f"只有數字，沒有意思：{x}")
                if cur_b and len(x) >= 6 and x.rstrip("。") in cur_b:
                    flags.append(f"重複小標：{x[:30]}")
            else:
                print(f"      （收合區塊）→ {x}")
        close()
        for f in flags:
            print(f"  ? {f}")
    return 1 if blocked and not a.force else 0


if __name__ == "__main__":
    sys.exit(main())
