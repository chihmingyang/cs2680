---
name: rewrite-with-example
description: James 貼一段站台（docs/lXX.html）或任何說明文字說「看不懂」、「語句不順」、「請修改」、「補案例」、「圖也看不懂」時用。先找出是語句接不上還是某個詞缺 context，改順句子、補詞的來歷、補一個真實的檔案內容或指令當案例、需要時加一張圖；圖看不懂就再改圖。核對事實，改進 HTML，跑檢查，push。
---

# 看不懂的段落：改順、補 context、補案例、補圖

James 讀不懂一段文字，通常是兩個原因：**語句不順**（句子接不上、代名詞不知道指誰、一句塞兩件事），或**某個詞缺 context**（名詞出現時沒說它是什麼、在哪裡、誰用）。他不偏好短句；為了短句把語氣切斷，反而更難讀。有圖更好，但圖也可能看不懂，要能再改。

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

### 2. 診斷：對原文逐句找問題，寫出 2–3 個原因

| 症狀 | 怎麼改 |
|---|---|
| **語句不順**：一句塞兩件事；「它」「這個」「各處」不知道指誰；前一句講 A，下一句突然講 B，中間沒有「所以」「但是」「因為」 | 一句一件事，但保留連接詞，讓句子接得上。代名詞換回名詞（「它」→「plugin 附的 `settings.json`」）。先講事實，再講結論。 |
| **某個詞缺 context**：名詞第一次出現就拿來用，沒說它是什麼、放在哪、誰寫它、什麼時候起作用 | 第一次出現時用一句定義，再用一句說它在這段裡扮演什麼。站台別處已有註，就改成 `<a class="tm" href="#n-xxx">` 連過去；沒有就在這裡寫。 |
| **只有規則，沒有案例**：全文是「可以寫在…」「差在…」 | 補一個 `figure.file`：真的檔名、真的內容，前面一句「你要做什麼」，後面一句「這會發生什麼」。 |
| **三個以上的東西互相影響**（誰合併誰、誰覆蓋誰、哪個先跑、放在哪一層） | 平行項目改成 `div.table-wrap > table`，一項一列。關係本身畫成一張 `figure.diagram`（第 4 步）。 |

原因要寫在回覆裡，一行一個，指出原文的哪一句。他要知道為什麼改。

STYLE_ARTICLE 第 5 節的 STE 比例是站台的規則，`check_article.py` 會算；它不是這個 skill 的目標。不要為了湊短句把一段話切得前後接不上。

### 3. 先給純文字版，等他說 OK

照他的習慣：先純文字，不要先改 HTML。回覆長這樣：

```
原段看不懂的原因有三個：
1. 第 2 句「各處的 hook 合併」：「各處」指哪幾處，前面沒說。
2. …
改寫如下：
---
（新標題）
（名詞定義一句 + 它在這裡做什麼一句）
（表）
案例：你要…。在 <檔名> 寫：
（code block）
（這會發生什麼，一句）
（其餘段落）
[圖：一句話說這張圖要回答什麼問題，列出幾個框、幾條箭頭]
---
要我寫進 docs/lXX.html、畫圖、跑檢查、push 嗎？
```

案例的規則：

- 用第二人稱情境開頭：「你要這個專案每次開對話，先印出 git 狀態。」
- 檔名寫完整路徑：`.claude/settings.json`，不寫「設定檔」。
- 內容要能直接貼進去用。能用一行指令就不要寫腳本（`git status --short` 比 `bootstrap.sh` 好懂）。
- 案例不在 slide 裡，就標「案例（本文補的）」。
- 標題改成講「放哪裡」「怎麼做」的具體句，不用「差在誰寫、何時生效」這種抽象句。

### 4. 圖解：什麼時候畫、怎麼畫才看得懂

**什麼時候畫**：原文在講三個以上的東西之間的關係（合併、覆蓋、順序、層次、誰能動誰），而文字要用兩段以上才講得完。只講一個名詞的定義，不畫。

**一張圖只回答一個問題**。先寫出那個問題，當 figcaption 的第一句：「四份 hook 設定怎麼合併成一份？」畫不進一個問題的，拆成兩張。

畫的規則（他看不懂圖，多半是下面其中一條沒做到）：

| 圖看不懂的原因 | 怎麼改 |
|---|---|
| 框太多，不知道先看哪裡 | 框最多 6 個。要讀者照順序看的，箭頭上標 ①②③。 |
| 框上的字是抽象詞（「設定」「來源」） | 框上寫真的檔名、路徑、值：`~/.claude/settings.json`、`hooks.json`。 |
| 箭頭不知道是什麼意思 | 每條箭頭都有動詞標籤：「合併進」「寫入」「觸發」。線的樣式超過兩種就加圖例。 |
| 圖和文字對不上 | 圖裡的名字和正文、案例裡的名字完全一樣。正文裡用一句說「看上圖：…」。 |
| 看完不知道結論是什麼 | figcaption 第二句寫結論：「結果：四份都跑；但 plugin 寫不進你的 settings.json。」 |

