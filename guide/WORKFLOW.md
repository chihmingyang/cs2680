# 工作流程

更新紀錄在 `guide/CHANGELOG.md`。

適用於綁在 CS2680 Project 的 session（有 shell、`gh`、WebFetch 工具）。

工作目錄是 `/home/claude/cs2680`，就是 repo 本身：

| 路徑 | 內容 |
|---|---|
| `docs/` | 站台。GitHub Pages 從 `main` 的 `/docs` 發布到 https://chihmingyang.github.io/cs2680/ |
| `tools/` | 檢查與組裝腳本，用法寫在每個檔案開頭 |
| `guide/` | 這份流程與撰寫規範 |
| `slides/` | 每堂 slides 的逐頁筆記 `lXX-notes.md` |
| `notes/`、`shots/` | 暫存（`.gitignore` 排除，不 commit） |

這個環境的限制（2026-10-19 實測）：

- `gh` 的 REST API 可以用：開 issue、加 label、讀留言。
- GitHub GraphQL 不能用，所以不用 Discussions。
- 不能改 repo 設定（Pages、Discussions 開關）。要改時，請 James 在自己的電腦執行指令。

---

## A. 開工（每個 session 都做）

1. 把 repo 加進 session，再 clone：
   - 呼叫 `add_repo`（owner `chihmingyang`、repo `cs2680`、access `push`）。
   - `git clone --depth 1 https://github.com/chihmingyang/cs2680 /home/claude/cs2680`（timeout 給 10 分鐘）。
   - clone 完呼叫 `register_repo_root`（owner `chihmingyang`、repo `cs2680`、directory `/home/claude/cs2680`）。2026-11-06 起 claude.ai 的 session 也有這個工具（10-30 時還沒有），實測下一步就生效：`CLAUDE.md` 以 system-reminder 自動載入，`.claude/skills/` 的 skill 進到 skill 清單，用 Skill 工具載入，不必自己 Read。呼叫失敗才改成自己 Read `CLAUDE.md` 和 `.claude/skills/<name>/SKILL.md`。
2. 確認 `gh` 可以用：
   ```bash
   gh api user --jq .login        # 應該印出 chihmingyang
   ```
3. 建暫存目錄：
   ```bash
   mkdir -p /home/claude/cs2680/{notes,shots}
   ```
4. 要寫內容時，讀 `guide/STYLE_ARTICLE.md` 和 `guide/STYLE_BASIC.md`；改延伸閱讀的摘要時再讀 `guide/STYLE_DIGEST.md`。

---

## B. 新增一堂（例：L9）

### B1. 確認素材

1. 用 WebFetch 打開 `https://cs2680.com`，找到這一講的 slides PDF 檔名和 readings 頁（格式像 `https://cs2680.com/readings/oct-19.html`）。shell 連不到 cs2680.com，只能用 WebFetch。
2. Slides 還沒公開，就停下來告訴 James。
3. 講次編號依站台順序往下排。只有公開 slides 的講次才編號（10/05 客座、10/14 學生主講沒有 slides，就不佔編號）。編號有疑問就問 James。

### B2. 整理 slide 筆記

用 WebFetch 讀 PDF，prompt 用這段：

```
This is a lecture slide deck (PDF). Write page-by-page study notes so a student can follow the deck without opening it. For EVERY page in order, write "=== Page N ===" (N = PDF page number, cover = 1) then a concise but complete paraphrase of that slide: its title, every point it makes, and ALL specifics — numbers, percentages, dates, benchmark/system/paper/product names, commands, file names, table rows (as compact rows), chart axes and values, and the example used. For each figure write one line "[Figure: ...]" describing what it shows. Do not skip pages, including optional/appendix pages. If a page has no extractable text, write "=== Page N === (no extractable text)". End with "TOTAL PAGES: X".
```

- 回傳太短或漏頁，就用較窄的 prompt 補（只問某幾頁，或問某張圖的數字）。
- 存成 `slides/l09-notes.md`，跟頁面一起 commit。之後修改這堂的 session 從這裡取事實，不必重抓 PDF。

### B3. 寫頁面

