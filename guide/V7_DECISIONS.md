# v7 重組的決定（2026-11-03）

L1–L8 改成 v7 時，每一堂怎麼排份量、補了什麼、刪了什麼。之後要改一堂的章序或把刪掉的東西加回來，先看這裡。排份量用的三個問題：會不會改變讀者的決定？忽略它的代價多大、能不能挽回？能不能從別的想法推出來？再看它多久會過時。各堂外部來源的查證紀錄在 `guide/sources/`（L5 沒有這份紀錄，它的來源在頁面的 fineprint）。

整個站的共同取捨：

- 每堂的主場不重複（L1 目標與 workload、L2 單一 agent 的機制、L3 當使用者怎麼放大、L4 context 與 tool、L5 multi-agent、L6 可靠性、L6b memory（2026-11-10 拆開）、L7 評估、L8 成本與速度）。別堂的主場用一兩句帶過再連過去。
- 文字裡不寫別堂的章號，寫 L4〈概念名〉，因為章號會變。
- L1–L4 的基礎題已有成員留言，題目不動，只重寫「相關：」，所以這四堂的基礎題仍是帶著問題看 slides。L5–L8 當時 0 則留言，基礎題依新章節重出。
- 問題討論與動手試試裡的舊畫法圖沒有重畫：L1 Q1–Q4 各一張，L2 Q1、Q2、Q5 各一張，L3 Q1、Q2、Q3、Q5 各一張，L4 Q1、Q2、Q4 各一張。

## L1 課程總覽與 AI 系統（10 章，40 分）

- **排法。** 一定要會（1 鏈、2 throughput 是錯的目標、3 人的時間）：最上游，選錯目標白做一季還看不出來，只讀這堂的人也要帶走；鏈排第一，因為目標的理由從它來。整張地圖（4 stack、5 agent 這一層）：決定動哪一層，每層標它動目標的哪一項。底層（6 五個假設、7 時間、8 狀態、9 不確定與故障）：改變排程、KV cache 放置和測試寫法，是 Part II 的起點，但要先有目標才知道為什麼重要。需要時查（10）：九個問題、十個性質、範圍與作業。
- **補。** 真實 trace（Microsoft Azure Research 的 GitHub Copilot trace、TraceLab，都是 2026-06 的資料）：課程對 agent workload 只有定性描述；結論變成 KV cache 的長閒置來自人，不是 tool，該搬的時機是 turn 邊界。人的時間（TraceLab、Faros 2025、METR 2025／2026）：目標式缺這一項，加上後 A、B 兩個系統的差距從 $0.13 變成 $14.94，同一個 batching 有人等和沒人等答案相反；Faros 是觀察資料，METR 2026 自稱不可靠，都寫明；時薪和 GPU 單價是假設。KV cache 的解法（Mooncake、LMCache、DistServe、NVIDIA Dynamo、Yuan 等 2026）：課程只說搬資料是瓶頸。
- **刪。** 舊 2.1 課程範圍收進目錄（成績、遲交不改變讀者的決定；10-28 補密度時才加的），AI 規則進第 3 章，範圍進第 4 章的圖。七個零件、ML 對系統的表縮成兩句（能推出）。Agent／assistant／bot、五步 loop、MHA 等名字、平行化切法收成查閱。MCP、skill 等四個名詞的註與投票、課務刪掉（L2 主場或不改變決定）。
- **可讀性審查（2026-11-06～07，WORKFLOW I）。** 第一輪 76 BLOCK、8 NIT，作者修完；第二輪剩 3 BLOCK（tokens/sec 繞路例子沒說甲為什麼每秒比較多、Autellix 的 head-of-line blocking 和 4–15 倍少一步、temperature 0 那格少「前兩名很接近」），主線修，沒有審第三輪。順手更正：第 9 章「第 7 位小數」改成「第 7 位有效數字」（基礎題第 2 題的答案沒動，留給 James）；第 10 章 A3、A5 的指標照 slide；第 4 章連到 L8 的錨點改成 `#i3`；第 4 章圖補 communication。
- **tldr 的 Copilot 數字（2026-11-07）。** James 問「聊天是 1 次、750 token、105 token」在寫什麼、為什麼審查會過。改成只留撐論點的兩個數字：agent 一段對話呼叫 model 15 次、每次送進 68K token 的前文，約是聊天一問一答的 90 倍；聊天的 750／105 不是 Copilot trace 的數字，是論文引用的更早研究（ModServe、DynamoLLM），舊寫法放在「GitHub Copilot 線上流量的紀錄裡」底下，讀起來像 Copilot Chat，現在用括號標出。輸出 247／105 token 留在第 1 章的長條圖。同一天照新規則把 tldr 單獨審（審查者只拿 tldr 和頁首），四條都改：thesis 說出 tokens/sec 變好時任務哪裡不一定變好，並把每個成功任務的成本寫成「連失敗的嘗試一起付的錢，攤到每個做成的任務上」（照第 2 章的定義）；第 1 條補上每次都把前面的對話和工具輸出整段重送、中間結果等工具時也佔著 GPU 記憶體；第 2 條寫明人的時間是等結果和驗結果、有人等用小 batch、沒人等用大 batch（照第 3 章的算例）；第 3 條把五個假設寫成「跑 LLM 時都反過來了」的五項，指到第 6 章。第 1、3 條現在是 3 句；James 同日決定放寬 tldr 的句數（可讀性優先於長度，STYLE 第 5 節開頭），所以不再壓回 2 句。

