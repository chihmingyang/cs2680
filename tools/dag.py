#!/usr/bin/env python3
"""觀念 DAG：檢查 docs/dag.json，並產生 docs/dag.html（頁面是英文版，2026-11-08 James 要求）。

用法：
  python3 -I tools/dag.py --check     # 只檢查，不寫檔；verify.sh 會跑
  python3 -I tools/dag.py             # 檢查通過就重寫 docs/dag.html

檢查什麼（規則在 guide/DAG.md）：
  - id 唯一、deps 都存在、沒有自己依賴自己、沒有環
  - 難度沿著邊不會降：前置觀念的難度 ≤ 這個觀念（Basic ≤ Intermediate ≤ Expert）
  - kind 是 concept（心智模型）或 practice（決定規則／技巧／案例）；concept 不能依賴 practice
  - src 的錨點（lXX#iN、lXX#iN-M）在該頁真的存在
  - 每一堂核心觀念的每一章，都被某個節點的 src 蓋到，或列在 excluded（目錄章）
  - short 在方塊裡要能放進兩行（用字寬估算）→ 放不下是 ERROR
  - 同一個 src 出現在兩個節點、可以從別的邊推出來的多餘邊 → 只提示

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
TIER_ORDER = ["Basic", "Intermediate", "Expert"]
TIER_CLASS = {"Basic": "a", "Intermediate": "c", "Expert": "d"}
KINDS = ["concept", "practice"]

# 方塊幾何（px）。英文標籤比中文長，所以字 12px、方塊高 52、最多兩行。
# 欄距最多 142：9 欄時整張 1300px，比內容欄寬一點，用 .scroll 橫向捲；「Fit to width」可以縮進去。
NW, NH, FONT = 124, 52, 12
TEXT_W = NW - 16          # 左右各 8px 內距
PITCH_MAX = 142


# ---------- 讀頁面：章節 id 與標題 ----------

def page_chapters(lec):
    """回傳 ({chapter_id: title}, {section_id: lead-in}, 全部 id 的集合)。章只算核心觀念裡的 iN。"""
    p = SITE / f"{lec}.html"
    s = p.read_text(encoding="utf-8")
    ids = set(re.findall(r'\sid="([^"]+)"', s))
    seg = s[s.index('id="s-ideas"'):s.index('id="s-try"')]
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


# ---------- 字寬估算與換行 ----------

def char_w(c, size=FONT):
    """IBM Plex Sans 的近似字寬。CJK 全形；大寫、小寫、數字、標點分開估。"""
    o = ord(c)
    if o > 0x2E7F:
        return size
    if c == " ":
        return size * 0.26
    if c in "il.,:;'|!":
        return size * 0.28
    if c in "fjrt-()[]/":
        return size * 0.38
    if c.isupper():
        return size * 0.66
    if c.isdigit():
        return size * 0.58
    if c in "mw":
        return size * 0.86
    return size * 0.54


def text_w(s, size=FONT):
    return sum(char_w(c, size) for c in s)


def wrap(s, max_w=TEXT_W):
    """貪婪換行：依空格切字，一行放不下就換行。回傳行的清單（可能超過兩行，由檢查擋）。"""
    if text_w(s) <= max_w:
        return [s]
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w) if cur else w
        if text_w(cand) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


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
        if n.get("kind") not in KINDS:
            errs.append(f"{n['id']}：kind 要是 {KINDS}，現在是 {n.get('kind')}")
        if n.get("theme") not in theme_ids:
            errs.append(f"{n['id']}：theme {n.get('theme')} 不在 themes 裡")
        if not n.get("src"):
            errs.append(f"{n['id']}：src 是空的")
        for dep in n.get("deps", []):
            if dep == n["id"]:
                errs.append(f"{n['id']}：依賴自己")
            elif dep not in by:
                errs.append(f"{n['id']}：dep {dep} 不存在")
        lines = wrap(n.get("short", ""))
        if len(lines) > 2 or any(text_w(x) > TEXT_W for x in lines):
            errs.append(f"{n['id']}：short「{n['short']}」在方塊裡放不進兩行（估 {text_w(n['short']):.0f}px，一行 {TEXT_W}px），請縮短")
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

    # 難度單調；concept 不能依賴 practice
    for n in nodes:
        for dep in n["deps"]:
            if TIER_ORDER.index(by[dep]["tier"]) > TIER_ORDER.index(n["tier"]):
                errs.append(f"{n['id']}（{n['tier']}）依賴 {dep}（{by[dep]['tier']}）：前置的難度不能比較高")
            if n["kind"] == "concept" and by[dep]["kind"] == "practice":
                errs.append(f"{n['id']} 是 concept，卻依賴 practice {dep}：心智模型不能建立在技巧上，邊或 kind 有一個錯")

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

def layout(d, info):
    by = {n["id"]: n for n in d["nodes"]}
    depth = info["depth"]
    D = max(depth.values())
    themes = [t["id"] for t in d["themes"]]
    cells = {(t, k): [] for t in themes for k in range(D + 1)}
    for i in info["order"]:
        cells[(by[i]["theme"], depth[i])].append(i)
    W_TOTAL = 1300
    ML, MR, MT = 14, 14, 30
    pitch = max(NW + 14, min(PITCH_MAX, (W_TOTAL - ML - MR) // (D + 1)))  # 欄太多就讓整張變寬，不擠方塊
    GAP_Y, HEAD, PAD = 10, 24, 10
    pos = {}
    rows = []
    y = MT
    for t in themes:
        maxn = max(len(cells[(t, k)]) for k in range(D + 1))
        top = y
        inner_top = y + HEAD
        for k in range(D + 1):
            cell = cells[(t, k)]

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
    return {"pos": pos, "rows": rows, "D": D, "pitch": pitch, "W": W, "H": H, "ML": ML, "MT": MT}


def svg(d, info, L):
    by = {n["id"]: n for n in d["nodes"]}
    theme_name = {t["id"]: t["name"] for t in d["themes"]}
    pos, W, H = L["pos"], L["W"], L["H"]
    out = []
    out.append(f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" role="img" '
               f'aria-label="Concept DAG: {len(by)} concepts in {L["D"] + 1} layers by dependency depth (left to right) and {len(L["rows"])} theme rows; color is difficulty">')
    for idx, (t, top, hgt) in enumerate(L["rows"]):
        cls = "dag-lane" + (" alt" if idx % 2 else "")
        out.append(f'<rect class="{cls}" x="0" y="{top}" width="{W}" height="{hgt}"/>')
    for k in range(L["D"] + 1):
        x = L["ML"] + k * L["pitch"] + NW / 2
        label = "Layer 0 · roots" if k == 0 else f"Layer {k}"
        out.append(f'<text class="dag-col-t" x="{x}" y="{L["MT"] - 10}" text-anchor="middle">{label}</text>')
    # 邊。跨好幾欄的邊走正交線：往右到來源那一欄右邊空隙裡的 lx，垂直到目標那一列，再往右接上。
    # 同一欄的來源各用空隙裡不同的 x，免得全部疊成一條。
    gap = L["pitch"] - NW
    col_rank = defaultdict(int)
    lane_x = {}
    for i in sorted(pos, key=lambda i: (pos[i][0], pos[i][1])):
        k = col_rank[pos[i][0]]
        col_rank[pos[i][0]] += 1
        lane_x[i] = pos[i][0] + NW + 5 + (k % 5) * ((gap - 10) / 4)
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
                lx = lane_x[dep]
                r = 5
                if abs(by_ - ay) < 2 * r:
                    dpath = f"M{ax:.0f},{ay:.0f} L{bx:.0f},{by_:.0f}"
                else:
                    sg = 1 if by_ > ay else -1
                    dpath = (f"M{ax:.0f},{ay:.0f} L{lx - r:.0f},{ay:.0f} Q{lx:.0f},{ay:.0f} {lx:.0f},{ay + sg * r:.0f} "
                             f"L{lx:.0f},{by_ - sg * r:.0f} Q{lx:.0f},{by_:.0f} {lx + r:.0f},{by_:.0f} L{bx:.0f},{by_:.0f}")
            out.append(f'<path class="dag-e" data-from="{dep}" data-to="{n["id"]}" d="{dpath}"/>')
    out.append("</g>")
    out.append('<g class="dag-nodes">')
    for n in d["nodes"]:
        x, y = pos[n["id"]]
        lec = n["src"][0].split("#")[0]
        tag = "L" + str(int(lec[1:]))
        lines = wrap(n["short"])
        label = html.escape(n["short"])
        out.append(f'<g class="dag-n tier-{TIER_CLASS[n["tier"]]} kind-{n["kind"]}" id="n-{n["id"]}" data-id="{n["id"]}" tabindex="0" role="button" '
                   f'aria-label="{label}, {n["kind"]}, {n["tier"]}, {tag}">')
        out.append(f'<rect class="dag-box" x="{x}" y="{y}" width="{NW}" height="{NH}" rx="5"/>')
        out.append(f'<rect class="dag-tier" x="{x}" y="{y}" width="4" height="{NH}" rx="2"/>')
        out.append(f'<text class="dag-tag" x="{x + NW - 6}" y="{y + NH - 5}" text-anchor="end">{tag}</text>')
        if len(lines) == 1:
            out.append(f'<text class="dag-t" x="{x + 10}" y="{y + 22}">{html.escape(lines[0])}</text>')
        else:
            out.append(f'<text class="dag-t" x="{x + 10}" y="{y + 19}">{html.escape(lines[0])}</text>')
            out.append(f'<text class="dag-t" x="{x + 10}" y="{y + 34}">{html.escape(lines[1])}</text>')
        out.append("</g>")
    out.append("</g>")
    # 泳道標題最後畫，壓在邊的上面；halo 用泳道自己的底色
    for idx, (t, top, hgt) in enumerate(L["rows"]):
        cls = "dag-lane-t" + (" alt" if idx % 2 else "")
        out.append(f'<text class="{cls}" x="{L["ML"]}" y="{top + 16}">{html.escape(theme_name[t])}</text>')
    out.append("</svg>")
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
        kinds = {k: sum(1 for n in ns if n["kind"] == k) for k in KINDS}
        ds = [depth[n["id"]] for n in ns]
        fw = sum(1 for n, dep in forward if n["src"][0].startswith(lec + "#"))
        per_lec[lec] = {"n": len(ns), "tiers": tiers, "kinds": kinds, "dmin": min(ds) if ds else None, "dmax": max(ds) if ds else None, "fw": fw}
    tier_total = {t: sum(1 for n in d["nodes"] if n["tier"] == t) for t in TIER_ORDER}
    kind_total = {k: sum(1 for n in d["nodes"] if n["kind"] == k) for k in KINDS}
    roots = [n for n in d["nodes"] if not n["deps"]]
    return {"merged": merged, "forward": forward, "per_lec": per_lec, "tier_total": tier_total, "kind_total": kind_total, "roots": roots}


# ---------- 頁面 ----------

def esc(s):
    return html.escape(s, quote=True)


def src_ref(s):
    """l04#i6-1 → ('l04.html#i6-1', 'L4 ch.6')"""
    lec, anchor = s.split("#")
    ch = anchor.split("-")[0]
    return f"{lec}.html#{anchor}", f"L{int(lec[1:])} ch.{ch[1:]}"


