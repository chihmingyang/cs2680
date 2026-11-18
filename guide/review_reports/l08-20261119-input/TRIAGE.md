# L8 `#i2-2` 三種 token 為什麼沒有 input：審查分流（2026-11-19）

起因：James 問「cost 為什麼只看 cache read、cache write、output，應該還有 input token」。正文沒交代 base input 去哪了。只審這次動到的單位。

第一輪 2 BLOCK、1 NIT：
- `#i2 ¶4` fix（改做法）：原本把「沒開 cache 時 input 照原價收、開了之後接近 0」加在三種 token 之前，讀者還沒看到三種就先讀到一種不列的。改成搬到圖後面另起一段（現在的 `#i2 ¶6`），`¶4` 還原。
- `#i2 圖2 說明` 不修：R12／R18「100、1、0.2 要照位置對回 200K、2K、0.4K」。這句不是這次改的，留到 `#i2` 下次整章送審。
- `#i2 圖2 內容` NIT（長條沒描述）：不修，同上。

第二輪 1 BLOCK，作者修，沒有開第三輪（skill 規定最多兩輪）：
- `#i2 ¶6` fix：R15「input」沒接回 context → 補「Input 就是這一步送給 model 的整個 context」；R2「這筆帳」指不出來 → 改成「cache write 為什麼比原價高，在第 3 章〈Hit rate〉」。

多了一段，`#i2` 的題庫定位 `¶6` 以後各加 1（25 處）。`#i2` 沒有 `review_status.py mark`：第二輪的修改沒再審，而且這一章 11-19 有 James 的網頁編輯還沒送審。
