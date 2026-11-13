# CS2680 架構文章撰寫規範（v7.0）

更新紀錄在 `guide/CHANGELOG.md`。

你負責把 Harvard CS2680 的一堂課寫成一篇「架構文章」：`/home/claude/cs2680/docs/lXX.html`。
**範本是 `docs/l05.html`（v7）。先完整讀一遍：結構、class、語氣、密度都照它做。** 下面寫「照 l02」的地方只是複製固定文字（lede、rg-legend、readmark 等）。

只寫你負責的 `lXX.html`。不要改 `styles.css`、`app.js` 和其他頁面；跨頁的改動由 `tools/add_lecture.py` 處理。不要 commit、push，不要寫入 memory。

## 0. v7：依想法的重要性重組（2026-11-03，L5 先行）

範本是 `docs/l05.html`，L1–L8 都已是這個版面（2026-11-03）。做法照 `.claude/skills/idea-first-lecture/SKILL.md`，每堂的取捨記在 `guide/V7_DECISIONS.md`。v7 和下面第 1–9 節衝突時，以這一節為準；沒提到的照舊。

- **目標換了。** 讀完要能判斷、能設計，不是記住 slides 的分類。Slides 是素材：順序不必照，頁碼不必寫（`h3` 不放 `a.ref`），可以刪。
- **份量的排法。** 用三個問題排每個想法：會不會改變讀者的決定？忽略它的代價多大、能不能挽回？能不能從別的想法推出來？再看它多久會過時。最上游的決定排最前面；能推出來的降級；會過時的細節收成查閱。
- **章的順序：有依賴就照依賴排，重要性不靠章序表達**（2026-11-12，James 讀 L6b：「閱讀順序沒有那麼順」，他自己畫的是 transcription → memory notes → memory representation → injected memory 四層）。先判斷這堂的想法屬於哪一種：
  - **彼此獨立**（L5 的幾個架構判斷、L6 的攔錯）：誰先誰後不影響理解，照上一條的份量排。
  - **有依賴**（資料流、層次、pipeline：後一個東西建在前一個上，例如 memory 的四層、inference 的 prefill → decode）：照依賴順序排，由下往上或由上游到下游。每一章開頭先說「這一層是什麼東西」（一張表、一條筆記、一份索引），再講它的判斷。
  判斷法：把各章的主題寫成名詞，問「不先講 A，B 講得清楚嗎」。有兩條以上這種邊，就是有依賴。也可以看 `docs/dag.json` 這堂的節點之間有沒有 deps。另一個訊號是往後指的名詞：一個名詞第一次出現時，只能寫「（第 N 章）」指到後面的章，表示這兩章的依賴倒過來了（L10 原本的量測在第 4 章，counter 用到第 5 章才講的 Tensor Core，2026-11-12 對調）。往後指的如果只是「後面會用到」的預告，不算。
  有依賴時，最重要的判斷可能落在中間的章。重要性改用三個地方表達：「先看這裡」先講結論、`nav.map` 的小字、紅字。不要為了把重要的排前面，讓讀者先讀欄位、才知道東西在哪。
  一堂只有一張地圖。兩張圖都說自己是全貌時（L6b 原本的六站圖與四層圖），一張當章的骨架，另一張降成某一章裡的回顧，圖上標的章號要照頁面的順序遞增。
  （L6b 原本照重要性排成「要不要記 → 時間與來源 → 檢索 → 放在哪裡」，六站圖標的章號是 1、2、4、3、2、2；wiki 分在三章講。2026-11-12 改成四層加一章跨層的操作，取捨在 `V7_DECISIONS.md`。）
- **做法從第一性原理推出來，不敘述「誰怎麼做」**（2026-11-11，James 讀 L6b dreams 那張圖：「寫了 Anthropic 怎麼做，但沒告訴我為什麼、trade-off」「盡量不要敘述這種用記憶式的知識，而是第一性原理去解釋做法」）。講一個做法、一個產品功能、一家公司的設計時，順序是：
  1. 問題有哪些性質（例：歸納有損、沒辦法當場驗、錯了會滾大）。
  2. 從這些性質推出做法（所以原本的不動、結果另存）。
  3. 這個做法的代價，以及什麼情況下選另一邊（成本、多一個切換步驟、人審或自動）。
  4. 最後才拿產品當例子，說它對上推論的哪一部分；產品的參數（上限、header、版本）不是重點，只留讀者做決定用得到的。
  「X 公司有個功能叫 Y，它的做法是 A、B、C」這種句子，讀者只能背，換一個產品就用不上；讀完要能自己推出 A、B、C。推論是本文自己的就標「本文的推論」，官方有說理由就引官方的。題庫也一樣：題幹問「為什麼這樣設計、不這樣會怎樣」，不問「某產品怎麼做」。
