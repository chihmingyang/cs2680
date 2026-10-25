# CS2680 架構文章撰寫規範（v4.1）

更新：2026-10-26（v4.1：指令、設定檔、對話一律用 code snippet；每章至少一張圖或表；清單用 ul/ol；見第 4 節第 2 段與新的第 6b 節）。2026-10-25（v4.0：文章要能不看 slides 從頭讀到尾，名詞在第一次出現的地方講清楚，深入區塊併回主線，觀念補充改成查閱詞條；見第 1、4 節。L3、L4 是第一批改寫的範例）。2026-10-23（v3.8：核心觀念的 prose 裡可以放比較圖或表格，見第 4 節第 2 段）。2026-10-22（v3.7：ASD-STE100 依段落分兩檔，推理段落放寬到約 60–70%，見第 5 節）。2026-10-22（v3.6：取消閱讀時間的限制，見第 7 節）。2026-10-22（v3.5：進階題每堂最多 3 題，見第 4 節第 5 段）。2026-10-22（v3.4：觀念補充的條數與閱讀時間上限改為建議，見第 4、7 節）。2026-10-21（v3.3：文章要讓沒看 slides 的人也讀得懂，見第 1 節；閱讀時間上限 16 → 30 分鐘，見第 7 節）。2026-10-19（v3.2：站台搬到 `docs/`；討論改用 GitHub Issues，連結由 `tools/discuss.py` 寫入）。對照的是 L1–L8 的實際格式。第 5 段的基礎題另見 `STYLE_BASIC.md`。

你負責把 Harvard CS2680 的一堂課寫成一篇「架構文章」：`/home/claude/cs2680/docs/lXX.html`。
**範本是 `docs/l02.html`。先完整讀一遍：結構、class、語氣、密度都照它做。**

只寫你負責的 `lXX.html`。不要改 `styles.css`、`app.js` 和其他頁面；跨頁的改動由 `tools/add_lecture.py` 處理，討論連結由 `tools/discuss.py` 處理。不要 commit、push，不要寫入 memory。

## 1. 定位

- **文章是主體，slides 是輔助**（2026-10-25 定，取代之前「配著 slides 讀」的定位）。讀者要能不看 slides 從頭讀到尾，讀完就跟上這堂的內容；頁碼只是出處，想對照時再打開。原因：只看 slides 吸收效果不好，教授給的名詞（semantic search、glob、LSP、hook、proxy）在 slide 上沒講清楚，成員要靠一問一答才懂，所以文章要把這些問答先寫進去。
- **由淺入深、流暢連貫。** 每一章從讀者已經知道的東西出發（一個 model 單獨能做什麼 → 加 tool → 加 loop），再往下走。章與章、段與段要接得上：每章開頭一句說這章從哪裡來，段落開頭一句說這段要講什麼。
- **不預設讀者懂。** 少見或複雜的觀念在第一次出現的地方就講清楚：是什麼、怎麼運作、一個具體例子、代價是什麼，通常是一整段，不是半句。不要用「見觀念補充」「見深入」把解釋推走；觀念補充只放查閱用的短版（第 4 節第 3 段）。讀者是軟體工程師，但不要假設他用過 Claude Code 或讀過前幾堂。
- Slide 列出的清單要在文中點名，不能只寫「p.18 的八種架構」。Slide 給的例子（指令、檔案內容、數字）要寫進文章，因為讀者不會去看 slide。
- **不要逐頁重講 slide。** 文章的結構依觀念的先後，可以和 slide 順序不同；但同一章盡量對到連續的頁碼範圍，方便對照。
- 這篇還提供 slide 給不了的東西：整堂的架構、slide 沒解釋的背景、超出 slide 的延伸思考、讀書會討論題。
- 讀者是軟體工程師，程度從新手到資深都有。講工具或流程時，附具體範例（檔案內容、實際指令、對話怎麼打）。只有概念，讀者無法實踐。
- 討論題維持**通用**：不寫特定公司、產品或專案名稱。用「你們團隊」「一個你熟悉的流程」。
- 成員的回答是低壓力的思考分享。不要寫成作業、考試或認證的語氣。

