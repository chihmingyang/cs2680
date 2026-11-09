# 觀念 DAG：規則

更新紀錄在 `guide/CHANGELOG.md`。

頁面：https://chihmingyang.github.io/cs2680/dag.html （2026-11-08 起；首頁「課程地圖」有連結，2026-11-09）。**頁面是英文的**（James 2026-11-08 要求；中文的主題名像「放大與人」他讀不出語意），所以 `dag.json` 的 `name`、`short`、`why`、主題名、難度名都用英文；出處章名照頁面的中文顯示，因為連過去的是中文頁。
資料：`docs/dag.json`。頁面由 `python3 -I tools/dag.py` 產生，改資料就重跑；`--check` 只檢查，`verify.sh` 會跑。

## 為什麼要有這張圖

James 2026-11-08 提出：課程現在用一小時的 slides 切成一堂一堂，沒有對到真正的概念理解；他要一張觀念的 DAG，每個觀念是某個觀念的延伸，分基礎、進階、專家三級，之後把整個課程改成 DAG 的形式進行。這張圖是第一步：先把現有 11 堂的核心觀念拆成節點、畫出「要先懂」的邊，算出講次和觀念對不上的地方，再談怎麼重新分堂。

## 節點：從「腦袋裡的單位」出發，不從章出發

James 2026-11-09：granularity 要以大腦的觀念為第一性原理，不要被現在的 slide 課程綁架。所以節點的單位是「讀者腦袋裡要有的東西」，章只是來源。

- 兩種節點（`kind`）：
  - `concept`：心智模型。一個系統行為，換產品還是對（loop、context、KV cache、Amdahl 上限）。concept 是 DAG 的骨架，**不能依賴 practice**，`--check` 會擋。
  - `practice`：套用心智模型的決定規則、技巧或案例（grep first、checkpoint 與上限、FlashAttention）。practice 可以依賴 concept 和別的 practice。頁面上 practice 是淡色虛線框，可以用「Show practices」關掉只看骨架。
- concept 的測試：不提產品名、不提講次、不提這門課，這句話還成立嗎？只有加上「Claude Code」「CLAUDE.md」才說得通的，節點是那個一般的想法，產品是它的例子。所以：
  - CLAUDE.md、auto memory → 一個 concept `persistent-text`（存一次、每個 session 都注入的文字）
  - skill、offloading → 一個 concept `context-admission`（用到才進來）
  - subagent、multi-agent 的「只能傳文字」 → 一個 concept `separate-contexts`
  - worktree、L11 的執行環境 → 一個 practice `isolation`
  - hook 是 practice `hooks`（掛在事件上的程式），Superpowers vs mattpocock 是它的例子
  - MCP 是 practice `mcp`（外部 tool server），plugin 是 practice
- 一個節點一句主張：能寫成一句話、有自己的前置、刪掉它後面某個節點讀不懂。課程裡的案例（Caveman、Superpowers、dsh-superagent）不是節點，是它說明的那個節點裡的例子（寫進 `name`／`why`，`src` 指到那一章，所以覆蓋檢查還是過）。
- 只有一個根：`next-token`——model 是一個沒有記憶的函數，token 序列進、下一個 token 的機率分布出。sampling、tokens、agent loop、prefill／decode 全部從它延伸；GPU 那條線另有一個根 `gpu-throughput`。
- 每一堂核心觀念的每一章都要被某個節點的 `src` 蓋到；目錄章列在 `excluded`。
- 欄位：`id`（英文 slug）、`name`（一句話主張）、`short`（方塊上的短名，要能單獨讀懂；方塊 124px 寬、12px 字、最多兩行，`--check` 用字寬估算，放不下是 ERROR）、`tier`（Basic／Intermediate／Expert）、`kind`、`theme`（泳道）、`src`、`deps`、`why`。
- `why` 寫「From X and Y: …」（根寫 Root.），只點名直接前置；要說出少了前置哪裡讀不懂。寫不出來就是邊畫錯了。

## 邊

- `deps` 裡的 A 對這個節點 B 的意思是「讀 B 之前要先懂 A」。方向是前置 → 延伸。
- 只畫直接的前置。A → C 能從 A → B → C 推出來就不畫；`--check` 會把這種多餘的邊列成 warn，目前 0 條。
- 邊只看觀念，不看講次。前置在後面的講次是正常的，那正是要找的落差。

## 難度

