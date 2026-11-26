# L10 只看標題的測試（GPU Basics & Kernel Optimization）

讀者設定：後端工程師。用過 LLM API，知道 token、prompt、batch。聽過 GPU，沒寫過 GPU 程式，沒做過 LLM serving。
材料：只讀 `notes/outline/l10-outline.txt`（章名與小標，沒有內文）。

結果：確定卡住 6 個，較輕 14 個。

---

## 1. 逐章：我認為這一章在講什麼

### 第 1 章 GPU 的設計：用上萬個簡單的核心換 throughput

GPU 和 CPU 的設計目標不同：CPU 要單件事快（latency），GPU 要單位時間做得多（throughput）。1.2 到 1.4 是 GPU 為了這個目標用的機制與代價：warp 切換蓋住等記憶體的時間，SIMT 讓 32 個 thread 一起跑同一段程式，分支不同時兩邊都要跑（divergence）。1.5 是收尾，把前面的代價整理成四項。

小標的關係：1.1 是目標，1.2–1.4 是機制，1.5 是總結。但 1.2 先用了 warp，1.3 才說 warp 是什麼。

### 第 2 章 Roofline：kernel 的時間由搬資料與運算較慢的一邊決定

這一章給一個估時間的模型。一段 GPU 程式要花的時間，是「搬資料的時間」和「運算的時間」兩個裡面較大的那個。2.1、2.2 準備名詞和 GPU 的規格，2.3 是公式，2.4 給一個判斷法（arithmetic intensity 對 ridge point），2.5 拿四種運算來套，2.6 講 ridge point 隨精度怎麼動。

小標的關係：名詞 → 規格 → 公式 → 判斷法 → 例子 → 趨勢。順序是直線的。

### 第 3 章 Decode：batch 1 只用到 0.5% 的算力

把第 2 章的模型用在 LLM 產生 token 的階段。Batch 1 時，每個 weight 讀進來只用一次，所以時間都花在搬資料，算力幾乎閒著。3.2 列出三個改善的方法，3.3–3.5 講其中幾個的效果與限制：batching 能分攤 weights 但不能分攤 KV cache，context 越長越慢，MoE 會把 batch 拆散。

小標的關係：3.1 是問題，3.2 是三個方法的總表，3.3–3.5 是細節。但 3.3–3.5 沒有一對一接到 3.2 的三個方法：「降低精度」沒有自己的小節，3.4 講的是 KV cache 的問題，不是「減少讀取」的做法，3.5 是 batching 的例外。

### 第 4 章 GPU 晶片的內部：SM、Tensor Core、記憶體階層

打開一顆 GPU（H200）看裡面有什麼。4.1 是總覽，4.2 是運算單元 SM 的結構，4.3 是 SM 裡面專做矩陣乘法的 Tensor Core，4.4 是從近到遠四層記憶體。4.5 用 Little's law 寫出頻寬的公式。

小標的關係：整體 → SM → SM 裡的 Tensor Core → 記憶體。4.5 看起來是接在記憶體後面的補充，但標題沒說它要解釋什麼。這一章也回頭支撐第 2 章的三個規格和第 1 章的 warp。

### 第 5 章 GPU 使用率的量測：nvidia-smi、MFU、MBU、DCGM counter

怎麼知道 GPU 有沒有被用好。5.1 說最常看的 GPU-Util 數字不代表算力用了幾成。5.2、5.3 給兩個正確的指標：算力看 MFU，頻寬看 MBU，各對應一種工作。5.4、5.5 是硬體 counter 與讀的順序。5.6 是更細的工具 profiler。

小標的關係：錯的指標 → 兩個對的指標 → 硬體 counter → 怎麼讀 → profiler。由粗到細。

### 第 6 章 GPU 程式的抽象層：從 graph compiler 到 CUDA

GPU 程式可以在不同的層級寫。6.1 先講 CPU 端怎麼叫 GPU 做事。6.2 是最低層：為一個 thread 寫 CUDA kernel。6.3 是最高層：只寫 model，compiler 產生 kernel。6.4 是中間層：為一塊資料（tile）寫。6.5 把全部排成五層。