1. 先建骨架（2026-11-06 起）：
   ```bash
   python3 -I tools/new_lecture.py l09 --date 2026-10-19 --part "Part II" \
       --title "中文標題" --en "英文原標題" --pdf 9_llm_serving_basics_1.pdf --pages 51
   # 一堂有兩份 deck（L10）：--pdf、--pages 各給兩次；data-pdf 是第一份，data-pages-total 是總和
   cp docs/l09.html notes/l09/base.html
   ```
   骨架從 `docs/l05.html`（v7 範本）複製 head、topbar、側欄、延伸閱讀的 legend、pager。
2. 依 `STYLE_ARTICLE.md` 寫片段放 `notes/l09/`：`head.html`、`i1.html`…、`tldr.html`、`fineprint.html`，以及整段的 `try.html`、`wrap.html`。組回頁面：`python3 -I tools/assemble_v7.py docs/l09.html notes/l09 --base notes/l09/base.html`。
3. 頁面很長，分章寫。交給 subagent 時（好幾堂同時寫時一堂一個），每個 subagent 把 HTML 寫進檔案（片段放 `notes/lXX/`），只回報路徑和要主線確認的事，不要把 HTML 貼在回報裡：HTML 貼在回報裡，同一段就會生成兩次（subagent 一次、主線 Edit 一次），而生成是 session 裡最慢的部分。好幾堂同時寫時，簡報是 `.claude/skills/idea-first-lecture/new-lecture-brief.md`：共用同一個 checkout（新頁面不改既有檔案，所以不需要 worktree），每個 subagent 只寫自己的 `docs/lXX.html`、`notes/lXX/`、`guide/sources/lXX.md`；跨新講次的連結先只連頁面，主線整合時補錨點（2026-11-06 L9–L11 這樣做）。

### B4. 驗證這一頁

```bash
cd /home/claude/cs2680
python3 -I tools/punct.py docs/l09.html --diff   # 看過再不帶 --diff 跑
python3 -I tools/punct.py docs/l09.html
python3 -I tools/add_anchors.py docs/l09.html
python3 -I tools/check_article.py docs/l09.html --pages N --pdf FILE.pdf --fix-time
python3 -I tools/shot_article.py docs/l09.html
```

- `check_article.py` 要印出 `OK`。`LONG` 句子拆短；`被` 改成主動。`warn` 可以不改，但要看一次。`… items joined by ；, use ul/ol` 這種 warn 要改：拆成清單，或確認是推理／算式後在 `<p>` 加 `data-inline`（STYLE_ARTICLE 第 4 節「並列項目一項一行」）。
- v5.0 版面（有 `nav.map`）的頁面，閱讀地圖裡每章的分鐘數這樣算（和 `check_article.py` 同一條公式；`notes/` 是暫存）：
  ```bash
  python3 -I - <<'EOF'
  import re, sys; sys.path.insert(0, 'tools'); import check_article as ca
  s = open('docs/l04.html', encoding='utf-8').read()
  seg = s[s.index('id="s-ideas"'):s.index('id="s-try"')]
  ids = re.findall(r'<div class="idea" id="(i\d)">', seg)
  pos = [seg.index(f'<div class="idea" id="{i}">') for i in ids] + [len(seg)]
  for k, i in enumerate(ids):
      v = ca.Vis(); v.feed('<main>' + seg[pos[k]:pos[k + 1]] + '</main>')
      print(i, -(-v.b['read-time'] // 400), '分')   # 填進 span.map-m
  EOF
  ```
- 用 Read 看每一張截圖一次：文字重疊、超出框、箭頭沒接好、手機版跑版。發現問題修一次。**一則訊息平行呼叫 6 次 Read**（6 張一起看），不要一張一則：每一則訊息都要重讀整個 context，L3 的 63 張截圖一張一則是 63 次，6 張一則是 11 次。
- 頁面寫好之後，每一輪檢查用 `bash tools/verify.sh l09` 一次跑完（check_article、check_diagrams、audit、add_lecture --check、punct 提示、figure-spots 提示），全部通過只印 `ALL OK`。figure-spots 列出可能該畫成圖的數字表和段落，以及表和圖畫同一組數字的地方；逐條看一次，照 `STYLE_ARTICLE.md` 第 6 節〈數字表換成圖〉決定，決定留著的加 `data-no-figure`（2026-11-07）。上面的指令還是要先跑一次，因為 `add_anchors.py`、`punct.py`（寫回）、`--fix-time`、`shot_article.py` 會改檔或產生截圖，`verify.sh` 不做這些。

### B5. 接到全站

```bash
python3 -I tools/add_lecture.py docs/l09.html --sum "一句話摘要，用分號分隔三個重點。"
```

