---
name: readability-review
description: 改了 docs/lXX.html 的正文（新寫一堂、改成 v7、rewrite-with-example、fact-check-extension）之後、push 之前用；或 James 說「跑一次可讀性審查」「review 一下 L6」時用。把改過的章打包成讀者視角的純文字，開一個全新的 subagent 當審查者，照 guide/REVIEW_READABILITY.md 的 checklist 逐單位重述並標 BLOCK／NIT，作者修完 BLOCK 再審一輪，最多兩輪，然後才 push。
---

# 可讀性審查：另一個 agent 讀一遍，blocker 清零才 push

規則與 checklist 在 `guide/REVIEW_READABILITY.md`，流程在 `guide/WORKFLOW.md` I。這份 skill 是操作步驟。核心是三件事：審查者是**另一個 session**；它只拿到**讀者看得到的文字**；它要**重述**，不能說「看得懂」。

## 1. 打包改過的章

```bash
cd /home/claude/cs2680
python3 -I tools/review_pack.py docs/lXX.html --since origin/main > notes/review/lXX-pack.md   # 只印文字有變的章
python3 -I tools/review_pack.py docs/lXX.html --units                                           # 看單位數，估時間
```

- 新寫一堂或改成 v7：不加 `--since`，全部章都審（含 tldr）。
- 只改一章或一段：`--since origin/main` 會自動只印那一章；也可以 `--chapter i2`。
- 改了問題討論或動手試試：加 `--sections s-discuss s-try`。
- 單位數超過 300，分兩個審查者，但**每個審查者都拿整頁的 pack**，prompt 裡指定「只審第 N–M 章，其他章是你讀過的上下文」。L6 pilot 的教訓：只給半頁，R3「名詞沒解釋」會大量誤報（第 1–5 章解釋過的 run、context、harness、store，第 6–10 章的審查者全標成 BLOCK），53 個 BLOCK 裡約 15 個是這種。
- pack 會印 code block 的內容（`codeN 內容`），因為正文會指著它說「第二種」「這些欄位」；少了它，這類句子會被誤判成 R2。

## 2. 開審查者（全新的 subagent）

一堂的審查者約 9 萬 token、4–5 分鐘（L6 pilot：三個審查者各 177／164／219 個單位）。

用 Agent tool 開一個 **general-purpose**（不是 fork：fork 會帶著寫作的 context，就不是另一個人了）。Prompt 是三段接起來：

1. `.claude/skills/readability-review/reviewer-prompt.md` 全文。
2. 一行：「審查包在 `/home/claude/cs2680/notes/review/lXX-pack.md`，用 Read 讀它。報告寫到 `/home/claude/cs2680/notes/review/lXX-YYYYMMDD.md`。」
3. 一行：「不要讀 repo 裡的其他檔案，不要上網查。」

審查者只能 Read 和 Write 那兩個檔案。它讀了 slides 或 `sources/`，審查就失效，因為讀者沒有那些。

Claude Code 裡的寫法（claude.ai 的 Agent tool 同理）：

```
Agent(subagent_type="general-purpose", run_in_background=false,
      prompt=<reviewer-prompt.md 全文> + "\n\n審查包在 /home/claude/cs2680/notes/review/l06-pack.md ……")
```

## 3. 讀報告，修 BLOCK

報告格式見 `REVIEW_READABILITY.md`。每個 BLOCK：

- 先看審查者「我讀到的」和你要表達的差在哪。差在哪就是 bug 在哪。
- 修法照 `rewrite-with-example`：接順句子、名詞第一次出現補來歷、表格格子寫成有主詞的完整句。格子放不下就把主張搬回正文，格子只留標籤。
- 保留語放句尾括號：「（Anthropic 一家的經驗，不是對照實驗）」。引用要帶結論：「Anthropic 2026-03 的 harness 實驗：agent 替自己的成果打分時穩定給高分」。
- 不修的 BLOCK，在報告那一條底下寫一句為什麼。

修完跑一次 `check_article.py`、`check_discuss.py`（表格的格子現在也有 lint，見下）。

## 4. 第二輪：只審被標過的單位

```bash
python3 -I tools/review_pack.py docs/lXX.html --chapter i2 i5 > notes/review/lXX-pack2.md
```

再開一個全新的審查者，prompt 多一句：「只審這些定位：[#i2 表2 列2 ‹為什麼抓不到›]、[#i5 ¶4]……其他單位略過。」報告寫到 `lXX-YYYYMMDD-r2.md`。兩輪後還有 BLOCK，留給 James，不開第三輪。

## 5. push 與回報

- `notes/review/` 不 commit（在 `.gitignore`）。
- 照 WORKFLOW D push。
- 回覆 James：貼第一輪的 BLOCK 清單（定位、我讀到的、原因）和每條修了什麼，一條兩行；再貼「最難讀的三處」。他不讀頁面，讀這個。

## 6. 校準：James 說審查沒抓到

James 看頁面還是說看不懂，或抽查發現審查者標錯：

1. 問 checklist 哪一條該抓到。有條目 → 在 `reviewer-prompt.md` 的那一條加一個例子。沒條目 → `REVIEW_READABILITY.md` 加 R9…，`reviewer-prompt.md` 同步。
2. 兩份文件開頭的更新行各加一句。
3. 不要為了這一次去改頁面以外的規則（版面、紅字、章數），那是別的 skill 的事。

## 和 lint 的分工

`check_article.py` 現在也看表格的格子（2026-11-06）：

- 格子裡有外部連結或年月、冒號後不到 12 個字 → warn「引用只有出處」（R5 的機械版）。
- 格子裡「單一公司」「不是對照實驗」等保留語不在括號裡 → warn（R6 的機械版）。

Lint 抓得到的不用等審查者；審查者抓需要判斷的（R1、R2、R4、R7）。
