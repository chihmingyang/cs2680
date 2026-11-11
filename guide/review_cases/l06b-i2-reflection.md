---
page: docs/l06b.html
ref: 75ec560dd5
chapter: i2
match: 歸納是風險最高的寫入 | 少了上面 snippet 裡的 evidence
rules: R10 R15 R16
in_prompt: no
date: 2026-11-11
---
James 請 Claude 評這一段的可讀性，並問怎麼減少「讀不順」的 feedback 次數。
「歸納」是課程的分類名，沒有定義，下一句換成 Reflection，沒說是同一件事；寫入者有 model、系統、agent 三個名字；「觀察」和 snippet 的 `ep-12` 沒對上。
下一段的 Harvard 例子看不出哪一句是推測；內文說關鍵是 `evidence` 和 `confidence`，snippet 的註解強調的卻是 `kind`。
為什麼沒被擋：這一章 11-10 才用 v14、`--prefix` 的包審過兩輪（補 Anthropic 五小節那次），這段仍留著。11-11 拿同一包、同一份舊 prompt 重審，審查者標了這兩個單位（R10、R9、R1）。所以不是審查者抓不到；是 11-10 那次的 BLOCK 沒有落到這一段（報告沒有 commit，查不到是沒標還是沒修）。這個事件加了 R15、R16、測試題和 `review_log.tsv`。
