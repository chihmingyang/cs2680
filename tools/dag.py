#!/usr/bin/env python3
"""觀念 DAG：檢查 docs/dag.json，並產生 docs/dag.html。

用法：
  python3 -I tools/dag.py --check     # 只檢查，不寫檔；verify.sh 會跑
  python3 -I tools/dag.py             # 檢查通過就重寫 docs/dag.html

檢查什麼（規則在 guide/DAG.md）：
  - id 唯一、deps 都存在、沒有自己依賴自己、沒有環
  - 難度沿著邊不會降：前置觀念的難度 ≤ 這個觀念（基礎 ≤ 進階 ≤ 專家）
  - src 的錨點（lXX#iN、lXX#iN-M）在該頁真的存在
  - 每一堂核心觀念的每一章，都被某個節點的 src 蓋到，或列在 excluded（目錄章）
  - short 太長（方塊放不下）、同一個 src 出現在兩個節點、可以從別的邊推出來的多餘邊 → 只提示

頁面怎麼畫：x 是依賴深度（最長路徑的層數），y 是主題泳道；顏色是難度；
hover／點一個觀念亮出它的前置（往左）和延伸（往右）；選講次看一堂的章散在哪裡。
頁面下半是從資料算出來的：講次和觀念的落差、依賴順序的閱讀清單。
"""
import html
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs"
DATA = SITE / "dag.json"
OUT = SITE / "dag.html"
TIER_ORDER = ["基礎", "進階", "專家"]
TIER_CLASS = {"基礎": "a", "進階": "c", "專家": "d"}

# ---------- 讀頁面：章節 id 與標題 ----------

def page_chapters(lec):
    """回傳 {chapter_id: title}（只有核心觀念裡的 iN），以及該頁全部 id 的集合。"""
    p = SITE / f"{lec}.html"
    s = p.read_text(encoding="utf-8")
    ids = set(re.findall(r'\sid="([^"]+)"', s))
    seg = s[s.index('id="s-ideas"'):s.index('id="s-discuss"')]
    chapters = {}
    for m in re.finditer(r'<div class="idea" id="(i\d+)">(.*?)(?=<div class="idea" id="i\d+">|$)', seg, re.S):
        h = re.search(r"<h3[^>]*>(.*?)</h3>", m.group(2), re.S)
        t = re.sub(r"<[^>]+>", "", h.group(1)) if h else ""
        t = re.sub(r"\s+", " ", html.unescape(t)).strip()
        t = re.sub(r"^\d+", "", t)  # h3 開頭是章號
        chapters[m.group(1)] = t
    secs = {}
    for m in re.finditer(r'<p[^>]*\bid="(i\d+-\d+)"[^>]*>(.*?)</p>', seg, re.S):
        lead = re.search(r"<(?:b|strong)[^>]*>(.*?)</(?:b|strong)>", m.group(2), re.S)
        t = re.sub(r"<[^>]+>", "", lead.group(1)) if lead else ""
        secs[m.group(1)] = html.unescape(t).strip().rstrip("。：:")
    return chapters, secs, ids


# ---------- 檢查 ----------

def check(d):
    errs, warns = [], []
    nodes = d["nodes"]
    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)):
        dup = {i for i in ids if ids.count(i) > 1}
        errs.append(f"重複的 id：{sorted(dup)}")
    by = {n["id"]: n for n in nodes}
    theme_ids = {t["id"] for t in d["themes"]}
    for n in nodes:
        for k in ("name", "short", "tier", "theme", "src", "deps", "why"):
            if k not in n:
                errs.append(f"{n['id']}：缺 {k}")
        if n.get("tier") not in TIER_ORDER:
            errs.append(f"{n['id']}：tier 要是 {TIER_ORDER}，現在是 {n.get('tier')}")
        if n.get("theme") not in theme_ids:
            errs.append(f"{n['id']}：theme {n.get('theme')} 不在 themes 裡")
        if not n.get("src"):
            errs.append(f"{n['id']}：src 是空的")
        for dep in n.get("deps", []):
            if dep == n["id"]:
                errs.append(f"{n['id']}：依賴自己")
            elif dep not in by:
                errs.append(f"{n['id']}：dep {dep} 不存在")
        w = sum(1 if ord(c) > 0x2E7F else (0.3 if c == " " else 0.56) for c in n.get("short", ""))
        if w > 11.5:
            warns.append(f"{n['id']}：short「{n['short']}」太長（{w:.1f} 個中文字寬），方塊會放不下")
    if errs:
        return errs, warns, None

    # 環 / 拓樸排序（Kahn）
    indeg = {i: len(by[i]["deps"]) for i in by}
    children = defaultdict(list)
    for n in nodes:
        for dep in n["deps"]:
            children[dep].append(n["id"])
    q = deque(sorted(i for i in by if indeg[i] == 0))
    order = []
    while q:
        i = q.popleft()
        order.append(i)
        for c in children[i]:
            indeg[c] -= 1
            if indeg[c] == 0:
                q.append(c)
    if len(order) != len(by):
        stuck = sorted(i for i in by if indeg[i] > 0)
        errs.append(f"有環：這些節點排不進拓樸順序 {stuck}")
        return errs, warns, None

    # 深度 = 最長路徑
    depth = {}
    for i in order:
        depth[i] = max((depth[dep] + 1 for dep in by[i]["deps"]), default=0)

    # 難度單調
    for n in nodes:
        for dep in n["deps"]:
            if TIER_ORDER.index(by[dep]["tier"]) > TIER_ORDER.index(n["tier"]):
                errs.append(f"{n['id']}（{n['tier']}）依賴 {dep}（{by[dep]['tier']}）：前置的難度不能比較高")

    # 多餘的邊：dep 已經是別的 dep 的祖先
    anc = {}
    for i in order:
        s = set()
        for dep in by[i]["deps"]:
            s.add(dep)
            s |= anc[dep]
        anc[i] = s
    for n in nodes:
        for dep in n["deps"]:
            others = set(n["deps"]) - {dep}
            if any(dep in anc[o] for o in others):
                warns.append(f"{n['id']} → {dep} 可以從別的前置推出來（多餘的邊，留著也可以）")

    # src 錨點存在、章節覆蓋
    lectures = sorted(d["lectures"])
    pages = {lec: page_chapters(lec) for lec in lectures}
    seen_src = defaultdict(list)
    covered = defaultdict(set)   # lec -> chapter ids
    for n in nodes:
        for s in n["src"]:
            m = re.fullmatch(r"(l\d\d)#(i\d+)(-\d+)?", s)
            if not m:
                errs.append(f"{n['id']}：src「{s}」格式要像 l04#i6 或 l04#i6-1")
                continue
            lec, ch = m.group(1), m.group(2)
            if lec not in pages:
                errs.append(f"{n['id']}：src「{s}」的講次不在 lectures 裡")
                continue
            if s.split("#")[1] not in pages[lec][2]:
                errs.append(f"{n['id']}：src「{s}」在 docs/{lec}.html 找不到這個 id")
            covered[lec].add(ch)
            seen_src[s].append(n["id"])
    for s, who in seen_src.items():
        if len(who) > 1:
            warns.append(f"src {s} 出現在 {who}")
    excluded = {e["src"] for e in d.get("excluded", [])}
    for lec in lectures:
        for ch in pages[lec][0]:
            key = f"{lec}#{ch}"
            if ch not in covered[lec] and key not in excluded:
                errs.append(f"{key}「{pages[lec][0][ch]}」沒有節點蓋到，也不在 excluded")
            if ch in covered[lec] and key in excluded:
                warns.append(f"{key} 既有節點蓋到又在 excluded")
    for e in d.get("excluded", []):
        lec, ch = e["src"].split("#")
        if lec not in pages or ch not in pages[lec][0]:
            errs.append(f"excluded {e['src']} 不是任何一頁的章")

    info = {"order": order, "depth": depth, "children": children, "anc": anc, "pages": pages}
    return errs, warns, info


