# CS2680 讀書會站台

動手前先讀 `guide/README.md` 和 `guide/WORKFLOW.md`。

- 這個 repo（`main`）是唯一來源。站台在 `docs/`，push 後 GitHub Pages 自動更新：https://chihmingyang.github.io/cs2680/
- 討論在 Issues，每一堂一串、只放基礎題；進階題（每堂最多 3 題）留在頁面。開串、寫連結、匯出討論都用 `tools/discuss.py`。
- 這個環境不能用 GitHub GraphQL，也不能改 repo 設定；用 `gh api` 的 REST endpoint。
- 舊的 claude.ai artifact 已停用，不要再發布到它。
- L1–L8 都已是 v7 依想法重組的版面（2026-11-03），各堂的取捨在 `guide/V7_DECISIONS.md`。新講次或重做一堂 → 照 `.claude/skills/idea-first-lecture/SKILL.md`，一個 session 一堂，或一堂一個 subagent。
- James 貼一段說看不懂、要補案例或圖 → 照 `.claude/skills/rewrite-with-example/SKILL.md`；他轉來一篇評論或文章要查證 → 照 `.claude/skills/fact-check-extension/SKILL.md`。
- James 也會在站台上直接改字（commit 訊息「網頁編輯：…」）或從頁面發問（label `ask` 的 issue），見 `guide/WORKFLOW.md` G。這些 issue 不是討論串，也不是錯誤回報。
- 改內容直接改 HTML、跑檢查、push，在頁面上給他看；不先給純文字版等 OK（他幾乎不看）。
- 回覆 James：重組、取捨這類決定，先講決策的邏輯（為什麼這樣排、補、刪），再列改了什麼、哪裡要他確認（2026-11-03：他要的是邏輯，不只是做了什麼）。小修改只列改了什麼。他的閱讀時間有限，不重貼全文。
