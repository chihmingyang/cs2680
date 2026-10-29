# CS2680 架構文章撰寫規範（v5.9）

更新：2026-10-30（v5.9：**知識點放正文，收合區塊只放查閱與查證**。James 讀 L3：「內容有點雜亂，很多知識點你用補充的」「版本比較對讀者幫助不大」「matt 應該要跟 superpowers 放在一起」。三條規則：（1）章的論證需要的東西一律寫在正文：機制的事實（plugin 的檔案結構、settings.json 的位置、proxy 用規則不用 model）、公式（Amdahl）、對案例的判斷（沒有 hook 怎麼保證）都是正文，不收進名詞註或本文延伸；名詞註只放名詞，本文延伸只放對外部評論、benchmark 的查證這類離主線的東西，一章最多 2 個，合計不超過該章正文的長度。（2）版本對照縮成章末一段或最多 3 項的清單（沒變的、改最多的、slide 沒提但後面會用到的），不放表；只有 slide 的結論因改版不成立時才列表對照。（3）本文補的案例章放在它對照的 slide 案例旁邊，不另立一組放最後；並排表放在那一組的最後一章末尾。L3 依此重排：8 章 3 組，收合區塊 17 → 7；v5.8 的名詞註案例 `#n-hook-files` 已改成 2.1 的正文 `#i1-5`。見第 4 節）。2026-10-29（**L5、L6 的正文補到 v4.0 密度**：各 8 章、每章 3–6 分鐘，read-time 40 與 35 分鐘；全站 L1–L8 現在都是 6–8 章的「文章是主體」版本，L2 除外（4 章，深入區塊仍在）。改法見 WORKFLOW C 的片段組裝）。2026-10-28（v5.8：**名詞註可以放案例**。`details.gloss` 不再限 2–4 句：讀者說看不懂的註，先一句定義名詞，三個以上的平行項目改成表，補一個本文補的案例（`figure.file`，真的檔名和內容），上方已有的 code 指過去不重貼；L3 `#n-hook-files` 是第一個（2026-10-30 已併進 2.1 正文 `#i1-5`，因為它是主線需要的事實，見 v5.9）。做法見 `.claude/skills/rewrite-with-example/SKILL.md`，規則見第 4 節第 2 段的名詞註）。2026-10-28（v5.7：**側欄目錄不放分組**。側欄的核心觀念底下只列章號 2.1、2.2…，不放 A／B／C 分組列。分組只留在正文的 `p.idea-group` 與閱讀地圖 `nav.map`，那裡有副標說明。原因：側欄同時有段號、字母、章號三套編號，讀起來混亂。L1–L8 同日改完，`styles.css` 刪掉 `.sn-group`、`.sn-g`。見第 4 節「分組與地圖」）。2026-10-28（v5.6：**並列項目一項一行**。一段裡用「；」串起 4 個以上並列的項目（skill、指令、策略、論文、假設），改成 `ul`／`ol`；`check_article.py` 對這種段落印 warn。L1–L8 同日改完。見第 4 節第 2 段「寫因果，不要條列 slide」那一條）。2026-10-28（v5.5：**slide 案例的版本對照**。Slide 拿一個會改版的 repo 當案例時，寫明 slide 對應哪一版、現在是哪一版、改了什麼、為什麼改，讓讀者判斷 slide 的內容還成不成立；L3 2.1 的 Superpowers 是第一個，見第 4 節第 2 段的最後一條）。2026-10-28（**L1、L7、L8 的正文補到 v4.0 密度**：每頁 6–8 章、每章 3–7 分鐘，第 1–4 段各約 30–40 分鐘；L1 加了一章課程範圍（p.9–26）；三頁的 `#iN` 重編號，index chip 與 L3、L6 的連結已同步）。2026-10-28（v5.4：**L1、L7、L8 也改成 v5.0 版面**：全站 L1–L8 都是 5 段；同日稍後再擴寫內容；第 3 節第 7 點、第 4 節的段號說明同步）。2026-10-28（v5.3：**全站一致**。紅字改成依長度配：每章正文每約 200 字 1 處（1–5 處），深入／本文延伸合計最多 1 處，`tldr` 剛好 3 處，架構剛好 1 處；L1–L8 依此重調。每個 code block 都包成 `figure.file`、有 figcaption，輸出也是；上色移到 `code.js`，`l02-readings.html` 也套用同一套樣式。見第 6c 節）。2026-10-28（v5.2：**本文補的案例章**，L3 2.8 mattpocock/skills 是第一個；見第 4 節第 2 段的最後一條）。2026-10-28（v5.1：**紅字重點與 IDE 配色**。`<strong>` 顯示成紅色粗體，標關鍵數字、結論、代價／風險，每章 3–6 處；`<b>` 仍是黑色粗體小標；code snippet 一律是深色編輯器底，`app.js` 依語言上色；inline `<code>` 改成紫色。L1–L8 同日標完。見第 6c 節）。2026-10-27（v5.0：**觀念補充併入核心觀念**，先在 L4 做。詞條改成正文裡的收合註 `details.gloss`（名詞／前情／背景），正文裡的名詞用 `a.tm` 連過去，點名詞就展開；核心觀念的章編號 2.1、2.2…，分成 A／B／C 三組，段首放一張閱讀地圖 `nav.map`；章內的粗體小標加 `id="iN-k"`，目錄多一層；一章超過約 4,000 字就拆（L4 的 Edit 與 execution 拆成 2.3、2.4，共 7 章，上限放寬到 8）。頁面因此只剩 5 段：1 架構、2 核心觀念、3 問題討論、4 動手試試、5 延伸閱讀；同日套用到 L3（7 章）、L5（5 章）、L2（4 章，深入區塊保留，meta 寫「深入與註」）、L6（5 章）；L1、L7、L8 仍是 6 段，等 James 確認後再逐頁改。見第 3、4 節）。2026-10-27（v4.5：「大家的討論」併入第 4 段問題討論的末尾（`div.submit#s-submit`）；延伸閱讀編為第 6 段。全站段落：1 架構、2 核心觀念、3 觀念補充、4 問題討論、5 動手試試、6 延伸閱讀）。2026-10-26（v4.4：全站取消「延伸思考」段，L1–L8 都改完；段落固定為 1 架構、2 核心觀念、3 觀念補充、4 問題討論、5 動手試試、6 大家的討論、延伸閱讀；10-27 再併掉大家的討論）。2026-10-26（v4.3：取消獨立的「延伸思考」段，推論改放在對應章節末尾的「本文延伸」收合區塊，後面的段落編號往前移；slide 留給 assignment 的問題（哪幾招 prompt 過期）直接給本文的判斷；context window 的清單只畫一次、畫完整；見第 3、4 節）。2026-10-26（v4.2：一章太長就拆章；平行的做法用「找法 1：」「改法 2：」編號小標；章首一句地圖；見第 4 節第 2 段）。2026-10-26（v4.1：指令、設定檔、對話一律用 code snippet；每章至少一張圖或表；清單用 ul/ol；見第 4 節第 2 段與新的第 6b 節）。2026-10-25（v4.0：文章要能不看 slides 從頭讀到尾，名詞在第一次出現的地方講清楚，深入區塊併回主線，觀念補充改成查閱詞條；見第 1、4 節。L3、L4 是第一批改寫的範例）。2026-10-23（v3.8：核心觀念的 prose 裡可以放比較圖或表格，見第 4 節第 2 段）。2026-10-22（v3.7：ASD-STE100 依段落分兩檔，推理段落放寬到約 60–70%，見第 5 節）。2026-10-22（v3.6：取消閱讀時間的限制，見第 7 節）。2026-10-22（v3.5：進階題每堂最多 3 題，見第 4 節第 5 段）。2026-10-22（v3.4：觀念補充的條數與閱讀時間上限改為建議，見第 4、7 節）。2026-10-21（v3.3：文章要讓沒看 slides 的人也讀得懂，見第 1 節；閱讀時間上限 16 → 30 分鐘，見第 7 節）。2026-10-19（v3.2：站台搬到 `docs/`；討論改用 GitHub Issues，連結由 `tools/discuss.py` 寫入）。對照的是 L1–L8 的實際格式。第 4 段的基礎題另見 `STYLE_BASIC.md`。

