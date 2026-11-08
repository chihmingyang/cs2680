#!/usr/bin/env python3
"""題庫（knowledge section 小測與整合題）：檢查、出卷、對定位、彙整。設計見 guide/QUIZ.md。

題庫放在頁面裡：<script type="application/json" id="quiz">…</script>（在 </main> 之後）。
app.js 讀它，在每一節後面放小測、在範圍最後一章後面放整合題。審查包與 page_text 都會去掉 <script>，
所以作答的 agent 看不到答案。

  python3 -I tools/quiz.py check docs/l06.html              # 題庫和頁面對得上嗎（verify.sh 會跑）
  python3 -I tools/quiz.py units docs/l06.html              # 每個單位屬於哪一節（除錯用）
  python3 -I tools/quiz.py exam docs/l06.html [k14b …] > exam.md   # 作答包：讀者文字＋題目，不含答案；列題號就只出那幾題
  python3 -I tools/quiz.py grade docs/l06.html answers.json [k1b k14b …] > judge.md
        # 對定位（程式判斷），並產出評分包給評分的 agent；後面列題號就只評那幾題（改了 key 之後重評）
  python3 -I tools/quiz.py report docs/l06.html answers.json verdicts.json [更多 answers verdicts 對]
        # 彙整：每題過不過、每一節的結果；給兩組以上就比較各次是否一致

作答的 answers.json：{"k1a": {"choice": "C", "cite": ["#i1 ¶1"]}, "k1b": {"answer": "…", "cite": [...]}, …}
評分的 verdicts.json：{"k1b": {"points": [1, 0], "why": "…"}, …}（只有問答題；points 對應題目的 key，1 是答到且引用的文字支持）

一題「過」＝內容對＋定位對（程式判斷：unit 題至少有一個定位落在它那一節；整合題在它列的每一節各至少一個定位）。
內容對：選擇題（kind choice）由程式比對選項；問答題（apply 與整合題）由評分 agent 逐要點判斷。
作答包裡的選擇題，最後都多一個「文章沒寫，答不出來」：文章不夠時要選它，刪掉內容後題目才會轉紅。
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_pack import Node, by_id, parse, tldr_of, units_of  # noqa: E402

SENT = re.compile(r"⟦(k\d+)⟧")
KINDS = {"recall": "回想", "apply": "應用", "choice": "選擇"}
NOT_IN_TEXT = "文章沒寫，答不出來"
LETTERS = "ABCDEFGH"


def load(path):
    src = Path(path).read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="quiz">(.*?)</script>', src, re.S)
    if not m:
        return src, None
    return src, json.loads(m.group(1))


def chapter_of(root, el):
    n = el
    while n is not None and not (n.tag == "div" and "idea" in n.cls()):
        n = n.parent
    return n


def check(path):
    src, q = load(path)
    if q is None:
        print(f"{path}: 沒有題庫，跳過")
        return 0
    root = parse(src)
    errs = []
    scope = q.get("scope") or []
    order = {}
    for i, cid in enumerate(scope):
        if by_id(root, cid) is None:
            errs.append(f"scope 的 #{cid} 在頁面上找不到")
    ids = [s["id"] for s in q["sections"]]
    if len(set(ids)) != len(ids):
        errs.append("sections 的 id 重複")
    # document order of every element with an id
    pos = {}
    for k, m in enumerate(re.finditer(r'\sid="([^"]+)"', src)):
        pos.setdefault(m.group(1), k)
    last = -1
    for s in q["sections"]:
        el = by_id(root, s["from"])
        if el is None:
            errs.append(f'{s["id"]}：起點 #{s["from"]} 在頁面上找不到（小節改名或刪了？）')
            continue
        ch = chapter_of(root, el)
        if ch is None or ch.attrs.get("id") not in scope:
            errs.append(f'{s["id"]}：起點 #{s["from"]} 不在 scope 的章裡')
        if pos[s["from"]] <= last:
            errs.append(f'{s["id"]}：起點 #{s["from"]} 的順序和頁面不一致')
        last = pos[s["from"]]
        order[s["id"]] = s
    first = q["sections"][0]["from"] if q["sections"] else None
    if scope and first != scope[0]:
        errs.append(f"第一節要從 scope 的第一章 #{scope[0]} 開始")
    starts = {s["from"] for s in q["sections"]}
    for cid in scope:
        if cid not in starts:
            errs.append(f"#{cid} 的開頭不屬於任何一節：sections 要有一節從 #{cid} 開始")
    qids = []
    used = set()
    for u in q["unit"]:
        qids.append(u["id"])
        if u["ks"] not in order:
            errs.append(f'{u["id"]}：節 {u["ks"]} 不存在')
        used.add(u["ks"])
        if u.get("kind") not in KINDS:
            errs.append(f'{u["id"]}：kind 要是 {"／".join(KINDS)}')
        if not u.get("q") or not u.get("key"):
            errs.append(f'{u["id"]}：缺題目或答案要點')
        if u.get("kind") == "choice":
            cs = u.get("choices") or []
            if not 3 <= len(cs) <= 4:
                errs.append(f'{u["id"]}：選擇題要 3 個選項；有 3 種真的誤解才用 4 個（QUIZ.md）')
            if sum(bool(c.get("ok")) for c in cs) != 1:
                errs.append(f'{u["id"]}：選擇題要剛好一個正確選項')
            for c in cs:
                if not c.get("t") or (not c.get("ok") and not c.get("why")):
                    errs.append(f'{u["id"]}：每個選項要有文字，錯的選項要寫 why（錯在哪）')
                    break
    for x in q.get("integration", []):
        qids.append(x["id"])
        if len(x["ks"]) < 2:
            errs.append(f'{x["id"]}：整合題至少要用到兩節')
        for k in x["ks"]:
            if k not in order:
                errs.append(f'{x["id"]}：節 {k} 不存在')
        if not x.get("q") or not x.get("key"):
            errs.append(f'{x["id"]}：缺題目或答案要點')
    if len(set(qids)) != len(qids):
        errs.append("題目 id 重複")
    for s in q["sections"]:
        if s["id"] not in used:
            errs.append(f'{s["id"]}（{s["title"]}）沒有 unit 題')
        if s.get("core"):
            mine = [u for u in q["unit"] if u["ks"] == s["id"]]
            nc = sum(u.get("kind") == "choice" for u in mine)
            na = sum(u.get("kind") == "apply" for u in mine)
            if nc < 3 or na < 1:
                errs.append(f'{s["id"]}（{s["title"]}）是重點觀念：要至少 3 題選擇、1 題應用（現在 {nc}、{na}）')
    for e in errs:
        print("FAIL", e)
    if not errs:
        print(f'ok   題庫：{len(q["sections"])} 節、{len(q["unit"])} 題 unit、{len(q.get("integration", []))} 題整合')
    return 1 if errs else 0


def unit_map(src, q):
    """[(locator, text, ks)] for the tldr (ks None) and every unit of the scope chapters."""
    root = parse(src)
    for s in q["sections"]:
        el = by_id(root, s["from"])
        if el is not None and not (el.tag == "div" and "idea" in el.cls()):
            el.children.insert(0, f"⟦{s['id']}⟧")
    starts = {s["from"]: s["id"] for s in q["sections"]}
    out = []
    t = tldr_of(root)
    if t is not None:
        out += [(lc, tx, None) for lc, tx in units_of(t, "#tldr")]
    cur = None
    for cid in q["scope"]:
        ch = by_id(root, cid)
        cur = starts.get(cid, cur)
        for lc, tx in units_of(ch, f"#{cid}"):
            m = SENT.search(tx)
            if m:
                cur = m.group(1)
                tx = SENT.sub("", tx).strip()
            out.append((lc, tx, cur))
    return out


def norm_cite(c):
    c = c.strip().strip("[]【】").strip()
    c = re.sub(r"\s*‹[^›]*›\s*$", lambda m: " " + m.group(0).strip(), c)
    c = re.sub(r"\s+", " ", c)
    if c and not c.startswith("#"):
        c = "#" + c
    return c


def resolve(cite, units):
    c = norm_cite(cite)
    hit = [u for u in units if u[0] == c]
    if not hit:
        hit = [u for u in units if u[0].startswith(c + " ")]
    return hit


def exam(path, only=()):
    src, q = load(path)
    units = unit_map(src, q)
    titles = {}
    root = parse(src)
    for cid in q["scope"]:
        h = next(by_id(root, cid).find_all(lambda x: x.tag == "h3"), None)
        titles[cid] = h.text() if h is not None else cid
    items = [x for x in q["unit"] + q.get("integration", []) if not only or x["id"] in only]
    print(f"# 作答包：{Path(path).name}　{len(items)} 題")
    print("""