小標的關係：6.1 是前提，6.2–6.4 是三個層，6.5 是總表。小節的順序是低 → 高 → 中，和章名「從 graph compiler 到 CUDA」的高 → 低不同。6.5 的五層裡有兩層前面沒有小節。

### 第 7 章 Kernel 之內的最佳化：Fusion 與 FlashAttention

在一個 kernel 裡面省時間，方法是讓中間結果留在晶片上，不寫回最遠的記憶體 HBM。7.1 是一般原則（fusion）。7.2 說標準 attention 會產生兩個 n × n 的中間結果，全部經過 HBM。7.3 是 FlashAttention 的做法：切成小塊算。7.4 是讓切塊可行的數學（online softmax）。7.5 是版本演進。

小標的關係：原則 → 問題 → 解法 → 解法的關鍵 → 歷史。這一章是第 2 章「搬資料較慢」的直接應用。

### 第 8 章 Kernel 之間的最佳化：SM 之間、launch 之間、GPU 之間的空等

GPU 有三種空等的時間：SM 等 SM、兩次 kernel launch 之間、GPU 等 GPU。8.1、8.3、8.4 各講一種和它的解法。8.5 是結論：這些不要自己寫，選已經做好的 serving engine。

小標的關係：三種空等各一節，加一個結論。8.2（Split-KV）夾在中間，我看不出它屬於哪一種。

### 第 9 章 AI 寫的 kernel：先驗證正確，再相信加速

AI 產生的 kernel 常回報很大的加速，其中很多是假的。9.1 是案例，9.2 把造假或出錯的方式分成五類，9.3 用第 2 章的 roofline 當物理上限（比上限還快就一定有錯），9.4 是驗收清單。

小標的關係：案例 → 分類 → 一個判準 → 清單。9.4 的各項可以對回 9.2 的五類和 9.3。

### 第 10 章 一張 GPU 之外：網路、故障、電力與水

視野從一張 GPU 拉到一台機器、一個資料中心。10.1、10.2 是 GPU 之間的連線與它的頻寬（比 GPU 內部少很多）。10.3 是規模變大後的故障頻率。10.4、10.5 是電力與用水。

小標的關係：四個並列的主題。網路佔兩節，其他各一節。

### 整堂的 mind map

第 1 章講 GPU 為什麼長這樣：它用很多簡單的核心換 throughput。第 2 章給全堂共用的尺：一段 GPU 程式的時間，由搬資料與運算較慢的一邊決定。第 3 章把這把尺用在 LLM 的 decode，結論是 decode 卡在搬資料，算力閒著。第 4 章打開晶片，解釋尺上的三個規格從哪裡來。第 5 章講怎麼在實機上量出自己卡在哪一邊。第 6 章轉到寫程式：GPU 程式有幾層寫法。第 7 章和第 8 章是一對：第 7 章在一個 kernel 之內省搬資料的量，第 8 章消掉 kernel 之外的空等。第 9 章是警告：AI 寫的 kernel 要用第 2 章的上限和一份清單驗收。第 10 章離開單張 GPU，看網路、故障、電力、水。

主線是：設計（1）→ 模型（2）→ 應用到 decode（3）→ 硬體細節（4）→ 量測（5）→ 寫法（6）→ 兩類最佳化（7、8）→ 驗收（9）→ 更大的系統（10）。第 2 章的 roofline 是中心節點，第 3、5、7、9 章都接回它。第 4 章的位置我要猜：它夾在 decode 和量測之間，從標題看不出為什麼不緊接第 1 章。

---

## 2. 單看看不懂的標題

### 確定卡住（6 個）

**1.5 GPU 的四個取捨：單一 thread 的速度、自動的平行、各自的控制流程、每個 thread 的記憶體**
- 卡在「取捨」的方向。取捨有兩邊，標題只列了一邊。我不知道這四項是 GPU 放棄的，還是 GPU 拿到的。
- 「自動的平行」兩種讀法都通：GPU 自動幫你平行（拿到），或 GPU 不會自動幫你找平行、要自己寫（放棄）。「每個 thread 的記憶體」也看不出是指什麼。
- 我猜：四項都是 GPU 放棄的，用來換 throughput。

