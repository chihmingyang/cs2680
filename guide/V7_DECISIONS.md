# v7 重組的決定（2026-11-03）

L1–L8 改成 v7 時，每一堂怎麼排份量、補了什麼、刪了什麼。之後要改一堂的章序或把刪掉的東西加回來，先看這裡。排份量用的三個問題：會不會改變讀者的決定？忽略它的代價多大、能不能挽回？能不能從別的想法推出來？再看它多久會過時。各堂外部來源的查證紀錄在 `guide/sources/`（L5 沒有這份紀錄，它的來源在頁面的 fineprint）。

整個站的共同取捨：

- 每堂的主場不重複（L1 目標與 workload、L2 單一 agent 的機制、L3 當使用者怎麼放大、L4 context 與 tool、L5 multi-agent、L6 memory 與可靠性、L7 評估、L8 成本與速度）。別堂的主場用一兩句帶過再連過去。
- 文字裡不寫別堂的章號，寫 L4〈概念名〉，因為章號會變。
- L1–L4 的基礎題已有成員留言，題目不動，只重寫「相關：」，所以這四堂的基礎題仍是帶著問題看 slides。L5–L8 當時 0 則留言，基礎題依新章節重出。
- 問題討論與動手試試裡的舊畫法圖沒有重畫：L1 Q1–Q4 各一張，L2 Q1、Q2、Q5 各一張，L3 Q1、Q2、Q3、Q5 各一張，L4 Q1、Q2、Q4 各一張。

## L1 課程總覽與 AI 系統（10 章，30 分）

- **排法。** 一定要會（1 鏈、2 throughput 是錯的目標、3 人的時間）：最上游，選錯目標白做一季還看不出來，只讀這堂的人也要帶走；鏈排第一，因為目標的理由從它來。整張地圖（4 stack、5 agent 這一層）：決定動哪一層，每層標它動目標的哪一項。底層（6 五個假設、7 時間、8 狀態、9 不確定與故障）：改變排程、KV cache 放置和測試寫法，是 Part II 的起點，但要先有目標才知道為什麼重要。需要時查（10）：九個問題、十個性質、範圍與作業。
- **補。** 真實 trace（Microsoft Azure Research 的 GitHub Copilot trace、TraceLab，都是 2026-06 的資料）：課程對 agent workload 只有定性描述；結論變成 KV cache 的長閒置來自人，不是 tool，該搬的時機是 turn 邊界。人的時間（TraceLab、Faros 2025、METR 2025／2026）：目標式缺這一項，加上後 A、B 兩個系統的差距從 $0.13 變成 $14.94，同一個 batching 有人等和沒人等答案相反；Faros 是觀察資料，METR 2026 自稱不可靠，都寫明；時薪和 GPU 單價是假設。KV cache 的解法（Mooncake、LMCache、DistServe、NVIDIA Dynamo、Yuan 等 2026）：課程只說搬資料是瓶頸。
- **刪。** 舊 2.1 課程範圍收進目錄（成績、遲交不改變讀者的決定；10-28 補密度時才加的），AI 規則進第 3 章，範圍進第 4 章的圖。七個零件、ML 對系統的表縮成兩句（能推出）。Agent／assistant／bot、五步 loop、MHA 等名字、平行化切法收成查閱。MCP、skill 等四個名詞的註與投票、課務刪掉（L2 主場或不改變決定）。

## L2 Claude Code 怎麼運作（10 章，35 分）

- **排法。** 一定要會（1 Loop、2 文字與程式、3 Context）：推不出來，其他判斷都靠它；「要保證的事寫成程式」從舊的末章提到第 2 章，因為錯了沒有警告。要防的（4 權限、5 Prompt injection）：不可挽回，又決定要放多少權。要用時會做（6 記憶、7 Hook、8 Skill、9 MCP、10 Plugin）：前面判斷的實作；hook 先於 skill，因為它落實第 2 章。
- **補。** Sandbox：官方文件說 Bash 規則不是安全邊界，舊頁「一定擋得住」不成立（Anthropic 2025-10 少 84% 提示、2026-03 93% 照准，單一公司）。Injection 的結論：Nasr 等 2025-10，12 個防禦多數被破過 90%，所以不能靠過濾。CLAUDE.md 與 skill 的實驗：ETH 2026（context file 沒有明顯提高成功率、成本多 20% 以上）、Vercel 2026-01（skill 56% 未觸發）。更正舊頁：一個 prompt 是 6 次呼叫 5 次 tool、compaction 的表、`acceptEdits` 含 `rm`、`sed`，`Bash(npm run *)` 在 auto 下會失效。
- **刪。** 經典 agent 圖對應、MCP 六步清單（只是命名，或已變成圖）。RAG 表（L4 主場）。三個時間點的表（推得出來）。API 表、mode 細表、目錄樹、MCP 細節收成查閱。
- **和 slide 相反的地方。** 第 6 章不建議在 CLAUDE.md 寫目錄總覽，只寫地雷（依 ETH 與 `/doctor`）。

