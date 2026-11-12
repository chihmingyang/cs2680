---
name: idea-first-lecture
description: James 要把某一堂（docs/lXX.html）改成「L5 的模式」「依想法重組」「v7」時用。先列出這堂傳遞的想法、排份量、查課程漏掉的主題，再照重要性（想法之間有依賴時照依賴順序，STYLE_ARTICLE 第 0 節〈章的順序〉）重寫核心觀念：不照 slides 順序、不寫 slide 頁碼、圖優先、目錄類內容收成查閱；保留動手試試、延伸閱讀，修好連進來的錨點，跑檢查，push。
---

# 把一堂改成 v7：依想法的重要性重組

範本是 `docs/l05.html`（2026-11-03 完成）。規則在 `guide/STYLE_ARTICLE.md` 第 0 節。L1–L8 都已改完（2026-11-03），各堂的取捨在 `guide/V7_DECISIONS.md`，之後用於新講次或重做一堂。一個 session 只改一堂，做完再開下一個；要同時改多堂，一堂一個 subagent，簡報是同目錄的 `subagent-brief.md`，整合方法見 `guide/WORKFLOW.md` H。

**新講次**（沒有舊頁面，2026-11-06 L9–L11 起）：骨架用 `tools/new_lecture.py` 建，動手試試、原文出處也寫成片段（`try.html`、`wrap.html`）由 `assemble_v7.py` 一起組；第 5 步的錨點與保留段落不適用。好幾堂同時寫，一堂一個 subagent，簡報是同目錄的 `new-lecture-brief.md`，接線照 `guide/WORKFLOW.md` B5。

James 的期待（2026-11-02、11-03）：

- 讀完能判斷、能設計，不是記住 slides 的分類。Slides 是素材，順序和頁碼都可以不管。
- 看投影片覺得舒服，是因為圖多字少。講架構、流程、狀態的地方一定要有圖。
- 他會問「決策的邏輯」，回覆要講為什麼這樣排、為什麼補、為什麼刪，不是只列做了什麼。

## 1. 開工

照 `guide/WORKFLOW.md` A 開工。然後讀三樣東西：

```bash
cd /home/claude/cs2680
sed -n 1,80p guide/STYLE_ARTICLE.md          # 第 0 節是 v7 的規則
cat slides/lXX-notes.md                       # 這堂 slides 的逐頁筆記（事實的來源）
python3 -I tools/page_text.py docs/lXX.html   # 舊頁面的文字，圖印成 aria-label；頁面很大，不要整個 Read
python3 -I - <<'EOF'                          # 目前頁面的章節與每章的小標
import re; s = open('docs/lXX.html', encoding='utf-8').read()
for h in re.findall(r'<h3><span class="idea-no">([\d.]+)</span>(.*?)<a', s): print(h[0], re.sub('<[^>]+>', '', h[1]))
for b in re.findall(r'<p[^>]*><b>(.*?)</b>', s[s.index('id="s-ideas"'):s.index('id="s-try"')]): print('  -', re.sub('<[^>]+>', '', b)[:50])
EOF
```

也看一次 `docs/l05.html` 的第 1 段，知道成品長什麼樣。

## 2. 排份量（先在回覆草稿裡寫出來，不必等 James 回）

把這堂的每個想法列成一行，用三個問題排：

1. **它會不會改變讀者的決定？** 會，就排前面。只是幫你命名的分類排後面。
2. **忽略它的代價多大、能不能挽回？** 錯在最上游的決定排最前面。
3. **它能不能從別的想法推出來？** 能，就降級，在推導時順帶講。

另外看它多久會過時：原則留在正文，方法名、欄位名、版本細節收成查閱。

排完份量之後，先檢查這些想法之間有沒有依賴（2026-11-12，L6b）：把各章的主題寫成名詞，問「不先講 A，B 講得清楚嗎」。有兩條以上這種邊（資料流、層次、pipeline），章就照依賴順序排，份量改用「先看這裡」、`nav.map` 小字、紅字表達，不靠章序。規則在 `STYLE_ARTICLE.md` 第 0 節〈章的順序〉。

分組照內容命名，L5 的分組是參考，不是固定的：「一定要會」「要用時會做」「底層」「要防的」「需要時查」。

## 3. 找課程漏掉的

問兩件事：這堂的論證有沒有不完整的地方（L5：權限隔離擋不住流回來的文字）？2025–2026 年業界或論文有沒有改變結論（L5：Cognition 2026 的讀寫分界）？

- 用 WebSearch／WebFetch 查原始來源，記下作者、日期、數字。只有一家公司的經驗要寫明「不是對照實驗」。
- 補進正文的章不標「本文補的」，正文也不寫「課程說…」「slides 的例子是…」（2026-11-13，STYLE_ARTICLE 第 0 節〈不提 slides 怎麼寫〉）。

## 4. 寫核心觀念

每章一個片段 `notes/lXX/iN.html`（不 commit），加上 `head.html`、`tldr.html`、`fineprint.html`，用 `tools/assemble_v7.py docs/lXX.html notes/lXX --base notes/lXX/old.html` 組回頁面：它換掉 tldr 與 `#s-ideas`、拿掉 `#s-arch`、改段號、eyebrow、meta、CSS 版本，並重建本頁的側欄。圖用 `tools/dg.py` 畫。做法：