你負責把 Harvard CS2680 的一堂課寫成一篇「架構文章」：`/home/claude/cs2680/docs/lXX.html`。
**範本是 `docs/l05.html`（v5.0 版面、8 章，2026-10-29 擴寫）。先完整讀一遍：結構、class、語氣、密度都照它做。** `l02.html` 只有 4 章、還留著 16 個深入區塊，不要照它的密度；下面寫「照 l02」的地方只是複製固定文字（lede、rg-legend、readmark 等）。

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
   - `ul.meta`：Slides 連結、頁數、頁碼（「PDF 檢視器的頁數」）、閱讀 `span.read-time`、收合區塊 `span.deep-time`（v5.0 的頁面寫「註與延伸」，含 `details.gloss` 與本文延伸；舊頁面寫「深入」或「本文延伸」）、全部展開 `span.full-time`。時間由 `check_article.py --fix-time` 填。
6. `section.tldr`「先看這裡」（`h2#tldr-h`）：`.thesis` 3–4 句、`ul.core` 3 條（`<b>粗體重點。</b>` + 1–2 句）、`.readhow` 讀法，照 l04 的句型：「這篇可以不看 slides 從頭讀到尾：每個名詞在第一次出現的地方就有解釋，由淺入深，頁碼只是出處。想對照 slides，就在讀到頁碼時打開那幾頁；想先帶著問題讀，就先看第 3 段的基礎題。讀書會前用第 3 段的進階題。」
7. `div.layout` > `div.content`：五個段落：1 架構、2 核心觀念、3 問題討論、4 動手試試、5 延伸閱讀（2026-10-28 起 L1–L8 全部如此）。工具仍依頁面有沒有 `#s-background` 決定段號，新頁面一律沒有。
8. `nav.pager`、`p.fineprint`（照 l02 的句型改成這一堂）、`<script src="app.js">`。

