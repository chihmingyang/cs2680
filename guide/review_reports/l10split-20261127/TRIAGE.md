# L10 拆成 L10 與 L10b 之後的可讀性審查（2026-11-27）

審查範圍：兩頁的導讀、拆堂時改過的句子；L10b 另外整頁掃 R3、R15（讀者現在從 L10b 的第 1 章開始讀）。審查包在 `notes/review/l10split/`（不進 git）。這一輪起，審查者不能寫檔，報告用文字回給主線；下面是主線的整理。

修法都寫在 `notes/l10split/build.py`（拆堂的 script），重建用 `notes/l10split/rebuild.sh`。

## L10

第一輪：18 個單位，7 BLOCK、2 NIT。

| 定位 | 條目 | 問題 | 處理 |
|---|---|---|---|
| #tldr ¶3 | R18 | 一段四個新名詞（arithmetic intensity、ridge point、memory-bound、compute-bound） | 第二輪仍 BLOCK → 拿掉「（叫 compute-bound）」，第 2 章才命名 |
| #tldr ¶6 | R18 | 四個新名詞（記憶體頻寬、MBU、prefill、MFU） | 刪掉 prefill／MFU 那一半與 MBU 的名字，只留「看頻寬用了幾成」 |
| #tldr ¶7 | R2 | 「程式寫在哪一層」的「層」 | 改成「要不要自己寫 GPU 程式」；第二輪「少空等」沒有主詞 → 改成「kernel 和 kernel 之間怎麼少空等（GPU 跑完一個 kernel，閒著等下一個）」 |
| #i1 ¶16 | R2、R13 | 「有些步驟」沒有例子；第二輪：attention 沒解釋、例子的原因在 L10b、「夠多的工作」對不上 ¶13 的「夠多的 thread」 | 開頭改成「第二個取捨的後果：工作小的時候晶片大半閒著」；第二層改寫成不靠 attention 的機制（能拆開平行的部分不多，切不出上百個 block），指到 L10b〈SM 之間的空等〉 |
| #i4 ¶1 | R13 | 「L10b 的每一種最佳化都是在滿足這兩個條件」在本頁驗不了 | 刪掉這一句 |
| #i4 註 n-chips 表1 列1 | R3、R18 | CUDA 沒解釋；第二輪：一格九個名字、PyTorch 沒解釋 | 補 CUDA、PyTorch 的說明；刪 hipify、Composable Kernel |
| #i5 ¶19 | R2 | 「寫在哪一層」沒有主詞 | 刪前半句，改成和導讀同一份清單 |

第二輪（7 個單位）：4 BLOCK，修法見上表最後一欄。第二輪之後沒有再審（最多兩輪）。

## L10b

第一輪：導讀與 64 個改過的單位，11 BLOCK、2 NIT；其他單位 R3／R15 17 條。

| 定位 | 條目 | 問題 | 處理 |
|---|---|---|---|
| #tldr ¶3 | R3 | tile language 只有例子 | 一句話說 tile language 是什麼（只寫一塊 tile 怎麼算），CUDA 則每個 thread 都要自己寫 |
| #tldr ¶5 | R2 | 「一步要跑幾十到上百個小 kernel」的「一步」 | 改成「每產生一個 token」 |
| #tldr ¶6 | R16 | 「五個公開報出的大幅加速，後來查出…」：表上只有前三列是事後查出 | 改成「2025 年有三個」 |
| #i1 ¶4 | R3 | SIMT 沒解釋 | 刪掉指向 L10〈SIMT〉的那一句；〈前情〉加 SIMT |
| #i2 ¶9 | R3、R9 | head、query 沒解釋；n × n 的第二個 n | 〈前情〉加 attention、head、Q、K、V；句子改成「Q 和 K 都是一個 token 一列、各有 n 列」 |
| #i2 ¶14 | R3 | KV cache 整頁沒解釋 | 〈前情〉加 KV cache（含 GQA） |
| #i2 ¶17 | R1 | 「FA4 不再和標準寫法逐位元相同」和 ¶14「差 10⁻¹⁶，只是浮點捨入」打架 | 改成「前三版和標準寫法只差浮點捨入，FA4 的誤差比捨入大」；題庫的 point 與 key 同步 |
| #i3 圖1 說明 | R1、R8 | 「前三格是 GPU 在等的三個地方」和正文的三種空等不是同一組；圖裡寫第 7、9 章 | 說明改成第一格是 kernel 之內、青色兩格是三種空等；aria-label 改成第 2、4 章 |
| #i3 ¶4 | R2 | 「8 份 K、V」 | 改成「K、V 存 8 組 head（GQA）」；題庫同步 |
| #i3 ¶12 | R13、R3 | 「回到 L10 的決策樹」；Nsight Systems 沒解釋 | 改成本頁第 1 章〈抽象層的選擇〉那張流程圖的第一問；補 Nsight Systems 是什麼 |
| #i4 ¶12 | R12、R18 | 0.14 ms、0.03 ms 用的 H100 規格只在 code 裡 | 寫成兩條算式，各帶 peak 與頻寬的標籤，並說取較大的那一項 |

R3／R15 的 17 條：多數是 L10 前五章定義過的詞，拆堂後讀者沒讀過。統一的處理是把〈前情〉表從 8 列加到 17 列：SIMT／lane／partition、tile、BF16、GEMM／GEMV、Ampere／Hopper／Blackwell、attention／head／Q／K／V、KV cache、MoE／expert、forward／backward。沒處理的：coalescing、layout、op 對「運算」、Context 對「n 個 token」、MMA、TMA／TMEM 的內容。前兩個是本頁後面才解釋的前向引用，其餘是拆堂之前就有的寫法；下次動到 L10b 時再審。

第二輪：只審改過的單位與〈前情〉表，結果見下一節。

## L10b 第二輪

改過的單位與〈前情〉表（63 個單位）：4 BLOCK。

| 定位 | 條目 | 問題 | 處理 |
|---|---|---|---|
| #tldr ¶5 | R15、R9 | 「一整步」和「每產生一個 token」是不是同一件事；為什麼 kernel 越小、空檔占比越大 | 補「CPU 每送一個 kernel 花的時間差不多固定」；「一整步」改成「產生一個 token 要送的 kernel」 |
| 〈前情〉MoE 那一列 | R3 | FFN 沒解釋 | 補「attention 之後的那幾個大矩陣乘法」 |
| #i3 ¶4 | R9 | 為什麼按 K、V 的 head 數切、不按 query head | 補「共用同一組 K、V 的 query head 放在同一個 block，K、V 只讀一次」 |
| #i4 ¶12 | R13 | 137 GFLOP、100 MB 怎麼來的只在 code 裡 | 正文寫出 2 × 4096³ 與三個矩陣的 bytes |

另外照審查者的建議刪了兩處只安排閱讀的字：FA4 那段重複的「這一部分是近似值」、第 3 章圖 1 說明的「第二、三格的這些名字，本章後面逐一解釋」。第二輪之後沒有再審（最多兩輪），`review_log.tsv` 記 v19。
