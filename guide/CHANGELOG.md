# 更新紀錄

`guide/` 各文件的更新紀錄，2026-11-06 從各檔第 3 行搬來。新紀錄寫在對應一節的**最上面**，一則一行。
這個檔案設了 `merge=union`（`.gitattributes`）：兩個 session 同時加一行，git 兩行都留，不會衝突。

## README.md
- 2026-11-13（James：「你決定就好」「核心觀念 bullet point 拿掉，直接進入正文」。**不提 slides 怎麼寫**推到 L1–L10（約 330 處；L11 講課程自己的作業統計，照留；L7 留下飽和圖數字的出處）；題庫跟著改字，L7 刪三題只問「這張圖是誰整理的」的題（k22c、k26g、k31e）與對應的觀念。**核心觀念開頭的章節清單 `nav.map` 全站拿掉**，分組名與每章小字一起拿掉；首頁「怎麼讀」同步。）
- 2026-11-13（**延伸閱讀改成「原文出處」**（James：「其實沒人會去看延伸閱讀，光看完原文就花時間了」）：L1–L11 的摘要、導讀、等級、最短路徑全刪，每篇只留標題與連結，全站少約 9 萬字；`l02-readings.html`、`insert_digest.py` 刪掉，`STYLE_DIGEST.md` 停用；正文裡「見延伸閱讀」的幾處改指原文出處，L5 一句指向 L7 摘要的話刪掉；首頁「怎麼讀」同步。**正文不提 slides 怎麼寫**（James：「我幾乎重寫了一半以上的內容」）：規則寫進 STYLE_ARTICLE 第 0 節，L4 先改（約 60 處：「課程列了…」「課程的例子」「本文補的」、動手試試的頁碼），其他講次待改。）
- 2026-11-13（L6b 用詞改成英文術語（James：「不是應該統一用英文 reflect 之類的？」）：當名詞用的「歸納」全頁改成 reflection（89 處，含題庫；「歸納出」「歸納成」當一般動詞的留著）；dreaming 的三件事改成 correct、reflection、promote 與 demote，並註明各是誰的用詞。`CLAUDE.md` 加一條：開工先跑 `review_status.py status`，checklist 加條目時只拿新條目掃舊章。）
- 2026-11-13（L6b 第 5 章：James 問 Reflect、Forget 和後面的 dreaming 是不是重疊。是：前兩個是操作，dreaming 是時機。開頭那一段改寫，加一張對照表（修錯、歸納、換層各是哪一站的操作、session 裡做不做得到）和 compaction／GC 的類比。）
- 2026-11-13（L6b 第 4 章接上 RAG：James 問「這不就是 RAG 流程嗎？」。第 2 段點名 RAG 與 semantic search；`#i4-1` 改寫成「在 RAG 上多加四個訊號」，順序是已知 → 為什麼不夠 → 新增；章標題、nav.map、側欄、dag.html 跟著改。圖、表、SQL、題庫沒動。）
- 2026-11-13（L10 整堂可讀性重審（v16）：兩輪 112 + 16 BLOCK 全修，第 9 章漏洞改成五類，A100 頻寬與 70B KV cache 的單位統一。取捨在 V7_DECISIONS，審查紀錄在 review_reports/l10-20261113/。）
- 2026-11-12（L6b 拿掉兩段 Pokémon 的例子（James：「我認為是多的」）：第 2 章記憶資料夾的比較整段刪；第 5 章 Mt. Moon 只留結論一段，原圖 `l06b-mtmoon.webp` 刪掉。加兩段「本文的推論」：第 4 章〈誰決定什麼時候讀寫〉控制權跟著 model 實測的行為分、不跟著大小分；第 5 章〈Session 之間的整理〉兩個時機可以用不同的 model（Letta 的 sleep-time agent）與要顧的兩件事。起因是 James 轉來他和 Gemini 的討論，取捨在 V7_DECISIONS。L6b 閱讀 50 → 45 分。）
- 2026-11-12（L9、L10 照「章的順序」檢查：L9 不重排，只改 lede；L10 第 4、5 章對調，晶片在前、量測在後，nav.map 組名改成這堂的骨架，首頁 chip 與 dag.json 跟著改。取捨在 V7_DECISIONS。）
- 2026-11-12（L6b 第 6 章補三處審查留下的 needs-source，重讀 Cisco、MINJA v5、arXiv 2601.05504：Anthropic「使用者完全可信」推到什麼、98.2%／76.8% 是 6 種設定的平均、54 筆的分母論文沒給（82 筆滿分裡的 54 筆）。來源檔同步。）
- 2026-11-12（**L6b 照記憶的四層重排**：六章 → 七章（Transcripts、Memory notes、Memory representations、Injected context、跨層的操作、安全、目錄），James 讀起來不順、自己畫的是四層；新寫 `#i1-3` transcripts 的兩張表與各章開頭；錨點、題庫位置、`l06.html` 的 `#moved` 表、DAG 的 `src` 跟著改。加「章的順序：有依賴就照依賴排」一條。取捨在 V7_DECISIONS。）
- 2026-11-12（L6b 直接放 Anthropic〈The components of agent memory〉的原圖（James 要求試著復用）：1 章〈往右靠〉的效益圖換成原文 Figure 5，`#n-clbench` 註加 Figure 3；2 章〈Session 之間的整理〉加四層圖兩張（session 進行中、dreaming）與 Mt. Moon 對照圖。圖檔在 `docs/img/`（webp，寬 1600）；新寫法 `figure.diagram.shot` 記在 STYLE_ARTICLE 第 6 節；`review_pack.py`、`page_text.py` 讀 `img` 的 `alt`，`audit.py` 檢查 `alt` 與檔案存在。）
- 2026-11-12（L6b 1 章〈往右靠，用「說明用途」來做〉依 James 的可讀性回饋與重讀原文修正：CL-Bench 的對照組其實只說「有記憶資料夾可用」、沒有說明用途，正文與註改寫；圖 6 改成圖例在上、只標數字、虛線框標出少掉的部分（標絕對差距，不標百分比）；Sonnet 4.6 的 0.034 → 0.311 搬進正文；「強的 model 寫用途就夠」補上文章只在 Sonnet 4.6 試過；Pokémon 段補過渡與和主張的關係；最後一段先講「錯了能不能補」再列邊界。Opus 5 筆記改照文章的描述（規則附證據、之前的答案、陷阱），不再說分成答錯／答對兩類。審查紀錄在 review_reports/l06b-20261112/。）
- 2026-11-11（腳本表加 `red_path.py`；新 skill `mark-red`。）
- 2026-11-11（L6b 依一份外部評價調整：研究案例的實驗設定與但書收進四個 `details.gloss`「查閱」（`#n-clbench`、`#n-wiki`、`#n-letta`、`#n-contracts`），正文只留結論與圖；Provenance 補「先看衝突的是哪一類事」；補重讀成本、transcripts 的保存代價。題庫加 k24.7 與 k24g。取捨在 V7_DECISIONS，審查紀錄在 review_reports/l06b-20261111b/。L6b 閱讀時間 40 分。）
- 2026-11-11（L7 整頁可讀性審查（v16）並照 slides 加四張圖：第 7 章六格折線圖與 23 個 benchmark 的時間軸、第 3 章 Pareto 示意圖、第 4 章題數橫條圖；L7 閱讀時間 55 分。取捨在 V7_DECISIONS，審查紀錄在 review_reports/l07-20261111。）
- 2026-11-11（腳本表加 `review_eval.py`、`review_status.py`。）
- 2026-11-11（腳本表加 `check_numbers.py`；`verify.sh`、`quiz.py` 兩列同步。）
- 2026-11-10（L6b 補 Anthropic〈The components of agent memory〉：五個新小節 `#i1-5`、`#i2-6`、`#i2-7`、`#i3-5`、`#i4-6`，延伸閱讀加一篇本文補的「推薦」；L6b 20 分 → 30 分。取捨在 V7_DECISIONS，來源在 sources/l06.md。）
- 2026-11-10（首頁課程地圖的 chip 也改成英文，例如 Memory Design、Reliability、Eval；層名本來就是英文。）
- 2026-11-10（James：課程名稱改成英文，例如 L6 Agent Reliability、L7 Agent Eval、L3 Multi-agent Workflows、L9 LLM Inference Basics。改了 h1、title、側欄、pager、首頁、別頁〈〉引用與 dag.json；英文原標題那行、網址、錨點不動。）

