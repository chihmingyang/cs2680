#!/usr/bin/env python3
"""Validate a lecture page in the architecture-article format.

Usage: python3 -I check_article.py docs/lXX.html --pages N --pdf FILE.pdf [--fix-time]

Checks: tag balance; required sections (#s-ideas [#s-arch optional since v7; #s-background, #s-beyond optional]
#wrap; 問題討論 removed 2026-11-09; #s-try 動手試試 removed 2026-11-17 and now a problem if present) and parts (tldr, diagram,
reading list ol.rg, pager, fineprint, read-time, full-time, read-box, sidenav);
sidenav anchors; every a.ref points at the PDF with #page in 1..N;
STE heuristics on prose; reading times;
red key points (<strong>, STYLE_ARTICLE 6c): never inside b/a/code/pre/headings/summary/figcaption/
figure/svg/table/nav/aside/details.gloss and no <b> inside them (problems); one mark per ~200 units of
main chapter prose outside any <details> (target = round(units / 200), 1..5; target-1 is fine),
plus at most 1 inside 深入/本文延伸 blocks per chapter, tldr exactly 3, #s-arch exactly 1, each mark <= 30 units (warnings);
inline lists (STYLE_ARTICLE 4, v5.6): a <p> with 4+ items joined by ； warns (skips p.lede, 相關：, p[data-inline]).
table cells (REVIEW_READABILITY R5/R6, 2026-11-06): a <td> whose text is a source (link, or 公司／年月) + ：
+ fewer than 12 units warns "引用只有出處"; a hedge (單一公司／單方／不是對照實驗／數字會變) outside
parentheses warns "保留語不在括號裡". Both are the mechanical half of the readability review.
number load (REVIEW_READABILITY R18, 2026-11-16): a <p> with more than 5 numbers warns "一段太多數字"
(chapter refs 第 N 章, L8, dates, model versions such as Opus 5.5 and code do not count; a worked
calculation can opt out with <p data-inline>). The fix is a figure or table, not more labels.

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
# 2026-10-28: where a red key point (<strong>) may not go
# 2026-11-20 (James：查閱區塊和表裡也標紅字): table cells and details.gloss are allowed now; th is not
STRONG_NOT_IN = {"b", "a", "code", "pre", "h1", "h2", "h3", "h4", "summary", "figcaption", "figure", "svg",
                 "th", "nav", "aside", "strong"}
CJK = re.compile(r"[㐀-鿿豈-﫿]")
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.'/+-]*")
# s-beyond optional since 2026-10-26 (L4); s-background optional since 2026-10-27 (L4 merged it into #s-ideas)
REQUIRED_IDS = ["s-ideas", "wrap", "read-box", "sidenav"]  # 問題討論 removed 2026-11-09, 動手試試 2026-11-17
REQUIRED_CLASSES = ["section.tldr", "figure.diagram", "ol.rg", "nav.pager",
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
        self.anc = []            # (tag, classes, id) for every open element, parallel to self.stack
        self.strong = None       # the <strong> being read: {"where": ..., "text": ...}
        self.strongs = []

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
        if tag == "strong":
            for t, c, _ in self.anc:
                if t in STRONG_NOT_IN:
                    self.errors.append(f"red mark <strong> inside <{t}> at line {self.getpos()[0]}")
                    break
            where = next((i for t, c, i in reversed(self.anc) if t == "div" and "idea" in c), "")
            where = where or next((i or ("tldr" if "tldr" in c else "") for t, c, i in reversed(self.anc)
                                   if t == "section"), "")
            deep = any(t == "details" and "deep" in c for t, c, _ in self.anc)
            # marks in a 查閱 block or a table cell do not count toward the chapter's main-prose quota
            side = any(t == "table" or (t == "details" and "gloss" in c) for t, c, _ in self.anc)
            self.strong = {"where": where, "text": "", "deep": deep, "side": side}
        elif tag == "b" and self.strong is not None:
            self.errors.append(f"<b> inside a red mark at line {self.getpos()[0]}")
        is_prose = bool(cls & PROSE_CLASSES) or tag == "dd"
        is_skip = tag in SKIP
        self.anc.append((tag, cls, a.get("id") or ""))
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
        if tag == "strong" and self.strong is not None:
            self.strongs.append(self.strong)
            self.strong = None
        while self.stack:
            t, pr, sk = self.stack.pop()
            self.anc.pop()
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
        if self.strong is not None:
            self.strong["text"] += data
        if self.prose_depth and not self.skip_depth:
            self.text.append(data)


class ChapterUnits(HTMLParser):
    """Main-prose units per div.idea: nothing inside <details> (深入、本文延伸、名詞註), code,
    figures, tables, headings or summaries."""
    SKIP_IN = {"pre", "figure", "table", "svg", "summary", "h3", "nav"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.cur, self.u = [], None, {}

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        self.stack.append((tag, cls))
        if tag == "div" and "idea" in cls:
            self.cur = a.get("id")
            self.u[self.cur] = 0

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            t, c = self.stack.pop()
            if t == "div" and "idea" in c:
                self.cur = None
            if t == tag:
                break

    def handle_data(self, data):
        if self.cur and not any(t in self.SKIP_IN or t == "details" for t, c in self.stack):
            self.u[self.cur] += units(data)


def mark_target(n_units):
    return min(5, max(1, int(n_units / 200 + 0.5)))


def mark_max(n_units):
    # 2026-11-13 (James: L6b 的紅字可以再多一點): up to one per ~100 units (2026-11-16)
    return max(mark_target(n_units), int(n_units / 100 + 0.5))


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


def inline_lists(html):
    """STYLE_ARTICLE 4 (v5.6): 4+ parallel items joined by ； in one <p> belong in ul/ol.
    Skipped: p.lede (the group map is right below it), 相關： lines, and <p data-inline> (a chain of
    reasoning or arithmetic that only looks like a list). ； inside <code> does not count."""
    out = []
    for m in re.finditer(r"<p\b([^>]*)>(.*?)</p>", html, re.S):
        attrs, body = m.group(1), m.group(2)
        if "lede" in attrs or "data-inline" in attrs:
            continue
        txt = re.sub(r"<code>.*?</code>", "x", body, flags=re.S)
        txt = re.sub(r"<[^>]+>", "", txt).strip()
        if txt.startswith("相關：") or txt.count("；") < 3:
            continue
        out.append((html.count("\n", 0, m.start()) + 1, txt))
    return out


NUM_SKIP = re.compile(r"第\s*\d+\s*[章段節列項]|\bL\d+b?\b|20\d\d(?:-\d\d){0,2}"
                      r"|(?:Opus|Sonnet|Haiku|Fable|Mythos|GPT|Gemini|Claude|Llama|Qwen|DeepSeek)[ -]?\d+(?:\.\d+)*"
                      r"|\b[A-Z]\d+\b|\bv\d+(?:\.\d+)*")
NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
NUM_LIMIT = 5
# R19 (2026-11-16): course-internal data (the class's own logs and assignments) means nothing to readers
# who never took CS2680. L11 is about the course's assignment statistics, so it is exempt.
COURSE_DATA = re.compile(r"全班|兩份作業|Assignment\s*\d|同學")


def number_load(html):
    """R18 (2026-11-16): (line, count, text) for each <p> with more than NUM_LIMIT numbers.
    James on L8 第 2 章: 「一堆數字，可讀性會好嗎？…乾脆做圖」. Skips <p data-inline> (worked arithmetic)."""
    out = []
    for m in re.finditer(r"<p\b([^>]*)>(.*?)</p>", html, re.S):
        if "data-inline" in m.group(1):
            continue
        txt = re.sub(r"<code>.*?</code>|<sup\b.*?</sup>", "", m.group(2), flags=re.S)
        txt = NUM_SKIP.sub("", re.sub(r"<[^>]+>", "", txt))
        n = len(NUM.findall(txt))
        if n > NUM_LIMIT:
            out.append((html.count("\n", 0, m.start()) + 1, n, re.sub(r"\s+", " ", txt).strip()))
    return out


HEDGES = ("單一公司", "單方經驗", "單方的經驗", "不是對照實驗", "數字會變", "一家的經驗")
SOURCE_HEAD = re.compile(r"^(?:[A-Za-z][\w .&'-]{1,40}|[一-鿿]{2,12})?[（(]?(?:20\d\d(?:[-–]\d\d)?)[)）]?[：:]")


def table_cells(html):
    """(line, text) for every <td> in div.table-wrap tables, tags stripped."""
    out = []
    for m in re.finditer(r"<td\b[^>]*>(.*?)</td>", html, flags=re.S):
        txt = re.sub(r"<[^>]+>", "", m.group(1))
        txt = re.sub(r"\s+", " ", txt).strip()
        out.append((html.count("\n", 0, m.start()) + 1, txt, 'href="http' in m.group(1)))
    return out


def cell_warnings(html):
    for line, txt, has_link in table_cells(html):
        if not txt:
            continue
        head, sep, tail = txt.partition("：")
        tail = tail.split("。")[0]
        if sep and (has_link or SOURCE_HEAD.match(txt)) and units(tail) < 12:
            yield f"line {line}: 格子只有出處，沒說量到什麼 (R5): {txt[:50]}"
        for h in HEDGES:
            i = txt.find(h)
            if i < 0:
                continue
            before = txt[:i]
            if not re.search(r"[。：]", before):
                continue  # the hedge is the cell's own statement (e.g. a 可信度 column), not an appendix
            if before.count("（") + before.count("(") <= before.count("）") + before.count(")"):
                yield f"line {line}: 保留語「{h}」不在括號裡，讀起來像第二個原因 (R6): {txt[:50]}"
                break


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
    if "s-try" in p.ids:  # 2026-11-17 James: 動手試試 拔掉，好的題目搬到整合題（guide/QUIZ.md）
        problems.append("#s-try: 動手試試 2026-11-17 拿掉了；練習題寫成整合題（guide/QUIZ.md），正文要用的指令寫在正文")
    for c in REQUIRED_CLASSES:
        if c not in p.seen:
            problems.append(f"missing {c}")
    for a in p.toc:
        if a not in p.ids:
            problems.append(f"sidenav link #{a} has no target")
    for href in p.refs:
        if href.startswith("#i") and href[1:] in p.ids:
            continue  # v7: a basic question points at a chapter of this page
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
    # red key points (STYLE_ARTICLE 6c): counts are advice, so they print as warn
    per, deep, side = {}, {}, {}
    for m in p.strongs:
        per[m["where"]] = per.get(m["where"], 0) + 1
        deep[m["where"]] = deep.get(m["where"], 0) + (m["deep"] and not m["side"])
        side[m["where"]] = side.get(m["where"], 0) + m["side"]
    cu = ChapterUnits()
    cu.feed(html)
    print(f"  red marks: {len(p.strongs)} (" + ", ".join(f"{k or '?'} {v}" for k, v in per.items()) + ")")
    for i, n in cu.u.items():
        want, got = mark_target(n), per.get(i, 0) - deep.get(i, 0) - side.get(i, 0)
        if not max(1, want - 1) <= got <= mark_max(n):
            print(f"  warn: chapter {i} has {got} red marks in its main prose; {n} units want {want}–{mark_max(n)}")
        if deep.get(i, 0) > 1:
            print(f"  warn: chapter {i} has {deep[i]} red marks inside 深入/本文延伸 (max 1)")
    # 2026-11-20 (James：導讀不限三處): tldr wants at least 3
    if per.get("tldr", 0) < 3:
        print(f"  warn: tldr has {per.get('tldr', 0)} red marks (want at least 3)")
    if 'id="s-arch"' in html and per.get("s-arch", 0) != 1:   # v7 idea-first pages have no 架構 section
        print(f"  warn: s-arch has {per.get('s-arch', 0)} red marks (want 1)")
    # 2026-11-20: every 查閱 block of some length carries at least one mark (James's own colour spans count)
    # only p / li / td count (a block that is one figure has nowhere to put a mark); data-no-red opts a block out
    # (a plain name list with no conclusion, e.g. L3 #d1)
    for g in re.finditer(r'<details class="gloss" id="([^"]+)"([^>]*)>(.*?)</details>', html.split('id="quiz"')[0], re.S):
        if "data-no-red" in g.group(2):
            continue
        body = " ".join(re.findall(r"<(?:p|li|td)\b[^>]*>(.*?)</(?:p|li|td)>", g.group(3), flags=re.S))
        if units(re.sub(r"<[^>]+>", "", body)) >= 120 and "<strong" not in body and "var(--key)" not in body:
            print(f"  warn: 查閱區塊 #{g.group(1)} 沒有紅字（6c：每個區塊至少一處）")
    for m in p.strongs:
        if units(m["text"]) > 30:
            print(f"  warn: long red mark ({units(m['text'])}): {m['text'][:40]}")
    for line, txt in inline_lists(html):
        print(f"  warn: line {line}: {txt.count('；') + 1} items joined by ；, use ul/ol: {txt[:40]}")
    for w in cell_warnings(html):
        print(f"  warn: {w}")
    if not path.name.startswith("l11"):
        body = re.sub(r"<[^>]+>", "", html.split('id="s-src"')[0])
        for m in COURSE_DATA.finditer(body):
            ctx = re.sub(r"\s+", " ", body[max(0, m.start() - 20):m.end() + 20])
            print(f"  warn: 課程內部的數據「{m.group(0)}」：改寫成機制加一個讀者會算的例子（R19）: …{ctx}…")
    for line, n, txt in number_load(html):
        print(f"  warn: line {line}: 一段太多數字（{n} 個），數字進圖或表，句子只講結論（R18）: {txt[:40]}")
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
