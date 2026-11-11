# L6b 可讀性審查的處理紀錄　2026-11-11　checklist v16

第一輪 70 個 BLOCK（tldr 3、第 1 章 20、第 2 章 11、第 3–5 章 27、第 6 章 9）。作者逐條判：**fix 66、strict 2、needs-source 2**。
第二輪只審修過的單位（76 個，第 2 章審了兩次），又標了 21 個 BLOCK；主線修掉大部分，沒修的和只修一半的列在最下面。沒有第三輪。

判定的意思見 `guide/REVIEW_READABILITY.md`〈誰判斷要不要修〉。各輪報告在同一個資料夾（r1-*.md、r2-*.md）。

## 第一輪：第 1、3–6 章逐條

| 定位 | 判定 | 理由 |
|---|---|---|
| #i1 圖1 說明 | fix | R15、R8 都成立：前面一路叫 model，圖和圖說改叫 LLM 沒接；「深紅箭頭」沒說是哪一條。圖說接上兩個名字，並指明是 read 那一條。 |
| #i1 圖1 內容 | fix | R15 成立：圖用 context window，前文叫 context，沒接。R13 連帶處理：前情註把 context window 說成「上限」，和圖的用法不同，在註裡補一句。圖裡的字不動，改 aria-label、圖說（併在上一條）和註。 |
| #i1 ¶2 | strict | token 是一般軟體工程師懂的詞（BRIEF 明列）；它為什麼是成本，同一句的「前情」註有寫，該註另在下面補上計費那一步。 |
| #i1 註 n-context ¶1 | fix | R3 成立：tool 在這一頁第一次出現（前面只說讀檔、改檔、跑指令），system prompt 也沒說是什麼。各補一個括號。（「tool 結果」的括號併在上一條的 edit。） |
| #i1 註 n-context ¶2 | fix | R9 成立：標題是錢，內文只有 token 數，少了「照 token 計費」這一步。 |
| #i1 註 n-context ¶7 | fix | R10、R3 都成立：「常駐」當一類東西用卻沒定義；MEMORY.md 和「索引」沒說是什麼。改成直接寫出意思，檔名接到 Claude Code。 |
| #i1 ¶3 | fix | R2、R13 都成立：前一段講的是「兩個成本」，讀者會把「兩種錯」對回租金和記錯，要到圖 2 才知道是哪兩種。小標不動（側欄用同一句），在同一段補上是哪兩種。 |
| #i1 圖3 內容 | fix | R12、R15 都成立：每題成本三個數字沒有任何一句用到；Lite 和 SWE-ContextBench 的關係沒說。圖說補上成本那一欄說明什麼、Lite 是什麼。 |
| #i1 ¶5 | fix | 四條都成立：AGENTS.md、repo 層的 context file 沒解釋；「常駐的記憶」沒定義；「也一樣」前後不是同一個發現；「非標準」沒說對什麼而言。數字補上標籤（36.36% 的題目）。 |
| #i1 ¶9 | fix | R16 成立：表的列 4（用不到）、列 5（prompt injection）對不回兩條規則，第二條規則在表裡也沒有對應的列。引言改成說明表依的是第一條，另加兩個考量，第二條管的是取回之後。 |
| #i1 表1 列1 ‹記嗎› | fix | R1 成立：¶7 把路徑列在不要記的，code1 過期的正是「在哪個檔案」，這一格卻說可以記 pointer。寫明不記的是內容，pointer 只當線索、一樣會過期、用之前先確認。 |
| #i1 ¶10 | fix | R3 兩條都成立：auto memory 只說了怎麼取捨，沒說是什麼；CLAUDE.md 第一次出現沒解釋。各補一個括號（依本頁第 4 章的表與 Claude Code 文件）。 |
| #i1 圖5 內容 | fix | R3、R13、R1 都成立：precision 在圖之前沒解釋（註 t3 在圖後）；「定期 LLM 回顧」「小 classifier」沒說在做什麼。Precision 補在圖前的 ¶11；兩個做法補在圖說和 aria-label，標本文的整理（slides 只有名稱）。 |
| #i1 ¶12 | fix | R1、R13、R2 都成立：「往右靠」和「沒有規定只准記什麼」並排，讀不出這兩條以外的事誰決定，要到 ¶13 才知道；「用量測決定」沒說量什麼。寫明兩條是下限、其他交給 model 判斷，量的是漏記。 |
| #i1 ¶13 | fix | R15 成立：¶12 預告的是「至少要記什麼／只准記什麼」，這段量的叫「寫死條件／說明用途」，沒接。各接一句。 |
| #i1 ¶17 | fix | R15 成立：同一段混用「圈」和「步」。文章用的單位是步，來源沒說一步是不是一次 model 呼叫，所以不寫等號，這一段統一用「步」。 |
| #i1 ¶18 | fix | R15 成立：〈先看這裡〉講過這個事後補救但沒叫它「整理」。用第 2 章那一節的名字，並接回前面的描述。 |
| #i1 圖7 說明 | fix | R2、R8 都成立：「model 看不到」和事後補救由 model 做衝突，要說是正在做任務的 model；Observe、Encode 不是「改寫 store」。圖說改成五站各做什麼，並順帶分開 Store 這一站和 memory store（圖7 內容的 R15）。 |
| #i1 圖7 內容 | fix | R3、R13 成立：圖上每一站其實有一行問題（值得記嗎、存成什麼……），aria-label 沒寫，所以審查者只看到站名；補進 aria-label。R15（Store 與 memory store）成立，寫在 aria-label 和圖說（上一條的 edit）。 |
| #i1 ¶20 | fix | R9 成立：「沒寫下來就說不出錯在哪一站」少了中間那一步（找錯要拿實際做的事對回規則）。補在紅字後面，同一句。 |
| #i3 ¶1 | fix | R13 成立：「最近」等於「意思像」要到後面的註 t1 才寫，top-k 這個詞也是；把這一句搬進本段。R14 是 NIT（store、context 在 tldr ¶1 解釋過），不處理。 |
| #i3 圖1 說明 | fix | R3、R2 都成立：top-1、top-2 沒接到「取 k 條」；「一樣像」沒寫和誰像；「同一件事」其實是同一個主題、兩個不同的 engine。 |
| #i3 ¶3 | fix | R10、R2 都成立：「訊號」被當成一類東西在數卻沒定義；「位置」是檢索流程裡的哪一步，要看後面的圖才知道。定義是本文的整理，句中已標。 |
| #i3 ¶4 | fix | R3 成立：pgvector 第一次出現沒說是什麼（第 4 章的圖才提到它存向量）。 |
| #i3 ¶5 | fix | R2 成立：這一頁前面沒說頁面分幾段，「第 2 段動手試試」指不出來。 |
| #i3 ¶7 | fix | R15 成立：instruction 檔是新名字，沒接到前面的 CLAUDE.md／每次都載入的那一層。 |
| #i3 表2 列1 | strict | 這張表的 thead 第一欄欄名就是「k」（HTML 是 <th>k</th><th>每圈多送</th><th>50 圈合計</th>），上方公式也寫了 k；審查包把第一欄當列名、沒印它的欄名。R12 條文自己說表格的數字由欄名當標籤。 |
| #i3 ¶10 | fix | R15 成立：這一節開始用「搜尋／search」，沒接到前面的「檢索、一條一條取回」。R11（NIT）順手修：把 1.28 億和 4.2 億的比例算出來，括號才看得出為什麼要提。注意：文章的 search 是比向量還是比文字，sources/l06.md 沒有記，所以只接名字、沒寫機制。 |
| #i3 ¶12 | fix | R16、R2 都成立：主張講跨文件，87% 對 73% 卻是「跨文件」和「要判斷」兩類題合算的，改成明說分不出來，並指出直接的證據是反面那個任務；「24 題」和「兩個任務」的層級接起來（依 sources/l06.md：併購 Q&A 24 題、另一任務）。 |
| #i4 ¶1 | fix | R3 成立：backend 下一段才定義，「獨立一層」要到圖 3 才知道是什麼的一層；在本段各補一個括號。R14 是 NIT，只順手替 policy 補了一句指什麼。 |
| #i4 ¶5 | fix | R15 成立：「Mem0 的競爭者」沒接到 Letta，「這個數字」也指不出是哪一個。R12 的「91.6 沒有單位」要修但缺來源：sources/l06.md 只記「自報 LoCoMo 91.6（原 71.4）」，沒有寫 Mem0 文件用的單位是不是百分比，這一處沒動。 |
| #i4 ¶8 | fix | R9 成立：列在「選檔案的理由」底下，卻沒寫從「policy 才難」到「所以先用檔案」的那一步。 |
| #i4 ¶10 | fix | R9、R2 都成立：少了「下一個 session 拿到的是另一個 sandbox」這一步；括號「查閱它的每個決定」沒有對象。注意：sandbox 不跨 session 保留這一步，是原句「留不到下一個 session」本來就隱含的（段尾已標本文的判斷），sources/l08.md 只記「不再每個 session 先配 container」，沒有直接寫 sandbox 何時收回，請 James 或主 session 對一次 Managed Agents 文件。 |
| #i4 註 n-cc 表1 列2 ‹Claude Code 的答案（2026-11 的文件）› | needs-source | R16 成立，要把四種 type 列出來才數得到。缺：Claude Code 文件裡 auto memory 四種 type 的名稱。sources/l02.md 只記「auto memory 四 type」，l06.md、站內 L2 也都沒有列名字（我記得是 user、feedback、project、reference，但沒有來源可對，不寫）。 |
| #i4 註 n-cc 表1 列5 ‹Claude Code 的答案（2026-11 的文件）› | fix | R3 成立：subagent 在這一頁第一次出現，不是一般工程師都懂的詞；照 L3 的說法補一個括號。 |
| #i4 ¶13 | needs-source | R2 成立，但寫不出來。缺：文章裡做「檢討、提議、重做」這一圈的是誰（寫表的那幾個 agent 之一，還是另開的 agent），提議是交給人核准還是自動套用。sources/l06.md 只記「Reflect–propose–rebuild 幾輪沒說」。 |
| #i4 ¶14 | fix | R9、R15 都成立：SWE-ContextBench 的結果到「所以要自己測」中間少一步；「對的 context／自己挑的 context」和第 1 章的「對的前例摘要」是同一個東西，改回同一個名字，並把「幾個百分點」換成第 1 章的數字（34% 對 26%、22% 對 26%）。 |
| #i4 ¶15 | fix | R16 成立：yaml 裡沒有量 precision 的那一組，改成指回 yaml 真的有的 should_recall 和 budget；例子改的是寫入、yaml 量的是查詢，補一句這組測試量的是哪一端、怎麼分辨兩種原因。 |
| #i5 ¶3 | fix | R16 成立：Cisco 是直接覆寫 MEMORY.md、Microsoft 是叫助理 remember，都看起來就是寫入記憶；四個案例真正共通的是「不是使用者自己決定要記的」，主張改成這一句。套用後請查題庫有沒有引用原句「看起來像寫入記憶」。 |
| #i5 表1 列1 ‹後果與條件› | fix | R2 成立：「沒開內容過濾」沒有主詞。依 sources/l06.md：沒開 Guardrails（Bedrock 的功能）。 |
| #i5 表1 列3 ‹怎麼進 store› | fix | R3 成立：hook、全域 hook 在這一頁第一次出現，沒有解釋。 |
| #i5 表1 列3 ‹後果與條件› | fix | R6 成立：括號改成明說它是在講「使用者同意安裝」這個條件。R4 部分成立：格子開頭補一句後果（攻擊者的內容留下來、之後照樣載入）。攻擊者靠這份記憶具體做到什麼（Cisco 的 payload 效果），sources/l06.md 沒有記，沒寫。 |
| #i5 表1 列4 ‹怎麼進 store› | fix | R15 成立：memory bank 是論文的名字，前後都叫 store，接一次。 |
| #i5 ¶4 | fix | R12、R9 都成立：兩個成功率各量什麼沒寫（論文的 ISR、ASR）；62% 對 6.67% 的倍數沒算；76.8% 和 62% 能不能比沒說；「共用」不是這幾個數字推出來的（它來自表 1 的前提）；「不會因此消失」的「因此」沒有對象。注意：兩個比例的白話定義是照 ISR／ASR 的名稱寫的，sources/l06.md 只記了縮寫和數字，套用前請對一次論文的定義。 |
| #i5 ¶5 | fix | R2 成立：MINJA 從攻擊的名字變成寫 prompt 的主詞，改成「MINJA 論文試過……」。R12 部分修：三個分數改成「135 筆裡的幾筆」，「滿分信任」補上是 LLM 打的信任分數。還缺來源的兩處沒寫死：135 筆是 135 個什麼（惡意查詢還是惡意記憶）、54 筆的分母；sources/l06.md 只有「131/135、0/135、53/135」和「54 筆惡意查詢以滿分信任存入：confidence filter 不是 security filter」。「打信任分數」的機制是從這一句讀出來的，套用前請對一次 2601.05504。 |
| #i5 表2 列5 ‹防線› | fix | R1 成立：「同一輪」可以是一圈、一個 session，第 4 章的「再跑一輪」又是第三個意思。改成 session：表 1 的 Unit 42 是 session 結束時的摘要寫進去的，以 session 為單位才抓得到（本文的防線，本來就是本文的整理）。 |
| #i5 ¶6 | fix | R3 成立：PreToolUse hook 沒解釋（hook 本身已在表 1 列 3 補上）。R7（NIT）順手修：Managed Agents 那一句講的是前面幾站漏掉的後果，不是並列的第二個出處，把「也提醒」改掉。 |
| #i6 表1 列1 ‹哪個決定沒做好› | fix | R4 成立：「query 的說法和記憶不像」是現象，沒寫出對回哪個決定；改成先點出兩個決定（檢索用什麼比對、k 設多大），現象接在後面。 |
| #i6 表1 列4 ‹長什麼樣› | fix | R1 成立：「蓋過」可讀成 store 裡覆蓋或檢索時排前面，和第 3 章表（並列）、本章 ¶2（被當成現在的）三處說法不同；改成和那兩處同一個說法，課程的 override 接一次。 |
| #i6 註 n-sys 標題 | fix | R3 兩條都成立：第 4 章用的名字是「獨立的 memory layer」「memory 系統」，dedicated 沒接過；stack 沒解釋。標題改用頁內已有的名字，課程的名字在註的第一段接一次。 |
| #i6 註 n-sys 表1 列1 ‹核心做法› | fix | R10、R13 成立：「以事實為中心」是課程的分類名（fact-centric），格子裡沒說指什麼，要靠右邊的例子猜；補一句它怎麼存（同一個註 ¶2 已寫 add 用 LLM 抽事實）。 |
| #i6 註 n-sys 表1 列1 ‹例子› | fix | R15 成立：同一句在第 2 章 code1 叫摘要，這裡示範「事實」，兩個名字沒接；在格子裡接一次，標明是本文的對應。 |
| #i6 註 n-sys 表1 列3 ‹核心做法› | fix | R3、R13 成立：三個層名第一次出現沒說各是什麼，memory 又和全文的 memory 同名；在格子裡各接一個中文，並標明 memory 在這裡是層名。只照課程的原話翻（user profile、memory、documents），各層的內容仍由例子那格示範。 |
| #i6 註 n-sys 圖1 說明 | fix | R15 成立：memory management 是新名字，和第 4 章的「獨立的 memory layer」沒接；圖說裡說它指什麼（課程：search and update memories 的那一層），並接回第 4 章的名字。 |
| #i6 註 n-sys 圖1 內容 | fix | R15 成立，已修：aria-label 寫明 stack 是三層的疊法、左邊的 memory management 那層就是獨立的 memory layer。R16 也成立，但只能部分修：svg 的「Letta 內建」照課程 Page 21 原樣（memory management: Mem0, Letta built-in, custom），不是文字錯誤，不改圖；為什麼內建的算獨立一層，notes 和 sources 都沒有，所以只在 aria-label 和圖說標明「投影片沒有說明」，不猜原因。要真的解掉這條，缺：課程 Page 21 的口頭說明或 Letta 的架構文件。 |
| #i6 註 n-metric 表2 列4 ‹規模› | fix | R1 成立：第 1 章和 tldr 寫 99 題，這裡 1,476 題，沒說兩者的關係；依 sources/l06.md（1,100 base 加 376 related；Lite 的 99 題 related task）寫明。 |

