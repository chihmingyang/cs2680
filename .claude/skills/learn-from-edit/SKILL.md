---
name: learn-from-edit
description: James 親手改了站台（commit 訊息以「網頁編輯：」或「改稿：」開頭）之後用；開工時 tools/edit_digest.py list 有東西、或他說「看我的改稿」「我改了 L3，你看看」時用。把他的改動當 code review 的 comment：逐處猜出他為什麼改、對到哪一條規則、流程哪一步該抓到卻沒抓到，再改流程（測試題、checklist、skill、規則），而不是只改這一處。
---

# 從 James 的改稿學：他的 diff 是 review comment

James 直接改字、commit，這比他在對話裡說「看不懂」更準：diff 精確告訴我們哪幾個字錯了、他要的是哪一種寫法。但 diff 只有「改了什麼」，沒有「為什麼」。這份 skill 的工作是補上「為什麼」，再問**流程哪一步該抓到它**，修那一步。

**他改的字是他的決定。** 不改回來、不順手潤他的句子。只有他的改動弄壞了別處（刪掉的詞後面還在用、連結斷了、檢查沒過），才修別處，並在回覆裡說。

## 1. 找出還沒處理的改稿

```bash
cd /home/claude/cs2680 && git pull --rebase
python3 -I tools/edit_digest.py list            # 沒有就結束
python3 -I tools/edit_digest.py show <sha>      # 讀者看得到的 before／after，[-刪-]{+加+}
python3 -I tools/edit_digest.py show <sha> --html   # 要看紅字、連結、標籤時
```

commit 訊息在摘要後面若寫了原因（「網頁編輯：L3 改 2 段 — 這句太繞」），以他寫的為準。

## 2. 每一處：寫一行「改了什麼 → 為什麼」

先讀改動前後各一段（`page_text.py`），再歸類。類別也是 `mark` 要填的：

| 類別 | 他的改動長什麼樣 | 先查哪條規則 |
|---|---|---|
| typo／事實 | 錯字、數字、名稱、日期 | `guide/sources/lXX.md`；同一個錯別處有沒有（`grep`） |
| 語句 | 換連接詞、拆句、代名詞換回名詞、調語序 | REVIEW_READABILITY 的 R 條、STYLE_ARTICLE 第 1 節 |
| 缺context | 加括號說明、加一句定義、加例子 | 名詞第一次出現要說來歷（R 條） |
| 刪支線 | 整段或半句刪掉 | STYLE_ARTICLE 第 0 節〈精簡〉、〈課程內部的數據〉 |
| 數字 | 數字刪掉或搬走 | R18、〈精簡〉 |
| 紅字 | 只動 `<strong>` | STYLE_ARTICLE 6c、mark-red |
| 結構 | 段落搬位置、標題改名 | 第 0 節〈章的順序〉 |
| 品味 | 換一個同義的說法，看不出規則 | 先不歸納 |

猜不出原因、而且兩種讀法會導出不同的規則時，才問他；問的時候給兩個選項。

## 3. 每一處：流程哪一步漏了

照順序問，停在第一個「是」：

1. **規則有寫，寫作的 skill 沒照做？**（idea-first-lecture、rewrite-with-example）→ 改那個 skill 的步驟或例子。
2. **規則有寫，可讀性審查沒抓到？** → 照 REVIEW_READABILITY〈審查者的測試題〉存一題到 `guide/review_cases/`，改 `reviewer-prompt.md` 那一條的說法，跑 `tools/review_eval.py`。
3. **規則有寫，修 BLOCK 的修法錯了？**（例如用補字修到超載）→ 改 readability-review 的〈修 BLOCK〉。
4. **紅字** → 改 6c 的判準或 mark-red 的步驟。
5. **沒有規則** → 新規則的候選。改規則要先問 James（WORKFLOW C）：回覆裡寫「你的改動 → 我讀出的規則 → 全站還有 N 處同樣的情況」，等他說好。
6. **品味、只出現一次** → 只記下，不立規則。`edit_log.tsv` 裡同一類出現第二次，再當成 5 提出來。

## 4. 掃全站有沒有同樣的情況

規則已經有、而且是機械能找的（某個詞、數字密度、某種句型），就 `grep` 或寫一次性的掃描，列出全站的命中數。照現有規則改得了的直接改（照平常的 I 審查、D 發布）；要判斷的列在回覆裡。能變成 `check_article.py` 的 warn 就加進去，讓下一次不必靠人。

## 5. 收尾

```bash
python3 -I tools/edit_digest.py mark <sha> <類別> "學到什麼；改了 guide／skill 的哪裡"
```

一個 commit 有好幾類，記主要的那一類，其他寫在句子裡。`guide/edit_log.tsv` 要 commit。流程改了就照 WORKFLOW E 記 CHANGELOG。

他改過的章在 `review_status.py` 會變成「改過」。不必為了他的改動重審；下次 Claude 動到那一章時照常審，審查者標到他的句子時，**不改他的字**，回報給他。

## 6. 回覆 James

先講讀出來的規律（一兩句），再一處一行：

```
L3 #n-plugin-dir：你把「每個 harness 各有一個」移到後面、加了 harness 是什麼 → 名詞第一次出現沒說來歷（R 缺 context）→ 審查沒抓到：存成測試題，reviewer-prompt 的那條改了說法
L3 #i2-4：你刪了 Superpowers 的版本比較 → 支線（〈精簡〉第 2 點已有）→ 全站還有 3 處同樣的比較，已刪
L5 #i3-1：換了一個說法 → 看不出規則，先記下
```

要他決定的（新規則）放最後，一條一行。不貼全文。