`add_lecture.py` 會改：每一頁的目錄、`LX / N`、上一堂的下一堂連結、首頁「已公開的講次」、首頁「還沒有 slides 的講次」（刪掉同日期的那一列）。v7 頁面的展開目錄直接建成 v7 格式（2026-11-06），不必再跑 `assemble_v7.py`。好幾堂一起接時依講次順序跑，每堂一次。

手動補兩件事：

1. 首頁「課程地圖」：把這堂的主題加成 chip，連到 `l09.html#i1` 這類錨點（`add_anchors.py` 印出的清單）。放在對應的層（Serving System、Model、Runtime / Kernels 等），並移除那一層「待公開」裡對應的日期。
2. 有需要時更新首頁 hero 或「怎麼讀」的文字。

然後跑全站檢查：

```bash
python3 -I tools/punct.py docs/index.html --diff
python3 -I tools/audit.py                          # 要印出 NO PROBLEMS
python3 -I tools/add_lecture.py --check            # 要印出 nothing (in sync)
```

### B6. 發布

見 D。

---

## C. 修改既有頁面

1. 做 A。
2. 修改 `docs/` 裡的檔案。規則以 `guide/STYLE_*.md` 為準；要改規則，先問 James。
3. `punct.py` 只對新寫的片段跑，先 `--diff` 看它會改什麼。不要對整頁盲跑：頁面的數學式與英文片語要維持 ASCII（2026-10-19 這樣做過一次，改壞了 L4–L8 的算式，後來還原）。
4. 對改過的講次頁跑 `bash tools/verify.sh lXX`（B4 的檢查加 `audit.py`，一次跑完）。
5. 發布（D）。

大改一堂的核心觀念（2026-10-29 L5、L6 的做法）：每章寫成一個片段 `notes/lXX/iN.html`（開一組的那章把 `p.idea-group` 放在最前面），`head.html` 放 `section#s-ideas` 的開頭到 `<div class="ideas">`（`nav.map` 的分鐘數寫 `__iN__`），要改 tldr 或架構的讀圖重點就再放 `tldr.html`、`arch.html`，然後：

```bash
python3 -I tools/assemble_ideas.py docs/l05.html notes/l05   # 換掉 #s-ideas、填分鐘數、重建本頁目錄
```

接著手動改延伸閱讀摘要、首頁 chip 與別頁連進來的 `#iN`（`grep -o 'l05.html#[a-z0-9-]*' docs/*.html`），再跑 B4 的檢查。片段留在 `notes/`（不 commit），改完就可以刪。

延伸閱讀的摘要（`details.rg-dg`，必讀與推薦都有）怎麼寫、怎麼插入，見 `guide/STYLE_DIGEST.md`。

---

## D. 發布

```bash
cd /home/claude/cs2680
git fetch origin main && git rebase origin/main   # 別的 session 可能先 push 過
git add -A
git status --short                                 # 確認 notes/、shots/ 沒有混進來
git commit -m "L9：新增 Efficient LLM serving basics I"
git push origin main
```

- commit 訊息用中文，一行說改了什麼。
- **改了正文就先過 I 的可讀性審查**（2026-11-06 起）：BLOCK 清零才 push。
- push 後 GitHub Pages 約 1–2 分鐘更新。用 WebFetch 打開 `https://chihmingyang.github.io/cs2680/l09.html` 抽查一次。
- 直接 push 到 `main`，不開 PR（只有 James 一個維護者）。
- push 後 CI（J）自動對全站跑 `verify.sh all`，約 2 分鐘：`gh run list -R chihmingyang/cs2680 -w verify.yml -L 1`。紅的就修，不要等 James 收到信。

---

## E. 收尾

1. 這次定下的新規則，寫回 `guide/` 裡對應的文件，跟頁面一起 commit。更新紀錄寫進 `guide/CHANGELOG.md` 對應那一節的最上面，一則一行；不要再寫在各文件的第 3 行（2026-11-06 起）。
2. 腳本有改，也一起 commit。
3. 回覆 James：只列改了什麼、哪裡要他確認。不要寫長報告；他的閱讀時間有限。

---

## F. 讀成員的討論（2026-11-09 停用）

頁面的「問題討論」段和各堂的 GitHub 討論串已拿掉、關閉，`discuss.py` 已刪（舊版在 git 歷史）。留言還在關閉的 issue 裡（label `L01`…`L11`）。label `ask` 的 issue 是「問 Claude」，見 G，照常運作。

