# CS2680 觀念導讀 — 工作區

發布位置：https://claude.ai/artifact/4rvCbHCpWxAgvro8s1sa6u（site/ 底下的檔案）

## 新的一堂（例：L9）怎麼做

1. 確認 cs2680.com 已公開 slides（`https://cs2680.com/slides/<pdf>`）。
2. 在 `tools/build_index.py` 的 `LECTURES` 加一列；在 `STYLE_ARTICLE.md` 第 9 節的表加一列。
3. 請 Claude 依 `STYLE_ARTICLE.md` 寫 `site/lXX.html`（範本 `site/l02.html`），
   再依 `STYLE_BASIC.md` 寫 `content/lXX-basic.html`，然後：
   ```bash
   python3 -I tools/punct.py site/lXX.html
   python3 -I tools/check_article.py site/lXX.html --pages N --pdf FILE.pdf --fix-time
   python3 -I tools/check_basic.py content/lXX-basic.html lXX
   python3 -I tools/split_discuss.py site/lXX.html content/lXX-basic.html
   python3 -I tools/add_anchors.py site/lXX.html
   python3 -I tools/check_discuss.py site/lXX.html
   python3 -I tools/shot_article.py site/lXX.html      # 看截圖
   python3 -I tools/build_index.py && python3 -I tools/punct.py site/index.html
   python3 -I tools/audit.py
   ```
4. 加上交作業段落：`python3 -I tools/add_submit.py site`（只動還沒有 `#s-submit` 的頁面）。
   同時在 `site/submit.js` 的 `LECTURES` 和 `site/submissions.html` 的表頭加一欄。
5. 發布：index.html 加上改動的 lXX.html，到上面的 artifact。發布時**不要**改 capabilities（省略就沿用）。

## 交作業（讀書會收作業）

- 每一講最後一段「7 · 交作業」是表單：成員貼上對進階題的回答，可附檔；`site/submissions.html` 是收作業總表。
- 邏輯在 `site/submit.js`。資料存在 artifact 的 db：collection `submissions`，每位成員一份 doc（id = user id），
  欄位 `nick`、`updatedAt`，以及每一講一個欄位 `lXX = { text, files:[{id,name,type,size}], updatedAt }`。
- Artifact 宣告的 capabilities（2026-10-16）：
  ```json
  {"db": {"rules": [{"path": "submissions", "read": "view", "write": "owner"},
                    {"path": "submissions/{self}", "write": "interact"}]},
   "user": {"scopes": ["profile"]},
   "assets": {"upload": "interact"},
   "downloads": true}
  ```
  所有登入的人可讀；每個人只能寫自己的 doc；owner（主持人）可以改或刪任何人的。
- 誰能送出：同一個 claude.ai 組織的成員（Contributor 以上），或用 email 邀請為 Editor 的外部成員
  （外部 Editor 只在**沒有**開「任何有連結的人」時有寫入權）。只有 view 權限的人會看到唯讀提示，
  可以用「複製成文字」把答案貼到群組。
- 主持人整理：在總表按「下載全部討論（Markdown）」；或在 Claude Code 用 ArtifactData 讀 `submissions` collection。

## 目錄

- `site/`：發布的頁面（index、l01–l08、submissions、styles.css、app.js、submit.js）
- `content/`：各堂的基礎題片段；l03-part2.html 是 L3 §5–6 的原稿
- `archive/`：舊版逐頁導讀（lXX-cards.html），寫新文章時的事實來源
- `tools/`：驗證與組裝腳本（見上）
- `STYLE_ARTICLE.md`、`STYLE_BASIC.md`：給 agent 的撰寫規範；`STYLE.md` 是舊版，可忽略
