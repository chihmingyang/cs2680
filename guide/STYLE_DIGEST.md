# 必讀摘要撰寫規範（v1.1）

更新：2026-10-19（v1.1：路徑改成 `docs/`）。對照的是 L2–L8 的 18 段摘要（L1 沒有必讀）。

延伸閱讀裡標「必讀」的每一篇，`li` 的最後加一段摘要 `details.rg-dg`。目的：成員時間有限，讀摘要（約 3 分鐘）就能掌握這篇的主張與數字；要看原文時，知道哪幾節值得看、哪些段落 slides 已經講過可以跳過。「推薦」「選讀」「查閱」不加摘要。

## 素材

1. 原文：用 WebFetch 讀。arXiv 先試 `https://arxiv.org/pdf/<id>`，失敗再試 `/html/<id>`、`/abs/<id>`。一次回傳太短就換 prompt 多問幾次（只問某一節、某個表、某個數字）。影片：WebSearch 找逐字稿頁再 WebFetch；找不到就用確定的內容，並在片段開頭的註解裡說明沒讀到原文。
2. 這堂課的頁面 `docs/lXX.html` 第 1–4 段：核心觀念 `div.idea#iN` 的 `h3` 有 `a.ref` 指向 slides 頁碼。「跟這堂課的關係」要引用這些頁碼與錨點。
3. 不確定的數字不寫。所有數字來自原文，保留單位。
4. 不直接引用原文句子，用自己的話改寫。

## 片段格式（嚴格照用）

```html
<details class="rg-dg"><summary>摘要<span>讀約 3 分；原文約 N 分</span></summary><div class="hint digest">
  <div class="dg-one"><p><b>一句話：</b>這篇在說什麼、結論是什麼。1–2 句。</p></div>
  <p class="tk-h">跟這堂課的關係</p>
  <p>1–3 句。指出 slides 哪幾頁（「slides p.N」「p.N–M」）來自這篇、本頁哪個核心觀念〈<a href="#iN">標題</a>〉或延伸思考〈<a href="#xN">標題</a>〉談同一件事。有分歧也寫：這篇和 slides 的主張哪裡不同。</p>
  <p class="tk-h">壓縮後的重點</p>
  <ol>
    <li><b>一句主張。</b>1–2 句支撐：機制、數字、例子。</li>
    …（4–7 點）
  </ol>
  <p class="tk-h">原文怎麼讀</p>
  <ul>
    <li><b>可以跳過：</b>哪些節／段落 slides 已經講過，或只是背景鋪陳。寫節名（或影片時間點）。</li>
    <li><b>值得看原文：</b>1–3 處只有原文才有的東西：某張圖、某個表、一段程式碼、一個案例。寫節名或頁數。</li>
    <li><b>時間：</b>只讀摘要約 3 分；照上面挑著看原文約 N 分。</li>
  </ul>
  <div class="callout caution"><span class="tag">別誤讀</span><div><p>一個讀者最容易誤會的地方：先寫錯的說法，再說為什麼不對。1–3 句。</p></div></div>
</div></details>
```

- `summary` 的 `<span>` 只放兩個時間；「原文約 N 分」用 `rg-meta` 上的估計。
- 「別誤讀」每篇都要有。
- 不加其他 class、不加 `style`、不放圖。錨點連結的文字可以用標題的前半（頁面的 `tk-rel` 也這樣做）。
- 長度 450–800 字（中文字 + 英文詞）。論文偏上限，部落格偏下限。
- 不寫討論題（頁面另有討論題）。
- 片段的 `details` 預設收合，所以不算進 read-time；會算進 full-time。
- `p.rg-intro` 的結尾加一句：「必讀」的 N 篇各附一段摘要：3 分鐘讀完它的主張與數字、它和 slides 重疊的部分，以及原文哪幾節值得看。

## 語言

同 `STYLE_ARTICLE.md` 第 5 節。另外：`O(n²)`、`works.any()` 這類程式與數學片段，放進 `<code>`，或確認 `punct.py --diff` 沒有把它們改成全形括號。

## 流程

1. 一篇一個片段檔：`notes/digests/lXX-rN.html`（N 是這篇在延伸閱讀裡的序號）。開頭一行 `<!-- source: <url> | read: yes/partial/no | note: … -->`。
2. 可以把不同講次交給幾個 subagent 平行寫；每個 subagent 先讀這份規範和那堂的頁面。
3. `python3 -I tools/punct.py notes/digests/*.html --diff`，看過再不帶 `--diff` 跑。
4. 用 script 依 `a.rg-t` 的網址（arXiv 比對 id，abs／pdf 都算）找到 `li`，把片段插在 `</li>` 之前。
5. 驗證每個錨點存在、頁碼不超過 `data-pages-total`（跨堂引用要寫「L5 p.36」這種形式）。
6. 跑 B4 的檢查；`check_article.py --fix-time` 會更新 full-time。
