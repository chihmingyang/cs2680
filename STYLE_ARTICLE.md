# CS2680 架構文章撰寫規範(v2)

你負責把 Harvard CS2680 某一堂課，寫成一篇「架構文章」:`/home/claude/cs2680/site/lXX.html`。
**範本是 `/home/claude/cs2680/site/l02.html`。先完整讀一遍：結構、class、語氣、密度都照它做。**

不要發布 artifact、不要寄送檔案、不要寫入 memory。只寫你負責的 `lXX.html`。
不要改 `styles.css`、`app.js`、`l02.html`、`index.html`,也不要改 archive 裡的檔案。

## 1. 這篇文章的定位

- 讀者先自己一頁一頁看完 slides,再讀這篇。**不要逐頁重講 slide。**
- 這篇提供 slide 給不了的東西：整堂的架構、串起主線的觀念、slide 預設你懂的背景、超出 slide 的延伸思考，以及讀書會討論題。
- 讀者是軟體工程師，程度從新手到資深都有。讀者偏好：講工具或流程時，要附具體範例(檔案內容、實際指令)。
- 讀者的時間有限，但也不想一直另外查資料。所以分兩層：主線維持短;slide 預設你懂、讀者卻要另外查的背景，放進預設收合的「深入」區塊(第 4 節「深入區塊」)。卡住才展開，不卡就不花時間。
- 這是讀書會教材。主持人會在讀書會**之前**把討論題發給成員回答，所以第 5 段要最紮實。
- 討論題維持**通用**:不要寫特定公司、產品或專案名稱。用「你們團隊」「一個你熟悉的流程」這類說法。

## 2. 素材來源

1. **主要來源**:`/home/claude/cs2680/archive/lXX-cards.html`。這是同一堂課的舊版逐頁導讀，內容已對照 slides 寫成，數字與事實都驗證過。用它取得 slide 的事實和例子。**它的頁碼可能來自較早的 PDF 匯出，不要直接抄**;頁碼照第 10 節對照現行 PDF。
2. Slide 本身:`https://cs2680.com/slides/<pdf>`。只有在舊版頁面不清楚、或你要確認某個細節時，才用 WebFetch 去查(shell 連不到這個網站)。
3. 一般知識：只寫你確定正確的內容。不確定就不寫。
4. 補充 Claude Code 或其他產品的細節前，先查官方文件(WebFetch `https://code.claude.com/docs/en/...`)。
5. 所有計算(token、成本、機率、平均值)都用 `python3` 驗算後再寫。

## 3. 頁面結構(照 l02.html)

依序:
1. `<head>`:同 l02(fonts、styles.css)。`<title>LX 中文標題 · CS2680</title>`。
2. `header.topbar`:brand、`nav.lecnav`(上一堂 / LX / 8 / 下一堂;第一堂和最後一堂只留存在的方向)。**不要**放「只看重點」按鈕。
3. `main.page.gutter.article[data-lecture="lXX"][data-format="article"][data-pdf="<pdf>"][data-pages-total="N"]`。**不要**放 `.proto` 試做標語。
4. `header.lecture-head`:eyebrow、h1、`.en-title`、`ul.meta`(Slides 連結、頁數、`<li><span class="k">頁碼</span>PDF 檢視器的頁數</li>`、`<span class="read-time">`;有深入區塊時再加 `<li><span class="k">深入</span><span class="deep-time">約 N 分鐘</span>,選讀</li>`)。`main` 的 `data-pages-total` 和「頁數」都等於現行 PDF 的實際頁數。
5. `section.tldr`「先看這裡」:`.thesis` 2–3 句、`ul.core` 3 條(`<b>粗體重點。</b>` + 1–2 句)、`.readhow` 一句讀法。
6. 左側目錄 `aside.sidenav`(在 `main` 之前)加上 `div.layout > div.content`:照 l02 現行的寫法。本堂那一列展開 `ol.sn-secs`;核心觀念那一項的 `span.sn-p` 寫頁碼範圍;子項 `ol.sn-subs` 連到 `#i1…`、`#t1…`、`#x1…`。舊版的 `nav.toc` 已經不用。
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
- 每個 `div.idea` 的 `div.prose` 後面，放一個 `div.exlist.deeplist`,內含 2–5 個「深入」區塊(見下方「深入區塊」)。

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

