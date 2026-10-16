#!/usr/bin/env python3
"""Structural check of an article page's six sections, focused on §5 (discussion).

Usage: python3 -I check_discuss.py site/l01.html [...]
Prints a short report and PROBLEMS / OK per page.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

TYPES = ["概念", "估算", "分析", "設計", "團隊實務", "風險", "取捨", "應用"]
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
        if not 3 <= len(items) <= 5:
            probs.append(f"s-ideas has {len(items)} ideas")
        if len(refs) != len(items):
            probs.append("an idea lacks a.ref")
    bg = sec("s-background")
    if bg:
        dts = bg.find("dt")
        rep.append(f"terms={len(dts)}")
        if not 4 <= len(dts) <= 6:
            probs.append(f"terms={len(dts)}")
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
        if not 6 <= len(bqs) <= 9:
            probs.append(f"{len(bqs)} basic questions")
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
            if sums != ["參考答案"]:
                probs.append(f"b{k}: details {sums}")
            elif not dets[0].find("div", "hint"):
                probs.append(f"b{k}: no hint div")
            if q.find("p", "qctx") or q.find("div", "qcover"):
                probs.append(f"b{k}: basic question must not have qctx/qcover")
        qs = d.find("li", "dq")
        rep.append(f"dq={len(qs)}")
        if len(qs) != 6:
            probs.append(f"{len(qs)} discussion questions")
        kinds = set()
        for k, q in enumerate(qs, 1):
            tag = q.find("p", "qtag")
            tagt = tag[0].txt() if tag else ""
            for ty in TYPES:
                if ty in tagt.split("·")[0]:
                    kinds.add(ty)
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
            dets = q.find("details")
            sums = [x.find("summary")[0].txt().strip() if x.find("summary") else "" for x in dets]
            if sums != ["思考方向", "參考觀點與追問"]:
                probs.append(f"q{k}: details {sums}")
            else:
                ref = dets[1]
                lis = ref.find("li")
                follow = [pp for pp in ref.find("p") if pp.txt().startswith("追問")]
                hint = dets[0].find("div", "hint")
                if not 4 <= len(lis) <= 6:
                    probs.append(f"q{k}: reference points {len(lis)}")
                if not follow:
                    probs.append(f"q{k}: no 追問")
                if not hint:
                    probs.append(f"q{k}: no hint div")
            rep_len = len(q.txt())
            rep.append(f"q{k}:{tagt.split('·')[0].strip()}({rep_len})")
        if len(kinds) < 5:
            probs.append(f"only {len(kinds)} question kinds: {sorted(kinds)}")
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
    if root.find(cls="proto"):
        probs.append(".proto banner present")
    if root.find(id="gist-toggle"):
        probs.append("gist toggle present")
    for pat in FORBID:
        if re.search(pat, text, re.I):
            probs.append(f"forbidden pattern {pat}")
    print(f"== {Path(path).name}: " + " ".join(rep))
    if probs:
        print("PROBLEMS:")
        for x in probs:
            print("  -", x)
    else:
        print("OK")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        check(a)
