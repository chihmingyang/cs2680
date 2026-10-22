# 基礎題撰寫規範（v3.1）

更新：2026-10-19（v3.1：站台搬到 `docs/`；留言改在 GitHub Issues）。對照的是 L1–L8 的實際格式（每堂 5 題，參考答案是重點複習）。

基礎題放在第 5 段的「基礎」分頁 `div.qset#qset-basic`，直接寫在 `docs/lXX.html` 裡。**範本：`docs/l02.html` 的 `#qset-basic`，先完整讀一遍。**

## 定位

- 讀者在**看 slides 之前**先讀題目，帶著問題一頁一頁看 slides，看到對應的頁就記下答案，看完再展開參考答案對照。讀書會後也可以只看參考答案複習。
- 每一題都要**能在 slides 裡直接找到答案**。不問 slide 沒講的事；不要求估算或設計（那是進階題的工作）。
- 題目指向這堂**最重要的機制、主張、數字、對比**：問「為什麼」「差在哪裡」「哪一個」「到什麼時候」。不問瑣碎的名詞定義。
- 通用：不提特定公司、產品或專案。
- 不要和進階題重複。基礎題問「slide 說了什麼」，進階題問「你會怎麼做」。

## 題數與題目

- **最多 5 題**（3–5 題；L1–L8 都是 5 題），依 slide 順序，id `b1`…`b5`。整堂的主要段落都要覆蓋到。
- 一題可以有 2–3 個小問，但都落在同一段連續的 slides。
- `p.qtag`：`a.ref`（`#page=` 用範圍的第一頁，文字寫 `p.N–M`）+ ` · ` + 2–6 字主題。
- `p.qtext`：1–3 句，≤ 60 字。
- 不放 `qctx`、`qcover`、作答範本。

## 參考答案：寫成重點複習

每題一個 `details.tk`，summary 是「參考答案與重點複習」，內容是 `div.hint.takeaway`。**不要寫短。** 它是讀書會後帶得走的複習筆記：約 600–1000 字（L1–L8 中位數約 800），有圖幫助理解時就附圖。

依序放：

1. `div.tk-ans`：`<p><b>答案：</b>……</p>`。先直接回答題目，2–4 句，標頁碼（例「p.11 說……」）。
2. `p.tk-h`「重點拆解」+ 2–3 段：把答案背後的機制拆開講。**只用 slides 的內容**，標頁碼。數字和 slide 一致。
3. 選用 `figure.diagram`：一張圖說清楚機制時就畫（L1–L8 約六成的題目有圖）。規則同 `STYLE_ARTICLE.md` 第 6 節；marker id 前綴 `tkN-<題號>-`。
4. `p.tk-h`「背景補充」+ 1–3 段：超出 slides 的背景（一般知識、官方文件、相關機制）。**超出 slides 的內容只放這裡。**
5. `div.callout.caution`「常見誤解」：一個讀者容易誤會的地方，先寫錯的說法，再說為什麼不對。幾乎每題都要有。
6. 選用 `div.callout.example`「例子」：設定檔、指令、小算式（`figure.file` 或 `pre`）。
7. `div.tk-keys`：`<b>帶走這幾點</b>` + `ol` **3 點**。每點一行，用 `→` 串起因果。
8. `p.tk-rel`：`<b>相關：</b>` 連到本頁的核心觀念〈`#iN`〉、延伸思考〈`#xN`〉、第 6 段，有進階題延伸這一題時，說是第幾題（進階題只有 3 題，沒有就不寫）。

結構範例（省略內文）：

```html
<li class="bq" id="b1">
  <div class="qbody">
    <p class="qtag"><a class="ref" href="https://cs2680.com/slides/<pdf>#page=6" target="_blank" rel="noopener">p.6–11</a> · Agent loop</p>
    <p class="qtext">題目。</p>
    <details class="tk"><summary>參考答案與重點複習</summary><div class="hint takeaway">
      <div class="tk-ans"><p><b>答案：</b>……</p></div>
      <p class="tk-h">重點拆解</p>
      <p>……</p>
      <figure class="diagram">……</figure>
      <p class="tk-h">背景補充</p>
      <p>……</p>
      <div class="callout caution"><span class="tag">常見誤解</span><div><p>……</p></div></div>
      <div class="callout example"><span class="tag">例子</span><div>……</div></div>
      <div class="tk-keys"><b>帶走這幾點</b><ol><li>……</li><li>……</li><li>……</li></ol></div>
      <p class="tk-rel"><b>相關：</b>核心觀念〈<a href="#i1">……</a>〉；……</p>
    </div></details>
  </div>
</li>
```

每一題下面的「到 GitHub 回答這一題（Qn）」連結（`p.gh-talk`）由 `tools/discuss.py` 寫入，不要自己寫。連結指到該堂的 issue（每堂一串）。

## 分頁外框（照抄範本，改講次與標題）

```html
<div class="qset" id="qset-basic" role="tabpanel" aria-labelledby="tab-basic">
  <p class="qset-lede">看 slides 之前先讀一遍這 5 題。它們依 slide 順序排列，答案都在對應的頁裡。看到那幾頁時，把答案記下來；看完再展開「參考答案與重點複習」對照：它先直接回答，再把這一題的觀念整理成複習筆記，有些附圖。卡住的地方，按題目下面的「到 GitHub 討論這一題」留言。</p>
  <div class="copyrow">
    <button type="button" class="copybtn" data-copy="basic" data-title="CS2680 LX 基礎題（帶著問題看 slides）：<中文標題>" data-slides="https://cs2680.com/slides/<pdf>">複製基礎題</button>
    <span class="copyhint">只複製題目與頁碼，方便貼到群組。</span>
  </div>
  <ol class="qlist qlist-basic">
    …
  </ol>
</div>
```

題數不是 5 時，改 `qset-lede` 裡的「這 5 題」。

## 語言

同 `STYLE_ARTICLE.md` 第 5 節：一句一件事、主動語態、不寫「被」、不用填充詞、術語保留英文、全形標點、中英文之間半形空格、HTML 特殊字元跳脫。

## 驗證

```bash
python3 -I tools/punct.py docs/lXX.html --diff
python3 -I tools/check_discuss.py docs/lXX.html
```

`check_discuss.py` 在 `discuss.py` 跑完後要印出 `OK`。`warn: no 常見誤解 callout` 表示少了常見誤解，能補就補。