**2.6 Ridge 的趨勢：精度越低越往右**
- 卡在「往右」。它指一張我沒看到的圖，標題沒說橫軸是什麼。
- 也卡在後果：往右之後對我有什麼影響，標題沒說。「趨勢」也可以讀成「新一代硬體的趨勢」。
- 我猜：橫軸是 arithmetic intensity。資料用越低的精度（例如 FP16 → FP8），ridge point 的 intensity 越高，所以更多運算會落在 memory-bound。

**6.5 五層抽象：graph compiler、tile language、明確的 tile、layout 與 warp 分工、thread**
- 卡在第三、四層。「明確的 tile」和第二層「tile language」分不開：都是 tile，看不出多了什麼。「layout 與 warp 分工」是一句描述，不是一層的名字，我不知道它對應哪種寫法或工具。
- 章名說「從 graph compiler 到 CUDA」，但這五層裡沒有 CUDA。我要猜 CUDA 是最後的「thread」，還是後三層全部。
- 我猜：越往下，自己要決定的事越多。第三層是自己切 tile，第四層是自己排資料位置並分配每個 warp 做什麼，第五層是 6.2 的 CUDA（為一個 thread 寫）。

**7.5 FlashAttention 1 到 4：每一代修上一代留下的瓶頸**
- 卡在「瓶頸」沒有列出是哪幾個。這句話套在任何有版本號的東西上都成立，所以這個節點在 mind map 裡沒有內容。
- 我猜：每一代各解一個不同的問題（例如 HBM 流量、平行度、新硬體的指令），但是哪幾個我猜不出來。

**8 Kernel 之間的最佳化：SM 之間、launch 之間、GPU 之間的空等**
- 卡在章名蓋不住小標。「Kernel 之間」和第 7 章「Kernel 之內」是一對，但 SM 是一顆 GPU 裡面的單元，一個 kernel 會同時跑在很多 SM 上。照這樣看，「SM 之間的空等」發生在一個 kernel 之內，不是 kernel 之間。「GPU 之間」也比 kernel 之間大。
- 8.5（選 serving engine）不是一種空等，但章名只列了三種空等。
- 我猜：這一章真正的主題是「空等」，不是「kernel 之間」。第 7 章省的是搬資料的量，第 8 章省的是硬體閒著的時間。

**8.2 Split-KV：decode 的 attention 要沿 KV cache 切**
- 卡在「切」。標題沒說切的是什麼（工作？資料？），也沒說為什麼「要」切。
- 也卡在位置。章名有三種空等，8.1、8.3、8.4 各有標籤，8.2 沒有。我看不出它屬於哪一種。
- 我猜：它接在 8.1 後面，屬於「SM 之間的空等」。Decode 時 batch 小，照原本的切法只有少數 SM 有事做，所以改成沿 KV cache 的長度切成幾段，分給更多 SM。

### 較輕（14 個）

**1.2 Warp 切換：GPU 藏住記憶體延遲的方法**
- 卡在 warp。1.3 才說 warp 是 32 個 thread 綁成的一組，1.2 先用了。
- 我猜：一組 thread 在等記憶體時，硬體換另一組來跑，像 OS 在等 I/O 時做 context switch。

**2 Roofline：kernel 的時間由搬資料與運算較慢的一邊決定**
- 卡在 kernel。後端工程師看到 kernel 先想到 OS kernel。這個詞從堂名、第 2 章就開始用，到 6.2、6.3 才看得出是「在 GPU 上跑的一段程式」。
- 我猜：kernel 是 GPU 上執行的一個函式，一次做一種運算。

**2.1 FLOP、byte、bandwidth：roofline 用的三個單位** 與 **2.2 GPU 的三個規格：算力、頻寬、容量**
- 卡在 bandwidth／頻寬。它在 2.1 是「單位」，在 2.2 是「規格」，一個寫英文一個寫中文。我要猜兩個是同一個東西。bandwidth 也不像 FLOP、byte 那樣是單位。
- 2.2 的「頻寬」「容量」沒說是誰的。後端工程師看到頻寬先想到網路。
- 我猜：都是記憶體的。頻寬是每秒能從 GPU 記憶體讀多少 bytes，容量是 GPU 記憶體有多大。