## 第一輪：tldr 與第 2 章（主線修）

- tldr ¶2、¶3、¶4：fix。壞的記憶分成記錯、過期、拿錯三種，實驗量的是第三種；時間與來源補了 vLLM → SGLang 的例子；取回補了「算分數、取最高幾條」。
- 第 2 章 11 個：fix。歸納一段（¶9、¶10、code2）重寫；serving、valid time、節點與邊、dreaming 與整理的名字各接一次。
- 第 2 章 ¶15、表 1 列 3：原判 needs-source，開了 Anthropic 原文後修掉（認路的工具沒有顯示那一跳；整理改的是 PokéCenter 位置那一條，「已通過」那條文章沒說）。
- 第 2 章遺忘表：和第 1 章衝突。定為「記錯的先標記失效，永久刪除只給不該存的、使用者要求刪的」，題庫 k26.3、k26.4、k26f 同步。

## 第二輪之後還留著的

| 定位 | 判定 | 說明 |
|---|---|---|
| #i4 註 n-cc 表1 列2 | needs-source | Claude Code auto memory 四種 type 的名稱；要開 code.claude.com/docs/en/memory |
| #i4 ¶5 | needs-source | Letta 實驗給 agent 的那個檔案裡放什麼、Mem0 的 91.6 是不是百分比；要開 Letta 的 blog |
| #i5 表1 列3 ‹後果與條件› | needs-source | Claude Code v2.1.50 移出 system prompt 的是哪一個檔（MEMORY.md 或 CLAUDE.md）；Anthropic 的立場那一句在替什麼打折 |
| #i5 ¶5 | needs-source（部分） | UMass 研究的 54 筆沒有分母；135 筆是 135 個什麼 |
| #i1 ¶12 的 R16 | strict | 「交給 model 判斷」不在圖 5 的五個做法裡：圖是課程的光譜，這一句是本文的補充，已標本文的判斷 |
| #i3 ¶12 的 R16 | strict | 第二個反例講的是 wiki 寫得比原文大，本來就不是跨文件的例子；段落已寫明「另一個任務」 |
| #i6 註 n-sys 圖1 的 Codex | strict | 和 Claude Code 並列在 agent runtime 的例子裡，看得出是同類產品 |
| #i2 ¶9、#i3 ¶1、#i4 ¶1、#i1 圖1 說明 | NIT | 不擋 |

三筆 needs-source 要開外部網頁；這次 session 的網頁抓取要 James 核准，當時沒有回應。