## L3 用多個 agent 放大產能（10 章，45 分）

- **排法。** 一定要會（1 三個軸、2 Amdahl、3 人的 review、4 終點與驗證）：決定要不要加 agent，忽略的代價最大又看不見，推不出來，不會過時。要用時會做（5 手動平行、6 subagent、7 team 與 workflow）：決定選哪種，但要先知道上限；指令會過時，收進 snippet。承接 L2（8 Superpowers 與 mattpocock/skills、9 Caveman）：只動一個 agent，可回退；機制能從 L2 推，事實每週變。往前一步（10 dsh-superagent）：前面全部合用，沒有量測，只當設計參考。
- **補。** Review 排隊算式 m ÷ r：課程只說人變 reviewer，沒算上限；本文推導，數字標假設。獨立量測（METR 2025-07、2026-02，Faros 2026-04、09，Anthropic 2026-01）：課程只有 OpenAI 的使用量，結論變成感覺變快不算數、瓶頸在下游。Plugin 的信任邊界：官方文件寫明能用你的權限跑任意程式。
- **刪。** Superpowers 的 skill 清單、session-start 全文、走一遍的例子（圖能推出來）。Karpathy、manifest、scope、27 個 skill、Caveman 零件表降成查閱（不改變決定）。mattpocock 的 setup、to-tickets、grilling 範本、星數（會過時）。
- **保留的（James 要求過）。** `#x1` Caveman 評論查證、`#x2` SWE-Shift 查證、dsh-superagent、Amdahl 兩張圖、`ultracode` 與 `/workflows` 指令、mattpocock 和 Superpowers 並排。Plugin 案例從最前面移到第 8–9 章，仍標承接 L2。

## L4 Context 管理與 tool 設計（10 章，40 分）

- **排法。** 一定要會（1–3 context 的帳）：最上游，每個決定都從這裡來，L2、L3 也要用。要用時會做（4–5 管 context）：會改變做法；有損不可逆的放最後。要用時會做（6–7 設計 tool）：原則可從第 1 章推出，所以不排前；shell 錯了不可逆，排在找、改之前。底層（8–9 search、edit）：現成 harness 通常替你選好，自己寫才要選；semantic search、glob、LSP 的解釋都留。最會過期的（10 prompt）：改錯最便宜、過時最快，過期的判斷直接給。
- **補。** Cache 穩定的排法（Manus 2025-07、OpenAI 2026-01、Anthropic 2026-04，都不是對照實驗）：課程只提一句保留開頭，它卻限制第 4、5 章的做法。倍數的條件（Lewis 2026-08）：課程只列約 2 倍；原論文的對照組放不下就停，262,144 token 時 102 比 101，模型是本地 4-bit。只給 shell 行不行、code execution（Vercel／Braintrust 2026-01、Schmid 2026-09、Anthropic 2025-11）：課程留給作業，只有 GPT-4 的數字。Edit 的第二派：OpenAI apply_patch 沒有行號，所以「search/replace 成了預設」要改寫。
- **刪。** Loop、ReAct、request JSON（和 L2 重複，留一段、一張圖、一個前情註）。平方的算式表（L8 主場）。八招的範例、時間軸、其他五種 tool 收成查閱。LSP 建索引五步與兩張表併成一張圖。Slide 的 token 示意數字（查不到哪個數字對哪一格）。
- **查證時更正舊頁。** 18.0% 是 SWE-bench Lite 300 題；Lewis 改良的是規則縮短，不是 compaction；Drift 不是 Breunig 的分類；few-shot「1 到 3 個」查無來源，改成兩家官方的說法；Boris Cherny 的評估他自己說靠 vibes。

## L5 Multi-agent 架構與溝通（9 章，25 分）

範本，2026-11-03 先改。見 `guide/README.md` 當天的紀錄。

## L6 Agent memory 與可靠性（10 章，30 分）

