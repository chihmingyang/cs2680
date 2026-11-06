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
  python3 -I tools/review_pack.py docs/l06.html --since HEAD --sections s-discuss s-try   # other sections too
  python3 -I tools/review_pack.py docs/l06.html --units          # just count the units (for the time budget)

Output format (one unit per line; the reviewer answers the checklist per unit):
  [#i2 ¶3] 一段正文……
  [#i2 表2 列2 ‹為什麼抓不到›] (列名：讓 agent 評自己的成果) 格子的文字
  [#i2 圖1 說明] figcaption 的文字
  [#i2 圖1 內容] svg 的 aria-label
  [#i2 註 n-sre 標題] 收合註的 summary
  [#i2 code 1] (程式碼或指令，不審句子，只審 figcaption)
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
                    out.append((f"{loc} code{counts['code']}", "(程式碼／指令，只審上面的說明)"))
                    continue
                if cap:
                    out.append((f"{loc} 圖{k} 說明", cap.text()))
                svg = next(c.find_all(lambda x: x.tag == "svg"), None)
                if svg is not None and svg.attrs.get("aria-label"):
                    out.append((f"{loc} 圖{k} 內容", svg.attrs["aria-label"]))
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


def pack(root, chapter_ids=None, sections=()):
    groups = []
    tldr = next(root.find_all(lambda x: x.tag == "section" and "tldr" in x.cls()), None)
    if tldr is not None and (not chapter_ids or "tldr" in chapter_ids):
        groups.append(("先看這裡", "#tldr", units_of(tldr, "#tldr")))
    for ch in chapters(root):
        cid = ch.attrs.get("id", "?")
        if chapter_ids and cid not in chapter_ids:
            continue
        h = next(ch.find_all(lambda x: x.tag == "h3"), None)
        groups.append((h.text() if h else cid, f"#{cid}", units_of(ch, f"#{cid}")))
    for sid in sections:
        sec = by_id(root, sid)
        if sec is not None:
            groups.append((sid, f"#{sid}", units_of(sec, f"#{sid}")))
    return groups


def changed_chapters(path, ref):
    old = subprocess.run(["git", "show", f"{ref}:{path.as_posix()}"], capture_output=True,
                         text=True, cwd=path.parent.parent if path.parent.name == "docs" else None)
    if old.returncode != 0:
        sys.exit(f"git show {ref}:{path} failed: {old.stderr.strip()}")
    o = {c.attrs.get("id"): [t for _, t in units_of(c, "")] for c in chapters(parse(old.stdout))}
    n = {c.attrs.get("id"): [t for _, t in units_of(c, "")] for c in chapters(parse(path.read_text(encoding="utf-8")))}
    return [cid for cid in n if o.get(cid) != n[cid]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--chapter", nargs="*", help="chapter ids, e.g. i2 i5")
    ap.add_argument("--since", help="git ref; only chapters whose text changed since it")
    ap.add_argument("--sections", nargs="*", default=[], help="extra section ids: s-discuss s-try wrap")
    ap.add_argument("--units", action="store_true", help="only count units")
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
    groups = pack(root, ids or None, a.sections)
    total = sum(len(u) for _, _, u in groups)
    if a.units:
        for title, loc, u in groups:
            print(f"{loc}\t{len(u)}\t{title}")
        print(f"total\t{total}")
        return
    print(f"# 審查包：{path.name}　{len(groups)} 組　{total} 個單位" + (f"　（自 {a.since} 起有改的章）" if a.since else ""))
    print("# 每一行是一個單位：[定位] 文字。表格格子帶欄名 ‹…› 與列名。請照 guide/REVIEW_READABILITY.md 逐單位審。")
    for title, loc, u in groups:
        print(f"\n## {loc}　{title}")
        for lc, tx in u:
            print(f"[{lc}] {tx}")


if __name__ == "__main__":
    main()
