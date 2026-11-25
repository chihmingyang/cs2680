# L9 大綱：只看標題的測試

讀者設定：後端工程師，用過 LLM API，知道 RAG、token、prompt；沒學過 transformer 內部，沒做過 LLM serving。
只讀了 `notes/outline/l09-outline.txt`，沒讀內文。

## 1. 逐章：只看標題，我認為在講什麼

**第 1 章 Request lifecycle。** 一個 request 從進來到結束的過程。1.1 說生成分 Prefill 與 Decode 兩段；1.2 說兩段之間靠 KV cache 接起來；1.3 說多個 request 怎麼併成 batch；1.4 說 Decode 何時停；1.5 說 agent 的 request 有什麼不同（每圈重送 context）。章名先給了結論：Prefill 管 TTFT，Decode 管 token 間隔。

**第 2 章 Transformer 的結構與參數。** Model 裡面有什麼、參數放在哪。2.1 是入口（token ID 變 vector）；2.3 是主體（block = Attention + FFN，疊很多層）；2.4 是參數在兩個子層的比例；2.2 與 2.5 是算運算量：先講一個矩陣的 FLOPs，再推到整個 model。

**第 3 章 Attention 與 KV cache。** Attention 怎麼算，KV cache 為什麼存在。3.1 三個 vector；3.2 計算步驟；3.3 成本是 n²；3.4 KV cache 是為了不重算；3.5 multi-head；3.6 GQA 把 KV cache 縮小。順序是「機制 → 成本 → 省成本的做法」。

**第 4 章 Serving 的三個數字。** 把第 2、3 章算出的三個量對到 serving 的三個限制。4.1 FLOPs → Prefill 時間；4.2 Weights → Decode 每步時間；4.3 KV cache → 能同時服務多少 token；4.4 把三個數字套到 agent workload。

**第 5 章 MoE。** MoE 把參數分成「存著的」和「每個 token 真的用到的」。5.1 定義兩種參數；5.2 何時適合用；5.3 MoE 在 Decode 加 batch 時的特殊成本。

**第 6 章 縮小 KV cache 的架構。** 五種做法各一節，每節一句話講它存什麼或讀什麼；6.6 講實務上怎麼混用。分工很清楚。

**第 7 章 Open-weight model 的每 token KV cache。** 實際 model 之間差多少。7.1 怎麼從 config.json 算；7.2 公式的例外；7.3 對選 model 的結論。

**第 8 章 Tokenizer 與中文的 token 數。** 8.1 BPE 的做法；8.2 詞彙大小的取捨；8.3 中文怎麼被切；8.4 繁中的實測數字；8.5 token 數影響哪些決定；8.6 streaming 輸出時的 UTF-8 問題。

**第 9 章 Sampling。** 9.1 Temperature；9.2 Top-k、Top-p；9.3 sampling 設定與輸出長度的關係；9.4 Temperature 0 也不保證相同輸出；9.5 託管 model 不讓你設，自架才用得到。

**查閱。** 附錄：符號表、公式表，加上一些正文沒放的架構。

整體 mind map 長得出來：lifecycle（1）→ model 內部（2、3）→ 三個數字對到 serving（4）→ 改變這三個數字的架構（5、6、7）→ 兩端的周邊（8 tokenizer、9 sampling）。

## 2. 單看看不懂的標題

確定卡住的 4 處（共 6 個標題）：

1. **`1.5 Agent 的 request：每一圈重送整段 context，prefix cache 省算力不省記憶體`** 與 **`4.4 Agent workload：算力靠 prefix cache 省下，KV cache 記憶體省不下`**
   卡在：兩個標題分不開。主題都是 agent，結論都是「prefix cache 省算力、不省記憶體」。只看標題，我不知道 4.4 比 1.5 多講了什麼。猜測是 1.5 講現象、4.4 用三個數字算，但標題沒寫出這個差別。

2. **`2.5 Weights 與每個 token 的 FLOPs：由參數總數 N 直接算出`**
   卡在：「Weights」不知道指哪個量。對我來說 weights 就是參數，「Weights 由參數總數算出」讀起來像同一件事算自己。猜測是「weights 佔的記憶體（bytes）」，但標題沒說。第 4 章章名的「Weights」是同一個問題，2.5 是它第一次出現的地方。

3. **`4.2 Weights 決定 Decode 一步的時間：batch 的原因`**
   卡在：「batch 的原因」只有四個字，不知道指什麼。可能是「所以要做 batch」，也可能是「batch 為什麼有效」或「batch 為什麼不增加時間」。另外同第 2 項，「Weights」是哪個量沒說。

4. **`5 MoE（Mixture of Experts）：記憶體看 Total 參數，運算看 Active 參數`** 與 **`5.1 Total 與 Active 參數：各管記憶體與運算`**
   卡在：章名和第一個小標講同一句話，分不開。而且沒有一個標題說 MoE 的結構是什麼（expert 是什麼、怎麼選）。我看得出 MoE 有兩種參數，看不出它怎麼運作，也看不出 5.1 在章名之外多講了什麼。

較輕的 4 處（看得出大概，但有一個詞要猜）：

5. **`1.3 Continuous batching：scheduler 每一步重組 batch，收不收看 KV cache 記憶體`**
   卡在：「收不收」沒有受詞，而且「收不收看」連讀會斷錯句。猜測是「收不收新的 request，看 KV cache 記憶體夠不夠」。

6. **`2 Transformer 的結構與參數`**
   卡在：章名蓋不住小標。2.2 與 2.5 講的是 FLOPs（運算量），章名只有「結構」與「參數」。第 4 章的三個數字裡有兩個（Weights、FLOPs）出自這一章，章名卻看不出來。

7. **`8.5 Token 數的影響：估算、選 model、prompt 用哪種語言`**
   卡在：「估算」沒有受詞。估算成本、估算 context 用量、還是估算 KV cache？後兩項（選 model、prompt 語言）是清楚的。

8. **`查閱：符號、公式與其他架構方向`**
   卡在：「其他架構方向」不知道相對於什麼。是第 6 章五種以外的縮小 KV cache 做法，還是 transformer 以外的架構？

## 不算看不懂，但順便記下

- `2.3 …重複 80 次`、`3.5 …切成 64 個 head`、`3.6 …縮成 320 KiB`：數字來自某一個具體 model，但整份大綱沒有一個標題說是哪個 model。每一節講哪一面是清楚的，所以不列入；只是讀者會以為這些是 transformer 的通用數字。
- `7.2 公式沒算到的部分：固定大小的 cache 與 state、FP8 的存法`：「公式」靠 7.1，「固定大小的 cache 與 state」靠第 6 章。在章內看得懂，單獨抽出來看不懂。
- `1.2` 與 `3.4` 都講 KV cache，但分得開：1.2 講它在 lifecycle 的角色，3.4 講它為什麼可以存。
