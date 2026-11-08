#!/usr/bin/env python3
"""Pack a lecture page into reader-view text for the readability review (read-only).

The reviewer must see exactly what a reader sees, nothing more: no slides, no notes, no
sources. This script prints the page as plain text, one unit per line, each unit with a
locator the author can jump to. Table cells carry their column header and row name, so the
reviewer can ask "does this cell answer its header?".

Usage:
  python3 -I tools/review_pack.py docs/l06.html                  # tldr + every chapter of 核心觀念
  python3 -I tools/review_pack.py docs/l06.html --chapter i2 i5  # only these chapters ("tldr" selects 先看這裡)
  python3 -I tools/review_pack.py docs/l06.html --since HEAD~1   # only chapters whose text changed since that git ref
  python3 -I tools/review_pack.py docs/l06.html --since HEAD --sections s-try wrap   # other sections too
  python3 -I tools/review_pack.py docs/l06.html --units          # just count the units (for the time budget)
  python3 -I tools/review_pack.py docs/l06.html --chapter i3 i4 --prefix   # tldr, i1, i2 as context; i3, i4 reviewed; nothing after i4
  python3 -I tools/review_pack.py docs/l06.html --chapter tldr   # the tldr alone: its reader has read nothing else

--since also notices a changed tldr (2026-11-07). Always give the reviewer a --prefix pack (or the
tldr alone), never the whole page: with the whole page the reviewer understands a unit through a
chapter the reader has not reached yet, and passes it (L1 tldr, 2026-11-07).

Output format (one unit per line; the reviewer answers the checklist per unit):
  [#i2 ¶3] 一段正文……
  [#i2 表2 列2 ‹為什麼抓不到›] (列名：讓 agent 評自己的成果) 格子的文字
  [#i2 圖1 說明] figcaption 的文字
  [#i2 圖1 內容] svg 的 aria-label
  [#i2 註 n-sre 標題] 收合註的 summary
  [#i2 code1 內容] 程式碼或指令的文字（讀者看得到，正文會引用它；不審句子，只審 code1 說明）
Locators are stable within one HTML revision: ¶N counts <p> and <li> inside the chapter in
document order; 表N / 圖N count tables / figures inside the chapter.
"""
import argparse
import html
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"br", "img", "hr", "input", "meta", "link", "path", "circle", "rect", "line", "polyline",
        "polygon", "use", "stop", "ellipse"}
NUMERIC = re.compile(r"[\d\s.,%×$—–\-+~≈<>/^a-zA-Z]{0,12}")  # a cell that is a number, a dash or a short unit


class Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.children, self.parent = tag, attrs, [], parent

    def cls(self):
        return (self.attrs.get("class") or "").split()

    def text(self):
        out = []
        for c in self.children:
            if isinstance(c, str):
                out.append(c)
            elif c.tag in ("svg", "script", "style"):
                continue
            elif c.tag == "br":
                out.append(" / ")
            elif c.tag == "sup":
                out.append("^" + c.text())
            elif c.tag == "sub":
                out.append("_" + c.text())
            else:
                out.append(c.text())
        return re.sub(r"\s+", " ", "".join(out)).strip()

    def find_all(self, pred):
        for c in self.children:
            if isinstance(c, Node):
                if pred(c):
                    yield c
                yield from c.find_all(pred)


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", {}, None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs), self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, dict(attrs), self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse(s):
    s = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->", "", s, flags=re.S)
    t = Tree()
    t.feed(s)
    return t.root


def by_id(root, i):
    return next(root.find_all(lambda n: n.attrs.get("id") == i), None)


