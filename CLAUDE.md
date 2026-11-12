# CS2680 讀書會站台

動手前先讀 `guide/README.md` 和 `guide/WORKFLOW.md`。

- 這個 repo（`main`）是唯一來源。站台在 `docs/`，push 後 GitHub Pages 自動更新：https://chihmingyang.github.io/cs2680/
- 頁面沒有「問題討論」段，也不開 GitHub 討論串（2026-11-09 James 決定拿掉，舊串已關閉，`discuss.py`、`check_discuss.py` 已刪）。題目改放在每一節後面的小測，規則在 `guide/QUIZ.md`。
- 這個環境不能用 GitHub GraphQL，也不能改 repo 設定；用 `gh api` 的 REST endpoint。
- 舊的 claude.ai artifact 已停用，不要再發布到它。
- L1–L11（L6 另拆出 L6b）都是 v7 依想法重組的版面，三段：核心觀念、動手試試、延伸閱讀，各堂的取捨在 `guide/V7_DECISIONS.md`。新講次或重做一堂 → 照 `.claude/skills/idea-first-lecture/SKILL.md`，一個 session 一堂，或一堂一個 subagent。
- 一堂不綁一份 slides（2026-11-10 James）：依觀念切堂，一份 slides 可以拆成幾堂（L6 可靠性／L6b memory），幾份也可以併成一堂。規則在 STYLE_ARTICLE 第 0 節，做法在 WORKFLOW K。
- 替一堂建題庫（每一節的小測與整合題），或改了某一節要補題 → 照 `.claude/skills/build-quiz/SKILL.md`，一個 session 一堂，先做完那一堂的可讀性審查。
- 紅字（`<strong>`）獨立成一步，可讀性審查過了才標（2026-11-11 James）→ 照 `.claude/skills/mark-red/SKILL.md`；寫作時不放紅字。
- James 貼一段說看不懂、要補案例或圖 → 照 `.claude/skills/rewrite-with-example/SKILL.md`；他轉來一篇評論或文章要查證 → 照 `.claude/skills/fact-check-extension/SKILL.md`。
- James 也會在站台上直接改字（commit 訊息「網頁編輯：…」）或從頁面發問（label `ask` 的 issue），見 `guide/WORKFLOW.md` G。這些 issue 不是討論串，也不是錯誤回報。
- 每一章通過的是哪一版可讀性 checklist，記在 `guide/review_log.tsv`（一章一行：版本、日期、當時文字的 hash）。開工先跑 `python3 -I tools/review_status.py status`：一堂一行，列出幾章是「舊規則」（審過之後 checklist 加了條目）、「改過」（審過之後文字動了）、「沒審過」。Checklist 加一條時，只拿新的那一條去掃「舊規則」的章，不必整份重審（2026-11-13 James）。
- 改內容直接改 HTML、跑檢查、push，在頁面上給他看；不先給純文字版等 OK（他幾乎不看）。
- 回覆 James：重組、取捨這類決定，先講決策的邏輯（為什麼這樣排、補、刪），再列改了什麼、哪裡要他確認（2026-11-03：他要的是邏輯，不只是做了什麼）。小修改只列改了什麼。他的閱讀時間有限，不重貼全文。