## 2. 素材

1. Slides：`slides/lXX-notes.md`。沒有就照 `WORKFLOW.md` B2 用 WebFetch 整理。
2. L1–L8 的事實已經在頁面裡，修改時以頁面和 slides 為準。
3. Readings：課程網站的 readings 頁（例如 `https://cs2680.com/readings/oct-07.html`），用 WebFetch 讀。
4. 一般知識：只寫你確定正確的內容。不確定就不寫。
5. Claude Code 或其他產品的細節：先查官方文件（WebFetch `https://code.claude.com/docs/en/...`）。
6. 所有計算（token、成本、機率、延遲、throughput）都用 `python3` 驗算後再寫。

## 3. 頁面結構（照 l02.html）

1. `<head>`：同 l02（fonts、styles.css）。`<title>LX 中文標題 · CS2680</title>`。
2. `header.topbar`：`button.sn-open`、brand、`nav.lecnav`（`← L(X-1)`、`span.here` 寫 `LX / N`；最後一堂沒有下一堂連結）、`div.readbar`。
3. `div.shell` > `aside.sidenav#sidenav`（照抄範本，`add_lecture.py` 會重建）+ `div.sn-scrim`。
4. `main.page.gutter.article[data-lecture="lXX"][data-format="article"][data-pdf="<pdf>"][data-pages-total="N"]`。
5. `header.lecture-head`：
   - `p.eyebrow`：`Lecture 09 · 2026-10-19 · Part II`（腳本從這行讀日期和 Part）。
   - `h1` 中文標題、`p.en-title` 英文原標題。
   - `ul.meta`：Slides 連結、頁數、頁碼（「PDF 檢視器的頁數」）、閱讀 `span.read-time`、（有深入區塊時才有）深入 `span.deep-time`、全部展開 `span.full-time`。時間由 `check_article.py --fix-time` 填；頁面沒有深入區塊時，刪掉深入那一個 `li`。
6. `section.tldr`「先看這裡」（`h2#tldr-h`）：`.thesis` 3–4 句、`ul.core` 3 條（`<b>粗體重點。</b>` + 1–2 句）、`.readhow` 讀法，照 l04 的句型：「這篇可以不看 slides 從頭讀到尾：每個名詞在第一次出現的地方就有解釋，由淺入深，頁碼只是出處。想對照 slides，就在讀到頁碼時打開那幾頁；想先帶著問題讀，就先看第 5 段的基礎題。」
7. `div.layout` > `div.content`：七個段落 + 延伸閱讀（第 4 節）。
8. `nav.pager`、`p.fineprint`（照 l02 的句型改成這一堂）、`<script src="app.js">`。

## 4. 段落

### 1 架構 `section.part#s-arch`
- `p.kicker`「1 · 架構」+ `h2`（這堂的零件怎麼接在一起）。
- 1–2 張 inline SVG（`figure.diagram`）畫主結構：元件、資料流、層次，或兩種做法的差別。
- `div.prose`：「讀圖重點」2–4 句。

