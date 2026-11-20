# L8b：標題改成節點之後的整堂重審（2026-11-20）

起因：James 說「把 L8b 完成」。章名與小標照 STYLE_ARTICLE 第 2 節〈標題是節點〉改（第 2、3 章各多切出小標），導讀與第 2、4 章本來就是「改過」，所以整堂重審。

## 導讀：第一輪 13 BLOCK（6 個單位），第二輪 4 BLOCK

fix（12）：
- ¶1 一段九個新名詞 → 刪掉 agent、model、container 的定義（讀序在 L2 之後，2026-11-11 James：前面講過的不必在導讀重複），三個問題各點名 session、container、sandbox。
- ¶1「container／放著使用者資料的環境／同一個地方」三個說法 → 都寫 container。Sandbox 不再叫「隔離環境」（拆之前它讀得到憑證）。
- ¶1 為什麼分不出誰壞、憑證是誰的 → 補「從外面只看得到它沒回應」「使用者交給 agent 的登入憑證」。
- ¶2「L8 算的是錢和時間」→ 刪。補一句「邊界指的是兩塊之間怎麼互相呼叫」，問題改成「用哪一種邊界」。
- ¶3「同一個程式裡，彼此是函式呼叫」例子沒寫 → 改成「直接互相呼叫，這是函式呼叫」；協定那一句補「給好幾個 agent 共用」（¶5 第三題的依據）。
- ¶4「只是其中一題」要讀到 ¶5 才懂 → 小標改成「不先數 agent 有幾個」；「更快」補上和什麼比。
- ¶5 秘密／憑證兩個名字 →「憑證這類秘密」；「基礎設施」→「同一套 tool 和 sandbox」。
- ¶6「設計重心在〈查閱〉」兩種讀法 → 改寫成「整理在最後的〈查閱〉一章」。

strict（3）：
- ¶5 tool 沒解釋（兩輪）：讀序在 L2 之後，導讀最後一句寫明。
- ¶5「每一條邊界各問」而例子整個工具答一次：三題都否時每一條邊界的答案相同，不必逐條列。

## 各章：第一輪 31 BLOCK，第二輪 12 BLOCK（第 2、3 章 0 個）

fix（24）：
- 第 1 章：「決定下一步的迴圈」改用業界的詞 agent loop，並寫明廣義與狹義的 harness；協定寫成「跨 process、跨機器」；「改起來比調參數貴」改成說出原因；1.1 那一段十個名詞搬進一張表（邊界、agent loop 的名字、誰執行程式碼、元件放在哪裡）；圖 1 圖說刪掉「責任移到服務」；補 microservices 這個業界的對應；1.2 補一句 monolithic 為什麼難隔離；圖 3 圖說的「本機」改寫；1.3 補共用、擴展各一句與「看 agent 數量」的理由；表裡 controller 為什麼變複雜。
- 「把邊界推出去」「拆邊界」「跨邊界」三個說法 → 只留「拆出去」，第 2 章章名改成〈拆成獨立服務的理由〉。
- 第 2 章：session 放在「harness 和 sandbox」外面；sandbox 掛了誰回報給誰；圖的「介面」改成「呼叫」（第 1 章的介面是同一個 process 裡的）；圖說補 vault；TTFT 那段寫出是表的哪一列、「文章」是哪一篇。
- 第 3 章：表裡 credential／秘密合成一個說法。
- 查閱：開頭的例子寫出 Codex CLI 問誰、Claude Code 對第一題的答案；「部署環境」刪掉（Codex 的假設是對人的）；目錄表三格補字（IDE 的功能、compaction 之前、context 用到 50%）；補一句表裡的詞出自 L4、L8；收合表：Pi 的小標改成 keep-alive、OpenClaw 的「輪」改成 turn、Hermes 補 write-ahead log 並把「解什麼問題」第二項寫成問題、表後一句改寫。

strict（18）：
- tool、memory、hook、skill、subagent、context、token 第一次出現沒解釋（7 處）：讀序在 L1、L2、L4 之後，導讀寫明；token 是一般工程師的詞。
- 圖 1、圖 3 的字（context 元件在 microkernel 那一欄沒有、runtime 管 scheduling、路徑起點叫 agent，3 處）：圖照來源畫，圖說與表已經對齊名字。
- 收合查閱表的專名與沒寫的機制（Lark grammar、凍結視圖、replacer、wire API、$0.05、snapcompact、TTSR、fence／taint／sentinel、recall、nudge，8 處）：查閱表是需要時再查的目錄，來源沒寫的不補（和 2026-11-16 同一個判斷）。

needs-source（1）：
- oh-my-pi 的「原生 tool」：slides 寫 native tools，沒說是內建還是用 Rust 寫的。照原文留著。

不開第三輪。第二輪的 fix 由主線改完，沒有再審。

## 審查之後的一處刪改

- 收合表 Pi 那一格的「$0.05」拿掉，改成「預期省得夠多時才送」：和 L8 3.4 同一個決定（2026-11-20 James：「拿掉」，slides 只有一句、兩種讀法分不出來），也是第二輪 R12 標的那一處。只刪不補，沒有再開審查，`review_status.py mark` 照記。