HTML 格式（STYLE_ARTICLE 第 6 節）：

```html
<figure class="diagram">
  <div class="scroll">
    <svg viewBox="0 0 640 220" role="img" aria-label="（把圖用文字講一遍：有哪幾個框、箭頭怎麼走、結論是什麼）">
      <defs><marker id="l3c-hf-ah" …></marker></defs>   <!-- marker id 加頁前綴 lNc-，全站不重複 -->
      <rect class="dg-box" …/><text class="dg-t" …>~/.claude/settings.json</text>
      <line class="dg-line" marker-end="url(#l3c-hf-ah)" …/><text class="dg-ts" …>① 合併進</text>
    </svg>
  </div>
  <figcaption>這張圖回答的問題。結論一句。（本文的整理）</figcaption>
</figure>
```

只用 `styles.css` 的 class（`dg-box`、`dg-box-soft`、`dg-box-accent`、`dg-line`、`dg-dash`、`dg-t`、`dg-tb`、`dg-ts`…），不寫死顏色，svg 內不放 `<style>`。文字 11–13px，viewBox 寬 600–760。畫完用 playwright 在 390px 和 1280px 截圖，自己看一次：框裡的字有沒有被切掉、箭頭有沒有壓到字。

**他說「圖也看不懂」時**：不要重畫一張更複雜的。問自己上表五個原因是哪一個；通常是框太多或標籤太抽象。改法是減框、把字換成真名、加 ①②③、figcaption 加結論。改完截圖給他看，再問一次。

### 5. 核對事實

寫到第三方 repo（Superpowers、Caveman、mattpocock/skills…）的檔名、欄位、路徑，先查再寫：

```bash
gh api repos/obra/superpowers/contents/hooks/hooks.json --jq .content | base64 -d
```

`gh` 不行就 WebSearch。查到和原文不同，改原文並在回覆裡說。查不到就不寫那個細節。

### 6. 改 HTML

- 只換 `<div class="gloss-body prose">…</div>` 或那幾個 `<p>`，不動 `summary` 的 id、`a.tm` 連結。
- 表：`<div class="table-wrap"><table><thead>…</thead><tbody>…</tbody></table></div>`。
- 檔案：`<figure class="file"><figcaption>檔名</figcaption><pre><code>…</code></pre></figure>`。`<` 寫 `&lt;`。
- 句子要接得上：每段先一句說這段講什麼，句與句之間有連接詞；代名詞能換名詞就換。
- 中文標點全形，中英文之間一個空格。

### 7. 跑檢查

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

`deep-time` 或 `read-time` 變了，再跑一次加 `--fix-time`。加了圖就跑 `python3 -I tools/audit.py`（SVG 的 `role`、`aria-label`、marker id 重複、390px 溢出）。

版面：用 playwright 在 390px 和 1280px 打開該 `details`，截圖看一眼，確認 `scrollWidth <= clientWidth` 且沒有 page error。沒裝瀏覽器先 `python3 -m playwright install chromium`。

### 8. 寫回規則、commit、push

- `guide/README.md` 第 3 行「更新：」最前面加一句，說改了哪一段、為什麼。
- 新的寫法（例如「名詞註可以放表和 code」）寫進 `guide/STYLE_ARTICLE.md` 對應的節。
- commit 訊息用中文，一句說改了什麼。push 到 `main`。
- push 被拒（non-fast-forward）：`git fetch origin main && git rebase origin/main`。`README.md` 和 `STYLE_ARTICLE.md` 第 3 行的「更新：」幾乎一定衝突：保留對方的句子，把自己的句子加在最前面；對方也升了版號，自己的版號再加一（例如對方 v5.7，自己改成 v5.8），標題行一起改。解完再跑一次第 7 步的檢查。

回覆 James：只列改了什麼、哪裡要他看。不重貼全文。

## 不要做的事

- 不要把上方已經有的 code 再貼一次；指過去。
- 不要為了短句切斷語氣；也不要為了湊「2–4 句」把案例或圖刪掉。有案例和圖的 gloss 可以長。
- 不要在 `gloss`、`summary`、`figcaption`、動手試試裡放 `<strong>`。
- 不要憑印象寫第三方 repo 的檔名或欄位。
- 不要盲跑 `punct.py` 寫回整頁；只用 `--diff` 看。
- 圖看不懂時，不要加更多框去解釋；先減。