- 2026-11-10（**L6 依觀念拆成兩堂**：L6〈Agent 可靠性〉＋ L6b〈Agent memory〉，James：以觀念切，不以 slides 切，之後 lesson 和投影片不必一對一。加「一堂不綁一份 slides」一條；講次章數、站台檔案、題庫、`add_lecture.py` 各列同步。工具接受 `l06b` 這種 key：`add_lecture.py`（插在原堂之後、前後兩堂互連、首頁列表位置）、`audit.py`、`verify.sh`、`dag.py`、`assemble_v7.py`（順手修好 11-09 後過時的段號與「問題討論」註解）、`add_anchors.py`（`#moved` 表裡的 xN 保留）。`app.js` 加舊錨點轉址（`#moved`）與題庫 `moved_from`，全站 `?v=` 升一號。取捨在 V7_DECISIONS L6。）
- 2026-11-10（題庫一列加 L7。`review_pack.py` 的 code block 從只印前 600 字放寬到 3000 字：L7 第 8 章的 plugin 目錄範例被截掉後兩個 grader 檔，作答者看不到讀者看得到的內容，兩題答不出來。）
- 2026-11-09（**L7 可讀性審查第二次**（WORKFLOW I，替 L7 建題庫之前）：tldr 一包、i1–i4／i5–i7／i8–i9／i10 各一包 `--prefix`。第一輪 62 個 BLOCK（4／19／22／8／9），三個作者 subagent 交替換清單、主線套用；第二輪剩 18 個（2／5／3／3／3 個單位），主線修，沒有審第三輪。修改中更正的事實：第 1 章「1 到 2 分」原文是 naive binomial 區間，不是題目抽樣，和第 4 章 ±11.8 分開；「將近 2 分」是中等資源設定的散布，單獨不顯著；Terminal-Bench 89→66 題是 3.0 換題組＋4.0 刪 8 題；RLI 的 judge 會開真的軟體，難在操作；FrontierCode 不能說第二種飽和還沒到；L4 的 102 比 101 是對照組小贏。）
- 2026-11-09（Skill 一列加 `build-quiz`；`quiz.py` 一列補 `init`、`spec`、`merge` 與用節號、章號挑題。）
- 2026-11-09（題庫加觀念涵蓋：`quiz.py` 一列補 `check` 的涵蓋檢查與 `coverage`、`closed`／`closedcheck`；題庫一列更新 L6 題數。）
- 2026-11-09（拿掉每一堂的「問題討論」段：James 打算在每個觀念後面直接放題目，問題討論和 GitHub 討論串不需要了。L1–L11 刪掉 `section#s-discuss`（基礎題、進階題、自我檢查、GitHub 區塊）與側欄項目，段號改成 1 核心觀念、2 動手試試、3 延伸閱讀，正文裡「第 3 段動手試試」「第 4 段延伸閱讀」跟著改，指向進階題的句子刪掉；側欄與首頁的「GitHub 討論」連結、首頁「留下你的想法」一節、「怎麼讀」裡講討論題的步驟拿掉，閱讀時間重算。各堂討論串 issue 關閉（留言保留）。刪 `tools/discuss.py`、`tools/check_discuss.py`；`verify.sh`、`check_article.py`、`new_lecture.py`、`assemble_v7.py`、`add_lecture.py`、`assemble_ideas.py`、`dag.py` 不再要求或產生 `#s-discuss`。STYLE_BASIC 標停用，STYLE_ARTICLE、WORKFLOW、CLAUDE.md、skill 同步。）
- 2026-11-09（L6 3.1〈每段切幾步最划算〉改成互動圖：James 問驗證成本固定 5 步、能不能調，不同的驗證成本和成功率會改變最佳的 checkpoint 間隔。新增 `docs/calc.js`，圖下兩個滑桿（一次驗證 0–20 步、每步成功率 90–99.5%），長條、最省的那列、`aria-label` 照同一條算式重畫；HTML 裡仍是預設值（5 步、95%）的靜態圖。正文原本手列「驗證算 1 步時六種切法是 663、187…」改成指向滑桿，並補第二個假設：每步越可靠，段切越長（99% 時每段 25 步最省、90% 時每段 5 步），歸成一條規則「驗證越貴、每步越可靠，段就切得越長」。題庫加 k8e；k8 的四題選擇題盲讀作答 4/4，定位都在該節。`edit.js` 開始編輯前先把互動圖還原；`review_pack.py` 把滑桿印成一個單位。「東西放在哪裡」加互動圖一列。可讀性審查第一輪審整個第 3 章：BLOCK 8、NIT 4，新段落沒有 BLOCK；同一節既有的 ¶3（驗證次數要自己乘、「不到 2 次」沒理由）、¶5（數字沒標籤）和圖說的「上面／圖下」已修；第二輪只審這 5 個單位：BLOCK 2（¶5 段長和步數分兩串並列、¶6 的 53 沒寫是總成本），主線修完。第 3 章後半既有文字的 6 個 BLOCK 也照 James 的要求修了：Replit 的「當事人」寫明是 Lemkin、圖5 說明的「3.1 開頭」改成指〈退回多遠〉、context reset 寫出原因（Sonnet 4.5 接近上限會提早收尾）並說明短 session 何時還要切、5／12 步寫出量法並標本文的判斷、「沒有進展」寫出 PostToolUse hook 的做法並說明 8 步擋不到一直改檔的情況、SRE 第一次出現就解釋（checkpoint 從「都是 SRE 習慣」拿掉）。這幾處審了一輪（BLOCK 5，主線修完）。）
- 2026-11-09（L6 第 2 章末尾加本文延伸 `#x5`〈檢查會往兩個方向錯：漏抓與誤判〉：James 問 detect 有沒有考慮 false negative。算式的 1 − detect 就是漏抓，沒算的是誤判；延伸加 false_alarm 的算式與四種檢查的橫條圖，正文第 2 段加一句指過去。取捨記在 V7_DECISIONS L6〈補（2026-11-09）〉。`tools/add_anchors.py` 改成跳過舊頁面留下的 `<span class="anchor" id="xN">` 號碼（L6 的 x1–x4 還有連結指著），不然新的本文延伸會被編成重複的 `#x1`；README 腳本表同步。）
- 2026-11-08（加觀念 DAG：`docs/dag.json`、`docs/dag.html`、`tools/dag.py`、`guide/DAG.md`；「東西放在哪裡」與腳本表各加一列；`verify.sh` 加 `dag.py --check`。James 要把課程改成觀念 DAG 的形式，這是第一版：100 個觀念、164 條邊、8 層、4 個起點；算出 14 個觀念散在兩堂、7 條前置在後面講次的邊。首頁還沒連過去，等他確認。）
- 2026-11-08（加 `tools/quiz.py` 一列、「東西放在哪裡」加題庫一列；`verify.sh` 對有題庫的頁面跑 `quiz.py check`。）
- 2026-11-07（`tools/verify.sh` 加 `all` 模式，「東西放在哪裡」加 CI 一列；見 WORKFLOW J。）
- 2026-11-07（L1 tldr 第 2 條改寫：James 問「聊天是 1 次、750 token、105 token」在寫什麼、為什麼可讀性審查會過。三個數字沒標籤、聊天的數字放在 Copilot 底下像是 Copilot 的、一段對話對一問一答單位不同；改成兩個數字加倍數，聊天的來源用括號標出。照新規則把 tldr 單獨審：第一輪 4 BLOCK、1 NIT，第二輪仍 4 BLOCK（每輪都是新的問題），主線修完、沒有第三輪；tldr 四條都改了，細節在 V7_DECISIONS L1 最後一條。`review_pack.py` 加 `--prefix`、`--since` 也抓 tldr，README 腳本表同步。）
- 2026-11-07（**L1–L8 可讀性審查跑完**（WORKFLOW I）：第一輪 L1–L8 共 506 個 BLOCK（76／48／97／68／37／39／76／65），作者修完；第二輪剩 41 個（3／4／8／8／4／5／6／3），主線修，沒有審第三輪。修改中順手更正的事實、各堂第二輪修了什麼記在 `guide/V7_DECISIONS.md` 各堂最後一條。首頁八堂的閱讀時間同步成審查後的數字（多數多 5–10 分鐘）；`guide/sources/l07.md` 的 ABC 一行與 OSWorld 2.1 一行照核對結果更新。）
- 2026-11-07（L5 4.1〈拆多細〉：同一組數字原本有一張表、又有一張「上表畫成長條圖」，讀者要讀兩次。表拿掉，數字寫進圖的標籤；圖改成橫條，一列一種拆法，「不拆」也是一列，100 秒畫成直虛線，加一列「拆成 3 份」證明 4 份真的最快。圖下的段落補上「每多拆一份，省下的秒數越來越少，比 8 秒少就變慢」這一步，並寫出拆到 9 份以上就比不拆慢。figure-spots 第一個抓到的表圖重複；可讀性審查兩輪，第一輪 4 BLOCK，第二輪 0 BLOCK、3 NIT 已修）
- 2026-11-06（L6 3.1 的 checkpoint 表換成橫條圖〈每段切幾步最划算〉。James 問表有沒有更好的形式。原表最短的是「每段 1 步」53 步，正文卻說不必切到每一步，因為表沒有驗證的成本；圖把步數（灰）和驗證成本（黃，一次驗證算 5 步，本文的假設）疊在一起：每段 10 步最省，5 步只多一點。3.1 開頭補「第 2 章每步檢查是假設檢查不花成本，貴的驗證才分段」，公式改成四行（含驗證次數、總成本），段落改成「兩筆帳」並補平均次數＝機率倒數。可讀性審查兩輪：4／4 BLOCK，第二輪的由主線修完）
- 2026-11-06（`tools/verify.sh` 支援兩份 deck 的講次：頁數改讀頁面的 `data-pages-total`，PDF 取頁面裡所有 slides 檔名的共同前綴；L10 原本會 FAIL。L1–L11 都 ALL OK。新講次簡報註明接線前不要用 verify.sh）。
- 2026-11-06（**新增 L9、L10、L11**，課程網站到 11/02 為止的 slides 都有頁面。編號 James 定：L9 是 10/19 LLM 入門；L10 是 10/21 GPU 入門，11/02 的 2b 是同一堂的後半，兩份 deck 合成一篇（`data-pdf` 是 2a、`data-pages-total` 96）；L11 是 11/02 的作業回饋與十個陷阱（課程排在 Part II，內容接 Part I）。10/26、10/28 的 `_protected` PDF 讀不到內容，沒有頁面。三堂由三個 subagent 同時寫，共用 checkout、各寫各的檔案，簡報是新的 `.claude/skills/idea-first-lecture/new-lecture-brief.md`；骨架用新的 `tools/new_lecture.py`，`assemble_v7.py` 多收 `discuss.html`、`try.html`、`wrap.html`，`add_lecture.py` 直接建 v7 側欄，`discuss.py` 會填新頁的 `#s-submit` 空殼，`insert_digest.py` 在 v7 新頁寫「它和本文哪幾章有關」。每堂的取捨在 `guide/V7_DECISIONS.md`，來源在 `guide/sources/l09–l11.md`。Issue：L9 #107、L10 #108、L11 #109。首頁：課程地圖加 chip、「還沒有 slides 的講次」依 2026-11-06 的時程重寫（batching 改到 11/04、speculative decoding 11/11、scheduling 11/23）、「怎麼讀」加 Part II 的順序。L2、L4 的 token 註依 L9 的實測更正：繁體中文一個字約 0.7–0.9 個 token，不是 1–2 個。push 前跑了可讀性審查（WORKFLOW I）：第一輪 L9 33、L10 71、L11 21 個 BLOCK，作者修完；第二輪剩 2、12、5 個，主線修，沒有審第三輪；細節在 `guide/V7_DECISIONS.md`）
- 2026-11-06（**省 context 與步數**：各檔第 3 行的「更新：」搬到 `guide/CHANGELOG.md`（設 `merge=union`，不再衝突；README 原本 72% 是這一行）；新增 `tools/verify.sh`，一輪檢查一步跑完；截圖改成一則訊息平行 Read 6 張；寫題目的 subagent 改成寫檔、只回報路徑；`register_repo_root` 在 claude.ai session 實測可用，repo 的 CLAUDE.md 與 skill 自動載入。Project 裡的 `guide/README.md` 換成三行指標。）
- 2026-11-06（**新增可讀性審查流程**：WORKFLOW I、`guide/REVIEW_READABILITY.md`（checklist R1–R8、報告格式）、skill `.claude/skills/readability-review/`（含 `reviewer-prompt.md`）、`tools/review_pack.py`（把改過的章印成讀者視角的純文字，表格格子帶欄名與列名）。起因：L6 第 2 章一格「Anthropic（2026-03）：穩定偏正面。單一公司的經驗」James 看不懂，七個腳本都過；原因是腳本只檢查結構與版面，表格文字從未被任何可讀性檢查讀過，而「單一公司要寫明」的規則只說要標、沒說怎麼寫。做法照 code review：另一個 session 的 agent 只拿讀者看得到的文字，逐單位重述、標 BLOCK／NIT，BLOCK 清零才 push，最多兩輪。`check_article.py` 加表格格子的 R5「引用只有出處」、R6「保留語不在括號裡」兩條 warn；STYLE_ARTICLE 第 5 節加「表格格子也是句子」；rewrite-with-example、fact-check-extension、idea-first-lecture 三個 skill 的 push 前都接上這一步。L6 當天跑了第一次 pilot）。
- 2026-11-03（**L1–L8 全部換成 v7**。L4 最後落地：10 章，context 的帳、管 context、設計 tool、search 與 edit、最會過期的 prompt；本文補的是 cache 穩定的排法、Lewis 倍數的條件、只給 shell 行不行、edit 的第二派；基礎題 issue #101 有留言，題目未動。全站：七堂各由一個 subagent 在 worktree 改，做法寫進 WORKFLOW H 與 skill 的 `subagent-brief.md`；每堂的取捨在 `guide/V7_DECISIONS.md`，來源查證在 `guide/sources/`。首頁改寫（開頭、怎麼讀、寫法、地圖 chip、每堂一句話與閱讀時間）；跨堂連結文字對上新章名；Part II 日期依 2026-11-03 的 cs2680.com 更新（首頁、L1、L8、STYLE 第 9 節）；L5 問題討論的說明改成讀文章）。
- 2026-11-03（**L7 換成 v7 依想法重組**：10 章，先講分數是什麼（整個系統的輸出、公開分數回答不了能不能上線），接著五章是讀分數要問的事（指標、雜訊、leakage、grader、飽和），再兩章是自己做評估，最後目錄收八個 benchmark。本文補的：自己怎麼做 eval（Anthropic 2026-01、Husain 與 Shankar、LangChain、Cursor，都是單方經驗）、grader 的效度（OpenAI 2026 撤回、Epoch、Berkeley RDI、METR）、harness 與基礎設施的雜訊（ARC Prize 2026-09、Anthropic 2026-02）。Terminal-Bench 題數依官方公告，和 slide 不同。issue #104 當時 0 則留言，基礎題依新章節重出）。
- 2026-11-03（**L3 換成 v7 依想法重組**：10 章，先決定要不要加 agent（三個軸、Amdahl、人的 review、終點與驗證），再來是四種放大（手動平行、subagent、team 與 workflow），接著承接 L2 的 plugin 案例（Superpowers 與 mattpocock/skills 並排、Caveman），最後 dsh-superagent。本文補的：review 排隊算式、獨立量測（METR、Faros、Anthropic）、plugin 的信任邊界。Caveman、SWE-Shift 的查證 `#x1`、`#x2` 保留。manifest、scope、27 skill 等收成查閱，事實依 2026-11-03 重抓。基礎題 issue #100 有留言，題目未動）。
- 2026-11-03（**L1 換成 v7 依想法重組**：10 章，先講 agent 是另一種 workload、目標要換（鏈、throughput 是錯的目標、人的時間），再來是地圖（stack、agent 這一層）、底層（五個假設、時間、狀態、不確定與故障，Part II 的起點）、目錄。本文補的：真實 trace（Microsoft Azure Research 的 GitHub Copilot trace、TraceLab，都是 2026-06）、人的時間（TraceLab、Faros 2025、METR）、KV cache 的業界解法（Mooncake、LMCache、DistServe、Dynamo）。舊 2.1 課程範圍收進目錄。基礎題 issue #98 有留言，題目未動）。
- 2026-11-03（**L8 換成 v7 依想法重組**：10 章，先把帳算對（成本公式與分母、重讀的 context、prompt cache、淨節省），再照順序壓（少走幾步、model／effort／output），接著上限、完成時間、harness 邊界、目錄。本文補的：分母（Voss 2026-07）、cache 的帳與 TTL（TraceLab 2026-06、Don't Break the Cache 2026-01；官方定價 cache read 已降到 0.05×、0.025×，L2 同步改成「十分之一或更低」）、harness 的三個問題（Managed Agents 2026-04）。issue #105 當時 0 則留言，基礎題依新章節重出）。
- 2026-11-03（**L6 換成 v7 依想法重組**：10 章分五組，長任務靠攔錯（錯誤相乘、驗證、checkpoint 與上限、失敗分層）排在 memory 前面，接著記憶讓錯誤活過 run（要不要記、時間與來源、檢索）、放在哪裡、安全、目錄。本文補的：算式的兩個前提（Failure as a Process 2026-07、Recovery-Bench 2025-08）、檢查要真要早（ImpossibleBench 2025-10）、先用檔案（Letta 2025-08、SWE-ContextBench 2026-02）、記憶中毒。issue #103 當時 0 則留言，基礎題依新章節重出）。
- 2026-11-03（**L2 換成 v7 依想法重組**：10 章分三組，一定要會（Loop、文字與程式、Context）、要防的（權限與 sandbox、prompt injection）、要用時會做（記憶、hook、skill、MCP、plugin）。本文補的：sandbox（Bash 規則不是安全邊界）、injection 防禦被破的結論、CLAUDE.md 與 skill 的實驗（ETH 2026-09、Vercel 2026-01）。基礎題 issue #99 有留言，題目未動，只重寫「相關：」）。
- 2026-11-03（L5 的 5 題基礎題依 v7 章節重出：只能傳文字（第 1、8 章）、要不要拆與讀寫（第 2、3 章）、派工與拆多細（第 4 章）、回報與失敗（第 5、6 章）、狀態與時間（第 7 章），qtag 連到章、不連 slide 頁碼；issue #102 當時 0 則留言，內文已同步。`discuss.py` 依頁面判斷 v7（沒有 `#s-arch`）：段號、issue 文字、連結跟著變；STYLE_BASIC v4.0 加「v7 頁面」一節。進階題未動）。
- 2026-11-03（**L5 換成 v7 依想法重組的版本**：試讀頁 `l05-v2.html` 的核心觀念取代原本的 8 章，問題討論、動手試試、延伸閱讀沿用並修好連結，段落變成 4 段；`l05-v2.html` 改成轉址頁。別頁連進來的錨點：index chip 改連 `#i9`，L3 改連 `#i1`、`#i4`，L6、L8 的 `#t3` 保留。`check_article.py` 的 `#s-arch` 改成可有可無，`check_discuss.py` 章數上限 10、整頁沒有 `a.ref` 也可以。新增 `tools/dg.py`（畫圖）與 skill `idea-first-lecture`。其他講次逐堂改）。
- 2026-11-03（L5 試讀版第 4 章重寫兩段：六種拆錯改成「拆錯／長什麼樣／擋它的欄位」表，欄位用 subtask.yaml 的 key；「拆多細」先定義四段時間，再給公式與逐列算出的表。James 看不懂原段：欄位名和 yaml 對不上、「八個欄位擋六種」數不起來、critical path 等名詞沒定義）。
- 2026-11-03（L5 試讀版加第 7 章「狀態與時間」：consistency 與 lost update（git push 被拒當例子）、CAP 與 PACELC、沒有全域時鐘與 Lamport clock、tracing 與 Claude Code 的 parent_tool_use_id、不確定性；原第 7、8 章改為第 8、9 章。圖裡的專有名詞改成英文）。
- 2026-11-03（L5 試讀版第 6 章補 partial failure：timeout 不等於失敗、心跳與租約、fencing token、部分結果，加一張租約時序圖）。
- 2026-11-03（新增試讀頁 `docs/l05-v2.html`：L5 依想法的重要性重組，不照 slides 順序、不寫 slide 頁碼，補讀寫分界與 agent 間的 prompt injection 兩章。James 看完決定要不要取代 `l05.html`；腳本 `audit.py`、`check_article.py` 不檢查這頁，圖用 `check_diagrams.py`）。
- 2026-11-02（L5 補 15 張圖，共 29 張：八種架構一種一張、總覽、拆錯、medium、timeout、A2A 抽象與追蹤、MCP；圖能說的從文字拿掉，每種架構的「三張圖的答案」移到圖底。2.3 的 p.17 描述依投影片更正。規則見 STYLE_ARTICLE 第 6 節 v6.1）。
- 2026-11-02（L5 的 14 張圖改成接近 slide 的畫法：填色方塊無外框、灰色直角線、深紅只標重點、字放大；第 1 段的總圖拆成兩張。規則見 STYLE_ARTICLE 第 6 節 v6.0，其他講次未改；新增 `tools/check_diagrams.py`）。
- 2026-11-02（**L1、L2、L5 依 v5.9 整理，知識點回正文**。L1 的 4 個本文延伸 `#x1`–`#x4` 和 KV cache、MTBF 兩個註，L5 的 4 個本文延伸和 5 個註，都改成正文段落，段首標「本文的判斷」，錨點留在 `span.anchor`，章內小標 id 往後移。L2 從 4 章擴寫成 8 章 3 組：A 2.1 Loop、2.2 Context、2.3 權限；B 2.4 記憶、2.5 CLAUDE.md、2.6 Auto memory 與記憶的成本；C 2.7 四種擴充機制與 skill、2.8 MCP、hook 與 plugin。16 個深入與本文延伸只留 2.1 末尾的各家 API 對照表 `#d1`（查閱用），其他併回正文。2.8 是新寫的：MCP tool call 的三段資料、選讀頁的元件與安全、hook 的 stdin JSON 與 `block-rm.sh`、「載入確定不等於遵守確定」的對照表、設計練習七題的「為什麼不是別的」；hook 事件數、exit code、`claude mcp add` 依 2026-11 的官方文件。L2 的 slide 頁碼全頁校正成 PDF 頁數：舊頁面從 p.7 起都少 1，依 `slides/l02-notes.md` 的 footer 換算。`#tN`、`#xN` 錨點都保留；首頁 chip、L3、L6 連到 L2 的章號更正；首頁 L2、L3、L5 的閱讀時間同步）。
- 2026-11-02（L3 2.6 Amdahl's law 加兩張折線圖：「三個推論」改成 ol，後面放加速倍數圖（s＝20%、10% 兩條線、理想線、5 倍與 10 倍上限，標 4／4.7／6.4 倍）；「真實情況更差」那段插一張總時間圖（20 ＋ 80 ÷ n 對照再加 0.5 × n 的協調成本，最低點約 13 個 agent、33 分；0.5 是本文的假設）。圖由 `notes/l03/fig*.html` 的 python 產生，橫軸 log2）。
- 2026-11-02（L3 2.8 末尾加本文補的案例 `#i8-7`–`#i8-11`「dsh-superagent」：DeepSeek Harness 團隊 2026-10-31 公開的研究原型（`deepseek-ai/dsh-superagent-prototype`，MIT），一個替整個團隊做事的 coding agent，設計原則是向人要最少的注意力。內容：五條規則、主 Session／worker 的分工（對照 2.5 的 A–D、2.6 的 lock file 與 `maxWorkers` 1–16 外加一個人的位子）、授權由 host 程式碼管的五層與「誰能起頭工作」表（對照 2.7）、操作者的四條責任與面板的三個問題；一張流程圖、一張表、兩個 snippet（`prompts/team/communication.md` 的例句、本文擬的 GitHub 對話）。2.8 從 3 分擴到 10 分（剛好 4,000 字，章的上限）；2.5、2.6、2.7、進階題 Q3、tldr、lede、fineprint、nav.map、側欄各加一句或一項指過去；2.4 的 map 分鐘數 5 → 6 更正。放成章內小標而不是新章，因為 L3 已有 8 章（上限）；放在 2.8，因為它回答 `#i8-5` 的 review 瓶頸。事實依 2026-10-31 的 repo（只有一個 commit），repo 更新就重抓核對；README 提到的文章〈Exploring Super-agent Design: Towards a More Autonomous Agent System〉沒找到公開版本，找到再補進延伸閱讀）。
- 2026-11-02（L3 2.5 D 的「兩種啟動方式」James 看不懂：改成先講 script 是 Claude 寫、runtime 背景跑，再用一個 code block 列 `ultracode` 關鍵字（只管這個任務）、`/effort ultracode`／`off`（整個 session）、`/workflows` 看進度；依 2026-11-02 的官方 workflows 文件，`/effort ultracode` 是 session 開關，不是 effort 等級，先前寫的「調到最高」已更正）。
- 2026-11-02（L3 語意 review：2.4 末尾 p.37 的「留在主對話／交給 subagent」清單原本是一段裡兩串頓號，James 讀成兩串都是 subagent 的用法；改成一張表，左欄情況＋小字為什麼、右欄交給誰，skill 那條也補了理由；p.36 三種叫法的註解統一成「只影響這一次」；巢狀上限改寫成「slide 5 層、文件預設 3 層」並和 2.5、第 4 段對齊；動手試試的「不一定載入 CLAUDE.md」改成「自訂的會讀、Explore／Plan 不讀」；2.1 的「2.1 下面」自我指涉改成指到那一節；2.5 的 `/effort ultracode` 補一句它做什麼；進階題第 1 題指到這張表）。
- 2026-10-30（L3 2.1 補 manifest 是什麼（說明檔的通稱，對照 package.json、AndroidManifest.xml）與新小節 `#i1-4`「裝在哪：三個 scope」：user／project／local 寫進哪個 settings.json、local > project > user、project scope 隊友要自己再 install 一次、檔案一律在 `~/.claude/plugins/cache/`、開著的 plugin 每圈佔 context 所以用不到就 disable；依 2026-10 的 code.claude.com plugins／install／loading 文件。後面的小標 id 往後移一號）。
- 2026-10-30（**L3 的核心觀念重排，知識點回到正文**：James 說內容雜亂、太多知識點放在補充、Superpowers 版本對照幫助不大、mattpocock 應該和 Superpowers 放一起。仍 8 章但改成 3 組：A 承接 L2 2.4 的擴充機制，2.1 Superpowers → 2.2 mattpocock/skills（本文補的）→ 2.3 Caveman，三個 plugin 的並排表移到 2.3 末尾；B 2.4 平行與 subagent、2.5 team 與 workflow（末尾加 implement-spec 案例）、2.6 長時間執行與 16 個 agent（Amdahl 與「任務切不開」改成正文）；C 2.7 Programming 3.0、2.8 田野證據。收合區塊從 17 個減到 7 個：plugin 結構、settings.json 位置、「沒有 hook 怎麼保證」、「proxy 用規則不用 model」、Amdahl、人的角色、讀數字要小心都改成正文；本文延伸只剩 `#x1` 回答寫短真的好嗎（2.3）、`#x2` SWE-Shift（2.4，砍一半）；版本對照縮成一個 3 項清單（`#i1-8`）。`#tN` 錨點保留；`#x5` 留一個 anchor span 在 Amdahl 一段；index chip、L5、L6、L8 連進來的 `#iN`、`#x5` 已改。`tools/assemble_ideas.py` 現在也會把開頭有 `span.anchor` 的小標列進側欄。規則見 STYLE_ARTICLE v5.9）。
- 2026-10-30（新增 skill `.claude/skills/fact-check-extension/SKILL.md`：查證 James 轉來的評論或文章，逐條對回原始來源，寫成本文延伸；10-29 的 Caveman 評論與 10-30 的 SWE-Shift 各做過一次。rewrite-with-example 第 3 步改成直接改 HTML、push 後再回報，不先給純文字版（James：幾乎不看純文字版）。WORKFLOW A1 註明 `register_repo_root` 只有 Claude Code 有；WORKFLOW B3 與 STYLE_ARTICLE 的範本從 l02 改成 l05）。
- 2026-10-30（L3 2.3 加本文延伸 `#x4`「主幹在動的時候：一個 benchmark，與『worktree 隔離、換 context 合併』的建議」：查證 James 轉來的一段評論（原出處待補，簡體中文）引用的 benchmark 是 SWE-Shift（Huang 等，arXiv 2610.32196，2026-10-23）：120 個場景、12 類變動、9 個節點 T10–T90、GPT-6 Astra 67.35% → 24.79%、PSR 20.34%；數字依 repo `JeixHuang/SWE-Shift` 的 `docs/paper/results.json` 與 `cases/public/*/case.json`（2026-10-30 比對；arXiv 全文當時被 rate limit，沒讀到）。內容：12 類變動表（agent 怎麼得知、worktree 擋不擋得住、兩個最強系統的 PSR）、T10–T90 的 PSR 折線圖、評論兩個痛點的查證、建議的範圍（只對別人改檔案的四類成立）、Claude Code 的兩段流程 snippet。原本的 `#x4`–`#x9` 改成 `#x5`–`#x10`，L5、L8 連到 `l03.html#x4` 的兩處一起改；2.3 正文「merge 也還是你的事」後加一句指過去。表在 390px 放不下時，把次要欄併進第一欄的 `<small>` 第二行、表頭只留短字，見 STYLE_ARTICLE 第 4 節的版本對照表那條）。
- 2026-10-29（**L5、L6 的核心觀念擴寫到 v4.0 密度**，各從 5 章拆成 8 章，正文 13 分鐘 → L5 40 分鐘、L6 35 分鐘：L5 是 2.1 要不要拆、2.2 中心化四種、2.3 去中心化與混合、2.4 子任務、2.5 粒度與拆錯、2.6 溝通的設計空間、2.7 分散式系統問題、2.8 兩個協定與四條原則；L6 是 2.1 兩層與七個問題、2.2 寫入與格式、2.3 backend／控制 policy／擁有權、2.4 檢索、2.5 反思遺忘與有效時間、2.6 八種失敗與評估、2.7 錯誤相乘、2.8 失敗的五層（26 種型態）。舊的 `#tN`、`#n-*`、`#xN` 錨點都保留；章號變了，所以 index 的 chip、L2、L3、L7 連進來的 `#iN` 已更正。章是用 `tools/assemble_ideas.py` 從 `notes/lXX/iN.html` 片段組回頁面的，見 WORKFLOW C）。
- 2026-10-29（L3 2.4 的本文延伸 `#x4` 改寫成「Amdahl's law：16 個 agent 為什麼不會快 16 倍」：補來歷（Amdahl 1967）、用 100 分鐘的例子一步步算、算式放 code block、加一張 n＝1／4／16／64／∞ 的總時間橫條圖，推論分成上限 1 ÷ s、報酬遞減、先縮 s 比加 agent 有效、真實協調成本更差（連 L5 `#x4`）、Gustafson's law 的反面；錨點不變）。
- 2026-10-29（L3 2.2 加本文延伸 `#x3`「回答寫短真的好嗎」：查證林承慶〈Caveman: 簡化 token 真的好嗎?〉（方格子，2026-06-04）的四個提醒與一個想法，對回原始來源，補上之後的量測（Renze & Guven 2024、Guzik 2026-04、JetBrains 2026-07、Adobe CAVEWOMAN 2026-06、Caveman v4.0.1 的三組 eval 與 L8 的花費比例）；原本的 `#x3`–`#x8` 改成 `#x4`–`#x9`，L5、L8 連到 `l03.html#x3` 的兩處一起改；2.2 正文 65% 那句與進階題第 2 題的參考觀點各加一句指過去）。
- 2026-10-29（L3 名詞註 `#n-plugin-dir` 改寫：James 讀成「skill、hook 不在 plugin 裡」，原因是第一句只說「這個資料夾」，沒先說 plugin 是整個 repo。改成先講 plugin = 整個 repo、`.claude-plugin/` 只放身分證，附 Superpowers v7.0.1 的 `plugin.json` 全文、「沒有 plugin 自己搬 vs 有 plugin」對照表與 `claude plugin` 指令；正文那句與 p.8 目錄樹同步。事實依 2026-10-29 的 repo 與 code.claude.com 的 plugins-reference）。
- 2026-10-29（L3 2.2 與基礎題 Q2 的 Caveman 雙向壓縮圖重畫：箭頭標 ①②③、skill 搬回 agent 框、底部改成「誰碰得到整個 request」；圖說改成先問題後結論，名字和圖一致；正文補一句 request 是什麼。原圖說的「上方／下方箭頭」對不上圖，request 也沒定義）。
- 2026-10-28（L3 名詞註 `#n-hook-files` 改寫：先說 hook 是什麼，三個 `settings.json` 位置改成表，加一個本文補的專案案例。名詞註可以放表和 code snippet（STYLE_ARTICLE v5.8）。這類「看不懂、補案例」的改寫做法寫成 skill `.claude/skills/rewrite-with-example/SKILL.md`，在 claude.ai 也可以用同一份。James 看不懂通常是語句不順或某個詞缺 context，不是句子太長；skill 以此診斷，必要時加圖，圖看不懂再減框改標籤）。
- 2026-10-28（側欄目錄拿掉 A／B／C 分組，核心觀念底下只列 2.1、2.2…；分組留在正文與閱讀地圖，見 STYLE_ARTICLE v5.7）。
- 2026-10-28（L3 2.1 加最後一節 `#i1-5`「Slide 之後，Superpowers 改了什麼」：slide 對應講課時的 v6.3.0，對照 2026-10-28 的 v7.0.1，寫明每項何時改、為什麼；2.8 比較表的 Superpowers 欄依 repo 更正；規則見 STYLE_ARTICLE v5.5）。
- 2026-10-28（L1、L7、L8 的正文擴寫到 v4.0 密度，三頁都是 6–8 章、閱讀 30–40 分鐘；全站 L1–L8 現在都是「文章是主體」的版本）。
- 2026-10-28（L1、L7、L8 改成 v5.0 版面，全站 L1–L8 都是 5 段；README 第 9 行與 STYLE_ARTICLE v5.4 第 3、4 節同步）。
- 2026-10-28（紅字依長度配、每個 code block 都有編輯器外框、上色移到 `docs/code.js`，全站一致，見 STYLE_ARTICLE v5.3）。
- 2026-10-28（L3 加 2.8「本文補的案例」：mattpocock/skills，slide 沒有的第三個 plugin 案例，和 Superpowers、Caveman 並排；規則見 STYLE_ARTICLE v5.2）。
- 2026-10-28（紅字重點 `<strong>`、code snippet 改成 IDE 配色，見 STYLE_ARTICLE 第 6c 節；`check_article.py` 多檢查紅字）。
- 2026-10-27（L4 先行：觀念補充併入核心觀念，詞條改成正文裡的收合註 `details.gloss`，章編號 2.1–2.7 分三組、段首閱讀地圖、目錄多一層；L4 因此只有 5 段，其他講次仍 6 段，見 STYLE_ARTICLE v5.0）。
- 2026-10-27（「大家的討論」併入問題討論末尾，延伸閱讀編為第 6 段）。
- 2026-10-26（全站取消「延伸思考」段，推論併入章節的「本文延伸」收合區塊，段落改為 6 段；指令與設定檔一律 code snippet、每章至少一張圖或表，STYLE_ARTICLE v4.1）。
- 2026-10-25（文章改為不看 slides 也能讀完的主體，名詞就地解釋，見 STYLE_ARTICLE v4.0；L3、L4 已改寫）。
- 2026-10-22（進階題每堂最多 3 題）。
- 2026-10-21（討論改為每堂一串；延伸閱讀的「推薦」也附摘要）。