**3 Decode：batch 1 只用到 0.5% 的算力**
- 卡在 Decode。標題沒說它是哪個東西的哪個階段。我用過 tokenizer 的 decode（token 轉回文字），這裡顯然不是。
- 我猜：LLM 一次產生一個 output token 的階段。

**3.2 Decode 的三個槓桿：batch、降低精度、減少 KV cache 的讀取**
- 卡在 KV cache。標題沒說它是哪一類東西。後端工程師會讀成 key-value cache（像 Redis）。3.3、3.4、8.2 也用到。
- 我猜：每個 request 自己的一塊資料，存前面 token 算過的 attention 結果，context 越長越大（從 3.4 推的）。

**3.5 MoE 的 batching：batch 被分給各個 expert**
- 卡在 MoE。標題沒說它是一種 model 架構，也沒說「被分給」之後的後果。
- 我猜：MoE 的 model 裡有很多 expert，每個 token 只走其中幾個。所以一個 batch 到了每個 expert 只剩一小份，batching 的好處變小。

**4.5 Little's law：頻寬 = 在路上的 bytes ÷ latency**
- 公式看得懂，卡在它在這一章的用途。章名列的是 SM、Tensor Core、記憶體階層，沒有它。
- 我猜：latency 是固定的，所以要頻寬高，就要同時有很多 bytes 在路上。這解釋了 1.2：GPU 要有很多 warp 同時在等記憶體。

**5.2 MFU（model FLOPs utilization）：prefill 和訓練看算力用了幾成**
- 卡在 prefill。全堂的標題沒有介紹它，第 3 章只講 decode。用 LLM API 的人知道的 prefill 是「先替 assistant 寫開頭幾個字」，這裡不是。
- 我猜：model 一次讀完整段 input prompt 的階段，和 decode 相對。它是 compute-bound，所以看 MFU。

**5.6 Profiler：Nsight Systems 看 timeline，Nsight Compute 看單一 kernel**
- 標題本身看得懂。卡在章名：章名是「使用率的量測」並列了四個工具，profiler 不在裡面，量的也不像是使用率。
- 我猜：counter 只說忙不忙，profiler 說時間花在哪一段。它是 5.5 之後的下一步。

**6.1 Host 與 device：用 PCIe 連接，kernel launch 是非同步的**
- 卡在 host 與 device 各是誰，標題沒說。這一節也不像章名說的「抽象層」。
- 我猜：host 是 CPU 那一邊，device 是 GPU。CPU 送出 kernel 之後不等它跑完。這是後面各層的前提，也是 9.4「同步後計時」的原因。

**6.2 CUDA kernel：為一個 thread 寫，用 block 與 thread 的編號算位置**
- 卡在 block 和「位置」。block 是什麼的 block、和 1.3 的 warp 是什麼關係，標題沒說。位置是誰的位置也沒說。
- 我猜：block 是一組 thread。每個 thread 用「第幾個 block 的第幾個 thread」算出自己負責資料的第幾個元素。

**6.4 Tile language（Triton）：為一整塊 tile 寫，不為一個 thread 寫**
- 卡在 tile。標題沒說是一塊什麼。6.5 的「明確的 tile」也靠這個詞。
- 我猜：矩陣切出來的一小塊資料。程式描述對一塊資料做什麼，compiler 決定怎麼分給 thread。

**7.1 Fusion：中間值不回 HBM**
- 卡在 Fusion 融合的是什麼。標題只給了效果。
- 我猜：把幾個連續的運算合併成一個 kernel。合併之前，每個運算的結果都要寫回 HBM 再讀出來。

**7.2 標準 attention 的 HBM 流量：n × n 的中間值 S 與 P**
- 卡在 S 與 P。標題直接用符號，沒說是什麼。7.3 只說 S 不離開晶片，沒提 P。
- 我猜：S 是每對 token 的分數，P 是 S 做完 softmax 的機率。n 是 token 數。
