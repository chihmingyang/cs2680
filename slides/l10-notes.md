# L10 slides 逐頁筆記

這一堂有兩份 deck，封面是同一個標題「LLM Serving Basics II: Intro to GPUs」：

- A：https://cs2680.com/slides/10_llm_serving_basics_2a.pdf（2026-10-21），41 頁：GPU basics、GPU architecture、optional（AMD、TPU、Trainium、SRAM 加速器）
- B：https://cs2680.com/slides/10_llm_serving_basics_2b.pdf（2026-11-02，課程網站寫「GPU programming (cont.)」），55 頁：GPU programming、efficiency and utilization、recent kernel advances、challenges、optional（optimize GPU code）
- 頁數：PDF 檢視器的頁數，封面 = 1。文中寫「A p.N」「B p.N」。
- 整理：2026-11-06，WebFetch 逐頁整理，再用較窄的 prompt 補問沒有文字的頁；內容是 paraphrase，不是原文
- 用途：寫文章時取事實。v7 的文章不寫頁碼，這裡的頁碼只供對照。

註：A p.6 沒有文字。B p.15、17–20、28–29、33、37–38 是前一頁的動畫 build，沒有新文字。B 的 footer 在 p.48–50 附近和 PDF 頁數可能差 1；下面依 WebFetch 從封面數起的順序。B p.49 的三個百分比和原因的對應、215 ms／24 ms 的意思，是 WebFetch 依文字位置推的，沒有從圖上確認（見該頁）。

# A：10_llm_serving_basics_2a.pdf（41 頁）

=== A Page 1 ===
Cover: "Modern AI Systems: Agents and System Optimizations," Juncheng Yang. Lecture "LLM Serving Basics II: Intro to GPUs." Harvard MaDSys, course.agentic-system.org.

=== A Page 2 ===
Logistics. Assignment 4 released today, due in about two and a half weeks. Goal: reason about performance and bottlenecks, iterate, see how real workloads differ from synthetic benchmarks. The write-up matters most; the code is small. No late days for leaderboard submissions. Do not use more than one GPU. Can be hard with limited systems programming experience. Proposal due next Wednesday, Oct 28; no limit on format or length. Do not upload AI-generated content.

=== A Page 3 ===
Plan: GPU introduction for LLM serving — GPU basics, GPU architecture, GPU programming with recent kernel advances. Footnote: details skipped; the goal is intuition.

=== A Page 4 ===
Section divider: "GPU Basics — Everything you must know about GPUs."

=== A Page 5 ===
GPU form factors: consumer PCIe card in a desktop vs data-center 8-GPU board in a server. [Figure: photos/renderings.]

=== A Page 6 === (no extractable text)

=== A Page 7 ===
A GPU is a throughput machine.
- CPU: optimized for one thread. Each core: large control logic (out-of-order, branch prediction), a few ALUs, L1/L2 caches. Cores share an L3 and a few DDR channels.
- GPU: optimized for the whole chip. Many SMs (32 of 132 drawn), each with arithmetic units, registers, caches. Shared L2, memory controllers, HBM stacks thousands of bits wide.
- Analogy: a sports car carries 2 riders on the fastest trip; a bus fleet is slower but moves thousands.

=== A Page 8 ===
A GPU trades a few fast cores for thousands of simple ones. (64-core server CPU | NVIDIA H200 SXM)
- Parallel units: 64 cores | 132 SMs, 16,896 FP32 cores
- Threads in flight: 128 | 270,336 (2,048 per SM)
- Memory bandwidth: ~0.46 TB/s (DDR5) | 4.8 TB/s (HBM3e)
- Peak dense math: ~5 TFLOPs FP32 | 989 TFLOPs BF16
- Hides latency by: caches and out-of-order execution | switching to a ready warp
- On a cache miss, a CPU thread runs ahead until its out-of-order window fills, then stalls; a GPU switches to another ready warp.
- Why it fits LLMs: every token runs the same matmuls on the same weights, in parallel.

=== A Page 9 ===
Switching warps hides memory latency. While one warp waits on memory, another issues instructions, so math units stay busy. Each of the 4 warp schedulers per SM manages up to 16 warps → 64 resident warps per SM (A100, H200, B200). [Figure: W0–W3 alternating between waiting and issuing.]

=== A Page 10 ===
SIMT: single instruction, multiple threads. A thread's code is written once as scalar code (i = threadIdx.x; y[i] = a*x[i] + b). A warp = 32 threads sharing one fetch, one decode, one scheduling decision; each lane has its own registers. One warp instruction does the work of 32 scalar instructions (like CPU SIMD). [Figure: one thread's program mapped onto lanes 0–31.]

=== A Page 11 ===
Branch divergence. Example: if (i % 4 == 0) a = f(x[i]) else a = g(x[i]). The warp runs both paths in turn using an active mask (0xFFFFFFFF, 0x11111111, 0xEEEEEEEE), then reconverges. Cost: f uses 8 of 32 lanes, g uses 24; masked-off lanes sit idle.

=== A Page 12 ===
Trade-offs behind the GPU (gives up | gets):
- Single-thread speed (modest clock, no speculation; serial code much slower) | area and power go to thousands of arithmetic units.
- Explicit parallelism required (~270K threads fill 132 SMs; small jobs leave the chip idle) | latency hidden by warp switching, not caches or speculation.
- Shared control flow in groups of 32; divergence costs throughput | one fetch/decode drives 32 cores.
- Small on-chip memory per thread (~240 bytes at full occupancy) | all thread state resident, so warp switches are free.

