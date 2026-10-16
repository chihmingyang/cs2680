# 基礎題撰寫規範（§5 的「基礎」分頁）

第 5 段「問題討論」現在分成兩個分頁：**基礎**（帶著問題看 slides）與 **進階**（原本的 6 題讀書會討論題，不要改）。
你負責寫一堂的基礎題，存成 `/home/claude/cs2680/content/lXX-basic.html`。**範本：`/home/claude/cs2680/content/l02-basic.html`，先完整讀一遍，結構與 class 完全照它。**

不要改 `site/` 裡的任何檔案、不要改 styles.css / app.js、不要發布。主程序會用 `tools/split_discuss.py` 把你的檔案接進頁面。

## 定位

- 讀者在**看 slides 之前**先讀這些題目，然後帶著問題一頁一頁看 slides。看到對應的頁，就把答案記下來。看完再展開「參考答案」對照。
- 所以每一題都要**能在 slides 裡直接找到答案**。不要問 slide 沒講的事、不要要求估算或設計（那是進階題的工作）。
- 題目要指向這堂**最重要的機制、主張、數字、對比**：問「為什麼」「差在哪裡」「哪一個」「到什麼時候」，不要問瑣碎的名詞定義。
- 一題可以有 2–3 個小問，但都落在同一段 slides（連續的頁碼範圍）。
- 通用：不提特定公司、產品或專案。

## 結構（照範本）

```html
        <div class="qset" id="qset-basic" role="tabpanel" aria-labelledby="tab-basic">
          <p class="qset-lede">看 slides 之前先讀一遍這 N 題。它們依 slide 順序排列，答案都在對應的頁裡。看到那幾頁時，把答案記下來；看完再展開「參考答案」對照。</p>
          <div class="copyrow">
            <button type="button" class="copybtn" data-copy="basic" data-title="CS2680 LX 基礎題（帶著問題看 slides）：<中文標題>" data-slides="https://cs2680.com/slides/<pdf>">複製基礎題</button>
            <span class="copyhint">只複製題目與頁碼，方便貼到群組。</span>
          </div>
          <ol class="qlist qlist-basic">
            <li class="bq" id="b1">
              <div class="qbody">
                <p class="qtag"><a class="ref" href="https://cs2680.com/slides/<pdf>#page=N" target="_blank" rel="noopener">p.N–M</a> · 主題</p>
                <p class="qtext">題目。</p>
                <details><summary>參考答案</summary><div class="hint">
                  <p>2–4 句。</p>
                  <p>可以第二段。</p>
                </div></details>
              </div>
            </li>
            …
          </ol>
        </div>
```

- **6–9 題**，依 slide 順序，id `b1`…`bN`。整堂的主要段落都要覆蓋到（每個核心觀念至少一題）。
- `qtag`：頁碼 `a.ref`（`#page=` 用範圍的第一頁）+ ` · ` + 2–6 字的主題。
- `qtext`：1–3 句，≤ 60 字。
- `參考答案`：2–4 句，直接給答案，必要時引用頁碼（例「p.11 的例子有 5 次 tool 執行、6 次 inference」）。數字要和 slide 一致（用 archive/lXX-cards.html 核對）。
- 不要放 `qctx`、`qcover`、「思考方向」。
- 不要在基礎題重複進階題的題目；基礎題問「slide 說了什麼」，進階題問「你會怎麼做」。

## 語言

和 STYLE_ARTICLE.md 第 5 節相同：一句一件事、主動語態、不寫「被」、不用填充詞、術語保留英文、全形標點、中英文之間半形空格、HTML 特殊字元跳脫。

## 驗證

寫完後執行：

```bash
cd /home/claude/cs2680
python3 -I tools/punct.py content/lXX-basic.html
python3 -I tools/check_basic.py content/lXX-basic.html lXX
```

`check_basic.py` 要印出 `OK`。然後回報：題數、每題的頁碼範圍與主題（一行一題）。
