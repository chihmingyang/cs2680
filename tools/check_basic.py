#!/usr/bin/env python3
"""Check a standalone basic-question fragment (content/lXX-basic.html).

Usage: python3 -I check_basic.py content/lXX-basic.html lXX
Wraps the fragment in a minimal page and runs the same structural rules as
check_discuss.py for the basic set, plus the STE heuristics of check_article.
"""
import re
import sys
from pathlib import Path

frag = Path(sys.argv[1]).read_text(encoding="utf-8")
lec = sys.argv[2]
n = int(lec[1:])
probs = []

# structure via check_discuss's parser
sys.path.insert(0, str(Path(__file__).parent))
import check_discuss as cd  # noqa: E402

p = cd.P(); p.feed(frag); root = p.root
panel = root.find("div", id="qset-basic")
if not panel:
    probs.append("no div#qset-basic")
else:
    panel = panel[0]
    if panel.attrs.get("role") != "tabpanel" or panel.attrs.get("aria-labelledby") != "tab-basic":
        probs.append("qset-basic attrs")
    if not panel.find("p", "qset-lede"):
        probs.append("no qset-lede")
    btn = [x for x in panel.find("button", "copybtn") if x.attrs.get("data-copy") == "basic"]
    if not btn:
        probs.append("no copy button")
    else:
        t = btn[0].attrs.get("data-title", "")
        if not t.startswith(f"CS2680 L{n} 基礎題（帶著問題看 slides）："):
            probs.append(f"data-title {t!r}")
        if not re.fullmatch(r"https://cs2680\.com/slides/[\w.]+\.pdf", btn[0].attrs.get("data-slides", "")):
            probs.append("data-slides")
    ol = panel.find("ol", "qlist-basic")
    if not ol:
        probs.append("no ol.qlist.qlist-basic")
    bqs = panel.find("li", "bq")
    if not 6 <= len(bqs) <= 9:
        probs.append(f"{len(bqs)} questions")
    last_page = 0
    for k, q in enumerate(bqs, 1):
        if q.attrs.get("id") != f"b{k}":
            probs.append(f"b{k}: id {q.attrs.get('id')}")
        tag = q.find("p", "qtag")
        ref = tag[0].find("a", "ref") if tag else []
        if not ref:
            probs.append(f"b{k}: qtag without a.ref")
        else:
            m = re.search(r"#page=(\d+)$", ref[0].attrs.get("href", ""))
            if not m:
                probs.append(f"b{k}: ref href")
            else:
                pg = int(m.group(1))
                if pg < last_page:
                    probs.append(f"b{k}: pages not in slide order ({pg} < {last_page})")
                last_page = pg
            if "·" not in tag[0].txt():
                probs.append(f"b{k}: qtag lacks ' · topic'")
        qt = q.find("p", "qtext")
        if not qt:
            probs.append(f"b{k}: no qtext")
        elif len(qt[0].txt().strip()) > 90:
            probs.append(f"b{k}: qtext too long ({len(qt[0].txt().strip())} chars)")
        dets = q.find("details")
        sums = [x.find("summary")[0].txt().strip() if x.find("summary") else "" for x in dets]
        if sums != ["參考答案"]:
            probs.append(f"b{k}: details {sums}")
        else:
            hint = dets[0].find("div", "hint")
            if not hint:
                probs.append(f"b{k}: no hint div")
            elif len(hint[0].txt().strip()) < 40:
                probs.append(f"b{k}: answer too short")
        if q.find("p", "qctx") or q.find("div", "qcover"):
            probs.append(f"b{k}: has qctx/qcover")

# language heuristics
text = re.sub(r"<[^>]+>", " ", frag)
if "被" in text:
    probs.append("passive 被")
for f in ("其實", "基本上", "非常", "相當", "可以說", "事實上", "簡單來說"):
    if f in text:
        probs.append(f"filler {f}")
if re.search(r"[一-鿿][,;:?!()]", text) or re.search(r"[,;:?!()][一-鿿]", text):
    probs.append("half-width punctuation next to CJK (run punct.py)")
opens = len(re.findall(r"<li class=\"bq\"", frag)); closes = frag.count("</li>")
if opens != closes:
    probs.append(f"li tags unbalanced {opens}/{closes}")
if frag.count("<details>") != frag.count("</details>"):
    probs.append("details unbalanced")

print(f"{Path(sys.argv[1]).name}: {len(root.find('li', 'bq'))} questions")
if probs:
    print("PROBLEMS:")
    for x in probs:
        print("  -", x)
    sys.exit(1)
print("OK")
