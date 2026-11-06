# L09 slides 逐頁筆記

- 來源：https://cs2680.com/slides/9_llm_serving_basics_1.pdf（2026-10-19，Efficient LLM serving basics I: intro to LLMs）
- 頁數：51（PDF 檢視器的頁數，封面 = 1）
- 整理：2026-11-06，WebFetch 逐頁整理，再用較窄的 prompt 補問沒有文字的頁；內容是 paraphrase，不是原文
- 用途：寫文章時取事實。v7 的文章不寫頁碼，這裡的頁碼只供對照。

註：p.6–8、13（部分）、24、26–27、31–34、42、44、46、49 沒有可擷取的文字（圖或動畫的 build），兩次 WebFetch 都讀不到。p.3 的 plan 列了 GPU 入門，實際在下一份 deck（L10）。

=== Page 1 ===
Cover. "Modern AI Systems: Agents and System Optimizations," Juncheng Yang. Lecture: "LLM Serving Basics I: Introduction to LLM." Harvard MaDSys · course.agentic-system.org.

=== Page 2 ===
Logistics. Assignment 3 due Tuesday 11:59pm. No late days for leaderboard submissions. Check the website for submission requirements. Project poster option 2: Dec 2, 1–3pm; sign up only if you cannot attend Dec 7 (signup was due "last Sunday"; email ASAP).

=== Page 3 ===
Plan for today.
- Introduction to LLMs: request lifecycle; the transformer architecture (assumes traditional self-attention); dense, MoE and advanced variants.
- Introduction to GPUs for LLM serving: basics, architecture, GPU programming and recent kernel advances (not detailed; to build intuition).

=== Page 4 ===
Lifecycle of an LLM request. Six stages from prompt to streamed text: (1) Tokenize, (2) Schedule, (3) Prefill, (4) Decode, (5) Detokenize, (6) Stream. Decode repeats per output token.
- Prefill determines time to first token (whole prompt in one forward pass).
- Decode determines tokens per second (one forward pass per output token).

=== Page 5 ===
Stage 1: Tokenization. Text is split into tokens, not words; about 3–4 characters per token. Token count drives cost and memory; tokenizers differ across models.
- Example: "Serving is hard" → 4 tokens (Serv, ing, is, hard), IDs 1841, 288, 374, 2653.
- Byte-level BPE starts from the 256 byte values and repeatedly merges the most frequent adjacent pair. No unknown tokens.

=== Page 6 === (no extractable text)
=== Page 7 === (no extractable text)
=== Page 8 === (no extractable text)

=== Page 9 ===
Stage 2: Scheduling and batching. Requests arrive independently, but GPUs want batches. The scheduler decides which requests run each step.
- Continuous batching: requests join or leave mid-flight; finished requests leave and new ones join without waiting for a full batch.
- Admission is capped by KV cache memory.
[Figure: three timesteps t, t+1, t+2 with slots R1–R5. R2 leaves after t, R4 joins at t+1, R5 joins at t+2; R1 and R3 keep running.]

=== Page 10 ===
Stage 3: Prefill. The whole prompt runs in one pass; all prompt tokens attend in parallel. Compute-bound; cost grows with prompt length. Generates the KV cache and emits output token 1. Prefill sets time to first token.
[Figure: six prompt tokens t1–t6 through one forward pass, producing the first output token.]

=== Page 11 ===
Stage 4: Decode and sampling. Each step: one forward pass per new token → logits; the cache grows by one token per step. Decode is bandwidth-bound, so it must be batched. If the cache is full, the scheduler preempts or queues requests.
Sampling:
- Temperature: 0 always picks the top token; > 1 allows more options.
- Top-k (e.g. top_k = 50): sample from the k most likely tokens; k fixed.
- Top-p / nucleus (e.g. top_p = 0.9): the fewest tokens whose probabilities sum to p; adapts to confidence.
Same model and prompt, but these settings change the answer and the run length.
[Figure: steps 1–4 each adding one KV entry to the cache.]

