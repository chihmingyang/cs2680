# CS2680 導讀頁撰寫規範

你負責 Harvard CS2680(Modern AI Systems: Agents and System Optimizations, Fall 2026)其中一堂課的導讀頁。
成品是一個 HTML 檔:`/home/claude/cs2680/site/lXX.html`。
**範本是 `/home/claude/cs2680/site/l02.html`。先完整讀一遍，結構、class、語氣都照它做。**

不要發布 artifact,不要寄送檔案，不要寫入 memory。只寫你負責的 `lXX.html`(不要改 `styles.css`、`app.js`、`l02.html`)。

## 1. 讀者與目標

- 讀者：軟體工程師，程度從新手到資深都有。課程沒有影片;讀者一邊開原 PDF,一邊讀你的頁面。
- 每一頁 slide 都要有對應說明(可合併相鄰頁)。
- 「深入淺出」= 說清楚**為什麼**、**怎麼運作**,用比喻和具體例子。不是逐句翻譯 slide。
- 讀者偏好：講工具或流程時，要附**具體範例**(檔案內容、實際指令、對話怎麼打)。只有概念，讀者無法實踐。

## 2. 取得 slide 內容

用 WebFetch 抓 PDF(shell 連不到 cs2680.com,只能用 WebFetch)。用這個 prompt:

```
This is a lecture slide deck (PDF). Write page-by-page study notes so a student can follow the deck without opening it. For EVERY page in order, write "=== Page N ===" (N = footer page number) then a concise but complete paraphrase of that slide: its title, every point it makes, and ALL specifics — numbers, percentages, dates, benchmark/system/paper/product names, commands, file names, table rows (as compact rows), chart axes and values, and the example used. For each figure write one line "[Figure: ...]" describing what it shows. Do not skip pages, including optional/appendix pages. If a page has no extractable text, write "=== Page N === (no extractable text)". End with "TOTAL PAGES: X".
```

如果回傳太精簡或漏頁，再用較窄的 prompt 補抓(例如只問某幾頁，或問某張圖的數字)。
頁碼以 PDF 的頁碼為準(footer 頁碼 = PDF 第 N 頁;封面是第 1 頁)。

## 3. 正確性與版權

1. 只寫 slide 上有的事實，加上你**確定正確**的一般知識(例如 git worktree 怎麼運作、HTTP 429 是什麼)。不確定就不寫。
2. 數字、名稱、指令、日期要和 slide 一致。
3. 沒有可擷取文字的頁：寫「圖片頁，沒有可擷取的文字」。可依前後頁加一句提示，寫明「前後頁在講…」。**不要編造圖片內容。**
4. Slide 與官方文件不一致時，兩者都寫:「slide 寫 X;官方文件(2026-10)寫 Y。」
5. 版權：不要逐字翻譯整句 slide。用自己的話解釋。Slide 的英文標題可原樣放在 `.orig`。直接引用原句時 ≤ 15 個英文字，整頁最多一次。
6. 圖表裡的數據(百分比、分數)可以引用，註明是 slide 的數字。

## 4. 語言：繁體中文 + 英文術語，ASD-STE100 約 70%

STE 規則(要遵守):
1. 一句只講一件事。描述句 ≤ 40 字;步驟句 ≤ 30 字(英文詞算 1 字)。
2. 用主動語態。寫「harness 執行 tool call」,不寫「tool call 被 harness 執行」。
3. 步驟用編號清單(`<ol>`),每步以動詞開頭。非順序的項目用 `<ul>`。
4. 一段最多 4 句。
5. 術語固定：同一概念全頁用同一個詞。業界標準術語保留英文:context window、tool call、harness、subagent、prefix cache、KV cache、compaction、prompt injection、benchmark、trajectory、throughput、latency。不要硬翻。第一次出現可以加一句中文說明。
6. 不用成語、誇飾、填充詞(其實、基本上、非常、相當、可以說、事實上、簡單來說)。
7. 不用「不是 X,而是 Y」句型，不用破折號插入語。
8. 「它」「這個」只在指涉很明確時用;不明確就重複名詞。
9. 數字用阿拉伯數字，保留單位。

30% 彈性(可以用):
- 比喻(放在 NOTE callout)。
- 一兩句較長的因果說明。
- 少量口語，讓解釋自然。