## WORKFLOW.md
- 2026-11-12（C 加〈補新材料之前，先判斷它是內容還是骨架〉與重排一堂的做法。起因是 L6b 補 Anthropic 研究文時只加小節、沒換骨架。）
- 2026-11-11（加 I2〈標紅字：審查過了才做〉：紅字獨立成 I 之後、D 之前的一步，`red_path.py` 當關卡；寫作的 skill 不放 `<strong>`。）
- 2026-11-11（I：審完跑 `review_status.py mark`；選要審的章時也看 `status` 的「舊規則」「改過」；James 說看不懂先加 `guide/review_cases/` 再改規則、跑 `review_eval.py`。）
- 2026-11-11（J 的第 1 層加 check_numbers。）

- 2026-11-10（加 K〈一份 slides 拆成幾堂〉：用 DAG 決定切點、key 加字母、章號重編、舊連結 `#moved`、題庫 `moved_from`、別頁連結、檢查與審查。第一例是 L6 → L6／L6b。）
- 2026-11-08（J 的第 2 層改成 pilot：L6 第 1–4 章題庫，手動跑；細節在新的 `QUIZ.md`。）
- 2026-11-07（新增 J：CI 三層設計；第 1 層 `.github/workflows/verify.yml` 上線，push 與「問 Claude」跑完後對全站跑 `verify.sh all`，只亮燈不擋。D、G 各加一句。起因：James 問改一章時能不能有 regression test。）
- 2026-11-07（verify.sh 多一段 figure-spots 提示：`tools/find_figure_spots.py` 列出結論是形狀的數字表和段落、以及表和圖重複的地方；決定留著的加 `data-no-figure`。James 問要不要另開一個找圖的流程；掃過 L1–L11，典型的地方多半已經有圖，所以併進現有檢查，不另開流程）
- 2026-11-07（I：審查包改用 `--prefix`（前文當上下文、後文不給），改到 tldr 時 tldr 單獨一個審查者；checklist 範圍改成 R1–R14，報告每條多一行「靠：」。）
- 2026-11-06（B3 新講次改成先用 `tools/new_lecture.py` 建骨架、片段組裝；好幾堂同時寫用 `new-lecture-brief.md`，共用 checkout；B5 的 `add_lecture.py` 直接建 v7 側欄）
- 2026-11-06（A1：claude.ai 的 session 也有 `register_repo_root`，實測可用；B3：subagent 寫檔、只回報路徑；B4、C5：用 `tools/verify.sh`，截圖一則訊息 Read 6 張；E1：更新紀錄寫進 CHANGELOG。）
- 2026-11-03（L1–L8 都改完 v7；H 補上組裝工具與多堂同時改的做法；B3 的新講次寫成 v7）。
- 2026-11-03（加 H：把一堂改成 v7 依想法重組）。
- 2026-11-02（加 G：線上編輯與「問 Claude」）。
- 2026-10-30（`assemble_ideas.py` 的側欄第三層也會抓開頭有 `span.anchor` 的小標；L3 重排用它組回，片段是用 `notes/l03/build_iN.py` 從舊頁面切出來的，大改既有頁面時可以照這個做法：先切片段、改片段、再組回）。
- 2026-10-30（A1 註明 `register_repo_root` 只有 Claude Code 的 session 有；B3 的範本從 l02 改成 l05）。
- 2026-10-29（C 加「大改一堂的核心觀念」的片段組裝法，`tools/assemble_ideas.py`）。
- 2026-10-28（L1、L7、L8 改成 v5.0，全站 5 段）。
- 2026-10-27（L4 改成 5 段的 v5.0 版面；B4 加一步算各章分鐘數）。
- 2026-10-21（討論改為每堂一串、只放基礎題）。

