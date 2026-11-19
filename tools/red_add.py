#!/usr/bin/env python3
"""加紅字（<strong>）而不改字：給一份清單，每一條是「在哪一段文字之後、標哪幾個字」。

Usage:
  python3 -I tools/red_add.py docs/l08.html marks.json            # 試跑：每一條印 ok 或原因，不寫檔
  python3 -I tools/red_add.py docs/l08.html marks.json --write    # 全部 ok 才寫檔

marks.json 是一個 list，每一條：
  {"after": "頁面上在它前面、找得到的一小段原始 HTML 或文字（用來定位，可以是區塊的 id，例如 id=\\"n-papers\\"）",
   "mark":  "要標紅的那幾個字，照頁面原始 HTML 一字不差（裡面有 <code>…</code> 就整個包進來）"}
工具從 after 第一次出現的位置往後找 mark 第一次出現的位置，包上 <strong>。

為什麼有這支：2026-11-20 紅字的位置放寬到查閱區塊、表、導讀（STYLE_ARTICLE 6c），全站要補一輪。
標紅字的規矩是只搬標籤、一個字都不改（mark-red skill 第 3 步）；手改 HTML 很容易順手動到字，
所以這支只會插入 <strong> 與 </strong>（表的格子裡原本整個用 <b> 標的字，把 <b> 換成 <strong>），而且不寫進下面這些地方：
  已經在 <strong>、<b>、<a>、<code>、<pre>、<th>、<summary>、<figcaption>、標題、<svg> 裡；題庫（<script id="quiz">）之後；
  James 自己標的紅色 span（color: var(--key)）裡。
一處超過 30 個單位（中文字數加英文詞數）也不收：6c 規定紅字是短語。
寫檔之前比對一次：拿掉 <strong> 之後，頁面和原本一模一樣。
"""
import json
import re
import sys
from pathlib import Path

BAD = ("strong", "b", "a", "code", "pre", "th", "summary", "figcaption", "h1", "h2", "h3", "h4", "svg", "script", "style")
CJK = re.compile(r"[㐀-鿿豈-﫿]")
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.'/+-]*")


def units(s):
    s = re.sub(r"<[^>]+>", "", s)
    return len(CJK.findall(s)) + len(WORD.findall(s))


def open_tags(html, pos):
    """tags still open at pos (names, innermost last), plus whether we are inside a key-colour span"""
    stack = []
    for m in re.finditer(r"<(/?)([a-zA-Z0-9]+)([^>]*?)(/?)>", html[:pos]):
        close, name, attrs, selfc = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if selfc or name in ("br", "img", "input", "meta", "link", "hr", "path", "rect", "circle", "line", "col"):
            continue
        if close:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == name:
                    del stack[i:]
                    break
        else:
            stack.append((name, attrs))
    return stack


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    path, marks = Path(args[0]), json.loads(Path(args[1]).read_text(encoding="utf-8"))
    src = path.read_text(encoding="utf-8")
    end = src.find('<script type="application/json" id="quiz"')
    end = len(src) if end < 0 else end
    html, bad = src, 0
    for k, m in enumerate(marks, 1):
        after, mark = m["after"], m["mark"]
        a = html.find(after, 0, end)
        why = None
        if a < 0:
            why = "找不到 after"
        else:
            i = html.find(mark, a, end)
            if i < 0:
                why = "after 之後找不到 mark（要照原始 HTML 一字不差）"
            elif mark.count("<") != mark.count(">") or len(re.findall(r"<[a-zA-Z]", mark)) != len(re.findall(r"</", mark)):
                why = "mark 裡的標籤沒有成對"
            elif units(mark) > 30:
                why = f"太長（{units(mark)} 個單位，上限 30）：只標短語"
            else:
                st = open_tags(html, i)
                hit = next((n for n, _ in st if n in BAD), None)
                # 表的格子裡整個 <b>…</b> 就是要標的字（原本用黑色粗體標贏的那一格）：把 <b> 換成 <strong>
                if (hit == "b" and html[i - 3:i] == "<b>" and html[i + len(mark):i + len(mark) + 4] == "</b>"
                        and any(n == "td" for n, _ in st) and [n for n, _ in st if n in BAD] == ["b"]):
                    html = html[:i - 3] + "<strong>" + mark + "</strong>" + html[i + len(mark) + 4:]
                    end += len("<strong></strong>") - len("<b></b>")
                    print(f"ok   {k}: {re.sub(r'<[^>]+>', '', mark)[:50]}（格子裡的 <b> 換成 <strong>）")
                    continue
                if hit:
                    why = f"位置在 <{hit}> 裡"
                elif any("var(--key)" in at for _, at in st):
                    why = "位置在 James 標的紅色裡"
                elif not any(n in ("p", "li", "td", "dd") for n, _ in st):
                    why = "位置不在 p、li、td 裡"
                elif re.search(r"<(b|a|strong)\b", mark):
                    why = "mark 裡包了 <b>、<a> 或 <strong>"
        if why:
            bad += 1
            print(f"FAIL {k}: {why}　mark={mark[:40]!r}　after={after[:30]!r}")
            continue
        html = html[:i] + "<strong>" + mark + "</strong>" + html[i + len(mark):]
        end += len("<strong></strong>")
        print(f"ok   {k}: {re.sub(r'<[^>]+>', '', mark)[:50]}")
    strip = lambda s: re.sub(r"</?(strong|b)>", "", s)
    assert strip(html) == strip(src), "內部錯誤：除了 <strong>（與格子裡的 <b>）還動到別的"
    if bad:
        sys.exit(f"{bad} 條沒過，沒有寫檔")
    if "--write" in sys.argv:
        path.write_text(html, encoding="utf-8")
        print(f"寫入 {path}：加了 {len(marks)} 處")
    else:
        print("試跑通過；加 --write 寫檔")


if __name__ == "__main__":
    main()
