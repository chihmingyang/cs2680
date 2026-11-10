#!/usr/bin/env python3
"""題庫（knowledge section 小測與整合題）：檢查、出卷、對定位、彙整。設計見 guide/QUIZ.md。

題庫放在頁面裡：<script type="application/json" id="quiz">…</script>（在 </main> 之後）。
app.js 讀它，在每一節後面放小測、在範圍最後一章後面放整合題。審查包與 page_text 都會去掉 <script>，
所以作答的 agent 看不到答案。

  python3 -I tools/quiz.py init docs/l07.html               # 新題庫：從頁面的小節產生節的骨架，寫進頁面（已有題庫就不動）
  python3 -I tools/quiz.py spec docs/l07.html [i1 i2 …] > spec.md   # 給列觀念的 agent：讀者文字依節分組，不含 tldr 與題目
  python3 -I tools/quiz.py merge docs/l07.html part.json …  # 把 subagent 寫的 points／unit／integration 併進頁面的題庫
  python3 -I tools/quiz.py check docs/l06.html              # 題庫和頁面對得上嗎（verify.sh 會跑）
  python3 -I tools/quiz.py units docs/l06.html              # 每個單位屬於哪一節（除錯用）
  python3 -I tools/quiz.py exam docs/l06.html [k14b …] > exam.md   # 作答包：讀者文字＋題目，不含答案；列題號就只出那幾題
        # exam、closed、grade 後面列的可以是題號（k14b）、節（k14：那一節的題）或章（i3：那一章的題、放在那一章後的整合題）
  python3 -I tools/quiz.py coverage docs/l06.html          # 每一節的觀念（points）各被哪幾題測到；沒測到的標出來
  python3 -I tools/quiz.py closed docs/l06.html > closed.md   # 閉卷：只有選擇題、不給文章；閉卷也答對的題沒在測文章
  python3 -I tools/quiz.py closedcheck docs/l06.html closed.json   # 列出閉卷答對而且有把握的題
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
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_pack import Node, by_id, parse, tldr_of, units_of  # noqa: E402

SENT = re.compile(r"⟦(k\d+)⟧")
KINDS = {"recall": "回想", "apply": "應用", "choice": "選擇"}
NOT_IN_TEXT = "文章沒寫，答不出來"
NUM_ONLY = re.compile(r"^\s*(?:約|大約|不到|超過|將近)?\s*[\d.,]+\s*(?:%|％|倍|步|次|個|題|成|分|秒|分鐘|小時|美元|token)?\s*(?:左右|以上|以下)?\s*$")
LETTERS = "ABCDEFGH"


def shown(u):
    """Choices in the order the exam packets show them: shuffled with the question id as seed,
    like the page shuffles them, so the bank's order (where writers tend to put the key) leaks nothing.
    Same id → same order, so grading can map letters back."""
    cs = list(u["choices"])
    random.Random(u["id"]).shuffle(cs)
    return cs


def key_letter(u):
    return LETTERS[next(i for i, c in enumerate(shown(u)) if c.get("ok"))]


def load(path):
    src = Path(path).read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="quiz">(.*?)</script>', src, re.S)
    if not m:
        return src, None
    return src, json.loads(m.group(1))


def picker(q, only):
    """Select questions by question id (k14b), section id (k14) or chapter id (i3)."""
    if not only:
        return lambda x: True
    ch = {s_["id"]: s_["from"].split("-")[0] for s_ in q["sections"]}
    last = q["scope"][-1] if q.get("scope") else None

    def ok(x):
        if x["id"] in only:
            return True
        ks = x["ks"] if isinstance(x["ks"], list) else [x["ks"]]
        if any(k in only for k in ks):
            return True
        if isinstance(x["ks"], str):
            return ch.get(x["ks"]) in only
        return x.get("after", last) in only
    return ok


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
    chap_of = {s["id"]: s["from"].split("-")[0] for s in q["sections"]}
    for x in q.get("integration", []):
        qids.append(x["id"])
        at = x.get("after", scope[-1] if scope else None)
        if at not in scope:
            errs.append(f'{x["id"]}：after 的 #{at} 不在 scope 裡')
        elif any(k in chap_of and scope.index(chap_of[k]) > scope.index(at) for k in x["ks"]):
            errs.append(f'{x["id"]}：用到的節在 #{at} 之後，讀者做這題時還沒讀到')
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
            if nc + na < 4 or na < 1 or nc < 2:
                errs.append(f'{s["id"]}（{s["title"]}）是重點觀念：至少 4 題，其中至少 2 題選擇、1 題應用（現在選擇 {nc}、應用 {na}）')
    # 正確選項最長、而且比錯的選項平均長 25% 以上：閉卷挑最長的就會對（QUIZ.md）。只警告，不擋。
    long = []
    for u in q["unit"]:
        if u.get("kind") != "choice" or not u.get("choices"):
            continue
        right = next((len(c["t"]) for c in u["choices"] if c.get("ok")), 0)
        wrong = [len(c["t"]) for c in u["choices"] if not c.get("ok")]
        if wrong and right > max(wrong) and right > 1.25 * sum(wrong) / len(wrong):
            long.append(u["id"])
    if long:
        print(f"warn 正確選項明顯最長 {len(long)} 題：{' '.join(long)}")
    # 觀念涵蓋（coverage）：每一節的 points 是 spec，每題的 covers 標它測哪個觀念。
    # 有 points 的節，每個觀念都要有一題 unit 測到（選擇或應用），covers 只能指向自己這一節的觀念。
    # evidence（2026-11-11）：量測的精確值、benchmark 怎麼設計、出處與證據力。讀者不必記，所以不強制出題；
    # 它的數字由 check_numbers.py 對照來源檔和正文。
    pts = {pt["id"]: s_["id"] for s_ in q["sections"] for pt in s_.get("points", [])}
    evid = {pt["id"] for s_ in q["sections"] for pt in s_.get("points", []) if pt.get("type") == "evidence"}
    TYPES = {"claim", "mechanism", "condition", "limit", "misconception", "evidence"}
    for s_ in q["sections"]:
        for pt in s_.get("points", []):
            if pt.get("type") not in TYPES:
                errs.append(f'{pt["id"]}：type 要是 {"／".join(sorted(TYPES))}')
    covered = set()
    for u in q["unit"]:
        for c in u.get("covers", []):
            if c not in pts:
                errs.append(f'{u["id"]}：covers 的 {c} 不存在')
            elif pts[c] != u["ks"]:
                errs.append(f'{u["id"]}：covers 的 {c} 屬於 {pts[c]}，不是這題的節 {u["ks"]}')
            covered.add(c)
    missing = [pid for pid in pts if pid not in covered and pid not in evid]
    for pid in missing:
        errs.append(f'觀念 {pid} 沒有題目測到')
    # 一題只測 evidence，就是在考數字或出處（QUIZ.md〈讀者自測優先〉）
    for u in q["unit"]:
        cv = u.get("covers", [])
        if cv and all(c in evid for c in cv):
            errs.append(f'{u["id"]}：covers 只有 evidence 類的觀念；這類不出題，題目要測它支持的那個觀念')
    # 選項只有數字的選擇題：答案就是一個數字，多半在考記憶。只警告：每個錯的數字各對應一種算錯的方式時可以留，
    # 在題目加 "num_choices_ok": "理由"。
    numonly = [u["id"] for u in q["unit"] if u.get("kind") == "choice" and u.get("choices") and not u.get("num_choices_ok")
               and all(NUM_ONLY.match(c.get("t", "")) for c in u["choices"])]
    if numonly:
        print(f"warn 選項只有數字 {len(numonly)} 題：{' '.join(numonly)}（改成問這個數字代表什麼；錯的數字各對應一種算錯的方式才留，加 num_choices_ok）")
    for e in errs:
        print("FAIL", e)
    if pts and not errs:
        print(f"ok   涵蓋：{len(pts) - len(evid)} 個觀念都有題目測到" + (f"；另有 {len(evid)} 條 evidence 不出題" if evid else ""))
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
    sel = picker(q, only)
    items = [x for x in q["unit"] + q.get("integration", []) if sel(x)]
    print(f"# 作答包：{Path(path).name}　{len(items)} 題")
    print("""
