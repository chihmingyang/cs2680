#!/usr/bin/env python3
"""大綱：只看章名與小標。標題是 mind map 的節點（STYLE_ARTICLE 第 2 節〈標題是節點〉，2026-11-20 James：
「我想要光看標題就能腦中有 mind map 出來」）。

  python3 -I tools/outline.py l08                       # 印大綱：章名與小標，沒有內文
  python3 -I tools/outline.py lint l08                  # 標題的 lint，只提示（verify.sh 會跑）；all 是全站
  python3 -I tools/outline.py pack l08 > notes/outline/l08-pack.md
        # 只看標題的測試包：大綱＋題庫每一節抽幾題的題幹。給一個沒讀過內文的 agent，
        # 請它只憑標題把每一題指到一節，並列出單看看不懂的標題（WORKFLOW I3）。
        # 路徑可以是 docs/ 以外的檔案（例如 git show 出來的舊版），用來比改之前和改之後。
  python3 -I tools/outline.py score l08 answers.json    # 對答案：節命中率、章命中率、沒有一題指得到的節
  python3 -I tools/outline.py quiz-titles l08 [--write] # 題庫每一節的 title 對回頁面的標題（小測區塊的標題用它）

lXX 也可以寫成檔案路徑。大綱的取法和側欄一樣（assemble_v7.v7_secs）：h3 是章，章裡不在 <details> 內的
<p id="iN-M"><b>小標</b> 是節。

lint 抓的是機械看得出來的四種（都只 warn）：
  指代      標題裡有「它」「這兩」「上面」這類要靠上下文才懂的詞
  只有數量  「四個上限」「三種時機」「兩件事要記」：寫了幾個，沒列出是哪幾個（「兩個 model」這種泛指不算）
  重名      同一頁兩個標題一樣（mind map 上分不出來）
  前綴      「本文的判斷：」開頭：佔掉概念名的位置，標示改寫在內文
  只有主題  小標不到五個單位又沒有冒號（「成功率」「Hit rate」「怎麼查」），沒說講它的哪一面
概念名有沒有用業界的詞、單看懂不懂，機械判斷不了，靠 pack／score 的測試。
"""
import html
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUIZ = re.compile(r'<script type="application/json" id="quiz">(.*?)</script>', re.S)
PER_SECTION = 3   # pack 每一節抽幾題


def path_of(arg):
    p = Path(arg)
    return p if p.suffix == ".html" else ROOT / "docs" / f"{arg}.html"


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def strip_end(t):
    return t.rstrip("。：: ")


def outline(src):
    """[(chapter id, 章號或 None, 章名, [(節 id, 節號, 小標)])]. 章號 None 是查閱。"""
    ideas = src[src.index('id="s-ideas"'):src.index('id="wrap"')]
    out = []
    for part in re.split(r'(?=<div class="idea" id="i\d+">)', ideas)[1:]:
        iid = re.match(r'<div class="idea" id="(i\d+)">', part).group(1)
        m = re.search(r'<h3>(?:<span class="idea-no">(.*?)</span>)?(.*?)</h3>', part, re.S)
        no, title = (text(m.group(1)) if m.group(1) is not None else None), text(m.group(2))
        top = re.sub(r"<details\b.*?</details>", "", part, flags=re.S)
        subs = []
        if no:
            for sid, st in re.findall(r'<p id="(i\d+-\d+)"[^>]*>(?:<span class="anchor" id="[^"]+"></span>)*<b>(.*?)</b>', top, re.S):
                subs.append((sid, f'{no}.{sid.split("-")[1]}', strip_end(text(st))))
        out.append((iid, no, title, subs))
    return out


def page_title(src):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S)
    return text(m.group(1)) if m else ""


def show(src):
    lines = [page_title(src)]
    for iid, no, title, subs in outline(src):
        lines.append(f"{no} {title}" if no else title)
        lines += [f"    {n} {t}" for _, n, t in subs]
    return "\n".join(lines)


# ---------- lint ----------
POINTER = re.compile(r"它|這兩|這三|這幾|這些|這個|這條|這裡|那個|那些|上面|下面|前面的|上圖|下圖|上表|下表|上一節|下一節")
COUNT = re.compile(r"(?<![第同每另某])(?:(?:[三四五六七八九十]|[3-9]|\d{2,})\s*(?:個|種|條|項|類|件|層|招)(?!鐘)|[二兩2]\s*(?:種|條|項|類|件|層|招))")
PREFIX = re.compile(r"^本文的(判斷|推論|整理)")