### 2 核心觀念 `section.part#s-ideas` ← 文章的主體
- 3–6 個 `div.idea#iN`（2026-10-25 從 3–5 放寬；`check_discuss.py` 已改）。`h3`（觀念句）內放 `a.ref`（slide 頁碼範圍）。
- 每章是一段連貫的教學，長度由內容決定（L4 的 i2 有 20 多段）。章內用 `<b>粗體小標。</b>` 開頭的段落分節，依「問題 → 名詞解釋 → 機制 → 例子 → 代價 → 證據」的順序走。可以放 `ol`、`figure.file`（指令、設定檔、程式碼，逐行標註）、`figure.diagram`、`div.table-wrap`。
- 名詞第一次出現就解釋（第 1 節）。解釋的順序是由淺入深：先講讀者熟的（shell 指令、git），再講建在上面的（worktree、LSP）。
- 寫因果，不要條列 slide。但 slide 上的「N 個理由」「N 種做法」「N 個步驟」要用 `ul`／`ol` 列出，每一條是 `<b>名稱。</b>` 加一兩句解釋；不要把五個項目塞進一段散文（2026-10-26，L3、L4 的 ol/ul 是範例）。
- **指令、設定檔、程式碼、對話，一律放 code snippet**（2026-10-26 定，見第 6b 節）。`grep -rn "timeout" src/`、`hooks.json`、`/goal "…"`、一段 JSON-RPC 請求，都不能只用 `<code>` 夾在句子裡帶過；要用 `figure.file` 完整寫出來，附輸出與逐行註解。
- **每章至少一張圖或一張表**（2026-10-26 定）。Slide 上的流程圖、分層圖、比較表、長條圖都重畫成 `figure.diagram` 或 `div.table-wrap`；本文自己整理的也可以畫，figcaption 寫明「本文的整理」。L3 有 11 張、L4 有 15 張（2026-10-26）。
- 「深入」區塊（`details.ex.deep#dN`）：**預設不用**（2026-10-25）。原本放在深入裡的內容（Claude Code 為什麼選 grep、LSP 怎麼建索引、五個執行考量各怎麼做）都是讀者想問的，應該併回主線。只有和主線無關、純粹補充的細節才收合。
- 選用：一個觀念要比較好幾種做法、或有一組數字時，可以在 `div.prose` 裡放一張 `figure.diagram` 或一個 `div.table-wrap` 表格（格式同第 6 節；`shot_article.py` 會一起截圖，收合的深入區塊裡的也會）。每個粗體小標最多一張，放在它說明的那段前後；slide 沒給的部分在 figcaption 寫明「本文的整理」。例子是 L4（2026-10-23）：i2 的 search 成本曲線與 edit 四種方式對照表、i4 的 lost in the middle 折線、i5 的 Breunig 表與 Lewis 長條圖、d2 的冪等時序圖。

### 3 觀念補充 `section.part#s-background`
- 2026-10-25 起改成**查閱用的詞條**：`header.part-head` 裡加一句 `p.lede`（「第 2 段已經在第一次出現的地方解釋過這些名詞。這裡是查閱用的短版……」）。每條 `dd` 2–4 句，結尾指回第 2 段講解的位置（`見 <a href="#i2">i2</a> 的 search 一節`）。
- 只有和主線無關的背景（例如 L4 的 reasoning model、guardrail 與 prompt injection）才在這裡完整寫。
- `dl.terms`，建議 4–6 條（上限只是建議，`check_discuss.py` 只警告），每條包在 `div#tN`：`dt`（名詞 + `<small>` 一句用途）。既有的 `#tN` 錨點有別頁連過來（index、L2、L5、L6），改寫時保留順序，新詞條加在後面。

### 4 延伸思考 `section.part#s-beyond`
- 開頭 `<p class="note-own">這一段是本文的延伸，不是 slide 的內容。</p>`。
- 3–4 個 `div.idea#xN`：推論、取捨、限制、跨堂連結、對 slide 主張的檢驗。推論要有根據，不要誇大。

### 5 問題討論 `section.part#s-discuss` ← 最重要
- `header.part-head` 的 `.lede` 照 l02。
- `div.qtabs`：兩個 `button.qtab`（`#tab-basic`「基礎」、`#tab-adv`「進階」）。
- `div.qset#qset-basic`：基礎題，見 `STYLE_BASIC.md`。
- `div.qset#qset-adv[hidden]`：進階題。
  - `p.qset-lede` 照 l02 的文字（「這 3 題留到讀書會當天一起討論，不用先寫在 GitHub……」）。
  - `div.copyrow`：`button.copybtn[data-copy="adv"]`，`data-title="CS2680 LX 進階題（讀書會討論）：<中文標題>"`、`data-slides="<PDF 網址>"`，加 `span.copyhint`。
  - `ol.qlist` 內**最多 3 題** `li.dq#q1…#q3`（2026-10-22 定，之前 6 題）。
  - 3 題的題型不重複（`qtag` 第一段：概念、估算、分析、設計、團隊實務、風險、取捨、應用）。
  - 挑題的優先順序：一題算數字或分析資料（估算／分析）、一題設計、一題帶回自己團隊（團隊實務／風險／應用）。
  - 3 題對到這堂不同段落的 slides。不要和基礎題、動手試試重複；概念題通常和基礎題重疊，優先刪。
