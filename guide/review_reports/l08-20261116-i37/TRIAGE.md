# L8 `#i3-7` 單價從哪裡來：審查分流（2026-11-16）

第一輪 12 BLOCK，全部 fix：`#i2-2` 補 prefill／decode 的名字與「讀權重的次數不同」；141 GB → 68 token/s 的算式搬進 code block；KV cache 接回 3.1 的「中間結果」，定義 K、V、attention；batching 和 Batch API 分開；「人」統一成 request；ridge point 的 200 改從兩個上限相除推出；「不到四分之一」改「四分之一左右」；FP8 那句刪掉；Batch API 補「平常湊不滿」的前提；fast mode 不再推「貴 2 倍」。

第二輪 9 BLOCK，作者修，沒有開第三輪（skill 規定最多兩輪）：
- fix：decode 的「一輪」和 agent 的「一步」分開；68 標成 batch 1；GPU 記憶體 282 GB、KV 每 token 320 KB、43 萬、29 毫秒都搬進 code block；141 GFLOP 寫出 705 億 × 2 次運算；「每一層」「下一個字」拿掉；ridge point 補 roofline 的名字；throughput 補名字；fast mode 寫出 68 ÷ 34 = 2，所以 2.5 倍要靠別的手法；fast mode 移到 Batch API 前面，Batch API 的「留餘裕」指回去。
- fix（改論點）：5 倍對不上長 context → 改寫成「單價不隨 context 長度變，5 倍是平均後的定價」；刪掉長 prompt output 加價那句（GPT-5.6 Sol 的 input 加得更多，撐不起論點）。
- 沒審過第三輪，所以這一章沒有 `review_status.py mark`。

## James 的決定（2026-11-16 下午，「你決定」）

- 「output 約 5 倍是平均後的定價」保留，句首標成「本文的解讀」，因為 provider 沒公開成本。
- 不開第三輪審查（skill 上限兩輪）。`#i3` 不 mark；下次這一章再改正文時，連同 `#i3-7` 一起送審。