def units(t):
    """標題有多長：一個中文字或一個英文詞算一個單位。"""
    return len(re.findall(r"[A-Za-z0-9_/÷×.+-]+|[^\sA-Za-z0-9_/÷×.+\-，。：:、（）()]", t))


def lint_page(src):
    """[(節號, 類別, 標題)]"""
    out, seen = [], {}
    for iid, no, title, subs in outline(src):
        nodes = [(no or "查閱", title, True)] + [(n, t, False) for _, n, t in subs]
        for n, t, is_ch in nodes:
            if not no and is_ch:
                continue  # 查閱的章名是目錄，不是觀念節點
            m = POINTER.search(t)
            if m:
                out.append((n, f"指代（{m.group(0)}）", t))
            m = COUNT.search(t)
            if m and not re.search(r"[、×]", t[m.end():]):
                out.append((n, f"只有數量（{m.group(0)}），沒列出是哪幾個", t))
            if PREFIX.search(t):
                out.append((n, "前綴（本文的判斷／推論：標示寫在內文）", t))
            if not is_ch and "：" not in t and ":" not in t and units(t) <= 4 and not re.search(r"[，,]", t):
                out.append((n, "只有主題，沒說講它的哪一面", t))
            key = re.sub(r"[\s。：:，,、（）()]", "", t).lower()
            if key in seen:
                out.append((n, f"重名（和 {seen[key]} 一樣）", t))
            else:
                seen[key] = n
    return out


def lint(args):
    pages = ([p for p in sorted((ROOT / "docs").glob("l[0-9][0-9]*.html")) if re.fullmatch(r"l\d\d[a-z]?", p.stem)]
             if args == ["all"] else [path_of(a) for a in args])
    total = 0
    for p in pages:
        src = p.read_text(encoding="utf-8")
        if 'id="s-ideas"' not in src:
            continue
        for n, kind, t in lint_page(src):
            total += 1
            print(f"warn {p.stem} {n} {kind}：{t}")
    print("OK" if not total else f"{total} 個標題要看（STYLE_ARTICLE 第 2 節〈標題是節點〉；只提示）")
    return 0


# ---------- 題庫的節 ↔ 大綱的節 ----------
def quiz_of(src):
    m = QUIZ.search(src)
    return json.loads(m.group(1)) if m else None


def node_of(q, src):
    """題庫的節 id → (節號, 章號)。from 是章 id（章首併進第一個小節）時，對到那一章的第一個小標；
    那個小標另有自己的題庫節、或那一章沒有小標，就對到章。"""
    ol = outline(src)
    froms = {s["from"] for s in q["sections"]}
    by = {}
    for iid, no, title, subs in ol:
        by[iid] = (no or "查閱", no or "查閱", title)
        for sid, n, t in subs:
            by[sid] = (n, no, t)
    out = {}
    for s in q["sections"]:
        f = s["from"]
        if "-" not in f:
            first = next((subs[0] for iid, no, title, subs in ol if iid == f and subs), None)
            if first and first[0] not in froms:
                f = first[0]
        if f in by:
            out[s["id"]] = by[f]
    return out


def pack(arg):
    src = path_of(arg).read_text(encoding="utf-8")
    q = quiz_of(src)
    if q is None:
        sys.exit(f"{arg} 沒有題庫，pack 需要題庫的題幹；只看大綱用 outline.py {arg}")
    nodes = node_of(q, src)
    picked = []
    for s in q["sections"]:
        if s["id"] not in nodes or nodes[s["id"]][0] == "查閱":
            continue
        mine = [u for u in q["unit"] if u["ks"] == s["id"]]
        random.Random(s["id"]).shuffle(mine)
        picked += mine[:PER_SECTION]
    random.Random(len(picked)).shuffle(picked)
    print("# 只看標題的測試\n")
    print("下面是一堂課的大綱：只有章名和小標，沒有內文。你沒有讀過這堂課。請只憑這份大綱做兩件事，不要去讀任何檔案。\n")
    print("1. 每一題：這一題的答案最可能寫在哪一節？填節號（例如 3.4）。那一章沒有小標就填章號。"
          "只能憑標題判斷；兩節都像就選比較像的那一個。")
    print("2. 列出單看看不懂的標題：看了標題說不出這一節在講什麼概念的，寫出節號和原因（一句）。"
          "常見的原因：要靠上下文才懂的詞、沒看過的自創說法、只有結論沒有主題、和別的標題分不出來。\n")
    print('把結果寫成一個 JSON 檔：{"answers": {"k1a": "1.1", …}, "unclear": [{"node": "3.3", "why": "…"}, …]}\n')
    print("## 大綱\n")
    print(show(src))
    print("\n## 題目\n")
    for u in picked:
        print(f"- {u['id']}：{u['q']}")
    return 0


