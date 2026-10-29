# CS2680 讀書會站台

動手前先讀 `guide/README.md` 和 `guide/WORKFLOW.md`。

- 這個 repo（`main`）是唯一來源。站台在 `docs/`，push 後 GitHub Pages 自動更新：https://chihmingyang.github.io/cs2680/
- 討論在 Issues，每一堂一串、只放基礎題；進階題（每堂最多 3 題）留在頁面。開串、寫連結、匯出討論都用 `tools/discuss.py`。
- 這個環境不能用 GitHub GraphQL，也不能改 repo 設定；用 `gh api` 的 REST endpoint。
- 舊的 claude.ai artifact 已停用，不要再發布到它。
- James 貼一段說看不懂、要補案例或圖 → 照 `.claude/skills/rewrite-with-example/SKILL.md`；他轉來一篇評論或文章要查證 → 照 `.claude/skills/fact-check-extension/SKILL.md`。
- 改內容直接改 HTML、跑檢查、push，在頁面上給他看；不先給純文字版等 OK（他幾乎不看）。
- 回覆 James：只列改了什麼、哪裡要他確認。他的閱讀時間有限。