=== A Page 13 ===
Three specs set the limits of every GPU.
- Peak BF16 compute: A100 312, H200 989, B200 2,250, Rubin ~4,000 TFLOP/s. Limits math speed.
- Memory capacity: A100 80 GB HBM2e, H200 141 GB HBM3e, B200 180 GB HBM3e, Rubin 288 GB HBM4. Limits how many weights and KV entries fit.
- Memory bandwidth: A100 2.0, H200 4.8, B200 8, Rubin ~22 TB/s. Limits how fast weights and KV are read.
- Analogy: compute = engine, bandwidth = fuel line, capacity = tank.

=== A Page 14 ===
Compute reaches peak only when each byte read feeds enough FLOPs.
- Decode, batch 1: 3.3 ms per token. HBM reads 16 GB of weights. Tensor cores idle 99.5% of the time. Each weight used once: 0.016 ms of math waits on 3.3 ms of reads.
- Prefill, 2,048 tokens: 33 ms per prompt. Weights load once, reads finish early. Tensor cores perform 33 TFLOP near peak. Each weight feeds 2,048 tokens: math sets the pace.
- Rule: kernel time ≈ max(bytes ÷ bandwidth, FLOPs ÷ peak).

=== A Page 15 ===
The roofline: memory or compute limits a kernel.
- Left of the ridge: memory-bound, speed = bandwidth × intensity. Right: compute-bound, speed = peak FLOP/s.
- Ridge = peak FLOP/s ÷ bandwidth. H200 ridge ≈ 206 FLOP/B.
- Arithmetic intensity = FLOPs performed ÷ bytes moved to/from HBM.
- Source: Williams, Waterman & Patterson, "Roofline," CACM 2009.
[Figure: log-log roofline; decode on the memory-bound slope, prefill on the roof.]

=== A Page 16 ===
Common arithmetic intensities (b = bytes per element):
- Square GEMM N×N: each element reused ~N times; intensity = 2N/(3b).
- Decode attention n×d: each KV entry used once per head; intensity = 2/b.
- GEMV in decode N×N: each weight used once; intensity ≈ 2/b.
- Vector add length N: 1 FLOP per 3 elements moved; intensity = 1/(3b).

=== A Page 17 ===
Does batching help decode? Chart: arithmetic intensity (FLOP/B, BF16) vs batch size 1–256, y 0–300. Weights line rises toward the 206 ridge (≈256 at batch 256). Attention line stays flat at 2/b. Takeaway: batching lifts weight GEMVs toward the ridge, decode attention stays flat.

=== A Page 18 ===
Does context length help decode? Llama 3 8B, batch 16, BF16. Weights fixed at 16.1 GB, read once per step at any length. KV cache 128 KiB per token, grows with batch × length. Step time ≈ bytes ÷ 4.8 TB/s: 3.8 ms at 1K context, 17.7 ms at 32K. Total HBM bytes per step: 1K 18.2 GB; 4K 24.7 GB; 8K 33.3 GB; 16K 50.5 GB; 32K 84.8 GB. Sources: Meta (2024); NVIDIA H200 datasheet (2024). [Figure: stacked bars weights vs KV at 1K–32K.]

=== A Page 19 ===
Quiz: how busy is an H200 during batch-1 decode? Given peak 989 TFLOP/s BF16, HBM 4.8 TB/s, batch-1 decode ≈ 1 FLOP per byte of weights read. Options A ≈ 50%, B ≈ 10%, C ≈ 2%, D < 1%. What would you change to raise it?

=== A Page 20 ===
On an H200 roofline, batch-1 decode runs at 0.5% of peak compute. Batch-1 GEMV at ~1 FLOP/B reaches ~5 of 989 TFLOP/s; decode is bandwidth-bound. Fixes: raise intensity by batching more, quantizing, or shrinking KV traffic. Prefill is compute-bound: large GEMMs sit on the roof, only faster math or fewer FLOPs help. Compute roof 989 TFLOP/s; memory roof 4.8 TB/s × intensity; ridge ≈ 206 FLOP/B. [Figure: points for vector add, GEMV batch 1, GQA decode, GEMV batch 32, GEMM N=8192.]

=== A Page 21 ===
Trend: lower precision pushes the ridge right. Ridge = dense peak ÷ HBM BW (FLOP/B). Columns HBM | FP32 | BF16 | FP8 | FP4:
- A100 SXM: 2.04 TB/s | 9.6 | 153 | – | –
- H100 SXM5: 3.35 TB/s | 20 | 295 | 591 | –
- H200: 4.8 TB/s | 14 | 206 | 412 | –
- B200 HGX: 8 TB/s | 9.4 | 281 | 563 | 1,125
- MI355X: 8 TB/s | – | 315 | 629 | 1,259
- Rubin (preliminary): 22 TB/s | – | 182 | 795 | 1,591
Notes: FP4 pushes the ridge right; Rubin's dense NVFP4 needs ~1,600 FLOP/B to be compute-bound. A100 → Rubin: BF16 compute ~13×, bandwidth ~9×, so kernels become increasingly bandwidth-bound.
（2026-11-06 本文驗算：依同頁的表，4,000 ÷ 312 = 12.8 倍，22 ÷ 2.04 = 10.8 倍，不是約 9 倍；BF16 的 ridge 依序 153、295、206、281、182，並不單調，右移主要來自 FP8／FP4。）

=== A Page 22 ===
GPU basics takeaways: (1) a throughput machine trades fast single threads for thousands of parallel cores; (2) three limits (peak compute, HBM bandwidth, capacity) bound every kernel; (3) the roofline ridge (206 FLOP/B on H200) separates memory-bound from compute-bound; (4) decode: batching lifts weight reads toward the ridge, KV-cache reads stay memory-bound; (5) newer GPUs move the ridge right, so more kernels become bandwidth-bound.

=== A Page 23 ===
Section divider: "GPU Architecture."