## L2 Claude Code 怎麼運作（10 章，45 分）

- **排法。** 一定要會（1 Loop、2 文字與程式、3 Context）：推不出來，其他判斷都靠它；「要保證的事寫成程式」從舊的末章提到第 2 章，因為錯了沒有警告。要防的（4 權限、5 Prompt injection）：不可挽回，又決定要放多少權。要用時會做（6 記憶、7 Hook、8 Skill、9 MCP、10 Plugin）：前面判斷的實作；hook 先於 skill，因為它落實第 2 章。
- **補。** Sandbox：官方文件說 Bash 規則不是安全邊界，舊頁「一定擋得住」不成立（Anthropic 2025-10 少 84% 提示、2026-03 93% 照准，單一公司）。Injection 的結論：Nasr 等 2025-10，12 個防禦多數被破過 90%，所以不能靠過濾。CLAUDE.md 與 skill 的實驗：ETH 2026（context file 沒有明顯提高成功率、成本多 20% 以上）、Vercel 2026-01（skill 56% 未觸發）。更正舊頁：一個 prompt 是 6 次呼叫 5 次 tool、compaction 的表、`acceptEdits` 含 `rm`、`sed`，`Bash(npm run *)` 在 auto 下會失效。
- **刪。** 經典 agent 圖對應、MCP 六步清單（只是命名，或已變成圖）。RAG 表（L4 主場）。三個時間點的表（推得出來）。API 表、mode 細表、目錄樹、MCP 細節收成查閱。
- **和 slide 相反的地方。** 第 6 章不建議在 CLAUDE.md 寫目錄總覽，只寫地雷（依 ETH 與 `/doctor`）。
- **可讀性審查（2026-11-06～07）。** 第一輪 48 BLOCK、8 NIT；第二輪剩 4 BLOCK，主線修：圖 3 第五問看檔名、寫 API 這類看任務的答「否」；Guardrails 與 ETH 相同的是「用心寫的內容沒有換到更高的解題率」；索引和 skill 差在 model 要做的決定變小、沒有消失；marketplace 在圖說第一次出現就解釋。順手更正：Check Point 的信任對話框原本就有；刪掉「gh 常常更省 token」；/doctor 改成「方向一致」；Vercel 56% 照原文；plan mode 標籤改「不改原始碼」。

## L3 用多個 agent 放大產能（10 章，55 分）