- 每題 `li.dq` > `div.qbody`：
  - `p.qtag`：題型 · 主題 · `a.ref`。
  - `p.qtext`：一個清楚的問題，可以有兩個小問。
  - `p.qctx`：`<b>情境：</b>` + 具體情境（數字、條件、例子）。成員只靠這段就能開始回答。
  - `div.qcover`：`<b>回答時請涵蓋</b>` + `ul` **3 點**。每點是可檢查的要求，後面接 `<span class="qh">提示：……</span>`：指出從哪一頁、哪個數字、哪個比較開始想。不給答案。
  - `details.qstart`「作答範本」> `div.hint`：**3 句** `p.tpl` 填空句，空格用「＿＿」，對應三個回答要點。
  - `details`「參考觀點與追問」> `div.hint`：4–6 點 `ul`，加 `<p><b>追問：</b>…</p>` 1–2 個延伸問題。估算題寫出完整算式與結果。
- 不要寫「思考方向」區塊（已由 `qh` 提示和作答範本取代）。
- 進階題不上 GitHub，不寫 `p.gh-talk`（`check_discuss.py` 會擋）。讀書會當天大家直接看頁面，所以題目、情境、回答要點和作答範本要能獨立讀懂。
- `textarea#copy-fallback.copybox[hidden]`：照 l02。
- `h3.subhead`「自我檢查」+ `div.quiz`：3 題有標準答案的題目（`details` > `summary` + `div.answer`）。

### 6 動手試試 `section.part#s-try`
- `p.lede` 一句說明範例依據。`div.exlist` 內 2–4 個 `details.ex`（預設收合）。`summary` 寫標題 + `<span>頁碼</span>`，內容 `div.exbody`。
- 工具類講次：可以照打的設定檔、指令、程式碼（`figure.file` > `figcaption` + `pre > code`）。
- 觀念類講次（Part II 多數是）：小練習（估算、設計、用 python 驗證一個現象），附解答。
- 範例要正確可用；產品相關內容以官方文件為準並寫明日期。

### 7 大家的討論 `section.part#s-submit`
- 只寫空殼：
  ```html
  <section class="part" id="s-submit">
    <header class="part-head">
      <p class="kicker">7 · 大家的討論</p>
      <h2>這堂的討論</h2>
    </header>
  </section>
  ```
- 內容（綜合討論與全部討論串的連結、留言方式）由 `tools/discuss.py` 填入。

### 延伸閱讀 `section.wrap#wrap`
- `h2` 延伸閱讀；`p.rg-intro`：教授列了幾篇、官方清單連結（`readings/<mon-dd>.html`）。
- `p.rg-legend`（照抄 l02）。
- 選用：`div.callout`「最短路徑」：時間不夠時讀哪幾篇、順序。
- 依主題分組：`h3.rg-h`（中文 + `<small>` 英文）+ `ol.rg`。每篇 `li`：
  - `div.rg-top`：`span.rgm[data-level=1|2|3]`（三個 `<i>`）、`span.rg-lvl`（必讀／推薦／選讀／查閱）、`a.rg-t`（標題，連原文）、`span.rg-meta`（作者 · 類型 · 年份 · 時間估計）。
  - `p.rg-s`：一句定位（這篇講什麼、為什麼讀）。
  - `p.rg-g`：`<b>導讀</b>` + 切入點與一個開場問題，讓認領的人能直接開場。
  - **必讀的每一篇**再加一段摘要 `details.rg-dg`（預設收合，不算進 read-time）。格式與寫法見 `guide/STYLE_DIGEST.md`。L2–L8 的 18 篇在 2026-10-19 全部補齊。
- `p.rg-intro` 的結尾加一句：「必讀」的 N 篇各附一段摘要……（句型照 l05）。
- 等級和時間是本站的建議，不是課程要求。
- `label.readmark` 加 `input#read-box`（照 l02）。