| 難度 | 標準 |
|---|---|
| Basic | 一句話能說清楚；靠日常經驗或一個前置觀念就能懂；不懂它，後面多數觀念讀不下去 |
| Intermediate | 要同時拿著兩個以上的前置觀念才能懂；通常是在做一個設計決定，或算一次帳 |
| Expert | 要進到機制內部（算式、硬體單元、演算法），或要能判斷研究結論的效度；不自己做 serving、harness、評估的人可以跳過，不影響上游的判斷 |

- 難度是觀念本身的性質，不是圖上的深度。「分散式狀態」在第 2 層但是專家；「先用檔案」在第 7 層但是進階。
- 一條硬規則：前置的難度不能比這個觀念高（Basic ≤ Intermediate ≤ Expert）。違反就是邊畫錯或難度標錯，`--check` 會擋。

## 版面

- x 是依賴深度：從起點算最長路徑的長度。第 k 層的前置都在前 k 層，所以由左到右就是一個合法的閱讀順序（拓樸排序）。
- y 是主題泳道（`themes` 的順序，11 條，第一條「The model as a function」放根）。同一格有好幾個觀念時上下排，依前置的位置排序。
- 顏色是難度：Basic `--dg-a`、Intermediate `--dg-c`、Expert `--dg-d`，方塊左緣的灰條也跟著難度變深。
- hover／點一個觀念：前置用藍實線往左亮，延伸用橘虛線往右亮，其他淡掉；下方面板顯示主張、`why`、出處、前置、延伸出去的觀念。清單裡的觀念名也都可以點。
- 篩選：難度勾選、講次下拉（看一堂的章散在圖的哪裡）、Show practices（關掉只剩 concept 骨架）。「Fit to width」預設開，把約 1280px 的圖縮進內容欄；關掉就 1:1 橫向捲。
- 這一頁沒有側欄：圖要 1178px 寬，有側欄的內容欄只有 920px。topbar 的連結不要加 `rel`，手機版的 CSS 會把 `.lecnav a[rel]` 畫成圓形箭頭鈕。

## 頁面下半（從資料算出來）

- **一個觀念散在兩堂**：`src` 跨兩堂的節點。
- **前置觀念在後面的講次**：節點被教的那一堂（`src[0]`）之前，前置連帶過都沒出現過（前置的 `src` 裡最早的講次 > 節點的主要講次）。前置若在更早的講次提過一句就不算，所以這個數字比「主要講次比較」小很多（7 條對 17 條）。
- **每一堂的難度組成與深度範圍**：節點算在 `src[0]` 那一堂。
- **依賴順序的閱讀清單**：一層一組，層內依主題。是改成 DAG 形式時的順序草稿，不是分堂。

## 怎麼改

1. 改 `docs/dag.json`。講次的 key 可以帶一個字母（`l06b`，2026-11-10 一份 slides 拆成兩堂），`src`、`excluded`、`lectures` 都用它；頁面上顯示成 L6b，排序照字串（l06 < l06b < l07）。新講次：每章一個節點（或拆、併），`src` 對到 `docs/lXX.html` 的章 id；目錄章加進 `excluded`。
2. `python3 -I tools/dag.py --check`，看 ERROR 和 warn。
3. `python3 -I tools/dag.py` 重寫 `docs/dag.html`，截圖看一次（圖、點一個節點、手機版）。
4. 章 id 改了（`add_anchors.py` 重編）會被覆蓋檢查抓到：每一章都要被某個節點蓋到或在 `excluded`。

## 2026-11-09 第二版的判斷（James 說 granularity 他交給我）

- 93 個節點：58 concept、35 practice；152 條邊；9 層；21 個觀念散在兩堂以上；8 條前置在後面講次的邊。
- 從第一版（100 個節點、以章為單位）改掉的：根從 4 個收成「next-token 函數」加 GPU 兩個；probabilistic 併進 sampling；CLAUDE.md 與 memory 併成 persistent-text；skill 併進 context-admission；subagent 與 text-only-channel 併成 separate-contexts；worktree 與 L11 執行環境併成 isolation；Caveman、Superpowers、dsh-superagent 三個案例降成例子；metrics 直接接 cost-per-success（不再經過 two-layer-testing）。
- 難度分布：Basic 20、Intermediate 61、Expert 12。
- 最值得先動的邊（前置在後面講次、連帶過都沒有）：MCP → tool（L4）、verification-defines-autonomy（L3）→ verification-loop（L6）、fix-harness-first（L4）→ failure-layers（L6）、memory-backend（L6）→ eval-driven-decisions（L7）、disaggregation（L1）→ three-numbers（L9）、two-layer-testing（L1）→ code-vs-text（L2）。