=== A Page 24 ===
An illustration of the H200: 132 SMs share one 50 MB L2 and 141 GB HBM3e; each SM has registers and 256 KB SRAM. HBM3e: 6 stacks × 24 GB = 141 GB usable at 4.8 TB/s. NVLink 900 GB/s to other GPUs. Sources: NVIDIA Hopper whitepaper (2022); H200 datasheet (2024).

=== A Page 25 ===
Each SM splits into four partitions, each issuing one warp instruction per cycle. Each partition: warp scheduler, 64 KB registers, 32 FP32 cores, a Tensor Core. Shared L1/shared memory 256 KB per SM. Warp = 32 threads; one instruction on all 32 (SIMT). Up to 64 warps (2,048 threads) resident; scheduler picks a ready warp each cycle. Tensor Cores do a small matrix multiply-add per instruction.

=== A Page 26 ===
LLM math is mostly matmul; Tensor Cores speed it up. One warp-level instruction computes D = A × B + C; tiles A 16×16, B 16×8, C/D 16×8. Matmuls are over 99% of LLM FLOPs; softmax and norms run on FP32 cores. One mma = 2,048 multiply-adds = 64× an FMA's work per instruction. Peak dense TFLOP/s, H200 SXM: BF16 Tensor 989; TF32 Tensor 495; FP16 scalar 134; FP32 scalar 67. Sources: NVIDIA PTX ISA (mma); H200 datasheet (2024); Dally et al., IEEE Micro (2021).

=== A Page 27 ===
Why Tensor Cores are fast: specialized multiply-add datapaths on whole tiles; fewer instructions per FLOP (one MMA amortizes decode, scheduling, operand handling); operand reuse (each A value feeds several output columns, each B value several rows); lower precision (FP16, BF16, FP8 raise throughput and shrink operands, usually with higher-precision accumulation). Source: Hopper whitepaper (2022).

=== A Page 28 ===
The memory hierarchy (level | capacity | latency | bandwidth):
- Registers: 256 KB per SM | in the pipeline | 3 operands per core per clock.
- Shared memory / L1: 256 KB pool per SM | ~30 cycles (40 for an L1 hit) | 128 B/clk per SM, ~33 TB/s across 132 SMs.
- L2: 50 MB | ~250 cycles | ~6 KB/clk, ~12 TB/s on Hopper.
- HBM3e: 141 GB in 6 stacks | ~500 cycles | 4.8 TB/s on H200 SXM.
- Host memory and peer GPUs: CPU DRAM, other GPUs over NVLink | microseconds | 450 GB/s each way on NVLink 4; PCIe 5.0 ~64 GB/s.
Source: Luo et al., Dissecting the NVIDIA Hopper Architecture (2024).

=== A Page 29 ===
Memory is a 250 ns pipe: bandwidth depends on bytes in flight. Little's law: bandwidth = bytes in flight ÷ latency; latency 250 ns from load issue to data arrival.
- Naive kernel: 4 KB in flight per SM (32 warps × 32 threads × one 4-byte load) → 2.2 TB/s, ~45% of peak. (The slide also writes "512 B", which contradicts its own arithmetic; 32 × 32 × 4 B = 4 KB.)
- Full pipe: ~9 KB in flight per SM (4.8 TB/s × 250 ns ÷ 132 SMs) → 100% of peak.
- Ways to raise bytes in flight: 16-byte vector loads, four independent loads per thread, bulk async copies (TMA). The hardware fixes the pipe length; the only lever is keeping more bytes inside it.
（2026-11-06 本文驗算：4 KB／SM × 132 = 541 KB，÷ 250 ns = 2.16 TB/s = 45%，和 slides 的 2.2 TB/s、45% 一致，所以 4 KB 是對的；512 B 應該是 A p.31 一條 16-byte vector load 的 warp 指令搬的量。）

=== A Page 30 ===
Bytes in flight per generation (H200 Hopper | B200 Blackwell | Rubin): SMs 132 | 148 | 224; HBM 141 GB HBM3e | 180 GB HBM3e | 288 GB HBM4; bandwidth 4.8 | 8 | 22 TB/s; bytes in flight per GPU 1.2 MB | 2.0 MB | 5.5 MB; per SM 9 KB | 14 KB | 25 KB; new data-path feature: TMA and clusters | TMEM and 2-SM MMA | inline TMA descriptors. Sources: NVIDIA Hopper and Blackwell whitepapers; Vera Rubin, GTC 2025.

=== A Page 31 ===
(ADVANCED, skim) Hopper enables more bytes in flight per instruction (feature | what | effect):
- Coalescing | 32 threads reading consecutive 4-byte words merge into one 128 B request | fewer, fuller requests.
- 16-byte vector loads | one warp instruction moves 512 B instead of 128 B | 4× bytes per instruction.
- cp.async (Ampere+) | global → shared without register staging | registers stay free.
- TMA (Hopper) | one thread issues a bulk tile copy; hardware generates addresses | KBs in flight from one instruction.
- TMA multicast | one L2 read lands in every SM of a cluster | less L2 traffic per SM.

=== A Page 32 ===
(ADVANCED) Hopper's TMA copies a whole tile with one instruction: one thread starts the copy; the TMA engine moves a tile (e.g. 128 × 64) from HBM to shared memory; registers free; tens of KB in flight. Cluster multicast: up to 8 thread blocks share one L2 read.

=== A Page 33 ===
(ADVANCED) Blackwell: results move into tensor memory (TMEM, 256 KB) instead of registers, freeing registers for more loads in flight. 2-SM MMA: two SMs do one matmul on a double-size tile, each loading half. Source: Blackwell whitepaper (2024).