## STYLE_ARTICLE.md
- 2026-11-13（第 0 節加〈不提 slides 怎麼寫〉：不寫「課程／slides／講者怎麼說」、不標「本文補的」、不寫 slides 的筆誤與頁碼；留 Slides 連結、fineprint、「本文的判斷」。第 4 節〈5 延伸閱讀〉換成〈3 原文出處〉：只列標題與連結。）
- 2026-11-13（第 1 節加〈業界的詞優先，先接上讀者已經會的東西〉與「讀者已知的詞」清單草稿。起因是 L6b 第 4 章把 RAG 寫成「五個訊號」。）
- 2026-11-12（第 0 節〈章的順序〉的判斷法加一個訊號：名詞第一次出現只能往後指「第 N 章」，就是依賴倒過來了；例子是 L10 的量測與晶片。）
- 2026-11-12（第 0 節加〈章的順序：有依賴就照依賴排，重要性不靠章序表達〉：獨立的想法照份量排；資料流、層次照依賴排，每章開頭先說這一層是什麼；一堂只有一張地圖。L6b 第一個照這條重排。）
- 2026-11-11（6c 加「什麼時候標」：可讀性審查過了才標，只搬標籤不改字。）
- 2026-11-13（6c 加〈數量是結果，不是挑選的方法〉與四個逐句的判準；上限改成 round(字數 ÷ 120)；`mark-red` skill 加 2b。起因：James 問 L6b 一句例外為什麼沒紅字。L6b 逐句重掃，67 → 86 處，文字沒改。）
- 2026-11-13（6c 紅字數量：James 讀 L6b「畫紅線的部分可以再多一點」。每章上限從 5 改成 round(字數 ÷ 150)，下限不變；`check_article.py` 加 `mark_max`，`mark-red` skill 同步。L6b 29 → 67 處，只加 `<strong>`、文字沒改；加的時候各章審查狀態是「改過」，用 `red_path.py --force` 看的，下次重審後要再看一次紅字。其他堂沒有重標。）
- 2026-11-11（6c 紅字：寫明目的是掃讀路徑（只讀 h3、`<b>`、紅字推得回論證），加三個檢查（`<b>` 是題目、紅字是答案；離開上下文看得懂；標意思不只標數字）；優先順序改成結論與做法第一、數字第三。L6b 依此重標 17 處，數量 25 → 26，文字沒改。）
- 2026-11-11（第 2 節第 6 點改寫：「先看這裡」從摘要改成案例導讀，四塊固定寫法；L1–L11 與 L6b 全部照這個形式重寫，每堂 tldr 單獨審兩輪。審查紀錄在 `review_reports/tldr-20261111d/`。）
- 2026-11-11（第 0 節加「做法從第一性原理推出來，不敘述誰怎麼做」：性質 → 做法 → 代價 → 產品當例子。起因是 L6b 第 2 章 dreams 那張圖只寫了 Anthropic 怎麼做。L6b 該段已照這條改寫，圖最後一格由「人看過」改成「換上或丟掉：人審或自動」。）