範例:
- ✗「基本上 context 其實就是模型的工作記憶，而且它會隨著對話不斷地被塞入越來越多的東西。」
- ✓「Context 是模型的 working memory。每一步都會往 context 加入新內容。」

## 5. 標點與排版

- 中文句子用全形標點:,。、;:?!()「」。
- 中文與英文、數字之間加一個半形空格:「用 Claude Code 執行 3 次」。全形標點旁不加空格。
- 程式碼、指令、路徑、檔名、tool 名稱放 `<code>`。
- HTML 特殊字元要跳脫:`&lt;project&gt;`、`&amp;`。
- 完成後一定跑 `tools/punct.py`(見第 10 節),它會修正中文段落裡殘留的半形標點。

## 6. 頁面結構(照 l02.html)

依序:
1. `<head>`:同 l02(fonts、styles.css、title 改成「LX 中文標題 · CS2680」)。
2. `header.topbar`:brand、`nav.lecnav`(上一堂 / LX / 8 / 下一堂;第一堂與最後一堂只留存在的方向)、`#gist-toggle`。
3. `main.page.gutter[data-lecture="lXX"]`。
4. `header.lecture-head`:eyebrow(`Lecture 0X · 日期 · Part I`)、`h1` 中文標題、`.en-title` 英文原標題、`ul.meta`(Slides 連結、頁數、`<span class="read-time">`)。
5. `section.tldr`「先看這裡」:`.thesis` 1–2 句 + `ul.core` 3–5 條(每條 `<b>粗體重點。</b>` + 1–2 句說明)。
6. `div.layout` > `nav.toc`(`details open` + `ol`,每節一行附頁碼範圍)+ `div.content`。
7. `section.part#s-xxx`:`header.part-head`(`.range`、`h2`、可選 `.lede`)、可選 `figure.diagram`、一張張 `article.slide`。
8. `section.wrap#wrap`:帶走的重點、自我檢查、延伸閱讀、`label.readmark`(`input#read-box`)。
9. `nav.pager`、`p.fineprint`、`<script src="app.js">`。

## 7. Slide 卡片規則

- **每一頁 slide 都要被某張卡片的 `data-pages` 涵蓋，恰好一次，依頁碼順序。**
- 卡片 `id="p{第一頁}"`;tab 連結 = `https://cs2680.com/slides/<pdf>#page={第一頁}`。
- 單頁 tab:`p.<b>07</b>`(兩位數補零)。多頁:`p.<b class="multi">13–15</b>` + `data-pages="13-15"`。
- `h3`:中文短標題 + `<span class="orig">英文原標題</span>`。
- **概念頁**:`.gist`(1–2 句，這頁的重點)+ `.teach`(2–6 句或清單;可加 callout、表格、檔案範例)。
- **課務頁、分隔頁、重複頁、圖片頁、下一堂預告**:用 `article.slide.compact`,只有 `.gist`,一句話。
- 相鄰且講同一件事的頁，可合併成一張卡(例如重複的 slide)。
- Callout 三種，每張卡最多 2 個:
  - `NOTE`:比喻、補充、跨堂連結(「L2 講過…」)。
  - `CAUTION`:常見誤解、風險、陷阱。
  - `EXAMPLE`:具體例子、設定檔、指令、對話範例。
- 檔案範例用 `figure.file` > `figcaption`(檔名)+ `pre > code`。表格用 `div.table-wrap > table`。
- 「只看重點」模式會隱藏所有 `.teach`。所以 `.gist` 自己要能獨立讀懂。

## 8. 長度

- 每堂閱讀時間目標 15–25 分鐘(check 腳本會估算)。
- 核心概念卡:150–350 字。一般卡:60–150 字。Compact 卡：一句。
- 重要的不是字數，而是「讀完能說出為什麼」。

## 9. 圖(每堂 1–2 張 inline SVG)