def src_title(s, pages):
    """出處的中文章名（頁面是中文的，所以照抄，讓讀者找得到那一章）。"""
    lec, anchor = s.split("#")
    ch = anchor.split("-")[0]
    chapters, secs, _ = pages[lec]
    t = chapters.get(ch, "")
    if "-" in anchor and anchor in secs:
        t = f"{t}（{secs[anchor]}）"
    return t


def tier_badge(t):
    return f'<span class="dag-badge tier-{TIER_CLASS[t]}">{t}</span>'


def ref_btn(n, cls=""):
    return f'<button type="button" class="dag-ref{(" " + cls) if cls else ""}" data-id="{n["id"]}">{esc(n["short"])}</button>'


def render(d, info, L, A):
    by = {n["id"]: n for n in d["nodes"]}
    pages = info["pages"]
    depth = info["depth"]
    theme_name = {t["id"]: t["name"] for t in d["themes"]}
    N = len(d["nodes"])
    E = sum(len(n["deps"]) for n in d["nodes"])
    tt = A["tier_total"]

    js_nodes = []
    for n in d["nodes"]:
        js_nodes.append({
            "id": n["id"], "name": n["name"], "short": n["short"], "tier": n["tier"], "kind": n["kind"],
            "theme": theme_name[n["theme"]], "deps": n["deps"], "why": n["why"],
            "depth": depth[n["id"]],
            "src": [{"href": src_ref(s)[0], "ref": src_ref(s)[1], "title": src_title(s, pages)} for s in n["src"]],
            "lecs": sorted({"L" + str(lec_no(s)) for s in n["src"]}, key=lambda x: int(x[1:])),
        })
    data_json = json.dumps({"nodes": js_nodes}, ensure_ascii=False).replace("</", "<\\/")

    # 講次 × 難度表
    rows = []
    for lec, r in A["per_lec"].items():
        t = r["tiers"]
        rows.append(
            f'<tr><th scope="row"><a href="{lec}.html">L{int(lec[1:])}</a> {esc(d["lectures"][lec])}</th>'
            f'<td>{r["kinds"]["concept"]} / {r["kinds"]["practice"]}</td><td>{t["Basic"]}</td><td>{t["Intermediate"]}</td><td>{t["Expert"]}</td>'
            f'<td>{r["dmin"]}–{r["dmax"]}</td><td>{r["fw"] or "—"}</td></tr>')
    kt = A["kind_total"]
    rows.append(f'<tr class="dag-sum"><th scope="row">Total</th><td>{kt["concept"]} / {kt["practice"]}</td><td>{tt["Basic"]}</td><td>{tt["Intermediate"]}</td><td>{tt["Expert"]}</td><td>0–{L["D"]}</td><td>{len(A["forward"])}</td></tr>')
    table = ("<div class=\"table-wrap\"><table class=\"dag-table\">"
             "<thead><tr><th>Lecture</th><th>Concepts / practices</th><th>Basic</th><th>Intermediate</th><th>Expert</th><th>Depth range</th><th>Prerequisites taught later</th></tr></thead>"
             f"<tbody>{''.join(rows)}</tbody></table></div>")

    # 散在兩堂
    merged_li = []
    for n in A["merged"]:
        srcs = ", ".join(f'<a href="{src_ref(s)[0]}" title="{esc(src_title(s, pages))}">{src_ref(s)[1]}</a>' for s in n["src"])
        merged_li.append(f'<li>{ref_btn(n)}: {srcs}</li>')

    # 前置在後面的講次
    fw_by_lec = defaultdict(list)
    for n, dep in A["forward"]:
        fw_by_lec[lec_no(n["src"][0])].append((n, dep))
    fw_blocks = []
    for lec in sorted(fw_by_lec):
        items = []
        for n, dep in fw_by_lec[lec]:
            items.append(f'<li>{ref_btn(n)} needs {ref_btn(dep)}<small> (first appears in L{first_lec(dep)})</small></li>')
        fw_blocks.append(f'<li><b>L{lec} {esc(d["lectures"][f"l{lec:02d}"])}</b><ul>{"".join(items)}</ul></li>')

    # 依賴順序的閱讀清單
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
            deps = ", ".join(ref_btn(by[dep]) for dep in n["deps"])
            href, ref = src_ref(n["src"][0])
            lis.append(
                f'<li id="o-{i}" class="kind-{n["kind"]}">{tier_badge(n["tier"])}<span class="dag-o-main">{ref_btn(n, "strong")}'
                f'<span class="dag-o-name">{esc(n["name"])}</span>'
                f'<span class="dag-o-meta"><a href="{href}" title="{esc(src_title(n["src"][0], pages))}">{ref}</a>'
                + (f' · needs: {deps}' if deps else " · root") + f' · {n["kind"]}' + "</span></span></li>")
        title = "Layer 0: roots — depend on nothing else in the course" if k == 0 else f"Layer {k}: all prerequisites are in layers 0–{k - 1}"
        layer_blocks.append(f'<li class="dag-layer"><h3>{title}<small>{len(ids)} concepts</small></h3><ol class="dag-olist">{"".join(lis)}</ol></li>')

    roots_txt = ", ".join(ref_btn(n) for n in A["roots"])
    tiers_desc = "".join(f"<li>{tier_badge(t)}<span>{esc(d['tiers'][t])}. {tt[t]} concepts.</span></li>" for t in TIER_ORDER)
    lec_opts = "".join(f'<option value="L{int(l[1:])}">L{int(l[1:])} {esc(t)}</option>' for l, t in sorted(d["lectures"].items()))
    excluded_li = "".join(f'<li><a href="{src_ref(e["src"])[0]}" title="{esc(src_title(e["src"], pages))}">{src_ref(e["src"])[1]}</a>: {esc(e["why"])}</li>' for e in d.get("excluded", []))
    hint = "Click a concept in the figure. This panel shows its claim, why it builds on its prerequisites, where it is taught, and what builds on it."

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Concept DAG · CS2680</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap">
<link rel="stylesheet" href="styles.css?v=20261110b">
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
.dag-bar select {{ font: inherit; font-size: .875rem; padding: .15rem .4rem; border: 1px solid var(--rule); border-radius: var(--radius); background: var(--sheet); color: var(--ink); max-width: 22rem; }}
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
.dag-lane-t {{ fill: var(--ink-soft); font-family: var(--font-display); font-weight: 600; font-size: 12px; letter-spacing: .02em; paint-order: stroke; stroke: var(--sheet); stroke-width: 4px; stroke-linejoin: round; }}
.dag-lane-t.alt {{ stroke: var(--dg-panel); }}
.dag-col-t {{ fill: var(--ink-soft); font-family: var(--font-mono); font-size: 10.5px; }}
.dag-e {{ fill: none; stroke: var(--dg-link); stroke-width: 1.2; opacity: .45; transition: opacity .12s, stroke-width .12s; }}
.dag-n {{ cursor: pointer; outline: none; }}
.dag-box {{ fill: var(--sheet); stroke: var(--rule); stroke-width: 1; transition: opacity .12s; }}
.dag-n.tier-a .dag-box {{ fill: var(--dg-a); }}
.dag-n.tier-c .dag-box {{ fill: var(--dg-c); }}
.dag-n.tier-d .dag-box {{ fill: var(--dg-d); }}
.dag-n.kind-practice .dag-box {{ fill-opacity: .38; stroke: var(--ink-soft); stroke-dasharray: 2 2.5; }}
.dag-n.kind-practice .dag-t {{ fill: var(--ink); }}
.dag-tier {{ fill: var(--ink-soft); opacity: 0; }}
.dag-n.tier-c .dag-tier {{ opacity: .35; }}
.dag-n.tier-d .dag-tier {{ opacity: .8; }}
.dag-t {{ fill: var(--ink); font-family: var(--font-body); font-size: {FONT}px; pointer-events: none; }}
.dag-tag {{ fill: var(--ink-soft); font-family: var(--font-mono); font-size: 9.5px; pointer-events: none; }}
.dag-n:hover .dag-box, .dag-n:focus-visible .dag-box {{ stroke: var(--signal); stroke-width: 1.6; }}
.has-focus .dag-n:not(.is-sel):not(.is-anc):not(.is-desc) {{ opacity: .22; }}
.has-focus .dag-e:not(.is-anc):not(.is-desc) {{ opacity: .06; }}
.dag-n.is-sel .dag-box {{ stroke: var(--key); stroke-width: 2.2; }}
.dag-n.is-anc .dag-box {{ stroke: var(--signal); stroke-width: 1.8; }}
.dag-n.is-desc .dag-box {{ stroke: var(--caution); stroke-width: 1.8; stroke-dasharray: 4 3; }}
.dag-e.is-anc {{ stroke: var(--signal); opacity: .95; stroke-width: 1.8; }}
.dag-e.is-desc {{ stroke: var(--caution); opacity: .9; stroke-width: 1.6; stroke-dasharray: 4 3; }}
.dag-n.is-off {{ opacity: .15; }}
.dag-e.is-off {{ opacity: .04; }}
.dag-legend {{ display: flex; flex-wrap: wrap; gap: .4rem 1.25rem; margin: .5rem 0 0; padding: 0; list-style: none; font-size: .8125rem; color: var(--ink-soft); }}
.dag-legend li {{ display: inline-flex; align-items: center; gap: .4rem; }}
.dag-legend i {{ display: inline-block; width: 1.4rem; height: 0; border-top: 2px solid var(--signal); }}
.dag-legend i.desc {{ border-top-style: dashed; border-color: var(--caution); }}
.dag-legend i.sel {{ width: .9rem; height: .9rem; border: 2px solid var(--key); border-radius: 3px; }}
.dag-legend i.box {{ width: 1.1rem; height: .8rem; border: 1px solid var(--rule); border-radius: 3px; background: var(--dg-c); }}
.dag-legend i.box.practice {{ border: 1px dotted var(--ink-soft); background: color-mix(in srgb, var(--dg-c) 38%, var(--sheet)); }}
.dag-detail {{ margin-top: 1rem; border: 1px solid var(--rule); border-left: 4px solid var(--signal); border-radius: var(--radius); background: var(--sheet); padding: 1rem 1.1rem; display: grid; gap: .6rem; max-width: 52rem; }}
.dag-detail .hint {{ color: var(--ink-soft); margin: 0; }}
.dag-detail h2 {{ margin: 0; font-size: 1.15rem; font-family: var(--font-display); display: flex; flex-wrap: wrap; gap: .5rem .6rem; align-items: center; }}
.dag-detail h2 small {{ font-family: var(--font-mono); font-weight: 400; font-size: .75rem; color: var(--ink-soft); }}
.dag-detail .claim {{ margin: 0; font-weight: 500; }}
.dag-detail .why {{ margin: 0; color: var(--ink); }}
.dag-detail dl {{ margin: 0; display: grid; grid-template-columns: 6.5rem minmax(0, 1fr); gap: .35rem .8rem; font-size: .9rem; }}
.dag-detail dt {{ color: var(--ink-soft); }}
.dag-detail dd {{ margin: 0; display: flex; flex-wrap: wrap; gap: .3rem .6rem; align-items: baseline; }}
.dag-detail dd .none {{ color: var(--ink-soft); }}
.dag-detail dd a small {{ color: var(--ink-soft); font-size: .8em; }}
@media (max-width: 520px) {{ .dag-detail dl {{ grid-template-columns: 1fr; gap: .15rem; }} .dag-detail dt {{ margin-top: .3rem; }} }}
.dag-ref {{ font: inherit; padding: 0 .1rem; border: 0; border-bottom: 1px dashed var(--signal); background: none; color: var(--signal); cursor: pointer; text-align: left; }}
.dag-ref:hover {{ border-bottom-style: solid; }}
.dag-ref.strong {{ font-weight: 600; color: var(--ink); border-bottom-color: var(--ink-soft); }}
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
.dag-olist > li {{ display: grid; grid-template-columns: 6rem minmax(0, 1fr); gap: .25rem .7rem; align-items: start; padding: .35rem 0; border-bottom: 1px solid var(--rule); }}
.dag-olist .dag-badge {{ justify-self: start; margin-top: .15rem; }}
.dag-o-main {{ display: grid; gap: .15rem; min-width: 0; }}
.dag-o-main > .dag-ref {{ justify-self: start; }}
.dag-o-name {{ font-size: .9rem; color: var(--ink); }}
.dag-o-meta {{ font-size: .8125rem; color: var(--ink-soft); }}
@media (max-width: 520px) {{ .dag-olist > li {{ grid-template-columns: 1fr; }} }}
.dag-rules {{ margin: 0; padding-left: 1.2rem; display: grid; gap: .35rem; }}
.dag-rules ul {{ margin: .3rem 0 0; padding-left: 1.2rem; display: grid; gap: .2rem; }}
.dag-tiers {{ list-style: none; margin: 0; padding: 0; display: grid; gap: .4rem; }}
.dag-tiers li {{ display: grid; grid-template-columns: 6rem minmax(0, 1fr); gap: .6rem; align-items: start; }}
.dag-tiers .dag-badge {{ margin-top: .2rem; justify-self: start; }}
</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-inner gutter">
    <a class="brand" href="index.html">CS2680 <span>觀念導讀</span></a>
    <nav class="lecnav" aria-label="Back to the course"><a href="index.html">← Course home</a><a href="#rules-h">How this was built</a></nav>
  </div>
