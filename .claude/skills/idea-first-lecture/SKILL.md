---
name: idea-first-lecture
description: James 要把某一堂（docs/lXX.html）改成「L5 的模式」「依想法重組」「v7」時用。先列出這堂傳遞的想法、排份量、查課程漏掉的主題，再照重要性重寫核心觀念：不照 slides 順序、不寫 slide 頁碼、圖優先、目錄類內容收成查閱；保留問題討論、動手試試、延伸閱讀，修好連進來的錨點，跑檢查，push。
---

# 把一堂改成 v7：依想法的重要性重組

範本是 `docs/l05.html`（2026-11-03 完成）。規則在 `guide/STYLE_ARTICLE.md` 第 0 節。一個 session 只改一堂，做完再開下一個。

James 的期待（2026-11-02、11-03）：

- 讀完能判斷、能設計，不是記住 slides 的分類。Slides 是素材，順序和頁碼都可以不管。
- 看投影片覺得舒服，是因為圖多字少。講架構、流程、狀態的地方一定要有圖。
- 他會問「決策的邏輯」，回覆要講為什麼這樣排、為什麼補、為什麼刪，不是只列做了什麼。

## 1. 開工

照 `guide/WORKFLOW.md` A 開工。然後讀三樣東西：

```bash
cd /home/claude/cs2680
sed -n 1,80p guide/STYLE_ARTICLE.md          # 第 0 節是 v7 的規則
cat slides/lXX-notes.md | head -120          # 這堂 slides 的逐頁筆記（事實的來源）
python3 -I - <<'EOF'                          # 目前頁面的章節與每章的小標
import re; s = open('docs/lXX.html', encoding='utf-8').read()
for h in re.findall(r'<h3><span class="idea-no">([\d.]+)</span>(.*?)<a', s): print(h[0], re.sub('<[^>]+>', '', h[1]))
for b in re.findall(r'<p[^>]*><b>(.*?)</b>', s[s.index('id="s-ideas"'):s.index('id="s-discuss"')]): print('  -', re.sub('<[^>]+>', '', b)[:50])
EOF
```

也看一次 `docs/l05.html` 的第 1 段，知道成品長什麼樣。

## 2. 排份量（先在回覆草稿裡寫出來，不必等 James 回）

把這堂的每個想法列成一行，用三個問題排：

1. **它會不會改變讀者的決定？** 會，就排前面。只是幫你命名的分類排後面。
2. **忽略它的代價多大、能不能挽回？** 錯在最上游的決定排最前面。
3. **它能不能從別的想法推出來？** 能，就降級，在推導時順帶講。

另外看它多久會過時：原則留在正文，方法名、欄位名、版本細節收成查閱。

分組照內容命名，L5 的分組是參考，不是固定的：「一定要會」「要用時會做」「底層」「要防的」「需要時查」。

## 3. 找課程漏掉的

問兩件事：這堂的論證有沒有不完整的地方（L5：權限隔離擋不住流回來的文字）？2025–2026 年業界或論文有沒有改變結論（L5：Cognition 2026 的讀寫分界）？

- 用 WebSearch／WebFetch 查原始來源，記下作者、日期、數字。只有一家公司的經驗要寫明「不是對照實驗」。
- 延伸閱讀裡已經有的文章，先讀頁面上的摘要，不要重查。
- 補進正文的章，在 `nav.map` 的小字標「本文補的」。

## 4. 寫核心觀念

一份 build script 寫在 `notes/lXX/build.py`（不 commit），用 `tools/dg.py` 畫圖、重用舊圖。做法照 L5（2026-11-03 的 `notes/l05dg/v2.py`、`final.py` 已刪，以下是它們的步驟）：