---

## G. 線上編輯與「問 Claude」（維護者工具）

James 在站台上直接改字、問問題。一般成員看不到：`app.js` 只在這個瀏覽器開過 `?edit` 之後才載入 `docs/edit.js`、`docs/edit.css`（`?edit=off` 取消）。頁面上多兩個鈕：鉛筆（編輯）、對話框（問 Claude）。

**編輯（`docs/edit.js`）**

- 點一段就能改。可改：`p`、`li`（不含子清單）、標題、表格儲存格、`figcaption`。不能改：`pre` 的 code、SVG 圖、`summary`、目錄。這些請 Claude 改。
- 工具列：`b` 粗體、`strong` 紅字、`em`、`u`、行內 `code`、`mark`、文字顏色（`span style="color: var(--…)"`，用 theme token，深色模式才正常）、連結、清除格式。Enter 在 `p`、`li` 分段；清空一段再存就刪掉那一段。
- 滑鼠移到區塊上，右上角出現操作：刪除（段落、清單項目、整個清單、表格的一列、整張表、圖、code、收合區塊、標題）、＋段落、＋圖。刪除要到存檔才生效，存檔前可按「復原」。區塊裡的錨點有別處連過來時會先問；刪掉後目錄不會自動更新，下次碰到那一頁要跑 `add_anchors.py`、`audit.py`。
- 貼圖：⌘V 或工具列「貼圖」，放在目前這一段後面，markup 是 `figure.pasted`（`styles.css`）。圖檔存檔時才上傳到 `docs/img/<頁>-<時間>-<n>.<副檔名>`，先於頁面 commit。
- 按「儲存」先出現 commit message 欄，已帶好摘要（「L3 改 2 段、刪 1 處」），可改；送出時自動加上前綴「網頁編輯：」，所以 `git log` 認得出來。
- 往上捲時右下角立刻出現浮動鉛筆（`.ed-fab`），不等捲過多少距離。頂端的鉛筆一直都在。
- 存檔不序列化整頁：用 GitHub Contents API 抓最新原始碼，用「tag＋原本的內容＋相同內容裡的第幾個」找到那一段，只換那幾個位元組，再 PUT 一個 commit。圖、表、code 這類區塊用文字找（`code.js` 會在執行時改寫 code，但字元不變）。那一段在 GitHub 上已被改過就標紅、不覆蓋。
- 網頁編輯直接進 `main`，存檔時**不跑 `check_article.py`**；push 後 J 的 CI 會對全站跑一次，沒過 James 會收到信。所以每個 session 開工前先 `git pull`（D 的 rebase 已涵蓋）；James 手改的文字是他的決定，不要順手改回來。紅字數量超過規則只是 warn，下次碰到那一頁再看。

**問 Claude（`.github/workflows/ask.yml`、`tools/ask_prompt.py`）**

- 選一段文字 → 按「問 Claude」→ 頁面開一個 label 為 `ask` 的公開 issue。Workflow 用 James 訂閱的 token 跑 `claude -p`，把回答留言回去並關閉 issue；面板每 8 秒讀一次留言。接著問就是在同一串留言，關閉的 issue 也會再觸發。
- 「問」只給唯讀工具。「請 Claude 改站台」多給 `Edit`、`Write`、`git`、`node --check`、`python3 -I tools/*`。內容問題照 `rewrite-with-example` 改；功能、版面、工具、規範也可以改（用途是 James 邊讀邊改進站台），跑檢查後 push。`.github/workflows/` 改不了，要改時只回覆改法。
- 只有 `chihmingyang` 觸發得到；`ask_prompt.py` 也只把他和 workflow 的留言放進 prompt，別人的留言到不了 Claude。

**設定（各做一次）**

1. 瀏覽器：開 `https://chihmingyang.github.io/cs2680/l03.html?edit`，按對話框鈕，照面板的步驟建 fine-grained token（只選 cs2680；Contents、Issues 都是 write），貼進去。Token 只存在這個瀏覽器的 localStorage，有效期 1 年。
2. 自己的電腦（「問 Claude」才需要）：
   ```bash
   claude setup-token                                              # 印出訂閱用的長效 token
   gh secret set CLAUDE_CODE_OAUTH_TOKEN -R chihmingyang/cs2680    # 貼上剛才的 token
   ```