=== A Page 34 ===
From one GPU to many: scale-up and scale-out. 8-GPU node (HGX H200): GPUs via NVSwitch, 8 NICs at 400 Gb/s to the scale-out network. NVL72 rack (GB200): units of 4 GPUs + 2 CPUs joined by NVLink switches across 9 rows. Specs: H200 4.8 TB/s HBM, 900 GB/s NVLink, 50 GB/s RDMA; B200 8 TB/s HBM, 1.8 TB/s NVLink, 100 GB/s RDMA. Source: NVIDIA HGX H200 and GB200 NVL72 specs (2024).

=== A Page 35 ===
(ADVANCED) Two decades of NVIDIA GPUs:
- Tesla 2006 G80: unified shaders; CUDA, thread blocks, shared memory.
- Fermi 2010 C2050: real L1/L2, ECC, unified address space, fast FP64.
- Kepler 2012 K20X: warp shuffles, dynamic parallelism, Hyper-Q.
- Maxwell 2014 M40: SM split into four partitions; perf-per-watt gains.
- Pascal 2016 P100: HBM2, NVLink, page-faulting unified memory, 2× FP16.
- Volta 2017 V100: Tensor Cores, independent thread scheduling, unified L1/shared.
- Turing 2018 T4: INT8/INT4 Tensor Cores, ray-tracing cores.
- Ampere 2020 A100: TF32, BF16, 2:4 sparsity, cp.async, MIG, 40 MB L2.
- Hopper 2022 H100: FP8, TMA, clusters and DSMEM, wgmma, confidential computing.
- Blackwell 2024 B200: two dies, FP6/FP4 and block scaling, TMEM, tcgen05, NVL72.
- Blackwell Ultra 2025 B300: 288 GB HBM3e, 15 PF dense NVFP4, faster exp, much less FP64.
- Rubin 2026 NVL72: HBM4, NVLink 6, larger TMEM and shared memory (preliminary).
Summary: 2006–17 graphics → general-purpose compute; 2018–26 compute → low-precision AI engines. G80 → B300: peak math ~43,000×, bandwidth ~90×.

=== A Page 36 ===
Next class: student sharing; GPU programming and performance optimization; LLM serving III: batching, paging, parallelism.

=== A Page 37 ===
Section divider: "Optional reading."

=== A Page 38 ===
AMD Instinct MI355X: chiplet GPU with more HBM per package. 8 compute dies seen as one GPU; 256 MB Infinity Cache in front of HBM; wavefronts of 64 threads (not 32-thread warps). Programming: ROCm and HIP (CUDA-style C++; hipify converts CUDA). PyTorch, vLLM, SGLang run on ROCm; custom kernels via Triton or Composable Kernel. MI355X | B200: 5.0 PF dense FP8 | 4.5 PF; 288 GB HBM3E | 180 GB; 8 TB/s | 8 TB/s; 8-GPU scale-up | NVL72 has 72. Source: AMD MI355X datasheet and CDNA 4 whitepaper (2025).

=== A Page 39 ===
Google TPU Ironwood: systolic arrays linked in a 3D torus. JAX or PyTorch/XLA; XLA tiles matmuls onto the arrays; Pallas for custom kernels. Ironwood | B200: 4.6 PF dense FP8 | 4.5; 192 GB HBM3E | 180; 7.4 TB/s | 8; 9,216 chips in a 3D torus | NVL72 has 72. Figure: SIMT lanes read operands from a register file and write back; a weight-stationary systolic array keeps each weight in its cell, activations enter from the left, partial sums flow down. Sources: Google Cloud TPU7x (Ironwood) docs (2026); Jouppi et al., ISCA 2023.

=== A Page 40 ===
Amazon Trainium3: systolic engines with software-managed SRAM. 8 NeuronCores, each with separate Tensor (systolic), Vector and Scalar engines; 32 MB SRAM per core filled by DMA, no hardware cache. Gains from MXFP8 and MXFP4; BF16 per core unchanged from Trainium2. Neuron SDK compiles PyTorch/JAX graphs; NKI gives Python kernels that move tiles HBM ↔ SRAM explicitly; no CUDA; kernels target engines, not threads. Trainium3 | B200: 2.5 PF dense MXFP8 | 4.5 PF FP8; 144 GB HBM3E | 180 GB; 4.9 TB/s | 8 TB/s; 144-chip scale-up | NVL72 72. Sources: AWS Trainium3 Architecture Guide for NKI (2025); AWS Trainium page (2025).

=== A Page 41 ===
Other accelerators: on-chip SRAM in place of HBM (chip | on-chip SRAM | off-chip | trade-off): Cerebras WSE-3 | 44 GB | none | whole wafer is one chip; larger models stream weights in. Groq LPU | 230 MB | none | a 70B model at 8 bits needs ~300 chips. Microsoft Maia 200 | 272 MB | 216 GB HBM3e | SRAM holds hot data; only inside Azure. Sources: Cerebras WSE-3 datasheet (2024); Groq LPU architecture (2024); Microsoft Maia 200 (2026).

TOTAL PAGES (A): 41

# B：10_llm_serving_basics_2b.pdf（55 頁）

=== B Page 1 ===
Title slide (same as A): "LLM Serving Basics II: Intro to GPUs."

=== B Page 2 ===
(Repeats A p.2 logistics: Assignment 4 out today, due in two and a half weeks; write-up matters most; no late days; one GPU; proposal due Oct 28; no AI-generated content.)

=== B Page 3 ===
Logistics (same text as B p.2).

=== B Page 4 ===
Plan: GPU basics, architecture, GPU programming and recent kernel advances; details skipped, the aim is intuition.

=== B Page 5 ===
Section divider: GPU Programming.

