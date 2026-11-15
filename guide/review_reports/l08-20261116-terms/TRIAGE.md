# L8 第 2、3 章 2026-11-16：一個觀念一個英文名字之後的審查（checklist v18）

James 2026-11-16：「provider、prefix cache、cache read、fresh input、cache write、output、decode 這些都用英文會不會比較好？」L8 整頁的中文別名換成一個英文名字（對照在 STYLE_ARTICLE 第 1 節），審第 2、3 章和〈先看這裡〉那一段。

## 第一輪：9 BLOCK、5 NIT
共同的根：頁面上剩兩組英文名字，hit／miss（讀不讀得到 cache）和 read／write（帳單上的那一列），第 2 章後段才接起來。修法照 readability-review〈修 BLOCK〉的順序，先刪再搬：
- 刪：`#i2-2` 的 prompt caching（第二個名字）、`#i3-1` 的 KV cache 和 Anthropic、`usage` 那段的第四種 token（「標記的位置」）、單價註的「快取」和 implicit caching、「第 2 章的圖用 0.1×」。
- 搬：hit ↔ read、miss ↔ write 的對應寫進圖的列說明（「cache hit：直接讀留下來的結果」）。
- 補：〈先看這裡〉定義 cache miss、保住 cache hit 的兩個條件；`#i3-2` 在 hit rate 第一次出現的地方定義它。
- NIT：「第 1 章的六個乘數」、hit rate 那段不再把 read 和 miss 交叉配對、TTL 圖說「照 cache read 收」。n-prefill 放在第 3 章的位置沒有動。

## 第二輪：3 BLOCK、1 NIT，兩個是第一輪的修法帶進來的
- `#i2-3` R1：把 hit/miss 定義清楚之後，「cache miss」包含新內容，TraceLab 那張圖卻用它只指過期重算的那一份。fix：圖和正文改成「重算的舊內容」，cache miss 不再有窄的意思。
- `#i2-2` R18（四個新名詞，壓在門檻上）：fix，對應句搬進圖，這一段只剩 provider、prefix cache。
- `#i3-1` R18（Claude API 變成第一次出現）：strict。Claude API 是讀者已知的詞（STYLE_ARTICLE 第 1 節〈讀者已知的詞〉有 API，Claude Code 前面已經出現），後三個欄位名都有括號接回已知的東西。
- NIT：右邊那一欄寫出「多了七成多」。

## 給下次
改名詞是全頁的事：刪掉一句裡的名字，那個名字的「第一次出現」就移到下一個地方，要跟著看那裡有沒有定義。這次第二輪的 BLOCK 有兩個是這樣來的。
