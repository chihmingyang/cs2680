"""List spots in a lecture's main text that may read better as a figure (a note, never a failure).

用法：python3 -I tools/find_figure_spots.py docs/l05.html [docs/l06.html ...]

印出兩種候選，只看核心觀念（#s-ideas）：
  ★數字表   至少 3 列、過半格子是數字的表，前後文有「形狀詞」（越來越、最划算、再往下……），
            也就是結論是趨勢、轉折或最佳點，不是數字本身。
  ★數字段落 至少 7 個數字、而且有形狀詞的段落或清單項；前後三個元素內已經有圖的不列（多半是在講那張圖）。
  表圖重複   一張數字表，後面三個元素內就有一張圖畫同一組數字（圖說寫「上表」，或過半數字相同）。
            讀者要讀兩次，留一個。

判斷規則（STYLE_ARTICLE 第 6 節〈數字表換成圖〉）：結論是一個形狀才改成圖，而且圖要取代表或段落，不是疊上去。
判斷過、決定留著的表或段落，在那個 <table> 或 <p>／<li> 加 data-no-figure，之後就不再列出。

為什麼：「每章至少一張圖或表」只管數量。一章已經有圖時，另一張數字表就沒有人再問它該不該是圖（L6 3.1，2026-11-06）。
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_pack import NUMERIC, Node, chapters, parse  # noqa: E402

NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
SHAPE = re.compile(r"越來越|最划算|划不來|最快|最省|最便宜|門檻|再往下|轉折|邊際|反而|占上風|遞減|翻倍|減半|停在|卡在")


def raw_text(n):
    """Text including <svg> labels (Node.text() skips svg)."""
    out = []
    for c in n.children:
        out.append(c if isinstance(c, str) else raw_text(c))
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def siblings_after(n, k):
    p = n.parent
    nodes = [c for c in p.children if isinstance(c, Node)]
    i = nodes.index(n)
    return nodes[i + 1:i + 1 + k]


def sibling_before(n):
    p = n.parent
    nodes = [c for c in p.children if isinstance(c, Node)]
    i = nodes.index(n)
    return nodes[i - 1] if i > 0 else None


def near_diagram(n, k=3):
    """A figure.diagram within k element siblings before or after n (the paragraph likely explains a chart)."""
    p = n.parent
    nodes = [c for c in p.children if isinstance(c, Node)]
    i = nodes.index(n)
    return any(x.tag == "figure" and "diagram" in x.cls() for x in nodes[max(0, i - k):i + 1 + k])


def inside(n, tags):
    p = n.parent
    while p is not None:
        if p.tag in tags:
            return True
        p = p.parent
    return False


def numbers(s):
    return {x.replace(",", "") for x in NUM.findall(s)}


def table_spots(ch, cid):
    out = []
    for t in ch.find_all(lambda x: x.tag == "table"):
        if "data-no-figure" in t.attrs:
            continue
        rows = [r for r in t.find_all(lambda x: x.tag == "tr")]
        body = [r for r in rows if not any(isinstance(c, Node) and c.tag == "th" for c in r.children)] or rows[1:]
        cells = [c.text() for r in body for c in [x for x in r.children if isinstance(x, Node) and x.tag in ("td", "th")][1:]]
        if len(body) < 3 or not cells:
            continue
        numeric = sum(1 for c in cells if c and NUMERIC.fullmatch(c))
        if numeric / len(cells) < 0.5:
            continue
        anchor = t.parent if "table-wrap" in t.parent.cls() else t
        heads = " | ".join(th.text() for th in t.find_all(lambda x: x.tag == "th"))[:60]
        after = siblings_after(anchor, 3)
        before = sibling_before(anchor)
        ctx = " ".join(a.text() for a in after[:2]) + (before.text() if before is not None else "")
        words = sorted(set(SHAPE.findall(ctx)))
        tnums = numbers(t.text()) - {str(i) for i in range(10)}
        for a in after:
            if a.tag == "figure" and "diagram" in a.cls():
                cap = next(a.find_all(lambda x: x.tag == "figcaption"), None)
                capt = cap.text() if cap is not None else ""
                same = tnums & numbers(raw_text(a))
                if "上表" in capt or (tnums and len(same) / len(tnums) >= 0.5):
                    out.append(f"  {cid} 表圖重複  {len(body)} 列：{heads}　圖說：{capt[:30]}")
                    words = []   # already charted: the question is which one to keep, not whether to chart
                break
        if words:
            out.append(f"  {cid} ★數字表  {len(body)} 列：{heads}　形狀詞：{'、'.join(words)}")
    return out


def para_spots(ch, cid):
    out = []
    for p in ch.find_all(lambda x: x.tag in ("p", "li")):
        if "data-no-figure" in p.attrs or inside(p, ("figure", "table", "nav")) or near_diagram(p):
            continue
        txt = p.text()
        nums = NUM.findall(txt)
        words = sorted(set(SHAPE.findall(txt)))
        if len(nums) >= 7 and words:
            out.append(f"  {cid} ★數字段落（{len(nums)} 個數字）：{txt[:40]}…　形狀詞：{'、'.join(words)}")
    return out


def main():
    paths = sys.argv[1:]
    if not paths:
        sys.exit(__doc__)
    total = 0
    for path in paths:
        root = parse(Path(path).read_text(encoding="utf-8"))
        lines = []
        for ch in chapters(root):
            cid = ch.attrs.get("id", "?")
            lines += table_spots(ch, cid) + para_spots(ch, cid)
        total += len(lines)
        if lines:
            print(f"== {Path(path).name}: {len(lines)}")
            print("\n".join(lines))
    if total == 0:
        print("no candidates")


if __name__ == "__main__":
    main()
