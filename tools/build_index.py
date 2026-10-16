#!/usr/bin/env python3
"""Build site/index.html from the lecture table and the finished lecture pages.

Usage: python3 -I build_index.py
A lecture links to its page only when site/lXX.html exists; otherwise it is
listed as 撰寫中. Reading time comes from each page's .read-time span.
"""
import html
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"
FONTS = ("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
         "&family=IBM+Plex+Sans+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600"
         "&family=Noto+Sans+TC:wght@400;500;700&display=swap")

LECTURES = [
    ("l01", "01", "09-02", "課程總覽與 AI 系統", "Course overview and logistics", "1_intro.pdf", 52,
     "AI 系統和傳統系統差在哪裡;為什麼 agent 是一個系統問題;這門課要回答的 9 個問題。"),
    ("l02", "02", "09-09", "Claude Code 怎麼運作", "Agents use I: How Claude Code Works", "2_agent_use_1.pdf", 60,
     "Agent loop 與 harness;CLAUDE.md 與 auto memory;skill、MCP、hook、plugin 各管什麼;permission mode。"),
    ("l03", "03", "09-14", "用多個 agent 放大產能", "Agents use II: 100x Engineer with Multi-agents", "3_agent_use_2.pdf", 83,
     "Superpowers 與 Caveman 兩個 plugin 案例;worktree、subagent、agent team;Programming 3.0 的不確定性。"),
    ("l04", "04", "09-16", "Context 管理與 tool 設計", "Agents design I: context management and tool design", "4_agent_design_1.pdf", 58,
     "ReAct loop;搜尋與編輯 tool 的取捨;prompt engineering 技巧;context 的四種管理策略與五種失敗。"),
    ("l05", "05", "09-23", "Multi-agent 架構與溝通", "Agents design II: multi-agent architecture, coordination, and communication", "5_agent_design_2.pdf", 49,
     "八種 multi-agent 架構;任務怎麼拆;agent 之間的溝通就是分散式系統問題;A2A 與 MCP。"),
    ("l06", "06", "09-28", "Agent memory 與可靠性", "Agents design III: agent memory and reliability", "6_agent_design_3.pdf", 33,
     "Memory 的寫入、組織、檢索、遺忘;錯誤會累積;五種失敗來源與對應的設計。"),
    ("l07", "07", "09-30", "Agent 評估", "Agent design IV: agent evaluation", "7_agent_design_4.pdf", 38,
     "從 GLUE 到 Terminal-Bench;pass@k 與 pass^k;資料洩漏、單輪評估、成本與延遲的盲點。"),
    ("l08", "08", "10-07", "成本、速度與 harness 架構", "Advanced agent design I: Cost and performance", "8_agent_design_5.pdf", 61,
     "Agent 成本公式與降本槓桿;critical path 與 speculative actions;三種 harness 架構;附 Assignment 3 說明。"),
]

UPCOMING = [
    ("10-05", "Guest lecture: Developing and Evaluating Agents in Enterprise Setting (Snowflake)", "沒有公開 slides"),
    ("10-14", "Advanced agent design II: agent safety, self-evolving harness", "學生主講"),
    ("10-19", "Efficient LLM serving: basics I", "Part II"),
    ("10-21", "Efficient LLM serving: basics II", "Part II"),
    ("10-28", "Efficient LLM serving: speculative decoding", "Part II"),
    ("11-02", "Efficient agentic systems: scheduling and prefix caching", "Part II"),
    ("11-04", "Efficient LLM serving: pruning and quantization", "Part II"),
    ("11-09", "Guest lecture: Why Infrastructure sets the pace of AI (Meta)", "Part II"),
    ("11-11", "Efficient LLM serving: GPU and kernels", "Part II"),
    ("11-16", "Efficient LLM serving: KV-cache optimization and model architectures", "學生主講"),
    ("11-23", "Efficient agentic system: routing and load balancing", "Part II"),
    ("11-30", "Efficient agentic systems: others", "Part II"),
]