你是讀者，只讀過下面這份文字。依序回答最後的每一題。

規則：
1. 只用這份文字寫的東西作答。你自己知道、文字沒寫的不算；文字不夠回答，就寫「文章沒寫」，說缺了什麼，不要猜。
2. 每一題附「定位」：支持你答案每個要點的單位，寫法和每行開頭方括號裡的一樣，例如 #i2 ¶1、#i2 表1 列2、#i2 code1 內容、#i2 表2 列1 ‹換成›。要計算的題，附上算式的出處。
3. 選擇題選一個字母。文字裡找不到能支持某個選項的內容，就選「文章沒寫，答不出來」，即使你自己知道答案。
4. 問答題的答案寫成完整的句子，數字寫出來。
5. 輸出一個 JSON 物件，不要其他文字：選擇題 {"k1a": {"choice": "C", "cite": ["#i1 ¶1"]}}，問答題 {"k1b": {"answer": "…", "cite": ["…"]}}，每一題一個 key。
""")
    print("## 文字\n")
    group = None
    for lc, tx, ks in units:
        g = lc.split(" ")[0]
        if g != group:
            group = g
            name = "先看這裡" if g == "#tldr" else titles.get(g[1:], g)
            print(f"\n### {g}　{name}")
        print(f"[{lc}] {tx}")
    print("\n## 題目\n")
    for x in items:
        print(f"- {x['id']}：{'（選擇題）' if x.get('kind') == 'choice' else ''}{x['q']}")
        if x.get("kind") == "choice":
            for i, c in enumerate(x["choices"] + [{"t": NOT_IN_TEXT}]):
                print(f"    {LETTERS[i]}. {c['t']}")
    return 0


def locate(q, units, answers):
    """Program half of grading: does each answer cite its own section(s)?"""
    res = {}
    allq = [(u["id"], [u["ks"]], u) for u in q["unit"]] + [(x["id"], x["ks"], x) for x in q.get("integration", [])]
    for qid, need, item in allq:
        a = answers.get(qid) or {}
        cites = a.get("cite") or []
        got, missing, texts = set(), [], []
        for c in cites:
            hit = resolve(c, units)
            if not hit:
                missing.append(c)
            for lc, tx, ks in hit:
                if ks:
                    got.add(ks)
                texts.append((lc, tx, ks))
        lack = [k for k in need if k not in got]
        res[qid] = {"need": need, "got": sorted(got, key=lambda k: int(k[1:])), "lack": lack,
                    "bad_cites": missing, "ok": bool(cites) and not lack, "texts": texts,
                    "answer": a.get("answer", ""), "item": item}
    return res


def grade(path, answers_path, only=()):
    src, q = load(path)
    units = unit_map(src, q)
    answers = json.loads(Path(answers_path).read_text(encoding="utf-8"))
    loc = locate(q, units, answers)
    names = {s["id"]: s["title"] for s in q["sections"]}
    print(f"# 評分包：{Path(path).name}　{len(loc)} 題")
    print("""
