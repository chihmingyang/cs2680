---
page: docs/l06b.html
ref: 8c62ed3c25
chapter: i4
match: 五個訊號，放在不同的位置
rules: R17
in_prompt: no
date: 2026-11-13
---
James 貼了這一段，問：「這不就是 RAG 流程嗎？」接著問：把 RAG 包裝成「五個訊號，放在不同的位置」，可學習性更好還是更差？
更差。內容是 RAG 的 metadata filter → vector search → rerank，整章沒有出現 RAG；讀者要先學「訊號」「位置」兩個詞，再自己認出這是 RAG。
為什麼沒被擋：這一段審過兩輪。11-11 標 R10（「訊號」沒有定義），11-12 標 R3、R13（scope、importance 沒解釋），兩次的修法都是補定義。Checklist 只問「每個詞有沒有定義」，沒有一條問「這件事業界是不是已經有名字」；鐵律「你知道不算」還要審查者不用自己的知識。這個事件加了 R17（鐵律的例外）和 STYLE_ARTICLE 第 1 節〈業界的詞優先〉。
R17 加進 prompt 之後還沒有跑 `review_eval.py`（2026-11-13 的 session 沒有開 subagent）；下一次審查前要跑。