1. 舊頁面先存一份：`git show HEAD:docs/lXX.html > notes/lXX/old.html`。之後一律從這份讀，script 才能重跑。
2. 每章的標題寫成「主題：主張」，例如「最重要的判斷：多數任務不該拆」。
3. 每章先一句講問題，再給圖或表，再講機制和例子。名詞第一次出現就解釋（STYLE_ARTICLE 第 4 節）。
4. 圖：關係、流程、時序、攻擊路徑畫成圖；要逐列比較的數字或條目用表。圖裡的專有名詞用英文。舊頁面的圖可以用 `dg.reuse()` 重用，改 marker 前綴、去掉 `p.N`。
5. 算式一步步算給讀者看：先定義每一項，再給公式，再列逐列算好的表（L5 第 4 章「拆多細」）。
6. 不寫 slide 頁碼，`h3` 不放 `a.ref`。來源是外部文章時，在句子裡放連結。
7. 分類、清單、協定細節收在最後一章「目錄」，或 `details.gloss`（`gloss-k` 寫「查閱」）。
8. `section#s-ideas` 開頭放 `header.part-head`（kicker「1 · 核心觀念」、h2、p.lede），接著 `nav.map`，每章一列 `a.map-row`，分組用 `p.map-g`。

## 5. 保留其他段落，修好連結

v7 頁面是三段：1 核心觀念、2 動手試試、3 原文出處（2026-11-13 之前叫延伸閱讀；2026-11-09 拿掉問題討論；題目改放每一節後面的小測，`guide/QUIZ.md`）。沒有「架構」段。

```bash
grep -o 'lXX\.html#[A-Za-z0-9_-]*' docs/*.html | grep -v '^docs/lXX' | sort | uniq -c   # 別頁連進來的錨點
```

- 別頁連進來的錨點：連到新章節（改那一頁的 href 與連結文字），或在新頁面相同內容的段落保留同一個 id（L5 保留了 `t1`、`t2`、`t3`）。
- 動手試試、原文出處從舊頁面整段搬過來。kicker 的段號是 2、3，「第 2 段動手試試」這類文字一起確認。
- 動手試試裡連到舊章節、舊本文延伸（`#xN`）的地方也改。改完確認沒有殘留：`grep -o 'href="#[^"]*"' docs/lXX.html` 的每個目標都存在。
- 側欄 `li.sn-lec.is-here` 由 `assemble_v7.py` 重建：四個 `sn-sec`（先看這裡、核心觀念、動手試試、原文出處），核心觀念底下列每章（`sn-sub`），每章的粗體小標當第三層（`sn-sub2`，小標的 `<p>` 要有 id）。
- 文字裡不寫別堂的章號（「L4 2.6」），寫 L4〈概念名〉。錨點用 `tools/anchor_map.py list`、`check` 對照，`apply` 改別頁的連結。
- `h1`、`p.en-title` 不改，否則每一頁的側欄都要重建（`add_lecture.py --check` 會報）。
- 首頁 `index.html` 的課程地圖 chip 連到哪一章，一起改。

## 6. 檢查

```bash
python3 -I tools/check_article.py docs/lXX.html --pages N --pdf FILE.pdf --fix-time   # 第一次跑：寫回閱讀時間
bash tools/verify.sh lXX     # 之後每一輪都用這個：check_article、check_diagrams、audit（連進來的錨點也查）、add_lecture --check 一次跑完，全過只印 ALL OK；punct 只提示
```

- `nav.map` 每章的分鐘數用 WORKFLOW B4 的公式算，和頁首的閱讀時間同一套。
- 用 playwright 截圖，亮、暗、390px 各看一次。一則訊息平行 Read 6 張，不要一張一則（每一則都要重讀整個 context）。
- 新增了 `styles.css` 的 class，就把這頁的 `styles.css?v=` 版本號往上改。
- push 之後在線上版再跑一次 `check_diagrams` 的 JS（真字型的寬度不同）。

## 6b. 可讀性審查（2026-11-06 起，push 前必做）

照 `.claude/skills/readability-review/SKILL.md`：新寫的一堂全部章都審：tldr 一個審查者（`--chapter tldr`），各章用 `--chapter … --prefix`，單位超過 300 就分成兩段各一個審查者，開全新的 subagent 讀，BLOCK 修完、第二輪過了才收尾。七個 subagent 一天改七堂的時候沒有這一步，L6 的「穩定偏正面」就是這樣漏出去的。

## 6c. 標紅字（2026-11-11 起，審查過了才做）

寫作和修 BLOCK 時不放 `<strong>`。第二輪沒有 BLOCK、`review_status.py mark` 之後，照 `.claude/skills/mark-red/SKILL.md` 整頁標一次（`tools/red_path.py lXX`）。Subagent 寫章的時候也不標，由收尾的 session 做。

## 7. 收尾

- `guide/CHANGELOG.md` 的「README.md」一節最上面加一行。規則變了就寫進 STYLE_ARTICLE 第 0 節，並在 CHANGELOG 的「STYLE_ARTICLE.md」一節加一行。
- commit、push（WORKFLOW D）。
- 回覆 James：先講決策的邏輯（份量怎麼排、補了什麼和為什麼、刪了什麼和為什麼），再貼可讀性審查的 BLOCK 清單與修法，再列要他確認的地方。不重貼全文。