- 2026-11-11（pilot，規則還沒改：L6b 的「先看這裡」改成案例導讀。起因是程度落後的組員反應沒有案例、看不懂。寫法：一個不用術語的案例、這堂回答的問題、三條各自回到同一個案例的判斷、一行指路；數字與實驗設定留給正文。同一個案例在第 1、2、3 章開頭接回來。James 讀得懂之後，再改第 2 節第 6 點並套到其他堂。審查紀錄在 `review_reports/l06b-20261111c/`。）
- 2026-11-10（第 0 節加〈一堂不綁一份 slides〉：堂依觀念切，判斷用 DAG；拆出來的堂用原編號加字母；兩堂各自讀得懂、過場句與 meta 的寫法。）
- 2026-11-10（版本號那條補 `app.js`：改了它也要往上改全站的 `app.js?v=`。）
- 2026-11-09（第 6 節加〈互動圖〉：結論取決於本文的假設、正文得逐一列出換值的結果時，用滑桿；HTML 留預設值的靜態圖，`docs/calc.js` 重畫。範例 L6 3.1。）
- 2026-11-07（**可讀性優先於長度**：第 5 節開頭加總原則，這份、STYLE_BASIC、STYLE_DIGEST 的句數、字數、段長都改成提醒；第 3 節 tldr 不再限 thesis 3–4 句、每條 1–2 句；第 5 節句長 70 字、一段 6 句改成「拆了會斷因果就不拆」「論點需要就寫更多句」。James：壓字數是為了省時間，讀不懂反而花更多時間。起因 L1 tldr 單獨審查後兩條要 3 句。）
- 2026-11-07（第 6 節〈數字表換成圖〉加：同一組數字不要表和圖各放一次，留圖；figure-spots 與 `data-no-figure`）
- 2026-11-06（第 6 節加一條：比一組數字的趨勢、轉折或最佳點，用照比例的橫條圖代替表；結論說「最划算」時，兩邊的成本都要畫進圖。例子 L6 3.1）
- 2026-11-07（第 5 節「兩檔都適用」第 4 條：數字要帶標籤、算好倍數、看得出撐哪個結論，兩組以上做成表或圖，tldr 和摘要只留一兩個數字。起因 L1 tldr「聊天是 1 次、750 token、105 token」。）
- 2026-11-06（第 0 節加「新講次」一條：L9–L11 的問題討論與摘要都連到本頁的章；第 9 節加 L9–L11，Part II 時程依 2026-11-06 的課程網站）
- 2026-11-06（第 5 節加第 5 條「表格格子也是句子」；新增 `REVIEW_READABILITY.md` 與 skill `readability-review`：改正文後、push 前由另一個 agent 讀一遍，見 WORKFLOW I）。
- 2026-11-03（**L1–L8 全部改完 v7**：各堂的決定見 `guide/V7_DECISIONS.md`；第 0 節加「文字裡不寫別堂的章號」；第 6 節的 v6.0 畫法現在是全站核心觀念的畫法；第 9 節 Part II 的日期依 2026-11-03 的課程網站更新）。
- 2026-11-03（**v7.0：依想法的重要性重組**，L5 先行，見第 0 節；做法寫成 skill `.claude/skills/idea-first-lecture/SKILL.md`，畫圖用 `tools/dg.py`。James：「以最適合的方式吸收投影片的內容，不需要在文章特別寫投影片第幾頁講了什麼」。L1–L4、L6–L8 還是 v5.9／v6 的版面，逐堂改）。
- 2026-11-03（第 6 節加一條：圖裡的專有名詞用英文；James：「你的圖盡量用英文，例如 heartbeat 之類的專有名詞」）。
- 2026-11-02（刪除每堂「先看這裡」的通用讀法 `.readhow`，見第 3 節第 6 點）。
- 2026-11-02（v6.1：講架構、流程、狀態的地方一律有圖，圖說得出來的就不再用文字重複，見第 6 節；James：「看投影片很舒爽，我的文章字太多、圖相對少，講架構的地方不畫圖很奇怪」）。
- 2026-11-02（v6.0：圖改成接近 slide 的畫法，L5 先行，見第 6 節；James 問「為什麼我們的圖跟投影片差這麼多」）。
- 2026-11-02（L1、L2、L5 依 v5.9 改完：本文延伸併回正文，段首標「本文的判斷」；L2 擴寫成 8 章，深入只留 2.1 的 API 對照表。全站 L1–L8 現在都是 6–8 章）。
- 2026-10-30（v5.9：**知識點放正文，收合區塊只放查閱與查證**。James 讀 L3：「內容有點雜亂，很多知識點你用補充的」「版本比較對讀者幫助不大」「matt 應該要跟 superpowers 放在一起」。三條規則：（1）章的論證需要的東西一律寫在正文：機制的事實（plugin 的檔案結構、settings.json 的位置、proxy 用規則不用 model）、公式（Amdahl）、對案例的判斷（沒有 hook 怎麼保證）都是正文，不收進名詞註或本文延伸；名詞註只放名詞，本文延伸只放對外部評論、benchmark 的查證這類離主線的東西，一章最多 2 個，合計不超過該章正文的長度。（2）版本對照縮成章末一段或最多 3 項的清單（沒變的、改最多的、slide 沒提但後面會用到的），不放表；只有 slide 的結論因改版不成立時才列表對照。（3）本文補的案例章放在它對照的 slide 案例旁邊，不另立一組放最後；並排表放在那一組的最後一章末尾。L3 依此重排：8 章 3 組，收合區塊 17 → 7；v5.8 的名詞註案例 `#n-hook-files` 已改成 2.1 的正文 `#i1-6`。見第 4 節）。
- 2026-10-29（**L5、L6 的正文補到 v4.0 密度**：各 8 章、每章 3–6 分鐘，read-time 40 與 35 分鐘；全站 L1–L8 現在都是 6–8 章的「文章是主體」版本，L2 除外（4 章，深入區塊仍在）。改法見 WORKFLOW C 的片段組裝）。
- 2026-10-28（v5.8：**名詞註可以放案例**。`details.gloss` 不再限 2–4 句：讀者說看不懂的註，先一句定義名詞，三個以上的平行項目改成表，補一個本文補的案例（`figure.file`，真的檔名和內容），上方已有的 code 指過去不重貼；L3 `#n-hook-files` 是第一個（2026-10-30 已併進 2.1 正文 `#i1-6`，因為它是主線需要的事實，見 v5.9）。做法見 `.claude/skills/rewrite-with-example/SKILL.md`，規則見第 4 節第 2 段的名詞註）。
- 2026-10-28（v5.7：**側欄目錄不放分組**。側欄的核心觀念底下只列章號 2.1、2.2…，不放 A／B／C 分組列。分組只留在正文的 `p.idea-group` 與閱讀地圖 `nav.map`，那裡有副標說明。原因：側欄同時有段號、字母、章號三套編號，讀起來混亂。L1–L8 同日改完，`styles.css` 刪掉 `.sn-group`、`.sn-g`。見第 4 節「分組與地圖」）。
- 2026-10-28（v5.6：**並列項目一項一行**。一段裡用「；」串起 4 個以上並列的項目（skill、指令、策略、論文、假設），改成 `ul`／`ol`；`check_article.py` 對這種段落印 warn。L1–L8 同日改完。見第 4 節第 2 段「寫因果，不要條列 slide」那一條）。
- 2026-10-28（v5.5：**slide 案例的版本對照**。Slide 拿一個會改版的 repo 當案例時，寫明 slide 對應哪一版、現在是哪一版、改了什麼、為什麼改，讓讀者判斷 slide 的內容還成不成立；L3 2.1 的 Superpowers 是第一個，見第 4 節第 2 段的最後一條）。
- 2026-10-28（**L1、L7、L8 的正文補到 v4.0 密度**：每頁 6–8 章、每章 3–7 分鐘，第 1–4 段各約 30–40 分鐘；L1 加了一章課程範圍（p.9–26）；三頁的 `#iN` 重編號，index chip 與 L3、L6 的連結已同步）。
- 2026-10-28（v5.4：**L1、L7、L8 也改成 v5.0 版面**：全站 L1–L8 都是 5 段；同日稍後再擴寫內容；第 3 節第 7 點、第 4 節的段號說明同步）。
- 2026-10-28（v5.3：**全站一致**。紅字改成依長度配：每章正文每約 200 字 1 處（1–5 處），深入／本文延伸合計最多 1 處，`tldr` 剛好 3 處，架構剛好 1 處；L1–L8 依此重調。每個 code block 都包成 `figure.file`、有 figcaption，輸出也是；上色移到 `code.js`，`l02-readings.html` 也套用同一套樣式。見第 6c 節）。
- 2026-10-28（v5.2：**本文補的案例章**，L3 2.8 mattpocock/skills 是第一個；見第 4 節第 2 段的最後一條）。
- 2026-10-28（v5.1：**紅字重點與 IDE 配色**。`<strong>` 顯示成紅色粗體，標關鍵數字、結論、代價／風險，每章 3–6 處；`<b>` 仍是黑色粗體小標；code snippet 一律是深色編輯器底，`app.js` 依語言上色；inline `<code>` 改成紫色。L1–L8 同日標完。見第 6c 節）。
- 2026-10-27（v5.0：**觀念補充併入核心觀念**，先在 L4 做。詞條改成正文裡的收合註 `details.gloss`（名詞／前情／背景），正文裡的名詞用 `a.tm` 連過去，點名詞就展開；核心觀念的章編號 2.1、2.2…，分成 A／B／C 三組，段首放一張閱讀地圖 `nav.map`；章內的粗體小標加 `id="iN-k"`，目錄多一層；一章超過約 4,000 字就拆（L4 的 Edit 與 execution 拆成 2.3、2.4，共 7 章，上限放寬到 8）。頁面因此只剩 5 段：1 架構、2 核心觀念、3 問題討論、4 動手試試、5 延伸閱讀；同日套用到 L3（7 章）、L5（5 章）、L2（4 章，深入區塊保留，meta 寫「深入與註」）、L6（5 章）；L1、L7、L8 仍是 6 段，等 James 確認後再逐頁改。見第 3、4 節）。
- 2026-10-27（v4.5：「大家的討論」併入第 4 段問題討論的末尾（`div.submit#s-submit`）；延伸閱讀編為第 6 段。全站段落：1 架構、2 核心觀念、3 觀念補充、4 問題討論、5 動手試試、6 延伸閱讀）。
- 2026-10-26（v4.4：全站取消「延伸思考」段，L1–L8 都改完；段落固定為 1 架構、2 核心觀念、3 觀念補充、4 問題討論、5 動手試試、6 大家的討論、延伸閱讀；10-27 再併掉大家的討論）。
- 2026-10-26（v4.3：取消獨立的「延伸思考」段，推論改放在對應章節末尾的「本文延伸」收合區塊，後面的段落編號往前移；slide 留給 assignment 的問題（哪幾招 prompt 過期）直接給本文的判斷；context window 的清單只畫一次、畫完整；見第 3、4 節）。
- 2026-10-26（v4.2：一章太長就拆章；平行的做法用「找法 1：」「改法 2：」編號小標；章首一句地圖；見第 4 節第 2 段）。
- 2026-10-26（v4.1：指令、設定檔、對話一律用 code snippet；每章至少一張圖或表；清單用 ul/ol；見第 4 節第 2 段與新的第 6b 節）。
- 2026-10-25（v4.0：文章要能不看 slides 從頭讀到尾，名詞在第一次出現的地方講清楚，深入區塊併回主線，觀念補充改成查閱詞條；見第 1、4 節。L3、L4 是第一批改寫的範例）。
- 2026-10-23（v3.8：核心觀念的 prose 裡可以放比較圖或表格，見第 4 節第 2 段）。
- 2026-10-22（v3.7：ASD-STE100 依段落分兩檔，推理段落放寬到約 60–70%，見第 5 節）。
- 2026-10-22（v3.6：取消閱讀時間的限制，見第 7 節）。
- 2026-10-22（v3.5：進階題每堂最多 3 題，見第 4 節第 5 段）。
- 2026-10-22（v3.4：觀念補充的條數與閱讀時間上限改為建議，見第 4、7 節）。
- 2026-10-21（v3.3：文章要讓沒看 slides 的人也讀得懂，見第 1 節；閱讀時間上限 16 → 30 分鐘，見第 7 節）。
- 2026-10-19（v3.2：站台搬到 `docs/`；討論改用 GitHub Issues，連結由 `tools/discuss.py` 寫入）。對照的是 L1–L8 的實際格式。第 4 段的基礎題另見 `STYLE_BASIC.md`。