=== B Page 6 ===
GPU code runs asynchronously. Host (CPU + DRAM) runs main(); device (GPU + HBM) runs kernels; connected by PCIe Gen5 x16 at ~64 GB/s, 75× below HBM bandwidth. The CPU does not wait for a kernel launch to finish; errors appear late, at the next sync call. Sequence: cudaMalloc, H→D memcpy, launch, other CPU work, vec_add runs on SMs, memcpy back (waits). [Figure: CPU thread, copy engine, SMs lanes overlapping.] Cites CUDA C++ Programming Guide (2024), PCI-SIG PCIe 5.0 (2019).

=== B Page 7 ===
A kernel is written for one thread (SIMT). Vector add: each thread computes one output element from a global index (block and thread IDs). Launch 256 threads per block; blocks = ceil(n/256). 1M elements → 4,096 blocks spread over 132 SMs. Block sizes in multiples of 32; 128–256 typical. Warps come from the linear thread ID. Qualifiers: __global__ (device, called from host); __device__ (device, device); __host__ __device__ (both).

=== B Page 8 ===
Each thread's IDs pick its element: launch 4,096 blocks × 256 threads; i = blockIdx.x × blockDim.x + threadIdx.x (block 2, thread 1 → i = 513); each thread writes out[i]. [Figure: blocks 0–4,095 × threads 0–255 → array of 1,048,576.]

=== B Page 9 ===
Blocks run on SMs as warps of 32. Grid (all blocks of a launch) → whole GPU (132 SMs); Block (≤ 1,024 threads, shared memory) → one SM, stays until finished; Warp (32 threads in lockstep) → one partition scheduler issues per cycle; Thread (own registers, index) → one lane of the warp's 32 SIMT lanes.

=== B Page 10 ===
Graph compilers (torch.compile): code the model, the compiler writes the kernels. Write `gelu(x @ w + b) * 0.5`; `torch.compile(mode="max-autotune")` captures, fuses, generates kernels; first call compiles. JAX: jax.jit → XLA. You decide the math; the compiler decides fusion, tile sizes, generated Triton or XLA kernels. Stops working when control flow breaks the graph or a slow op cannot be fused. Cites Ansel et al. (PyTorch 2, ASPLOS 2024), OpenXLA docs (2026).