- **補課程漏掉的。** 論證不完整的地方、2025–2026 年改變結論的業界經驗或論文，查原始來源後補成正文的章，不另外標示（見下一條）。只有一家公司的經驗要寫明不是對照實驗。
- **不提 slides 怎麼寫**（2026-11-13，James：「可以不用特別提原本 slide 怎麼寫了，我幾乎重寫了一半以上的內容」）。正文直接講內容，不講它在課程裡的樣子：
  - 不寫「課程列了五種…」「Slides 的例子是…」「課程把它分成…」「講者說…」。改成直接講：「常見的有五種…」「例如…」「分成…」。
  - 不標「本文補的」（`nav.map` 小字、章內小標、側欄、圖說都不標），lede 也不寫「不照 slides 的順序」「標本文補的是課程沒講的」。哪些是 slides 有的、哪些是後來加的，讀者不需要知道。
  - 不寫 slides 的筆誤、兩個數字對不上、哪一頁沒交代。本文用查證過的那個數字，直接寫；對不上又查不到原始來源的數字就不用。
  - 不寫頁碼（`summary` 的 `<span>p.N</span>`、「和 p.18 一樣」都不寫）。
  - **留著的**：`ul.meta` 的 Slides 連結；`p.fineprint` 的取材與版權聲明；「本文的判斷」「本文的推論」（區分查得到的事實和自己的推論，和 slides 無關）；code 範例的「輸出是示意」「註解是本文加的」；數字只出自 slides、查不到原始來源時，圖說留半句出處（「數字取自課程的 slides」）。課程本身就是主題的地方照寫（L1 的課程範圍與作業、L11 的作業回饋）。
  - 進度：L1–L10（含 L6b）都照這條改了（2026-11-13）。L11 沒改：那一堂講的就是課程對自己學生作業的統計，「課程看到…」「slides 沒有標…」是資料的出處與限制，照留。
- **核心觀念開頭不放章節清單**（2026-11-13，James：「應該把核心觀念 bullet point 拿掉，直接進入正文」）。`section#s-ideas` 開頭只有 `header.part-head`（kicker、h2、`p.lede`），接著就是 `div.ideas`；不再寫 `nav.map`。章的清單由左邊的側欄提供。原本寫在 `nav.map` 的分組名（一定要會、需要時查）和每章小字跟著拿掉，各章怎麼排、哪幾章先讀寫在 `p.lede` 一段話裡；本節其他地方提到 `nav.map` 的小字、分鐘數都停用。
- **頁面三段**（2026-11-09 拿掉問題討論；2026-11-13 延伸閱讀縮成原文出處）：1 核心觀念、2 動手試試、3 原文出處。題目放在每一節後面的小測（`guide/QUIZ.md`）。沒有「架構」段；`section#s-ideas` 開頭放 `header.part-head` 與 `nav.map`。
- **章**：`h3` 寫「主題：主張」，`span.idea-no` 只放 1、2、3…。章依份量分組（`p.map-g`），組名照內容取，例如「一定要會」「要用時會做」「底層」「要防的」「需要時查」。最多 10 章。
- **圖優先**：講架構、流程、狀態、時序的地方都要有圖，圖裡的專有名詞用英文。要逐列比較的數字或條目用表。算式先定義每一項，再給公式，再列逐列算好的表。
- **刪減的準則**：不改變決定的、能從主線推出來的、很快會過時的、和別處重複的，刪掉或收進最後一章「目錄」或 `details.gloss`（`gloss-k` 寫「查閱」）。
- **錨點**：別頁連進來的錨點要接到新章節，或在相同內容的段落保留同一個 id。`h1` 不改。
- **跨堂引用**：文字裡不寫別堂的章號（「L4 2.6」），寫 L4〈概念名〉再放連結，章號會變。別堂是主場的主題，一兩句帶過再連過去，頁面仍要能單獨讀懂。
- **一堂不綁一份 slides**（2026-11-10，James：「以觀念去 split，而不是 slide 去 split；未來 lesson 跟課程投影片不需要一對一」）。堂是觀念的單位：一份 slides 講了兩個彼此不依賴的觀念時拆成兩堂，幾份 slides 講同一個觀念時也可以併成一堂。判斷用觀念 DAG（`guide/DAG.md`）：兩組章的節點之間沒有「要先懂」的邊，就是兩堂。第一例是舊 L6：可靠性的四個節點和 memory 的五個節點互不依賴（memory 接在 L2 的 persistent text 與 L4 的 context 上），拆成 L6〈Agent 可靠性〉與 L6b〈Agent memory〉。
  - 編號：拆出來的堂沿用 slides 的編號加字母（`l06b`、L6b），排在原堂之後。別堂的編號、檔名、讀者的已讀與作答紀錄都不動（2026-10-21 定的「不改講次編號」照舊）。
  - 每堂要能單獨讀：tldr 和 `part-head` 的 lede 說這堂和另一堂怎麼分；用到另一堂的觀念時寫 L6〈章名〉並連過去，名詞在本堂第一次出現的地方重新解釋（run、harness、context 不能靠另一堂解釋過）。
  - 目錄章、動手試試、延伸閱讀、fineprint 的來源也依觀念分到兩堂；延伸閱讀的 `rg-intro` 說另外幾篇在哪一堂。`ul.meta` 加一列「同一份 slides」連到另一堂；eyebrow 補「和 L6 同一份 slides」。`data-pdf`、`data-pages-total` 照原 slides 填（頁碼連結要驗證得過）。
  - 做法見 `WORKFLOW.md` K。