=== Page 12 ===
Stage 5: Detokenize and stream. Token IDs become text as they are produced; partial characters are buffered. Streaming makes output interactive. Stopping early frees cache memory. The stream ends on a stop token, a length limit, or a client disconnect.
[Figure: "The" → "The model" → "The model streams" → "The model streams tokens."]

=== Page 13 ===
(Build of p.12; same title "Stage 5, Detokenize and stream", rows t1–t4 "what the user sees, token by token".)

=== Page 14 ===
Lifecycle takeaways.
1. Tokenize: text → token IDs; a larger vocabulary means fewer tokens but a bigger embedding table.
2. Schedule: continuous batching lets requests join and leave each step; KV cache memory caps admission.
3. Prefill: one compute-bound pass over the whole prompt builds the KV cache and the first token.
4. Decode and sample: one memory-bound pass per token; sampling picks each token from the logits.
5. Detokenize and stream: convert IDs to text and send each token as produced.

=== Page 15 ===
Section divider: "Peeking into the model."

=== Page 16 ===
Notation. Llama 3 70B shape: d (model width) 8,192; L (layers) 80; H (query heads) 64; Hkv (KV heads) 8; dk (head dim, d ÷ H) 128; dff (MLP hidden width) 28,672; V (vocab) 128,256.
Workload and memory: n (tokens in sequence, e.g. 20,000); B (concurrent requests, e.g. 16); N (parameters) 70.6B; W (weight bytes, BF16) 141 GB; KV (bytes per token) 320 KB = 2 × L × Hkv × dk × 2 B. Kᵀ = K transposed. Source: Meta, The Llama 3 Herd of Models (2024).

=== Page 17 ===
An LLM is a stack of identical transformer blocks: token IDs → embedding (each ID → 8,192-dim vector) → transformer block × L (80 in Llama 3 70B; each with norm and residual) → LM head (one score per vocab token) → softmax → next-token probabilities. Each block: self-attention (mixes information across tokens) + FFN (transforms each token independently).

=== Page 18 ===
Each block adds attention and an MLP to a residual stream, each sublayer after RMSNorm.
- h = x + Attn(RMSNorm(x)); y = h + FFN(RMSNorm(h)).
- RMSNorm rescales by the root-mean-square, one learned gain per dimension.
- Pre-norm normalizes each sublayer's input so deep stacks train stably.
- The residual stream x flows through all 80 blocks; each sublayer only adds an update.
Sources: Zhang & Sennrich (RMSNorm, NeurIPS 2019); Xiong et al. (ICML 2020); Meta (Llama 3, 2024).

=== Page 19 ===
Self-attention lets each token read every earlier token.
- Each token emits a query, a key and a value. Query·key scores set how much to read from each token.
- A causal mask hides future tokens.
- n tokens produce n² scores, so cost grows with context.
- Scaling by √dk keeps the softmax from saturating (q·k sums dk products and grows with dk).
[Figure: causal attention matrix over "The cat sat on the", future masked; an example row 0.1, 0.2, 0.5, 0.2 sums to 1.]
Source: Vaswani et al. (Attention Is All You Need, NeurIPS 2017).

=== Page 20 ===
Each token is a row of X; weight matrices turn X into Q, K, V.
- Q = X·WQ: what each token looks for. K = X·WK: what each token offers. V = X·WV: what each token passes on.
- Shapes: X n × d; WQ, WK, WV d × dk per head; Q n × dk.
- Head: one attention unit; 64 run in parallel.
[Figure: X (n × d) × WQ (d × dk) = Q (n × dk).]

=== Page 21 ===
Q·Kᵀ scores every token pair; softmax turns each row into weights.
- S = QKᵀ ÷ √dk (n × n); add mask M (−∞ above the diagonal); softmax → A (rows sum to 1).
- O = A·V (n × dv): each output row is a weighted mix of V rows.
- Example: row 4 of A = how much token 4 takes from tokens 1–4. dv = 128.