你是讀者，只讀過下面這份文字。依序回答最後的每一題。

規則：
1. 只用這份文字寫的東西作答。你自己知道、文字沒寫的不算；文字不夠回答，就寫「文章沒寫」，說缺了什麼，不要猜。
2. 每一題附「定位」：支持你答案每個要點的單位，寫法和每行開頭方括號裡的一樣，例如 #i2 ¶1、#i2 表1 列2、#i2 code1 內容、#i2 表2 列1 ‹換成›。要計算的題，附上算式的出處。
3. 選擇題選一個字母。文字裡找不到能支持某個選項的內容，就選「文章沒寫，答不出來」，即使你自己知道答案。
4. 問答題的答案寫成完整的句子，數字寫出來。
5. 覺得題目本身有問題（兩個選項都對、選項說得比文章多、題目要的文章沒寫、題目分不出懂不懂），照樣作答，另外寫在 "_issues"，一題一句。
6. 輸出一個 JSON 物件，不要其他文字：選擇題 {"k1a": {"choice": "C", "cite": ["#i1 ¶1"]}}，問答題 {"k1b": {"answer": "…", "cite": ["…"]}}，每一題一個 key；另加 "_issues": {"k23d": "…"}（沒有就給空物件）。
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
            for i, c in enumerate(shown(x) + [{"t": NOT_IN_TEXT}]):
                print(f"    {LETTERS[i]}. {c['t']}")
    return 0