=== B Page 11 ===
Tile languages: describe the work of a whole block, not one thread. CUDA C++ (per-thread work, manual staging, __syncthreads, Tensor Core warp MMA) vs tile languages (per-tile work, program_id + a range over the tile; compiler stages and syncs). Triton (Python; NVIDIA and AMD), Pallas (JAX kernels for TPU and GPU), TileLang (Python DSL on TVM), ThunderKittens (C++ tile templates), cuTile (NVIDIA's tile model in CUDA). Cites Tillet et al. (MAPL 2019), Spector et al. (ThunderKittens, 2024), NVIDIA CUDA 13.1 (2025).

=== B Page 12 ===
(ADVANCED) Triton: each program handles one tile. `add` kernel: each program (one CUDA block) owns BLOCK=1024 elements; offsets from program_id and tl.arange; masked loads/stores. Grid = ceil(n/1024). The compiler handles coalescing, shared-memory staging, Tensor Core MMA via tl.dot; @triton.autotune searches BLOCK sizes and warp counts per shape.

=== B Page 13 ===
(ADVANCED) TileLang: you place each tile in shared memory; the compiler maps threads. Matmul: T.Kernel grid over N/bn and M/bm, 128 threads; alloc_shared for A and B tiles; alloc_fragment for the float accumulator; T.Pipelined loop num_stages=3; T.copy and T.gemm. You choose tile shapes, shared vs register storage, pipeline stages; TileLang chooses thread mapping, copy instructions, swizzles, MMA calls. For GEMM and attention variants needing explicit staging. Cites Wang et al. (TileLang, arXiv 2025).

=== B Page 14 ===
(ADVANCED) CuTe, CUTLASS, ThunderKittens: you choose layouts, async copies, warp roles. CuTe layout: make_layout((8,4), stride=(4,1)) vs stride=(1,8), mapping (i, j) to i*4+j vs i+j*8. The same layout algebra describes thread-to-data mapping, swizzled shared tiles, TMA boxes, MMA fragments. The library supplies tested per-GPU building blocks; use to reach peak on GEMM and attention.

=== B Page 15 === (build of p.14, no new text)

=== B Page 16 ===
(ADVANCED) Levels of abstraction (level | when | cost), labeled a course synthesis:
- Graph compiler (torch.compile, XLA): default for the whole model; little control over the slow op.
- Tile language (Helion, Triton, Pallas): one op is unfused or missing; hours; portable across GPUs.
- Explicit tiles (TileLang): need control of staging; days.
- Layouts and warp roles (CuTe, CUTLASS, ThunderKittens): GEMM or attention must reach peak; weeks; per GPU generation.
- Threads (CUDA C++): irregular work (sort, sparse, graphs); everything is on you.

=== B Page 17 === (build, no new text)
=== B Page 18 === (build, no new text)
=== B Page 19 === (build, no new text)
=== B Page 20 === (build, no new text)

=== B Page 21 ===
(ADVANCED) Every GPU program compiles down to SASS. Triton → Triton IR → TritonGPU IR → LLVM IR → PTX → ptxas → SASS (cubin). CUDA C++: NVCC → NVVM → PTX → ptxas → SASS. cuTile: CUDA Tile IR → tileiras → SASS. Host: GCC/Clang/MSVC host object; linker → executable with a fatbin (SASS + PTX). At load, the driver runs SASS matching the GPU or JIT-compiles PTX and caches it.

=== B Page 22 ===
Section divider: GPU efficiency and utilization.

=== B Page 23 ===
MFU in inference: model FLOPs utilization = achieved model FLOP/s ÷ peak FLOP/s. Model FLOPs ≈ 2N per generated token (forward only). Peak = dense Tensor Core rate. Example: Llama 2 70B on 8 H100s: per token ≈ 140 GFLOP; 3,040 tok/s per GPU × 140 GFLOP ≈ 426 TFLOP/s; MFU = 426 ÷ 1,979 ≈ 22%. Rule of thumb: training 35–45%; inference prefill 40–60%; decode 10–40%. Cites Chowdhery et al. (PaLM, JMLR 2023), Korthikanti et al. (MLSys 2023).

=== B Page 24 ===
Four reasons MFU is low: communication (TP, PP, DP transfers not hidden behind compute); pipeline bubbles (stages idle while batches fill and drain); memory-bound kernels (norms, softmax, optimizer steps at bandwidth, not Tensor Core peak); recomputation (training: activation checkpointing reruns forward work MFU does not count). MFU separates hardware capability from software maturity.

=== B Page 25 ===
MBU: decode efficiency is bytes per second, not FLOPs. MBU = achieved bytes/s ÷ peak HBM bandwidth; bytes per decode step = all weights + KV cache read. Example: Llama 3 8B, BF16, batch 1, H200: 16 GB per token; at 200 tok/s, 3.2 TB/s ÷ 4.8 TB/s ≈ 67%. Rule: report MFU for prefill and training, MBU for decode. Other serving metrics: tokens/s per GPU at a latency target (e.g. p50 time per output token); energy per token (average board power ÷ tokens/s); cost per million tokens = ($ per GPU-hour ÷ (tokens/s × 3,600)) × 10⁶. Cites Databricks, LLM Inference Performance Engineering (2023).

=== B Page 26 ===
Profile the timeline, then the kernel. Nsight Systems: `nsys profile -o run ./app` — timeline of CPU threads, CUDA API calls, copies, kernels, streams; finds idle gaps, serialized streams, launch overhead. Nsight Compute: `ncu --set full -k vec_add ./app` — replays each kernel for counters (speed of light, memory traffic, warp stalls, hot lines); finds why one kernel is slow; replay timings for comparison only. Workflow: nsys finds the slow region; ncu explains one kernel; change one thing and measure again.

=== B Page 27 ===
GPU utilization counters: nvidia-smi utilization (share of time at least one kernel runs); SM active (share of SM cycles with a warp resident); SM occupancy (resident warps ÷ max warps, all SMs); Tensor pipe active (share of cycles Tensor Cores busy); DRAM active (share of cycles HBM moves data). `dcgmi dmon -e 203,1002,1003,1004,1005` gives one column per counter. Cites NVIDIA DCGM User Guide (2026).

=== B Page 28 === (build of the counters slide, no new text)
=== B Page 29 === (build, no new text)

=== B Page 30 ===
Reading the counters: find which unit is busy. Decision tree: (1) GPU busy (nvidia-smi 100%)? If no: idle between kernels → CPU launch overhead or data loading; next: Nsight Systems timeline, CUDA graphs. (2) SMs busy (SM active high)? If no: too few thread blocks → larger batch or more blocks per kernel. (3) Which unit? DRAM active high → memory-bound, judge by MBU. Tensor pipe active high → compute-bound, judge by MFU. Both low → latency-bound, use Nsight Compute.

=== B Page 31 ===
GPU efficiency takeaways: (1) MFU = achieved model FLOP/s ÷ dense peak; judge prefill and training by it; (2) low MFU comes from communication, pipeline bubbles, memory-bound kernels, recomputation; (3) MBU = achieved bytes/s ÷ peak HBM bandwidth; judge decode by it; (4) nvidia-smi at 100% only means a kernel is running; read SM, Tensor and DRAM activity.

=== B Page 32 ===
Section divider: Recent Advances in GPU Kernel Optimizations.

=== B Page 33 === (build, no new text)

=== B Page 34 ===
Kernels lose GPU time in three places: (1) inside a kernel — Tensor Cores wait on loads, softmax, exp; advances: FlashAttention, warp specialization, FlashAttention-4. (2) Across SMs — SMs idle in uneven rounds and between launches; advances: persistent kernels, split-KV, CUDA Graphs, PDL, megakernels. (3) Across GPUs — GPUs wait for each other's data; advances: fused collectives, MoE all-to-all overlap. Writing kernels: each new GPU needs new hand-tuned kernels; advance: agents that write and test kernels.

=== B Page 35 ===
Kernel fusion: vertical chains steps; horizontal merges parallel ops. Vertical: producer feeds consumer in one kernel (GEMM + bias + GELU; LayerNorm; masked softmax), saves HBM round trips. Horizontal: ops sharing an input merge (x·W_q, x·W_k, x·W_v → x·[W_q W_k W_v]), saves launches and repeated reads of x (QKV projection; FFN gate and up). torch.compile fuses vertical chains into one Triton kernel; model code often concatenates QKV and gate/up weights by hand. Example: scale, add bias, ReLU on 1 GB FP32: unfused 1.25 ms, three kernels, every step through HBM; fused 0.42 ms, ~3× less HBM traffic.

=== B Page 36 ===
FlashAttention: compute attention tile by tile so S never reaches HBM. Problem: standard attention writes the n × n score matrix S and softmax P to HBM and reads them back; at 8K tokens, 67M scores per head per layer. Solution: tile Q, loop over K, V tiles in shared memory and registers, keep a running max and sum (online softmax); S and P never leave the chip; HBM reads K, V once and writes O once. Cites Dao et al. (NeurIPS 2022), Dao (FlashAttention-2, ICLR 2024).

=== B Page 37 === (build, no new text)
=== B Page 38 === (build, no new text)

=== B Page 39 ===
(ADVANCED) From FlashAttention to FlashAttention-4:
- FA1 (2022, A100): bottleneck HBM traffic from the n × n matrix; fix shared-memory tiling with online softmax; 2–4× faster; memory linear in length.
- FA2 (2023, A100): bottleneck low occupancy (one block per head, many non-matmul FLOPs); fix splitting work across the sequence; ~2× FA1; up to ~70% of A100 peak.
- FA3 (2024, H100): bottleneck Tensor Cores waiting on loads and softmax; fix TMA, warp specialization, overlapping softmax with GEMM, FP8; ~75% of H100 peak in FP16.
- FA4 (2025, B200): bottleneck Tensor Cores doubled while exp did not, so softmax is the limit; fix TMEM accumulators and part of exp on FMA units; faster than cuDNN attention on B200.

=== B Page 40 ===
Persistent kernels: one thread block per SM works through many tiles. Problem: a matmul split into 160 output tiles, one block per tile, on 132 SMs; round 2 has only 28 blocks, leaving 104 SMs idle; each block repeats setup. Solution: one block per SM looping over tiles; no idle round, setup once. CUTLASS and DeepGEMM do this. Stream-K: split tiles into smaller pieces so all SMs finish together. Cites Osama et al. (Stream-K, PPoPP 2023), CUTLASS 3.x (2024).

=== B Page 41 ===
Split-KV balances decode across SMs. Problem: decode has one query token per request, so splitting only across batch × heads leaves SMs idle; KV lengths differ by 100× across requests and pages are scattered in HBM. Solution: split KV pages across SMs (e.g. 4 pages per SM) and merge partial (m, ℓ, O) per request, as in online softmax. Paged KV = block-sparse rows with a fixed grid, CUDA Graph-safe. FlashInfer (MLSys 2025 Outstanding Paper) pairs block-sparse KV, JIT-specialized kernels and this scheduler; vLLM and SGLang use it. Cites Dao et al. (Flash-Decoding, 2023), Ye et al. (FlashInfer, MLSys 2025).

=== B Page 42 ===
CUDA Graphs: record the launches once, replay with one call. Problem: decoding one token runs dozens of small kernels; each launch costs a few µs of CPU and driver time, leaving GPU gaps. Solution: capture the decode step once, replay per token with a single graph launch. Pattern: cudaStreamBeginCapture → launch kernels → cudaStreamEndCapture → cudaGraphInstantiate → cudaGraphLaunch. vLLM and SGLang do this.

=== B Page 43 ===
Programmatic Dependent Launch (PDL) starts the next kernel early. Problem: in a stream, kernel B launches only after A fully drains and flushes memory; decode has many µs-scale kernels, so launch latency, prologue and tails add up. Solution: A calls cudaTriggerProgrammaticLaunchCompletion(); B calls cudaGridDependencySynchronize(); B's prologue overlaps A's tail. Needs Hopper+ (SM 9.0); works inside CUDA Graphs. Cites CUDA Programming Guide §4.5 (2025).

=== B Page 44 ===
A megakernel runs the model in one launch. Problem: batch-1 decode of Llama-3.2-1B runs ~7 kernels per layer × 16 layers per token; each boundary drains the GPU; vLLM and SGLang reach ~50% of H100 bandwidth. Solution: the Hazy Research megakernel reaches 78% of H100 bandwidth at batch 1, ~1.5× SGLang per-user throughput. Components: on-GPU interpreter, per-SM instruction queue, paged shared memory for weights, global counters for dependencies. Mirage MPK compiles such task graphs automatically. Cites Spector, Juravsky et al. (Hazy Research, 2025), Mirage MPK (2025).

=== B Page 45 ===
Fused collectives hide tensor-parallel communication. Problem: TP across 8 GPUs adds an AllGather before and a ReduceScatter after every sharded GEMM; as separate kernels, the GEMM waits for the whole collective. Solution: fuse communication into the GEMM; each tile's epilogue writes to its owner GPU; AllGather + GEMM starts tiles as rows arrive; peer writes over NVLink or NVSHMEM, no extra kernel. FLUX overlaps up to 96% of communication; up to 1.66× faster prefill and 1.30× faster decode than vLLM on 8 GPUs. Cites Chang et al. (FLUX, arXiv:2406.06858, 2024).

=== B Page 46 ===
MoE all-to-all hides behind compute. Problem: each MoE layer sends each token to its top-8 experts on other GPUs and gathers outputs back; back-to-back dispatch and combine leave Tensor Cores idle, and NCCL kernels take SMs from compute. Solution (DeepEP): two micro-batches overlap, so attention of A and B, expert GEMMs and dispatch/combine interleave; hook-based transfers run on the NIC, no SMs; dispatch FP8, combine BF16; NVLink → RDMA forwarding. DeepEP ~153 GB/s dispatch over NVLink within a node, ~43 GB/s over RDMA across nodes. Cites DeepSeek-AI (DeepEP, 2025), DeepSeek-V3 (arXiv:2412.19437).

=== B Page 47 ===
Agents become the new compiler. Problem: each GPU generation (TMA, TMEM, FP4) and attention variant needs new hand-tuned kernels, and few engineers write them; generated kernels can look fast by passing a weak test or exploiting the harness. Solution: a feedback loop — agent writes a kernel (CUDA, Triton, CuTe DSL) → compile (nvcc, ptxas errors) → check against a PyTorch reference over many shapes → profile runtime and Nsight counters → back. fast_p: share of tasks that are correct and more than p× faster than PyTorch. Static checks reject racy schedules. Cites Ouyang et al. (KernelBench, 2025), AutoMegaKernel (arXiv:2606.09682, 2026).

=== B Page 48 ===
Kernel advances takeaways: (1) inside a kernel, feed the Tensor Cores: fuse epilogues, scale per block in FP8/FP4, split warps into producers and consumers, move work off the slowest unit; (2) across SMs and launches, remove idle time: persistent CTAs and split-KV balance SMs; PDL and megakernels close gaps; (3) across GPUs, hide communication: fuse TP collectives into GEMM tiles; overlap MoE all-to-all with expert compute; (4) writing kernels, automate the search: agents write and profile candidates; correctness checks on many shapes decide which survive.

=== B Page 49 ===
Challenges in AI hardware.
- Networking: 9× slower off-node, shown for a KV-cache handoff of a 32K-token Llama 3 70B prompt (215 ms next to "400G NIC", 24 ms next to "NVLink (H100)"; WebFetch's reading, not confirmed from the figure).
- Reliability: one failure every 3 hours; causes of 419 interruptions in Llama 3 training shown as 8%, 17%, 30% for network, HBM3 memory, GPU faults (the pairing by text order is Network 8%, HBM3 17%, GPU 30%; not confirmed from the figure).
- Power: 8× a conventional rack. Per rack: GB200 NVL72 120 kW, HGX B200 60 kW, conventional 15 kW; GB200 NVL72 racks require liquid cooling.
- Cooling and water: ~700,000 L of freshwater to train GPT-3; AI projected to withdraw 4.2–6.6 billion m³ by 2027 (2027E).
Footnotes: Llama 3 Herd of Models; NVIDIA HGX data center guide; "Making AI Less Thirsty."
（2026-11-06 核對原始來源：Llama 3 論文 Table 5 是 Faulty GPU 30.1%、GPU HBM3 Memory 17.2%、Network Switch/Cable 8.4%，所以 8%／17%／30% 依序是網路、HBM3、GPU，上面依文字順序的推測成立。215 ms／24 ms 和本文的算式一致：70B 每 token 320 KB × 32,768 = 10.74 GB，÷ 50 GB/s（400 Gb/s 網卡）= 215 ms，÷ 450 GB/s（H100 NVLink 單向）= 24 ms。見 guide/sources/l10.md。）

=== B Page 50 ===
Next class (divider).

=== B Page 51 ===
Optional reading: Optimize GPU code (divider).

=== B Page 52 ===
Optimizing GPU code, four goals that combine in one kernel: (1) move less data (coalescing, tiling, fusion); (2) hide waiting time (async copies, warp specialization); (3) expose more parallelism (split-K, independent accumulators); (4) use faster instructions (Tensor Cores, lower precision). They stack: a fast GEMM coalesces loads, double-buffers tiles, uses Tensor Cores.

=== B Page 53 ===
Optimize memory traffic: memory coalescing (thread i reads x[i], not x[32·i]); shared-memory tiling (load a block once, reuse across threads); register tiling (each thread computes several outputs); kernel fusion (matmul + bias + activation); padding or swizzling to avoid bank conflicts (transpose tile 32×32 → 32×33); cache-aware ordering (group output tiles reading the same inputs).

=== B Page 54 ===
Hide waiting and expose parallelism: async copies and double buffering (load the next tile while computing the current; two shared buffers in a GEMM); ILP (several accumulators, not one dependency chain); warp specialization (producer warps load, consumer warps run MMAs); split-K / split reductions (split a long KV sequence across blocks in decode); warp-level communication (shuffle-based warp sum or max). Cost: split-K adds a merge step; pipelining adds buffers and syncs.

=== B Page 55 ===
Cheaper computation: Tensor Core mapping (MMA instead of scalar FMAs); lower precision (FP16/BF16 inputs with FP32 accumulation); unrolling and specialization (a kernel built for one head dim or mask type); less branch divergence (group tasks with similar control flow); autotuning (search tile size, warp count, pipeline depth). Takeaway: Tensor Cores need fitting shapes, and precision must stay accurate.

TOTAL PAGES (B): 55

## Readings（https://cs2680.com/readings/oct-21.html，2026-11-06 讀）

頁面沒有必讀／選讀之分，依主題分組。

- The GPU programming model：CUDA programming guide, https://docs.nvidia.com/cuda/cuda-c-programming-guide/（查閱用，不要從頭讀）
- The performance model：Roofline: An Insightful Visual Performance Model for Multicore Architectures, 2009, https://doi.org/10.1145/1498765.1498785；Making Deep Learning Go Brrrr From First Principles, 2022, https://horace.io/brrr_intro.html（compute-bound、bandwidth-bound、overhead-bound 三種）
- FlashAttention needs your attention：FlashAttention, 2022, https://arxiv.org/abs/2205.14135；FlashAttention-2, 2023, https://arxiv.org/abs/2307.08691；FlashAttention-3, 2024, https://arxiv.org/abs/2407.08608；FlashAttention-4, 2026, https://arxiv.org/abs/2603.05451；B200 Attention Kernel from Scratch to Near-SOTA in 60 Diagrams (Iaroslav Elistratov), 2026, https://iaroslavelistratov.github.io/b200-attention（14 個一次改一處的版本，各自對照 FlashAttention-4）
- Attention kernels inside a serving engine：FlashInfer, 2025, https://arxiv.org/abs/2501.01005；ragged paged attention (TPU), 2026, https://arxiv.org/abs/2604.15464
- Kernel fusion：FLUX, 2024, https://arxiv.org/abs/2406.06858
- Compilers and mega-kernels：TVM, 2018, https://arxiv.org/abs/1802.04799；Mirage, 2024, https://arxiv.org/abs/2405.05751；MPK, 2025, https://arxiv.org/abs/2512.22219
- The runtime between the scheduler and the kernel：CUDA graphs, 2026, https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#cuda-graphs；PyTorch 2, 2024, https://doi.org/10.1145/3620665.3640366
- Measurements：A Systematic Characterization of LLM Inference on GPUs, 2025, https://arxiv.org/abs/2512.01644（A100 與 Jetson Orin 上 prefill、decode 的時間花在哪）