def units_of(container, loc):
    """Yield (locator, text) for every reader-visible unit inside container, in document order."""
    counts = {"p": 0, "table": 0, "figure": 0, "code": 0}
    out = []

    def walk(n, in_table=None):
        for c in n.children:
            if isinstance(c, str):
                continue
            cls = c.cls()
            if c.tag in ("h2", "h3"):
                no = next((x for x in c.children if isinstance(x, Node) and "idea-no" in x.cls()), None)
                tx = c.text()
                if no is not None and no.text():
                    tx = tx.replace(no.text(), no.text() + " ", 1)
                out.append((f"{loc} 標題", tx))
            elif c.tag == "figure":
                counts["figure"] += 1
                k = counts["figure"]
                cap = next(c.find_all(lambda x: x.tag == "figcaption"), None)
                if "file" in cls:
                    counts["code"] += 1
                    if cap:
                        out.append((f"{loc} code{counts['code']} 說明", cap.text()))
                    pre = next(c.find_all(lambda x: x.tag == "pre"), None)
                    body = pre.text() if pre is not None else ""
                    out.append((f"{loc} code{counts['code']} 內容",
                                "(程式碼／指令，讀者看得到、可以被正文引用；不審句子) " + body[:600]))
                    continue
                if cap:
                    out.append((f"{loc} 圖{k} 說明", cap.text()))
                svg = next(c.find_all(lambda x: x.tag == "svg"), None)
                if svg is not None and svg.attrs.get("aria-label"):
                    out.append((f"{loc} 圖{k} 內容", svg.attrs["aria-label"]))
                calc = next(c.find_all(lambda x: x.tag == "div" and "calc" in x.cls()), None)
                if calc is not None:
                    # interactive figure (calc.js): the sliders with their ranges, then the readout at the default
                    parts = []
                    for x in calc.find_all(lambda x: x.tag in ("label", "input", "output", "button")
                                           or (x.tag == "div" and "calc-h" in x.cls())):
                        if x.tag == "input":
                            parts.append(f"[滑桿 {x.attrs.get('min')}–{x.attrs.get('max')}]")
                        else:
                            parts.append(x.text())
                    out.append((f"{loc} 圖{k} 滑桿",
                                "(互動元件：拖滑桿時長條照同一條算式重畫，下面是預設值時的文字) " + " ".join(parts)))
            elif c.tag == "table":
                counts["table"] += 1
                k = counts["table"]
                heads = [h.text() for h in c.find_all(lambda x: x.tag == "th")]
                rows = [r for r in c.find_all(lambda x: x.tag == "tr") if any(
                    isinstance(d, Node) and d.tag == "td" for d in r.children)]
                for ri, r in enumerate(rows, 1):
                    cells = [d for d in r.children if isinstance(d, Node) and d.tag == "td"]
                    rowname = cells[0].text() if cells else ""
                    if len(cells) > 1 and all(NUMERIC.fullmatch(d.text()) for d in cells[1:]):
                        # a row of numbers: one unit, the reviewer checks the row reads as a whole
                        row = " ｜ ".join(f"{heads[ci] if ci < len(heads) else ''} {d.text()}".strip()
                                         for ci, d in enumerate(cells[1:], 1))
                        out.append((f"{loc} 表{k} 列{ri}", f"{rowname} ｜ {row}"))
                        continue
                    for ci, d in enumerate(cells):
                        head = heads[ci] if ci < len(heads) else f"欄{ci + 1}"
                        if ci == 0:
                            out.append((f"{loc} 表{k} 列{ri} ‹{head}›", d.text()))
                        else:
                            out.append((f"{loc} 表{k} 列{ri} ‹{head}›", f"(列名：{rowname}) {d.text()}"))
            elif c.tag == "details":
                did = c.attrs.get("id", "")
                summ = next((x for x in c.children if isinstance(x, Node) and x.tag == "summary"), None)
                kind = "註" if "gloss" in cls else "收合"
                if summ:
                    # 本文延伸／深入: the trailing class-less <span> is a tag on the page (「不是 slide 的內容」),
                    # not part of the title; print it apart so the reviewer does not read it as one sentence
                    tail = [x for x in summ.children if not (isinstance(x, str) and not x.strip())]
                    tag = tail[-1] if tail and isinstance(tail[-1], Node) and tail[-1].tag == "span" and not tail[-1].cls() else None
                    if tag is not None:
                        rest = Node("summary", {}, None)
                        rest.children = [x for x in summ.children if x is not tag]
                        out.append((f"{loc} {kind} {did} 標題", f"{rest.text().strip()}　〔頁面上的標籤：{tag.text().strip()}〕"))
                    else:
                        out.append((f"{loc} {kind} {did} 標題", summ.text()))
                sub = Node("div", {}, None)
                sub.children = [x for x in c.children if x is not summ]
                for lc, tx in units_of(sub, f"{loc} {kind} {did}"):
                    out.append((lc, tx))
            elif c.tag in ("p", "li", "dd", "dt"):
                if "kicker" in cls or "map-m" in cls:
                    continue
                counts["p"] += 1
                tx = c.text()
                if tx:
                    out.append((f"{loc} ¶{counts['p']}", tx))
                # nested lists inside li
                for sub in c.children:
                    if isinstance(sub, Node) and sub.tag in ("ul", "ol"):
                        walk(sub)
            elif c.tag in ("pre", "svg"):
                continue
            else:
                walk(c)

    walk(container)
    return out


def chapters(root):
    ideas = by_id(root, "s-ideas")
    if ideas is None:
        return []
    return [n for n in ideas.find_all(lambda x: x.tag == "div" and "idea" in x.cls())]


def tldr_of(root):
    return next(root.find_all(lambda x: x.tag == "section" and "tldr" in x.cls()), None)