# Course map: (layer, gloss, chips, note). A chip is (label, lecture, anchor).
# Anchors come from tools/add_anchors.py: i<n> core idea, x<n> extended idea, t<n> term.
MAP = [
    ("Application / User", "人怎麼使用 agent", [
        ("用 Claude Code", "l02", "s-arch"),
        ("多 agent 工作流程", "l03", "i3"),
        ("Programming 3.0", "l03", "i5"),
    ], None),
    ("Agent / Harness", "agent 本身怎麼設計", [
        ("Agent loop", "l04", "i1"),
        ("Tool 設計", "l04", "i2"),
        ("Context 管理", "l04", "i5"),
        ("CLAUDE.md", "l02", "i2"),
        ("Memory 設計", "l06", "i1"),
        ("Skill、MCP、hook", "l02", "i3"),
        ("Multi-agent 架構", "l05", "i2"),
        ("可靠性", "l06", "i5"),
        ("評估", "l07", "i3"),
        ("成本", "l08", "i1"),
        ("速度", "l08", "i5"),
        ("Harness 架構", "l08", "x3"),
    ], None),
    ("Model", "model 的大小與結構", [
        ("架構演進得很快", "l01", "i2"),
    ], "待公開：11/04 pruning 與 quantization · 11/16 KV cache 與 model 架構"),
    ("Serving System", "把 model 跑成服務", [
        ("Prefill 與 decode", "l01", "t1"),
        ("Prefix cache 與單價", "l08", "t2"),
    ], "待公開：10/19–10/21 serving 基礎 · 10/28 speculative decoding · 11/02 scheduling 與 prefix caching · 11/23 routing"),
    ("Runtime / Kernels", "GPU 上實際執行的程式", [
        ("浮點數的不確定性", "l01", "t2"),
    ], "待公開：11/11 GPU 與 kernel"),
    ("Hardware", "GPU、CPU、記憶體、網路", [
        ("故障率與耗電", "l01", "t4"),
    ], "待公開：11/09 客座演講(Meta):infrastructure"),
]


def map_rows():
    out = ['    <ol class="stack">']
    for layer, gloss, chips, note in MAP:
        out.append('      <li class="layer">')
        out.append(f'        <div class="lname"><b>{html.escape(layer)}</b><small>{html.escape(gloss)}</small></div>')
        out.append('        <div class="ltopics">')
        for label, key, anchor in chips:
            no = "L" + str(int(key[1:]))
            if not is_ready(key):
                out.append(f'          <span class="chip off">{html.escape(label)}<b>{no}</b></span>')
                continue
            page = (SITE / f"{key}.html").read_text(encoding="utf-8")
            href = f"{key}.html"
            if anchor:
                if f'id="{anchor}"' in page:
                    href += "#" + anchor
                else:
                    print(f"WARNING: {key}.html has no #{anchor}; chip {label!r} links to the page top")
            out.append(f'          <a class="chip" href="{href}">{html.escape(label)}<b>{no}</b></a>')
        if note:
            out.append(f'          <span class="soon">{html.escape(note)}</span>')
        out.append('        </div>')
        out.append('      </li>')
    out.append('    </ol>')
    return "\n".join(out)


def read_time(path):
    m = re.search(r'<span class="read-time">([^<]*)</span>', path.read_text(encoding="utf-8"))
    return m.group(1).replace("約 ", "約 ").replace("分鐘", "分") if m else ""