- **排法。** 一定要會（1 三個軸、2 Amdahl、3 人的 review、4 終點與驗證）：決定要不要加 agent，忽略的代價最大又看不見，推不出來，不會過時。要用時會做（5 手動平行、6 subagent、7 team 與 workflow）：決定選哪種，但要先知道上限；指令會過時，收進 snippet。承接 L2（8 Superpowers 與 mattpocock/skills、9 Caveman）：只動一個 agent，可回退；機制能從 L2 推，事實每週變。往前一步（10 dsh-superagent）：前面全部合用，沒有量測，只當設計參考。
- **補。** Review 排隊算式 m ÷ r：課程只說人變 reviewer，沒算上限；本文推導，數字標假設。獨立量測（METR 2025-07、2026-02，Faros 2026-04、09，Anthropic 2026-01）：課程只有 OpenAI 的使用量，結論變成感覺變快不算數、瓶頸在下游。Plugin 的信任邊界：官方文件寫明能用你的權限跑任意程式。
- **刪。** Superpowers 的 skill 清單、session-start 全文、走一遍的例子（圖能推出來）。Karpathy、manifest、scope、27 個 skill、Caveman 零件表降成查閱（不改變決定）。mattpocock 的 setup、to-tickets、grilling 範本、星數（會過時）。
- **保留的（James 要求過）。** `#x1` Caveman 評論查證、`#x2` SWE-Shift 查證、dsh-superagent、Amdahl 兩張圖、`ultracode` 與 `/workflows` 指令、mattpocock 和 Superpowers 並排。Plugin 案例從最前面移到第 8–9 章，仍標承接 L2。
- **可讀性審查（2026-11-06～07）。** 第一輪 97 BLOCK、15 NIT；第二輪剩 8 BLOCK、3 NIT，主線修。順手更正：.claude-plugin/ 也可能有 marketplace.json；push 被拒不等於被認領；subagent「主要」買到專注（slide 是 throughput and focus；h3 與目錄的章名沒改，留給 James）；F03、3.14 倍、2–3 層、auto-merge 帳號、第 10 章的協調方式（訂閱加轉述）、workflow 重跑範圍照原文。Superpowers 2026-11-03 稍晚發了 v7.0.2，頁面仍以 v7.0.1 為準。

## L4 Context 管理與 tool 設計（10 章，50 分）

- **排法。** 一定要會（1–3 context 的帳）：最上游，每個決定都從這裡來，L2、L3 也要用。要用時會做（4–5 管 context）：會改變做法；有損不可逆的放最後。要用時會做（6–7 設計 tool）：原則可從第 1 章推出，所以不排前；shell 錯了不可逆，排在找、改之前。底層（8–9 search、edit）：現成 harness 通常替你選好，自己寫才要選；semantic search、glob、LSP 的解釋都留。最會過期的（10 prompt）：改錯最便宜、過時最快，過期的判斷直接給。
- **補。** Cache 穩定的排法（Manus 2025-07、OpenAI 2026-01、Anthropic 2026-04，都不是對照實驗）：課程只提一句保留開頭，它卻限制第 4、5 章的做法。倍數的條件（Lewis 2026-08）：課程只列約 2 倍；原論文的對照組放不下就停，262,144 token 時 102 比 101，模型是本地 4-bit。只給 shell 行不行、code execution（Vercel／Braintrust 2026-01、Schmid 2026-09、Anthropic 2025-11）：課程留給作業，只有 GPT-4 的數字。Edit 的第二派：OpenAI apply_patch 沒有行號，所以「search/replace 成了預設」要改寫。
- **刪。** Loop、ReAct、request JSON（和 L2 重複，留一段、一張圖、一個前情註）。平方的算式表（L8 主場）。八招的範例、時間軸、其他五種 tool 收成查閱。LSP 建索引五步與兩張表併成一張圖。Slide 的 token 示意數字（查不到哪個數字對哪一格）。
- **查證時更正舊頁。** 18.0% 是 SWE-bench Lite 300 題；Lewis 改良的是規則縮短，不是 compaction；Drift 不是 Breunig 的分類；few-shot「1 到 3 個」查無來源，改成兩家官方的說法；Boris Cherny 的評估他自己說靠 vibes。
- **可讀性審查（2026-11-06～07）。** 第一輪 68 BLOCK、8 NIT；第二輪剩 8 BLOCK、1 NIT，主線修：四種策略的順序改成「model 失去多少」（admission 沒看過所以沒有當時那一份）；context reset 寫出比較的結論（Sonnet 4.5 的 context anxiety，Opus 4.5 之後拿掉）；Confusion 的 stub 寫出機制並引 tool search 的準確率；repo 大時兩邊都變貴的推論；Cursor 的 % 原文沒說是百分點還是相對值。順手更正：五種找法；五條原則的分組標成本文的整理；冪等的反例換成 SMTP；55% 是 slide 的數字；索引的查詢成本不是零。

## L5 Multi-agent 架構與溝通（9 章，30 分）

範本，2026-11-03 先改。見 `guide/README.md` 當天的紀錄。
- **可讀性審查（2026-11-06～07）。** 第一輪 37 BLOCK、7 NIT；第二輪剩 4 BLOCK、1 NIT，主線修：260 種設定不是 5×6×3（每家不只一個 model）；Anthropic 研究系統那格不用 lead（和第 9 章的中層 lead 撞名）；「換不到東西」加上不需要平行、不需要隔開權限的前提；LLM Tagging 的「少約 5%」照原文、寫明原文沒說是哪一種。順手更正：17.2 倍的架構是「結果只合成一份、中間沒有人檢查」（第 5 章與基礎題第 4 題答案）。

