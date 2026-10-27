# CS2680 讀書會站台：維護說明

更新：2026-10-28（紅字重點 `<strong>`、code snippet 改成 IDE 配色，見 STYLE_ARTICLE 第 6c 節；`check_article.py` 多檢查紅字）。2026-10-27（L4 先行：觀念補充併入核心觀念，詞條改成正文裡的收合註 `details.gloss`，章編號 2.1–2.7 分三組、段首閱讀地圖、目錄多一層；L4 因此只有 5 段，其他講次仍 6 段，見 STYLE_ARTICLE v5.0）。2026-10-27（「大家的討論」併入問題討論末尾，延伸閱讀編為第 6 段）。2026-10-26（全站取消「延伸思考」段，推論併入章節的「本文延伸」收合區塊，段落改為 6 段；指令與設定檔一律 code snippet、每章至少一張圖或表，STYLE_ARTICLE v4.1）。2026-10-25（文章改為不看 slides 也能讀完的主體，名詞就地解釋，見 STYLE_ARTICLE v4.0；L3、L4 已改寫）。2026-10-22（進階題每堂最多 3 題）。2026-10-21（討論改為每堂一串；延伸閱讀的「推薦」也附摘要）。

## 這個 repo 管什麼

- 讀書會站台「CS2680 觀念導讀」：https://chihmingyang.github.io/cs2680/
- 課程：Harvard CS2680 Modern AI Systems: Agents and System Optimizations（Fall 2026，Juncheng Yang）。課程沒有錄影，讀書會讀 slides。
- 每一堂有六段：架構、核心觀念、觀念補充、問題討論（含 GitHub 討論串連結）、動手試試、延伸閱讀。L2–L6 從 2026-10-27 起是五段：觀念補充併進核心觀念，名詞在正文裡用收合註解釋（STYLE_ARTICLE v5.0；L2 另保留「深入」區塊）；L1、L7、L8 還是六段。一篇架構文章（文章是主體，slides 是輔助；超出 slide 的推論放在章節末尾的「本文延伸」收合區塊）、最多 5 題基礎題（附重點複習）、最多 3 題進階題（附提示與作答範本；2026-10-22 從 6 題減為 3 題）、延伸閱讀導讀（必讀與推薦的每一篇附摘要；選讀、查閱不附）。
- Part I 的建議閱讀順序是 L2 → L4 → L3 → L5（2026-10-21 定）：L2、L3 會先用到 L4 才解釋的 context 代價、subagent。順序寫在首頁「怎麼讀」和 L2、L4 頁尾的 `.pager-note`。講次編號、檔名、issue label 不跟著改。
- 成員的討論在這個 repo 的 Issues：每一堂一串，只放基礎題（2026-10-21 起；之前每一題一串，太散）。每人一則留言，`### Q1`…`### Q5` 當小標。進階題不上 GitHub，留在頁面給讀書會當天討論。

## 東西放在哪裡

| 東西 | 位置 | 說明 |
|---|---|---|
| 站台檔案 | `docs/`（index、l01–l08、l02-readings、styles.css、app.js） | 唯一來源。push 到 `main` 後 GitHub Pages 自動更新。 |
| 撰寫規範 | `guide/STYLE_ARTICLE.md`、`guide/STYLE_BASIC.md`、`guide/STYLE_DIGEST.md` | 寫新講次或改內容前先讀。DIGEST 是延伸閱讀裡必讀與推薦摘要的規範。 |
| 工作流程 | `guide/WORKFLOW.md` | 開工、新講次、修改、發布、讀討論。 |
| 腳本 | `tools/` | 9 支 `.py`，用法寫在每個檔案開頭。 |
| Slide 筆記 | `slides/lXX-notes.md` | 從 PDF 整理的逐頁筆記。Part II 起每堂一份。 |
| 成員的討論 | repo 的 Issues（每堂一串，label `L01`…） | `tools/discuss.py --digest lXX` 依題號匯出成 Markdown。 |
| L2 readings 的逐篇導讀 | `docs/l02-readings.html` | 只有 L2 有，10 篇全寫；l02.html 的延伸閱讀連到它。其他講次用頁內的必讀摘要。 |

已停用（2026-10-19）：

- claude.ai artifact「CS2680 觀念導讀」（4rvCbHCpWxAgvro8s1sa6u）：換成搬家說明頁。原因是個人方案的 artifact 只有擁有者能寫入共用資料庫，其他成員無法留言。
- 私人 artifact「CS2680 工具箱」：腳本已搬到 `tools/`。
- Project 的 `guide/` 文件：已搬到這裡。

## 腳本（tools/）

| 檔案 | 做什麼 |
|---|---|
| `punct.py` | 中文標點正規化（全形標點、中英文間空格）。`--diff` 先看會改什麼；數學式與英文片語的 ASCII 括號、冒號會保留。只對新片段跑，不要對頁面盲跑。 |
| `check_article.py` | 全頁結構（`#s-background`、`#s-beyond` 可有可無）、slide 頁碼連結、STE 句長、閱讀時間（`--fix-time` 寫回三個時間；`deep-time` 含 `details.deep` 與 `details.gloss`）、紅字重點 `<strong>` 的位置與每章數量。 |
| `check_discuss.py` | 問題討論段：基礎題 3–5 題與重點複習結構、進階題最多 3 題、題型不重複，與提示／範本；基礎題連到該堂 issue、進階題不連；核心觀念 3–8 章。 |
| `add_anchors.py` | 核心觀念、觀念補充、本文延伸加上 `i1`、`t1`、`x1` 錨點，並列出標題（v5.0 頁面沒有觀念補充，`tN` 錨點手動保留在正文）。 |
| `add_lecture.py` | 新講次接到全站：目錄、講次數、上一堂連結、首頁列表。段號依頁面有沒有 `#s-background`／`#s-beyond` 決定；每頁自己的展開目錄不重建（L4 的三層目錄是手寫的）。 |
| `discuss.py` | 每一堂開一個 issue（內文是基礎題＋回覆範本）、把連結寫進每題基礎題、重建問題討論末尾的 GitHub 區塊；`--sync-body` 同步題目（issue 內文寫的「站台第 N 段」依頁面算）；`--digest` 匯出討論。 |
| `audit.py` | 全站連結、SVG 無障礙屬性、marker id 重複、390px 與 1280px 版面、JS 錯誤。 |
| `shot_article.py` | 截圖：架構圖（亮／暗）、第一題基礎題、第一題進階題、手機版。 |
| `insert_digest.py` | 把 `notes/digests/lXX-rN.html` 的摘要片段插進該篇的 `li`、重寫 `rg-intro` 的篇數，並檢查錨點、頁碼、長度與「別誤讀」。`--check` 只驗證。 |

以上腳本在 2026-10-19 對 L1–L8 全部通過。

## 規則變了怎麼辦

在任何 session 定下新規則（題數、格式、語氣、版面），就在同一個 session 寫回 `guide/` 裡對應的文件，跟頁面一起 commit。檢查規則變了，就改對應的腳本。這樣下一個 session 不必重新摸索。