</header>

<main class="page gutter dag-page">
  <header class="dag-head">
    <p class="eyebrow">Course map · Concept DAG · draft {d["updated"]}</p>
    <h1>Concept DAG: where each concept comes from</h1>
    <p>The course is cut into one-hour lecture decks, but understanding does not come in one-hour pieces. This figure starts from the other end: what mental models does a reader have to hold, and which one must be in place before the next makes sense? It has <b>{A["kind_total"]["concept"]} concepts</b> (mental models that stay true across products), <b>{A["kind_total"]["practice"]} practices</b> (decision rules and techniques that apply them) and <b>{E} “understand this first” edges</b>. Everything grows from {len(A["roots"])} root{"s" if len(A["roots"]) > 1 else ""}: {roots_txt}.</p>
    <p>How to read it: <b>left to right is dependency depth</b> (everything in layer k needs only layers 0 to k−1, so reading left to right is a valid order); <b>each row is a theme</b>; <b>color is difficulty</b>; <b>solid boxes are concepts, pale dotted boxes are practices</b>. Click a box to see what it builds on (to the left) and what builds on it (to the right). Untick “Show practices” to see only the skeleton of mental models. Pick a lecture to see where its chapters land.</p>
  </header>

  <div class="dag-bar" role="group" aria-label="Filters">
    <fieldset><legend>Difficulty</legend>
      <label><input type="checkbox" class="dag-f-tier" value="Basic" checked> {tier_badge("Basic")}</label>
      <label><input type="checkbox" class="dag-f-tier" value="Intermediate" checked> {tier_badge("Intermediate")}</label>
      <label><input type="checkbox" class="dag-f-tier" value="Expert" checked> {tier_badge("Expert")}</label>
    </fieldset>
    <label>Lecture <select id="dag-f-lec"><option value="">all</option>{lec_opts}</select></label>
    <label><input type="checkbox" id="dag-f-practice" checked> Show practices</label>
    <span class="spacer"></span>
    <label><input type="checkbox" id="dag-fit" checked> Fit to width</label>
    <button type="button" id="dag-clear">Clear selection</button>
  </div>

  <figure class="diagram dag-fig" id="dag-fig">
    <div class="scroll">{svg(d, info, L)}</div>
    <ul class="dag-legend" aria-label="Legend">
      <li>{tier_badge("Basic")} {tier_badge("Intermediate")} {tier_badge("Expert")} difficulty</li>
      <li><i class="box"></i> concept (mental model) · <i class="box practice"></i> practice (rule or technique)</li>
      <li><i class="sel"></i> selected</li>
      <li><i></i> its prerequisites (to the left)</li>
      <li><i class="desc"></i> what builds on it (to the right)</li>
      <li>The L-number in a box is the lecture that covers the concept most fully; concepts split across two lectures are listed below the figure.</li>
    </ul>
    <figcaption>Each box is one concept or practice, shown by its short name; click it for the one-sentence claim and why it builds on its prerequisites. An edge A → B means “understand A before reading B”. Only direct prerequisites are drawn: an edge that follows from other edges is omitted. A concept never depends on a practice, so the solid boxes alone form a complete map. Layout: x is the length of the longest dependency path, y is the theme; several boxes in one cell stack vertically.</figcaption>
  </figure>

  <aside class="dag-detail" id="dag-detail" aria-live="polite">
    <p class="hint">{hint}</p>
  </aside>

  <section class="dag-sec" aria-labelledby="gap-h">
    <h2 id="gap-h">Where lectures and concepts disagree</h2>
    <p>The three findings below are computed from the figure, not written by hand. They are the places where “one hour per lecture” and “what depends on what” do not line up.</p>
    <h3>One concept split across two lectures<small>{len(A["merged"])} concepts</small></h3>
    <p>The same concept is taught half in one lecture and half in another, for example once as a workload property and once as a mechanism. As concepts they are a single node.</p>
    <ul class="dag-fw">{"".join(merged_li)}</ul>
    <h3>Prerequisites taught in a later lecture<small>{len(A["forward"])} edges</small></h3>
    <p>Reading in lecture order, you reach this concept before its prerequisite has appeared at all, not even in passing (a prerequisite mentioned briefly in an earlier lecture does not count). The site already changed the recommended order of Part I to L2 → L4 → L3 → L5, which fixed several of these; the rest are bridged by notes in the articles.</p>
    <ul class="dag-fw">{"".join(fw_blocks)}</ul>
    <h3>Difficulty mix and depth range per lecture</h3>
    <p>Depth is the layer in the figure. A wide depth range means a lecture teaches roots and far-downstream ideas in the same hour; a high count in the last column means reading that lecture in sequence gets stuck more often. A concept is counted under the lecture that covers it most fully.</p>
    {table}
  </section>

  <section class="dag-sec" aria-labelledby="order-h">
    <h2 id="order-h">Reading order by dependency</h2>
    <p>The figure flattened into a list: one group per layer, ordered by theme within a layer. Every prerequisite of a layer is in the layers before it, so following this list never hits an unexplained concept. This is a draft order for a DAG-shaped version of the course, not a final split into lectures.</p>
    <ol class="dag-layers">{"".join(layer_blocks)}</ol>
  </section>

  <section class="dag-sec" aria-labelledby="rules-h">
    <h2 id="rules-h">How this figure was built</h2>
    <h3>What a node is</h3>
    <ul class="dag-rules">
      <li>The unit is what a reader holds in their head, not what a lecture covers. A <b>concept</b> is a mental model: {esc(d["kinds"]["concept"])}</li>
      <li>A <b>practice</b> applies concepts: {esc(d["kinds"]["practice"])}</li>
      <li>The test for a concept: state it without naming a product, a lecture or this course. If the sentence only works with “Claude Code” or “CLAUDE.md” in it, the node is the general idea and the product is its example (CLAUDE.md and auto memory are one concept, persistent text; skills and offloading are one concept, keep it out until needed; subagents and multi-agent systems are one concept, agents share only text).</li>
      <li>One node, one claim: it can be written as a single sentence, it has its own prerequisites, and removing it makes some later node unreadable. Worked cases from the lectures (Caveman, Superpowers, dsh-superagent) are not nodes; they are examples inside the node they illustrate.</li>
      <li>Every chapter of every lecture article maps onto at least one node, so nothing taught is lost. Catalog chapters (lookup lists) are not concepts and stay out:{excluded_li and "<ul>" + excluded_li + "</ul>"}</li>
    </ul>
    <h3>What an edge is</h3>
    <ul class="dag-rules">
      <li>A → B means “understand A before reading B”. B's “why” sentence must say what becomes unreadable without A.</li>
      <li>Only direct prerequisites are drawn. If A → C follows from A → B → C, it is not drawn.</li>
      <li>Edges look only at ideas, never at lectures. Prerequisites that live in a later lecture are therefore expected; they are exactly the gap this figure is meant to expose.</li>
      <li>A concept never depends on a practice. If it seems to, either the edge points the wrong way or the node is misclassified. <code>tools/dag.py --check</code> rejects it.</li>
    </ul>
    <h3>How difficulty is assigned</h3>
    <ul class="dag-tiers">{tiers_desc}</ul>
    <p>Difficulty is a property of the concept, not of its depth in the figure. One hard rule: a prerequisite can never be harder than the concept that depends on it (Basic ≤ Intermediate ≤ Expert). A violation means either the edge or the difficulty is wrong, and <code>tools/dag.py --check</code> rejects it.</p>
    <p>Data: <a href="https://github.com/chihmingyang/cs2680/blob/main/docs/dag.json" target="_blank" rel="noopener">docs/dag.json</a>. Rules in full (Chinese): <a href="https://github.com/chihmingyang/cs2680/blob/main/guide/DAG.md" target="_blank" rel="noopener">guide/DAG.md</a>. This page is generated from the data by <code>tools/dag.py</code>; edit the data and rerun.</p>
  </section>

  <p class="fineprint">This figure is the study group's reading of the course. The claims, edges and difficulty levels are our judgment, not the instructor's. The original slides and course content are © Juncheng Yang and Harvard CS2680. Chapter links go to the group's Chinese-language lecture articles.</p>