## L6 Agent memory 與可靠性（10 章，40 分）

- **拆成兩堂（2026-11-10）。** James：「把 Agent Memory、Agent reliability 分成兩個章節，以觀念去 split 而不是 slide 去 split，未來 lesson 的對應跟課程投影片不需要綁死一對一對應。」切的依據是觀念 DAG：可靠性的四個節點（error-compounding、verification-loop、checkpoint-budget、failure-layers）和 memory 的五個節點（persistent-text、valid-time-provenance、memory-retrieval、memory-backend、memory-poisoning）之間沒有一條「要先懂」的邊；memory 接在 L2 的 persistent text、L4 的 context 上，可靠性接在 agent loop、sampling 上。舊頁 tldr 用「錯誤會活過一個 run」把兩半綁在一起，那是敘事的橋，不是理解上的前置，所以留成兩堂之間的過場句。
  - L6〈Agent 可靠性〉（`l06.html`，5 章 20 分）：原第 1–4 章不動，第 5 章是目錄（只留 26 種 run 的失敗）。保留 `l06` 這個 key 與 `#i1`–`#i4` 錨點：別頁帶錨點連進 L6 的 17 條連結有 14 條指可靠性。
  - L6b〈Agent memory〉（`l06b.html`，6 章 20 分）：原第 5–9 章重編 1–5，第 6 章是目錄（八種記憶失敗、七個設計問題、系統、指標）。第 1 章開頭改寫：不再說「前四章的錯誤」，改說 L6 講的錯誤停在一個 run 裡，並在本頁重新解釋 run、session、harness。
  - 新寫的只有兩頁的 tldr、lede、目錄章開頭、兩半之間的三句過場；L6 第 3 章「context 是什麼」原本指 memory 那章的註，改指 L4〈Context 的成本〉。動手試試（compound.py、run 預算 → L6；memory 記錄 → L6b）、延伸閱讀（失敗模式 4 篇 → L6；State 與記憶 2 篇 → L6b）、fineprint 的來源依觀念分開。
  - 編號用 L6b，不把 L7–L11 往後推：2026-10-21 定過講次編號、檔名不跟著改；成員的已讀與作答紀錄都綁在 key 上。
  - **2026-11-10 補 Anthropic〈The components of agent memory〉（2026-11-06）**：James 轉來，目的是「掌握底層的 agent 開發邏輯」，改法交給 Claude 判斷。不另開一章（章號、錨點、題庫都不動），補成五個小節：1 章〈往右靠，用「說明用途」來做〉`#i1-5`、2 章〈記憶疊成四層〉`#i2-6` 與〈Session 之間的整理〉`#i2-7`、3 章〈整理過的頁面要配搜尋〉`#i3-5`、4 章〈多個 agent 一起寫〉`#i4-6`；tldr 加一句事後補救；延伸閱讀加一篇「推薦」（不在教授清單，標本文補的）。取捨：(1) 原本第 1 章的 policy 把 observe 寫死成「使用者糾正時才寫」，和文章量到的結果衝突，改成兩層：值不值得記寫用途、交給 model；後果收不回來的邊界（外部內容、scope、刪除）由程式擋。(2) 主線是「transcripts 是 log，上面三層是 view」：這是本文的類比，用來說明為什麼原始紀錄不能省。(3) 文章的人類睡眠類比、Opus 5.5 破關、wiki 成長的頁數不寫。(4) 數字都是 Anthropic 量自家 model，多數沒交代跑幾次，頁面每處都標。來源細節在 `sources/l06.md`。
  - 可讀性審查只審新寫的定位（兩頁 tldr、L6 第 3 章兩段與第 5 章、L6b 第 1 章開頭與第 6 章）。第一輪 BLOCK：L6 tldr 4、章 5，L6b tldr 4、章 4；第二輪 4／1／4／2，主線修完，沒有第三輪。修的方向：兩頁開頭都先定義 agent 是 model 加一層叫 harness 的程式（原本兩頁各說各的，審查者分不出 agent 和 harness）；88% 寫出 5% × 5% 那一步，10 步寫出比的是什麼並指到第 3 章的圖；L6b 的邊界統一成 session（context 在一個 session 裡會留著，run 結束不會清掉）；SWE-ContextBench 寫明「配好的那份」與挑中率，才撐得起「拿錯的記憶比沒有更糟」；Memory 錯誤那一列寫明改到的是舊路徑新建的檔案、為什麼沒有錯誤訊息；七個設計問題與 checklist 七站逐一對上。L6 第 3 章〈存什麼〉順手補上「沒驗證就存為什麼沒用」，Recovery-Bench 寫明它量的是接手失敗的環境。
  - 舊連結：`l06.html` 帶一張 `#moved` 表，68 個搬走的 id 轉到 `l06b.html` 的新 id。`#i5` 例外：它現在是 L6 的目錄章，舊的 `l06.html#i5`（要不要記）會停在 L6。站內三條已改指 L6b。