def lecture_rows():
    rows = []
    for key, no, date, zh, en, pdf, pages, summary in LECTURES:
        page = SITE / f"{key}.html"
        ready = is_ready(key)
        rt = read_time(page) if ready else ""
        side = [f"<span>{pages} 頁</span>"]
        if ready:
            side.append(f"<span>{html.escape(rt)}</span>")
            if 'data-format="article"' not in page.read_text(encoding="utf-8"):
                side.append('<span class="pill muted">舊版，改寫中</span>')
            side.append(f'<span class="pill" data-read-key="{key}" hidden>已讀</span>')
        else:
            side.append('<span class="pill muted">撰寫中</span>')
        inner = (f'<span class="no">{no}</span>'
                 f'<span class="t">{html.escape(zh)}<span class="en">{html.escape(en)} · {date}</span></span>'
                 f'<span class="sum">{html.escape(summary)}</span>'
                 f'<span class="side">{"".join(side)}</span>')
        if ready:
            rows.append(f'      <li><a class="row" href="{key}.html">{inner}</a></li>')
        else:
            rows.append(f'      <li class="upcoming"><div class="row">{inner}</div></li>')
    return "\n".join(rows)


def is_ready(key):
    """A lecture is ready when its page exists, is complete (has the pager),
    and, if lecture keys were given on the command line, is one of them."""
    import sys
    page = SITE / f"{key}.html"
    if not page.exists() or 'class="pager"' not in page.read_text(encoding="utf-8"):
        return False
    chosen = [a for a in sys.argv[1:] if a.startswith("l")]
    return not chosen or key in chosen


def upcoming_rows():
    out = []
    for date, title, note in UPCOMING:
        out.append(f'        <li><span class="d">{date}</span><span class="w">{html.escape(title)}</span><span class="n">{html.escape(note)}</span></li>')
    return "\n".join(out)


