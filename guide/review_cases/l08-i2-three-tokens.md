---
page: docs/l08.html
ref: ebb41031cb
chapter: i2
match: 三種 token 的量大約是 cache read 100
rules: R18
in_prompt: yes
date: 2026-11-16
---
James 貼了〈三種 token：量和單價方向相反〉這一段，說：「你這裡一堆數字，可讀性會好嗎？你思考一下人類的認知 model，這樣能有效吸收？如果數字不是重點，你乾脆做圖不是嗎」
一段裡第一次出現的名詞有七個（provider、prefix cache、cache read、fresh input、cache write、output、decode），再並列兩組共六個數字。讀者要自己在腦中排成 3 × 2 的表，才看得出「方向相反」。
為什麼沒被擋：這是審查造成的。11-13 精簡時拿掉了量 × 單價的表，審查者標 R12（數字沒有標籤），作者的修法是把標籤一個一個補進句子；第二輪每個數字都有標籤，就過了。Checklist 沒有一條問「一段裝得下嗎」。這個事件加了 R18，STYLE_ARTICLE〈精簡〉第 4 點改成「數字進圖，句子講結論」。
修法：數字全部搬進一張圖（一列一種 token，三欄：量、單價、花的錢），正文只留機制和「cache read 單價最低，仍佔約八成」。下面的 TraceLab 換算（58%、26%、41%、36%）同樣改成一條堆疊長條。