- **排法。** 一定要會（1–4 長任務靠攔錯）：每個 agent 都碰到，有沒有 memory 都一樣，所以排在 memory 前面；它決定力氣投資在哪裡。一定要會（5–7 記憶讓錯誤活過 run）：錯誤會跨 session，時間與來源沒存就補不回來，最難挽回。要用時會做（8 放在哪裡）：backend 能換，也能從「之後怎麼查」推出來。要防的（9 安全）：代價高、難發現，但要有不可信的輸入才發生。需要時查（10）：都是前面決定沒做好的名字。
- **補。** 算式的前提：課程說要每步都對，Failure as a Process（UCL、南京大學 2026-07）量到成功的 run 有 71% 修過錯，Recovery-Bench（Letta 2025-08）量到接手失敗環境從 26.3% 掉到 11.2%；舊頁「0.95ⁿ 是上界」不嚴格，改掉。檢查要真、要早：ImpossibleBench（CMU、Anthropic 2025-10）量到作弊 76%；第 7 步錯、第 16 步才看到。先用檔案：課程打了問號，Letta 2025-08、SWE-ContextBench 2026-02 都不是對照實驗。記憶中毒：課程只有一列，補 Unit 42、Microsoft、Cisco、MINJA。
- **補（2026-11-09）。** 第 2 章末尾加本文延伸 `#x5`〈檢查會往兩個方向錯〉：James 問 detect 有沒有考慮 false negative。算式裡的漏抓就是 1 − detect，沒算的是誤判（把做對的步驟判成錯）。延伸寫四種結果、FP／FN 的名字看把什麼當 positive（和 L7 grader 的叫法相反，所以用漏抓、誤判）、加上 false_alarm 的算式、誤判碰到的步驟是漏抓的 19 倍（p ÷ (1 − p)）、四種檢查的橫條圖（調嚴要少誤判才有用；重試修不好時調嚴反而差）、flaky test 與 ImpossibleBench 是誤判的實例、漏抓的錯會被當成成功交出去。正文第 2 段加一句指過去，「檢查就不是越嚴越好」標紅（加了這句後 i2 的紅字目標從 3 變 4）。都是本文的推算，沒有外部來源。可讀性審查只審新寫的單位：第一輪 9 BLOCK、1 NIT（係數怎麼來、「碰到 19 倍」和「傷害一樣大」怎麼抵銷、「寬鬆」沒定義、圖的數字沒標籤、重做不再檢查的假設、26% 和九成對不起來），第二輪 4 BLOCK，主線修完、沒有第三輪；其中標題那一條是 `review_pack.py` 把頁面上的標籤和標題印成一串，已改工具。
- **刪。** 26 種失敗、七個問題收成查閱（只是命名）。Mem0 程式碼刪掉（Mem0 改成只新增，舊頁「合併舊記憶」不成立）。三種 policy 的程式碼換成一張圖。Claude Code 目錄樹刪掉（L2 主場）。650 步的舊圖和算式不符，重畫。
- **可讀性審查（2026-11-06～07）。** 第一輪 39 BLOCK、8 NIT；第二輪剩 5 BLOCK，主線修：tldr 的 88% 要「重試一次」；context 在表 2 第一次出現就解釋；寫出 git 為什麼沒有 /rewind 的三個限制、context 怎麼另外退；圖 4 的段尾驗證和每步檢查分開；system prompt 的「份量」指向表 2 列 3。順手更正：Cisco 那列的記憶檔仍會載入、只是移出 system prompt；表 2 的機制是共用 context，不是同一個 model；topic 檔一條記憶一個檔；記憶 checklist 是七站。

## L7 Agent 評估（10 章，45 分）