=== Page 22 ===
Attention has O(n²) computation cost.
Steps: X (n × d) → Q = XWQ (n × dk) → S = QKᵀ/√dk (n × n) → A = softmax(S + M) (n × n) → O = AV (n × dv).
- FLOPs per layer ≈ 4n²d (2n²d for QKᵀ + 2n²d for AV).
- Memory if S were stored: n² × heads × layers × 2 B = 8,192² × 64 × 80 × 2 B ≈ 690 GB (n = 8,192). FlashAttention computes softmax tile by tile and never stores S.
Sources: Vaswani et al. (2017); Dao et al. (FlashAttention, NeurIPS 2022).

=== Page 23 ===
Multi-head attention: 64 small attentions in parallel, mixed with WO.
- Split Q, K, V into H = 64 heads of dk = 8,192 ÷ 64 = 128.
- Each head runs masked softmax attention on its own 128 dimensions; WO blends heads back into one vector.
- Same FLOPs as one wide head (64 × 128 = 8,192): splitting changes what is learned, not the cost.

=== Page 24 === (no extractable text)

=== Page 25 ===
Each head attends with its own 128 dimensions, so heads learn different patterns.
- Examples: head 1 → previous token; head 2 → first token; head 3 → nearby tokens; head 64 → whole context; ~60 more not shown.
- Output: each head n × 128; concat 64 heads → n × 8,192; × WO → n × 8,192.
[Figure: five-token example with per-head Q, K, V, each head's attention pattern, concatenation and WO mixing.]

=== Page 26 === (no extractable text)
=== Page 27 === (no extractable text)

=== Page 28 ===
Sharing key/value heads shrinks the KV cache.
- MHA: 8 query heads, 8 KV heads, 1× cache. GQA: 8 query heads, 2 KV heads, ¼×. MQA: 8 query heads, 1 KV head, ⅛×.
- KV cache per token = 2 × L × Hkv × dk × bytes per value.
- Llama 3 70B: 64 query heads share 8 KV heads → 8× smaller than MHA: 2 × 80 × 8 × 128 × 2 B = 320 KB per token, vs 2.5 MB with MHA.
Sources: Ainslie et al. (GQA, EMNLP 2023); Shazeer (MQA, 2019).

=== Page 29 ===
Llama 3 70B as an example: d = 8,192; h = 64 query heads, dh = 128 (64 × 128 = 8,192); hkv = 8; dff = 28,672 (3.5 × d); L = 80; V = 128,256. Each token is 8,192 numbers; output is 128,256 scores. Source: Meta (2024).

=== Page 30 ===
Llama 3 70B: where the parameters sit.
| Component | Formula | Params |
| Attention per layer | 2d·H·dk + 2d·Hkv·dk | 151M |
| FFN per layer | 3·d·dff | 705M |
| All 80 layers | 80 × 856M | 68.5B |
| Embedding + LM head | 2·V·d | 2.1B |
| Total | | 70.6B |

=== Page 31 === (no extractable text)
=== Page 32 === (no extractable text)
=== Page 33 === (no extractable text)
=== Page 34 === (no extractable text)

=== Page 35 ===
Systems intuition: weights, compute and KV cache set prefill, decode and memory.
- Weights: 2 bytes × params = 141 GB. Compute: ≈ 2 × params = 141 GFLOPs per token. KV cache: 2 × L × Hkv × dk × 2 B = 320 KB per token.
- Example (Llama 3 70B, BF16, 2× H200 = 1,978 TFLOP/s, 9.6 TB/s, 282 GB; n = 80,000 tokens, B requests):
  - Prefill 80K tokens: 9.95 s for 1 request; 637 s for 64 requests.
  - VRAM needed (W + B·n·KV): 167 GB for 1 request; 1,779 GB for 64 requests.
- Closing question: "How do you support longer sequences?"
Sources: Meta (2024); NVIDIA H200 datasheet (2024).

=== Page 36 ===
MoE replaces each block's FFN with a router and smaller expert FFNs.
- Dense block: attention → one large MLP, all of it runs for every token.
- MoE block: attention → router picks top 2 of 8 experts (E0–E7); only 2 run per token; outputs form a weighted sum.
Sources: Shazeer et al. (MoE, ICLR 2017); Jiang et al. (Mixtral of Experts, 2024).

=== Page 37 ===
Dense vs MoE: memory scales with total parameters, compute with active parameters.
| Model | Experts | Total | Active/token | Weights (BF16) | GFLOPs/token |
| Llama 2 70B | all (dense) | 69B | 69B | 138 GB | 138 |
| Mixtral 8x7B | 2 of 8 | 46.7B | 12.9B | 93 GB | 26 |
| Llama 3.1 405B | all (dense) | 405B | 405B | 810 GB | 810 |
| DeepSeek-V3 | 9 of 257 | 671B | 37B | 1,342 GB | 74 |
- Mixtral matches Llama 2 70B at about 1/5 the FLOPs.
- DeepSeek-V3 rivals Llama 3.1 405B at about 1/11 the FLOPs but needs 1.7× the memory.
- GFLOPs ≈ 2 × active parameters.

=== Page 38 ===
Advanced LLMs ("skim, or read more on your own"): sliding window, multi-latent attention, linear attention, state-space models, sparse attention, looped transformers, multi-token prediction, diffusion LMs.

=== Page 39 ===
Sliding-window layers cap the KV cache; a few global layers keep long-range recall.
- Full causal attention: the last token reads all tokens, KV grows with n. Sliding window (w = 3): the last token reads 3 tokens, KV capped at w.
- Gemma 3: 5 local layers (w = 1,024) to 1 global, repeated. Mistral 7B: every layer local, w = 4,096. Gemma 2: alternates 1 local (w = 4,096) with 1 global.
- Serving effect: at 128K context, Gemma 3 stores about 6× less KV than all-global layers.
Source: Gemma Team (Gemma 3 Technical Report, 2025).

=== Page 40 ===
Multi-latent attention (MLA) stores one compressed latent per token.
- Token h is compressed to latent c, which is cached; K and V are expanded from c when attention needs them.
- The up-projection is folded into the query and output weights at decode time.
- Serving effect: versus DeepSeek 67B, DeepSeek-V2 cuts KV cache by 93% and lifts generation throughput 5.8×.
[Figure: MHA caches K and V per head; MLA caches one latent c per token, K and V rebuilt from c, never stored.]
Sources: DeepSeek-AI (V2, 2024; V3, 2024).

=== Page 41 ===
Linear-attention layers keep a fixed-size state instead of a growing KV cache.
- Softmax attention: one more KV entry per token, forever.
- Linear attention: state St of size dk × dv, same size every step, updated in place. Each token adds key × value to the state; a query reads the state.
- Gated DeltaNet: first fades the old state (decay gate αt), then overwrites what the new key points to (write gate βt).
- Qwen3-Next: 48 layers in a 3:1 pattern (36 Gated DeltaNet + 12 attention). Only the 12 attention layers keep a KV cache. Same recipe: Kimi Linear, Qwen3.5.
- Serving effect: 3 of 4 layers hold a constant-size state per request at any context length.
Sources: Yang et al. (Gated Delta Networks, ICLR 2025); Qwen Team (Qwen3-Next, 2025).

=== Page 42 === (no extractable text)

=== Page 43 ===
State-space models also keep a fixed-size state.
- Selective: Ā and B̄ depend on each token, so the layer chooses what to keep.
- Fixed state: each channel keeps a small state h, so decode memory stays flat as n grows.
- Serving effect: no growing KV cache; Mamba reports up to 5× a Transformer's generation throughput.
- Gated linear attention vs SSM: GLA updates a dk × dv matrix S with forgetting gate α; Mamba updates a small vector h per channel with Ā and adds B̄ × x.
- Hardware-aware scan: a parallel scan keeps the state in SRAM; Mamba-2 turns it into matmuls.
Sources: Gu & Dao (Mamba, COLM 2024); Dao & Gu (Mamba-2, ICML 2024).

=== Page 44 === (no extractable text)

=== Page 45 ===
Sparse attention reads only the top 2,048 past tokens per query (DeepSeek-V3.2 k = 2,048; the example uses k = 4 of 16).
1. Score: an indexer computes It,s = Σj wt,j · ReLU(qt,j · ks) for each past token.
2. Select: keep the top-k scores as St.
3. Attend: ot = Attn(qt, {cs : s ∈ St}).
- The indexer uses few heads, FP8, and a 128-number key per token.
- Serving effect: work per token capped at 2,048 reads, but all tokens' KV is still stored.
Source: DeepSeek-AI (DeepSeek-V3.2-Exp, 2025).

=== Page 46 === (no extractable text)

=== Page 47 ===
Looped transformers reuse one block many times: depth costs compute, not weights.
- One block R applied K times; extra depth adds no parameters.
- Depth at test time: a 3.5B recurrent-depth model improves on reasoning tasks as K grows.
- Tradeoff: weights stay small, but each loop is sequential, so latency grows with K. K loops cost K× the block's FLOPs, no extra weight memory.
[Figure: Input → Prelude P → Block R × K → Coda C → Output.]
Sources: Dehghani et al. (Universal Transformers, ICLR 2019); Geiping et al. (2025).

=== Page 48 ===
Diffusion LMs fill in masked tokens over a few parallel refinement steps.
- Step 0 is all [M]; each step fills more tokens. Each diffusion step re-reads all weights.
- LLaDA (2025): 8B masked-diffusion model trained from scratch on 2.3T tokens; competitive with Llama 3 8B.
- Dream 7B (2025): starts from Qwen2.5 7B weights; the network is still a Transformer.
- Serving effect: one pass fills many tokens, but fewer steps cost quality.
Sources: Nie et al. (LLaDA, 2025); Ye et al. (Dream 7B, 2025).

=== Page 49 === (no extractable text)

=== Page 50 ===
Next class (title only).

=== Page 51 ===
Optional reading (title only; no titles in the extracted text).

TOTAL PAGES: 51

## Readings（https://cs2680.com/readings/oct-19.html，2026-11-06 讀）

頁面沒有必讀／選讀之分，依主題分組；「Why read it」是 AI 產生、教授選的。

- From text to tokens：Neural Machine Translation of Rare Words with Subword Units (BPE), 2015, https://arxiv.org/abs/1508.07909
- The Transformer：Attention Is All You Need, 2017, https://arxiv.org/abs/1706.03762；The Illustrated Transformer, 2018, https://jalammar.github.io/illustrated-transformer/；The Annotated Transformer, 2018, https://nlp.seas.harvard.edu/annotated-transformer/
- The decoder block in current models：RMSNorm, 2019, https://arxiv.org/abs/1910.07467；GLU Variants Improve Transformer (SwiGLU), 2020, https://arxiv.org/abs/2002.05202
- A dense model sized end to end：The Llama 3 Herd of Models, 2024, https://arxiv.org/abs/2407.21783（頁面說 70B 的 KV cache 是 BF16 每 token 320 KB）
- Weights, FLOPs, and the KV cache：Transformer Inference Arithmetic, 2022, https://kipp.ly/transformer-inference-arithmetic/
- Mixture of experts：Switch Transformer, 2021, https://arxiv.org/abs/2101.03961；Mixtral of Experts, 2024, https://arxiv.org/abs/2401.04088（約 13B / 47B）；DeepSeekMoE, 2024, https://arxiv.org/abs/2401.06066；DeepSeek-V3 Technical Report, 2024, https://arxiv.org/abs/2412.19437（671B、37B active）
- Beyond a fixed-depth autoregressive stack：Recurrent Depth (Geiping et al.), 2025, https://arxiv.org/abs/2502.05171；LLaDA, 2025, https://arxiv.org/abs/2502.09992（頁面說它和 KV caching 不相容）；Dream 7B, 2025, https://arxiv.org/abs/2508.15487（從 Qwen2.5 7B 初始化、580B token）
