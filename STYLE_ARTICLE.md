# CS2680 架構文章撰寫規範(v2)

你負責把 Harvard CS2680 某一堂課，寫成一篇「架構文章」:`/home/claude/cs2680/site/lXX.html`。
**範本是 `/home/claude/cs2680/site/l02.html`。先完整讀一遍：結構、class、語氣、密度都照它做。**

不要發布 artifact、不要寄送檔案、不要寫入 memory。只寫你負責的 `lXX.html`。
不要改 `styles.css`、`app.js`、`l02.html`、`index.html`,也不要改 archive 裡的檔案。

## 1. 這篇文章的定位

- 讀者先自己一頁一頁看完 slides,再讀這篇。**不要逐頁重講 slide。**
- 這篇提供 slide 給不了的東西：整堂的架構、串起主線的觀念、slide 預設你懂的背景、超出 slide 的延伸思考，以及讀書會討論題。
- 讀者是軟體工程師，程度從新手到資深都有。讀者偏好：講工具或流程時，要附具體範例(檔案內容、實際指令)。
- 這是讀書會教材。主持人會在讀書會**之前**把討論題發給成員回答，所以第 5 段要最紮實。
- 討論題維持**通用**:不要寫特定公司、產品或專案名稱。用「你們團隊」「一個你熟悉的流程」這類說法。

## 2. 素材來源

1. **主要來源**:`/home/claude/cs2680/archive/lXX-cards.html`。這是同一堂課的舊版逐頁導讀，內容已對照 slides 寫成，數字與事實都驗證過。用它取得 slide 的事實、頁碼、例子。
2. Slide 本身:`https://cs2680.com/slides/<pdf>`。只有在舊版頁面不清楚、或你要確認某個細節時，才用 WebFetch 去查(shell 連不到這個網站)。
3. 一般知識：只寫你確定正確的內容。不確定就不寫。
4. 補充 Claude Code 或其他產品的細節前，先查官方文件(WebFetch `https://code.claude.com/docs/en/...`)。
5. 所有計算(token、成本、機率、平均值)都用 `python3` 驗算後再寫。

## 3. 頁面結構(照 l02.html)

依序:
1. `<head>`:同 l02(fonts、styles.css)。`<title>LX 中文標題 · CS2680</title>`。
2. `header.topbar`:brand、`nav.lecnav`(上一堂 / LX / 8 / 下一堂;第一堂和最後一堂只留存在的方向)。**不要**放「只看重點」按鈕。
3. `main.page.gutter.article[data-lecture="lXX"][data-format="article"][data-pdf="<pdf>"][data-pages-total="N"]`。**不要**放 `.proto` 試做標語。
4. `header.lecture-head`:eyebrow、h1、`.en-title`、`ul.meta`(Slides 連結、頁數、`<span class="read-time">`)。
5. `section.tldr`「先看這裡」:`.thesis` 2–3 句、`ul.core` 3 條(`<b>粗體重點。</b>` + 1–2 句)、`.readhow` 一句讀法。
6. `div.layout` > `nav.toc` + `div.content`。TOC 七項，右欄文字照 l02:`全貌`、`p.X–Y`、`背景`、`延伸`、`讀書會`、`範例`(或 `練習`)、`—`。
7. 六個段落 + 延伸閱讀(見第 4 節)。
8. `nav.pager`、`p.fineprint`(照 l02 的句型，改成這一堂)、`<script src="app.js">`。

## 4. 六個段落

### 1 架構 `section.part#s-arch`
- `p.kicker`「1 · 架構」+ `h2`(這堂的零件怎麼接在一起)。
- 一張 inline SVG(`figure.diagram`),畫這堂的**主結構**:元件、資料流、層次，或兩種做法的差別。舊版頁面的圖可以改寫沿用，但要服務「全貌」這個目的。最多兩張。
- `div.prose`:一段「讀圖重點」,2–4 句。

