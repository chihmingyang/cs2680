# L10 2026-11-13 整堂重審（checklist v16）

James 2026-11-13 說「yes」：L10 前一天照〈章的順序〉重排後，整堂上次是 checklist v8 審的，這次全部重審。i4、i5 的第一輪用 `../l10-20261112/l10-20261112.md`；其餘三份是今天的第一輪（A：i1–i3，B：i6–i8，C：i9–i10）。

## 第一輪：112 BLOCK（A 21、B 34、C 22、i4–i5 35），全部 fix
多數是 R3：名詞先用後講（decode、prefill、batch、KV cache、kernel、FMA、tile、stream、agent、KernelBench……），補在第一次出現的地方。其餘是少一步的推理（R9）、同一件事兩個名字（R15）、數字沒標籤（R12）。沒有判 strict。

順手更正的事實：
- 第 2 章規格表的 A100 頻寬 2.0 → 2.04，和查閱表、正文的 153（312 ÷ 2.04）一致。
- 第 3 章前情與第 10 章：Llama 3 70B 每個 token 的 KV cache 是 320 KiB（327,680 bytes），不是 320 KB；10.7 GB 是照 KiB 算的。
- 第 8 章 split-KV 圖：部分結果寫成 (m, ℓ, o)，和第 7 章未正規化的 o 同名。
- 第 9 章：「改掉的計時函式」不在五個案例裡，刪掉；「直接呼叫 torch、寫了 CUDA 卻沒呼叫、縮小 batch」另成第五類，小標改成〈漏洞集中在五個地方〉。

## 第二輪：16 BLOCK（A 6、i4–i5 3、B 4、C 3），全部 fix，沒有開第三輪
三處第二輪審查者指出是事實或推理問題，不只是字：
- 第 2 章〈趨勢〉：低精度讓 kernel 掉到斜坡上，原文沒說清楚。若每個數字都變小，intensity 和 ridge 一起加倍、位置不變；實際上是只有 weights 變小、activation 和 KV cache 還是 BF16，才掉下去。照這個改寫。
- 第 2 章查閱〈二十年的 NVIDIA GPU〉：「43,000 倍大半來自精度」改成算出來的拆法：同樣 FP32 約 200 倍、Tensor Core 加 FP4 約 200 倍；同精度的 ridge 只右移約 2 倍（G80 約 4、B300 約 9）。B300 FP32 約 75 TFLOP/s 是由查閱表 B200 的 FP32 ridge 9.4 × 8 TB/s 推的，同代同值。
- 第 5 章 MBU：原文說 decode 的 MFU「只會看到雜訊」，審查者指出同一張 GPU 上 MFU、MBU 都正比於 tokens/s。改成：MFU 低看不出離上限多遠，MBU 量的才是真正的瓶頸、看得出還剩多少空間。

needs-source（留給能查原文的時候）：
- 第 3 章 Wang 等 2025-12：Qwen3-30B-A3B 的 FFN intensity 在他們的 batch 範圍裡「停在約 8」。照本文的算法應該隨 batch 慢慢上升，正文改成寫明「論文沒有說明為什麼幾乎是平的」；要查論文的圖確認 batch 範圍與數值。
- 第 9 章 Hacker-fixer loop 的「62% → 0%」：本文寫成「拿已知、公開過的漏洞手法去攻擊」，要對回論文的定義。