### 深入區塊 `details.ex.deep`(放在第 2 段每個核心觀念裡)

範本是 l02.html 的 `#d1`–`#d12`。

**目的。** 補上 slide 預設你懂、讀者卻要另外查的背景。主線不變長。讀者看 slides 卡住時，才展開對應的區塊。

**結構。**

```html
<div class="exlist deeplist">
  <details class="ex deep" id="d1">
    <summary>深入｜一次 model 呼叫，實際送出什麼<span>p.6–10</span></summary>
    <div class="exbody prose">
      <p>…</p>
      <figure class="file"><figcaption>示意：…</figcaption><pre><code>…</code></pre></figure>
      <ul><li>…</li></ul>
      <div class="table-wrap"><table class="wide">…</table></div>
    </div>
  </details>
  …
</div>
```

- 位置：`div.idea` 裡、`div.prose` 後面。每個核心觀念 2–5 塊。
- `id` 用 `d1…dN`,全頁不重複。`summary` 以「深入｜」開頭，寫一個問題或主題;`span` 寫 PDF 檢視器頁碼。
- 內文用 `div.exbody.prose`。可以用 `p`、`ul`/`ol`、`figure.file`、`pre`、`div.table-wrap > table`(三欄以上加 `.wide`)。不要另寫 CSS。
- 每塊約 150–450 字。全篇深入合計約 8–12 分鐘。
- 簡化過的資料格式，在 `figcaption` 寫「示意」。

**怎麼找缺口。** 一頁一頁看 slides,自問「沒用過這個工具的工程師，看到這頁會卡在哪裡」。優先寫這六種：

1. **機制的實際樣子**:資料、檔案、request 長什麼樣。例：L2 `#d1` 的 request JSON。
2. **數量感**:token、延遲、成本、上限的具體數字。例：L2 `#d1` 的 token 換算。
3. **Slide 只帶過一句的頁**:主線沒提、slide 也沒解釋的頁。例：L2 `#d2`(不讀整個 repo)。
4. **容易混淆的一組概念**:用表格比較。例：L2 `#d2`(agentic search 與 RAG)、`#d3`(六種權限模式)。
5. **跨頁的總表**:把散在多頁的事實串成一張表。例：L2 `#d4`(檔案地圖)、`#d5`(什麼時候進 context)。
6. **讀者會問的「為什麼不直接…」**:例：L2 `#d10`(為什麼不用 Bash 跑 `gh`)。

讀者在讀書會或對話裡提過的問題，也是缺口的來源。L2 的 `#d5`–`#d7` 就來自讀者的追問。

**不要寫。** 逐頁重講 slide;和主線、第 3 段或基礎題「重點複習」重複的內容;沒查證的產品細節。Claude Code、API 價格這類細節，先查官方文件，再寫明版本或日期。

**和基礎題「重點複習」分工。** 第 5 段每一題基礎題的參考答案，已經寫成重點複習(答案、重點拆解、背景補充、常見誤解、例子)。寫深入區塊前先讀完它們。已經講過的，用一句話指過去，例如「規則的寫法見第 5 段基礎題第 1 題的重點複習」。深入區塊只補它們沒講的部分。

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

- 主線閱讀時間目標 **12–16 分鐘**(check 腳本估算，不含深入區塊)。第 5 段可以長，其他段落要精簡。
- 深入區塊另計，全篇約 **8–12 分鐘**。check 腳本會分開印出兩個數字;`--fix-time` 把主線寫進 `span.read-time`,把深入寫進 `span.deep-time`。

## 8. 驗證(必做)

```bash
cd /home/claude/cs2680
python3 -I tools/punct.py site/lXX.html
python3 -I tools/check_article.py site/lXX.html --pages N --pdf FILE.pdf --fix-time
python3 -I tools/shot_article.py site/lXX.html     # 用 Read 看產生的圖
```

- check 必須印出 `OK`。`LONG` 句子要拆短;`passive 被` 要改寫成主動。check 也會檢查 `data-pages-total` 是否等於 `--pages`。
- 用 Read 看截圖一次：圖裡文字有沒有重疊、超出框、箭頭有沒有接好;討論卡片排版是否正常。發現問題修一次即可。
- 有深入區塊時，把全部 `details.deep` 打開(`e.open = true`)再截圖，桌面 1280px、手機 390px 各一次。看表格能不能左右滑、`pre` 有沒有撐破版面。
- 發布前先讀線上版(Artifact read)。線上版可能比 repo 新(例如介面調整)，要在線上版的基礎上修改。

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