- **排法。** 一定要會（1–4 長任務靠攔錯）：每個 agent 都碰到，有沒有 memory 都一樣，所以排在 memory 前面；它決定力氣投資在哪裡。一定要會（5–7 記憶讓錯誤活過 run）：錯誤會跨 session，時間與來源沒存就補不回來，最難挽回。要用時會做（8 放在哪裡）：backend 能換，也能從「之後怎麼查」推出來。要防的（9 安全）：代價高、難發現，但要有不可信的輸入才發生。需要時查（10）：都是前面決定沒做好的名字。
- **補。** 算式的前提：課程說要每步都對，Failure as a Process（UCL、南京大學 2026-07）量到成功的 run 有 71% 修過錯，Recovery-Bench（Letta 2025-08）量到接手失敗環境從 26.3% 掉到 11.2%；舊頁「0.95ⁿ 是上界」不嚴格，改掉。檢查要真、要早：ImpossibleBench（CMU、Anthropic 2025-10）量到作弊 76%；第 7 步錯、第 16 步才看到。先用檔案：課程打了問號，Letta 2025-08、SWE-ContextBench 2026-02 都不是對照實驗。記憶中毒：課程只有一列，補 Unit 42、Microsoft、Cisco、MINJA。
- **刪。** 26 種失敗、七個問題收成查閱（只是命名）。Mem0 程式碼刪掉（Mem0 改成只新增，舊頁「合併舊記憶」不成立）。三種 policy 的程式碼換成一張圖。Claude Code 目錄樹刪掉（L2 主場）。650 步的舊圖和算式不符，重畫。

## L7 Agent 評估（10 章，35 分）

- **排法。** 一定要會（1–2）：選 model、能不能上線、分數變高算不算數，三個決定都靠它，推不出來。讀分數時要問的（3–7 指標、雜訊、leakage、grader、飽和）：每章對應一題；錯了當場看不出來，代價大。要用時會做（8–9 建立評估、用評估做決定）：代價最大，但要用前面的結論，所以排在後面。需要時查（10）：八個 benchmark 只是命名，兩個問題就能讀懂。
- **補。** 自己怎麼做 eval（Anthropic 2026-01、Husain 與 Shankar 2025–26、LangChain 2026、Cursor 2026-03，都是單方經驗）：課程只講 benchmark。Grader 的效度（OpenAI 2026 兩度撤回、Epoch 審 24 個 12 個 Flawed、Berkeley RDI 2026-04、METR 2026-03）：課程只有一句，這些改變了結論。Harness 與基礎設施的雜訊（ARC Prize 2026-09 同一個 model 62.7% 到 98.6%、Anthropic 2026-02）。
- **刪。** 八個 benchmark 逐一介紹收成查閱（不改變決定）。五層目標、時代表、早期指標、六維度表收成查閱。教授徵人、指標與難處總表刪掉。
- **和 slide 不同的地方。** 課程說 Terminal-Bench 89 題刪到 66 題是刪飽和題；公告是 3.0 換成新題組 74 題、4.0 刪 8 題，因飽和只有 2 題。本文照公告寫。

## L8 成本、速度與 harness 架構（10 章，35 分）

- **排法。** 一定要會（1 公式與分母、2 重讀、3 prompt cache、4 淨節省）：都改變先動哪裡，算錯了後面每個決定都錯；cache 無損，沒開差 8.5 倍以上，所以排在所有槓桿前。要用時會做（5 少走幾步、6 model／effort／output）：先無損後有損；要不要 LLM 最上游，排第一；output 只佔 8–22%，降到最後。要防的（7 上限）：失敗的錢可佔大半，花了拿不回來。另一本帳（8 時間）：另一個目標，能從重送推出的槓桿併成一張表。底層（9 harness 邊界）：不常改，改起來貴。需要時查（10）：不改變決定，又會過時。
- **補。** 分母與邊際成本（Voss 2026-07）：課程公式只算花費；依它的表，每次便宜三成的 model 每個成功任務貴約 1.9 倍（本文算的比例）。Cache 的帳與 TTL（TraceLab 2026-06、Don't Break the Cache 2026-01；官方定價 cache read 降到 0.05×、0.025×）：課程只給單價和一條建議；結論從先縮 context 改成先保命中。Harness 的三個問題（Managed Agents 2026-04，單一公司）：課程用 agent 數量選架構，這是反例。
- **刪。** 論文逐條說明、speculation 分類、八個 harness 全表收成查閱。單價與 model 價目收進 `#t2`，寫查詢日期。加速四類槓桿的條列換成一張時間 × 錢的表。全班 turn／step 分布只留數字。架構比較表 8 列縮成 5 列。