**改 `edit.js` 之後**：`python3 -I tools/test_editor.py`（用假的 GitHub API 在瀏覽器跑；全站每一段都要找得到原始碼位置，存檔的 diff 只能動到改過的段落）。

---

## H. 把一堂改成 v7：依想法重組（2026-11-03 起）

照 `.claude/skills/idea-first-lecture/SKILL.md` 做，範本是 `docs/l05.html`，規則在 `STYLE_ARTICLE.md` 第 0 節。一個 session 改一堂，或一堂一個 subagent。每章寫成片段放 `notes/lXX/`（不 commit），用 `tools/assemble_v7.py` 組回頁面，`tools/dg.py` 畫圖，`tools/page_text.py` 讀舊頁面的文字。

2026-11-03 L1–L4、L6–L8 是七個 subagent 同時改的：每堂一個 git worktree（`notes/wt/lXX`），簡報在 `.claude/skills/idea-first-lecture/subagent-brief.md`。連到別堂一律用舊錨點，每堂交一份 `anchor-map.json`。一堂做完就落地：拿它的頁面，把已落地各堂的 map 套到這一頁，再把這一堂的 map 套到其他頁（`tools/anchor_map.py apply`，一個檔案只套一次），跑全站檢查，push。每堂的取捨寫進 `guide/V7_DECISIONS.md`，外部來源寫進 `guide/sources/`。

---

## I. 可讀性審查：另一個 agent 讀一遍（2026-11-06 起）

改了 `docs/lXX.html` 的正文（新寫、v7、rewrite-with-example、fact-check-extension）之後、D 發布之前做。規則與 checklist 在 `REVIEW_READABILITY.md`，操作在 `.claude/skills/readability-review/SKILL.md`。

起因：L6 第 2 章一格「Anthropic（2026-03）：穩定偏正面。單一公司的經驗」James 看不懂，七個腳本都過。腳本檢查結構和版面，沒有一步是「一個沒寫過這頁的人讀一遍」。

做法照 code review：

1. `python3 -I tools/review_pack.py docs/lXX.html --since origin/main --prefix > notes/review/lXX-pack.md`：只審文字有變的章，讀者視角的純文字，表格格子帶欄名與列名；前面的章標「上下文」，後面的章不給（2026-11-07）。改到 tldr 時，tldr 另開一個審查者，只給 `--chapter tldr`。
2. 開一個**全新的** subagent 當審查者（general-purpose，不是 fork），只給它 `reviewer-prompt.md` 和這個 pack。它對每個單位寫「我讀到的」和「靠：」，照 R1–R14 標 BLOCK／NIT，最後列「最難讀的三處」。
3. 作者修 BLOCK（照 `rewrite-with-example`），跑 `check_article.py`（表格格子現在有 R5、R6 的 lint）。
4. 第二輪只審被標過的單位。最多兩輪；還有 BLOCK 就留給 James。
5. push。回覆 James 貼 BLOCK 清單和修法，不貼全文。

`notes/review/` 不 commit。James 說「看不懂」而審查沒抓到，先改 checklist 或 `reviewer-prompt.md`，見 `REVIEW_READABILITY.md` 末段。

---

## J. CI：push 後自動檢查（2026-11-07 起）

James 問：每次改一章，能不能像 CI 的 regression test 一樣，確保每次修改都往好的方向。CI 證明不了「更好」，只證明測試寫到的地方沒有變壞，所以分三層，由便宜到貴：

| 層 | 對應 code CI | 檢查什麼 | 狀態 |
|---|---|---|---|
| 1 機械檢查 | build＋lint | `verify.sh all`：每一堂的 check_article、check_diagrams、check_numbers（引用來源的數字對照 `guide/sources/`，2026-11-11），全站的 audit、add_lecture --check | 2026-11-07 上線：`.github/workflows/verify.yml` |
| 2 理解測試 | regression test suite | 題庫：一個沒看過寫作過程的 agent 只拿頁面作答，每個答案附定位，定位落在該節、引用的文字真的寫了答案才算過 | 2026-11-08：L6 整堂（第 1–4 章 pilot 時，刪掉 K4 的算式後考算式的題轉紅），手動跑（`guide/QUIZ.md`） |
| 3 前後對照 | 和 baseline 比的 benchmark | 改過的章，舊版和新版並排重述，哪一版讀得懂 | 等第 2 層與雜訊數字 |