## 4. 段落

### 1 架構 `section.part#s-arch`
- `p.kicker`「1 · 架構」+ `h2`（這堂的零件怎麼接在一起）。
- 1–2 張 inline SVG（`figure.diagram`）畫主結構：元件、資料流、層次，或兩種做法的差別。
- `div.prose`：「讀圖重點」2–4 句。

### 2 核心觀念 `section.part#s-ideas` ← 文章的主體
- 3–8 個 `div.idea#iN`（2026-10-27 放寬到 8；`check_discuss.py` 已改）。`h3` 內放 `a.ref`（slide 頁碼範圍）。
- **章名（v5.0）**：「主題：這章的結論」，主題在前（Agent loop、Search tool、Edit tool、Prompt、Context 的成本、Context 管理），冒號後一句結論。`h3` 開頭放章號 `<span class="idea-no">2.3</span>`。正文引用別章一律寫章號（「2.6 會解釋原因」「見 2.4 的註」），不要寫 `i5`、「下一個觀念」。
- **分組與地圖（v5.0）**：章依內容分成 2–3 組，組名寫在 `div.ideas` 裡的 `p.idea-group#g-a`（「A · Loop：agent 的最小單位」），放在該組第一章前面。側欄目錄（`ol.sn-subs`）不放分組，只列章（v5.7）。`header.part-head` 加一句 `p.lede` 說三組各講什麼；header 後面放 `nav.map`：每組一個 `p.map-g`，每章一列 `a.map-row[href="#iN"]`（`span.map-no` 章號、`span.map-t` 主題 + `<small>` 結論、`span.map-m` 頁碼與分鐘）。分鐘用 `check_article.py` 的公式（400 單位／分鐘）算該章收合時的字數，寫法見 WORKFLOW B4。
- **章內小標加 id（v5.0）**：結構性的粗體小標（找法 1–4、改法 1–4、四種策略、五種失敗…）寫成 `<p id="i2-3"><b>找法 1：…。</b>…`，sidenav 的第三層 `ol.sn-sub2s > li > a.sn-sub2` 連到它們，只在該章在畫面上時顯示。每章 4–9 個。
- **名詞註 `details.gloss`（v5.0，取代觀念補充）**：少見的名詞、別堂講過的東西、超出 slide 的背景，放在它第一次出現的那段正文後面，收合：
  ```html
  <details class="gloss" id="n-rag">
    <summary><span class="gloss-k">名詞</span><span class="gloss-t">RAG、vector database、HNSW：semantic search 背後的三個名字</span></summary>
    <div class="gloss-body prose"><p>…2–4 句，每句新資訊…</p></div>
    <!-- v5.8：讀者看不懂的註可以更長：先一句定義，平行項目用 div.table-wrap > table，再放一個 figure.file 案例（標「案例（本文補的）」）；不放 <strong> -->
  </details>
  ```
  `gloss-k` 三種：**名詞**（軟體工程師不一定知道的名詞：JSON Schema、PageRank、exit code、container、SWE-bench）、**前情**（別堂講過、這堂要用的：prefix cache、MCP）、**背景**（和主線無關、slide 沒講的：reasoning model、prompt injection）。正文裡的那個名詞寫成 `<a class="tm" href="#n-rag">RAG</a>`（虛線底線），`app.js` 會在點擊時打開註並捲過去；從別頁連進任何收合區塊也會自動打開。主線的名詞（token、LSP、AST、hunk、冪等）仍在正文裡用一整段講清楚，不收進註；一句就能講完的（CI、formatter、DOM、handle、blast radius）直接在正文括號裡講。