### 2 核心觀念 `section.part#s-ideas`
- 3–5 個 `div.idea`。每個有 `h3`(觀念句)+ `a.ref`(slide 頁碼範圍)+ `div.prose`(2–3 段)。
- 用文章串起 slide 的主線：問題 → 機制 → 後果。重點是因果與連結，不是條列 slide 內容。

### 3 觀念補充 `section.part#s-background`
- `dl.terms`,4–6 個條目。每條:`dt`(名詞 + `<small>` 一句用途)、`dd`(2–5 句)。
- 寫 slide 預設你懂、但沒解釋的背景。可以附 `a.ref` 指回相關 slide。

### 4 延伸思考 `section.part#s-beyond`
- 開頭放 `<p class="note-own">這一段是本文的延伸，不是 slide 的內容。</p>`。
- 3–4 個 `div.idea`:推論、取捨、限制、跨堂連結(「L6 會講…」)、對 slide 主張的檢驗。
- 推論要有根據：引用 slide 的事實或你確定的一般知識。不要誇大。

### 5 問題討論 `section.part#s-discuss` ← **最重要**
- `header.part-head` 的 `.lede` 照 l02。
- `div.copyrow`:`button#copy-q.copybtn`,屬性 `data-title="CS2680 LX 讀書會討論題：<中文標題>"`、`data-slides="<PDF 網址>"`;再加 `span.copyhint`。然後放 `textarea#copy-fallback.copybox`(照 l02,保留 `hidden`)。
- `ol.qlist` 內放 **6 題** `li.dq#q1…#q6`。題型要混合，至少涵蓋五種:**概念**(解釋機制)、**估算/分析**(要算數字)、**設計**(做決定並說理由)、**團隊實務**、**風險/取捨**、**應用**(套用到自己的流程)。
- 每題的結構(全部必要):
  - `p.qtag`:題型 · 主題 · `a.ref`(相關 slide)。
  - `p.qtext`:題目。一個清楚的問題，可以有兩個小問。
  - `p.qctx`:`<b>情境：</b>` + 具體情境(數字、條件、例子)。成員要能只靠這段就開始回答。
  - `div.qcover`:`<b>回答時請涵蓋</b>` + `ul` **3 點**。每點是一個可檢查的要求(列出、估算、比較、指出、說明理由)。
  - `details`「思考方向」:`div.hint`,2–4 句。提示切入點與相關觀念，不給答案。
  - `details`「參考觀點與追問」:`div.hint`,**4–6 點**有內容的參考答案(`ul`),加一段 `<p><b>追問:</b>…</p>` 給 1–2 個延伸問題。估算題要寫出完整算式與結果。
- 題目不要只問「你怎麼看」。要有情境、有限制條件、有可以比較的答案。
- `h3.subhead`「自我檢查」+ `div.quiz`:3 題有標準答案的題目(`details` > `summary` + `div.answer`)。

### 6 動手試試 `section.part#s-try`
- 2–4 個 `details.ex`(預設收合)。`summary` 寫標題 + `<span>` 相關頁碼。
- 工具類講次：可以照打的設定檔、指令、程式碼(`figure.file` 或 `pre`)。
- 觀念類講次：小練習(計算、設計、用 python 驗證一個現象),附解答。
- 範例要正確可用。Claude Code 相關內容以官方文件為準(2026-10)。

### 延伸閱讀 `section.wrap#wrap`
- `h2` 延伸閱讀 + `ul.reading`(用舊版頁面的閱讀清單)+ `label.readmark`(`input#read-box`)。

## 5. 語言：繁體中文 + 英文術語，ASD-STE100 約 75–80%