- **新講次（L9 起，2026-11-06）**：沒有舊頁面，骨架用 `tools/new_lecture.py`。延伸閱讀摘要的「跟這堂課的關係」連到本頁的章。一堂有兩份 deck 時（L10）合成一篇，meta 一份一行。


## 1. 定位

- **文章是主體，slides 是輔助**（2026-10-25 定，取代之前「配著 slides 讀」的定位）。讀者要能不看 slides 從頭讀到尾，讀完就跟上這堂的內容；頁碼只是出處，想對照時再打開。原因：只看 slides 吸收效果不好，教授給的名詞（semantic search、glob、LSP、hook、proxy）在 slide 上沒講清楚，成員要靠一問一答才懂，所以文章要把這些問答先寫進去。
- **由淺入深、流暢連貫。** 每一章從讀者已經知道的東西出發（一個 model 單獨能做什麼 → 加 tool → 加 loop），再往下走。章與章、段與段要接得上：每章開頭一句說這章從哪裡來，段落開頭一句說這段要講什麼。
- **業界的詞優先，先接上讀者已經會的東西。**（2026-11-13，James：「你應該優先使用業界的 term」）一節要講的東西，業界已經有名字（RAG、semantic search、rerank、metadata filter、ranking signal），就在這一節的第一句用那個名字，再講這裡和它差在哪裡。不要另取一個名字把它包起來：讀者要先學新詞，再自己認出「這就是 RAG」。業界的詞有三個好處：讀者可能已經會、查得到、和同事講得通。只有業界沒有名字時才自己取，取了要標「本文的整理」。寫的順序是「已知 → 只靠已知哪裡不夠 → 新增的部分」。起因：L6b 第 4 章把 RAG 的 retrieve 寫成「五個訊號，放在不同的位置」，整章沒有出現 RAG 這個詞，James 讀完問「這不就是 RAG 流程嗎？」。
  - **讀者已知的詞（草稿，James 可以增刪）**：這些詞是什麼，讀者知道；直接拿來當起點，最多附半句提醒。它們的實作細節讀者不一定會，用到細節時照下一條講清楚。清單：LLM、token、prompt、context window、embedding、vector DB、RAG、semantic search、top-k、API、JSON、SQL（`WHERE`、`ORDER BY`）、cache、git、CI、container。
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
6. `section.tldr`「先看這裡」（`h2#tldr-h`）是這一堂的**導讀**，不是摘要（2026-11-11 James 定；起因是程度落後的組員反應沒有案例、看不懂，而 11-07 放寬長度之後它長成了 1,000 字以上的小文章）。固定四塊：(1) `p.thesis` 一段案例，「先看一個例子。」開頭，一個人、一個 agent 或一個系統、一件出錯或要決定的事，用平常的話寫，這堂的術語不在案例裡第一次出現就不解釋；(2) `p.thesis` 一段，說這堂回答的問題（`<strong>` 標出），結尾預告「下面三條是這堂的判斷」；(3) `ul.core` 3 條，`<b>粗體判斷。</b>` 加兩到四句，每一條都回到同一個案例，句尾標去哪一章看；(4) `p.readhow` 一行指路，交代三條沒涵蓋的章，以及真的有的前置要求（例如 l03 的「建議先讀 L2 和 L4」）。標準是讀完知道這堂的三個判斷是什麼、去哪一章看為什麼，**不要求只讀導讀就能自己推出來**：每條最多留一個撐起判斷的數字，實驗設定、算式、例外條件留給正文；前幾堂講過的機制（例如 model 不記事、harness 每步重送）不在導讀重講，除非它就是這一堂的主題（L4）。案例盡量用正文已經有的例子，並在用到它的章開頭接回來，叫它「『先看這裡』的例子」。審查照 `REVIEW_READABILITY.md` 的 tldr 單獨審，審查者的讀者設定加一句「程度比較落後的組員」，BLOCK 只留三種：會讀錯意思、名詞沒交代到那一句讀不下去、例子和主張對不上；沒寫推導不算。
7. `div.layout` > `div.content`：五個段落：1 架構、2 核心觀念、3 問題討論、4 動手試試、5 延伸閱讀（2026-10-28 起 L1–L8 全部如此）。工具仍依頁面有沒有 `#s-background` 決定段號，新頁面一律沒有。
8. `nav.pager`、`p.fineprint`（照 l02 的句型改成這一堂）、`<script src="app.js">`。

## 4. 段落

### 1 架構 `section.part#s-arch`
- `p.kicker`「1 · 架構」+ `h2`（這堂的零件怎麼接在一起）。
- 1–2 張 inline SVG（`figure.diagram`）畫主結構：元件、資料流、層次，或兩種做法的差別。
- `div.prose`：「讀圖重點」2–4 句。