## STYLE_BASIC.md

- 2026-11-07（語言一節：句數、字數是提醒，不是上限，見 STYLE_ARTICLE 第 5 節開頭。）
- 2026-11-03（v4.0：v7 依想法重組的頁面，基礎題跟著文章走，見下方「v7 頁面」；L5 先行，James：「L5 的基礎題可以換掉，因為還沒開始上」）。
- 2026-10-28（段號：基礎題在第 3 段、動手試試是第 4 段，L1–L8 全站如此）。
- 2026-10-19（v3.1：站台搬到 `docs/`；留言改在 GitHub Issues）。對照的是 L1–L8 的實際格式（每堂 5 題，參考答案是重點複習）。

## STYLE_DIGEST.md

- 2026-11-07（開頭加一句：句數是提醒，不是上限，見 STYLE_ARTICLE 第 5 節開頭。）
- 2026-11-06（v1.3：L9 起的新講次，「跟這堂課的關係」連到本頁的章〈`#iN`〉，不寫 slides 頁碼；`insert_digest.py` 在這種頁面把 rg-intro 那一句寫成「它和本文哪幾章有關」）
- 2026-10-21（v1.2：「推薦」也附摘要；新增 `tools/insert_digest.py`）。對照的是 L1–L8 的 42 段摘要。