def main():
    first_ready = next((k for k, *_ in LECTURES if is_ready(k)), "l02")
    page = f"""<title>CS2680 觀念導讀</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="styles.css">
<style>
  .later {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 0; border-top: 1px solid var(--rule); }}
  .later li {{ display: grid; grid-template-columns: 3.4rem minmax(0, 1fr) auto; gap: .2rem .9rem; padding: .5rem .25rem; border-bottom: 1px solid var(--rule); font-size: .9375rem; color: var(--ink-soft); }}
  .later .d {{ font-family: var(--font-mono); font-size: .8125rem; font-variant-numeric: tabular-nums; padding-top: .1rem; }}
  .later .w {{ min-width: 0; color: var(--ink); }}
  .later .n {{ font-family: var(--font-mono); font-size: .75rem; white-space: nowrap; padding-top: .15rem; }}
  @media (max-width: 560px) {{ .later li {{ grid-template-columns: 3rem minmax(0, 1fr); }} .later .n {{ grid-column: 2; }} }}
  .limits {{ margin: 0; padding-left: 1.3rem; display: grid; gap: .4rem; max-width: var(--measure); font-size: .9375rem; color: var(--ink-soft); }}
</style>

<header class="topbar">
  <div class="topbar-inner gutter">
    <a class="brand" href="index.html">CS2680 <span>觀念導讀</span></a>
    <nav class="lecnav" aria-label="開始閱讀"><a href="submissions.html">收作業總表</a><a href="{first_ready}.html">開始閱讀 →</a></nav>
  </div>
</header>

<main class="page gutter">
  <header class="hero">
    <p class="eyebrow">Harvard SEAS · Fall 2026 · Juncheng Yang</p>
    <h1>CS2680 觀念導讀</h1>
    <p class="sub">Modern AI Systems: Agents and System Optimizations</p>
    <p>這門課沒有錄影。這裡每一堂有一篇架構文章，搭配官方 slides 讀。文章整理整堂的架構，補上 slides 沒解釋的背景，再加上延伸思考和讀書會討論題。</p>
  </header>

  <section class="block" aria-labelledby="map-h">
    <h2 id="map-h">課程地圖</h2>
    <p>課程從最上層的 agent,一路往下講到硬體(分層來自 L1 p.42)。點主題，直接跳到講這個主題的段落。灰字是 Part II 還沒公開 slides 的講次。</p>
{map_rows()}
    </ol>
  </section>

  <section class="block" aria-labelledby="list-h">
    <h2 id="list-h">已公開的講次</h2>
    <ol class="leclist">
{lecture_rows()}
    </ol>
  </section>

  <section class="block" aria-labelledby="how-h">
    <h2 id="how-h">怎麼讀</h2>
    <ol class="howto">
      <li>先讀第 5 段「問題討論」的<b>基礎題</b>。它們依 slide 順序排列，答案都在 slides 裡。</li>
      <li>帶著問題，自己一頁一頁看完 slides。看到對應的頁，把答案記下來；看完展開「參考答案」對照。</li>
      <li>再讀文章。「先看這裡」和架構圖給你整堂的全貌，核心觀念把主線串起來，「觀念補充」解釋 slides 預設你懂的名詞。</li>
      <li>讀書會前：主持人切到<b>進階題</b>，按「複製進階題」貼到群組。成員寫下自己的答案，貼到那一堂最後的「交作業」。</li>
      <li>讀書會上：一起展開「參考觀點與追問」，比較彼此的答案。</li>
      <li>想動手時，照「動手試試」做。裡面有可以照打的設定檔、指令或小練習。</li>
    </ol>
  </section>

  <section class="block" aria-labelledby="hw-h">
    <h2 id="hw-h">交作業</h2>
    <p>每一堂的第 7 段「交作業」收大家對進階題的討論，可以附檔。送出後所有成員都看得到。<a href="submissions.html">收作業總表</a>列出誰交了哪幾堂，主持人也能在那裡把全部討論下載成一份 Markdown。</p>
  </section>

  <section class="block" aria-labelledby="style-h">
    <h2 id="style-h">這份筆記的寫法</h2>
    <p>文字約 75% 遵守 ASD-STE100(Simplified Technical English)的原則。比喻和因果說明保留彈性。</p>
    <div class="rules">
      <div><b>一句一件事</b><p>每句只講一個概念。描述句控制在 40 字以內。</p></div>
      <div><b>主動語態</b><p class="ok">✓ harness 執行 tool call。</p><p class="no-good">✗ tool call 被 harness 執行。</p></div>
      <div><b>術語保留英文</b><p>context window、harness、prefix cache 等標準術語不硬翻。</p></div>
    </div>
    <ul class="limits">
      <li>文章不逐頁重講 slides。它整理架構、補背景、做延伸，並附討論題。</li>
      <li>「延伸思考」是本文的推論，不是 slides 的內容。每篇都有標示。</li>
      <li>基礎題只問 slides 講了什麼；進階題問你會怎麼做。兩者都維持通用，不綁定特定公司或專案。估算題的參考答案附完整算式。</li>
      <li>Claude Code 的設定檔與指令已對照 2026 年 10 月的官方文件。</li>
      <li>本站不轉載 slides 的圖片。頁碼連結會開到官方 PDF 的那一頁。</li>
      <li>「已讀」標記只存在你自己的瀏覽器。「交作業」的內容存在這個站台的共用資料庫，登入 claude.ai 的成員都看得到。</li>
    </ul>
  </section>

  <section class="block" aria-labelledby="later-h">
    <h2 id="later-h">還沒有 slides 的講次</h2>
    <p>Slides 在上課後才公開。以下依課程網站的時程(可能調整)。</p>
    <ul class="later">
{upcoming_rows()}
    </ul>
  </section>

  <p class="fineprint">本站是 CS2680 slides 的學習筆記：用自己的話改寫並延伸說明。原始 slides 與課程內容的版權屬於 Juncheng Yang 與 Harvard CS2680。課程網站:<a href="https://cs2680.com" target="_blank" rel="noopener">cs2680.com</a>。</p>
</main>
<script src="app.js"></script>
<script src="submit.js"></script>
"""
    (SITE / "index.html").write_text(page, encoding="utf-8")
    ready = [k for k, *_ in LECTURES if (SITE / f"{k}.html").exists()]
    print("index.html written; ready lectures:", ready)


if __name__ == "__main__":
    main()
