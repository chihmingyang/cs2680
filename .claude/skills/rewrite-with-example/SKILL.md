---
name: rewrite-with-example
description: James 貼一段站台（docs/lXX.html）或任何說明文字說「看不懂」、「請修改」、「補案例」時用。先診斷為什麼難讀，改成 STE 短句，補一個真實的檔案內容或指令當案例，核對事實，改進 HTML，跑檢查，push。
---

# 看不懂的段落：改寫並補案例

James 很少用 Claude Code。只有概念、沒有檔案內容或指令的段落，他讀不懂。這個 skill 把「看不懂」變成一段可以照著做的文字。

## 流程

### 1. 找到原文和它的前後文

```bash
cd /home/claude/cs2680   # 沒有就先 clone（見 guide/WORKFLOW.md）
grep -n '<貼來的標題前幾個字>' docs/l0*.html
```

讀前後各 20 行。要看三件事：

- 上面是不是已經有一張圖或一段 code（例如 L3 的 gloss `#n-hook-files` 正上方就是 Superpowers 的 `hooks.json`）。有，就指過去，不要再貼一次。
- 原文有沒有說「第 N 段動手試試的範例」。有，案例就要和那個範例一致，或寫明「完整版在那裡」。
- 原文是正文、`details.gloss`、`details.deep` 還是動手試試。`gloss` 和動手試試不能放紅字 `<strong>`（STYLE_ARTICLE 6c）。

### 2. 診斷：寫出 2–3 個具體的原因

常見的三個：

| 症狀 | 怎麼改 |
|---|---|
| 第一句就用名詞，沒先說它是什麼 | 第一段先一句話定義：「X 是『…』。」 |
| 三個以上的平行項目擠在一句裡（位置、模式、選項） | 改成 `div.table-wrap > table`，一項一列 |
| 全文零案例，只有「可以寫在…」「差在…」 | 補一個 `figure.file`：真的檔名、真的內容，加一句「這會做什麼」 |

原因要寫在回覆裡，一行一個。他要知道為什麼改。

### 3. 先給純文字版，等他說 OK

照他的習慣：先純文字，不要先改 HTML。回覆長這樣：

```
原段看不懂的原因有三個：…
改寫如下：
---
（新標題）
（定義一句）
（表）
案例：你要…。在 <檔名> 寫：
（code block）
（其餘段落）
---
要我寫進 docs/lXX.html、跑檢查、push 嗎？
```

案例的規則：

- 用第一人稱情境開頭：「你要這個專案每次開對話，先印出 git 狀態。」
- 檔名寫完整路徑：`.claude/settings.json`，不寫「設定檔」。
- 內容要能直接貼進去用。能用一行指令就不要寫腳本（`git status --short` 比 `bootstrap.sh` 好懂）。
- 案例不在 slide 裡，就標「案例（本文補的）」。
- 標題改成講「放哪裡」「怎麼做」的具體句，不用「差在誰寫、何時生效」這種抽象句。

### 4. 核對事實

寫到第三方 repo（Superpowers、Caveman、mattpocock/skills…）的檔名、欄位、路徑，先查再寫：

```bash
gh api repos/obra/superpowers/contents/hooks/hooks.json --jq .content | base64 -d
```

`gh` 不行就 WebSearch。查到和原文不同，改原文並在回覆裡說。查不到就不寫那個細節。

### 5. 改 HTML

- 只換 `<div class="gloss-body prose">…</div>` 或那幾個 `<p>`，不動 `summary` 的 id、`a.tm` 連結。
- 表：`<div class="table-wrap"><table><thead>…</thead><tbody>…</tbody></table></div>`。
- 檔案：`<figure class="file"><figcaption>檔名</figcaption><pre><code>…</code></pre></figure>`。`<` 寫 `&lt;`。
- 句子照 STE：一句一個意思，主動語態，少用「被」。
- 中文標點全形，中英文之間一個空格。

### 6. 跑檢查

頁數在 `slides/lXX-notes.md` 第 4 行，PDF 檔名在頁面的 `a.ref`：

```bash
cd /home/claude/cs2680
python3 -I tools/punct.py docs/lXX.html --diff         # 要印 0 text nodes would change；有就只看自己改的那幾行
grep -o 'slides/[^"#]*\.pdf' docs/lXX.html | head -1   # PDF 檔名
sed -n 4p slides/lXX-notes.md                          # 頁數
python3 -I tools/check_article.py docs/lXX.html --pages N --pdf FILE.pdf > /tmp/after.txt 2>&1
git stash -q && python3 -I tools/check_article.py docs/lXX.html --pages N --pdf FILE.pdf > /tmp/before.txt 2>&1; git stash pop -q
diff /tmp/before.txt /tmp/after.txt                    # 只能差行號和句數，不能多 warn
```

`deep-time` 或 `read-time` 變了，再跑一次加 `--fix-time`。

版面：用 playwright 在 390px 和 1280px 打開該 `details`，截圖看一眼，確認 `scrollWidth <= clientWidth` 且沒有 page error。沒裝瀏覽器先 `python3 -m playwright install chromium`。

### 7. 寫回規則、commit、push

- `guide/README.md` 第 3 行「更新：」最前面加一句，說改了哪一段、為什麼。
- 新的寫法（例如「名詞註可以放表和 code」）寫進 `guide/STYLE_ARTICLE.md` 對應的節。
- commit 訊息用中文，一句說改了什麼。push 到 `main`。
- push 被拒（non-fast-forward）：`git fetch origin main && git rebase origin/main`。`README.md` 和 `STYLE_ARTICLE.md` 第 3 行的「更新：」幾乎一定衝突：保留對方的句子，把自己的句子加在最前面；對方也升了版號，自己的版號再加一（例如對方 v5.7，自己改成 v5.8），標題行一起改。解完再跑一次第 6 步的檢查。

回覆 James：只列改了什麼、哪裡要他看。不重貼全文。

## 不要做的事

- 不要把上方已經有的 code 再貼一次；指過去。
- 不要為了湊「2–4 句」把案例刪掉。有案例的 gloss 可以長。
- 不要在 `gloss`、`summary`、`figcaption`、動手試試裡放 `<strong>`。
- 不要憑印象寫第三方 repo 的檔名或欄位。
- 不要盲跑 `punct.py` 寫回整頁；只用 `--diff` 看。