## REVIEW_READABILITY.md

- 2026-11-13（**R17 業界已有名字**，checklist v17。起因：L6b 第 4 章「五個訊號」審過兩輪，兩次都只替自創的詞補定義。R17 是鐵律「你知道不算」的例外。測試題 `l06b-i4-rag-renamed`。reviewer-prompt 同步；`review_eval.py` 還沒跑。）
- 2026-11-11（**作者自己判斷要不要修，報告進 repo**。James：「這兩個決定你做就好，我也不知道有哪些要修」。每個 BLOCK 判 fix／strict／needs-source，寫進 `guide/review_reports/lXX-YYYYMMDD/TRIAGE.md`，各輪報告一起 commit；strict 的比例當誤報率記在 `review_cases/RESULTS.md`。第一次：L6b 整頁 70 個 BLOCK，fix 66、strict 2、needs-source 2；第二輪 76 個單位又標 21 個。L6b 遺忘表定為「記錯的先標記失效」，題庫同步。）
- 2026-11-11（**審查者的測試題與 checklist 版本**。起因：L6b 第 2 章「歸納是風險最高的寫入……Reflection 讀好幾筆觀察」一段，James 請 Claude 評可讀性並問怎麼減少 feedback 次數；這一章 11-10 用 v14 審過兩輪，這段仍留著；11-11 用同一份舊 prompt 重審，審查者其實標得到它。第一次量測：5 個沒寫進 prompt 的事件抓到 5 個，但審查者把 14%–71% 的單位標成 BLOCK，誤報率還沒量（`guide/review_cases/RESULTS.md`）。加 R15 別名（同一個東西兩個名字，讀者分不出是一個還是兩個）、R16 例子對得上主張（鐵律多一種「只靠主張、例子對不上」）；Checklist 版本 16。新增 `guide/review_cases/`（8 個事件）與 `tools/review_eval.py`（量 recall），`guide/review_log.tsv` 與 `tools/review_status.py`（哪些章用哪一版審過，11-11 以前照 commit 訊息回填）；`verify.sh` 多一行提示。事件先當測試題、不先貼進 prompt 當例子。）
- 2026-11-09（`tools/review_pack.py`：本文延伸、深入區塊標題後面的 `<span>` 標籤（「不是 slide 的內容」「查證」）另外印成「〔頁面上的標籤：…〕」。L6 `#x5` 兩輪審查都把「漏抓與誤判不是 slide 的內容」讀成一句話，是包的誤報。）
- 2026-11-07（新增〈審查者的雜訊〉：L6 第 2–4 章沒改、審三次，BLOCK 13／17／15，11 個單位三次都標；判斷方向看多數決的單位，不看總數。新工具 `tools/review_noise.py`。skill 的成本估計同步。）
- 2026-11-07（**校準：審查者不能看後文**。L1 tldr「聊天是 1 次、750 token、105 token」第二輪放行：審查者拿整頁 pack，先讀過第 1 章的長條圖，又能照位置把三個數字對回前一組，所以重述得出來。原則 2 改成前文全給、後文不給（`review_pack.py --prefix`），tldr 單獨一個審查者；原則 6 加三種入口的讀者；鐵律改成「你知道不算，後面寫的不算」，每個單位寫「靠：」；加 R12 數字（BLOCK）、R13 後文（BLOCK）、R14 章首（NIT）（R11 已由同日另一個 session 的「來回對照」用掉，R12 管一個單位自己的數字，R11 管跨列、圖文之間的對照）；作者的修法加數字與後文兩條；`reviewer-prompt.md` 同步，這句收成例子一。審查包一律帶頁首（eyebrow、h1）當上下文。James 2026-11-07 同意：「審 tldr 時當作沒讀過後面」太窄，同樣的漏洞每一章都有。）
- 2026-11-07（L1–L8 第一次整批跑：一堂 1–3 個審查者，每個都拿整頁 pack。第二輪剩的 BLOCK 多是 R9（推理少一步）和數字的讀法（百分點還是相對值、比例算反）；後者要回原文確認，原文本身沒寫清楚時，頁面寫明「原文沒說」。這次 WebFetch 直接開網址要等核准、沒人回，改用 WebSearch，結果裡就讀得到原文的句子（Cursor、Prompt Infection、ABC 附錄 E.2）。）
- 2026-11-07（加 R11 來回對照，NIT：讀者要在幾列數字、或圖和段落之間來回對照才看得出結論。審查者只說症狀，形式由作者決定。起因：L6 3.1 第二輪審查說「要和圖3 的數字來回對照」，這類問題原本沒有條目）
- 2026-11-06（第一次用在新講次：L9–L11，10 個審查者，第一輪 33／71／21 BLOCK，第二輪剩 2／12／5，主線修完、沒有第三輪。「作者怎麼用報告」加兩條：第二輪的定位附第一輪的「我讀到的」（作者加段落後定位會移動）；新頁接到全站後就地改 HTML、不從片段重組。skill 第 4 步同步。十個審查者加三個作者修改碰到一次 5 小時的用量上限，大堂分給審查者時留意）。

