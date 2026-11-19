---
page: docs/l08.html
ref: 34d5125
chapter: i3
match: 內容相同，位元組不同
rules: R4 R9
in_prompt: no
date: 2026-11-19
---
James 沒有說看不懂，是直接改稿（bd76879）：查閱〈七種會打斷 cache 的動作〉的表，「JSON key 順序不固定」那一列的「為什麼斷」只有「內容相同，位元組不同」十個字。他改寫成一段機制：JSON 不保證 object 的 key 順序（RFC 8259 把 object 定義成 unordered collection），所以 {"a":1,"b":2} 和 {"b":2,"a":1} 語意相等，serializer 可以用任何順序輸出。

格子回答了「結果是什麼」，沒有回答欄名問的「為什麼」：讀者不知道 key 的順序為什麼會不固定。這一章 11-16、11-19 各審過一次（v19），這一格都過了。
