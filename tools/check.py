#!/usr/bin/env python3
"""Validate one CS2680 lecture page.

Usage: python3 -I check.py PATH/lXX.html --pages N [--pdf FILE.pdf] [--fix-time]

Checks
  1. tag balance (non-void elements closed in order)
  2. every slide page 1..N appears in exactly one article.slide[data-pages]
  3. each slide tab links to <pdf>#page=<first page> and the article id is p<first>
  4. required page parts exist (tldr, toc, wrap, quiz, reading, read-box, pager, fineprint)
  5. TOC anchors resolve to ids in the page
  6. STE heuristics on .gist/.teach prose: long sentences, filler words, passive 被, em dashes
  7. reading-time estimate; --fix-time rewrites the .read-time span
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
FILLERS = ["其實", "基本上", "非常", "相當", "可以說", "事實上", "總而言之", "簡單來說", "換句話說", "某種程度上", "顯然", "毋庸置疑"]
CJK = re.compile(r"[㐀-鿿豈-﫿]")
LATIN_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.'/+-]*")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.ids = set()
        self.slides = []          # (data-pages, id, tab_href)
        self.classes_seen = set()
        self.toc_links = []
        self.prose = []           # text from .gist / .teach (excluding pre/code/table)
        self._prose_depth = []    # stack flags: inside gist/teach
        self._skip_depth = 0      # inside pre/code/table/figcaption/svg
        self._current_slide = None
        self._in_toc = False
        self.lecture_attr = None
        self.has_read_box = False
        self.companion = False    # main[data-format="companion"]: coverage by section ranges
        self.sections = []        # section.part[data-pages]
        self._cur_section = None
        self.notes = []           # (href, section pages) for a.pg links

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        self.classes_seen |= {f"{tag}.{c}" for c in cls} | {tag}
        if "id" in a:
            if a["id"] in self.ids:
                self.errors.append(f"duplicate id: {a['id']}")
            self.ids.add(a["id"])
        if a.get("data-lecture"):
            self.lecture_attr = a["data-lecture"]
        if tag == "main" and a.get("data-format") == "companion":
            self.companion = True
        if tag == "section" and "part" in cls and a.get("data-pages"):
            self._cur_section = {"pages": a.get("data-pages"), "id": a.get("id"), "tab": None}
            self.sections.append(self._cur_section)
        if tag == "a" and "pg" in cls:
            self.notes.append((a.get("href") or "", self._cur_section["pages"] if self._cur_section else None))
        if tag == "input" and a.get("id") == "read-box":
            self.has_read_box = True
        if tag == "article" and "slide" in cls and not a.get("data-aux-pages"):
            self._current_slide = {"pages": a.get("data-pages"), "id": a.get("id"), "tab": None}
            self.slides.append(self._current_slide)
        if tag == "a" and "tab" in cls and self._current_slide is not None:
            self._current_slide["tab"] = a.get("href")
        if tag == "nav" and "toc" in cls:
            self._in_toc = True
        if tag == "a" and self._in_toc and (a.get("href") or "").startswith("#"):
            self.toc_links.append(a["href"][1:])
        prose_here = bool(cls & {"gist", "teach", "story", "nb"})
        if tag in {"pre", "code", "table", "figcaption", "svg", "summary"}:
            self._skip_depth += 1 if tag not in VOID else 0
        if tag not in VOID:
            self.stack.append((tag, prose_here, tag in {"pre", "code", "table", "figcaption", "svg", "summary"}))
            if prose_here:
                self._prose_depth.append(True)
        if tag in {"p", "li", "br", "td"} and self._prose_depth:
            self.prose.append("\n")

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "input" and a.get("id") == "read-box":
            self.has_read_box = True

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}>")
            return
        top, prose_here, skip_here = self.stack[-1]
        if top != tag:
            # find it deeper to report precisely
            names = [t for t, _, _ in self.stack]
            if tag in names:
                while self.stack and self.stack[-1][0] != tag:
                    t, ph, sk = self.stack.pop()
                    self.errors.append(f"unclosed <{t}> before </{tag}> (line {self.getpos()[0]})")
                    if ph and self._prose_depth:
                        self._prose_depth.pop()
                    if sk:
                        self._skip_depth -= 1
                top, prose_here, skip_here = self.stack[-1]
            else:
                self.errors.append(f"unexpected </{tag}> at line {self.getpos()[0]} (open: <{top}>)")
                return
        self.stack.pop()
        if prose_here and self._prose_depth:
            self._prose_depth.pop()
        if skip_here:
            self._skip_depth -= 1
        if tag == "article":
            self._current_slide = None
        if tag == "section":
            self._cur_section = None
        if tag == "nav":
            self._in_toc = False

    def handle_data(self, data):
        if self._prose_depth and self._skip_depth == 0:
            self.prose.append(data)


def expand(spec):
    pages = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            pages.extend(range(int(lo), int(hi) + 1))
        else:
            pages.append(int(part))
    return pages


def text_units(s):
    return len(CJK.findall(s)) + len(LATIN_WORD.findall(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--pages", type=int, required=True)
    ap.add_argument("--pdf", default=None, help="expected pdf file name in tab links")
    ap.add_argument("--fix-time", action="store_true")
    ap.add_argument("--long", type=int, default=55, help="flag sentences longer than this many units")
    args = ap.parse_args()

    path = Path(args.path)
    html = path.read_text(encoding="utf-8")
    p = Page()
    p.feed(html)
    p.close()
    problems = list(p.errors)
    for t, _, _ in p.stack:
        if t not in {"html", "body"}:
            problems.append(f"unclosed <{t}> at end of file")

    # coverage
    seen = {}
    entries = p.sections if p.companion else p.slides
    for s in entries:
        if not s["pages"]:
            problems.append(f"slide without data-pages (id={s['id']})")
            continue
        try:
            pages = expand(s["pages"])
        except ValueError:
            problems.append(f"bad data-pages {s['pages']!r}")
            continue
        first = pages[0]
        if not p.companion:
            if s["id"] != f"p{first}":
                problems.append(f"slide data-pages={s['pages']} has id={s['id']!r}, expected 'p{first}'")
            tab = s["tab"] or ""
            if not tab.endswith(f"#page={first}"):
                problems.append(f"slide {s['pages']}: tab href {tab!r} should end with #page={first}")
            if args.pdf and args.pdf not in tab:
                problems.append(f"slide {s['pages']}: tab href does not point at {args.pdf}")
        for pg in pages:
            if pg in seen:
                problems.append(f"page {pg} covered twice ({seen[pg]} and {s['pages']})")
            seen[pg] = s["pages"]
    missing = [i for i in range(1, args.pages + 1) if i not in seen]
    extra = sorted(i for i in seen if i > args.pages or i < 1)
    if missing:
        problems.append(f"pages not covered: {missing}")
    if extra:
        problems.append(f"pages outside 1..{args.pages}: {extra}")
    order = [expand(s['pages'])[0] for s in entries if s['pages']]
    if order != sorted(order):
        problems.append("slides are not in page order")
    if p.companion:
        for href, sec in p.notes:
            m = re.search(r"#page=(\d+)$", href)
            if not m:
                problems.append(f"note link without #page: {href}")
                continue
            if args.pdf and args.pdf not in href:
                problems.append(f"note link does not point at {args.pdf}: {href}")
            if sec and int(m.group(1)) not in expand(sec):
                problems.append(f"note p.{m.group(1)} sits outside its section p.{sec}")

    # required parts
    required = {
        "section.tldr": "先看這裡 panel",
        "nav.toc": "section index",
        "section.wrap": "wrap-up section",
        "div.quiz": "self-check quiz",
        "ul.reading": "reading list",
        "nav.pager": "prev/next pager",
        "p.fineprint": "fine print",
        "span.read-time": "reading-time span",
    }
    for key, label in required.items():
        if key not in p.classes_seen:
            problems.append(f"missing {label} ({key})")
    if not p.has_read_box:
        problems.append("missing read-box checkbox")
    if not p.lecture_attr:
        problems.append("missing data-lecture attribute")
    for anchor in p.toc_links:
        if anchor not in p.ids:
            problems.append(f"TOC link #{anchor} has no target")
    if "<title>" not in html[:8192]:
        problems.append("no <title> in first 8KB")

    # STE heuristics
    prose = "".join(p.prose)
    sentences = [x.strip() for x in re.split(r"[。!?;\n]+", prose) if x.strip()]
    long_ones = [x for x in sentences if text_units(x) > args.long]
    fillers = {f: prose.count(f) for f in FILLERS if f in prose}
    passive = len(re.findall(r"被[一-鿿]", prose))
    dashes = prose.count("——") + prose.count(" — ")

    units = text_units(re.sub(r"<[^>]+>", " ", html.split("<main", 1)[-1]))
    raw_min = units / 400
    minutes = -(-int(raw_min * 10) // 10) if raw_min < 15 else max(5, round(raw_min / 5) * 5)
    minutes = int(-(-raw_min // 1)) if raw_min < 15 else minutes

    kind = f"{len(p.sections)} sections, {len(p.notes)} notes" if p.companion else f"{len(p.slides)} slide entries"
    print(f"{path.name}: {kind}, pages covered {len(seen)}/{args.pages}")
    print(f"  prose sentences: {len(sentences)}, avg units {sum(map(text_units, sentences)) / max(1, len(sentences)):.1f}, "
          f"> {args.long} units: {len(long_ones)}")
    for x in long_ones[:12]:
        print(f"    LONG({text_units(x)}): {x[:90]}")
    if fillers:
        print(f"  filler words: {fillers}")
    print(f"  passive 被 count: {passive}; em-dash count: {dashes}")
    print(f"  text units: {units} -> reading time about {minutes} min")

    if args.fix_time:
        new = re.sub(r'<span class="read-time">[^<]*</span>', f'<span class="read-time">約 {minutes} 分鐘</span>', html, count=1)
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
