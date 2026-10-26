#!/usr/bin/env python3
"""Structural check of a lecture page's sections, focused on §4 (discussion; §5 before 2026-10-26).

Usage: python3 -I check_discuss.py docs/l01.html [...]
Prints a short report and PROBLEMS / OK per page. Rules as of 2026-10-22:
  基礎題 li.bq: 3-5, each with one details「參考答案與重點複習」> div.hint.takeaway holding
    div.tk-ans, p.tk-h「重點拆解」and「背景補充」, div.tk-keys (3 points), p.tk-rel.
    A「常見誤解」callout is expected (warning only).
  核心觀念 ideas: 3-8 (2026-10-27; was 3-6).
  觀念補充 terms: 4-6 is a suggestion (warning only, 2026-10-22); the section is optional
    since 2026-10-27 (L4 merged it into the chapters as details.note).
  進階題 li.dq: at most 3 (2026-10-22; was 6), each a different type (the qtag label before「·」),
    each with qctx「情境：」, qcover of 3 li each carrying span.qh (提示),
    details「作答範本」(details.qstart, >= 2 p.tpl) and「參考觀點與追問」(4-6 li + 追問).
  Every li.bq has p.gh-talk linking to the lecture's GitHub issue; li.dq has none (進階題 stay
    on the page); #s-submit links to that issue (all written by tools/discuss.py).
  div.submit#s-submit at the end of #s-discuss (2026-10-27) and the reading list ol.rg in #wrap (§6) exist.
  #s-beyond is optional (gone since 2026-10-26).
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

TYPES = ["概念", "估算", "分析", "設計", "團隊實務", "風險", "取捨", "應用"]
ISSUE = "https://github.com/chihmingyang/cs2680/issues/"
FORBID = [r"password", r"密碼", r"passwd", r"帳號.{0,6}密", r"login.{0,10}pass"]


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text = [], []

    def cls(self):
        return (self.attrs.get("class") or "").split()

    def all(self):
        yield self
        for c in self.children:
            yield from c.all()

    def find(self, tag=None, cls=None, id=None):
        return [n for n in self.all() if (tag is None or n.tag == tag)
                and (cls is None or cls in n.cls()) and (id is None or n.attrs.get("id") == id)]

    def txt(self):
        out = []
        def walk(n):
            out.extend(n.text_parts)
        for n in self.all():
            pass
        return "".join(self._t())

    def _t(self):
        for item in self.seq:
            if isinstance(item, Node):
                yield from item._t()
            else:
                yield item


VOID = {"br", "img", "meta", "link", "input", "hr", "source", "wbr", "path", "line", "rect",
        "circle", "polygon", "polyline", "ellipse", "use", "stop"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", [], None)
        self.root.seq = []
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        n.seq = []
        self.cur.children.append(n)
        self.cur.seq.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        n.seq = []
        self.cur.children.append(n)
        self.cur.seq.append(n)

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.seq.append(data)


def check(path):
    text = Path(path).read_text(encoding="utf-8")
    p = P()
    p.feed(text)
    root = p.root
    probs = []
    warns = []
    rep = []
    main = root.find("main")
    lec = main[0].attrs.get("data-lecture") if main else "?"
    pdf = main[0].attrs.get("data-pdf") if main else "?"

    def sec(i):
        s = root.find("section", id=i)
        return s[0] if s else None

    arch = sec("s-arch")
    if arch:
        figs = arch.find("figure", "diagram")
        rep.append(f"diagrams={len(figs)}")
        if not 1 <= len(figs) <= 2:
            probs.append(f"s-arch has {len(figs)} diagrams")
    ideas = sec("s-ideas")
    if ideas:
        items = ideas.find("div", "idea")
        refs = [it for it in items if it.find("a", "ref")]
        rep.append(f"ideas={len(items)}")
        if not 3 <= len(items) <= 8:  # 2026-10-25: 放寬到 6 章（v4.0）；2026-10-27: 8 章（v5.0，L4 拆成 7 章）
            probs.append(f"s-ideas has {len(items)} ideas")
        if len(refs) != len(items):
            probs.append("an idea lacks a.ref")
    bg = sec("s-background")
    if bg:
        dts = bg.find("dt")
        rep.append(f"terms={len(dts)}")
        if not 4 <= len(dts) <= 6:
            warns.append(f"terms={len(dts)} (suggested 4-6)")
    by = sec("s-beyond")
    if by:
        items = by.find("div", "idea")
        rep.append(f"beyond={len(items)}")
        if not by.find("p", "note-own"):
            probs.append("s-beyond lacks note-own")
        if not 3 <= len(items) <= 4:
            probs.append(f"s-beyond has {len(items)} ideas")
    d = sec("s-discuss")
    if d:
        n = int(lec[1:]) if lec and lec[1:].isdigit() else 0
        tabs = d.find("button", "qtab")
        if len(tabs) != 2:
            probs.append(f"{len(tabs)} qtabs")
        for name, prefix in (("basic", f"CS2680 L{n} 基礎題（帶著問題看 slides）："), ("adv", f"CS2680 L{n} 進階題（讀書會討論）：")):
            panel = d.find("div", id=f"qset-{name}")
            if not panel:
                probs.append(f"no #qset-{name}"); continue
            if not panel[0].find("p", "qset-lede"):
                probs.append(f"#qset-{name} lacks qset-lede")
            btn = [x for x in panel[0].find("button", "copybtn") if x.attrs.get("data-copy") == name]
            if not btn:
                probs.append(f"no copy button for {name}")
            else:
                t = btn[0].attrs.get("data-title", "")
                sl = btn[0].attrs.get("data-slides", "")
                if not t.startswith(prefix):
                    probs.append(f"{name} data-title {t!r}")
                if sl != f"https://cs2680.com/slides/{pdf}":
                    probs.append(f"{name} data-slides {sl!r}")
        if not d.find("textarea", id="copy-fallback"):
            probs.append("no copy-fallback textarea")
        bqs = d.find("li", "bq")
        rep.append(f"bq={len(bqs)}")
        if not 3 <= len(bqs) <= 5:
            probs.append(f"{len(bqs)} basic questions (want 3-5)")
        for k, q in enumerate(bqs, 1):
            if q.attrs.get("id") != f"b{k}":
                probs.append(f"b{k}: id {q.attrs.get('id')}")
            tag = q.find("p", "qtag")
            if not tag or not tag[0].find("a", "ref"):
                probs.append(f"b{k}: qtag without a.ref")
            if not q.find("p", "qtext"):
                probs.append(f"b{k}: no qtext")
            dets = q.find("details")
            sums = [x.find("summary")[0].txt().strip() if x.find("summary") else "" for x in dets]
            if sums != ["參考答案與重點複習"]:
                probs.append(f"b{k}: details {sums}")
            else:
                tk = dets[0].find("div", "takeaway")
                if not tk:
                    probs.append(f"b{k}: no div.hint.takeaway")
                else:
                    tk = tk[0]
                    heads = [x.txt().strip() for x in tk.find("p", "tk-h")]
                    if not tk.find("div", "tk-ans"):
                        probs.append(f"b{k}: no div.tk-ans")
                    for h in ("重點拆解", "背景補充"):
                        if h not in heads:
                            probs.append(f"b{k}: no tk-h {h}")
                    keys = tk.find("div", "tk-keys")
                    if not keys or len(keys[0].find("li")) != 3:
                        probs.append(f"b{k}: tk-keys needs 3 points")
                    if not tk.find("p", "tk-rel"):
                        probs.append(f"b{k}: no p.tk-rel")
                    if "常見誤解" not in tk.txt():
                        warns.append(f"b{k}: no 常見誤解 callout")
            gh = q.find("p", "gh-talk")
            if not gh or not any((x.attrs.get("href") or "").startswith(ISSUE) for x in gh[0].find("a")):
                probs.append(f"b{k}: no GitHub issue link (run tools/discuss.py)")
            if q.find("p", "qctx") or q.find("div", "qcover"):
                probs.append(f"b{k}: basic question must not have qctx/qcover")
        qs = d.find("li", "dq")
        rep.append(f"dq={len(qs)}")
        if not 1 <= len(qs) <= 3:
            probs.append(f"{len(qs)} discussion questions (want at most 3)")
        labels = []
        for k, q in enumerate(qs, 1):
            tag = q.find("p", "qtag")
            tagt = tag[0].txt() if tag else ""
            label = tagt.split("·")[0].strip()
            if not any(ty in label for ty in TYPES):
                probs.append(f"q{k}: unknown question type {label!r}")
            labels.append(label)
            if q.attrs.get("id") != f"q{k}":
                probs.append(f"q{k}: id {q.attrs.get('id')}")
            if not tag or not tag[0].find("a", "ref"):
                probs.append(f"q{k}: qtag without a.ref")
            if not q.find("p", "qtext"):
                probs.append(f"q{k}: no qtext")
            ctx = q.find("p", "qctx")
            if not ctx or not ctx[0].txt().startswith("情境："):
                probs.append(f"q{k}: qctx missing or not 情境：")
            cov = q.find("div", "qcover")
            if not cov or len(cov[0].find("li")) != 3:
                probs.append(f"q{k}: qcover li != 3")
            elif len([li for li in cov[0].find("li") if li.find("span", "qh")]) != 3:
                probs.append(f"q{k}: every qcover point needs span.qh 提示")
            if q.find("p", "gh-talk"):
                probs.append(f"q{k}: 進階題 must not link to GitHub (run tools/discuss.py)")
            dets = q.find("details")
            sums = [x.find("summary")[0].txt().strip() if x.find("summary") else "" for x in dets]
            if sums != ["作答範本", "參考觀點與追問"]:
                probs.append(f"q{k}: details {sums}")
            else:
                if "qstart" not in dets[0].cls():
                    probs.append(f"q{k}: 作答範本 must be details.qstart")
                if len(dets[0].find("p", "tpl")) < 2:
                    probs.append(f"q{k}: 作答範本 needs >= 2 p.tpl")
                ref = dets[1]
                lis = ref.find("li")
                follow = [pp for pp in ref.txt().split("\n") if "追問" in pp]
                if not 4 <= len(lis) <= 6:
                    probs.append(f"q{k}: reference points {len(lis)}")
                if not follow:
                    probs.append(f"q{k}: no 追問")
            rep_len = len(q.txt())
            rep.append(f"q{k}:{tagt.split('·')[0].strip()}({rep_len})")
        if len(set(labels)) != len(labels):
            probs.append(f"進階題 types repeat: {labels}")
        quiz = d.find("div", "quiz")
        if not quiz or len(quiz[0].find("details")) != 3:
            probs.append("self-check quiz != 3")
    t = sec("s-try")
    if t:
        ex = t.find("details", "ex")
        rep.append(f"ex={len(ex)}")
        if not 2 <= len(ex) <= 4:
            probs.append(f"s-try has {len(ex)} examples")
        for e in ex:
            if e.attrs.get("open") is not None:
                probs.append("an example is open by default")
    sub = (root.find(id="s-submit") or [None])[0]  # div.submit inside #s-discuss since 2026-10-27
    if not sub:
        probs.append("no #s-submit (GitHub block at the end of #s-discuss)")
    elif not any((x.attrs.get("href") or "").startswith(ISSUE) for x in sub.find("a")):
        probs.append("#s-submit has no link to the lecture issue (run tools/discuss.py)")
    w = sec("wrap") or (root.find(id="wrap") or [None])[0]
    if not w or not w.find("ol", "rg"):
        probs.append("no ol.rg reading list in #wrap")
    if root.find(cls="proto"):
        probs.append(".proto banner present")
    if root.find(id="gist-toggle"):
        probs.append("gist toggle present")
    for pat in FORBID:
        if re.search(pat, text, re.I):
            probs.append(f"forbidden pattern {pat}")
    print(f"== {Path(path).name}: " + " ".join(rep))
    for x in warns:
        print("  warn:", x)
    if probs:
        print("PROBLEMS:")
        for x in probs:
            print("  -", x)
    else:
        print("OK")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        check(a)