1. 一句只講一件事。描述句 ≤ 40 字(英文詞算 1 字)。
2. 主動語態。不寫「被…」句型。
3. 一段最多 4 句。
4. 業界標準術語保留英文:context window、harness、subagent、prefix cache、KV cache、compaction、benchmark、trajectory、throughput、latency 等。第一次出現可加一句中文說明。
5. 不用填充詞(其實、基本上、非常、相當、可以說、事實上、簡單來說)、不用成語、不用破折號插入語、不用「不是 X,而是 Y」句型。
6. 數字用阿拉伯數字，保留單位。
7. 中文用全形標點;中英文之間加半形空格。寫完一定跑 `tools/punct.py`。
8. HTML 特殊字元要跳脫(`&lt;`、`&amp;`)。

## 6. 圖(inline SVG)

- 照 l02 的寫法:`figure.diagram > div.scroll > svg[viewBox][role="img"][aria-label]` + `figcaption`。
- 只用 styles.css 的 class:`dg-box`、`dg-box-soft`、`dg-box-accent`、`dg-frame`、`dg-line`、`dg-soft`、`dg-dash`、`dg-accent`、`dg-fill-ink`、`dg-fill-accent`、`dg-fill-soft`、`dg-t`、`dg-tb`、`dg-ts`、`dg-tm`、`dg-ta`。不寫死顏色，svg 內不放 `<style>`。
- marker id 加講次前綴(例 `l5c-ah`)。箭頭要有標籤。文字 11–13px。viewBox 寬 600–760。
- 數據圖要照比例畫，標籤寫實際數值。

## 7. 長度

- 閱讀時間目標 **12–16 分鐘**(check 腳本估算)。第 5 段可以長，其他段落要精簡。

## 8. 驗證(必做)

```bash
cd /home/claude/cs2680
python3 -I tools/punct.py site/lXX.html
python3 -I tools/check_article.py site/lXX.html --pages N --pdf FILE.pdf --fix-time
python3 -I tools/shot_article.py site/lXX.html     # 用 Read 看產生的圖
```

- check 必須印出 `OK`。`LONG` 句子要拆短;`passive 被` 要改寫成主動。
- 用 Read 看截圖一次：圖裡文字有沒有重疊、超出框、箭頭有沒有接好;討論卡片排版是否正常。發現問題修一次即可。

## 9. 各堂資料

| 檔案 | PDF | 頁數 | 日期 | 英文標題 | 中文標題 | 上一堂 / 下一堂 |
|---|---|---|---|---|---|---|
| l01.html | 1_intro.pdf | 52 | 2026-09-02 | Course overview and logistics | 課程總覽與 AI 系統 | — / L2 Claude Code 怎麼運作 |
| l03.html | 3_agent_use_2.pdf | 83 | 2026-09-14 | Agents use II: 100x Engineer with Multi-agents | 用多個 agent 放大產能 | L2 Claude Code 怎麼運作 / L4 Context 管理與 tool 設計 |
| l04.html | 4_agent_design_1.pdf | 58 | 2026-09-16 | Agents design I: context management and tool design | Context 管理與 tool 設計 | L3 / L5 Multi-agent 架構與溝通 |
| l05.html | 5_agent_design_2.pdf | 49 | 2026-09-23 | Agents design II: multi-agent architecture, coordination, and communication | Multi-agent 架構與溝通 | L4 / L6 Agent memory 與可靠性 |
| l06.html | 6_agent_design_3.pdf | 33 | 2026-09-28 | Agents design III: agent memory and reliability | Agent memory 與可靠性 | L5 / L7 Agent 評估 |
| l07.html | 7_agent_design_4.pdf | 38 | 2026-09-30 | Agent design IV: agent evaluation | Agent 評估 | L6 / L8 成本、速度與 harness 架構 |
| l08.html | 8_agent_design_5.pdf | 61 | 2026-10-07 | Advanced agent design I: Cost and performance | 成本、速度與 harness 架構 | L7 / — |

- L1 沒有上一堂:lecnav 只放「L1 / 8」和「L2 →」;pager 左邊是「← 回總覽」連到 `index.html`。
- L8 沒有下一堂:lecnav 只放「← L7」和「L8 / 8」;pager 右邊是「回總覽 →」連到 `index.html`。