- 表裡的頁數是寫文章當時的數字。L3、L5、L8 和現行 PDF 可能不同，動手前先做第 10 節的對照。L2 是 `2_agent_use_1.pdf`,現行 53 頁(2026-10-19 已修正)。
- L1 沒有上一堂:lecnav 只放「L1 / 8」和「L2 →」;pager 左邊是「← 回總覽」連到 `index.html`。
- L8 沒有下一堂:lecnav 只放「← L7」和「L8 / 8」;pager 右邊是「回總覽 →」連到 `index.html`。

## 10. 頁碼規則

- 頁碼一律用 **PDF 檢視器的頁數**(第幾頁 / 共幾頁)。`a.ref` 的 `#page=N` 也開到這一頁。不用 slide 右下角印的編號，因為它會跳號(隱藏頁仍佔編號)。
- 課程可能重新匯出 PDF:拿掉封面或隱藏頁，頁數就會變。舊頁碼會整段偏移。
- 寫新文章或補深入之前，先對照現行 PDF:
  1. 在瀏覽器打開 PDF(shell 連不到 cs2680.com;用 Claude 的瀏覽器，或請使用者附上 PDF)。
  2. 記下總頁數，和 `data-pages-total`、meta 的「頁數」比對。
  3. 從頭到尾挑 5 個以上的點，對照「檢視器頁數 → slide 標題」，和文章引用的頁碼比對。
- 有偏移時，寫一份 `tools/pagemap/lXX.json`(舊頁碼 → 新頁碼，並在 `note` 寫明對照方法與日期)，再跑：

```bash
python3 -I tools/fix_pages.py tools/pagemap/lXX.json site/lXX.html               # 本堂頁面
python3 -I tools/fix_pages.py tools/pagemap/lXX.json content/lXX-*.html --no-guard  # 片段
python3 -I tools/fix_pages.py tools/pagemap/lXX.json site/lYY.html --xref LX        # 別堂引用的「LX p.N」
```

  腳本只改本堂的頁碼。「L8 p.26」這類別堂的引用會保留。同一份 map 對同一個檔案只能跑一次;完整頁面有防呆，片段和 `--xref` 沒有，重跑前先看 `git diff`。
- 對照狀態(2026-10-19):

| 講次 | 文章寫的頁數 | 現行 PDF | 狀態 |
|---|---|---|---|
| L2 | 60 | 53 | 已修正，`tools/pagemap/l02.json` |
| L3 | 83 | 約 72 | 差很多，待逐頁對照 |
| L5 | 49 | 約 45 | 差很多，待逐頁對照 |
| L8 | 61 | 約 54 | 差很多，待逐頁對照 |
| L1、L4 | 52、58 | 約 51、57 | 可能只差最後的空白頁，待確認 |
| L6、L7 | 33、38 | 33、38 | 看起來一致 |

  「約」是用 WebFetch 估的數字，不精確。修正前一定要照上面三步在檢視器裡確認。

## 11. 既有講次補深入區塊(L3–L8)

依序做，一次一堂：

1. **頁碼**:照第 10 節對照現行 PDF。有偏移就先修，再寫深入區塊，避免新內容又要重算頁碼。
2. **基礎**:發布前的線上版可能比 repo 新。先用 Artifact read 取得線上的 `lXX.html`,在它上面修改。
3. **缺口清單**:一頁一頁看 slides,對照現行文章，依 slide 段落列出缺口(第 4 節「深入區塊」的六種)。每個核心觀念挑 2–5 個最常卡住的。
4. **查證**:產品細節查官方文件;數字用 python 驗算。
5. **撰寫**:照 l02 的 `#d1`–`#d12` 寫。先讀第 5 段基礎題的重點複習，不重複。頁碼直接寫新頁碼。
6. **驗證**:`punct.py` → `check_article.py`(看主線與深入的分鐘數)→ 展開全部深入區塊截圖(桌面、手機)。
7. **發布**:只發布改動的檔案(`lXX.html`,必要時加 `index.html`)。不要改 capabilities。