# ---------- 版面 ----------

def wrap_short(s, units=9.2):
    def w(t):
        return sum(1 if ord(c) > 0x2E7F else (0.3 if c == " " else 0.56) for c in t)
    if w(s) <= units:
        return [s]
    # 先找空格，離中間最近的
    best = None
    for i, c in enumerate(s):
        if c == " ":
            cand = (abs(w(s[:i]) - w(s) / 2), i)
            if best is None or cand < best:
                best = cand
    if best:
        i = best[1]
        return [s[:i], s[i + 1:]]
    # 沒空格：在中文字之間切
    acc = 0
    for i, c in enumerate(s):
        acc += 1 if ord(c) > 0x2E7F else 0.56
        if acc >= w(s) / 2:
            return [s[:i + 1], s[i + 1:]]
    return [s]


def layout(d, info):
    by = {n["id"]: n for n in d["nodes"]}
    depth = info["depth"]
    D = max(depth.values())
    themes = [t["id"] for t in d["themes"]]
    cells = {(t, k): [] for t in themes for k in range(D + 1)}
    for i in info["order"]:
        cells[(by[i]["theme"], depth[i])].append(i)
    # 幾何
    W_TOTAL = 1200
    ML, MR, MT = 14, 14, 30
    pitch = min(150, (W_TOTAL - ML - MR) // (D + 1))
    NW, NH, GAP_Y = pitch - 18, 46, 10
    HEAD = 24
    PAD = 10
    pos = {}
    rows = []
    y = MT
    for t in themes:
        maxn = max(len(cells[(t, k)]) for k in range(D + 1))
        top = y
        inner_top = y + HEAD
        for k in range(D + 1):
            cell = cells[(t, k)]
            # 依前置的 y 重心排序，前置都在左邊的欄，已經放好
            def bary(i):
                ys = [pos[dep][1] for dep in by[i]["deps"] if dep in pos]
                return sum(ys) / len(ys) if ys else 0
            cell.sort(key=bary)
            for j, i in enumerate(cell):
                pos[i] = (ML + k * pitch, inner_top + j * (NH + GAP_Y))
        hgt = HEAD + maxn * (NH + GAP_Y) - GAP_Y + PAD * 2 if maxn else HEAD + PAD
        rows.append((t, top, hgt))
        y = top + hgt
    H = y + 10
    W = ML + (D + 1) * pitch - (pitch - NW) + MR
    return {"pos": pos, "rows": rows, "D": D, "pitch": pitch, "NW": NW, "NH": NH, "W": W, "H": H, "ML": ML, "MT": MT}


def svg(d, info, L):
    by = {n["id"]: n for n in d["nodes"]}
    theme_name = {t["id"]: t["name"] for t in d["themes"]}
    pos, NW, NH, W, H = L["pos"], L["NW"], L["NH"], L["W"], L["H"]
    out = []
    out.append(f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" role="img" '
               f'aria-label="觀念 DAG：{len(by)} 個觀念，依依賴深度由左到右分成 {L["D"] + 1} 層，依主題分成 {len(L["rows"])} 列；顏色是難度">')
    # 泳道底
    for idx, (t, top, hgt) in enumerate(L["rows"]):
        cls = "dag-lane" + (" alt" if idx % 2 else "")
        out.append(f'<rect class="{cls}" x="0" y="{top}" width="{W}" height="{hgt}"/>')
        out.append(f'<text class="dag-lane-t" x="{L["ML"]}" y="{top + 16}">{html.escape(theme_name[t])}</text>')
    # 欄標
    for k in range(L["D"] + 1):
        x = L["ML"] + k * L["pitch"] + NW / 2
        label = "第 0 層 · 起點" if k == 0 else f"第 {k} 層"
        out.append(f'<text class="dag-col-t" x="{x}" y="{L["MT"] - 10}" text-anchor="middle">{label}</text>')
    # 邊。跨好幾欄的邊會有一段接近垂直的線，落在來源那一欄右邊的空隙裡；
    # 同一欄的來源各用空隙裡不同的 x，免得全部疊成一條。
    gap = L["pitch"] - NW
    col_rank = defaultdict(int)
    lane_x = {}
    for i in sorted(pos, key=lambda i: (pos[i][0], pos[i][1])):
        k = col_rank[pos[i][0]]
        col_rank[pos[i][0]] += 1
        lane_x[i] = pos[i][0] + NW + 6 + (k % 5) * ((gap - 12) / 4)
    out.append('<g class="dag-edges">')
    for n in d["nodes"]:
        x2, y2 = pos[n["id"]]
        for dep in n["deps"]:
            x1, y1 = pos[dep]
            ax, ay = x1 + NW, y1 + NH / 2
            bx, by_ = x2, y2 + NH / 2
            if bx - ax <= gap + 1:
                mx = (ax + bx) / 2
                dpath = f"M{ax:.0f},{ay:.0f} C{mx:.0f},{ay:.0f} {mx:.0f},{by_:.0f} {bx:.0f},{by_:.0f}"
            else:
                # 正交走線，轉角圓一點：往右到空隙裡的 lx，垂直到目標那一列，再往右接上
                lx = lane_x[dep]
                r = 6
                if abs(by_ - ay) < 2 * r:
                    dpath = f"M{ax:.0f},{ay:.0f} L{bx:.0f},{by_:.0f}"
                else:
                    sg = 1 if by_ > ay else -1
                    dpath = (f"M{ax:.0f},{ay:.0f} L{lx - r:.0f},{ay:.0f} Q{lx:.0f},{ay:.0f} {lx:.0f},{ay + sg * r:.0f} "
                             f"L{lx:.0f},{by_ - sg * r:.0f} Q{lx:.0f},{by_:.0f} {lx + r:.0f},{by_:.0f} L{bx:.0f},{by_:.0f}")
            out.append(f'<path class="dag-e" data-from="{dep}" data-to="{n["id"]}" d="{dpath}"/>')
    out.append("</g>")
    # 節點
    out.append('<g class="dag-nodes">')
    for n in d["nodes"]:
        x, y = pos[n["id"]]
        lec = n["src"][0].split("#")[0]
        tag = "L" + str(int(lec[1:]))
        lines = wrap_short(n["short"])
        label = html.escape(n["short"])
        out.append(f'<g class="dag-n tier-{TIER_CLASS[n["tier"]]}" id="n-{n["id"]}" data-id="{n["id"]}" tabindex="0" role="button" '
                   f'aria-label="{label}，{n["tier"]}，{tag}">')
        out.append(f'<rect class="dag-box" x="{x}" y="{y}" width="{NW}" height="{NH}" rx="5"/>')
        out.append(f'<rect class="dag-tier" x="{x}" y="{y}" width="4" height="{NH}" rx="2"/>')
        out.append(f'<text class="dag-tag" x="{x + NW - 6}" y="{y + 11}" text-anchor="end">{tag}</text>')
        if len(lines) == 1:
            out.append(f'<text class="dag-t" x="{x + 10}" y="{y + NH / 2 + 4.5:.1f}">{html.escape(lines[0])}</text>')
        else:
            out.append(f'<text class="dag-t" x="{x + 10}" y="{y + 20}">{html.escape(lines[0])}</text>')
            out.append(f'<text class="dag-t" x="{x + 10}" y="{y + 35}">{html.escape(lines[1])}</text>')
        out.append("</g>")
    out.append("</g></svg>")
    return "\n".join(out)


# ---------- 分析 ----------

def lec_no(src):
    return int(src.split("#")[0][1:])


def first_lec(n):
    """這個觀念第一次出現（哪怕只是帶過）的講次。"""
    return min(lec_no(s) for s in n["src"])


def analyze(d, info):
    by = {n["id"]: n for n in d["nodes"]}
    depth = info["depth"]
    merged = [n for n in d["nodes"] if len({s.split("#")[0] for s in n["src"]}) > 1]
    # 前置在後面的講次：這個觀念在主要講次（src[0]）被教的時候，前置連第一次提到都還沒出現
    forward = []
    for n in d["nodes"]:
        me = lec_no(n["src"][0])
        for dep in n["deps"]:
            if first_lec(by[dep]) > me:
                forward.append((n, by[dep]))
    per_lec = {}
    for lec in sorted(d["lectures"]):
        ns = [n for n in d["nodes"] if n["src"][0].startswith(lec + "#")]
        tiers = {t: sum(1 for n in ns if n["tier"] == t) for t in TIER_ORDER}
        ds = [depth[n["id"]] for n in ns]
        fw = sum(1 for n, dep in forward if n["src"][0].startswith(lec + "#"))
        per_lec[lec] = {"n": len(ns), "tiers": tiers, "dmin": min(ds) if ds else None, "dmax": max(ds) if ds else None, "fw": fw}
    tier_total = {t: sum(1 for n in d["nodes"] if n["tier"] == t) for t in TIER_ORDER}
    roots = [n for n in d["nodes"] if not n["deps"]]
    return {"merged": merged, "forward": forward, "per_lec": per_lec, "tier_total": tier_total, "roots": roots}


# ---------- 頁面 ----------

def esc(s):
    return html.escape(s, quote=True)


def src_label(s, pages):
    lec, anchor = s.split("#")
    ch = anchor.split("-")[0]
    chapters, secs, _ = pages[lec]
    t = chapters.get(ch, "")
    if "-" in anchor and anchor in secs:
        t = f"{t}（{secs[anchor]}）"
    return f"L{int(lec[1:])} 第 {ch[1:]} 章 {t}"


def src_label_short(s, pages):
    """清單用：只到章名的冒號為止，例如「L2 第 1 章 Loop」。"""
    full = src_label(s, pages)
    return full.split("：")[0]


def tier_badge(t):
    return f'<span class="dag-badge tier-{TIER_CLASS[t]}">{t}</span>'


def render(d, info, L, A):
    by = {n["id"]: n for n in d["nodes"]}
    pages = info["pages"]
    depth = info["depth"]
    theme_name = {t["id"]: t["name"] for t in d["themes"]}
    N = len(d["nodes"])
    E = sum(len(n["deps"]) for n in d["nodes"])

    # 給 JS 的資料（含章節標題，點節點時顯示）
    js_nodes = []
    for n in d["nodes"]:
        js_nodes.append({
            "id": n["id"], "name": n["name"], "short": n["short"], "tier": n["tier"],
            "theme": theme_name[n["theme"]], "deps": n["deps"], "why": n["why"],
            "depth": depth[n["id"]],
            "src": [{"href": f"{s.split('#')[0]}.html#{s.split('#')[1]}", "label": src_label(s, pages)} for s in n["src"]],
            "lecs": sorted({"L" + str(int(s.split("#")[0][1:])) for s in n["src"]}, key=lambda x: int(x[1:])),
        })
    data_json = json.dumps({"nodes": js_nodes}, ensure_ascii=False).replace("</", "<\\/")

    # 講次 × 難度表
    rows = []
    for lec, r in A["per_lec"].items():
        t = r["tiers"]
        rows.append(
            f'<tr><th scope="row"><a href="{lec}.html">L{int(lec[1:])}</a> {esc(d["lectures"][lec])}</th>'
            f'<td>{r["n"]}</td><td>{t["基礎"]}</td><td>{t["進階"]}</td><td>{t["專家"]}</td>'
            f'<td>{r["dmin"]}–{r["dmax"]}</td><td>{r["fw"] or "—"}</td></tr>')
    tt = A["tier_total"]
    rows.append(f'<tr class="dag-sum"><th scope="row">合計</th><td>{N}</td><td>{tt["基礎"]}</td><td>{tt["進階"]}</td><td>{tt["專家"]}</td><td>0–{L["D"]}</td><td>{len(A["forward"])}</td></tr>')
    table = ("<div class=\"table-wrap\"><table class=\"dag-table\">"
             "<thead><tr><th>講次</th><th>觀念數</th><th>基礎</th><th>進階</th><th>專家</th><th>深度範圍</th><th>前置在後面講次的邊</th></tr></thead>"
             f"<tbody>{''.join(rows)}</tbody></table></div>")

    # 散在兩堂
    merged_li = []
    for n in A["merged"]:
        srcs = "、".join(f'<a href="{s.split("#")[0]}.html#{s.split("#")[1]}" title="{esc(src_label(s, pages))}">{esc(src_label_short(s, pages))}</a>' for s in n["src"])
        merged_li.append(f'<li><button type="button" class="dag-ref" data-id="{n["id"]}">{esc(n["short"])}</button>：{srcs}</li>')

    # 前置在後面的講次
    fw_by_lec = defaultdict(list)
    for n, dep in A["forward"]:
        fw_by_lec[lec_no(n["src"][0])].append((n, dep))
    fw_blocks = []
    for lec in sorted(fw_by_lec):
        items = []
        for n, dep in fw_by_lec[lec]:
            items.append(f'<li><button type="button" class="dag-ref" data-id="{n["id"]}">{esc(n["short"])}</button>'
                         f' 要先懂 <button type="button" class="dag-ref" data-id="{dep["id"]}">{esc(dep["short"])}</button>'
                         f'<small>（L{first_lec(dep)} 才出現）</small></li>')
        fw_blocks.append(f'<li><b>L{lec} {esc(d["lectures"][f"l{lec:02d}"])}</b><ul>{"".join(items)}</ul></li>')

    # 依賴順序的閱讀清單：一層一組，層內依主題
    theme_rank = {t["id"]: k for k, t in enumerate(d["themes"])}
    layers = defaultdict(list)
    for i in info["order"]:
        layers[depth[i]].append(i)
    layer_blocks = []
    for k in range(L["D"] + 1):
        ids = sorted(layers[k], key=lambda i: (theme_rank[by[i]["theme"]], by[i]["short"]))
        lis = []
        for i in ids:
            n = by[i]
            deps = "、".join(f'<button type="button" class="dag-ref" data-id="{dep}">{esc(by[dep]["short"])}</button>' for dep in n["deps"])
            lec = "L" + str(int(n["src"][0].split("#")[0][1:]))
            lis.append(
                f'<li id="o-{i}">{tier_badge(n["tier"])}<span class="dag-o-main"><button type="button" class="dag-ref strong" data-id="{i}">{esc(n["short"])}</button>'
                f'<span class="dag-o-name">{esc(n["name"])}</span>'
                f'<span class="dag-o-meta"><a href="{n["src"][0].split("#")[0]}.html#{n["src"][0].split("#")[1]}">{lec}</a>'
                + (f' · 前置：{deps}' if deps else " · 起點") + "</span></span></li>")
        title = "第 0 層：起點，不靠課程裡別的觀念" if k == 0 else f"第 {k} 層：前置都在前 {k} 層"
        layer_blocks.append(f'<li class="dag-layer"><h3>{title}<small>{len(ids)} 個</small></h3><ol class="dag-olist">{"".join(lis)}</ol></li>')

    roots_txt = "、".join(f'<button type="button" class="dag-ref" data-id="{n["id"]}">{esc(n["short"])}</button>' for n in A["roots"])
    tiers_desc = "".join(f"<li>{tier_badge(t)}<span>{esc(d['tiers'][t])}。全站 {tt[t]} 個。</span></li>" for t in TIER_ORDER)
    lec_opts = "".join(f'<option value="L{int(l[1:])}">L{int(l[1:])} {esc(t)}</option>' for l, t in sorted(d["lectures"].items()))
    excluded_li = "".join(f'<li><a href="{e["src"].split("#")[0]}.html#{e["src"].split("#")[1]}">{esc(src_label(e["src"], pages))}</a>：{esc(e["why"])}</li>' for e in d.get("excluded", []))

    page = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>觀念 DAG · CS2680</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap">
<link rel="stylesheet" href="styles.css?v=20261102b">
<script>try{{var m=localStorage.getItem('cs2680.mode');if(m==='light'||m==='dark')document.documentElement.setAttribute('data-mode',m)}}catch(e){{}}</script>
<style>
/* 這一頁自己的樣式；配色全部用 styles.css 的 token，暗色才正常 */
.dag-page {{ max-width: 76rem; }}
.dag-head {{ max-width: var(--measure); display: grid; gap: .45rem; padding-block: .5rem 1.25rem; }}
.dag-head p {{ margin: 0; }}
.dag-bar {{ display: flex; flex-wrap: wrap; gap: .6rem 1.25rem; align-items: center; margin: 1rem 0 .6rem; font-size: .875rem; }}
.dag-bar fieldset {{ border: 0; padding: 0; margin: 0; display: flex; gap: .6rem; align-items: center; flex-wrap: wrap; }}
.dag-bar legend {{ float: left; padding: 0; margin-right: .2rem; color: var(--ink-soft); }}
.dag-bar label {{ display: inline-flex; gap: .3rem; align-items: center; cursor: pointer; }}
.dag-bar select {{ font: inherit; font-size: .875rem; padding: .15rem .4rem; border: 1px solid var(--rule); border-radius: var(--radius); background: var(--sheet); color: var(--ink); }}
.dag-bar .spacer {{ flex: 1; }}
.dag-bar button {{ font: inherit; font-size: .8125rem; padding: .2rem .7rem; border: 1px solid var(--rule); border-radius: 999px; background: var(--sheet); color: var(--ink); cursor: pointer; }}
.dag-bar button:hover {{ border-color: var(--signal); color: var(--signal); }}
.dag-badge {{ display: inline-block; font-family: var(--font-mono); font-size: .6875rem; line-height: 1.5; padding: 0 .45rem; border-radius: 999px; border: 1px solid var(--rule); color: var(--ink); white-space: nowrap; }}
.dag-badge.tier-a {{ background: var(--dg-a); }}
.dag-badge.tier-c {{ background: var(--dg-c); }}
.dag-badge.tier-d {{ background: var(--dg-d); }}
.dag-fig .scroll {{ padding: .5rem .25rem .75rem; }}
.dag-fig svg {{ width: {L["W"]}px; min-width: {L["W"]}px; max-width: none; height: auto; }}
@media (min-width: 1100px) {{ .dag-fig.fit svg {{ width: 100%; min-width: 0; }} }}
.dag-lane {{ fill: transparent; }}
.dag-lane.alt {{ fill: var(--dg-panel); }}
.dag-lane-t {{ fill: var(--ink-soft); font-family: var(--font-display); font-weight: 600; font-size: 12px; letter-spacing: .02em; }}
.dag-col-t {{ fill: var(--ink-soft); font-family: var(--font-mono); font-size: 10.5px; }}
.dag-e {{ fill: none; stroke: var(--dg-link); stroke-width: 1.2; opacity: .45; transition: opacity .12s, stroke-width .12s; }}
.dag-n {{ cursor: pointer; outline: none; }}
.dag-box {{ fill: var(--sheet); stroke: var(--rule); stroke-width: 1; transition: opacity .12s; }}
.dag-n.tier-a .dag-box {{ fill: var(--dg-a); }}
.dag-n.tier-c .dag-box {{ fill: var(--dg-c); }}
.dag-n.tier-d .dag-box {{ fill: var(--dg-d); }}
.dag-tier {{ fill: var(--ink-soft); opacity: .0; }}
.dag-n.tier-c .dag-tier {{ opacity: .35; }}
.dag-n.tier-d .dag-tier {{ opacity: .8; }}
.dag-t {{ fill: var(--ink); font-family: var(--font-body); font-size: 12.5px; pointer-events: none; }}
.dag-tag {{ fill: var(--ink-soft); font-family: var(--font-mono); font-size: 9.5px; pointer-events: none; }}
.dag-n:hover .dag-box, .dag-n:focus-visible .dag-box {{ stroke: var(--signal); stroke-width: 1.6; }}
/* 高亮狀態：has-focus 時沒被點名的都淡掉 */
.has-focus .dag-n:not(.is-sel):not(.is-anc):not(.is-desc) {{ opacity: .22; }}
.has-focus .dag-e:not(.is-anc):not(.is-desc) {{ opacity: .06; }}
.dag-n.is-sel .dag-box {{ stroke: var(--key); stroke-width: 2.2; }}
.dag-n.is-anc .dag-box {{ stroke: var(--signal); stroke-width: 1.8; }}
.dag-n.is-desc .dag-box {{ stroke: var(--caution); stroke-width: 1.8; stroke-dasharray: 4 3; }}
.dag-e.is-anc {{ stroke: var(--signal); opacity: .95; stroke-width: 1.8; }}
.dag-e.is-desc {{ stroke: var(--caution); opacity: .9; stroke-width: 1.6; stroke-dasharray: 4 3; }}
/* 篩選：不符合的淡掉 */
.dag-n.is-off {{ opacity: .15; }}
.dag-e.is-off {{ opacity: .04; }}
.dag-legend {{ display: flex; flex-wrap: wrap; gap: .4rem 1.25rem; margin: .5rem 0 0; padding: 0; list-style: none; font-size: .8125rem; color: var(--ink-soft); }}
.dag-legend li {{ display: inline-flex; align-items: center; gap: .4rem; }}
.dag-legend i {{ display: inline-block; width: 1.4rem; height: 0; border-top: 2px solid var(--signal); }}
.dag-legend i.desc {{ border-top-style: dashed; border-color: var(--caution); }}
.dag-legend i.sel {{ width: .9rem; height: .9rem; border: 2px solid var(--key); border-radius: 3px; }}
/* 詳細面板 */
.dag-detail {{ margin-top: 1rem; border: 1px solid var(--rule); border-left: 4px solid var(--signal); border-radius: var(--radius); background: var(--sheet); padding: 1rem 1.1rem; display: grid; gap: .6rem; max-width: 52rem; }}
.dag-detail .hint {{ color: var(--ink-soft); margin: 0; }}
.dag-detail h2 {{ margin: 0; font-size: 1.15rem; font-family: var(--font-display); display: flex; flex-wrap: wrap; gap: .5rem .6rem; align-items: center; }}
.dag-detail h2 small {{ font-family: var(--font-mono); font-weight: 400; font-size: .75rem; color: var(--ink-soft); }}
.dag-detail .claim {{ margin: 0; font-weight: 500; }}
.dag-detail .why {{ margin: 0; color: var(--ink); }}
.dag-detail dl {{ margin: 0; display: grid; grid-template-columns: 5.5rem minmax(0, 1fr); gap: .35rem .8rem; font-size: .9rem; }}
.dag-detail dt {{ color: var(--ink-soft); }}
.dag-detail dd {{ margin: 0; display: flex; flex-wrap: wrap; gap: .3rem .5rem; align-items: baseline; }}
.dag-detail dd .none {{ color: var(--ink-soft); }}
@media (max-width: 520px) {{ .dag-detail dl {{ grid-template-columns: 1fr; gap: .15rem; }} .dag-detail dt {{ margin-top: .3rem; }} }}
.dag-ref {{ font: inherit; padding: 0 .1rem; border: 0; border-bottom: 1px dashed var(--signal); background: none; color: var(--signal); cursor: pointer; text-align: left; }}
.dag-ref:hover {{ border-bottom-style: solid; }}
.dag-ref.strong {{ font-weight: 600; color: var(--ink); border-bottom-color: var(--ink-soft); }}
/* 下半：分析與清單 */
.dag-sec {{ margin-top: 2.5rem; display: grid; gap: .9rem; max-width: 52rem; }}
.dag-sec > h2 {{ margin: 0; font-family: var(--font-display); font-weight: 700; font-size: 1.5rem; }}
.dag-sec > p, .dag-sec li {{ max-width: var(--measure); }}
.dag-sec > p {{ margin: 0; }}
.dag-sec h3 {{ margin: 1rem 0 .3rem; font-size: 1.05rem; font-family: var(--font-display); }}
.dag-sec h3 small {{ margin-left: .5rem; font-family: var(--font-mono); font-size: .75rem; font-weight: 400; color: var(--ink-soft); }}
.dag-table {{ border-collapse: collapse; font-size: .875rem; width: 100%; }}
.dag-table th, .dag-table td {{ padding: .4rem .6rem; border-bottom: 1px solid var(--rule); text-align: left; white-space: nowrap; }}
.dag-table thead th {{ color: var(--ink-soft); font-weight: 500; border-bottom: 2px solid var(--ink); }}
.dag-table td {{ font-variant-numeric: tabular-nums; }}
.dag-table .dag-sum th, .dag-table .dag-sum td {{ font-weight: 600; border-bottom: 0; }}
.dag-fw {{ list-style: none; padding: 0; margin: 0; display: grid; gap: .6rem; }}
.dag-fw > li > ul {{ margin: .25rem 0 0; padding-left: 1.2rem; display: grid; gap: .2rem; }}
.dag-fw small {{ color: var(--ink-soft); }}
.dag-layers {{ list-style: none; padding: 0; margin: 0; display: grid; gap: .4rem; }}
.dag-layer > h3 {{ margin: .8rem 0 .4rem; }}
.dag-olist {{ list-style: none; padding: 0; margin: 0; display: grid; gap: .45rem; }}
.dag-olist > li {{ display: grid; grid-template-columns: 3.2rem minmax(0, 1fr); gap: .25rem .7rem; align-items: start; padding: .35rem 0; border-bottom: 1px solid var(--rule); }}
.dag-olist .dag-badge {{ justify-self: start; margin-top: .15rem; }}
.dag-o-main {{ display: grid; gap: .15rem; min-width: 0; }}
.dag-o-main > .dag-ref {{ justify-self: start; }}
.dag-o-name {{ font-size: .9rem; color: var(--ink); }}
.dag-o-meta {{ font-size: .8125rem; color: var(--ink-soft); }}
.dag-rules {{ margin: 0; padding-left: 1.2rem; display: grid; gap: .35rem; }}
.dag-tiers {{ list-style: none; margin: 0; padding: 0; display: grid; gap: .4rem; }}
.dag-tiers li {{ display: grid; grid-template-columns: 3.2rem minmax(0, 1fr); gap: .6rem; align-items: start; }}
.dag-tiers .dag-badge {{ margin-top: .2rem; justify-self: start; }}
</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner gutter">
    <a class="brand" href="index.html">CS2680 <span>觀念導讀</span></a>
    <nav class="lecnav" aria-label="回首頁"><a href="index.html">← 課程總覽</a><a href="#rules-h">規則</a></nav>
  </div>
</header>

<main class="page gutter dag-page">
  <header class="dag-head">
    <p class="eyebrow">課程地圖 · 觀念 DAG · 草稿 {d["updated"]}</p>
    <h1>觀念 DAG：每個觀念從哪裡來</h1>
    <p>這門課現在是用一小時的 slides 切成一堂一堂，但觀念之間的依賴不照堂次走。這張圖把 11 堂的核心觀念拆成 <b>{N} 個觀念</b>、<b>{E} 條「要先懂」的邊</b>，每個觀念都從別的觀念延伸出來，只有 {len(A["roots"])} 個起點：{roots_txt}。</p>
    <p>怎麼讀：<b>由左到右是依賴深度</b>（第 k 層的前置都在前 k 層，所以從左往右讀就是一個合法的順序）；<b>每一列是一個主題</b>；<b>顏色是難度</b>。點一個觀念，看它往左的前置和往右的延伸；選一堂講次，看那一堂的章散在圖的哪裡。</p>
  </header>

  <div class="dag-bar" role="group" aria-label="篩選">
    <fieldset><legend>難度</legend>
      <label><input type="checkbox" class="dag-f-tier" value="基礎" checked> {tier_badge("基礎")}</label>
      <label><input type="checkbox" class="dag-f-tier" value="進階" checked> {tier_badge("進階")}</label>
      <label><input type="checkbox" class="dag-f-tier" value="專家" checked> {tier_badge("專家")}</label>
    </fieldset>
    <label>講次 <select id="dag-f-lec"><option value="">全部</option>{lec_opts}</select></label>
    <span class="spacer"></span>
    <label><input type="checkbox" id="dag-fit"> 縮到螢幕寬</label>
    <button type="button" id="dag-clear">清除選取</button>
  </div>

  <figure class="diagram dag-fig" id="dag-fig">
    <div class="scroll">{svg(d, info, L)}</div>
    <ul class="dag-legend" aria-label="圖例">
      <li>{tier_badge("基礎")} {tier_badge("進階")} {tier_badge("專家")} 難度</li>
      <li><i class="sel"></i> 選取的觀念</li>
      <li><i></i> 它的前置（往左）</li>
      <li><i class="desc"></i> 從它延伸出去的（往右）</li>
      <li>方塊右上的 L 數字是講得最完整的那一堂；散在兩堂的觀念列在下面</li>
    </ul>
    <figcaption>每個方塊是一個觀念，寫的是短名；點開看完整的一句話主張和「為什麼從那裡延伸」。一條邊 A → B 的意思是「讀 B 之前要先懂 A」，只畫直接的前置，能從別條邊推出來的不重畫。版面：x 是最長依賴路徑的長度，y 是主題；同一格有好幾個觀念時上下排。</figcaption>
  </figure>

  <aside class="dag-detail" id="dag-detail" aria-live="polite">
    <p class="hint">點圖上的一個觀念，這裡會顯示它的主張、為什麼從那些觀念延伸、出處章節，和從它延伸出去的觀念。</p>
  </aside>

  <section class="dag-sec" aria-labelledby="gap-h">
    <h2 id="gap-h">講次和觀念的落差</h2>
    <p>下面三件事都是從上面的圖算出來的，不是另外寫的。它們就是「一小時一堂」和「觀念的依賴」對不上的地方。</p>
    <h3>一個觀念散在兩堂<small>{len(A["merged"])} 個</small></h3>
    <p>同一個觀念在兩堂各講一半：一堂從 workload 講，一堂從機制講。拆成觀念之後它們是同一個節點。</p>
    <ul class="dag-fw">{"".join(merged_li)}</ul>
    <h3>前置觀念在後面的講次<small>{len(A["forward"])} 條邊</small></h3>
    <p>照講次讀，讀到這個觀念的那一堂，它的前置連帶過都還沒出現過（前置若在更早的講次提過一句，就不算）。站台把 Part I 的建議順序改成 L2 → L4 → L3 → L5，修掉了幾條；剩下的只能靠文章裡的前情註。</p>
    <ul class="dag-fw">{"".join(fw_blocks)}</ul>
    <h3>每一堂的難度組成與深度範圍</h3>
    <p>深度是圖上的層數。一堂的深度範圍越寬，表示它同時在講起點和很下游的東西；「前置在後面講次的邊」越多，表示照講次讀會越卡。</p>
    {table}
  </section>

  <section class="dag-sec" aria-labelledby="order-h">
    <h2 id="order-h">依賴順序的閱讀清單</h2>
    <p>把圖攤平成清單：一層一組，同一層裡依主題排。每一層的前置都在前面的層，所以照這份清單讀不會碰到沒教過的前置。這是把課程改成 DAG 形式時的順序草稿，不是最後的分堂。</p>
    <ol class="dag-layers">{"".join(layer_blocks)}</ol>
  </section>

  <section class="dag-sec" aria-labelledby="rules-h">
    <h2 id="rules-h">這張圖怎麼定的</h2>
    <h3>節點是什麼</h3>
    <ul class="dag-rules">
      <li>一個節點是一個觀念：能用一句話寫成主張、有自己的前置、刪掉它後面某個觀念就讀不懂。</li>
      <li>起點是各堂核心觀念的章（v7 版面已經一章一個想法）。一章講兩個前置不同的觀念就拆成兩個節點（例如 L1 第 9 章拆成機率性輸出、測試分兩層、故障是常態）；兩堂講同一個觀念就併成一個節點（例如 Agent loop 來自 L1 與 L2）。</li>
      <li>目錄章（查閱用的清單）不是觀念，不進圖：{excluded_li and "<ul>" + excluded_li + "</ul>"}</li>
    </ul>
    <h3>邊是什麼</h3>
    <ul class="dag-rules">
      <li>A → B 表示「讀 B 之前要先懂 A」。B 的「為什麼從這裡延伸」那一句要能說出少了 A 哪裡讀不懂。</li>
      <li>只畫直接的前置。A → C 能從 A → B → C 推出來就不畫。</li>
      <li>邊只看觀念，不看講次。所以會出現前置在後面講次的邊，那正是要找的落差。</li>
    </ul>
    <h3>難度怎麼分</h3>
    <ul class="dag-tiers">{tiers_desc}</ul>
    <p>一條規則：前置的難度不能比這個觀念高。基礎觀念不能依賴進階觀念，否則不是邊畫錯就是難度標錯。<code>tools/dag.py --check</code> 會擋。</p>
    <p>資料在 <a href="https://github.com/chihmingyang/cs2680/blob/main/docs/dag.json" target="_blank" rel="noopener">docs/dag.json</a>，規則全文在 <a href="https://github.com/chihmingyang/cs2680/blob/main/guide/DAG.md" target="_blank" rel="noopener">guide/DAG.md</a>。這一頁由 <code>tools/dag.py</code> 從資料產生，改資料就重跑。</p>
  </section>

  <p class="fineprint">這張圖是讀書會對課程內容的整理，節點的主張、邊和難度都是本文的判斷，不代表講者。原始 slides 與課程內容的版權屬於 Juncheng Yang 與 Harvard CS2680。</p>
</main>

<script type="application/json" id="dag-data">{data_json}</script>
<script>
(function () {{
  var data = JSON.parse(document.getElementById('dag-data').textContent);
  var by = {{}}, kids = {{}};
  data.nodes.forEach(function (n) {{ by[n.id] = n; kids[n.id] = []; }});
  data.nodes.forEach(function (n) {{ n.deps.forEach(function (d) {{ kids[d].push(n.id); }}); }});
  var fig = document.getElementById('dag-fig');
  var svgEl = fig.querySelector('svg');
  var nodeEls = {{}}, edgeEls = [];
  svgEl.querySelectorAll('.dag-n').forEach(function (g) {{ nodeEls[g.getAttribute('data-id')] = g; }});
  svgEl.querySelectorAll('.dag-e').forEach(function (p) {{ edgeEls.push(p); }});
  var detail = document.getElementById('dag-detail');
  var selected = null;

  function walk(id, next) {{
    var seen = {{}}, q = [id];
    while (q.length) {{
      var x = q.shift();
      next(x).forEach(function (y) {{ if (!seen[y]) {{ seen[y] = true; q.push(y); }} }});
    }}
    delete seen[id];
    return seen;
  }}
  function paint(id) {{
    Object.keys(nodeEls).forEach(function (k) {{ nodeEls[k].classList.remove('is-sel', 'is-anc', 'is-desc'); }});
    edgeEls.forEach(function (e) {{ e.classList.remove('is-anc', 'is-desc'); }});
    if (!id) {{ fig.classList.remove('has-focus'); return; }}
    fig.classList.add('has-focus');
    var anc = walk(id, function (x) {{ return by[x].deps; }});
    var desc = walk(id, function (x) {{ return kids[x]; }});
    nodeEls[id].classList.add('is-sel');
    Object.keys(anc).forEach(function (k) {{ nodeEls[k].classList.add('is-anc'); }});
    Object.keys(desc).forEach(function (k) {{ nodeEls[k].classList.add('is-desc'); }});
    edgeEls.forEach(function (e) {{
      var f = e.getAttribute('data-from'), t = e.getAttribute('data-to');
      if ((t === id || desc[t]) && (f === id || desc[f])) e.classList.add('is-desc');
      if ((t === id || anc[t]) && (f === id || anc[f])) e.classList.add('is-anc');
    }});
  }}
  function refBtn(id) {{
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'dag-ref'; b.setAttribute('data-id', id); b.textContent = by[id].short;
    return b;
  }}
  function show(id) {{
    var n = by[id];
    detail.innerHTML = '';
    var h = document.createElement('h2');
    var badge = document.createElement('span'); badge.className = 'dag-badge tier-' + ({{'基礎': 'a', '進階': 'c', '專家': 'd'}})[n.tier]; badge.textContent = n.tier;
    h.appendChild(badge);
    h.appendChild(document.createTextNode(n.short));
    var sm = document.createElement('small'); sm.textContent = n.theme + ' · 第 ' + n.depth + ' 層 · ' + n.lecs.join('、');
    h.appendChild(sm);
    detail.appendChild(h);
    var claim = document.createElement('p'); claim.className = 'claim'; claim.textContent = n.name; detail.appendChild(claim);
    var why = document.createElement('p'); why.className = 'why'; why.textContent = n.why; detail.appendChild(why);
    var dl = document.createElement('dl');
    function row(label, fill) {{
      var dt = document.createElement('dt'); dt.textContent = label; dl.appendChild(dt);
      var dd = document.createElement('dd'); fill(dd); dl.appendChild(dd);
    }}
    row('前置', function (dd) {{
      if (!n.deps.length) {{ var s = document.createElement('span'); s.className = 'none'; s.textContent = '起點，不靠課程裡別的觀念'; dd.appendChild(s); return; }}
      n.deps.forEach(function (d) {{ dd.appendChild(refBtn(d)); }});
    }});
    row('延伸出去', function (dd) {{
      if (!kids[id].length) {{ var s = document.createElement('span'); s.className = 'none'; s.textContent = '沒有，是葉子'; dd.appendChild(s); return; }}
      kids[id].forEach(function (d) {{ dd.appendChild(refBtn(d)); }});
    }});
    row('出處', function (dd) {{
      n.src.forEach(function (s) {{ var a = document.createElement('a'); a.href = s.href; a.textContent = s.label; dd.appendChild(a); }});
    }});
    detail.appendChild(dl);
  }}
  function select(id, scroll) {{
    selected = id;
    paint(id);
    show(id);
    if (history.replaceState) history.replaceState(null, '', '#n-' + id);
    if (scroll) {{
      var g = nodeEls[id];
      var box = fig.querySelector('.scroll');
      var r = g.getBoundingClientRect(), fr = box.getBoundingClientRect();
      if (r.left < fr.left || r.right > fr.right) box.scrollLeft += (r.left + r.right) / 2 - (fr.left + fr.right) / 2;
      detail.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }});
    }}
  }}
  Object.keys(nodeEls).forEach(function (id) {{
    var g = nodeEls[id];
    g.addEventListener('mouseenter', function () {{ paint(id); }});
    g.addEventListener('mouseleave', function () {{ paint(selected); }});
    g.addEventListener('click', function () {{ select(id, false); detail.scrollIntoView({{ block: 'nearest', behavior: 'smooth' }}); }});
    g.addEventListener('keydown', function (ev) {{ if (ev.key === 'Enter' || ev.key === ' ') {{ ev.preventDefault(); select(id, false); detail.scrollIntoView({{ block: 'nearest' }}); }} }});
  }});
  document.addEventListener('click', function (ev) {{
    var b = ev.target.closest && ev.target.closest('.dag-ref');
    if (!b) return;
    var id = b.getAttribute('data-id');
    if (by[id]) {{ select(id, true); fig.scrollIntoView({{ block: 'start', behavior: 'smooth' }}); }}
  }});
  document.getElementById('dag-clear').addEventListener('click', function () {{
    selected = null; paint(null);
    detail.innerHTML = '<p class="hint">點圖上的一個觀念，這裡會顯示它的主張、為什麼從那些觀念延伸、出處章節，和從它延伸出去的觀念。</p>';
    if (history.replaceState) history.replaceState(null, '', location.pathname);
  }});

  // 篩選：難度 × 講次
  var tierBoxes = Array.prototype.slice.call(document.querySelectorAll('.dag-f-tier'));
  var lecSel = document.getElementById('dag-f-lec');
  function applyFilter() {{
    var tiers = {{}};
    tierBoxes.forEach(function (c) {{ tiers[c.value] = c.checked; }});
    var lec = lecSel.value;
    var on = {{}};
    data.nodes.forEach(function (n) {{
      on[n.id] = !!tiers[n.tier] && (!lec || n.lecs.indexOf(lec) >= 0);
      nodeEls[n.id].classList.toggle('is-off', !on[n.id]);
    }});
    edgeEls.forEach(function (e) {{
      e.classList.toggle('is-off', !(on[e.getAttribute('data-from')] && on[e.getAttribute('data-to')]));
    }});
  }}
  tierBoxes.forEach(function (c) {{ c.addEventListener('change', applyFilter); }});
  lecSel.addEventListener('change', applyFilter);

  var fit = document.getElementById('dag-fit');
  try {{ fit.checked = localStorage.getItem('cs2680.dag.fit') === '1'; }} catch (e) {{}}
  function applyFit() {{ fig.classList.toggle('fit', fit.checked); try {{ localStorage.setItem('cs2680.dag.fit', fit.checked ? '1' : '0'); }} catch (e) {{}} }}
  fit.addEventListener('change', applyFit); applyFit();

  var m = /^#n-(.+)$/.exec(location.hash);
  if (m && by[m[1]]) select(m[1], true);
}})();
</script>
<script src="app.js"></script>
</body>
</html>
"""
    return page


def main():
    check_only = "--check" in sys.argv
    d = json.loads(DATA.read_text(encoding="utf-8"))
    errs, warns, info = check(d)
    for w in warns:
        print("warn:", w)
    for e in errs:
        print("ERROR:", e)
    if errs:
        sys.exit(1)
    L = layout(d, info)
    A = analyze(d, info)
    print(f"OK: {len(d['nodes'])} nodes, {sum(len(n['deps']) for n in d['nodes'])} edges, depth 0–{L['D']}, "
          f"{len(A['merged'])} merged, {len(A['forward'])} forward edges; svg {L['W']}×{L['H']}")
    if check_only:
        return
    OUT.write_text(render(d, info, L, A), encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