- **排法。** 一定要會（1–2）：選 model、能不能上線、分數變高算不算數，三個決定都靠它，推不出來。讀分數時要問的（3–7 指標、雜訊、leakage、grader、飽和）：每章對應一題；錯了當場看不出來，代價大。要用時會做（8–9 建立評估、用評估做決定）：代價最大，但要用前面的結論，所以排在後面。需要時查（10）：八個 benchmark 只是命名，兩個問題就能讀懂。
- **補。** 自己怎麼做 eval（Anthropic 2026-01、Husain 與 Shankar 2025–26、LangChain 2026、Cursor 2026-03，都是單方經驗）：課程只講 benchmark。Grader 的效度（OpenAI 2026 兩度撤回、Epoch 審 24 個 12 個 Flawed、Berkeley RDI 2026-04、METR 2026-03）：課程只有一句，這些改變了結論。Harness 與基礎設施的雜訊（ARC Prize 2026-09 同一個 model 62.7% 到 98.6%、Anthropic 2026-02）。
- **刪。** 八個 benchmark 逐一介紹收成查閱（不改變決定）。五層目標、時代表、早期指標、六維度表收成查閱。教授徵人、指標與難處總表刪掉。
- **和 slide 不同的地方。** 課程說 Terminal-Bench 89 題刪到 66 題是刪飽和題；公告是 3.0 換成新題組 74 題、4.0 刪 8 題，因飽和只有 2 題。本文照公告寫。
- **可讀性審查（2026-11-06～07）。** 第一輪 76 BLOCK、8 NIT；第二輪剩 6 BLOCK、2 NIT，主線修：「隔壁欄」改成 shell 欄；τ-bench 只有部分題目檢查回覆（ABC 附錄 E.2）；LiveCodeBench 補一句；Go module 偽造達成什麼標成本文的推論；METR 的比例改成「一半到三分之二不會 merge」；圖 1 的兩條 agent 類沒有基準線，「最快」改寫。順手更正：5.2%、前 50 名 24% 名次不對、UI-TARS 少算 28 個百分點、ARC-AGI-3 的 effort、四組對照第二列、兩列改「還沒飽和」、OSWorld 2.1 抽查結果。

## L8 成本、速度與 harness 架構（10 章，40 分）

- **排法。** 一定要會（1 公式與分母、2 重讀、3 prompt cache、4 淨節省）：都改變先動哪裡，算錯了後面每個決定都錯；cache 無損，沒開差 8.5 倍以上，所以排在所有槓桿前。要用時會做（5 少走幾步、6 model／effort／output）：先無損後有損；要不要 LLM 最上游，排第一；output 只佔 8–22%，降到最後。要防的（7 上限）：失敗的錢可佔大半，花了拿不回來。另一本帳（8 時間）：另一個目標，能從重送推出的槓桿併成一張表。底層（9 harness 邊界）：不常改，改起來貴。需要時查（10）：不改變決定，又會過時。
- **補。** 分母與邊際成本（Voss 2026-07）：課程公式只算花費；依它的表，每次便宜三成的 model 每個成功任務貴約 1.9 倍（本文算的比例）。Cache 的帳與 TTL（TraceLab 2026-06、Don't Break the Cache 2026-01；官方定價 cache read 降到 0.05×、0.025×）：課程只給單價和一條建議；結論從先縮 context 改成先保命中。Harness 的三個問題（Managed Agents 2026-04，單一公司）：課程用 agent 數量選架構，這是反例。
- **刪。** 論文逐條說明、speculation 分類、八個 harness 全表收成查閱。單價與 model 價目收進 `#t2`，寫查詢日期。加速四類槓桿的條列換成一張時間 × 錢的表。全班 turn／step 分布只留數字。架構比較表 8 列縮成 5 列。
- **可讀性審查（2026-11-06～07）。** 第一輪 65 BLOCK、8 NIT；第二輪剩 3 BLOCK，主線修：gpt-oss-120b 便宜的機制寫成「花費 ÷ 成功次數」（難題較貴一句標成本文的推論）；decode 為什麼最貴寫出 prefill 的對照；effort 那格的四個例外寫明是 Claude Code 文件列的、文件沒說怎麼做到。順手更正：compaction 算例的摘要大小統一成 3K；5 分鐘內換回 model 舊 cache 還能讀；Hermes 的 nudge；cache 命中「通常快」。

## 新講次（2026-11-06 起）