def coverage(path):
    src, q = load(path)
    by = {}
    for u in q["unit"]:
        for c in u.get("covers", []):
            by.setdefault(c, []).append(u["id"])
    TYPE = {"claim": "主張", "mechanism": "機制", "condition": "前提", "limit": "限制", "misconception": "誤解", "evidence": "證據"}
    tot = cov = ev = 0
    for s_ in q["sections"]:
        if not s_.get("points"):
            continue
        print(f"\n## {s_['id']} {s_['title']}")
        for pt in s_["points"]:
            qs = by.get(pt["id"], [])
            if pt.get("type") == "evidence":
                ev += 1
                print(f"- {pt['id']} [證據] {'、'.join(qs) if qs else '不出題'}｜{pt['t']}")
                continue
            tot += 1
            cov += bool(qs)
            print(f"- {pt['id']} [{TYPE.get(pt['type'], pt['type'])}] {'、'.join(qs) if qs else '**沒有題目**'}｜{pt['t']}")
    print(f"\n涵蓋 {cov}/{tot}" + (f"（另有 {ev} 條 evidence 不出題）" if ev else ""))
    return 0


def closed(path, only=()):
    """Closed-book exam: the choice questions only, no article. A question answered right
    with confidence here does not measure reading (passage independence)."""
    src, q = load(path)
    sel = picker(q, only)
    items = [u for u in q["unit"] if u.get("kind") == "choice" and sel(u)]
    print(f"# 閉卷作答包：{Path(path).name}　{len(items)} 題選擇題，沒有文章")
    print("""
你沒有讀過這些題目出自的文章。只用常識、推理和你本來就知道的東西，每一題都選一個最可能的答案（一定要選，不能不答）。
每一題另外標 sure：true 表示你不靠文章也有把握（例如選項之間的因果或定義就能推出答案），false 表示主要是猜的。
再用一句話寫你怎麼判斷的。
只輸出一個 JSON 物件，不要其他文字：{"k1a": {"choice": "C", "sure": true, "why": "…"}, …}，每一題一個 key。
""")
    for u in items:
        print(f"- {u['id']}：{u['q']}")
        for i, c in enumerate(shown(u)):
            print(f"    {LETTERS[i]}. {c['t']}")
    return 0