第 1 層：

- 觸發：push 到 `main` 且動到 `docs/`、`tools/`；「問 Claude」跑完（它用 `GITHUB_TOKEN` push，GitHub 不會因此觸發 `on: push`，所以改掛 `workflow_run`，main 沒動就跳過）；手動 `gh workflow run verify.yml -R chihmingyang/cs2680`。
- 只亮燈、不擋。push 已經進 `main`，Pages 照常部署；沒過時 commit 旁打 ✗，GitHub 寄信給觸發的人。不擋的原因：網頁編輯存檔後若檢查沒過、頁面不更新，James 會以為沒存到。
- 輸出在該次 run 的 summary。本機重現：`bash tools/verify.sh all`（約 30 秒）。
- 雜訊實驗（第 2、3 層能不能擋的前提，2026-11-07）：L6 第 2–4 章沒改，三個新審查者各審一次，BLOCK 13／17／15；21 個單位被標過，11 個三次都標。結論：不比總數，比多數決的單位集合。細節在 `REVIEW_READABILITY.md`〈審查者的雜訊〉，比對用 `tools/review_noise.py`。

---

## K. 一份 slides 拆成幾堂（2026-11-10 起）

規則在 `STYLE_ARTICLE.md` 第 0 節〈一堂不綁一份 slides〉。第一例是 L6 → L6〈Agent 可靠性〉＋ L6b〈Agent memory〉，build script 在 `notes/l06split/`（不 commit；做法記在這裡）。

1. **先用 DAG 決定切在哪裡。** `docs/dag.json` 裡這堂各章的節點，分成兩組之後，組和組之間沒有 deps 邊，就是乾淨的切法。目錄章、動手試試的每一項、延伸閱讀的每一篇、fineprint 的每個來源、題庫的每一節，都依觀念歸到其中一組。
2. **新頁的 key 是原編號加字母**（`l06b`）。`add_lecture.py`、`audit.py`、`verify.sh`、`dag.py`、`assemble_v7.py` 都接受 `lNN` 加一個小寫字母；`add_lecture.py` 會把新頁插在原堂之後：前一堂的下一堂、後一堂的上一堂、首頁列表的位置都跟著改。原堂在首頁的那一列（標題、英文、一句話、分鐘數）和前一堂 pager 裡的標題要手改。
3. **原頁保留留下來那一半的章號與錨點**，搬走的章在新頁從 1 重編：`id`／`href` 的 `iN`、`iN-M`、`span.idea-no`、正文與 SVG 裡的「第 N 章」、題庫的 `from`／`after`／`scope`／`at` 一起換。兩半之間的引用改成 L6〈章名〉＋連結。gloss（`n-context` 這類）兩頁都要用到的，各留一份或改連到主場那一堂。
4. **舊連結**：原頁放 `<script type="application/json" id="moved">{"to": "l06b.html", "ids": {"i6": "i2", …}}</script>`（放在 `app.js` 前）。`app.js` 在網址的錨點不在這一頁時，照表轉到新頁。`add_anchors.py` 不會把表裡的 `xN` 再編給新的本文延伸。原頁新的章號若和搬走的舊章號相同（L6 的 `#i5` 現在是目錄章），舊連結會停在原頁，這一點沒有轉址。
5. **題庫**：搬走的節、題保留原 id，新頁的 JSON 加 `"moved_from": "l06"`，`app.js` 會把讀者在舊頁的作答紀錄複製一份過來。只有拆開的那一節（L6 舊第 10 章）要分 points 和題目；新開的節用沒用過的 id（L6 的 `k43`），不要重用搬走的 id，否則舊頁的 localStorage 會被當成新題的答案。跨兩半的整合題改寫成只用本頁的節，另一堂的觀念寫在題幹裡當前提（L6b 的 x7）。
6. **別頁的連結和文字**：`grep -n 'l06.html' docs/*.html`，逐條判斷屬於哪一半；首頁課程地圖的 chip、`dag.json` 的 `src`、`excluded`、`lectures` 一起改，`python3 -I tools/dag.py` 重寫 `dag.html`。
7. 兩頁跑 `bash tools/verify.sh l06`、`l06b`，全站 `all`；新寫的 tldr、lede、目錄章開頭、兩半之間的過場句跑可讀性審查（I），只審新寫的定位；`app.js` 有改就把全站的 `?v=` 版本號加一號。