- 舊的 `#tN` 錨點（index、L2、L5、L6 連過來）要保留：放在對應正文段落開頭的 `<span class="anchor" id="t6"></span>`，或直接當 `details.gloss` 的 id（L4 的 `#t8`、`#t11`）。
- 每章是一段連貫的教學，長度由內容決定，但一章超過約 10 分鐘（4,000 字）就拆成兩章（2026-10-26：L4 原本的 i2 拆成 search、edit 與 execution；2026-10-27：edit 與 execution 再拆成 2.3、2.4）。拆章會改 `#iN` 錨點，要同步 index 的 chip、別頁連過來的連結（`grep -o 'l04.html#i[0-9]' docs/*.html`）、本頁基礎題與延伸閱讀裡的 `tk-rel` 連結（2026-10-27 發現 L4 這些連結在上次拆章後沒更新，依連結文字對回正確的章）。
- 章首一句地圖：「這一章先看 A，再把 B 逐一講清楚；下一章講 C」。
- 一章裡平行的好幾種做法，粗體小標用編號：「找法 1：grep 與 glob，依字面找。」「改法 3：search/replace。」每一種的段落順序一致：做法 → 例子（snippet）→ 代價。好幾種做法共用同一個例子（L4 的 edit 四種都改 `RETRY_MS = 500`）。
- 名詞第一次出現就解釋，而且從讀者用過的東西講起（LSP 從 VS Code 的 F12 講起；AST 從「compiler 處理前先讀成樹」講起；search/replace 從 Ctrl+H 講起）。Slide 的術語（anchor）要翻成工具實際的欄位名（`old_string`）。章內用 `<b>粗體小標。</b>` 開頭的段落分節，依「問題 → 名詞解釋 → 機制 → 例子 → 代價 → 證據」的順序走。可以放 `ol`、`figure.file`（指令、設定檔、程式碼，逐行標註）、`figure.diagram`、`div.table-wrap`。
- 名詞第一次出現就解釋（第 1 節）。解釋的順序是由淺入深：先講讀者熟的（shell 指令、git），再講建在上面的（worktree、LSP）。
- 寫因果，不要條列 slide。但 slide 上的「N 個理由」「N 種做法」「N 個步驟」要用 `ul`／`ol` 列出，每一條是 `<b>名稱。</b>` 加一兩句解釋；不要把五個項目塞進一段散文（2026-10-26，L3、L4 的 ol/ul 是範例）。
- **並列項目一項一行**（v5.6，2026-10-28；James 讀 L3 2.1 的 9 個 skill 那段：「是不是要一個 skill 一行比較好閱讀？」）。上一條只管 slide 寫明「N 個…」的清單；這條管所有並列：一段裡有 **4 個以上**並列的項目，每一項是「一個名字 + 它的說明」（skill、指令、flag、檔案、策略、層、論文、假設、失敗型態、限制），就拆成清單，不用「；」串在一句裡。3 項而每一項都有名字和自己的說明，也拆。理由：讀者要能掃名字、數項目、跳到想看的那一項；串成一段時，他得自己找分號。
  1. 引言留在前面的 `<p>`，以「：」結尾，說清單是什麼、有幾項（「Slide p.7 挑了 9 個 skill，每一個的職責：」）。清單後面的話另起一段。
  2. 順序有意義（步驟、層次由上到下、slide 的「五條順序」、由無損到有損）用 `ol`，否則用 `ul`。
  3. 每一項的寫法：名字是一般詞，寫 `<li><b>名稱。</b>說明。</li>`；名字是 code（skill 名、指令、flag、檔名），寫 `<li><code>name</code>：說明。</li>`，不再包 `<b>`。說明一兩句；一項很長時，表示它該是一個粗體小標的段落，不是清單項。
  4. 不拆的：推理的因果鏈（每一句接上一句的結論）、算式的連續步驟、`p.lede` 的分組地圖（下面已經有 `nav.map`）、「相關：」那一行、作答範本的填空欄。推理或算式只是剛好用了 3 個「；」時，在 `<p>` 加 `data-inline` 讓 `check_article.py` 略過。
  5. 紅字的數量不變（第 6c 節）：`li` 算正文，原本在段落裡的 `<strong>` 跟著那一項走。