### 2 核心觀念 `section.part#s-ideas` ← 文章的主體
- 3–8 個 `div.idea#iN`（2026-10-27 放寬到 8）。`h3` 內放 `a.ref`（slide 頁碼範圍）。
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
- （2026-11-13 起不再標「本文補的」，下面講標示的部分停用，見第 0 節〈不提 slides 怎麼寫〉。）**本文補的案例章**（2026-10-28 定，2026-10-30 改位置；L3 2.2 mattpocock/skills 是範例）：slide 沒有、但和這堂主題直接對照的真實案例（一個 plugin、一套 skill），可以寫成獨立一章，緊接在它對照的 slide 案例後面（L3：2.1 Superpowers → 2.2 mattpocock → 2.3 Caveman），`nav.map` 的 `map-t` 小字標「（本文補的）」，不另立一組放最後；章數仍受 3–8 限制。`h3` 的 `a.ref` 寫「對照 p.N–M」，指向它對照的 slide 頁（`check_article.py` 要求每章有 `a.ref`）；`nav.map` 的 `map-m` 同樣寫「對照 p.N–M · 約 K 分」。章內：先說為什麼拿來對照、事實依哪一天的 repo；和 slide 案例的並排表放在這一組最後一章的末尾（L3 在 2.3 `#i3-8`），章內只寫和鄰章的幾點差別；查閱用的長表（例如 27 個 skill 一覽）收在 `details.ex.deep#dN`「深入」區塊，summary 寫「深入｜標題」+ `<span>查閱用</span>`，`ul.meta` 的 `deep-time` 標籤改成「註、深入與延伸」；案例原文的例子用 `figure.file` 照抄並標來源與日期。tldr 的 thesis、第 2 段的 `p.lede`、`p.fineprint` 都要說明這一章不是 slide 的內容。延伸閱讀是教授的清單，不加這個案例。
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
- `dl.terms`，建議 4–6 條（上限只是建議），每條包在 `div#tN`：`dt`（名詞 + `<small>` 一句用途）。既有的 `#tN` 錨點有別頁連過來（index、L2、L5、L6），改寫時保留順序，新詞條加在後面。

### 本文延伸（沒有獨立的段，2026-10-26 起全站如此）
- 超出 slide 的推論放在它所屬章節的末尾，用收合區塊：`div.exlist.deeplist > details.ex.deep#xN`，summary 寫「本文延伸｜標題」+ `<span>不是 slide 的內容</span>`，內容放 `div.exbody.prose`。錨點用 `#x1`…依全頁順序編號；一個章節可以有好幾個。
- 不再寫 `section#s-beyond`。舊頁面的「延伸思考」已在 2026-10-26 全部併入章節。段落編號：1 架構、2 核心觀念、3 問題討論、4 動手試試、5 延伸閱讀（L1–L8 都是）。正文提到段落用這個編號（「第 3 段的基礎題」「第 4 段有實測」）；跨頁引用時寫對方頁面的編號（L2 寫「L4 第 4 段」）。首頁「怎麼讀」不寫段號，寫「問題討論」段。
- `ul.meta` 有一行「本文延伸 `span.deep-time`，收合」；頁面同時有「深入」區塊時寫「深入與本文延伸」；v5.0 的頁面寫「註與延伸」（`deep-time` 算進 `details.deep` 與 `details.gloss`）。時間由 `check_article.py --fix-time` 填。
- **只放離主線的東西**（v5.9）：對外部評論或 benchmark 的查證、純粹的推算。章的論證需要的事實、公式、判斷一律寫在正文，用粗體小標分節（L3 2.6 的 Amdahl 一段、2.2 的「沒有 hook，拿什麼保證」）。一章最多 2 個本文延伸，合計長度不超過該章正文；超過就併回正文或刪。
- 推論要有根據，不要誇大。Slide 留給 assignment 的問題（例如 L4 p.39「哪幾招 prompt 過期」），本文直接給判斷，標明「本文的判斷（年月）」，不要讓讀者自己去找。
- 工具：`check_article.py` 不再要求 `#s-beyond`；`add_lecture.py` 依頁面有沒有 `#s-beyond` 決定段號（新頁面一律沒有）。

### 3 問題討論（2026-11-09 停用）
- 頁面不再有 `section#s-discuss`：基礎題、進階題、自我檢查、GitHub 區塊都拿掉了。題目改放在每一節後面的小測（`guide/QUIZ.md`）。舊規則在 git 歷史。

### 4 動手試試 `section.part#s-try`
- `p.lede` 一句說明範例依據。`div.exlist` 內 2–4 個 `details.ex`（預設收合）。`summary` 寫標題 + `<span>頁碼</span>`，內容 `div.exbody`。
- 工具類講次：可以照打的設定檔、指令、程式碼（`figure.file` > `figcaption` + `pre > code`）。
- 觀念類講次（Part II 多數是）：小練習（估算、設計、用 python 驗證一個現象），附解答。
- 範例要正確可用；產品相關內容以官方文件為準並寫明日期。