## 5. 語言：繁體中文 + 英文術語，ASD-STE100 依段落分兩檔

2026-10-22 放寬（James 讀 L4 覺得卡）。原因：「一句只講一件事」把推理的因果切成好幾句，句子之間的「所以、但是」常常消失，讀者要自己接回去。中文少了英文的冠詞、代名詞與時態幫忙串句，拆短之後更像條列。L4 第 1–4 段是第一個照新規則改寫的範例。

**推理段落，約 60–70%**：「先看這裡」的 thesis、第 1 段讀圖重點、第 2 段核心觀念（含深入區塊）、第 4 段延伸思考、進階題的參考觀點。

1. 一句可以講兩三件有關係的事，但關係要用連接詞寫明：因為、所以、但、因此、也就是、反過來、這表示。
2. 句子要接得上：下一句從上一句的結論往下講，不要每句都換主詞重新開始。
3. 句長 ≤ 70 字（英文詞算 1 字）。超過就拆，拆開後保留連接詞。
4. 一段講一個論點，最多 6 句。段落開頭一句說這段要講什麼。

**查閱段落，約 75–80%**：第 3 段觀念補充、基礎題的參考答案與「帶走這幾點」、第 6 段動手試試、延伸閱讀摘要。

1. 一句只講一件事。描述句 ≤ 40 字（英文詞算 1 字）。
2. 一段最多 4 句。

**兩檔都適用**：

1. 主動語態，不寫「被」。
2. 標準術語保留英文：context window、harness、subagent、prefix cache、KV cache、prefill、decode、batching、compaction、benchmark、throughput、latency 等。第一次出現可加一句中文說明。
3. 不用填充詞（其實、基本上、非常、相當、可以說、事實上、簡單來說）、成語、破折號插入語、「不是 X，而是 Y」句型。
4. 數字用阿拉伯數字，保留單位。
5. 全形標點；中英文之間半形空格。新寫的檔案或片段先跑 `tools/punct.py FILE --diff` 看它會改什麼，再不帶 `--diff` 執行。**不要對既有頁面整頁跑**：頁面裡的數學式與英文片語（`× (1 + 2)`、`Fail?`）要維持 ASCII，2026-10-19 的規則版本已經避開大多數，但仍先看 diff。
6. HTML 特殊字元要跳脫（`&lt;`、`&amp;`）。

## 6. 圖（inline SVG）

- `figure.diagram > div.scroll > svg[viewBox][role="img"][aria-label]` + `figcaption`。
- 只用 styles.css 的 class：`dg-box`、`dg-box-soft`、`dg-box-accent`、`dg-frame`、`dg-line`、`dg-soft`、`dg-dash`、`dg-accent`、`dg-fill-ink`、`dg-fill-accent`、`dg-fill-soft`、`dg-t`、`dg-tb`、`dg-ts`、`dg-tm`、`dg-ta`。不寫死顏色，svg 內不放 `<style>`。
- marker id 加前綴，全站不能重複：文章本文用 `lNc-`（L9 → `l9c-ah`），基礎題答案用 `tkN-<題號>-`（L9 第 2 題 → `tk9-2-ah`）。
- 箭頭要有標籤。文字 11–13px。viewBox 寬 600–760。數據圖照比例畫，標籤寫實際數值。

## 6b. Code snippet（`figure.file`）

2026-10-26 定（James：「grep 指令或是 glob 指令難道不能用 code snippet 嗎」）。