- **指令、設定檔、程式碼、對話，一律放 code snippet**（2026-10-26 定，見第 6b 節）。`grep -rn "timeout" src/`、`hooks.json`、`/goal "…"`、一段 JSON-RPC 請求，都不能只用 `<code>` 夾在句子裡帶過；要用 `figure.file` 完整寫出來，附輸出與逐行註解。
- 同一個東西（例如 context window 裡有什麼）整篇只畫一次，畫完整（L4 i5 的十格圖），其他地方用一句話指回去，不要每處各畫一個不一樣的縮寫版。
- 機制要交代到「harness 在資料結構上做了什麼」：規則是什麼、改哪一筆、換成什麼文字、什麼時候觸發、代價（例如 prefix cache 失效），附 messages 陣列改前改後的 snippet（L4 i6 的 transformation 是範例）。
- **每章至少一張圖或一張表**（2026-10-26 定）。Slide 上的流程圖、分層圖、比較表、長條圖都重畫成 `figure.diagram` 或 `div.table-wrap`；本文自己整理的也可以畫，figcaption 寫明「本文的整理」。L3 有 11 張、L4 有 15 張（2026-10-26）。
- 「深入」區塊（`details.ex.deep#dN`）：**預設不用**（2026-10-25）。原本放在深入裡的內容（Claude Code 為什麼選 grep、LSP 怎麼建索引、五個執行考量各怎麼做）都是讀者想問的，應該併回主線。只有和主線無關、純粹補充的細節才收合。
- **本文補的案例章**（2026-10-28 定，2026-10-30 改位置；L3 2.2 mattpocock/skills 是範例）：slide 沒有、但和這堂主題直接對照的真實案例（一個 plugin、一套 skill），可以寫成獨立一章，緊接在它對照的 slide 案例後面（L3：2.1 Superpowers → 2.2 mattpocock → 2.3 Caveman），`nav.map` 的 `map-t` 小字標「（本文補的）」，不另立一組放最後；章數仍受 3–8 限制。`h3` 的 `a.ref` 寫「對照 p.N–M」，指向它對照的 slide 頁（`check_article.py` 要求每章有 `a.ref`）；`nav.map` 的 `map-m` 同樣寫「對照 p.N–M · 約 K 分」。章內：先說為什麼拿來對照、事實依哪一天的 repo；和 slide 案例的並排表放在這一組最後一章的末尾（L3 在 2.3 `#i3-8`），章內只寫和鄰章的幾點差別；查閱用的長表（例如 27 個 skill 一覽）收在 `details.ex.deep#dN`「深入」區塊，summary 寫「深入｜標題」+ `<span>查閱用</span>`，`ul.meta` 的 `deep-time` 標籤改成「註、深入與延伸」；案例原文的例子用 `figure.file` 照抄並標來源與日期。tldr 的 thesis、第 2 段的 `p.lede`、`p.fineprint` 都要說明這一章不是 slide 的內容。延伸閱讀是教授的清單，不加這個案例。
- **Slide 案例的版本對照**（2026-10-28 定，2026-10-30 縮短；L3 2.1 的 Superpowers 是範例）：slide 拿一個會改版的 repo、plugin 或產品當案例時，寫之前先抓 repo 對照。有差異就這樣寫：
  1. 介紹案例的那段加一句版本：slide 對應哪一版（依講課日期和 slide 上的細節判斷）、本文比對哪一天、當時最新是哪一版與發布日期；接一句「下面照 slide 講，機制沒有變；改了什麼，本章最後一段交代」。
  2. 章末一個粗體小標「Slide 之後，X 改了什麼」（加 `id="iN-k"`），內容是一段或最多 3 項的清單：沒變的（slide 哪些照讀就對）、改最多的（版本、日期、原因一句）、slide 沒提但後面章節會用到的。原因依 release notes 或 commit 寫；release notes 沒寫原因就不寫。結尾寫「依 repo 的 tag 與 RELEASE-NOTES.md」。
  3. 不放版本對照表、不貼實際的設定檔（James：「版本比較對讀者幫助不大」）。只有 slide 的結論因改版不成立時，才用一張小表把那一項的 slide 版和現在版並排。
  4. 正文裡依 slide 寫的數字（skill 數等）改成「slide 列 N 個，repo 有 M 個」；別章引用這個案例的地方（比較表、基礎題的重點複習）一起更正。`p.fineprint` 加一句比對日期與版本。
  5. 表頭要在 390px 放得下：`th` 是 nowrap，表頭用 `<br>` 分兩行；4 欄以上放不下時，把次要的一欄併進第一欄或最後一欄，寫成第二行的 `<small>`（L3 2.1 的擴充機制表是例子）。
