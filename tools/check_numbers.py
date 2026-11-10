#!/usr/bin/env python3
"""頁面引用外部來源的數字，和 guide/sources/lXX.md 記的對得上嗎（read-only）。規則見 guide/QUIZ.md〈數字對照〉。

  python3 -I tools/check_numbers.py docs/l06.html          # 有對不上的數字就列出來，exit 1
  python3 -I tools/check_numbers.py docs/l06.html -v       # 另外列出每個來源被哪幾段引用
  python3 -I tools/check_numbers.py docs/l07.html --ci     # verify.sh 用：來源檔沒有標 strict 的講次只印一行 note，不算失敗

為什麼：內容是 agent 改寫的，改寫時把 54% 寫成 45%、或補一個來源沒有的數字，句子讀起來一樣順，
讀者和可讀性審查都看不出來。來源檔已經逐條記了原文的數字，所以用程式對。

怎麼對：
- 來源檔的一筆 ＝ 一個頂層的「- 」項目和它縮排的幾行。裡面的網址是這一筆的 key，裡面的數字是可以出現的數字。
- 頁面的一段（p、表格的一列、figcaption、li）「引用了某一筆」＝ 這一段有連到那個網址的連結，
  或寫出了那個來源的名字（頁面上連到那個網址的連結文字，例如 Failure as a Process）。
- 範圍是從寫出來源的那一句起，到這一段結束；這個範圍裡的每個數字都要在它引用的那幾筆裡找得到。四捨五入算對得上（來源 57.9，頁面寫 58）。
- 對不上有兩種原因：數字錯了（改頁面），或這個數字是本文自己的、不是來源的（例如同一段的「50 步」）。
  後一種在那一段的元素加 data-num-own="50 95"，列出不必對照的數字：本文自己算的，或出自同一段沒寫名字的另一個來源。
- 題庫：觀念清單裡 type 是 evidence 的條目不出題（QUIZ.md），改由這裡保護：
  它的每個數字都要在來源檔裡找得到，也要還在它那一章的讀者文字裡（百分比連 % 一起比）。
  這一項只看數字還在不在那一章，同一章別處剛好有同一個數字時抓不到。
  題目的題幹、正確選項、答案要點如果寫了來源的名字，裡面的數字要在來源檔裡找得到（對整份檔；本文自己的數字加 "num_own"）。
- 沒有來源檔的講次直接跳過。
- 清過的講次在來源檔加一行 `<!-- check_numbers: strict -->`，之後對不上就讓 verify.sh 失敗（2026-11-11：L6、L6b）。
  還沒清的講次，各堂來源檔的寫法不一樣（有的不是一筆一個網址），列出來的多半是格式對不上，不是數字錯。
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = re.compile(r"(?<![\w.#/\-])\d[\d,]*(?:\.\d+)?(?![\w\-])")
URL = re.compile(r"https?://[^\s<>\"'）)，。；、」]+")
# 不是量測數字的：第 N 章／節／堂、圖 N、表 N、L6、年月日
SKIP = re.compile(r"第\s*\d+(?:\s*[、–\-到和與]\s*\d+)*\s*[章節堂列欄]|[圖表列欄]\s*\d+|\bL\d+[a-z]?\b"
                  r"|20\d\d\s*年(?:\s*\d+\s*月)?(?:\s*\d+\s*日)?|\b20\d\d(?:[-/]\d{1,2}){0,2}\b|\d+\s*月\s*\d+\s*日"
                  r"|\b(?:Sonnet|Opus|Haiku|Fable|Mythos|Claude|GPT|Gemini|Llama|Qwen|Nova)[\s\-]?\d+(?:\.\d+)?|\bo\d\b")
NAME = re.compile(r"^[A-Z][A-Za-z0-9 :?'’.\-]{4,}$")
MARK = re.compile(r"⟦([\d,]*)⟧")
BLOCK = re.compile(r"<(p|tr|figcaption|li|dd)\b([^>]*)>(.*?)</\1>", re.S)


def norm_url(u):
    u = html.unescape(u).split("#")[0].rstrip("/.").lower()
    u = re.sub(r"^https?://(www\.)?", "", u)
    m = re.match(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", u)
    return f"arxiv:{m.group(1)}" if m else u


def nums(text):
    """Numbers in a text as (string, value). Chapter refs and dates are dropped first."""
    text = URL.sub(" ", SKIP.sub(" ", text))
    out = []
    for m in NUM.finditer(text):
        s = m.group(0).replace(",", "")
        try:
            out.append((m.group(0), float(s)))
        except ValueError:
            pass
    return out


def matches(tok, val, pool):
    """Exact, or the page rounded the source's number to the precision the page shows."""
    if val in pool:
        return True
    d = len(tok.split(".")[1]) if "." in tok else 0
    return any(abs(round(v, d) - val) < 1e-9 for v in pool)


