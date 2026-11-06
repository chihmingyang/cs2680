# CS2680 讀書會站台：維護說明

更新紀錄在 `guide/CHANGELOG.md`。

## 這個 repo 管什麼

- 讀書會站台「CS2680 觀念導讀」：https://chihmingyang.github.io/cs2680/
- 課程：Harvard CS2680 Modern AI Systems: Agents and System Optimizations（Fall 2026，Juncheng Yang）。課程沒有錄影，讀書會讀 slides。
- 每一堂有四段（2026-11-03 起 L1–L8 全部如此）：核心觀念、問題討論（含 GitHub 討論串連結）、動手試試、延伸閱讀。核心觀念依想法的重要性排，不照 slides 的順序，不寫頁碼（STYLE_ARTICLE 第 0 節），課程漏掉的主題查原始來源補上，標「本文補的」。名詞在正文裡解釋，或用收合註 `details.gloss`；最多 5 題基礎題（附重點複習）、最多 3 題進階題（附提示與作答範本）、延伸閱讀導讀（必讀與推薦的每一篇附摘要；選讀、查閱不附）。
- 每一堂的章數與閱讀時間（2026-11-03）：L1 10 章 30 分、L2 10 章 35 分、L3 10 章 45 分、L4 10 章 40 分、L5 9 章 25 分、L6 10 章 30 分、L7 10 章 35 分、L8 10 章 35 分。為什麼這樣排、補了什麼、刪了什麼，見 `guide/V7_DECISIONS.md`；外部事實的來源、數字與查詢日期見 `guide/sources/lXX.md`。
- 事實會過時的地方，要改就重抓：L2、L3、L4、L6、L8 的 Claude Code 細節依 2026-11 的官方文件；L3 的 repo 依 2026-11-03（Superpowers v7.0.1、mattpocock/skills 1.3.2、Caveman 4.0.1、`deepseek-ai/dsh-superagent-prototype` 2026-10-31）；L7 的 benchmark 現況與 L8 的單價依 2026-11-03。L3 的 `#x1`（Caveman 評論查證）、`#x2`（SWE-Shift 查證）是 James 要留的本文延伸。
- Part I 的建議閱讀順序是 L2 → L4 → L3 → L5（2026-10-21 定）：L2、L3 會先用到 L4 才解釋的 context 代價、subagent。順序寫在首頁「怎麼讀」和 L2、L4 頁尾的 `.pager-note`。講次編號、檔名、issue label 不跟著改。
- 成員的討論在這個 repo 的 Issues：每一堂一串，只放基礎題（2026-10-21 起；之前每一題一串，太散）。每人一則留言，`### Q1`…`### Q5` 當小標。進階題不上 GitHub，留在頁面給讀書會當天討論。

## 東西放在哪裡

| 東西 | 位置 | 說明 |
|---|---|---|
| 站台檔案 | `docs/`（index、l01–l08、l02-readings、styles.css、app.js、code.js） | 唯一來源。push 到 `main` 後 GitHub Pages 自動更新。 |
| 撰寫規範 | `guide/STYLE_ARTICLE.md`、`guide/STYLE_BASIC.md`、`guide/STYLE_DIGEST.md` | 寫新講次或改內容前先讀。DIGEST 是延伸閱讀裡必讀與推薦摘要的規範。 |
| 可讀性審查 | `guide/REVIEW_READABILITY.md` | 改正文後、push 前，另一個 agent 讀一遍的 checklist 與報告格式。James 說看不懂就先回來改這份。 |
| v7 的決定與來源 | `guide/V7_DECISIONS.md`、`guide/sources/lXX.md` | 每堂怎麼排、補、刪；外部事實的來源與查證紀錄。 |
| 工作流程 | `guide/WORKFLOW.md` | 開工、新講次、修改、發布、讀討論。 |
| 更新紀錄 | `guide/CHANGELOG.md` | `guide/` 各文件的更新紀錄，依文件分節，新的在最上面、一則一行。開工不必讀；要查某堂的來龍去脈就 `grep L3 guide/CHANGELOG.md`。設了 `merge=union`，不會衝突（2026-11-06 以前寫在各檔第 3 行）。 |
| Skill | `.claude/skills/` | `rewrite-with-example`：James 說看不懂、不順、要案例或圖。`idea-first-lecture`：把一堂改成 v7 依想法重組。`fact-check-extension`：查證他轉來的評論，寫成本文延伸。`readability-review`：改正文後、push 前的可讀性審查。開工時呼叫 `register_repo_root` 後會自動進 skill 清單（WORKFLOW A1）。 |
| 腳本 | `tools/` | 用法寫在每個檔案開頭。 |
| Slide 筆記 | `slides/lXX-notes.md` | 從 PDF 整理的逐頁筆記。Part II 起每堂一份。 |
| 成員的討論 | repo 的 Issues（每堂一串，label `L01`…） | `tools/discuss.py --digest lXX` 依題號匯出成 Markdown。 |
| L2 readings 的逐篇導讀 | `docs/l02-readings.html` | 只有 L2 有，10 篇全寫；l02.html 的延伸閱讀連到它。其他講次用頁內的必讀摘要。 |

