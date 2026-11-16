# L8b 拆出來之後的可讀性審查（2026-11-16）

拆分的取捨在 `guide/V7_DECISIONS.md` 的 L8。搬過去的文字原本在 L8 第 9、10 章審過，但前面八章的上下文沒了，名詞第一次出現的位置跟著移動，所以整堂重審。

## 導讀（l08b-tldr-20261116.md）：3 BLOCK，全修

- ¶2 harness 一下是三樣東西之一、一下是整體 → 問題改成「跑 agent 的系統要拆成哪幾塊」，點明例子的三樣就是三塊。
- ¶3「除錯更難」和例子方向相反 → 代價改成「服務之間多了呼叫和故障，出錯要到好幾個服務找 log」；例子補「也分不出是哪一個壞了」。
- ¶5 和「不看 agent 數量」、和網頁騙憑證的例子衝突 → 第二條改成「agent 有幾個只是其中一題」；筆電工具加「不讀外部網頁也不碰秘密」（第 3 章同步）。
- NIT 順手修：container、prompt injection 補名字，「它」寫明，「更快」說明快在哪裡。
- L8 導讀 ¶6：0 BLOCK、1 NIT（舊文字），不改。

## 各章（l08b-20261116.md）：31 BLOCK

fix（18）：
- 第 1 章：決定下一步的迴圈在三種架構的名字（planner／executor、controller、core runtime）一次對齊；monolithic 改說 process，runtime 只留一個意思；定義「把邊界推出去」；MCP 那句改成「讓 tool 跑在 agent 程式外面的標準協定」，並說明 modular 裡接 MCP 只是那一條邊界是協定；「單一 agent 用 monolithic」改成「常見的選法」，標明第 2 章是反例；表的 monolithic 隔離改「難強制」，和圖一致。
- 第 2 章：圖說補 proxy 做什麼；TTFT 補業界名字。
- 第 3 章：13 秒對毫秒級寫「差上千倍」。
- 第 4 章：開頭段刪掉 Claude Code、Hermes 兩例（名詞太多，表裡都有），補一句接回第 3 章；章名改成「八個 harness 的設計重心」（表寫的是重心，不是假設）；收合註標題「其他七個」；Pi 的 provider 改成 model 供應商、keep-alive 補半句並連 L8；oh-my-pi 的檔案標籤改成內容雜湊（和 t5 同一個詞）、「解什麼問題」改成完整的問題；OpenClaw 的 run 改 turn、compaction 的反向成本寫成具體的問題；Hermes 的「重用；成本；可靠性」寫成三個問題；lost update 接回「互相蓋掉的寫入」。
- 動手試試：code 說明拿掉「團隊共用」（和 shared: no 矛盾）；「假設」改「設計」。

strict（13）：
- tool、memory、context、hook、skill、subagent 第一次出現沒解釋（5 處）：這堂的導讀寫明先讀 L2，站台的讀序也是 L2 在前。
- 收合查閱表裡的 Lark grammar、replacer、wire API、adapter、policy、fence／taint／sentinel 這類專名（6 處）：查閱表是需要時再查的目錄，不是主線。
- 目錄表的 ‹對應› 欄只寫「L2 的機制」「L8〈…〉」（2 處）：欄名是「對應到哪一章」，連結就是答案。

## 第二輪：導讀 1 BLOCK、各章 7 BLOCK，主線修，不開第三輪

- 導讀 ¶5（第 3 章同句）：筆電工具的例子只答了第一題 → 改成三題各有答案（不讀外部網頁也不碰秘密、對話斷了重開就好、只有這一個 agent）。fix。
- 第 1 章 ¶1：harness 一下是整個系統、一下是三塊之一 → 改成「跑 agent 的系統有幾個元件：決定下一步的迴圈（狹義的 harness）…」，第 2 章圖前補一句接回。fix。
- 第 4 章 ¶1：OpenCode 的例子對不到三個問題 → 換成 Claude Code，兩個例子都答第一題，對照更清楚。fix。
- Pi 兩格：keep-alive 為什麼要算錢補半句；「解什麼問題」改寫成問題。fix。prompt cache、wire API、$0.05 是每次送的門檻：查閱表，strict。
- oh-my-pi、OpenClaw 的 turn（L2 的詞）、sentinel 的讀法、taint 標上之後怎樣：查閱表，原文沒寫的不補，strict。
- Hermes「解什麼問題」第一項改成問題，fix；早一點 compaction 為什麼省錢，連 L8 第 4 章就有，strict。