### 3 原文出處 `section.wrap#wrap`（2026-11-13 起；之前是「延伸閱讀」）

James：「其實沒人會去看延伸閱讀，光看完原文就花時間了。」這一段只給查閱用，越短越好：

- `p.kicker`「3 · 原文出處」+ `h2` 原文出處；`p.rg-intro` 一到兩句：教授列了幾篇、官方清單連結（`readings/<mon-dd>.html`），結尾固定寫「要對照原文時從這裡找，不必讀；本文引用的其他來源列在頁尾。」
- 一個 `ol.rg.rg-src`，不分組。每篇一個 `li`：`a.rg-t`（標題，連原文）+ `span.rg-meta`（作者或出處 · 類型 · 年份）。
- 不寫等級（必讀／推薦／選讀）、時間估計、一句定位、導讀、最短路徑，也不寫摘要。舊的摘要（`details.rg-dg`）與 `docs/l02-readings.html` 在 2026-11-13 刪掉，要找就看這天之前的 commit；`STYLE_DIGEST.md`、`tools/insert_digest.py` 停用。
- 選用：`p.rg-fn` 列本文範例的依據（官方文件）。
- 正文要引某一篇時，在句子裡直接放原文連結，不要寫「見延伸閱讀」。
- `label.readmark` 加 `input#read-box`（照 l05）。

## 5. 語言：繁體中文 + 英文術語，ASD-STE100 依段落分兩檔

2026-10-22 放寬（James 讀 L4 覺得卡）。原因：「一句只講一件事」把推理的因果切成好幾句，句子之間的「所以、但是」常常消失，讀者要自己接回去。中文少了英文的冠詞、代名詞與時態幫忙串句，拆短之後更像條列。L4 第 1–4 段是第一個照新規則改寫的範例。

**可讀性優先於長度**（2026-11-07 James 定）。這份規範、`STYLE_BASIC.md`、`STYLE_DIGEST.md` 裡所有的句數、字數、段長（「1–2 句」「≤ 70 字」「最多 6 句」「≤ 60 字」）都是提醒，不是上限。壓短會讓讀者看不懂、要回頭找、或要另外問時，就寫長。原因是 James 說的：原本壓字數和句數是為了省閱讀時間，可是讀不懂反而花更多時間。起因是 L1 tldr：照「每條 1–2 句」壓出來的「聊天是 1 次、750 token、105 token」，單獨審查時四條都是 BLOCK，補足推理後有兩條變成 3 句。`check_article.py` 的 `LONG(n)` 只列出長句給你看一次，不必修到零；要拆，只拆拆了不會斷掉因果的句子。

**推理段落，約 60–70%**：「先看這裡」的 thesis、第 1 段讀圖重點、第 2 段核心觀念（含本文延伸與 `details.gloss`）、進階題的參考觀點。

1. 一句可以講兩三件有關係的事，但關係要用連接詞寫明：因為、所以、但、因此、也就是、反過來、這表示。
2. 句子要接得上：下一句從上一句的結論往下講，不要每句都換主詞重新開始。
3. 句長約 70 字（英文詞算 1 字）是提醒。超過時先看能不能拆，拆開後保留連接詞；拆了會斷掉因果就不拆。
4. 一段講一個論點，約 6 句。段落開頭一句說這段要講什麼。論點需要更多句才講得清楚，就寫更多句。
5. **表格格子也是句子**（2026-11-06 定，起因 L6 第 2 章「Anthropic（2026-03）：穩定偏正面。單一公司的經驗」）。格子裡放的是主張、原因、做法時，寫成有主詞的完整句，而且要回答它那一欄的欄名（欄名「為什麼」就要有機制）。放不下就把主張留在正文，格子只放標籤。引用要帶結論：「Anthropic 2026-03 的 harness 實驗：agent 替自己的成果打分時穩定給高分」，不能只有出處加片語。保留語（單一公司、不是對照實驗、數字會變）放句尾括號，不另起一句，否則讀起來像第二個原因。`check_article.py` 對格子有 R5、R6 兩條 warn；完整的審查見 `REVIEW_READABILITY.md`。

**查閱段落，約 75–80%**：`details.gloss` 的名詞註、基礎題的參考答案與「帶走這幾點」、第 4 段動手試試、延伸閱讀摘要。

1. 一句只講一件事。描述句 ≤ 40 字（英文詞算 1 字）。
2. 一段最多 4 句。

**兩檔都適用**：