- 選用：一個觀念要比較好幾種做法、或有一組數字時，可以在 `div.prose` 裡放一張 `figure.diagram` 或一個 `div.table-wrap` 表格（格式同第 6 節；`shot_article.py` 會一起截圖，收合的深入區塊裡的也會）。每個粗體小標最多一張，放在它說明的那段前後；slide 沒給的部分在 figcaption 寫明「本文的整理」。例子是 L4（2026-10-23）：i2 的 search 成本曲線與 edit 四種方式對照表、i4 的 lost in the middle 折線、i5 的 Breunig 表與 Lewis 長條圖、d2 的冪等時序圖。

### 3 觀念補充 `section.part#s-background`（v5.0 起不再寫；L1–L8 已全部併入第 2 段的 `details.gloss`，這一節只留作歷史）
- 2026-10-25 起改成**查閱用的詞條**：`header.part-head` 裡加一句 `p.lede`（「第 2 段已經在第一次出現的地方解釋過這些名詞。這裡是查閱用的短版……」）。每條 `dd` 2–4 句，結尾指回第 2 段講解的位置（`見 <a href="#i2">i2</a> 的 search 一節`）。
- 只有和主線無關的背景（例如 L4 的 reasoning model、guardrail 與 prompt injection）才在這裡完整寫。
- `dl.terms`，建議 4–6 條（上限只是建議，`check_discuss.py` 只警告），每條包在 `div#tN`：`dt`（名詞 + `<small>` 一句用途）。既有的 `#tN` 錨點有別頁連過來（index、L2、L5、L6），改寫時保留順序，新詞條加在後面。