- 格式：`<figure class="file"><figcaption>標題（頁碼或「本文補的」）</figcaption><pre><code>…</code></pre></figure>`。放在它說明的那段前後。
- 什麼要放：shell 指令（附 `$` 提示字元和範例輸出）、設定檔（`hooks.json`、`SKILL.md`、MCP 設定）、tool call 與 tool result 的 JSON、prompt 範例、對話範例（`>` 開頭）、patch、程式碼。`<code>` 只用在句子裡提到一個名字或一小段參數。
- 逐行註解：用 `← 說明` 放在行尾，或 `#`／`//` 的註解行。對齊用空格，不用 tab。讀者是沒用過這個工具的人，所以每個 flag、每個欄位第一次出現都要註。
- 輸出要寫：指令後面接它印出來的東西（可以省略，用 `… 共 37 行` 標明）。Slide 沒給輸出時自己補，figcaption 寫「輸出是本文補的」。
- 跳脫：`<`、`>`、`&` 寫成 `&lt;`、`&gt;`、`&amp;`。
- 維持 ASCII 標點（`punct.py` 會跳過 `pre`／`code`）。
- 範例：L4 i2 的 grep/glob 三步、tool 定義、Edit tool call、shell tool result；L3 i1 的 `hooks.json`、`session-start`；L3 i4 的 `/goal`、git lock file。

## 7. 長度

- 閱讀時間沒有限制（2026-10-22 取消；2026-10-25 再確認：寧可長而完整，不要短而要讀者去問）。長度由內容決定：每一句要有新資訊。L3、L4 改寫後第 1–4 段各約 25–35 分鐘。
- 頁面仍然顯示 `read-time`（所有 details 收合時看得到的文字）、`deep-time`、`full-time`，讓讀者知道要花多久。用 `check_article.py --fix-time` 算出並寫回；顯示值 15 分鐘以上四捨五入到 5 分鐘。
- 不逐頁重講 slides；不轉載 slide 圖片；頁碼一律用 PDF 檢視器的頁數。

## 8. 驗證

照 `WORKFLOW.md` B4。`check_article.py` 要 `OK`；`check_discuss.py` 在 `discuss.py` 跑完後要 `OK`；截圖用 Read 看一次。

## 9. 各堂資料

| 檔案 | PDF | 頁數 | 日期 | 英文標題 | 中文標題 |
|---|---|---|---|---|---|
| l01.html | 1_intro.pdf | 50 | 2026-09-02 | Course overview and logistics | 課程總覽與 AI 系統 |
| l02.html | 2_agent_use_1.pdf | 53 | 2026-09-09 | Agents use I: How Claude Code Works | Claude Code 怎麼運作 |
| l03.html | 3_agent_use_2.pdf | 72 | 2026-09-14 | Agents use II: 100x Engineer with Multi-agents | 用多個 agent 放大產能 |
| l04.html | 4_agent_design_1.pdf | 56 | 2026-09-16 | Agents design I: context management and tool design | Context 管理與 tool 設計 |
| l05.html | 5_agent_design_2.pdf | 46 | 2026-09-23 | Agents design II: multi-agent architecture, coordination, and communication | Multi-agent 架構與溝通 |
| l06.html | 6_agent_design_3.pdf | 31 | 2026-09-28 | Agents design III: agent memory and reliability | Agent memory 與可靠性 |
| l07.html | 7_agent_design_4.pdf | 37 | 2026-09-30 | Agent design IV: agent evaluation | Agent 評估 |
| l08.html | 8_agent_design_5.pdf | 54 | 2026-10-07 | Advanced agent design I: Cost and performance | 成本、速度與 harness 架構 |

Part II（依課程網站時程，可能調整；PDF 檔名等 slides 公開後再填）：

| 日期 | 英文標題 | 備註 |
|---|---|---|
| 10-19 | Efficient LLM serving: basics I | |
| 10-21 | Efficient LLM serving: basics II | |
| 10-28 | Efficient LLM serving: speculative decoding | |
| 11-02 | Efficient agentic systems: scheduling and prefix caching | |
| 11-04 | Efficient LLM serving: pruning and quantization | |
| 11-09 | Guest lecture: Why Infrastructure sets the pace of AI (Meta) | 客座 |
| 11-11 | Efficient LLM serving: GPU and kernels | |
| 11-16 | Efficient LLM serving: KV-cache optimization and model architectures | 學生主講 |
| 11-23 | Efficient agentic system: routing and load balancing | |
| 11-30 | Efficient agentic systems: others | |

10/05 客座（Snowflake）沒有公開 slides；10/14 Advanced agent design II 是學生主講。兩堂目前都沒有頁面。