1. 主動語態，不寫「被」。
2. 標準術語保留英文：context window、harness、subagent、prefix cache、KV cache、prefill、decode、batching、compaction、benchmark、throughput、latency 等。第一次出現可加一句中文說明。
3. 不用填充詞（其實、基本上、非常、相當、可以說、事實上、簡單來說）、成語、破折號插入語、「不是 X，而是 Y」句型。
4. 數字用阿拉伯數字，保留單位。每個數字前面寫它量的是什麼，有對照就把倍數或差距算好，並讓讀者看得出它撐起哪個結論；兩組以上並排就做成表或圖，不要把一張表塞進一句話。Tldr 和摘要只留撐起論點的一兩個數字（2026-11-07，起因 L1 tldr「聊天是 1 次、750 token、105 token」；審查時是 `REVIEW_READABILITY.md` 的 R12）。
5. 全形標點；中英文之間半形空格。新寫的檔案或片段先跑 `tools/punct.py FILE --diff` 看它會改什麼，再不帶 `--diff` 執行。**不要對既有頁面整頁跑**：頁面裡的數學式與英文片語（`× (1 + 2)`、`Fail?`）要維持 ASCII，2026-10-19 的規則版本已經避開大多數，但仍先看 diff。
6. HTML 特殊字元要跳脫（`&lt;`、`&amp;`）。

## 6. 圖（inline SVG）

- `figure.diagram > div.scroll > svg[viewBox][role="img"][aria-label]` + `figcaption`。
- 只用 styles.css 的 class，不寫死顏色，svg 內不放 `<style>`。顏色在 `:root` 有亮、暗兩組。
- **v6.0 畫法（2026-11-02；2026-11-03 起 L1–L8 的核心觀念都用這個畫法，新圖一律用它，`tools/dg.py` 是 helper）：**
  - 方塊填色、沒有外框：`dg-n-focus`（深紅底白字）、`dg-n-a` 青、`dg-n-b` 黃、`dg-n-c` 藍、`dg-n-d` 粉、`dg-n-n` 灰。分格的底用 `dg-panel`。
  - 深紅只標這張圖要看的地方，通常一個：`dg-n-focus`、`dg-link-key`、`dg-k`、`dg-l-key`。其他方塊用淺色。
  - 淺色要有意義（角色、層級、共享的中介、出問題的節點），意義不明顯就寫進 figcaption。Figcaption 提到顏色時用這裡的色名。
  - 連接線用 `dg-link`（灰）、優先走直角，同一層用一條匯流線，不畫一束斜線。只有全連接這類畫法本身就是重點的圖才用斜線。生命線用 `dg-soft-link dg-dash`。箭頭 marker 的 fill 用 `dg-fill-link`、`dg-fill-key`。
  - 文字：標題 `dg-h`，方塊內 `dg-l`（15px）、`dg-l-on`（focus 內）、小方塊 `dg-ls`（13px），說明 `dg-c`、粗體 `dg-cb`，等寬 `dg-mn`。不小於 12px，一般不小於 13px。
  - **圖優先（v6.1）。** 講架構、流程、狀態機、時序、slide 上有圖的地方，每個都要有圖：一種架構一張，參考 slide 一頁一張，內容相近的可以併成一張小格圖（L5 2.5 的六種拆錯）。圖說得出來的就從文字拿掉，不要兩邊都寫：清單、例子欄、每種架構的「三張圖的答案」都移進圖。架構圖底部放一條 Task / Control / Comms 的摘要（深紅細條加 `dg-c`、`dg-cb`），對應 slide 的頁底。表只留圖放不下的欄（原因、預防、代價）。
  - **圖裡的專有名詞用英文（2026-11-03）**：heartbeat、lease、fencing token、network partition、read-only、merge、summary 這類有標準英文名稱的詞，在圖裡寫英文；解釋性的短句可以用中文。正文第一次出現時照舊附中文說明。L1–L8 的核心觀念都已照做。
  - 一張圖只講一件事。放不下就拆成兩張，或把說明移到 figcaption，不要縮字（L5 第 1 段就拆成兩張）。
  - 畫完跑 `tools/check_diagrams.py`，再看亮、暗兩種截圖。
  - 頁面開始用 `styles.css` 新增的 class 時，把該頁的連結版本號往上改（`styles.css?v=日期`）。GitHub Pages 會快取約 10 分鐘，舊 CSS 配新 SVG 時，沒有樣式的方塊會變成全黑（2026-11-02 L5 發生過）。
  - 改了 `app.js` 也一樣，全站的 `app.js?v=日期` 一起往上改（`tools/dag.py`、`tools/new_lecture.py` 的樣板也要改）。2026-11-10 目錄打勾第一次改版時 `app.js` 沒有版本號，瀏覽器拿到舊 JS 配新 CSS，標記黏在標題後面。
