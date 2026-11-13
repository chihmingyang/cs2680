# CS2680 讀書會站台：維護說明

更新紀錄在 `guide/CHANGELOG.md`。

## 這個 repo 管什麼

- 讀書會站台「CS2680 觀念導讀」：https://chihmingyang.github.io/cs2680/
- 課程：Harvard CS2680 Modern AI Systems: Agents and System Optimizations（Fall 2026，Juncheng Yang）。課程沒有錄影，讀書會讀 slides。
- 每一堂有三段（2026-11-09 起；之前第 2 段是問題討論，已拿掉）：核心觀念、動手試試、原文出處（2026-11-13 起；之前是延伸閱讀，摘要、導讀、等級都拿掉，只留標題與連結）。核心觀念依想法的重要性排，不照 slides 的順序，不寫頁碼（STYLE_ARTICLE 第 0 節），課程漏掉的主題查原始來源補上；正文不提 slides 怎麼寫、不標「本文補的」（2026-11-13，STYLE_ARTICLE 第 0 節，L1–L10 已改，L11 照留）；核心觀念開頭的章節清單 `nav.map` 也拿掉（同日），直接進正文。名詞在正文裡解釋，或用收合註 `details.gloss`；題目放在每一節後面的小測（`guide/QUIZ.md`，目前只有 L6）。
- 每一堂的章數與閱讀時間（2026-11-03）：L1 10 章 30 分、L2 10 章 35 分、L3 10 章 45 分、L4 10 章 40 分、L5 9 章 25 分、L6 10 章 30 分（2026-11-10 拆成 L6 可靠性 5 章 20 分、L6b memory 6 章 20 分；同日 L6b 補 Anthropic 的 agent memory 研究文後 30 分；2026-11-12 L6b 照記憶的四層重排成 7 章，同日拿掉兩段 Pokémon 的例子後 45 分）、L7 10 章 35 分、L8 10 章 35 分（2026-11-13 第 2、3 章精簡，主線字數淨少 16% 與 26%，顯示值仍是 35 分；其餘各章與拆出 L8b 等 James 看過）；L9 10 章 40 分、L10 10 章 55 分、L11 10 章 35 分（2026-11-06）。為什麼這樣排、補了什麼、刪了什麼，見 `guide/V7_DECISIONS.md`；外部事實的來源、數字與查詢日期見 `guide/sources/lXX.md`。
- 事實會過時的地方，要改就重抓：L2、L3、L4、L6、L8 的 Claude Code 細節依 2026-11 的官方文件；L3 的 repo 依 2026-11-03（Superpowers v7.0.1、mattpocock/skills 1.3.2、Caveman 4.0.1、`deepseek-ai/dsh-superagent-prototype` 2026-10-31）；L7 的 benchmark 現況與 L8 的單價依 2026-11-03。L3 的 `#x1`（Caveman 評論查證）、`#x2`（SWE-Shift 查證）是 James 要留的本文延伸。L9 的每 token KV 表依 2026-11-06 的 config.json，中文 token 數是本文用六個 tokenizer 實測（重現方法在 `guide/sources/l09.md`）；L10 的 GPU 規格與 AI 寫 kernel 的案例依 2026-11-06；L11 的 Claude Code 細節依 2026-11 的官方文件，第 5 章引的兩串 GitHub issue 到 2026-11-06 都沒有官方回覆，有變化就重抓。
- **一堂不綁一份 slides**（2026-11-10，James）：堂依觀念切，不依 slides 切。一份 slides 講了兩個互不依賴的觀念就拆成兩堂，編號沿用加字母：舊 L6 拆成 L6〈Agent 可靠性〉（`l06.html`）和 L6b〈Agent memory〉（`l06b.html`），兩堂都指同一份 `6_agent_design_3.pdf`、共用 `slides/l06-notes.md` 與 `guide/sources/l06.md`。規則在 STYLE_ARTICLE 第 0 節，做法在 WORKFLOW K。
- **章的順序：有依賴就照依賴排**（2026-11-12，James 讀 L6b）：想法彼此獨立的堂照重要性排；資料流、層次這類後一個建在前一個上的，照依賴順序排，重要性改由「先看這裡」、`nav.map` 小字、紅字表達。L6b 因此從六章（要不要記、時間與來源、檢索、放在哪裡、安全、目錄）改成七章（Transcripts、Memory notes、Memory representations、Injected context、跨層的操作、安全、目錄）。補新材料前先判斷它是內容還是骨架（WORKFLOW C）。L9、L10 也照這條檢查過（2026-11-12）：L9 本來就是依賴順序，只改 lede；L10 把〈晶片裡面〉搬到〈量測〉前面（量測的 counter 要先認得晶片的單元）。
- Part I 的建議閱讀順序是 L2 → L4 → L3 → L5（2026-10-21 定）：L2、L3 會先用到 L4 才解釋的 context 代價、subagent。順序寫在首頁「怎麼讀」和 L2、L4 頁尾的 `.pager-note`。講次編號、檔名、issue label 不跟著改。
- 2026-11-09 James 決定拿掉「問題討論」段：之後每個觀念後面直接放題目（小測）。基礎題、進階題、自我檢查與 GitHub 討論串連結從 L1–L11 刪掉（內容留在 git 歷史，要找就看 2026-11-09 之前的 commit）；各堂的討論串 issue 已關閉，成員留言還在 GitHub 上。