你是評分者。每一題有：題目、答案要點（key）、作答者的答案、作答者引用的文字。
對每個要點判斷：作答者的答案有沒有答到它（意思對就算，不必同字；數字要對，四捨五入可以），
而且作答者引用的文字裡有寫到支持它的內容（引用的文字裡有算式、作答者照算式算出來，也算支持）。兩個都成立記 1，否則記 0。
不要用你自己的知識補作答者沒寫的東西；引用的文字沒寫、答案卻寫了的要點，記 0，並在 why 裡說明。
只輸出一個 JSON 物件，不要其他文字：{"k1a": {"points": [1, 0], "why": "一句話：哪個要點沒答到或沒有出處"}, …}
""")
    for qid, r in loc.items():
        if only and qid not in only:
            continue
        it = r["item"]
        if it.get("kind") == "choice":
            continue  # 選擇題由程式判，不進評分包
        kind = "整合" if qid.startswith("x") else KINDS.get(it.get("kind"), "")
        print(f"\n## {qid}（{kind}；節：{'、'.join(names[k] for k in r['need'])}）")
        print(f"題目：{it['q']}")
        print("答案要點：")
        for i, k in enumerate(it["key"], 1):
            print(f"  {i}. {k}")
        print(f"作答：{r['answer'] or '（沒有作答）'}")
        print("引用的文字：")
        if not r["texts"]:
            print("  （沒有引用，或引用的定位不存在）")
        for lc, tx, ks in r["texts"]:
            print(f"  [{lc}] {tx}")
    Path(answers_path).with_suffix(".loc.json").write_text(json.dumps(
        {k: {kk: v[kk] for kk in ("need", "got", "lack", "bad_cites", "ok")} for k, v in loc.items()},
        ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


def report(path, pairs):
    src, q = load(path)
    units = unit_map(src, q)
    names = {s["id"]: s["title"] for s in q["sections"]}
    items = [(u["id"], [u["ks"]], u) for u in q["unit"]] + [(x["id"], x["ks"], x) for x in q.get("integration", [])]
    asked = set()
    for a, _ in pairs:
        asked |= set(json.loads(Path(a).read_text(encoding="utf-8")))
    items = [x for x in items if x[0] in asked]  # 只出了部分題目（exam 指定題號）時，沒出的題不算
    runs = []
    for a, v in pairs:
        answers = json.loads(Path(a).read_text(encoding="utf-8"))
        verdicts = json.loads(Path(v).read_text(encoding="utf-8"))
        loc = locate(q, units, answers)
        r = {}
        for qid, need, it in items:
            if it.get("kind") == "choice":
                right = LETTERS[next(i for i, c in enumerate(it["choices"]) if c.get("ok"))]
                got = str((answers.get(qid) or {}).get("choice", "")).strip().upper()[:1]
                none = LETTERS[len(it["choices"])]
                content = got == right
                why = "" if content else ("選了「文章沒寫」" if got == none else f"選 {got or '?'}，正確是 {right}")
                r[qid] = {"pass": content and loc[qid]["ok"], "content": content, "loc": loc[qid]["ok"],
                          "pts": f"選{got or '?'}", "lack": loc[qid]["lack"], "why": why}
                continue
            pts = (verdicts.get(qid) or {}).get("points") or []
            content = len(pts) == len(it["key"]) and all(pts)
            r[qid] = {"pass": content and loc[qid]["ok"], "content": content, "loc": loc[qid]["ok"],
                      "pts": "".join("✓" if p else "✗" for p in pts) or "?",
                      "lack": loc[qid]["lack"], "why": (verdicts.get(qid) or {}).get("why", "")}
        runs.append((Path(a).stem, r))
    hdr = " | ".join(n for n, _ in runs)
    print(f"| 題 | 節 | {hdr} |\n|---|---|" + "---|" * len(runs))
    for qid, need, it in items:
        cells = []
        for _, r in runs:
            x = r[qid]
            mark = "過" if x["pass"] else "**不過**"
            extra = x["pts"] + ("" if x["loc"] else f" 定位缺 {'、'.join(x['lack'])}")
            cells.append(f"{mark} {extra}")
        print(f"| {qid} | {'＋'.join(need)} | " + " | ".join(cells) + " |")
    print()
    for n, r in runs:
        u = [k for k in r if not k.startswith("x")]
        x = [k for k in r if k.startswith("x")]
        print(f"- {n}：unit {sum(r[k]['pass'] for k in u)}/{len(u)} 過，整合 {sum(r[k]['pass'] for k in x)}/{len(x)} 過")
    if len(runs) > 1:
        flaky = [qid for qid, _, _ in items if len({r[qid]["pass"] for _, r in runs}) > 1]
        print(f"- 各次結果不一致的題：{'、'.join(flaky) if flaky else '沒有'}")
    print("\n沒過的原因：")
    for n, r in runs:
        for qid, need, _ in items:
            if not r[qid]["pass"]:
                why = r[qid]["why"] or ("定位沒落在 " + "、".join(names[k] for k in r[qid]["lack"]))
                print(f"- {n} {qid}：{why}")
    return 0


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    cmd, path = argv[1], argv[2]
    if cmd == "check":
        return check(path)
    src, q = load(path)
    if q is None:
        sys.exit(f"{path} 沒有題庫")
    if cmd == "units":
        for lc, tx, ks in unit_map(src, q):
            print(f"{ks or '-':4} [{lc}] {tx[:50]}")
        return 0
    if cmd == "exam":
        return exam(path, set(argv[3:]))
    if cmd == "grade" and len(argv) >= 4:
        return grade(path, argv[3], set(argv[4:]))
    if cmd == "report" and len(argv) >= 5 and len(argv) % 2 == 1:
        return report(path, list(zip(argv[3::2], argv[4::2])))
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