- 舊 class（L1–L4 基礎題答案裡的圖還在用，不要用在新圖）：`dg-box`、`dg-box-soft`、`dg-box-accent`、`dg-frame`、`dg-line`、`dg-soft`、`dg-dash`、`dg-accent`、`dg-fill-ink`、`dg-fill-accent`、`dg-fill-soft`、`dg-t`、`dg-tb`、`dg-ts`、`dg-tm`、`dg-ta`。
- marker id 加前綴，全站不能重複：文章本文用 `lNc-`（L9 → `l9c-ah`），基礎題答案用 `tkN-<題號>-`（L9 第 2 題 → `tk9-2-ah`）。
- 箭頭要有標籤。舊畫法的文字 11–13px。viewBox 寬 600–760。數據圖照比例畫，標籤寫實際數值。
- **直接放來源的原圖（2026-11-12）**：來源文章的圖已經把事情講清楚時，可以直接放原圖，不重畫：`<figure class="diagram shot"><div class="scroll"><img src="img/lXX-名稱.webp" width height loading="lazy" alt="…"></div><figcaption>…</figcaption></figure>`。圖檔放 `docs/img/`，縮到寬 1600 存 webp。`alt` 把圖用文字講一遍（審查包拿它當「圖 內容」）；figcaption 照舊先問題再結論，用中文說明圖上的英文標籤要看哪裡，最後寫「圖取自〈來源〉（年月）」。原圖沒有的數字（本文算的）在 figcaption 或註裡標明。第一例是 L6b 的 CL-Bench、四層與 Mt. Moon。
- **數字表換成圖（2026-11-06）**：要讀者看出一組數字的趨勢、轉折或最佳點（「省下的越來越少」「最划算」），用照比例的橫條圖代替表：一列一個選項，標籤寫實際數值，最佳的那列用 `dg-l-key`／`dg-k`。結論說「最划算」時，兩邊的成本都要畫進圖（疊成兩色），不然圖上最短的那條會和結論相反。中間值（每段全對、平均跑幾次）放在列名下一行的 `dg-c`。例子：L6 3.1〈每段切幾步最划算〉。同一組數字不要表和圖各放一次，讀者要讀兩次：留圖，數字寫進圖的標籤；表裡有圖放不下的欄（公式、出處）才留表。`tools/find_figure_spots.py`（`verify.sh` 會跑）列出候選；判斷過、決定留著的表或段落加 `data-no-figure`（2026-11-07）。
- **互動圖（2026-11-09）**：圖的結論取決於本文的假設（驗證算幾步、每步成功率這類可以換的數字），正文又得逐一列出「換成別的值會怎樣」時，加滑桿讓讀者自己換，正文只留一兩個代表值和規則。James 問 L6 3.1 的驗證成本固定 5 步、能不能調。做法：
  - HTML 裡的 SVG 是預設值的靜態圖，就是正文和題庫講的那一組數字；沒有 JS、審查包、`check_diagrams.py`、網頁編輯都讀它。`figure.diagram` 加 `data-calc="名字"`，滑桿放在 `div.calc[hidden]`（`div.scroll` 之後、`figcaption` 之前），`docs/calc.js` 顯示它、拖動時照同一條算式重畫 SVG 和 `aria-label`，回到預設值就還原成原本的 SVG。範例：L6 3.1〈每段切幾步最划算〉（`ckpt`）。
  - 會變的文字不放在 `p`、`li`、`figcaption`：結論寫在 `output.calc-out`。Figcaption 說明預設是哪組假設。
  - 數字的進位和靜態圖一致（L6：總成本＝步數取整＋驗證成本取整，所以預設時 126＝84＋42），最省的那列先比顯示的數字。
  - 最長的長條超過最短的 8 倍就截斷（斜缺口，`dg-gap`），數字照寫實際值。
  - 頁面在 `code.js` 後面載入 `<script src="calc.js"></script>`。`edit.js` 開始編輯前會呼叫 `cs2680Calc.resetAll()`，把圖還原成原始碼的樣子。

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
- **什麼時候標**（2026-11-11 James）：可讀性審查沒有 BLOCK 之後才標，獨立成一步（WORKFLOW I2、skill `mark-red`、`tools/red_path.py`）。寫新段落時不放 `<strong>`；標的時候只搬標籤、不改字。
- **紅字是給誰的**（2026-11-11 James 問「畫紅線的目的」）：讀書會前回來複習、或沒時間讀完的人，只掃 h3、`<b>` 小標和紅字。所以紅字是一條**掃讀路徑**，三個檢查：
  1. **只讀 h3 ＋ `<b>` ＋ 紅字，推得回這章的論證**：每個 `<b>` 小標提出的事，後面要有一處紅字給答案（做法、判斷或代價）。`<b>` 是題目，紅字是答案；紅字不要重複 `<b>` 已經說的話。
  2. **離開上下文也看得懂**：不靠「右邊」「上圖」「第 3 章」「它」「這兩個」才懂；需要主詞或條件時，把紅字的範圍拉長到包住它（不必改字）。問句、指路句（「先看第 3 章」）不標。
  3. **標意思，不只標數字**：只有數字的紅字（`只剩 0.030`）要拉長到包住它的意思（`之後只剩 0.030，幾乎等於沒有記憶`）。題庫不考精確值（QUIZ〈讀者自測優先〉），掃讀的人要帶走的也是含義。