## 東西放在哪裡

| 東西 | 位置 | 說明 |
|---|---|---|
| 站台檔案 | `docs/`（index、l01–l11、l06b、styles.css、app.js、code.js、calc.js） | 唯一來源。push 到 `main` 後 GitHub Pages 自動更新。 |
| 撰寫規範 | `guide/STYLE_ARTICLE.md`、`guide/STYLE_DIGEST.md` | 寫新講次或改內容前先讀。DIGEST 是延伸閱讀摘要的規範，2026-11-13 停用。`STYLE_BASIC.md`（基礎題）2026-11-09 停用。 |
| 可讀性審查 | `guide/REVIEW_READABILITY.md` | 改正文後、push 前，另一個 agent 讀一遍的 checklist 與報告格式。James 說看不懂就先回來改這份。 |
| v7 的決定與來源 | `guide/V7_DECISIONS.md`、`guide/sources/lXX.md` | 每堂怎麼排、補、刪；外部事實的來源與查證紀錄。 |
| 工作流程 | `guide/WORKFLOW.md` | 開工、新講次、修改、發布。 |
| 更新紀錄 | `guide/CHANGELOG.md` | `guide/` 各文件的更新紀錄，依文件分節，新的在最上面、一則一行。開工不必讀；要查某堂的來龍去脈就 `grep L3 guide/CHANGELOG.md`。設了 `merge=union`，不會衝突（2026-11-06 以前寫在各檔第 3 行）。 |
| Skill | `.claude/skills/` | `rewrite-with-example`：James 說看不懂、不順、要案例或圖。`idea-first-lecture`：把一堂改成 v7 依想法重組，或寫一堂新講次（`new-lecture-brief.md`）。`fact-check-extension`：查證他轉來的評論，寫成本文延伸。`readability-review`：改正文後、push 前的可讀性審查。`build-quiz`：替一堂建題庫，先列觀念再出題，開卷閉卷都過才 push。開工時呼叫 `register_repo_root` 後會自動進 skill 清單（WORKFLOW A1）。 |
| 腳本 | `tools/` | 用法寫在每個檔案開頭。 |
| 題庫 | 頁面裡的 `<script type="application/json" id="quiz">` | 每一節的小測與整合題；app.js 產生，規則在 `guide/QUIZ.md`。目前有 L6 與 L6b（2026-11-08 建在舊 L6，2026-11-09 補齊觀念涵蓋；2026-11-10 隨頁面拆開：L6 106 題 unit、3 題整合，L6b 152 題 unit、4 題整合，同日補五個小節後 172 題）、L5（2026-11-09，119 題 unit、7 題整合）和 L7（2026-11-10，265 題 unit、7 題整合；2026-11-13 刪三題後 262 題）。各堂的數字在 `guide/QUIZ.md`〈各堂題庫〉。 |
| 觀念 DAG | `docs/dag.json`、`docs/dag.html` | 以心智模型為單位的觀念依賴圖（concept／practice、三級難度、要先懂的邊）；頁面由 `tools/dag.py` 從資料產生，規則在 `guide/DAG.md`（英文頁，首頁課程地圖有連結，2026-11-09）。 |
| 互動圖 | `docs/calc.js`、`figure.diagram[data-calc]` | 拖滑桿換假設、圖照算式重畫；HTML 裡是預設值的靜態圖。目前只有 L6 3.1（2026-11-09）。規則在 `STYLE_ARTICLE.md` 第 6 節〈互動圖〉。 |
| CI | `.github/workflows/verify.yml` | push 後對全站跑 `verify.sh all`，只亮燈不擋（WORKFLOW J，2026-11-07）。`ask.yml` 是「問 Claude」。 |
| Slide 筆記 | `slides/lXX-notes.md` | 從 PDF 整理的逐頁筆記。Part II 起每堂一份。 |