def closedcheck(path, ans_path):
    src, q = load(path)
    ans = json.loads(Path(ans_path).read_text(encoding="utf-8"))
    items = [u for u in q["unit"] if u.get("kind") == "choice" and u["id"] in ans]
    right = sure = 0
    flagged = []
    for u in items:
        a = ans.get(u["id"]) or {}
        ok = str(a.get("choice", "")).strip().upper()[:1] == key_letter(u)
        right += ok
        if ok and a.get("sure"):
            sure += 1
            flagged.append((u["id"], a.get("why", ""), u.get("closed_ok")))
    print(f"閉卷：{len(items)} 題選擇題，答對 {right}（純猜的期望值約 {sum(1 / len(u['choices']) for u in items):.0f}），答對而且有把握 {sure}")
    bad = [f for f in flagged if not f[2]]
    print(f"要改的（沒標 closed_ok）：{len(bad)}")
    for qid, why, _ in bad:
        print(f"- {qid}：{why}")
    ok_ = [f for f in flagged if f[2]]
    if ok_:
        print(f"已接受（closed_ok）：{len(ok_)}")
        for qid, _, reason in ok_:
            print(f"- {qid}：{reason}")
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
    sel = picker(q, only)
    n = sum(1 for k, r in loc.items() if sel(r["item"]) and r["item"].get("kind") != "choice")
    print(f"# 評分包：{Path(path).name}　{n} 題")
    print("""
你是評分者。每一題有：題目、答案要點（key）、作答者的答案、作答者引用的文字。
對每個要點判斷：作答者的答案有沒有答到它（意思對就算，不必同字；數字要對，四捨五入可以），
而且作答者引用的文字裡有寫到支持它的內容（引用的文字裡有算式、作答者照算式算出來，也算支持）。兩個都成立記 1，否則記 0。
不要用你自己的知識補作答者沒寫的東西；引用的文字沒寫、答案卻寫了的要點，記 0，並在 why 裡說明。
只輸出一個 JSON 物件，不要其他文字：{"k1a": {"points": [1, 0], "why": "一句話：哪個要點沒答到或沒有出處"}, …}
""")
    for qid, r in loc.items():
        if not sel(r["item"]):
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
        asked |= {k for k in json.loads(Path(a).read_text(encoding="utf-8")) if not k.startswith("_")}
    items = [x for x in items if x[0] in asked]  # 只出了部分題目（exam 指定題號）時，沒出的題不算
    runs = []
    for a, v in pairs:
        answers = json.loads(Path(a).read_text(encoding="utf-8"))
        verdicts = json.loads(Path(v).read_text(encoding="utf-8"))
        loc = locate(q, units, answers)
        r = {}
        for qid, need, it in items:
            if it.get("kind") == "choice":
                right = key_letter(it)
                got = str((answers.get(qid) or {}).get("choice", "")).strip().upper()[:1]
                none = LETTERS[len(it["choices"])]
                content = got == right
                why = "" if content else ("選了「文章沒寫」" if got == none else f"選 {got or '?'}，正確是 {right}")
                r[qid] = {"pass": content and loc[qid]["ok"], "content": content, "loc": loc[qid]["ok"],
                          "pts": f"選{got or '?'}", "lack": loc[qid]["lack"], "why": why}
                continue
            pts = (verdicts.get(qid) or {}).get("points") or []
            content = len(pts) == len(it["key"]) and all(pts)
            why = (verdicts.get(qid) or {}).get("why", "") if pts else "還沒評分（問答題要評分 agent 的 verdicts）"
            r[qid] = {"pass": content and loc[qid]["ok"], "content": content, "loc": loc[qid]["ok"],
                      "pts": "".join("✓" if p else "✗" for p in pts) or "?",
                      "lack": loc[qid]["lack"], "why": why}
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


BLOCK = re.compile(r'<script type="application/json" id="quiz">(.*?)</script>', re.S)


def save(path, src, q):
    body = json.dumps(q, ensure_ascii=False, indent=1)
    Path(path).write_text(BLOCK.sub(lambda m: f'<script type="application/json" id="quiz">\n{body}\n</script>', src, count=1),
                          encoding="utf-8")


def init(path):
    """Skeleton for a new bank: scope = every chapter (div.idea), one section per chapter head and
    one per subsection (p#iN-M, title from its bold lead-in). A chapter head with at most one unit
    (a transition sentence) merges into its first subsection (QUIZ.md). Written into the page."""
    src = Path(path).read_text(encoding="utf-8")
    if BLOCK.search(src):
        sys.exit(f"{path} 已經有題庫，init 不動它")
    root = parse(src)
    scope = [m.group(1) for m in re.finditer(r'<div class="idea" id="(i\d+)"', src)]
    secs = []
    for cid in scope:
        ch = by_id(root, cid)
        h = next(ch.find_all(lambda x: x.tag == "h3"), None)
        secs.append({"from": cid, "title": re.sub(r"^\s*\d+\s*", "", h.text()).strip() if h is not None else cid})
        for m in re.finditer(rf'<p id="({cid}-\d+)"', src):
            el = by_id(root, m.group(1))
            b = next((c for c in el.children if isinstance(c, Node) and c.tag in ("b", "strong")), None)
            secs.append({"from": m.group(1), "title": (b.text() if b is not None else m.group(1)).strip().rstrip("。：:")})
    for i, s_ in enumerate(secs, 1):
        s_["id"] = f"t{i}"
    q = {"version": 1, "scope": scope, "sections": secs, "unit": [], "integration": []}
    n = {}
    for lc, tx, ks in unit_map(src, q):
        if ks and " 標題" not in lc:
            n[ks] = n.get(ks, 0) + 1
    out = []
    for i, s_ in enumerate(secs):
        nxt = secs[i + 1] if i + 1 < len(secs) else None
        if "-" not in s_["from"] and n.get(s_["id"], 0) <= 1 and nxt and nxt["from"].startswith(s_["from"] + "-"):
            nxt["from"] = s_["from"]  # 章首只有一句過場：併進第一個小節
            continue
        out.append(s_)
    out = [{"id": f"k{i}", "from": s_["from"], "title": s_["title"], "core": False, "points": []}
           for i, s_ in enumerate(out, 1)]
    q = {"version": 1, "note": f"題庫：{Path(path).stem.upper()}（規則見 guide/QUIZ.md）。", "scope": scope,
         "sections": out, "unit": [], "integration": []}
    body = json.dumps(q, ensure_ascii=False, indent=1)
    m = re.search(r'<script src="app\.js(\?v=[^"]*)?"></script>', src)
    if not m:
        sys.exit(f'{path} 找不到 <script src="app.js…"></script>')
    tag = m.group(0)
    src = src.replace(tag, f'<script type="application/json" id="quiz">\n{body}\n</script>\n{tag}', 1)
    Path(path).write_text(src, encoding="utf-8")
    print(f"寫進 {path}：{len(scope)} 章、{len(out)} 節（併掉 {len(secs) - len(out)} 個只有一句的章首）")
    for s_ in out:
        print(f"  {s_['id']:4} #{s_['from']:6} {s_['title']}")
    return 0