- **紅字標什麼**，依優先順序：
  1. 這一章的結論或做法，寫成短語（`<strong>必須強制的事，用 hook 或權限</strong>`、`<strong>歸納不直接改原本的 store，把結果寫成另一份</strong>`）。
  2. 主要的代價、風險、陷阱、常見的誤解（`<strong>有損又不可逆</strong>`、`<strong>Valid time 和寫入時間是兩件事</strong>`）。
  3. 撐起論點的數字，連同它的意思（`<strong>解出 18.0%，比沒有記憶還低</strong>`）。
  （2026-11-11 前數字排第一；改成結論優先，理由見上面第 3 點。）
  名額不夠時，先給還沒有紅字的那一節，再給例子裡的重述（例子的結論通常和前面的 `<b>` 重複）。
- **數量依長度，全站同一個密度**（v5.3；James：「要一致」）：
  - 每章的正文（不含 `details` 收合區塊、code、圖、表）每約 200 字 1 處：目標 = round(字數 ÷ 200)，至少 1、最多 5；比目標少 1 也可以。L1、L7、L8 的章短，所以多半 1–2 處；L3、L4 的章長，所以 4–5 處。
  - **長的章可以超過 5 處**（2026-11-13，James 讀 L6b：「畫紅線的部分可以再多一點」）：L6b 最長的兩章有 3,000 多字，上限 5 等於 600 多字才一處，好幾個 `<b>` 小標後面沒有答案。上限改成 max(原本的目標, round(字數 ÷ 120))，全站同一條；下限不變。多出來的名額先給還沒有紅字的 `<b>` 小標，再給開頭段的結論、清單項目裡的理由、代價。L6b 依此從 29 處加到 86 處（文字沒改）；其他堂還在舊的範圍內，沒有重標。
  - **數量是結果，不是挑選的方法**（2026-11-13，James 問「重新取得很貴、內容又很少變的資訊值得存一份」為什麼沒有紅字）：第一次加密時先定了「加到大約兩倍」，再從候選裡刪到那個數，刪掉的正好是規則的例外和做法。挑的時候逐句問四件事，是就標，不看名額：(a) 它是所在 `<b>` 小標的答案；(b) 它是讀者要照做的規則或做法（「做法是」「所以要」「本文的判斷」後面那一句）；(c) 它是一條規則的例外或成立條件（「值得」「前提」「才」）；(d) 它是主要的代價。解釋、例子、證據的細節、指路句不標。一段裡先講比較方法、再講結論時，標結論那一句，不要只標引出它的那一句。標完超過上限，才回頭刪 (d) 和重複小標的。
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

照 `WORKFLOW.md` B4。`check_article.py` 要 `OK`；截圖用 Read 看一次。

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
| l09.html | 9_llm_serving_basics_1.pdf | 51 | 2026-10-19 | Efficient LLM serving basics I: intro to LLMs | LLM 的結構與 serving 的帳 |
| l10.html | 10_llm_serving_basics_2a.pdf ＋ 10_llm_serving_basics_2b.pdf | 41 ＋ 55 | 2026-10-21（2b 是 11-02） | Efficient LLM serving basics II: intro to GPUs | GPU 入門與 kernel 最佳化 |
| l11.html | feedback_assignment.pdf | 72 | 2026-11-02 | Assignments feedback and agent pitfalls | 作業回饋與 agent 的十個陷阱 |

Part II 還沒有頁面的講次（依課程網站 2026-11-06 的時程，可能調整；PDF 檔名等 slides 公開後再填）：

| 日期 | 英文標題 | 備註 |
|---|---|---|
| 10-26 | Student sharing II: Harness optimization | 學生分享；`assignment3_sharing_protected.pdf` 讀不到內容 |
| 10-28 | Assignment 3 feedback | `assignment3_feedback_protected.pdf` 讀不到內容 |
| 11-04 | Efficient LLM serving basics III: Batching, paging, and parallelism | |
| 11-09 | Guest lecture: Why Infrastructure sets the pace of AI (Meta) | 客座 |
| 11-11 | Efficient LLM serving: speculative decoding | |
| 11-16 | Efficient LLM serving: KV-cache optimization and model architectures | 學生主講 |
| 11-18 | Efficient LLM serving: pruning and quantization | |
| 11-23 | Efficient agentic systems: scheduling and prefix caching | |
| 11-25 | No class（Thanksgiving recess） | |
| 11-30 | Efficient agentic systems: routing and load balancing | |
| 12-02 | Student sharing III: Showcase your full stack optimizations (Assignment 5) | 學生主講 |
| 12-07 | Final project poster and demo | |

11/02 那一堂有兩份 slides：`feedback_assignment.pdf` 編成 L11，`10_llm_serving_basics_2b.pdf` 是 10/21 GPU 入門的後半，併進 L10（2026-11-06 James 定）。L11 在課程網站排在 Part II，內容是用 agent 的實務，可以接在 Part I 後面讀。

10/05 客座（Snowflake）沒有公開 slides；10/14 Advanced agent design II 是學生主講。兩堂目前都沒有頁面。