### 本文延伸（沒有獨立的段，2026-10-26 起全站如此）
- 超出 slide 的推論放在它所屬章節的末尾，用收合區塊：`div.exlist.deeplist > details.ex.deep#xN`，summary 寫「本文延伸｜標題」+ `<span>不是 slide 的內容</span>`，內容放 `div.exbody.prose`。錨點用 `#x1`…依全頁順序編號；一個章節可以有好幾個。
- 不再寫 `section#s-beyond`。舊頁面的「延伸思考」已在 2026-10-26 全部併入章節。段落編號：1 架構、2 核心觀念、3 問題討論、4 動手試試、5 延伸閱讀（L1–L8 都是）。正文提到段落用這個編號（「第 3 段的基礎題」「第 4 段有實測」）；跨頁引用時寫對方頁面的編號（L2 寫「L4 第 4 段」）。首頁「怎麼讀」不寫段號，寫「問題討論」段。
- `ul.meta` 有一行「本文延伸 `span.deep-time`，收合」；頁面同時有「深入」區塊時寫「深入與本文延伸」；v5.0 的頁面寫「註與延伸」（`deep-time` 算進 `details.deep` 與 `details.gloss`）。時間由 `check_article.py --fix-time` 填。
- **只放離主線的東西**（v5.9）：對外部評論或 benchmark 的查證、純粹的推算。章的論證需要的事實、公式、判斷一律寫在正文，用粗體小標分節（L3 2.6 的 Amdahl 一段、2.2 的「沒有 hook，拿什麼保證」）。一章最多 2 個本文延伸，合計長度不超過該章正文；超過就併回正文或刪。
- 推論要有根據，不要誇大。Slide 留給 assignment 的問題（例如 L4 p.39「哪幾招 prompt 過期」），本文直接給判斷，標明「本文的判斷（年月）」，不要讓讀者自己去找。
- 工具：`check_article.py` 不再要求 `#s-beyond`；`add_lecture.py`、`discuss.py` 依頁面有沒有 `#s-beyond` 決定段號（新頁面一律沒有）。

### 3 問題討論 `section.part#s-discuss` ← 最重要
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

### 4 動手試試 `section.part#s-try`
- `p.lede` 一句說明範例依據。`div.exlist` 內 2–4 個 `details.ex`（預設收合）。`summary` 寫標題 + `<span>頁碼</span>`，內容 `div.exbody`。
- 工具類講次：可以照打的設定檔、指令、程式碼（`figure.file` > `figcaption` + `pre > code`）。
- 觀念類講次（Part II 多數是）：小練習（估算、設計、用 python 驗證一個現象），附解答。
- 範例要正確可用；產品相關內容以官方文件為準並寫明日期。

### 到 GitHub 寫你的答案 `div.submit#s-submit`（在第 4 段的最後，2026-10-27 起不再是獨立的段）
- 放在 `section#s-discuss` 的結尾、`div.quiz` 之後。新頁面只寫空殼：
  ```html
        <div class="submit" id="s-submit">
          <h3 class="subhead">到 GitHub 寫你的答案</h3>
        </div>
  ```
- 內容（lede、這堂與全部討論串的連結、留言方式）由 `tools/discuss.py` 填入。

### 5 延伸閱讀 `section.wrap#wrap`
- `p.kicker`「5 · 延伸閱讀」+ `h2` 延伸閱讀；`p.rg-intro`：教授列了幾篇、官方清單連結（`readings/<mon-dd>.html`）。
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

**推理段落，約 60–70%**：「先看這裡」的 thesis、第 1 段讀圖重點、第 2 段核心觀念（含本文延伸與 `details.gloss`）、進階題的參考觀點。

1. 一句可以講兩三件有關係的事，但關係要用連接詞寫明：因為、所以、但、因此、也就是、反過來、這表示。
2. 句子要接得上：下一句從上一句的結論往下講，不要每句都換主詞重新開始。
3. 句長 ≤ 70 字（英文詞算 1 字）。超過就拆，拆開後保留連接詞。
4. 一段講一個論點，最多 6 句。段落開頭一句說這段要講什麼。

**查閱段落，約 75–80%**：`details.gloss` 的名詞註、基礎題的參考答案與「帶走這幾點」、第 4 段動手試試、延伸閱讀摘要。

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

## 6c. 強調與配色（v5.1，v5.3 改成全站一致）

2026-10-28 定（James：「整份排版有辦法有更多顏色對比嗎？例如 code snippet 有類似 IDE 的顏色，然後字體會有 bold and red font」）。

- **兩種粗體，分工不同。** `<b>` 是黑色粗體，只當小標與條目名稱（`<b>找法 1：…。</b>`、`ul.core` 的 `<b>重點。</b>`）。`<strong>` 是紅色粗體，標「掃過去也該看到」的短語。
- **紅字標什麼**，依優先順序：
  1. 撐起論點的數字：結果、比較、成本（`<strong>解出 18.0%</strong>`、`<strong>97.6% 是 cache read</strong>`）。
  2. 這一章的結論，寫成短語（`<strong>必須強制的事，用 hook 或權限</strong>`）。
  3. 主要的代價、風險、陷阱（`<strong>有損又不可逆</strong>`、`<strong>回成功但改錯地方</strong>`）。