已停用（2026-10-19）：

- claude.ai artifact「CS2680 觀念導讀」（4rvCbHCpWxAgvro8s1sa6u）：換成搬家說明頁。原因是個人方案的 artifact 只有擁有者能寫入共用資料庫，其他成員無法留言。
- 私人 artifact「CS2680 工具箱」：腳本已搬到 `tools/`。
- Project 的 `guide/` 文件：已搬到這裡。Project 裡還留一份 `guide/README.md`，2026-11-06 起只有三行指標（指回這個 repo），每個 Project 對話開頭都會自動讀它，所以不放現況、不要同步這份 README 過去。

## 腳本（tools/）

| 檔案 | 做什麼 |
|---|---|
| `punct.py` | 中文標點正規化（全形標點、中英文間空格）。`--diff` 先看會改什麼；數學式與英文片語的 ASCII 括號、冒號會保留。只對新片段跑，不要對頁面盲跑。 |
| `check_article.py` | 全頁結構（`#s-background`、`#s-beyond` 可有可無）、slide 頁碼連結、STE 句長、閱讀時間（`--fix-time` 寫回三個時間；`deep-time` 含 `details.deep` 與 `details.gloss`）、紅字重點 `<strong>` 的位置與每章數量（依正文長度算目標）、用「；」串 4 項以上的段落（該改成清單；例外加 `data-inline`）。 |
| `check_discuss.py` | 問題討論段：基礎題 3–5 題與重點複習結構、進階題最多 3 題、題型不重複，與提示／範本；基礎題連到該堂 issue、進階題不連；核心觀念 3–8 章。 |
| `add_anchors.py` | 核心觀念、觀念補充、本文延伸加上 `i1`、`t1`、`x1` 錨點，並列出標題（v5.0 頁面沒有觀念補充，`tN` 錨點手動保留在正文）。 |
| `add_lecture.py` | 新講次接到全站：目錄、講次數、上一堂連結、首頁列表。段號依頁面有沒有 `#s-background`／`#s-beyond` 決定；每頁自己的展開目錄不重建（L4 的三層目錄是手寫的）。 |
| `discuss.py` | 每一堂開一個 issue（內文是基礎題＋回覆範本）、把連結寫進每題基礎題、重建問題討論末尾的 GitHub 區塊；`--sync-body` 同步題目（issue 內文寫的「站台第 N 段」依頁面算）；`--digest` 匯出討論。 |
| `audit.py` | 全站連結、SVG 無障礙屬性、marker id 重複、390px 與 1280px 版面、JS 錯誤。 |
| `dg.py` | 畫圖的 helper（v6／v7 的配色與元件、重用舊圖），給 `notes/` 裡的 build script 用。 |
| `check_diagrams.py` | 圖的幾何檢查：文字超出方塊或 viewBox、文字互相重疊、連接線穿過文字。 |
| `assemble_v7.py` | 把 `notes/lXX/` 的章片段組回 v7 頁面：換掉 tldr 與 `#s-ideas`、拿掉 `#s-arch`、改段號、eyebrow、meta、CSS 版本，重建本頁側欄。 |
| `page_text.py` | 把頁面印成純文字，圖印成 aria-label，連結印出目標；也能印全部 id。讀大頁面用。 |
| `anchor_map.py` | 錨點對照表：`list` 哪些 id 有別頁連進來，`check` 對照表是否完整，`apply` 改別頁的連結（一個檔案只套一次）。 |
| `shot_article.py` | 截圖：架構圖（亮／暗）、第一題基礎題、第一題進階題、手機版。看的時候一則訊息平行 Read 6 張。 |
| `verify.sh` | 一次跑完一堂的檢查：`bash tools/verify.sh l03`。check_article、check_discuss、check_diagrams、audit、add_lecture --check，全過只印 `ALL OK`；punct 只提示。不寫回檔案。 |
| `assemble_ideas.py` | （v5 頁面用，v7 改用 `assemble_v7.py`）把 `notes/lXX/` 的章片段（`head.html`、`i1.html`…、選用的 `tldr.html`、`arch.html`）組回頁面的核心觀念：換掉 `#s-ideas`、填閱讀地圖的分鐘數、重建本頁的三層目錄。大改一堂的核心觀念時用（L5、L6 的擴寫）。 |
| `review_pack.py` | 把一頁（或 `--since <ref>` 之後文字有變的章）印成讀者視角的純文字審查包：一行一個單位、帶定位，表格格子帶欄名與列名，數字列併成一行。給可讀性審查的 subagent 讀。 |
| `insert_digest.py` | 把 `notes/digests/lXX-rN.html` 的摘要片段插進該篇的 `li`、重寫 `rg-intro` 的篇數，並檢查錨點、頁碼、長度與「別誤讀」。`--check` 只驗證。 |

以上腳本在 2026-10-19 對 L1–L8 全部通過。

## 規則變了怎麼辦

在任何 session 定下新規則（題數、格式、語氣、版面），就在同一個 session 寫回 `guide/` 裡對應的文件，跟頁面一起 commit。檢查規則變了，就改對應的腳本。這樣下一個 session 不必重新摸索。