L9–L11 沒有舊頁面，直接寫成 v7。三堂由三個 subagent 同時寫（簡報 `.claude/skills/idea-first-lecture/new-lecture-brief.md`），主場表多了三列：L9 model 的帳、L10 GPU 的帳、L11 用 agent 的證據與習慣。新講次的基礎題與進階題都連到本頁的章，不寫 slide 頁碼。

## L9 LLM 的結構與 serving 的帳（10 章，40 分）

- **排法。** 一定要會（1 request 的一生、2 骨架與參數、3 attention 與 KV cache、4 三個數字）：每個 serving 與買 GPU 的決定都從這裡算，算錯就是買錯硬體、答應錯的 SLA，難挽回也推不出來；章內照依賴排，先兩段，再零件，最後算帳。選 model 時看的（5 MoE、6 改 KV 的架構、7 現在的 model、8 tokenizer）：機制能從第 4 章推，但要有數字才能選；model 名會過時，原則寫正文、表格標查詢日。自己架時會調的（9 sampling）：改錯便宜、託管 model 已經不給調。需要時查（10）：looped、diffusion、MTP 能從三個數字推出，也還不是主流。
- **補。** 每 token 的 KV（第 7 章）：課程只算 Llama 3 70B；六個 open-weight model 依官方 config.json 算出 24 到 320 KiB，差 13 倍，結論變成「參數多的 model 可能放得下更多長 context 的人」（計算，不是量測）。中文的 token 數（第 8 章）：slides 的「3–4 字元一個 token」是英文；本文用六個 tokenizer 實測本站 50,315 個繁體字，0.71–0.91 token／字（GPT-4 的 cl100k 是 1.36），繁體比同段簡體多 6–23%，和 DeepSeek、Qwen 的官方經驗值與 Bailong（2024）一致。Token 預算併進第 4 章，不標本文補的（方法來自延伸閱讀的 kipply）。
- **刪。** RMSNorm、pre-norm、√dk 收成名詞註。690 GB 的 S、FlashAttention、roofline 一句帶過連 L10。Continuous batching 只寫 slides 講的（11/04 的主場）。Temperature 0 不保證相同連 L1，不重講。
- **更正 slides。** 320 KB 實際是 327,680 byte，所以 64 個 request 是 1,819 GB，不是 1,779 GB（頁面註明）；「Serving is hard」的 token ID 是示意，改用 Llama 3 tokenizer 的實際輸出。
- **可讀性審查（push 前，WORKFLOW I）。** 第一輪 33 BLOCK：tldr 的名詞（KV cache、context、GQA 這類先用後講）、head 在第 3 章先用後講、linear attention 的 S 和第 3 章的分數矩陣同名、表格格子沒回答欄名；也抓到一個錯：Qwen3-Next 那格 3.3 GB 應是 3.2 GB。第二輪剩 2 BLOCK、1 NIT，主線修，沒有審第三輪。

## L10 GPU 入門與 kernel 最佳化（10 章，55 分）