- **數量依長度，全站同一個密度**（v5.3；James：「要一致」）：
  - 每章的正文（不含 `details` 收合區塊、code、圖、表）每約 200 字 1 處：目標 = round(字數 ÷ 200)，至少 1、最多 5；比目標少 1 也可以。L1、L7、L8 的章短，所以多半 1–2 處；L3、L4 的章長，所以 4–5 處。
  - 深入／本文延伸區塊：每章合計最多 1 處，不算進上面的目標。
  - `section.tldr` 剛好 3 處；第 1 段架構的 prose 剛好 1 處。
  - 一句最多一處；同一段兩處只用在兩個數字互相比較時。
  - 要刪減時，留「讀者不看上下文也懂」的那一處；兩個互相比較的數字只留一個時，改標結論。
- **長度**：一個短語，約 25 個中文字以內；不要整句標紅。
- **位置**：只在正文 prose、`.thesis`、`ul.core` 的說明文字。不放在標題、`summary`、`figcaption`、圖、表、code、`details.gloss`、問題討論、動手試試、延伸閱讀。不和 `<b>`、`<a>`、`<code>` 互相嵌套；要包住一個 `a.tm` 或 `<code>` 時，整個元素都在紅字裡。
- **每個 code block 都長一樣**（v5.3）：一律寫成 `figure.file` + `figcaption`，沒有例外。指令的輸出也是，caption 寫「fp_order.py 的輸出」；沒有檔名的指令寫「terminal：做什麼」。
- **Code snippet 的配色**：`pre` 一律是深色編輯器底（亮、暗模式都是），`figcaption` 是編輯器的分頁列。`code.js` 載入時依 figcaption 的副檔名和內容猜語言並上色：`$` 指令、`#`／`//` 註解、`←` 註解、字串、JSON／YAML 的 key、數字、flag、diff 的增刪行、`FAILED`／`error` 等字。猜錯時在 `code` 加 `class="lang-json"`（json、py、js、sh、shell、yaml、md、diff、text）。HTML 裡仍然只寫純文字，不手寫 `span`。
- 顏色都定義在 `styles.css` 的 `:root`（`--key`、`--icode-*`、`--cd-*`），亮、暗模式各一組；要調顏色只改這裡。`l02-readings.html` 有自己的 inline 樣式，複製了同一組值，改顏色時兩邊一起改。
- 新講次的頁面在 `app.js` 後面也要載入 `<script src="code.js"></script>`（範本 l02.html 已經有）。
- `check_article.py` 會檢查紅字的位置（錯了是 PROBLEM），並依上面的公式檢查每章、`tldr`、架構的紅字數（不符是 warn，要修到沒有 warn）。

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

Part II（依課程網站 2026-10-28 的時程，可能調整；PDF 檔名等 slides 公開後再填）：

| 日期 | 英文標題 | 備註 |
|---|---|---|
| 10-19 | Efficient LLM serving basics I: intro to LLMs | |
| 10-21 | Efficient LLM serving basics II: intro to GPUs | |
| 10-26 | Assignment feedback and Assignment 3 student sharing | 學生分享 |
| 10-28 | Efficient LLM serving basics III: batching, paging, and parallelism | |
| 11-02 | Efficient LLM serving: speculative decoding | |
| 11-04 | Efficient agentic systems: scheduling and prefix caching | |
| 11-09 | Guest lecture: Why Infrastructure sets the pace of AI (Meta) | 客座 |
| 11-11 | Efficient LLM serving: pruning and quantization | |
| 11-16 | Efficient LLM serving: KV-cache optimization and model architectures | 學生主講 |
| 11-18 | Student sharing III: engine optimizations and agent-engine co-design | 學生主講 |
| 11-23 | Efficient agentic system: routing and load balancing | |
| 11-30 | Efficient agentic systems: others | |
| 12-02 | Student sharing IV | 學生主講 |
| 12-07 | Final project poster and demo | |

10/05 客座（Snowflake）沒有公開 slides；10/14 Advanced agent design II 是學生主講。兩堂目前都沒有頁面。
