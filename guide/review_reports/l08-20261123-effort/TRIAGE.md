# L8 effort／cache 修正（2026-11-23）的可讀性審查 triage

範圍：#i3 查閱〈七種會打斷 cache 的動作〉表第 5 列兩格；#i6〈Per-turn effort〉¶12–¶14 與 code1。共 6 個單位，兩輪。

## 第一輪：5 BLOCK
- 表1 列5 ‹為什麼斷›（R2/R3/R13/R9/R15/R18）：fix。刪掉「實驗功能」與 per-message effort 的推測（推測留在 sources/l08.md），「新 model 也一樣」改成「新 model 改 effort 也會斷」。
- 表1 列5 ‹怎麼避開›（R1/R15）：fix。不寫「system 訊息」，改寫「request 最上層的 effort 設定不動，在 messages 尾端加一則只帶 effort 的訊息」。
- ¶13（R15/R1/R9）：fix。這是內容錯誤，不只是措辭：per-message effort 要等下一則有新輸入的 user 訊息才生效，只有 tool_result 的訊息不算，所以是按 turn 換，不是按步驟換。小標改成 Per-turn effort，¶12 寫明單位是 turn，步驟級的分工交給 subagent。
- ¶14（R1/R2）：fix。寫明加在「你這則訊息的文字最後」。
- code1（R16）：fix。effort 訊息移到 turn 2 的 user 訊息之後，註解標 turn 1／turn 2。

## 第二輪：1 BLOCK
- ¶12（R9/R2）：fix。補 API 規則（只裝 tool 結果的訊息不算新輸入，所以要等下一則訊息才生效）；「上一節的 routing」改「本章開頭的 routing」。已達兩輪上限，沒有開第三輪。