## QUIZ.md
- 2026-11-12（L6b 刪掉兩段 Pokémon 例子之後，刪觀念 k44.5、k44.6、k46.2 與題目 k44d、k44e、k46a；170 題 unit。新加的兩段推論還沒有題。）
- 2026-11-12（L6b 重排章節：31 節、173 題的 id 不變，節的 `from`、整合題的 `after`、`scope`（6 章 → 7 章）、points 的 `at` 跟著新位置改；k33 與 20 幾題裡的章號改寫。新寫的 `#i1-3` 沒有題，併在 k45 這一節裡。）
- 2026-11-11（**讀者自測優先**：James 讀 L6 發現有些題問論文的數字，定了優先順序：讀者自測比 regression test 重要，數字背後的含義才是重點。加〈讀者自測優先〉：判準是遷移；帶數字的題分三種；量測類觀念寫成「發現 → 所以」；觀念清單加 `evidence` 類，不出題。加〈數字對照〉：新的 `tools/check_numbers.py` 拿頁面引用來源的數字對 `guide/sources/lXX.md`，接進 `verify.sh`，L6、L6b 標 strict。`quiz.py check` 放行 `evidence`、擋只測 `evidence` 的題、選項只有數字給 warn。L6 題庫照改：106 題變 102 題。L6b 來源檔補三個漏記的數字（重開原文核對過）。build-quiz 的 points-prompt、writer-brief 同步。）
- 2026-11-10（L6b 補五個小節的題：新節 k44–k48、20 題；用「只改了某一節」的維護流程，觀念由主線列。〈各堂題庫〉加一列。）

- 2026-11-10（L6 拆成 L6／L6b：〈各堂題庫〉加兩列；資料一節加 `moved_from`；整合題一條改寫成拆堂後的放法。）
- 2026-11-10（目錄打勾的標記改成固定寬度的一欄（4.4rem、置中），✓ 和「9/19 題」上下對齊；全站 `app.js` 加版本號 `?v=20261110d`，James 看到的「黏在標題後面」是瀏覽器還拿著舊的 app.js。`quiz.py init` 改成認得帶版本號的 app.js 標籤。）
- 2026-11-10（目錄打勾再往右：有標記的列右邊距從 .55rem 改 .15rem，標記貼齊目錄右緣（和反白底色的右緣差 3px）；CSS 版本 20261110c。）
- 2026-11-10（目錄打勾改版：James 說標記跟在文字後面太散，只寫「9/19」會被當成日期。改成整列兩欄、標記靠右對齊成一欄，進度寫「9/19 題」放外框小標，做完是綠色 ✓；CSS 版本 20261110b。）
- 2026-11-10（左邊目錄依小測進度打勾：James 要快速看出還沒讀的範圍。一節的題都做了打 ✓、做一部分顯示「做了／總題數」、章那一列加總；`app.js` 讀 localStorage 產生，答題時即時更新；`styles.css` 加 `.sn-qk`，全站 CSS 版本改 20261110。〈資料放在哪裡〉加一條。）
- 2026-11-09（**L5 題庫**，照 `build-quiz` skill 做的第一堂：21 節（重點 9 節：k1、k2、k3、k7、k8、k11、k12、k14、k19；第 9 章目錄留 k20、k21 兩節）、196 個觀念（主張 59、機制 71、前提 19、限制 35、誤解 12）、119 題 unit（86 選擇、33 應用）、7 題整合（第 4 章後 3 題、第 8 章後 4 題）。開卷第一次 unit 121／121、整合 6／7（x6 定位缺 k1，改成明問第 1 章的表），改完全過；作答者指出的題目毛病照改（k10a 含不含最上層、k11f 算哪一次的 token、k14e 要點要求文章沒寫的重讀結果、x2 PlanCraft 文章沒說算讀還是寫、x7 PR 描述算不算 diff）。閉卷 88 題選擇答對 85、有把握 60，分類後線索類改兩輪：第一輪 24 題（14 題選項線索、10 題同節洩漏；k13a／k13b、k14c／k14d 各併成一題），第二輪 7 題；兩輪後仍有把握的 4 題（k2k、k11a、k11c、k15b）作答者的理由都是領域常識，標 `closed_ok`，共 44 題。〈各堂題庫〉表加一列。）
- 2026-11-10（**L7 題庫**，第一次照 `build-quiz` 跑：53 節（第 10 章目錄併成一節）、350 個觀念（主張 65、機制 80、前提 57、限制 100、誤解 48）、265 題 unit（選擇 193、應用 72）、7 題整合。列觀念第一版 554 條、邊界類 24–30%，退回同一個 agent 修成 350 條、57–60%。五個出題 agent 寫出 8 條文章本身的問題，正文已改。開卷第一次 unit 265/266、整合 3/7（`ks` 列太寬），改完全過。閉卷 197 題答對 193、有把握 156：114 題 closed_ok，42 題改（option 21、同節 leak 17、compute 4，併掉 1 題）；第二輪 41 題有把握 18，17 題 closed_ok、1 題再改；第三輪 0。`build-quiz` 補上這些教訓：列觀念太細就退回同一個 agent、`_notes` 的文章問題怎麼處理、整合題 `ks` 只列用到的節、重跑時評分也要列題號、開卷閉卷可同時跑、中斷時先看結果檔。〈各堂題庫〉表加 L7 一列。）
- 2026-11-09（加 `build-quiz` skill：James 要替 L6 以外的講次出題。把 L6 的做法照實際順序寫成步驟：init 切節 → 沒看過題目的 agent 列觀念 → 分批出題 → check → 開卷作答與評分 → 閉卷作答與分類 → 改線索 → verify、push；附列觀念、出題、閉卷分類三份 prompt。`quiz.py` 加 `init`（從 `p#iN-M` 產生節的骨架，只有一句的章首自動併掉）、`spec`（依節分組的讀者文字，不含 tldr）、`merge`（把 subagent 的 points／unit／integration 併進頁面）；`exam`、`closed`、`grade` 可用節號或章號挑題。開頭加一行指向 skill，加〈各堂題庫〉表。）
- 2026-11-09（**觀念涵蓋**：James 指出題目像只測 happy case。每一節加 `points`（主張、機制、前提、限制、誤解），每題加 `covers`，`check` 擋沒有題目測到的觀念、`coverage` 列對照。L6 從 133／317 補到 320／320（限制原本只測到 27%），題庫 100 → 258 題 unit；清單由沒看過題目的 agent 寫，再拿另一個 session 獨立列的清單對照補 3 條。新題開卷選擇 202／203、問答 26／29 第一次就過，沒過的是題目毛病。閉卷改成只抓線索：新題閉卷答對 202／203，大多是領域常識，分類後線索類改兩輪、刪 8 題合併，120 題標 `closed_ok`。Mutation：刪掉三句前提或限制，舊題庫 6 題全綠，新題庫 1 題轉紅、2 題由作答者指出文章沒寫。作答者抓到第 5 章光譜圖說沒對上灰色和 write everything，已補。作答包、閉卷包的選項改成依題號打亂。）
- 2026-11-08（第 2 章選擇題照新規則重寫：選項等長、錯的選項是說得通的誤解、計算移到應用題（加 k4e），閉卷有把握答對從 8/8 降到 4/9，剩下的標 `closed_ok`。重點觀念改成至少 4 題、2 選擇、1 應用。`quiz.py check` 對「正確選項明顯最長」給 warn。）
- 2026-11-08（加閉卷測試：`quiz.py closed`／`closedcheck`。L6 87 題選擇題閉卷答對 85、有把握 80；67 題正確選項最長。寫出四種原因與避開的寫法。k6a 改成三個邏輯上都說得通的順序，閉卷作答者答不出把握。James 問 k6a 光看題目能不能答、可讀性審查能不能解。）
- 2026-11-08（擴到 L6 整堂：第 5–10 章 26 節、52 題選擇、6 題應用、4 題整合；重點觀念 5-1、6-1、7-1、8-4、9-2。整合題加 `after` 欄位，可以放在不同章之後；第 10 章是目錄，只出兩題選擇。James 要 L6 全部加題目。）
- 2026-11-08（選項預設 3 個，4 個要有 3 種真的誤解；刪掉 k1a、k4a 湊數的「約 50%」。重點觀念標 `core`，至少 3 題選擇＋1 題應用、從不同角度問：L6 加 k1c、k1d、k8c、k8d、k14d。`quiz.py check` 擋這兩條。James 問選項幾個合適、重要觀念能不能重複出題。）
- 2026-11-08（回想題改成選擇題：James 要自己能快速知道答對沒有。L6 第 1–4 章 18 題回想拆成 30 題選擇題，點了立刻判對錯、選錯說錯在哪；應用題、整合題維持問答。`quiz.py` 用程式判選擇題，作答包加「文章沒寫」選項。）
- 2026-11-08（新增。James 2026-11-07 提：內容拆成有連貫性的 knowledge section，學完一節做 unit 題、最後做整合題，同一批題當 CI 第 2 層的 regression test。節＝文章自己的小節；題庫放在頁面的 `<script id="quiz">`；L6 第 1–4 章 pilot：16 節、22 題 unit、3 題整合。基準全過，mutation 刪 K4 算式後 3 題轉紅；從 k1b、k14b、k4a 學到三條出題規則。）

## DAG.md
- 2026-11-12（L6b 重排後只改五個節點的 `src` 與 excluded 的 `l06b#i7`；四層（log 在下、view 在上）還沒有自己的節點。）

- 2026-11-10（講次 key 可以帶字母：L6 拆成 `l06`（Agent reliability）與 `l06b`（Agent memory），`src` 與 `excluded` 跟著改；`dag.py` 的講次標籤與排序改用字串。）
- 2026-11-09（第二版：節點改以心智模型為單位，加 `kind`（concept／practice）、concept 不能依賴 practice 的檢查；根收成 next-token 函數；產品名的節點改成一般觀念、案例降成例子；93 個節點 152 條邊。首頁課程地圖加連結。）
- 2026-11-08（頁面改成英文版：James 說中文主題名「放大與人」讀不出語意。`dag.json` 全部欄位改英文，`dag.py` 的字寬估算改成英文字、方塊 134×52、短名放不進兩行就 ERROR。）
- 2026-11-08（新增：節點、邊、難度的規則，版面與頁面下半的定義，第一版的判斷。）
