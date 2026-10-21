#!/usr/bin/env python3
"""把延伸閱讀的摘要片段插進講次頁。

用法：
  python3 -I tools/insert_digest.py docs/l04.html notes/digests/l04-r*.html
  python3 -I tools/insert_digest.py docs/l04.html --check      # 只檢查，不插入

片段檔格式見 guide/STYLE_DIGEST.md：第一行是
  <!-- source: <url> | read: yes/partial/no | note: ... -->
接著是 <details class="rg-dg">…</details>。

做什麼：
1. 依 source 網址找到頁面裡的 a.rg-t（arXiv 比對 id，abs／pdf／html 都算），
   把片段插在該 li 的 </li> 之前；該 li 已有 rg-dg 就整段換掉（可重跑）。
2. 重寫 p.rg-intro 裡「『必讀』的 N 篇各附一段摘要」那一句，
   改成「『必讀』與『推薦』的 N 篇各附一段摘要」，N 是頁面裡 rg-dg 的數量。
   L1 這類沒有這句的頁面會在 rg-intro 結尾補一句。
3. 檢查每段 rg-dg：錨點 href="#…" 在頁面存在；「p.N」「p.N–M」不超過 data-pages-total
   （「L5 p.36」這種跨堂引用不檢查）。
"""
import re
import sys
from pathlib import Path

INDENT = " " * 10
INTRO_SENT = "的 {n} 篇各附一段摘要：3 分鐘讀完它的主張與數字、它和 slides 重疊的部分，以及原文哪幾節值得看。"


def norm_url(u: str) -> str:
    u = u.strip().rstrip("/")
    m = re.search(r"arxiv\.org/(?:abs|pdf|html)/([0-9.]+?)(?:v\d+)?(?:\.pdf)?$", u)
    if m:
        return "arxiv:" + m.group(1)
    return re.sub(r"^https?://(www\.)?", "", u)


def find_li_span(html: str, pos: int):
    """pos 在某個 li 裡。回傳 (li_start, li_end) 其中 li_end 指向 </li> 的開頭。"""
    start = html.rfind("<li>", 0, pos)
    if start < 0:
        start = html.rfind("<li ", 0, pos)
    depth = 0
    i = start
    while True:
        m = re.compile(r"<li\b|</li>").search(html, i)
        if not m:
            raise SystemExit("unbalanced <li>")
        if m.group(0).startswith("<li"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start, m.start()
        i = m.end()


def insert(html: str, frag_path: Path) -> tuple[str, str]:
    text = frag_path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--\s*source:\s*(\S+)", text)
    if not m:
        raise SystemExit(f"{frag_path}: no source comment")
    src = norm_url(m.group(1))
    body = text[text.index("<details"):].strip()
    if not body.startswith('<details class="rg-dg">') or not body.endswith("</details>"):
        raise SystemExit(f"{frag_path}: fragment must be a single details.rg-dg")

    target = None
    for a in re.finditer(r'<a class="rg-t" href="([^"]+)"', html):
        if norm_url(a.group(1)) == src:
            target = a
            break
    if not target:
        raise SystemExit(f"{frag_path}: no a.rg-t for {m.group(1)}")

    li_start, li_end = find_li_span(html, target.start())
    li = html[li_start:li_end]
    indented = "\n".join(INDENT + line if line.strip() else line for line in body.splitlines())
    old = re.search(r"\n *<details class=\"rg-dg\">.*?</details>", li, re.S)
    if old:
        new_li = li[: old.start()] + "\n" + indented + li[old.end():]
        action = "replaced"
    else:
        new_li = li.rstrip() + "\n" + indented + "\n" + INDENT
        action = "inserted"
    return html[:li_start] + new_li + html[li_end:], action


def fix_intro(html: str) -> str:
    """篇數與措辭依頁面實際有的摘要：只有必讀、只有推薦，或兩者都有。"""
    levels = []
    for li in re.finditer(r"<li>\s*<div class=\"rg-top\">.*?</li>", html, re.S):
        if '<details class="rg-dg">' in li.group(0):
            levels.append(re.search(r'data-level="(\d)"', li.group(0)).group(1))
    n = len(levels)
    who = "「必讀」與「推薦」" if {"3", "2"} <= set(levels) else ("「推薦」" if "2" in levels else "「必讀」")
    sent = who + INTRO_SENT.format(n=n)
    m = re.search(r'(<p class="rg-intro">)(.*?)(</p>)', html, re.S)
    if not m or n == 0:
        return html
    intro = m.group(2)
    pat = re.compile(r"「(?:必讀|推薦)」(?:與「推薦」)?的 \d+ 篇各附一段摘要：[^。]*。")
    if pat.search(intro):
        intro = pat.sub(sent, intro)
    else:
        intro = intro.rstrip() + sent
    return html[: m.start(2)] + intro + html[m.end(2):]


def check(html: str, name: str) -> int:
    problems = 0
    total = int(re.search(r'data-pages-total="(\d+)"', html).group(1))
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    for i, dg in enumerate(re.finditer(r'<details class="rg-dg">.*?</details>', html, re.S), 1):
        seg = dg.group(0)
        title = html[:dg.start()]
        t = re.findall(r'<a class="rg-t" [^>]*>([^<]+)</a>', title)
        label = t[-1] if t else f"#{i}"
        for a in re.findall(r'href="#([^"]+)"', seg):
            if a not in ids:
                print(f"  {name}: [{label}] anchor #{a} missing")
                problems += 1
        plain = re.sub(r"<[^>]+>", "", seg)
        for mm in re.finditer(r"(?<![A-Za-z0-9])(L\d+\s+)?p\.(\d+)(?:[–-](\d+))?", plain):
            if mm.group(1):
                continue
            for g in (mm.group(2), mm.group(3)):
                if g and int(g) > total:
                    print(f"  {name}: [{label}] p.{g} > total {total}")
                    problems += 1
        chars = len(re.findall(r"[一-鿿]|[A-Za-z0-9][A-Za-z0-9.+_/-]*", plain))
        if not 450 <= chars <= 800:
            print(f"  {name}: [{label}] length {chars} (want 450–800)")
        if "別誤讀" not in seg:
            print(f"  {name}: [{label}] no 別誤讀")
            problems += 1
    return problems


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    page = Path(argv[1])
    html = page.read_text(encoding="utf-8")
    only_check = "--check" in argv
    frags = [Path(a) for a in argv[2:] if a != "--check"]
    if not only_check:
        for f in frags:
            html, action = insert(html, f)
            print(f"  {action}: {f.name}")
        html = fix_intro(html)
        page.write_text(html, encoding="utf-8")
    bad = check(html, page.name)
    print("OK" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