def spec(path, chapters=()):
    """Packet for the agent that lists concepts: the reader text grouped by section.
    No tldr (a summary teaches nothing new), no questions, no existing points."""
    src, q = load(path)
    names = {s_["id"]: s_ for s_ in q["sections"]}
    secs = [s_ for s_ in q["sections"] if not chapters or s_["from"].split("-")[0] in chapters]
    print(f"# 觀念清單包：{Path(path).name}　{len(secs)} 節")
    cur = None
    for lc, tx, ks in unit_map(src, q):
        if ks is None or (chapters and lc.split(" ")[0][1:] not in chapters):
            continue
        if ks != cur:
            cur = ks
            s_ = names[ks]
            print(f"\n## {ks}　{s_['title']}{'（重點）' if s_.get('core') else ''}")
        print(f"[{lc}] {tx}")
    return 0


def merge(path, parts):
    """Merge subagent output into the page's bank. Each part is a JSON object with any of:
    "points": {"k3": [ {id,type,t,at}, … ]} (replaces that section's points),
    "unit": [ … ] and "integration": [ … ] (a question with an existing id replaces it, otherwise appended
    and the unit list re-sorted by section order)."""
    src, q = load(path)
    order = {s_["id"]: i for i, s_ in enumerate(q["sections"])}
    secs = {s_["id"]: s_ for s_ in q["sections"]}
    np_ = nu = ni = 0
    for part in parts:
        d = json.loads(Path(part).read_text(encoding="utf-8"))
        for k, pts in d.get("points", {}).items():
            if k not in secs:
                sys.exit(f"{part}：節 {k} 不存在")
            secs[k]["points"] = pts
            np_ += len(pts)
        for key, cnt in (("unit", "nu"), ("integration", "ni")):
            have = {x["id"]: i for i, x in enumerate(q.setdefault(key, []))}
            for x in d.get(key, []):
                if x["id"] in have:
                    q[key][have[x["id"]]] = x
                else:
                    q[key].append(x)
                if key == "unit":
                    nu += 1
                else:
                    ni += 1
    q["unit"].sort(key=lambda u: order.get(u.get("ks"), 1e9))
    save(path, src, q)
    print(f"併進 {path}：points {np_} 條、unit {nu} 題、整合 {ni} 題（現在共 {len(q['unit'])} 題 unit、{len(q.get('integration', []))} 題整合）")
    return 0


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    cmd, path = argv[1], argv[2]
    if cmd == "check":
        return check(path)
    if cmd == "init":
        return init(path)
    if cmd == "merge" and len(argv) >= 4:
        return merge(path, argv[3:])
    src, q = load(path)
    if q is None:
        sys.exit(f"{path} 沒有題庫")
    if cmd == "units":
        for lc, tx, ks in unit_map(src, q):
            print(f"{ks or '-':4} [{lc}] {tx[:50]}")
        return 0
    if cmd == "spec":
        return spec(path, set(argv[3:]))
    if cmd == "exam":
        return exam(path, set(argv[3:]))
    if cmd == "closed":
        return closed(path, set(argv[3:]))
    if cmd == "coverage":
        return coverage(path)
    if cmd == "closedcheck" and len(argv) == 4:
        return closedcheck(path, argv[3])
    if cmd == "grade" and len(argv) >= 4:
        return grade(path, argv[3], set(argv[4:]))
    if cmd == "report" and len(argv) >= 5 and len(argv) % 2 == 1:
        return report(path, list(zip(argv[3::2], argv[4::2])))
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
