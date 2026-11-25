# L8b：題目與閱讀順暢度 review 之後的審查（2026-11-25）

起因：James「review l8b 題目 跟 閱讀順暢性 要兼顧 文章長度」。主線先自己讀一遍（找重複與接不順的地方）、改正文與題庫，再照 I 審改過的章：導讀一包、第 1–3 章一包，第二輪只審被標過的單位。開卷作答一次（37 題選擇全對，3 題整合要點都答到）。

## 導讀：1 BLOCK、4 NIT

strict（1）：
- ¶3「同一個 container 裡直接互相呼叫，這是函式呼叫」和下一句「同一個程式」：這次沒動的字，11-20 兩輪已過；審查者自己說成立的前提是讀者分不清 container 和程式。

## 第 1–3 章：第一輪 9 BLOCK，第二輪 3 BLOCK

fix（5）：
- [#i1 表1] provider、Core 在解釋之前先用（第一輪 2 條，第二輪換成 controller、Core 2 條）→「元件放在哪裡」移到名字兩列之前，這一列只用前面有的詞（agent loop、執行程式碼的服務），名字留給下面兩列。
- [#i1 ¶5]「只有 microkernel 把 sandbox 交給獨立的服務」和「modular 的 provider 背後也可以是外部服務」衝突（兩輪）→ 小標與圖說改成「規定 sandbox 交給獨立的服務」，段尾寫「不留這個選擇：執行請求一律……」。
- [#i2 圖1 說明]「依原文」指不出對象 →「依 Anthropic 的原文」。
- [#i2 ¶1]（NIT）「看 agent 的數量選架構」補「第 1 章」。

strict（5，都是這次沒動、11-20 審過的字）：
- ¶1 的 memory、tool：讀序在 L2 之後。
- 圖1 的 context、runtime 管 state／scheduling／security：圖照 slides 的元件畫，正文不逐一解釋。
- 「agent 程式」「agent 自己的 process」：和 harness 明顯同指。
- 表2「主要的新代價」monolithic 一格、「modular 是最常見的起點」：常見選法的轉述，第 2 章就是它的反例，不替它補理由。