def pack(root, chapter_ids=None, sections=(), prefix=False):
    """Groups in reading order: (title, locator, units, under_review).

    prefix=False: only the selected groups. prefix=True: everything from the top of the page
    up to the last selected group; groups before it that were not selected come back as
    context (under_review=False). Nothing after the last selected group is printed, so the
    reviewer cannot lean on text the reader has not reached yet (2026-11-07, L1 tldr).
    """
    items = []
    tldr = tldr_of(root)
    if tldr is not None:
        items.append(("tldr", "先看這裡", "#tldr", tldr))
    for ch in chapters(root):
        cid = ch.attrs.get("id", "?")
        h = next(ch.find_all(lambda x: x.tag == "h3"), None)
        items.append((cid, h.text() if h else cid, f"#{cid}", ch))
    for sid in sections:
        sec = by_id(root, sid)
        if sec is not None:
            items.append((sid, sid, f"#{sid}", sec))
    picked = [i for i, (key, *_) in enumerate(items)
              if key in sections or not chapter_ids or key in chapter_ids]
    if not picked:
        return []
    last = picked[-1] if prefix else None
    groups = []
    # The page title sits above the tldr and every reader sees it first; without it "這堂" in the
    # tldr has no referent (L1 tldr review, 2026-11-07). Always context, never reviewed.
    head = [n for n in root.find_all(lambda x: (x.tag == "p" and "eyebrow" in x.cls()) or x.tag == "h1")][:2]
    if head:
        groups.append(("頁首", "#top", [("#top 頁首", " ／ ".join(n.text() for n in head))], False))
    for i, (key, title, loc, node) in enumerate(items):
        if i in picked:
            groups.append((title, loc, units_of(node, loc), True))
        elif prefix and i < last:
            groups.append((title, loc, units_of(node, loc), False))
    return groups


def changed_chapters(path, ref):
    old = subprocess.run(["git", "show", f"{ref}:{path.as_posix()}"], capture_output=True,
                         text=True, cwd=path.parent.parent if path.parent.name == "docs" else None)
    if old.returncode != 0:
        sys.exit(f"git show {ref}:{path} failed: {old.stderr.strip()}")
    def text_by_group(root):
        d = {c.attrs.get("id"): [t for _, t in units_of(c, "")] for c in chapters(root)}
        t = tldr_of(root)
        if t is not None:  # before 2026-11-07 a tldr-only edit came back as "no chapter changed"
            d["tldr"] = [x for _, x in units_of(t, "")]
        return d
    o = text_by_group(parse(old.stdout))
    n = text_by_group(parse(path.read_text(encoding="utf-8")))
    return [cid for cid in n if o.get(cid) != n[cid]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--chapter", nargs="*", help="chapter ids, e.g. i2 i5")
    ap.add_argument("--since", help="git ref; only chapters whose text changed since it")
    ap.add_argument("--sections", nargs="*", default=[], help="extra section ids: s-try wrap")
    ap.add_argument("--units", action="store_true", help="only count units")
    ap.add_argument("--prefix", action="store_true",
                    help="also print, as unreviewed context, every group before the last selected one; "
                         "nothing after it (the reader has not reached it yet)")
    a = ap.parse_args()
    path = Path(a.page)
    root = parse(path.read_text(encoding="utf-8"))
    ids = set(a.chapter or [])
    if a.since:
        ch = changed_chapters(path, a.since)
        if not ch and not a.sections:
            print(f"# {path.name}: no chapter text changed since {a.since}")
            return
        ids |= set(ch)
    groups = pack(root, ids or None, a.sections, a.prefix)
    total = sum(len(u) for _, _, u, r in groups if r)
    ctx = sum(len(u) for _, _, u, r in groups if not r)
    if a.units:
        for title, loc, u, r in groups:
            print(f"{loc}\t{len(u)}\t{title}" + ("" if r else "\t(context)"))
        print(f"total\t{total}" + (f"\tcontext\t{ctx}" if ctx else ""))
        return
    n_rev = sum(1 for g in groups if g[3])
    print(f"# 審查包：{path.name}　審 {n_rev} 組　{total} 個單位" + (f"　（自 {a.since} 起有改的章）" if a.since else "")
          + (f"　另有上下文 {ctx} 個單位" if ctx else ""))
    print("# 每一行是一個單位：[定位] 文字。表格格子帶欄名 ‹…› 與列名。請照 guide/REVIEW_READABILITY.md 逐單位審。")
    if ctx:
        print("# 標「上下文」的組是讀者在審查範圍之前讀過的文字：讀，但不審。審查範圍之後的文字不在這份審查包裡，"
              "因為讀者讀到這裡時還沒看到它。")
    for title, loc, u, r in groups:
        print(f"\n## {loc}　{title}" + ("" if r else "　〔上下文：讀過，不審〕"))
        for lc, tx in u:
            print(f"[{lc}] {tx}")


if __name__ == "__main__":
    main()