已停用（2026-10-19）：

- claude.ai artifact「CS2680 觀念導讀」（4rvCbHCpWxAgvro8s1sa6u）：換成搬家說明頁。原因是個人方案的 artifact 只有擁有者能寫入共用資料庫，其他成員無法留言。
- 私人 artifact「CS2680 工具箱」：腳本已搬到 `tools/`。
- Project 的 `guide/` 文件：已搬到這裡。Project 裡還留一份 `guide/README.md`，2026-11-06 起只有三行指標（指回這個 repo），每個 Project 對話開頭都會自動讀它，所以不放現況、不要同步這份 README 過去。

## 腳本（tools/）

| 檔案 | 做什麼 |
|---|---|
| `punct.py` | 中文標點正規化（全形標點、中英文間空格）。`--diff` 先看會改什麼；數學式與英文片語的 ASCII 括號、冒號會保留。只對新片段跑，不要對頁面盲跑。 |
| `check_article.py` | 全頁結構（`#s-ideas`、`#s-try`、`#wrap`；`#s-background`、`#s-beyond` 可有可無）、slide 頁碼連結、STE 句長、閱讀時間（`--fix-time` 寫回三個時間；`deep-time` 含 `details.deep` 與 `details.gloss`）、紅字重點 `<strong>` 的位置與每章數量（依正文長度算目標）、用「；」串 4 項以上的段落（該改成清單；例外加 `data-inline`）。 |
| `add_anchors.py` | 核心觀念、觀念補充、本文延伸加上 `i1`、`t1`、`x1` 錨點，並列出標題（v5.0 頁面沒有觀念補充，`tN` 錨點手動保留在正文）。舊連結還指著的 `<span class="anchor" id="xN">` 保留原號，新的本文延伸跳過這些號碼（L6 的 x1–x4 是這種，所以 L6 第一個本文延伸是 `#x5`，2026-11-09）。頁面的 `#moved` 表（一堂拆成兩堂時搬走的 id）裡的 `xN` 也跳過（2026-11-10）。 |
| `add_lecture.py` | 新講次接到全站：目錄、講次數、上一堂連結、首頁列表。段號依頁面有沒有 `#s-background`／`#s-beyond` 決定；每頁自己的展開目錄不重建（L4 的三層目錄是手寫的）。Key 可以帶一個字母（`l06b`，2026-11-10）：新頁插在原堂之後，前後兩堂的 lecnav、pager 和首頁列表的位置跟著改。 |
| `audit.py` | 全站連結、SVG 無障礙屬性、marker id 重複、390px 與 1280px 版面、JS 錯誤。 |
| `dg.py` | 畫圖的 helper（v6／v7 的配色與元件、重用舊圖），給 `notes/` 裡的 build script 用。 |
| `check_diagrams.py` | 圖的幾何檢查：文字超出方塊或 viewBox、文字互相重疊、連接線穿過文字。 |
| `assemble_v7.py` | 把 `notes/lXX/` 的章片段組回 v7 頁面：換掉 tldr 與 `#s-ideas`、拿掉 `#s-arch`、改段號、eyebrow、meta、CSS 版本，重建本頁側欄。新講次還可以給 `try.html`、`wrap.html`，整段換掉（2026-11-06）。 |
| `new_lecture.py` | 新講次的 v7 骨架（2026-11-06）：head、topbar、本頁側欄、meta、動手試試與延伸閱讀的外框、延伸閱讀的 legend、pager。一堂兩份 deck 時給兩次 `--pdf`、`--pages`。 |
| `page_text.py` | 把頁面印成純文字，圖印成 aria-label，連結印出目標；也能印全部 id。讀大頁面用。 |
| `anchor_map.py` | 錨點對照表：`list` 哪些 id 有別頁連進來，`check` 對照表是否完整，`apply` 改別頁的連結（一個檔案只套一次）。 |
| `shot_article.py` | 截圖：架構圖（亮／暗）、第一題基礎題、第一題進階題、手機版。看的時候一則訊息平行 Read 6 張。 |
| `verify.sh` | 一次跑完一堂的檢查：`bash tools/verify.sh l03`；`all` 是每一堂的頁面檢查加全站檢查各一次，CI 用（WORKFLOW J）。check_article、check_diagrams、quiz（有題庫的頁面）、check_numbers（來源檔標了 strict 的講次才算失敗，其他只提示）、audit、add_lecture --check、dag --check，全過只印 `ALL OK`；punct 只提示。不寫回檔案。 |
| `assemble_ideas.py` | （v5 頁面用，v7 改用 `assemble_v7.py`）把 `notes/lXX/` 的章片段（`head.html`、`i1.html`…、選用的 `tldr.html`、`arch.html`）組回頁面的核心觀念：換掉 `#s-ideas`、填閱讀地圖的分鐘數、重建本頁的三層目錄。大改一堂的核心觀念時用（L5、L6 的擴寫）。 |
| `review_pack.py` | 把一頁（或 `--since <ref>` 之後文字有變的章，tldr 也算）印成讀者視角的純文字審查包：一行一個單位、帶定位，表格格子帶欄名與列名，數字列併成一行。給可讀性審查的 subagent 讀。`--prefix` 把要審的章前面的章當上下文印出、後面的章不印（2026-11-07 起一律這樣給，tldr 用 `--chapter tldr` 單獨一包）。互動圖的滑桿與預設的結論印成一個單位 `圖N 滑桿`（2026-11-09）。 |
| `review_eval.py` | 量審查者準不準：`guide/review_cases/` 一個檔是 James 說看不懂的一段（修改前的 commit）。`pack` 把每個事件做成審查包，各開一個全新的審查者，`score` 印 recall：事件的單位被標成 BLOCK 才算抓到，被 `reviewer-prompt.md` 引用當例子的分開計。改 prompt 或 checklist 之後跑（2026-11-11）。 |
| `review_status.py` | 哪些章審過、用第幾版 checklist 審的：`status lXX` 對照 `guide/review_log.tsv` 與現在的頁面，列出「改過」「舊規則」「沒審過」的章；`stale lXX` 印出這些章的 id，接給 `review_pack.py --chapter`；`mark lXX <章>` 在第二輪沒有 BLOCK 之後記一筆（2026-11-11）。 |
| `review_noise.py` | 比對同一包的幾份審查報告：每份的 BLOCK／NIT 數、哪些單位每次都被標、兩兩重疊、「最難讀的三處」重疊。量審查者的雜訊用（2026-11-07）。 |
| `quiz.py` | 題庫：`init` 從頁面的小節產生節的骨架；`spec` 印給列觀念的 agent 讀的文字；`merge` 把 subagent 寫的 points／題目併進頁面；`check` 題庫和頁面的小節對不對得上、`evidence` 以外的每個觀念（`points`）都有題目測到、選項只有數字的題給 warn（verify.sh 會跑）；`coverage` 列出每個觀念被哪幾題測到；`exam` 出作答包；`closed`／`closedcheck` 閉卷測試；`grade` 對定位、出評分包；`report` 彙整與比較各次結果；`exam`、`closed`、`grade` 可用題號、節號或章號挑題。流程見 `build-quiz` skill，規則見 `guide/QUIZ.md`（2026-11-08）。 |
| `check_numbers.py` | 頁面引用外部來源的數字對不對得上 `guide/sources/lXX.md`：寫出來源的那一句起到段尾，每個數字都要在來源檔那一筆裡；題庫裡 `evidence` 類觀念的數字要在來源檔、也要還在那一章的正文。本文自己的數字加 `data-num-own`。來源檔有 `check_numbers: strict` 的講次（L6、L6b）對不上就讓 `verify.sh` 失敗，其他只提示。規則見 `guide/QUIZ.md`〈數字對照〉（2026-11-11）。 |
| `red_path.py` | 標紅字用（WORKFLOW I2）：`red_path.py lXX [章]` 先確認那幾章的可讀性審查是 ok，不是就擋下來；過了印掃讀路徑（章名、`<b>` 小標、紅字）和提示。只讀不寫（2026-11-11）。 |
| `find_figure_spots.py` | 列出核心觀念裡可能該畫成圖的地方：結論是趨勢、轉折或最佳點的數字表和段落（文字有「越來越」「最划算」「再往下」這類詞），以及表和圖畫同一組數字的地方。只提示，`verify.sh` 會跑；決定留著的元素加 `data-no-figure`。規則見 `STYLE_ARTICLE.md` 第 6 節。 |
| `dag.py` | 觀念 DAG：`--check` 檢查 `docs/dag.json`（無環、難度沿邊不降、src 錨點存在、每章都被蓋到或在 excluded），不帶參數就重寫 `docs/dag.html`。規則見 `guide/DAG.md`（2026-11-08）。 |

以上腳本在 2026-10-19 對 L1–L8 全部通過。

## 規則變了怎麼辦

在任何 session 定下新規則（題數、格式、語氣、版面），就在同一個 session 寫回 `guide/` 裡對應的文件，跟頁面一起 commit。檢查規則變了，就改對應的腳本。這樣下一個 session 不必重新摸索。