</main>

<script type="application/json" id="dag-data">{data_json}</script>
<script>
(function () {{
  var data = JSON.parse(document.getElementById('dag-data').textContent);
  var HINT = {json.dumps(hint)};
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
    var badge = document.createElement('span'); badge.className = 'dag-badge tier-' + ({{'Basic': 'a', 'Intermediate': 'c', 'Expert': 'd'}})[n.tier]; badge.textContent = n.tier;
    h.appendChild(badge);
    h.appendChild(document.createTextNode(n.short));
    var sm = document.createElement('small'); sm.textContent = n.kind + ' · ' + n.theme + ' · layer ' + n.depth + ' · ' + n.lecs.join(', ');
    h.appendChild(sm);
    detail.appendChild(h);
    var claim = document.createElement('p'); claim.className = 'claim'; claim.textContent = n.name; detail.appendChild(claim);
    var why = document.createElement('p'); why.className = 'why'; why.textContent = n.why; detail.appendChild(why);
    var dl = document.createElement('dl');
    function row(label, fill) {{
      var dt = document.createElement('dt'); dt.textContent = label; dl.appendChild(dt);
      var dd = document.createElement('dd'); fill(dd); dl.appendChild(dd);
    }}
    row('Needs first', function (dd) {{
      if (!n.deps.length) {{ var s = document.createElement('span'); s.className = 'none'; s.textContent = 'nothing — this is a root'; dd.appendChild(s); return; }}
      n.deps.forEach(function (d) {{ dd.appendChild(refBtn(d)); }});
    }});
    row('Builds into', function (dd) {{
      if (!kids[id].length) {{ var s = document.createElement('span'); s.className = 'none'; s.textContent = 'nothing — this is a leaf'; dd.appendChild(s); return; }}
      kids[id].forEach(function (d) {{ dd.appendChild(refBtn(d)); }});
    }});
    row('Taught in', function (dd) {{
      n.src.forEach(function (s) {{
        var a = document.createElement('a'); a.href = s.href; a.textContent = s.ref;
        if (s.title) {{ a.appendChild(document.createTextNode(' ')); var t = document.createElement('small'); t.textContent = s.title; a.appendChild(t); }}
        dd.appendChild(a);
      }});
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
    detail.innerHTML = '';
    var p = document.createElement('p'); p.className = 'hint'; p.textContent = HINT; detail.appendChild(p);
    if (history.replaceState) history.replaceState(null, '', location.pathname);
  }});

  var tierBoxes = Array.prototype.slice.call(document.querySelectorAll('.dag-f-tier'));
  var lecSel = document.getElementById('dag-f-lec');
  var practiceBox = document.getElementById('dag-f-practice');
  function applyFilter() {{
    var tiers = {{}};
    tierBoxes.forEach(function (c) {{ tiers[c.value] = c.checked; }});
    var lec = lecSel.value;
    var on = {{}};
    data.nodes.forEach(function (n) {{
      on[n.id] = !!tiers[n.tier] && (!lec || n.lecs.indexOf(lec) >= 0) && (practiceBox.checked || n.kind === 'concept');
      nodeEls[n.id].classList.toggle('is-off', !on[n.id]);
    }});
    edgeEls.forEach(function (e) {{
      e.classList.toggle('is-off', !(on[e.getAttribute('data-from')] && on[e.getAttribute('data-to')]));
    }});
  }}
  tierBoxes.forEach(function (c) {{ c.addEventListener('change', applyFilter); }});
  lecSel.addEventListener('change', applyFilter);
  practiceBox.addEventListener('change', applyFilter);

  var fit = document.getElementById('dag-fit');
  fit.checked = true;  // 預設縮到內容欄寬（約 0.9 倍）；取消就 1:1 橫向捲
  try {{ var fv = localStorage.getItem('cs2680.dag.fit'); if (fv !== null) fit.checked = fv === '1'; }} catch (e) {{}}
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