1. 舊頁面先存一份：`git show HEAD:docs/lXX.html > notes/lXX/old.html`。之後一律從這份讀，script 才能重跑。
2. 每章的標題寫成「主題：主張」，例如「最重要的判斷：多數任務不該拆」。
3. 每章先一句講問題，再給圖或表，再講機制和例子。名詞第一次出現就解釋（STYLE_ARTICLE 第 4 節）。
4. 圖：關係、流程、時序、攻擊路徑畫成圖；要逐列比較的數字或條目用表。圖裡的專有名詞用英文。舊頁面的圖可以用 `dg.reuse()` 重用，改 marker 前綴、去掉 `p.N`。
5. 算式一步步算給讀者看：先定義每一項，再給公式，再列逐列算好的表（L5 第 4 章「拆多細」）。
6. 不寫 slide 頁碼，`h3` 不放 `a.ref`。來源是外部文章時，在句子裡放連結。
7. 分類、清單、協定細節收在最後一章「目錄」，或 `details.gloss`（`gloss-k` 寫「查閱」）。
8. `section#s-ideas` 開頭放 `header.part-head`（kicker「1 · 核心觀念」、h2、p.lede），接著 `nav.map`，每章一列 `a.map-row`，分組用 `p.map-g`。

## 5. 保留其他段落，修好連結

v7 頁面是四段：1 核心觀念、2 問題討論、3 動手試試、4 延伸閱讀。沒有「架構」段。

```bash
grep -o 'lXX\.html#[A-Za-z0-9_-]*' docs/*.html | grep -v '^docs/lXX' | sort | uniq -c   # 別頁連進來的錨點
```

- 別頁連進來的錨點：連到新章節（改那一頁的 href 與連結文字），或在新頁面相同內容的段落保留同一個 id（L5 保留了 `t1`、`t2`、`t3`）。
- 問題討論、動手試試、延伸閱讀從舊頁面整段搬過來。kicker 的段號改成 2、3、4，「第 4 段動手試試」這類文字一起改。
- 每題基礎題的 `p.tk-rel`（相關：）整句重寫，連到新章節。延伸閱讀摘要裡連到舊章節、舊本文延伸（`#xN`）的地方也改。改完確認沒有殘留：`grep -o 'href="#[^"]*"' docs/lXX.html` 的每個目標都存在。
- 側欄 `li.sn-lec.is-here`：四個 `sn-sec`，核心觀念底下列每章（`sn-sub`），每章的粗體小標當第三層（`sn-sub2`，小標的 `<p>` 要有 id）。
- `h1`、`p.en-title` 不改，否則每一頁的側欄都要重建（`add_lecture.py --check` 會報）。
- 首頁 `index.html` 的課程地圖 chip 連到哪一章，一起改。

## 6. 檢查

```bash
python3 -I tools/check_article.py docs/lXX.html --pages N --pdf FILE.pdf --fix-time   # 要 OK；warn 看一次
python3 -I tools/check_discuss.py docs/lXX.html     # 要 OK
python3 -I tools/check_diagrams.py docs/lXX.html    # 圖的文字不超框、不重疊
python3 -I tools/audit.py                           # 要 NO PROBLEMS（連進來的錨點也在這裡檢查）
python3 -I tools/add_lecture.py --check             # 要 nothing (in sync)
python3 -I tools/punct.py docs/lXX.html --diff      # 只看，不要盲跑寫回
python3 -I tools/discuss.py docs/lXX.html --sync-body --dry   # issue 內文的「站台第 N 段」會變，看過再去掉 --dry
```

- `nav.map` 每章的分鐘數用 WORKFLOW B4 的公式算，和頁首的閱讀時間同一套。
- 用 playwright 截圖，亮、暗、390px 各看一次。
- 新增了 `styles.css` 的 class，就把這頁的 `styles.css?v=` 版本號往上改。
- push 之後在線上版再跑一次 `check_diagrams` 的 JS（真字型的寬度不同）。

## 7. 收尾

- `guide/README.md` 第 3 行「更新：」加一句。規則變了就寫進 STYLE_ARTICLE 第 0 節。
- commit、push（WORKFLOW D）。
- 回覆 James：先講決策的邏輯（份量怎麼排、補了什麼和為什麼、刪了什麼和為什麼），再列要他確認的地方。不重貼全文。