- **兩份 deck 一篇。** 10/21 的 2a 與 11/02 的 2b 封面是同一堂，James 定合成一篇。
- **排法。** 一定要會（1 GPU 的設計、2 roofline、3 decode、4 量測）：瓶頸在 bytes 還是 FLOP，決定之後每種改法有沒有用；拿 nvidia-smi 做容量規劃會買錯 GPU，代價大又看不出來；第 1 章是第一次接觸 GPU 的讀者的前提。底層（5 晶片裡面）：解釋 peak 只屬於矩陣乘法、頻寬靠 bytes in flight，不改變多數人的決定，但第 7、8 章要用；規格會過時，收成查閱。要用時會做（6 程式、7 kernel 之內、8 kernel 之間）：只有要寫或選 kernel 的人用到；先講抽象層回答要不要往下寫，手法的名字會過時，結論收成「選有這些手法的 engine」。要防的（9 AI 寫的 kernel、10 一張卡之外）：錯了事後才發現，代價大。
- **補。** AI 寫的 kernel 怎麼量錯（第 9 章整章）：課程只有一句提醒；METR、Sakana 與 robust-kbench（加速從 3.13x 降到 1.49x）、CUDA-L1（另開 stream 騙過計時）、KernelBench v0.1、Hacker-fixer loop（2025-02 到 2026-06），收成五個驗收檢查，第一個是 roofline 的 speed of light。MoE 把 batch 分給各 expert（第 3 章一節）：slides 的 batching 結論只對 dense 成立；DeepSeek 2025-02 的推論系統說明（EP144）與 2025-12 的 A100 量測。
- **刪。** 課務；GPU 世代、各精度 ridge 表、TMA／TMEM、其他晶片、編譯到 SASS 收成查閱（會過時）；最佳化清單併成第 7 章開頭的四個目標；batching、quantization、speculative decoding 各一句（後面的講次）。
- **更正 slides。** Little's law 那頁是 4 KB 不是 512 B；A100 到 Rubin 的頻寬是 10.8 倍不是約 9 倍，BF16 的 ridge 也沒有一路右移；MFU 22% 的分母是 FP8 peak，換成 BF16 是 43%；故障原因的 8%／17%／30% 用 Llama 3 論文 Table 5 確認。
- **待決定。** 55 分鐘比其他堂長（可讀性審查補了約 20 個名詞的解釋，從 50 分變 55 分）；要縮的話，第 5 章可以整章改成查閱（約省 4 分）。
- **可讀性審查（push 前，WORKFLOW I）。** 第一輪 71 BLOCK：tldr 約 20 個先用後講的名詞、查閱表的硬體名詞與「–」、幾個對不起來的數字（Llama 3 故障 58.7% 對圖上加起來的 55.9%，差的是沒畫出的兩個小類；NVLink 900 是兩個方向合計，每個方向 450；EP144 × 2 = 288 是 256 個 expert 加 32 份備份）。作者另外更正兩處沒被標的：Llama 3 8B 的 GQA 是 g = 4，不是 8；slides 列的是三個 GPU 丟時間的地方，第四個是人的時間。第二輪剩 12 BLOCK、1 NIT，主線修，沒有審第三輪。

## L11 作業回饋與 agent 的十個陷阱（10 章，35 分）

- **排法。** 一定要會（1 數據、2 開工前定義做完、3 收工時看證據）：最上游，每個任務都碰到，錯了沒有警告；學生自己抓到的錯從 61% 掉到 33%。比較版本時（4 實驗、5 harness 會變）：第三份作業最多人踩，錯了白做好幾天、結論相反，但只在比較時發生。要防的（6 破壞性指令、7 secrets）：拿不回來，但設定一次就生效，所以排在每天的習慣前面（依「能不能挽回」，和 slides 的 P 編號不同）。每天的習慣（8 session、9 執行環境）：能挽回，代價是時間；P9 併進第 8 章，P10 與派工成本併進第 9 章。需要時查（10）：P1–P10 一覽、數據的讀法、學生想要的功能對到現在的做法。機制在 Part I 講過的都只帶一兩句再連過去。
- **補。** Sonar 2026-01（1,100 多位開發者，96% 不完全信任、48% 每次都檢查）：課程只有學生的資料，補上後結論從「要小心」變成「檢查要做成機制」（廠商的自陳調查）。GitGuardian 2026 與官方文件：Claude Code 署名的 commit 外洩率 3.2% 對全體 1.5%，transcript 是明文、history.jsonl 不會自動清（相關分析，不是對照實驗）。Bash 優先的公開紀錄：GitHub issue #87575、#87971 是使用者回報，沒有官方回覆；加上 checkpointing 文件，補出第二個後果：綁在 Edit／Write 的安全網會安靜失效，真正的 checkpoint 是 git。
- **刪。** 對應不清楚的數字不用（permission mode 比例、失敗類型比例、兩個中位數、P8 的順序）；疊改動與只看一次 run 只用總表的數字。學生的願望清單收進目錄；flag 名、model 範圍、流程圖收成查閱（會過時）；課務刪掉。
- **語氣。** 第 5 章寫成「slides 的結論是 Anthropic 刻意做的實驗」，公開紀錄另段寫，不推測原因。
- **延伸閱讀。** 課程沒有列 readings；五篇取自 9/9、9/30、10/14 的官方清單，rg-intro 寫明。OWASP 的 PDF 抓不到，只列選讀。
- **可讀性審查（push 前，WORKFLOW I）。** 第一輪 21 BLOCK，最大的一個是結構問題：第 4、5 章都叫 harness，一個是學生交出去的程式，一個是 Claude Code。作者查了作業說明：排行榜跑的是學生自己的 agent，Claude Code 的 flag 不會直接改 v8、v9 的分數，原文暗示會，是錯的；第 5 章改成「Claude Code：它也會在你腳下變」，只對經過 Claude Code 量出的數字成立。第二輪剩 5 BLOCK、3 NIT，主線修，沒有審第三輪。
