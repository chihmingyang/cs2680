#!/usr/bin/env python3
"""Validate a lecture page in the architecture-article format.

Usage: python3 -I check_article.py docs/lXX.html --pages N --pdf FILE.pdf [--fix-time]

Checks: tag balance; required sections (#s-arch #s-ideas [#s-background, #s-beyond optional]
#s-discuss #s-try #s-submit #wrap) and parts (tldr, diagram, two question tabs,
quiz, reading list ol.rg, pager, fineprint, read-time, full-time, read-box, sidenav);
sidenav anchors; every a.ref points at the PDF with #page in 1..N;
STE heuristics on prose; reading times.

Reading times (400 text units per minute; a CJK character or an English word is 1 unit;
under 15 min: round up; 15 min or more: nearest 5):
  read-time  text a reader sees with every <details> closed (summaries count), no SVG text
  deep-time  text inside details.deep and details.gloss (深入 / 本文延伸 / 名詞註 blocks)
  full-time  all text in <main>, no SVG text
--fix-time writes all three spans. The formula reproduces the numbers on L1-L8 (2026-10-19).
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr",
        "path", "circle", "line", "rect", "polyline", "polygon"}
SKIP = {"pre", "code", "svg", "summary", "figcaption", "script", "style"}
PROSE_CLASSES = {"prose", "hint", "qtext", "qctx", "qh", "lede", "qset-lede", "thesis", "exbody", "answer",
                 "note-own", "rg-s", "rg-g"}
FILLERS = ["其實", "基本上", "非常", "相當", "可以說", "事實上", "總而言之", "簡單來說", "換句話說", "顯然"]
CJK = re.compile(r"[㐀-鿿豈-﫿]")
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.'/+-]*")
# s-beyond optional since 2026-10-26 (L4); s-background optional since 2026-10-27 (L4 merged it into #s-ideas)
REQUIRED_IDS = ["s-arch", "s-ideas", "s-discuss", "s-try", "s-submit", "wrap",
                "read-box", "qset-basic", "qset-adv", "sidenav"]
REQUIRED_CLASSES = ["section.tldr", "figure.diagram", "div.qtabs", "ol.qlist", "div.quiz", "ol.rg", "nav.pager",
                    "p.fineprint", "span.read-time", "span.full-time", "aside.sidenav", "nav.lecnav"]


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.ids, self.seen = [], [], set(), set()
        self.refs, self.toc, self.text = [], [], []
        self.prose_depth = 0
        self.skip_depth = 0
        self.in_toc = False
        self.dd_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        self.seen |= {f"{tag}.{c}" for c in cls}
        if "id" in a:
            if a["id"] in self.ids:
                self.errors.append(f"duplicate id {a['id']}")
            self.ids.add(a["id"])
        if tag == "a" and "ref" in cls:
            self.refs.append(a.get("href") or "")
        if tag == "aside" and "sidenav" in cls:
            self.in_toc = True
        if tag == "a" and self.in_toc and (a.get("href") or "").startswith("#"):
            self.toc.append(a["href"][1:])
        if tag in VOID:
            return
        is_prose = bool(cls & PROSE_CLASSES) or tag == "dd"
        is_skip = tag in SKIP
        self.stack.append((tag, is_prose, is_skip))
        if is_prose:
            self.prose_depth += 1
        if is_skip:
            self.skip_depth += 1
        if tag in {"p", "li", "dd"} and self.prose_depth:
            self.text.append("\n")

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        names = [t for t, _, _ in self.stack]
        if tag not in names:
            self.errors.append(f"unexpected </{tag}> at line {self.getpos()[0]}")
            return
        while self.stack:
            t, pr, sk = self.stack.pop()
            if pr:
                self.prose_depth -= 1
            if sk:
                self.skip_depth -= 1
            if t == tag:
                break
            self.errors.append(f"unclosed <{t}> before </{tag}> (line {self.getpos()[0]})")
        if tag == "aside":
            self.in_toc = False

    def handle_data(self, data):
        if self.prose_depth and not self.skip_depth:
            self.text.append(data)


def units(s):
    return len(CJK.findall(s)) + len(WORD.findall(s))


class Vis(HTMLParser):
    """Sum text units of <main> into three buckets for the reading times."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.b = {"read-time": 0, "deep-time": 0, "full-time": 0}

    def handle_starttag(self, tag, attrs):
        if tag in VOID - {"path", "circle", "line", "rect", "polyline", "polygon"}:
            return
        self.stack.append((tag, set((dict(attrs).get("class") or "").split())))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in [t for t, _ in self.stack]:
            while self.stack and self.stack.pop()[0] != tag:
                pass

    def handle_data(self, data):
        tags = [t for t, _ in self.stack]
        if "main" not in tags or "svg" in tags or "script" in tags:
            return
        n = units(data)
        self.b["full-time"] += n
        if any(("deep" in c or "gloss" in c) for t, c in self.stack if t == "details"):
            self.b["deep-time"] += n
        d = tags.count("details")
        if d == 0 or (d == 1 and "summary" in tags[tags.index("details"):]):
            self.b["read-time"] += n