- 畫**機制**:資料怎麼流、元件怎麼互動、兩個選項差在哪、狀態怎麼轉換。一句話能講完的，不要畫。
- 照 l02 寫法:`figure.diagram > div.scroll > svg[viewBox][role="img"][aria-label]` + `figcaption`(一兩句說明這張圖的重點)。
- 顏色只用 styles.css 的 class:`dg-box`、`dg-box-accent`、`dg-box-soft`、`dg-frame`、`dg-line`、`dg-soft`、`dg-dash`、`dg-accent`、`dg-fill-ink`、`dg-fill-accent`、`dg-fill-soft`、`dg-t`、`dg-tb`、`dg-ts`、`dg-tm`、`dg-ta`。不要寫死顏色，不要在 svg 內放 `<style>`。
- 每個 shape 都要有 fill(class 已提供)。箭頭用 `<marker>`,id 加講次前綴(例 `l5a-ah`),避免和別頁衝突。
- 文字 11–13px,標籤 1–4 個詞。viewBox 寬度約 560–720。對齊格線，間距一致。
- 箭頭要標註意義(「送出 context」「回傳結果」),不要畫沒有標籤的箭頭。

## 10. 驗證(必做)

```bash
cd /home/claude/cs2680
python3 -I tools/punct.py site/lXX.html
python3 -I tools/check.py site/lXX.html --pages N --pdf FILE.pdf --fix-time
python3 -I tools/shot.py site/lXX.html      # 截圖，然後用 Read 看圖
```

- check 必須輸出 `OK`。修到沒有 PROBLEMS。
- 「LONG」句子(> 55 units)要拆短。
- 用 Read 看 shot.py 產生的圖：檢查圖裡文字有沒有重疊、超出邊界、箭頭有沒有接好。發現問題修一次即可。

## 11. 各堂資料

| 檔案 | PDF | 頁數 | 日期 | 英文標題 | 中文標題(建議) |
|---|---|---|---|---|---|
| l01.html | 1_intro.pdf | 52 | 2026-09-02 | Course overview and logistics | 課程總覽與 AI 系統 |
| l02.html | 2_agent_use_1.pdf | 60 | 2026-09-09 | Agents use I: How Claude Code Works | Claude Code 怎麼運作(範本，已完成) |
| l03.html | 3_agent_use_2.pdf | 83 | 2026-09-14 | Agents use II: 100x Engineer with Multi-agents | 用多個 agent 放大產能 |
| l04.html | 4_agent_design_1.pdf | 58 | 2026-09-16 | Agents design I: context management and tool design | Context 管理與 tool 設計 |
| l05.html | 5_agent_design_2.pdf | 49 | 2026-09-23 | Agents design II: multi-agent architecture, coordination, and communication | Multi-agent 架構與溝通 |
| l06.html | 6_agent_design_3.pdf | 33 | 2026-09-28 | Agents design III: agent memory and reliability | Agent memory 與可靠性 |
| l07.html | 7_agent_design_4.pdf | 38 | 2026-09-30 | Agent design IV: agent evaluation | Agent 評估 |
| l08.html | 8_agent_design_5.pdf(+ 8_assignment3.pdf) | 61(+6) | 2026-10-07 | Advanced agent design I: Cost and performance | 成本、速度與 harness 架構 |

上一堂/下一堂:l01 沒有上一堂(pager 左邊改成「回總覽」連到 `index.html`);l08 沒有下一堂(pager 右邊改成「回總覽」)。pager 標籤用上表的中文標題。

各堂延伸閱讀(課程網站列出的):
- L1:課程網站 https://cs2680.com ;背景書:Operating Systems: Three Easy Pieces https://pages.cs.wisc.edu/~remzi/OSTEP/ ;Machine Learning Systems https://mlsysbook.ai ;Foundations of Large Language Models https://arxiv.org/abs/2501.09223 ;The Little Book of Deep Learning https://fleuret.org/francois/lbdl.html
- L3:Claude Code agent teams https://code.claude.com/docs/en/agent-teams ;Software is changing (again) https://www.youtube.com/watch?v=LCEmiRjPEtQ ;Research acceleration: The view inside OpenAI https://openai.com/index/research-acceleration-view-inside-openai/ ;更多 https://cs2680.com/readings/sep-14.html
- L4:ReAct https://arxiv.org/abs/2210.03629 ;A practical guide to building agents https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents ;LLM Powered Autonomous Agents https://lilianweng.github.io/posts/2023-06-23-agent ;更多 https://cs2680.com/readings/sep-16.html
- L5:How we built our multi-agent research system https://www.anthropic.com/engineering/multi-agent-research-system ;Towards a science of scaling agent systems https://arxiv.org/pdf/2512.08296 ;Don't build multi-agents https://cognition.com/blog/dont-build-multi-agents ;更多 https://cs2680.com/readings/sep-23.html
- L6:Where LLM agents fail https://arxiv.org/abs/2509.25370 ;MemGPT https://arxiv.org/abs/2310.08560 ;更多 https://cs2680.com/readings/sep-28.html
- L7:課程筆記 Agent evaluation and benchmarks https://cs2680.com/notes/agent-evaluation.html
- L8:課程筆記 Cost-effective agents https://cs2680.com/notes/cost-effective-agents.html

