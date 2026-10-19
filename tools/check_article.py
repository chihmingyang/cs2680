#!/usr/bin/env python3
"""Validate a lecture page in the architecture-article format.

Usage: python3 -I check_article.py site/lXX.html --pages N --pdf FILE.pdf [--fix-time]

Checks: tag balance; required sections (#s-arch #s-ideas #s-background #s-beyond
#s-discuss #s-try #wrap) and parts (tldr, diagram, quiz, reading list, pager, fineprint,
read-time, read-box, side nav); nav anchors; every a.ref points at the PDF with #page in 1..N;
data-pages-total equals N; STE heuristics on prose; reading time.

Reading time (400 text units per minute):
  main  = text a reader sees before opening anything: every <details> body is left
          out, its <summary> line is kept. This is the 「閱讀」 number.
  deep  = text inside <details class="ex deep"> (the optional 深入 blocks).
  full  = all text with every block opened.
--fix-time writes main to span.read-time, deep to span.deep-time and full to
span.full-time (each only if the page has that span).
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr",
        "path", "circle", "line", "rect", "polyline", "polygon"}
SKIP = {"pre", "code", "svg", "summary", "figcaption", "script", "style"}
PROSE_CLASSES = {"prose", "hint", "qtext", "lede", "thesis", "exbody", "answer", "note-own"}
FILLERS = ["其實", "基本上", "非常", "相當", "可以說", "事實上", "總而言之", "簡單來說", "換句話說", "顯然"]
CJK = re.compile(r"[㐀-鿿豈-﫿]")
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.'/+-]*")
REQUIRED_IDS = ["s-arch", "s-ideas", "s-background", "s-beyond", "s-discuss", "s-try", "wrap", "read-box"]
REQUIRED_CLASSES = ["section.tldr", "figure.diagram", "ol.qlist", "div.quiz", "nav.pager",
                    "p.fineprint", "span.read-time"]
# the page layout changed over time; one of each group must be present
REQUIRED_ANY = [("nav.toc", "aside.sidenav"), ("ul.reading", "ol.rg")]
DEEP = re.compile(r'<details class="ex deep"[^>]*>.*?</details>', re.S)


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
        if (tag == "nav" and "toc" in cls) or (tag in {"ol"} and "sn-secs" in cls):
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
        if tag == "nav" or (tag == "ol" and self.in_toc and not any(t == "ol" for t, _, _ in self.stack)):
            self.in_toc = False

    def handle_data(self, data):
        if self.prose_depth and not self.skip_depth:
            self.text.append(data)


def visible_only(h):
    """Drop every <details> body (nested ones too); keep the top-level <summary> lines."""
    out, depth = [], 0
    for tok in re.split(r"(<details\b[^>]*>|</details>|<summary\b.*?</summary>)", h, flags=re.S):
        if tok.startswith("<details"):
            depth += 1
        elif tok == "</details>":
            depth -= 1
        elif tok.startswith("<summary"):
            if depth <= 1:
                out.append(tok)
        elif depth == 0:
            out.append(tok)
    return "".join(out)


def units(s):
    return len(CJK.findall(s)) + len(WORD.findall(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--fix-time", action="store_true")
    ap.add_argument("--long", type=int, default=50)
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
    for group in REQUIRED_ANY:
        if not any(c in p.seen for c in group):
            problems.append(f"missing {' or '.join(group)}")
    m_total = re.search(r'data-pages-total="(\d+)"', html)
    if m_total and int(m_total.group(1)) != args.pages:
        problems.append(f"data-pages-total={m_total.group(1)} but --pages {args.pages}")
    for a in p.toc:
        if a not in p.ids:
            problems.append(f"TOC link #{a} has no target")
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
    main_html = re.sub(r"<script.*?</script>|<svg.*?</svg>", " ", html.split("<main", 1)[-1], flags=re.S)
    deep_html = "".join(DEEP.findall(main_html))
    total = units(re.sub(r"<[^>]+>", " ", visible_only(main_html)))
    deep_total = units(re.sub(r"<[^>]+>", " ", deep_html))
    full_total = units(re.sub(r"<[^>]+>", " ", main_html))

    def to_min(u):
        raw = u / 400
        return int(-(-raw // 1)) if raw < 15 else max(5, round(raw / 5) * 5)
    minutes = to_min(total)
    deep_minutes = to_min(deep_total) if deep_total else 0
    full_minutes = to_min(full_total)

    print(f"{path.name}: {len(p.refs)} slide refs, {len(sentences)} prose sentences "
          f"(avg {sum(map(units, sentences)) / max(1, len(sentences)):.1f} units, > {args.long}: {len(long_ones)})")
    for s in long_ones[:10]:
        print(f"    LONG({units(s)}): {s[:80]}")
    if fillers:
        print(f"  filler words: {fillers}")
    print(f"  passive 被: {passive}; main (closed blocks): {total} units -> about {minutes} min"
          + (f"; deep blocks: {len(DEEP.findall(main_html))}, {deep_total} units -> about {deep_minutes} min" if deep_total else "")
          + f"; everything open: {full_total} units -> about {full_minutes} min")
    if args.fix_time:
        new = re.sub(r'<span class="read-time">[^<]*</span>', f'<span class="read-time">約 {minutes} 分鐘</span>', html, count=1)
        if deep_total:
            new = re.sub(r'<span class="deep-time">[^<]*</span>', f'<span class="deep-time">約 {deep_minutes} 分鐘</span>', new, count=1)
        new = re.sub(r'<span class="full-time">[^<]*</span>', f'<span class="full-time">約 {full_minutes} 分鐘</span>', new, count=1)
        if new != html:
            path.write_text(new, encoding="utf-8")
            print(f"  read-time set to 約 {minutes} 分鐘")
    if problems:
        print("PROBLEMS:")
        for x in problems:
            print("  - " + x)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