def score(arg, ans_path):
    src = path_of(arg).read_text(encoding="utf-8")
    q = quiz_of(src)
    nodes = node_of(q, src)
    a = json.loads(Path(ans_path).read_text(encoding="utf-8"))
    ans = a.get("answers", a)
    ks = {u["id"]: u["ks"] for u in q["unit"]}
    per, hit, hit_ch, n = {}, 0, 0, 0
    for uid, got in ans.items():
        if uid not in ks or ks[uid] not in nodes:
            continue
        want, ch, title = nodes[ks[uid]]
        got = str(got).strip()
        ok = got == want
        ok_ch = got.split(".")[0] == str(ch)
        n += 1
        hit += ok
        hit_ch += ok_ch
        d = per.setdefault(want, {"t": title, "n": 0, "ok": 0, "to": []})
        d["n"] += 1
        d["ok"] += ok
        if not ok:
            d["to"].append(got)
    if not n:
        sys.exit("answers 裡沒有題庫的題號")
    print(f"節命中 {hit}/{n}（{hit * 100 // n}%）　章命中 {hit_ch}/{n}（{hit_ch * 100 // n}%）")
    zero = [(k, d) for k, d in per.items() if d["ok"] == 0]
    part = [(k, d) for k, d in per.items() if 0 < d["ok"] < d["n"]]
    if zero:
        print("\n沒有一題指得到的節（標題先看這些）：")
        for k, d in zero:
            print(f"  {k} {d['t']}　0/{d['n']}　被指到 {'、'.join(d['to'])}")
    if part:
        print("\n部分指得到：")
        for k, d in part:
            print(f"  {k} {d['t']}　{d['ok']}/{d['n']}　指錯到 {'、'.join(d['to'])}")
    unclear = a.get("unclear", []) if isinstance(a, dict) else []
    if unclear:
        print(f"\n單看看不懂的標題（{len(unclear)} 個）：")
        for x in unclear:
            print(f"  {x.get('node')}　{x.get('why')}")
    return 0


def quiz_titles(arg, write):
    p = path_of(arg)
    src = p.read_text(encoding="utf-8")
    q = quiz_of(src)
    if q is None:
        print("ok 沒有題庫")
        return 0
    nodes = node_of(q, src)
    diff = [(s, nodes[s["id"]][2]) for s in q["sections"]
            if s["id"] in nodes and strip_end(s["title"]) != strip_end(nodes[s["id"]][2])]
    for s, want in diff:
        print(f"{'改' if write else 'warn'} {s['id']} #{s['from']}：{s['title']} → {strip_end(want)}")
        if write:
            s["title"] = strip_end(want)
    if write and diff:
        body = json.dumps(q, ensure_ascii=False, indent=1)
        p.write_text(QUIZ.sub(lambda m: f'<script type="application/json" id="quiz">\n{body}\n</script>', src, count=1),
                     encoding="utf-8")
    print("ok 題庫的節名和頁面一樣" if not diff else f"{len(diff)} 個節名{'已改' if write else '和頁面的標題不一樣：加 --write 寫回'}")
    return 0


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == "lint" and len(argv) >= 3:
        return lint(argv[2:])
    if cmd == "pack" and len(argv) == 3:
        return pack(argv[2])
    if cmd == "score" and len(argv) == 4:
        return score(argv[2], argv[3])
    if cmd == "quiz-titles" and len(argv) >= 3:
        return quiz_titles(argv[2], "--write" in argv[3:])
    if len(argv) == 2:
        print(show(path_of(cmd).read_text(encoding="utf-8")))
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