def read_sources(path):
    """[(urls, numbers, first line)] — one per top-level list item with its indented lines."""
    entries, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- "):
            cur = [line]
            entries.append(cur)
        elif cur is not None and (line.startswith((" ", "\t")) and line.strip()):
            cur.append(line)
        else:
            cur = None
    out = []
    for e in entries:
        text = "\n".join(e)
        urls = {norm_url(u) for u in URL.findall(text)}
        out.append((urls, {v for _, v in nums(text)}, e[0][2:60]))
    return out


def plain(h):
    h = re.sub(r'<svg\b[^>]*aria-label="([^"]*)"[^>]*>.*?</svg>', r" \1 ", h, flags=re.S)
    h = re.sub(r"<svg\b.*?</svg>|<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    page = Path(argv[1])
    verbose = "-v" in argv[2:]
    ci = "--ci" in argv[2:]
    stem = page.stem
    srcfile = next((p for p in (ROOT / "guide/sources" / f"{stem}.md", ROOT / "guide/sources" / f"{stem.rstrip('abcdefgh')}.md") if p.exists()), None)
    if srcfile is None:
        print(f"ok   {stem}: 沒有來源檔，跳過")
        return 0
    entries = read_sources(srcfile)
    strict = "check_numbers: strict" in srcfile.read_text(encoding="utf-8")
    by_url = {}
    for i, (urls, _, _) in enumerate(entries):
        for u in urls:
            by_url.setdefault(u, set()).add(i)
    allnums = set().union(*(e[1] for e in entries)) if entries else set()

    src = page.read_text(encoding="utf-8")
    a, b = src.find("<main"), src.find("</main>")
    main_html = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->", " ", src[a:b], flags=re.S)

    # 來源的名字：頁面上連到這個網址的連結文字（像名字的才算：大寫開頭、6 個字元以上的英文）
    names = {}
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', main_html, re.S):
        ids = by_url.get(norm_url(m.group(1)))
        t = plain(m.group(2)).rstrip(" ↗")
        if ids and NAME.match(t):
            names.setdefault(t, set()).update(ids)

    bad, seen, used = [], set(), {}
    ids_pos = [(m.start(), m.group(1)) for m in re.finditer(r'\sid="([^"]+)"', main_html)]

    def where(pos):
        last = "?"
        for p, i in ids_pos:
            if p > pos:
                break
            last = i
        return "#" + last

    def mark(mm):
        ids = by_url.get(norm_url(mm.group(1)), set())
        return mm.group(2) + (" ⟦" + ",".join(map(str, sorted(ids))) + "⟧ " if ids else "")

    for m in BLOCK.finditer(main_html):
        tag, attrs, inner = m.groups()
        if tag in ("li", "dd") and re.search(r"<(p|tr)\b", inner):
            continue                      # 容器：裡面的 p、tr 會各自檢查
        text = plain(re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', mark, inner, flags=re.S))
        own = re.search(r'data-num-own="([^"]*)"', attrs)
        own = {float(x.replace(",", "")) for x in own.group(1).split()} if own else set()
        active = set()                    # 從寫出來源的那一句起，到這一段結束
        for sent in re.split(r"(?<=[。！？；])", text):
            for mk in MARK.finditer(sent):
                active |= {int(x) for x in mk.group(1).split(",")}
            for n, i in names.items():
                if n in sent:
                    active |= i
            if not active:
                continue
            for i in active:
                used.setdefault(i, []).append(where(m.start()))
            pool = set().union(*(entries[i][1] for i in active)) | own
            clean = MARK.sub(" ", sent)
            for tok, val in nums(clean):
                if not matches(tok, val, pool) and (m.start(), tok) not in seen:
                    seen.add((m.start(), tok))
                    src_names = "、".join(sorted(entries[i][2].split("，")[0][:32] for i in active))
                    k = clean.find(tok)
                    bad.append(f"{where(m.start())} 的 {tok}：這一句引用 {src_names}，來源檔那一筆沒有這個數字｜…{clean[max(0, k - 28):k + len(tok) + 14].strip()}…")

    # 題庫：evidence 類的觀念，和寫了來源名字的題目
    mq = re.search(r'<script type="application/json" id="quiz">(.*?)</script>', src, re.S)
    if mq:
        q = json.loads(mq.group(1))
        chap_text = {}
        for cid in q.get("scope", []):
            cm = re.search(rf'<div\b[^>]*\bid="{re.escape(cid)}"', main_html)
            if cm:
                nxt = re.search(r'<div\b[^>]*class="[^"]*\bidea\b', main_html[cm.end():])
                chap_text[cid] = plain(main_html[cm.start(): cm.end() + nxt.start() if nxt else len(main_html)])
        for s in q["sections"]:
            cid = s["from"].split("-")[0]
            here = {v for _, v in nums(chap_text.get(cid, ""))}
            for pt in s.get("points", []):
                if pt.get("type") != "evidence":
                    continue
                ctext = chap_text.get(cid, "")
                for tok, val in nums(pt["t"]):
                    pct = re.search(r"(?<![\d.,])" + re.escape(tok) + r"\s*%", pt["t"]) is not None
                    if not matches(tok, val, allnums):
                        bad.append(f"觀念 {pt['id']}（evidence）的 {tok}：來源檔沒有這個數字")
                    elif not matches(tok, val, here) or (pct and not re.search(r"(?<![\d.,])" + re.escape(tok) + r"\s*%", ctext)):
                        bad.append(f"觀念 {pt['id']}（evidence）的 {tok}：第 {cid[1:]} 章的文字已經沒有這個數字（正文刪了或改了？）")
        for u in q["unit"] + q.get("integration", []):
            parts = [u.get("q", "")] + [c["t"] for c in u.get("choices", []) if c.get("ok")] + list(u.get("key", []))
            text = " ".join(parts)
            ids = {i for n, s_ in names.items() if n in text for i in s_}
            if not ids:
                continue
            own = {float(x.replace(",", "")) for x in str(u.get("num_own", "")).split()}
            done = set()
            for tok, val in nums(text):          # 題目常把幾個來源放在一起問，所以對整份來源檔
                if tok not in done and not matches(tok, val, allnums | own):
                    done.add(tok)
                    bad.append(f"題目 {u['id']} 的 {tok}：題目寫了來源的名字，來源檔沒有這個數字（本文自己的數字就在題目加 \"num_own\": \"{tok}\"）")

    if verbose:
        for i, (_, _, head) in enumerate(entries):
            print(f"  {head}｜{' '.join(sorted(set(used.get(i, [])))) or '（頁面沒有引用）'}")
    if ci and not strict:
        print(f"ok   {stem}: note {len(bad)} 個數字還沒對過 {srcfile.name}（這一堂還沒清；清完在來源檔加 check_numbers: strict）")
        return 0
    for line in bad:
        print("FAIL", line)
    if not bad:
        print(f"ok   {stem}: 引用來源的 {len(used)} 筆、數字都對得上 {srcfile.name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