(連結文字用你自己確認過的標題;不確定標題時，用課程網站上的短名稱。)

## 12. 已驗證的 Claude Code 事實(官方文件，2026-10)

需要具體範例時，優先用這些(已核對):

**Subagent**
- 檔案位置:`.claude/agents/`(專案)、`~/.claude/agents/`(使用者)。同名時優先序:managed settings > `--agents` CLI flag > 專案 > 使用者 > plugin。
- Frontmatter 只有 `name`、`description` 必填。其他:`tools`、`disallowedTools`、`model`(`sonnet`、`opus`、`haiku`、`fable`、完整 model ID、`inherit`)、`permissionMode`、`maxTurns`、`skills`、`mcpServers`、`hooks`、`memory`、`background`、`omitClaudeMd`、`effort`、`isolation: worktree`、`color`、`initialPrompt`。
- 範例:
  ```markdown
  ---
  name: code-reviewer
  description: Reviews code for quality and best practices
  tools: Read, Glob, Grep
  model: sonnet
  ---

  You are a code reviewer. When invoked, analyze the code and provide
  specific, actionable feedback on quality, security, and best practices.
  ```
- 內建:Explore(唯讀搜尋，thoroughness 有 quick / medium / very thorough)、Plan(plan mode 用的唯讀研究)、general-purpose(所有 tool)。
- 明確呼叫：自然語言點名;`@agent-<name>`;`claude --agent code-reviewer`(整個 session 用這個 agent)。
- 巢狀：預設最多在主對話下 3 層，可用環境變數 `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` 調整;同時執行的 subagent 預設上限 20(`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`)。

**Hooks**
- 常用事件:`SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PostToolUse`、`Stop`、`SubagentStart`、`SubagentStop`、`PreCompact`、`PostCompact`、`SessionEnd`(官方共列出 30 個以上)。
- 設定位置:`~/.claude/settings.json`、`.claude/settings.json`、`.claude/settings.local.json`、managed policy、plugin 的 `hooks/hooks.json`、skill 或 subagent 的 frontmatter。
- 設定格式見 l02 p.43。PreToolUse 擋下 tool call:exit code 2(stderr 當原因),或輸出 JSON `hookSpecificOutput.permissionDecision: "deny"`。
- Hook 從 stdin 收到 JSON,常見欄位:`session_id`、`cwd`、`hook_event_name`;PreToolUse 另有 `tool_name`、`tool_input`。

**Skills**
- 位置:`~/.claude/skills/<name>/SKILL.md`、`.claude/skills/<name>/SKILL.md`、plugin 的 `skills/<name>/SKILL.md`(呼叫時是 `/plugin-name:skill-name`)。
- Frontmatter:`name`、`description`、`disable-model-invocation`、`user-invocable`、`allowed-tools`、`model`、`effort`、`context: fork`、`paths` 等。`$ARGUMENTS` 會換成 `/skill-name` 後面的參數。

**Memory**
- CLAUDE.md 四層與 `.claude/rules/` 的 `paths:` 見 l02。Auto memory 在 `~/.claude/projects/<project>/memory/`,MEMORY.md 前 200 行或 25KB 每次載入。

**未驗證的功能**(L3 會遇到:worktree 的 `claude -w`、agent teams、`/goal`、`/loop`、dynamic workflow / ultracode):先用 WebFetch 查 `https://code.claude.com/docs/en/` 對應頁面(例如 `agent-teams`、`common-workflows`)再給範例。查不到就用 slide 的寫法，並寫「slide 的示範:…」。