def minutes(n):
    raw = n / 400
    return int(-(-raw // 1)) if raw < 15 else max(5, round(raw / 5) * 5)


def times(html):
    v = Vis()
    v.feed(html)
    return {k: (minutes(n) if n else 0) for k, n in v.b.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--fix-time", action="store_true")
    ap.add_argument("--long", type=int, default=70)  # 2026-10-22: 推理段落放寬到 70 字（STYLE_ARTICLE 第 5 節）
    args = ap.parse_args()
    path = Path(args.path)
    html = path.read_text(encoding="utf-8")
    p = P()
    p.feed(html)
    p.close()
    problems = list(p.errors)
    for t, _, _ in p.stack:
        if t not in {"html", "body"}:
            problems.append(f"unclosed <{t}> at end of file")
    for i in REQUIRED_IDS:
        if i not in p.ids:
            problems.append(f"missing #{i}")
    for c in REQUIRED_CLASSES:
        if c not in p.seen:
            problems.append(f"missing {c}")
    for a in p.toc:
        if a not in p.ids:
            problems.append(f"sidenav link #{a} has no target")
    for href in p.refs:
        m = re.search(r"#page=(\d+)$", href)
        if args.pdf not in href or not m:
            problems.append(f"bad slide ref {href}")
        elif not 1 <= int(m.group(1)) <= args.pages:
            problems.append(f"slide ref outside 1..{args.pages}: {href}")
    if "<title>" not in html[:8192]:
        problems.append("no <title> in first 8KB")

    prose = "".join(p.text)
    sentences = [s.strip() for s in re.split(r"[。！？；\n]+", prose) if s.strip()]
    long_ones = [s for s in sentences if units(s) > args.long]
    fillers = {f: prose.count(f) for f in FILLERS if f in prose}
    passive = len(re.findall(r"被[一-鿿]", prose))
    t = times(html)
    print(f"{path.name}: {len(p.refs)} slide refs, {len(sentences)} prose sentences "
          f"(avg {sum(map(units, sentences)) / max(1, len(sentences)):.1f} units, > {args.long}: {len(long_ones)})")
    for s in long_ones[:10]:
        print(f"    LONG({units(s)}): {s[:80]}")
    if fillers:
        print(f"  filler words: {fillers}")
    print(f"  passive 被: {passive}; reading time: " + ", ".join(f"{k} {v} min" for k, v in t.items() if v))
    if args.fix_time:
        new = html
        for k, v in t.items():
            if v:
                new = re.sub(rf'<span class="{k}">[^<]*</span>', f'<span class="{k}">約 {v} 分鐘</span>', new, count=1)
        if new != html:
            path.write_text(new, encoding="utf-8")
            print("  reading-time spans updated")
    if problems:
        print("PROBLEMS:")
        for x in problems:
            print("  - " + x)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
