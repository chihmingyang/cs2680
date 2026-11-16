# R19 第一次全站清理（2026-11-16，checklist v19）

James：「改吧，都改」。`check_article.py` 的 R19 warn 在 L3、L7、L8 抓到 9 處課程內部數據（L11 講課程作業統計，照留）。

## 改法
- L8 `#i5-2`：全班「只有一個 prompt 的 session 佔 68% / 75%」「marathon session」→ 第 2 章的平方：100 turn 的 session 重送的總量將近十個 10 turn session 的十倍。
- L8 `#i5-3`：「全班每個 turn 的 step 數中位數 3 到 4、有的將近 1,000 步」刪掉，只留公開的 TraceLab（8.8 步）。
- L8 `#i8-3`：「所以 Assignment 3 的三個指標要分開看」→「優化時間時，花費要一起量，反過來也一樣」。
- L8 動手試試：刪掉〈Assignment 3 概觀〉（課程競賽的規則、評分、api.cs2680.com，讀者不能參加）；首頁 L8 的簡介拿掉「附 Assignment 3 說明」。
- L7 `#i3-4`：「課程的 Assignment 3 也是這樣評分」→「評一個 coding agent 也該這樣分開量」。
- L3 `#i9-1` 的圖：「依全班 Assignment 1 的資料」→ L8〈三種 token〉的機制例子；名字跟 L8 一致（fresh input → cache write，只改這張圖和它旁邊的表）。比例 83 / 8 / 8 不動，因為後面的敏感度分析建立在它上面。

## 審查
第一輪 4 BLOCK、1 NIT。兩個是改寫帶進來的（「平方」推不出「九倍」；「所以…三個指標」第三個指標沒有來歷），其餘是同一段原本就有的（TraceLab、call 指什麼、15 倍的單位、L3 圖說的單價沒寫）。第二輪 0 BLOCK。第二輪另外點出兩處名字不一致（L8 第 5 章圖的「一次 call 一個動作」、L3 表的「Input 與 cache read」），一起改了。
